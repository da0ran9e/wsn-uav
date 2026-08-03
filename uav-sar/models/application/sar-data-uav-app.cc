#include "sar-data-uav-app.h"
#include "../common/sar-metrics.h"
#include "../common/sar-types.h"
#include "../common/sar-params.h"

#include "../common/gmc.h"

#include "ns3/core-module.h"
#include "ns3/packet.h"
#include "ns3/mac16-address.h"

#include <algorithm>
#include <cmath>
#include <cstring>

using namespace ns3;

namespace ns3::uavsar {

NS_OBJECT_ENSURE_REGISTERED(SarDataUavApp);

TypeId SarDataUavApp::GetTypeId() {
    static TypeId tid = TypeId("ns3::uavsar::SarDataUavApp")
                            .SetParent<Application>().SetGroupName("uav-sar")
                            .AddConstructor<SarDataUavApp>();
    return tid;
}
SarDataUavApp::SarDataUavApp() : m_rng(CreateObject<UniformRandomVariable>()) {}
SarDataUavApp::~SarDataUavApp() = default;

void SarDataUavApp::StartApplication() {
    m_fc.AttachTo(GetNode());
    Simulator::Schedule(Seconds(1.0 + 0.3 * m_nodeId), &SarDataUavApp::TakeOff, this);
}
void SarDataUavApp::StopApplication() {
    Simulator::Cancel(m_ctrl); Simulator::Cancel(m_traj); Simulator::Cancel(m_claimEvent);
    m_fc.Hover(); m_fc.SetClimb(0);
}

void SarDataUavApp::TakeOff() {
    if (m_metrics) { Vector p = m_fc.GetPosition();
        m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "DATA", "takeoff", "", p.x, p.y, p.z); }
    if (m_mode == Mode::SWEEP_DUMP) {
        // plan sweep with the design coverage radius (see FAST app note).
        m_radius = params::kUavBroadcastRadiusM;
        m_targets = m_tourOverride.empty()
                        ? BuildGmc(m_sensors, m_radius, m_fc.GetPosition(), m_alt, m_speed)
                        : m_tourOverride;   // tsp-mc: pre-planned VBS/TSP tour
        m_ti = 0;
    }
    m_state = State::CLIMB; m_fc.Hover(); m_fc.SetClimb(params::kClimbRateMps);
    m_ctrl = Simulator::Schedule(Seconds(params::kControlTickS), &SarDataUavApp::ControlTick, this);
    TrajTick();
}

void SarDataUavApp::SendClaim(uint8_t role) {
    if (!m_dev) return;
    std::vector<uint8_t> b(kClaimLen);
    uint8_t* q = b.data();
    *q++ = (uint8_t)Msg::CLAIM;
    uint16_t rid = 1; std::memcpy(q, &rid, 2); q += 2;
    *q++ = role;
    uint16_t id = (uint16_t)m_nodeId; std::memcpy(q, &id, 2);
    m_dev->Send(Create<Packet>(b.data(), b.size()), Mac16Address("ff:ff"), 0);
    if (m_metrics) { m_metrics->AddSent(); m_metrics->AddSentBytes(b.size()); }
}

void SarDataUavApp::ClaimDivert() {
    if (m_yieldedDivert || m_claimed) return;   // someone else already claimed
    SendClaim(0);                               // announce on the radio, then act
    TryClaimDivert(m_pendX, m_pendY);
}

void SarDataUavApp::TryClaimDivert(double x, double y) {
    if (m_claimed || m_state == State::DELIVER || m_state == State::RETURN) return;
    m_claimed = true;
    Vector p = m_fc.GetPosition();
    m_divert = Vector(x, y, m_alt);
    m_divertStartDist = std::hypot(x - p.x, y - p.y);
    // If already cruising (loiter/en-route), divert now; if still on the ground
    // or climbing, remember it and divert once we reach cruise altitude — else a
    // late TakeOff would clobber the DIVERT state.
    if (m_state == State::LOITER || m_state == State::GOTO_CENTER)
        m_state = State::DIVERT;
    else
        m_pendingDivert = true;
    if (m_metrics) {
        m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "DATA", "divert", "to region", p.x, p.y, p.z);
        m_metrics->AddDeviation(m_divertStartDist);
    }
}

