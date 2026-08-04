#include "sar-fast-uav-app.h"
#include "../common/sar-metrics.h"
#include "../common/sar-types.h"
#include "../common/sar-params.h"

#include "ns3/core-module.h"
#include "ns3/packet.h"
#include "ns3/mac16-address.h"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstring>

using namespace ns3;

namespace ns3::uavsar {

NS_OBJECT_ENSURE_REGISTERED(SarFastUavApp);

TypeId SarFastUavApp::GetTypeId() {
    static TypeId tid = TypeId("ns3::uavsar::SarFastUavApp")
                            .SetParent<Application>().SetGroupName("uav-sar")
                            .AddConstructor<SarFastUavApp>();
    return tid;
}
SarFastUavApp::SarFastUavApp() : m_rng(CreateObject<UniformRandomVariable>()) {}
SarFastUavApp::~SarFastUavApp() = default;

void SarFastUavApp::SendClaim(uint8_t role) {
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

void SarFastUavApp::ClaimCourier() {
    if (m_yieldedCourier || m_courier) return;   // another FAST is the courier
    SendClaim(1);
    m_courier = true;
    m_state = State::RETURN_BS;
    if (m_metrics) {
        Vector p = m_fc.GetPosition();
        m_metrics->AddCustody();
        m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "FAST",
                         "report_pickup", "courier claimed", p.x, p.y, p.z);
    }
}

void SarFastUavApp::StartApplication() {
    m_fc.AttachTo(GetNode());
    // Plan the sweep with the (conservative) design coverage radius, not the
    // optimistic LoS link-budget range — otherwise coverage degenerates to a
    // single waypoint and the sweep becomes meaningless.
    m_radius = params::kUavBroadcastRadiusM;
    Simulator::Schedule(Seconds(1.0 + 0.3 * m_nodeId), &SarFastUavApp::TakeOff, this);
}
void SarFastUavApp::StopApplication() {
    Simulator::Cancel(m_ctrl); Simulator::Cancel(m_dis); Simulator::Cancel(m_traj);
    m_fc.Hover(); m_fc.SetClimb(0);
}

void SarFastUavApp::BuildMission() {
    m_targets.clear(); m_ti = 0;
    const size_t N = m_sensors.size();
    if (N == 0 || m_radius <= 0) return;
    const double r2 = m_radius * m_radius;
    std::vector<std::vector<uint32_t>> cov(N);
    for (size_t i = 0; i < N; i++)
        for (size_t j = 0; j < N; j++) {
            double dx = m_sensors[i].x - m_sensors[j].x, dy = m_sensors[i].y - m_sensors[j].y;
            if (dx * dx + dy * dy <= r2) cov[i].push_back(j);
        }
    std::vector<bool> covered(N, false), used(N, false);
    size_t cc = 0; Vector last = m_fc.GetPosition();
    while (cc < N) {
        double bs = -1; int bi = -1;
        for (size_t i = 0; i < N; i++) {
            if (used[i]) continue;
            uint32_t g = 0; for (uint32_t s : cov[i]) if (!covered[s]) g++;
            if (!g) continue;
            double d = std::hypot(m_sensors[i].x - last.x, m_sensors[i].y - last.y);
            double sc = g / (1.0 + d / m_speed);
            if (sc > bs) { bs = sc; bi = (int)i; }
        }
        if (bi < 0) break;
        Vector wp(m_sensors[bi].x, m_sensors[bi].y, m_alt);
        m_targets.push_back(wp); used[bi] = true;
        for (uint32_t s : cov[bi]) if (!covered[s]) { covered[s] = true; cc++; }
        last = wp;
    }
}

void SarFastUavApp::TakeOff() {
    BuildMission();
    if (m_targets.empty()) return;
    if (m_metrics) { Vector p = m_fc.GetPosition();
        m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "FAST", "takeoff", "", p.x, p.y, p.z); }
    m_state = State::CLIMB; m_fc.Hover(); m_fc.SetClimb(params::kClimbRateMps);
    m_ctrl = Simulator::Schedule(Seconds(params::kControlTickS), &SarFastUavApp::ControlTick, this);
    m_dis = Simulator::Schedule(Seconds(params::kDisseminateStaggerS), &SarFastUavApp::DisseminateTick, this);
    TrajTick();
}

