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
SarFastUavApp::SarFastUavApp() = default;
SarFastUavApp::~SarFastUavApp() = default;

void SarFastUavApp::StartApplication() {
    m_fc.AttachTo(GetNode());
    double exponent = (0.0 - params::kRxSensitivityDbm - params::kRefLossDb) /
                      (10.0 * params::kA2GExponent);
    double slant = std::pow(10.0, exponent);
    m_radius = (slant > m_alt) ? std::sqrt(slant * slant - m_alt * m_alt) : 0.0;
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
    if (m_state == State::CRUISE && !m_cues.empty() && m_dev) {
        const Fragment& f = m_cues[m_cueIdx % m_cues.size()];
        std::vector<uint8_t> b(kCueLen);
        uint8_t* p = b.data();
        *p++ = (uint8_t)Msg::CUE; *p++ = kBroadcast;
        uint16_t id = (uint16_t)f.id; std::memcpy(p, &id, 2); p += 2;
        *p++ = (uint8_t)f.layer;
        *p++ = (uint8_t)std::min(255.0, f.utility * 255.0);
        m_dev->Send(Create<Packet>(b.data(), b.size()), Mac16Address("ff:ff"), 0);
        if (m_metrics) m_metrics->AddSent();
        m_cueIdx++;
    }
    m_dis = Simulator::Schedule(Seconds(params::kDisseminateStaggerS), &SarFastUavApp::DisseminateTick, this);
}

void SarFastUavApp::TrajTick() {
    if (m_metrics) { Vector p = m_fc.GetPosition();
        m_metrics->Traj(Simulator::Now().GetSeconds(), m_nodeId, "FAST", p.x, p.y, p.z); }
    m_traj = Simulator::Schedule(Seconds(params::kTrajLogS), &SarFastUavApp::TrajTick, this);
}

bool SarFastUavApp::OnReceive(Ptr<NetDevice>, Ptr<const Packet> pkt, uint16_t, const Address&) {
    uint32_t sz = pkt->GetSize();
    if (sz < 2) return true;
    std::vector<uint8_t> b(sz); pkt->CopyData(b.data(), sz);
    if (b[0] == (uint8_t)Msg::SUMMON && sz >= kSummonLen && m_dev) {
        // relay to DATA team over A2A (same body, different type).
        std::vector<uint8_t> r(b.begin(), b.begin() + kSummonLen);
        r[0] = (uint8_t)Msg::A2A;
        m_dev->Send(Create<Packet>(r.data(), r.size()), Mac16Address("ff:ff"), 0);
        if (m_metrics) { m_metrics->AddSent(); m_metrics->AddCustody(); }
    }
    return true;
}

}  // namespace ns3::uavsar
