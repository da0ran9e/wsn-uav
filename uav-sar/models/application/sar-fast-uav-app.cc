#include "sar-fast-uav-app.h"
#include "../common/sar-metrics.h"
#include "../common/sar-types.h"
#include "../common/sar-params.h"

#include "ns3/core-module.h"
#include "ns3/packet.h"
#include "ns3/mac16-address.h"

#include <algorithm>
#include <cmath>
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
            if (m_ti >= m_targets.size()) { m_fc.Hover(); /* stay, keep spreading cues */ }
            else { Vector n = m_targets[m_ti];
                m_fc.Turn(std::atan2(n.y - p.y, n.x - p.x) * 180 / M_PI); m_fc.Forward(m_speed); }
        }
    } else return;
    m_ctrl = Simulator::Schedule(Seconds(params::kControlTickS), &SarFastUavApp::ControlTick, this);
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
        std::vector<uint8_t> b(kReportLen);
        uint8_t* q = b.data();
        *q++ = (uint8_t)Msg::REPORT; *q++ = 0x00;
        uint16_t rid = 1; std::memcpy(q, &rid, 2); q += 2; *q++ = 255;
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
    if (b[0] == (uint8_t)Msg::SUMMON && sz >= kSummonLen && m_dev) {
        // relay to DATA team over A2A (same body, different type).
        m_summonSeen = true;   // region found -> stop spreading cues
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