void SarDataUavApp::ControlTick() {
    Vector p = m_fc.GetPosition();
    double arriveR = std::max(1.0, m_speed * params::kControlTickS * 1.5);
    switch (m_state) {
        case State::CLIMB:
            if (p.z >= m_alt) {
                m_fc.SetClimb(0);
                if (m_mode == Mode::SWEEP_DUMP) {
                    if (m_targets.empty()) { m_state = State::DONE; return; }
                    m_state = State::SWEEP;
                    Vector t = m_targets[m_ti];
                    m_fc.Turn(std::atan2(t.y - p.y, t.x - p.x) * 180 / M_PI); m_fc.Forward(m_speed);
                } else if (m_pendingDivert) {   // claimed before takeoff -> region
                    m_pendingDivert = false;
                    m_state = State::DIVERT;
                } else {
                    m_state = State::GOTO_CENTER;
                    m_fc.Turn(std::atan2(m_loiter.y - p.y, m_loiter.x - p.x) * 180 / M_PI);
                    m_fc.Forward(m_speed);
                }
            }
            break;
        case State::SWEEP: {
            Vector t = m_targets[m_ti];
            if (std::hypot(t.x - p.x, t.y - p.y) <= arriveR) {
                m_fc.Hover(); m_state = State::DELIVER;
                // blind dwell: cycle chunks with no ground feedback. tsp-mc sizes
                // the connection time as kMcRedundancy x the dataset airtime (the
                // coded-multicast overhead of Zeng'18: send extra to ride out
                // drops); nocoop keeps the fixed design budget.
                double dwell = params::kBaselineDwellS;
                if (m_reportAtEnd) {
                    uint32_t chunks = 0;
                    for (const auto& f : m_full)
                        chunks += std::max(1u, (f.sizeBytes + kChunkBytes - 1) / kChunkBytes);
                    dwell = m_mcRedundancy * chunks * params::kDeliverStaggerS;
                }
                m_dwellUntil = Simulator::Now().GetSeconds() + dwell;
                SendFullChunk(0, 0);
            }
            break;
        }
        case State::GOTO_CENTER:
            if (std::hypot(m_loiter.x - p.x, m_loiter.y - p.y) <= arriveR) {
                m_fc.Hover(); m_state = State::LOITER; }
            break;
        case State::LOITER:
            break;  // wait for A2A relay
        case State::DIVERT: {
            double d = std::hypot(m_divert.x - p.x, m_divert.y - p.y);
            m_fc.Turn(std::atan2(m_divert.y - p.y, m_divert.x - p.x) * 180 / M_PI);
            m_fc.Forward(m_speed);
            if (d <= arriveR) { m_fc.Hover(); m_state = State::DELIVER;
                m_deliverUntil = Simulator::Now().GetSeconds() + params::kMinDeliverDwellS;
                if (m_metrics) m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "DATA",
                                                "deliver_start", "", p.x, p.y, p.z);
                SendFullChunk(0, 0); }
            break;
        }
        case State::DELIVER:
            break;  // delivery chain runs; then we wait for CONFIRM
        case State::RETURN: {
            double d = std::hypot(m_bsPos.x - p.x, m_bsPos.y - p.y);
            m_fc.Turn(std::atan2(m_bsPos.y - p.y, m_bsPos.x - p.x) * 180 / M_PI);
            m_fc.Forward(m_speed);
            if (d <= arriveR) {
                m_fc.Hover(); m_state = State::DONE;
                if (m_metrics) m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "DATA",
                                                "report_tx", "to BS", p.x, p.y, p.z);
                SendReport();   // retried until quota (F2: no single-shot loss)
                return;
            }
            break;
        }
        case State::IDLE: case State::DONE: return;
    }
    m_ctrl = Simulator::Schedule(Seconds(params::kControlTickS), &SarDataUavApp::ControlTick, this);
}