void SarFastUavApp::ControlTick() {
    Vector p = m_fc.GetPosition();
    double arriveR = std::max(1.0, m_speed * params::kControlTickS * 1.5);
    if (m_state == State::CLIMB) {
        if (p.z >= m_alt) { m_fc.SetClimb(0); m_state = State::CRUISE;
            Vector t = m_targets[m_ti];
            m_fc.Turn(std::atan2(t.y - p.y, t.x - p.x) * 180 / M_PI); m_fc.Forward(m_speed); }
    } else if (m_state == State::RETURN_BS) {
        double d = std::hypot(m_bsPos.x - p.x, m_bsPos.y - p.y);
        m_fc.Turn(std::atan2(m_bsPos.y - p.y, m_bsPos.x - p.x) * 180 / M_PI);
        m_fc.Forward(m_speed);
        if (d <= arriveR) {
            m_fc.Hover(); m_state = State::DONE;
            if (m_metrics) m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId,
                                            "FAST", "report_tx", "courier at BS",
                                            p.x, p.y, p.z);
            SendReport();
            return;
        }
    } else if (m_state == State::CRUISE) {
        Vector t = m_targets[m_ti];
        if (std::hypot(t.x - p.x, t.y - p.y) <= arriveR) {
            m_ti++;
            if (m_ti >= m_targets.size()) {
                // audit A10: a FAST UAV is the ONLY thing that can relay a
                // SUMMON to the loitering DATA team. Flying home the instant the
                // sweep ends means that on a small grid — where the sweep
                // finishes long before the ground has finished reporting — the
                // region forms with nobody airborne to hear it, and the mission
                // silently delivers nothing. Measured: at 8x8 this capped
                // mission completion at 63%, and made any observation window
                // >= 45 s fail outright.
                //
                // So: hold station as a relay for a BOUNDED grace period, then
                // go home. The bound is what keeps this from regressing to the
                // old hover-forever trap (which burned 620 kJ at 16x16); the
                // grace is what keeps a relay alive across the decision. Both
                // ends are local — no UAV consults the ground truth or a global
                // view to decide.
                if (!m_allHome) { m_fc.Hover(); }
                else if (m_summonSeen) { m_state = State::RETURN_BS; }
                else {
                    m_fc.Hover();
                    m_state = State::RELAY_HOLD;
                    m_relayUntilS = Simulator::Now().GetSeconds() + params::kRelayGraceS;
                }
            }
            else { Vector n = m_targets[m_ti];
                m_fc.Turn(std::atan2(n.y - p.y, n.x - p.x) * 180 / M_PI); m_fc.Forward(m_speed); }
        }
    } else if (m_state == State::RELAY_HOLD) {
        // Hold as an airborne relay until either the region forms (we relayed a
        // SUMMON, so the DATA team has its task) or the grace period runs out.
        if (m_summonSeen || Simulator::Now().GetSeconds() >= m_relayUntilS)
            m_state = State::RETURN_BS;
    } else return;
    m_ctrl = Simulator::Schedule(Seconds(params::kControlTickS), &SarFastUavApp::ControlTick, this);
}

void SarFastUavApp::RelayBestEcho() {
    // Dispatch the DATA team to the best DIRECT echo. Byte-for-byte the same
    // A2A the cooperative arm sends, so the two arms differ in HOW the aim point
    // was formed and in nothing else downstream.
    if (m_summonSeen || m_bestEchoEv <= 0 || !m_dev) return;
    m_summonSeen = true;
    m_hasFix = true; m_fixX = m_bestEchoX; m_fixY = m_bestEchoY;
    std::vector<uint8_t> r(kA2ALen, 0);
    uint8_t* q = r.data();
    *q++ = (uint8_t)Msg::A2A; *q++ = kBroadcast;
    uint16_t rid = 1; std::memcpy(q, &rid, 2); q += 2;
    int16_t cx = (int16_t)(m_bestEchoX * 10), cy = (int16_t)(m_bestEchoY * 10);
    std::memcpy(q, &cx, 2); q += 2; std::memcpy(q, &cy, 2);
    m_dev->Send(Create<Packet>(r.data(), r.size()), Mac16Address("ff:ff"), 0);
    if (m_metrics) {
        m_metrics->AddSent(); m_metrics->AddSentBytes(r.size()); m_metrics->AddCustody();
        Vector p = m_fc.GetPosition();
        char det[64];
        std::snprintf(det, sizeof det, "echo ev=%.2f -> %.1f;%.1f",
                      m_bestEchoEv, m_bestEchoX, m_bestEchoY);
        m_metrics->MarkLocalize(Simulator::Now().GetSeconds());
        m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "FAST",
                         "echo_relay", det, p.x, p.y, p.z);
    }
}