void SarDataUavApp::SendFullChunk(size_t fi, uint16_t seq) {
    if (m_state != State::DELIVER || m_full.empty()) return;  // stopped / nothing to send
    if (fi >= m_full.size()) {
        // One full pass over the dataset finished.
        if (m_mode == Mode::SWEEP_DUMP) {
            if (Simulator::Now().GetSeconds() < m_dwellUntil) {
                SendFullChunk(0, 0);   // keep cycling within the dwell budget
                return;
            }
            m_ti++;
            Vector p = m_fc.GetPosition();
            if (m_ti >= m_targets.size()) {
                // tsp-mc: mission ends only when the UAV is back at the BS and
                // the report is received — fly home now (ControlTick services it).
                m_state = m_reportAtEnd ? State::RETURN : State::DONE;
                return;
            }
            m_state = State::SWEEP;
            Vector t = m_targets[m_ti];
            m_fc.Turn(std::atan2(t.y - p.y, t.x - p.x) * 180 / M_PI); m_fc.Forward(m_speed);
            // ControlTick is still looping (from DELIVER); it will service SWEEP.
            return;
        }
        // SUMMONED: cycle until the leader's CONFIRM stops us — the cooperation
        // feedback is exactly what lets us retransmit lost chunks and stop.
        SendFullChunk(0, 0);
        return;
    }
    const Fragment& f = m_full[fi];
    uint16_t total = (uint16_t)std::max(1u, (f.sizeBytes + kChunkBytes - 1) / kChunkBytes);
    if (m_dev) {
        uint32_t payloadLen = std::min(kChunkBytes, f.sizeBytes - seq * kChunkBytes);
        std::vector<uint8_t> b(kChunkHdr + payloadLen, 0);
        uint8_t* p = b.data();
        *p++ = (uint8_t)Msg::FULL; *p++ = kBroadcast;
        uint16_t id = (uint16_t)f.id; std::memcpy(p, &id, 2); p += 2;
        std::memcpy(p, &seq, 2); p += 2;
        std::memcpy(p, &total, 2); p += 2;
        *p++ = (uint8_t)f.layer;
        m_dev->Send(Create<Packet>(b.data(), b.size()), Mac16Address("ff:ff"), 0);
        if (m_metrics) {
            m_metrics->AddSent(); m_metrics->AddSentBytes(b.size());
            // viz: decimated A2G full-data broadcast marker (1 in 50 chunks)
            if (++m_fullTxCount % 50 == 1) {
                Vector p = m_fc.GetPosition();
                m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "DATA",
                                 "full_tx", "", p.x, p.y, p.z);
            }
        }
    }
    uint16_t ns = seq + 1; size_t nf = fi;
    if (ns >= total) { ns = 0; nf = fi + 1; }
    Simulator::Schedule(Seconds(params::kDeliverStaggerS), &SarDataUavApp::SendFullChunk, this, nf, ns);
}

void SarDataUavApp::SendReport() {
    if (m_reportsSent >= params::kReportRetries) return;
    if (m_dev) {
        std::vector<uint8_t> b(kReportLen);
        uint8_t* q = b.data();
        *q++ = (uint8_t)Msg::REPORT; *q++ = 0x00;
        uint16_t rid = 1; std::memcpy(q, &rid, 2); q += 2; *q++ = 255;
        m_dev->Send(Create<Packet>(b.data(), b.size()), m_bsAddr, 0);
        if (m_metrics) { m_metrics->AddSent(); m_metrics->AddSentBytes(b.size()); }
    }
    m_reportsSent++;
    Simulator::Schedule(Seconds(params::kReportRetryS), &SarDataUavApp::SendReport, this);
}