void SarFastUavApp::DisseminateTick() {
    // Byte-honest cue dissemination: cue fragments are chunked exactly like
    // full-data fragments (same header), cycling (frag, seq). Stops once a
    // summon has been relayed — the region is found, cues are moot.
    if (m_state == State::CRUISE && !m_summonSeen && !m_cues.empty() && m_dev) {
        const Fragment& f = m_cues[m_cueIdx % m_cues.size()];
        uint16_t total = (uint16_t)std::max(1u, (f.sizeBytes + kChunkBytes - 1) / kChunkBytes);
        uint32_t payloadLen = std::min(kChunkBytes, f.sizeBytes - m_cueSeq * kChunkBytes);
        std::vector<uint8_t> b(kChunkHdr + payloadLen, 0);
        uint8_t* p = b.data();
        *p++ = (uint8_t)Msg::CUE; *p++ = kBroadcast;
        uint16_t id = (uint16_t)f.id; std::memcpy(p, &id, 2); p += 2;
        std::memcpy(p, &m_cueSeq, 2); p += 2;
        std::memcpy(p, &total, 2); p += 2;
        *p++ = (uint8_t)f.layer;
        m_dev->Send(Create<Packet>(b.data(), b.size()), Mac16Address("ff:ff"), 0);
        if (m_metrics) {
            m_metrics->AddSent(); m_metrics->AddSentBytes(b.size());
            // viz: decimated A2G cue broadcast marker (1 in 25 sends)
            if (++m_cueTxCount % 25 == 1) {
                Vector p = m_fc.GetPosition();
                m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "FAST",
                                 "cue_tx", "", p.x, p.y, p.z);
            }
        }
        m_cueSeq++;
        if (m_cueSeq >= total) { m_cueSeq = 0; m_cueIdx = (m_cueIdx + 1) % m_cues.size(); }
    }
    m_dis = Simulator::Schedule(Seconds(params::kDisseminateStaggerS), &SarFastUavApp::DisseminateTick, this);
}

void SarFastUavApp::TrajTick() {
    if (m_metrics) {
        Vector p = m_fc.GetPosition();
        m_metrics->Traj(Simulator::Now().GetSeconds(), m_nodeId, "FAST", p.x, p.y, p.z);
        // Propulsion energy over the last second (Zeng-Xu-Zhang rotary model).
        m_metrics->AddEnergy(params::EnergyPowerW(m_fc.Speed()) * params::kTrajLogS);
    }
    m_traj = Simulator::Schedule(Seconds(params::kTrajLogS), &SarFastUavApp::TrajTick, this);
}

void SarFastUavApp::SendReport() {
    if (m_reportsSent >= params::kReportRetries) return;
    if (m_dev) {
        std::vector<uint8_t> b(kReportLen, 0);
        uint8_t* q = b.data();
        *q++ = (uint8_t)Msg::REPORT; *q++ = m_hasFix ? kFlagHasFix : 0x00;
        uint16_t rid = 1; std::memcpy(q, &rid, 2); q += 2; *q++ = 255;
        int16_t fx = (int16_t)std::lround(m_fixX * 10.0);
        int16_t fy = (int16_t)std::lround(m_fixY * 10.0);
        std::memcpy(q, &fx, 2); q += 2; std::memcpy(q, &fy, 2);
        m_dev->Send(Create<Packet>(b.data(), b.size()), m_bsAddr, 0);
        if (m_metrics) { m_metrics->AddSent(); m_metrics->AddSentBytes(b.size()); }
    }
    m_reportsSent++;
    Simulator::Schedule(Seconds(params::kReportRetryS), &SarFastUavApp::SendReport, this);
}