void SarDataUavApp::SendHandoff() {
    if (m_handoffsSent >= params::kConfirmRetries) return;
    if (m_dev) {
        std::vector<uint8_t> b(kHandoffLen);
        uint8_t* q = b.data();
        *q++ = (uint8_t)Msg::HANDOFF; *q++ = kBroadcast;
        uint16_t rid = 1; std::memcpy(q, &rid, 2);
        m_dev->Send(Create<Packet>(b.data(), b.size()), Mac16Address("ff:ff"), 0);
        if (m_metrics) { m_metrics->AddSent(); m_metrics->AddSentBytes(b.size()); }
    }
    m_handoffsSent++;
    Simulator::Schedule(Seconds(params::kConfirmRetryS), &SarDataUavApp::SendHandoff, this);
}

void SarDataUavApp::TrajTick() {
    if (m_metrics) {
        Vector p = m_fc.GetPosition();
        m_metrics->Traj(Simulator::Now().GetSeconds(), m_nodeId, "DATA", p.x, p.y, p.z);
        m_metrics->AddEnergy(params::EnergyPowerW(m_fc.Speed()) * params::kTrajLogS);
    }
    if (m_state != State::DONE)
        m_traj = Simulator::Schedule(Seconds(params::kTrajLogS), &SarDataUavApp::TrajTick, this);
}

bool SarDataUavApp::OnReceive(Ptr<NetDevice>, Ptr<const Packet> pkt, uint16_t, const Address&) {
    uint32_t sz = pkt->GetSize();
    if (sz < 2) return true;
    std::vector<uint8_t> b(sz); pkt->CopyData(b.data(), sz);
    uint8_t type = b[0];
    if (type == (uint8_t)Msg::A2A && sz >= kA2ALen) {
        int16_t cx, cy; std::memcpy(&cx, &b[4], 2); std::memcpy(&cy, &b[6], 2);
        // Radio mutual exclusion: schedule a CLAIM after a short backoff; if a
        // peer's CLAIM arrives first we yield, so exactly one DATA UAV diverts.
        if (!m_claimed && !m_yieldedDivert && !m_claimEvent.IsPending() &&
            m_state != State::DELIVER && m_state != State::RETURN) {
            m_pendX = cx / 10.0; m_pendY = cy / 10.0;
            m_claimEvent = Simulator::Schedule(Seconds(m_rng->GetValue(0.0, params::kClaimBackoffS)),
                                               &SarDataUavApp::ClaimDivert, this);
        }
    } else if (type == (uint8_t)Msg::CLAIM && sz >= kClaimLen) {
        uint8_t role = b[3]; uint16_t id; std::memcpy(&id, &b[4], 2);
        if (role == 0 && id != (uint16_t)m_nodeId && !m_claimed) {
            m_yieldedDivert = true;                 // another DATA UAV took it
            Simulator::Cancel(m_claimEvent);
        }
        // A FAST courier claimed the report over the radio: the faster UAV owns
        // the trip home now — stop our slow (15 vs 25 m/s) fallback return and
        // hover in place, saving the transit energy.
        if (role == 1 && m_confirmed && m_state == State::RETURN) {
            m_fc.Hover();
            m_state = State::DONE;
            if (m_metrics) {
                Vector p = m_fc.GetPosition();
                m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "DATA",
                                 "return_yield", "courier took the report", p.x, p.y, p.z);
            }
        }
    } else if (type == (uint8_t)Msg::CONFIRM && sz >= kConfirmLen) {
        // our delivery confirmed -> hand the report to the FAST team (25 m/s
        // courier beats our 15 m/s) and still fly home as the fallback; the BS
        // deduplicates, first REPORT wins.
        if (m_claimed && !m_confirmed && (m_state == State::DELIVER || m_state == State::DIVERT)) {
            m_confirmed = true;
            // Keep delivering until the coverage dwell elapses so the whole
            // localized footprint (incl. a slightly-off victim) reconstructs the
            // data — then head home and hand the report to the FAST courier.
            double wait = std::max(0.0, m_deliverUntil - Simulator::Now().GetSeconds());
            Simulator::Schedule(Seconds(wait), &SarDataUavApp::BeginReturn, this);
        }
    }
    return true;
}

void SarDataUavApp::BeginReturn() {
    if (m_state == State::RETURN || m_state == State::DONE) return;
    m_state = State::RETURN;
    SendHandoff();
}

}  // namespace ns3::uavsar