bool SarFastUavApp::OnReceive(Ptr<NetDevice>, Ptr<const Packet> pkt, uint16_t, const Address&) {
    uint32_t sz = pkt->GetSize();
    if (sz < 2) return true;
    std::vector<uint8_t> b(sz); pkt->CopyData(b.data(), sz);
    if (b[0] == (uint8_t)Msg::HANDOFF && sz >= kHandoffLen) {
        // audit B3: take custody of the fix as well as of the errand.
        if (b[1] & kFlagHasFix) {
            int16_t fx, fy; std::memcpy(&fx, &b[4], 2); std::memcpy(&fy, &b[6], 2);
            m_hasFix = true; m_fixX = fx / 10.0; m_fixY = fy / 10.0;
        }
        // Radio courier election: schedule a CLAIM after a short backoff; the
        // first FAST to claim on the radio wins, the rest yield.
        if (!m_courier && !m_yieldedCourier && !m_courierEvent.IsPending())
            m_courierEvent = Simulator::Schedule(
                Seconds(m_rng->GetValue(0.0, params::kClaimBackoffS)),
                &SarFastUavApp::ClaimCourier, this);
        return true;
    }
    if (b[0] == (uint8_t)Msg::CONFIRM && m_allHome && m_state == State::CRUISE) {
        // audit F2: the delivery is done -> this UAV's task is over; fly home and
        // report like every baseline UAV must.  (Symmetric completion rule.)
        m_summonSeen = true;                 // stop spreading cues
        m_state = State::RETURN_BS;
        return true;
    }
    if (b[0] == (uint8_t)Msg::CLAIM && sz >= kClaimLen) {
        uint8_t role = b[3]; uint16_t id; std::memcpy(&id, &b[4], 2);
        if (role == 1 && id != (uint16_t)m_nodeId && !m_courier) {
            m_yieldedCourier = true;               // another FAST is the courier
            Simulator::Cancel(m_courierEvent);
        }
        return true;
    }
    if (b[0] == (uint8_t)Msg::A2A && sz >= kA2ALen) {
        // A peer already dispatched the DATA team, so the region is found and
        // cues are moot. In the cooperative arm the ground SUMMON reaches every
        // FAST at once; the closed-loop arm has no such shared plane, so the
        // fleet message is what stops the others cueing.
        m_summonSeen = true;
        Simulator::Cancel(m_echoSettle);
        return true;
    }
    if (b[0] == (uint8_t)Msg::ECHO && sz >= kEchoLen && m_echoRelay && !m_summonSeen) {
        // audit W4: closed-loop NON-cooperative arm. There is no ground leader
        // and no region, so this UAV aims at the strongest thing it personally
        // overheard. Track the running argmax; the relay is scheduled once the
        // evidence stops improving (same "aim when it settles" rule the
        // cooperative arm uses, so the two differ ONLY in whether the ground
        // aggregates for them).
        uint8_t evQ8 = b[3];
        int16_t x, y; std::memcpy(&x, &b[4], 2); std::memcpy(&y, &b[6], 2);
        double ev = evQ8 / 255.0;
        if (ev > m_bestEchoEv) {
            m_bestEchoEv = ev; m_bestEchoX = x / 10.0; m_bestEchoY = y / 10.0;
            Simulator::Cancel(m_echoSettle);
            m_echoSettle = Simulator::Schedule(Seconds(params::kEvidenceStableS),
                                               &SarFastUavApp::RelayBestEcho, this);
        }
        return true;
    }
    if (b[0] == (uint8_t)Msg::SUMMON && sz >= kSummonLen && m_dev) {
        // relay to DATA team over A2A (same body, different type).
        m_summonSeen = true;   // region found -> stop spreading cues
        // audit B3: a relaying FAST heard the coordinates itself, so it can also
        // carry them home — the fix is not the courier's private property.
        {
            int16_t cx, cy; std::memcpy(&cx, &b[4], 2); std::memcpy(&cy, &b[6], 2);
            m_hasFix = true; m_fixX = cx / 10.0; m_fixY = cy / 10.0;
        }
        std::vector<uint8_t> r(b.begin(), b.begin() + kSummonLen);
        r[0] = (uint8_t)Msg::A2A;
        m_dev->Send(Create<Packet>(r.data(), r.size()), Mac16Address("ff:ff"), 0);
        if (m_metrics) {
            m_metrics->AddSent();
            m_metrics->AddSentBytes(r.size());
            m_metrics->AddCustody();
            // viz: A2A relay marker at the relaying FAST UAV
            Vector p = m_fc.GetPosition();
            m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "FAST",
                             "a2a_relay", "", p.x, p.y, p.z);
        }
    }
    return true;
}

}  // namespace ns3::uavsar
