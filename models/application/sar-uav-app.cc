#include "sar-uav-app.h"
#include "../common/log.h"
#include "../common/sar-metrics.h"

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"
#include "ns3/mac16-address.h"

#include <algorithm>
#include <cmath>
#include <cstring>
#include <limits>

using namespace ns3;

namespace ns3::wsn::uav {

using sar::MsgType;
using sar::FragClass;
using sar::UavRole;
using sar::Scheme;

namespace {
constexpr double CONTROL_TICK_S   = 0.1;
constexpr double ARRIVAL_RADIUS_M = 1.0;
constexpr double CLIMB_RATE_MPS   = 5.0;
constexpr double TRAJ_LOG_S       = 1.0;
constexpr double GMC_ALPHA        = 1.0;
constexpr double DELIVER_STAGGER_S = 0.02;  // point-blank bulk delivery to target

std::string RoleStr(UavRole r) { return r == UavRole::FAST ? "FAST" : "DATA"; }
}  // namespace

NS_OBJECT_ENSURE_REGISTERED(SarUavApp);

TypeId SarUavApp::GetTypeId() {
    static TypeId tid = TypeId("ns3::wsn::uav::SarUavApp")
                            .SetParent<Application>()
                            .SetGroupName("wsn-uav")
                            .AddConstructor<SarUavApp>();
    return tid;
}

SarUavApp::SarUavApp() = default;
SarUavApp::~SarUavApp() = default;

void SarUavApp::StartApplication() {
    m_ctrl.AttachTo(GetNode());
    LogT("sar-uav[" + std::to_string(m_nodeId) + "]")
        << "start role=" << RoleStr(m_role) << " carries=" << m_carried.size()
        << " frags, scheme=" << (int)m_scheme;
    // Compute coverage radius from the standard LogDistance link budget.
    double exponent = (0.0 - (-95.0) - 46.6) / (10.0 * 3.0);
    double slant = std::pow(10.0, exponent);
    m_broadcastRadius = (slant > m_cruiseAlt)
                            ? std::sqrt(slant * slant - m_cruiseAlt * m_cruiseAlt)
                            : 0.0;
    // Small per-UAV stagger before takeoff so the fleet doesn't move in lockstep.
    double delay = 1.0 + 0.3 * (m_nodeId);
    Simulator::Schedule(Seconds(delay), &SarUavApp::TakeOff, this);
}

void SarUavApp::StopApplication() {
    Simulator::Cancel(m_controlEvent);
    Simulator::Cancel(m_disEvent);
    m_ctrl.Hover();
    m_ctrl.SetClimb(0.0);
}

void SarUavApp::TakeOff() {
    BuildMission();
    if (m_targets.empty()) {
        LogT("sar-uav[" + std::to_string(m_nodeId) + "]") << "no targets, abort";
        return;
    }
    if (m_metrics) {
        Vector p = m_ctrl.GetPosition();
        m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, RoleStr(m_role),
                         "takeoff", "", p.x, p.y, p.z);
    }
    m_state = State::CLIMBING;
    m_ctrl.Hover();
    m_ctrl.SetClimb(CLIMB_RATE_MPS);
    m_controlEvent = Simulator::Schedule(Seconds(CONTROL_TICK_S), &SarUavApp::ControlTick, this);
    LogTraj();
    // Begin disseminating once airborne (guarded by state inside the tick).
    m_disEvent = Simulator::Schedule(Seconds(sar::SEND_STAGGER_S), &SarUavApp::DisseminateTick, this);
}

void SarUavApp::BuildMission() {
    m_targets.clear();
    m_targetIdx = 0;
    const size_t N = m_sensorPositions.size();
    if (N == 0 || m_broadcastRadius <= 0.0) return;

    // For SINGLE scheme the lone UAV must cover the whole grid; for multi-UAV
    // schemes each UAV still plans full coverage but staggered start + claim
    // logic spreads them out. (Round 1 keeps planning identical; differentiation
    // comes from role behaviour, not partitioning.)
    const double r2 = m_broadcastRadius * m_broadcastRadius;
    std::vector<std::vector<uint32_t>> cov(N);
    for (size_t i = 0; i < N; i++)
        for (size_t j = 0; j < N; j++) {
            double dx = m_sensorPositions[i].x - m_sensorPositions[j].x;
            double dy = m_sensorPositions[i].y - m_sensorPositions[j].y;
            if (dx * dx + dy * dy <= r2) cov[i].push_back(j);
        }

    std::vector<bool> covered(N, false), used(N, false);
    size_t coveredCount = 0;
    Vector last = m_ctrl.GetPosition();
    while (coveredCount < N) {
        double bestScore = -1.0; int bestIdx = -1;
        for (size_t i = 0; i < N; i++) {
            if (used[i]) continue;
            uint32_t gain = 0;
            for (uint32_t s : cov[i]) if (!covered[s]) gain++;
            if (gain == 0) continue;
            double dx = m_sensorPositions[i].x - last.x;
            double dy = m_sensorPositions[i].y - last.y;
            double dist = std::sqrt(dx * dx + dy * dy);
            double score = gain / (1.0 + GMC_ALPHA * dist / m_cruiseSpeed);
            if (score > bestScore) { bestScore = score; bestIdx = (int)i; }
        }
        if (bestIdx < 0) break;
        Vector wp(m_sensorPositions[bestIdx].x, m_sensorPositions[bestIdx].y, m_cruiseAlt);
        m_targets.push_back(wp);
        used[bestIdx] = true;
        for (uint32_t s : cov[bestIdx]) if (!covered[s]) { covered[s] = true; coveredCount++; }
        last = wp;
    }
    LogT("sar-uav[" + std::to_string(m_nodeId) + "]")
        << "GMC mission " << m_targets.size() << " wps, radius=" << m_broadcastRadius << "m";
}

bool SarUavApp::AdvanceToNextTarget() {
    if (m_targetIdx >= m_targets.size()) return false;
    Vector pos = m_ctrl.GetPosition();
    Vector tgt = m_targets[m_targetIdx];
    double headingDeg = std::atan2(tgt.y - pos.y, tgt.x - pos.x) * 180.0 / M_PI;
    m_ctrl.Turn(headingDeg);
    m_ctrl.Forward(m_cruiseSpeed);
    return true;
}

void SarUavApp::ControlTick() {
    Vector pos = m_ctrl.GetPosition();
    // Arrival tolerance must exceed one tick's travel or the UAV overshoots the
    // waypoint every tick and never registers arrival (flies off to infinity).
    const double arriveR = std::max(ARRIVAL_RADIUS_M, m_cruiseSpeed * CONTROL_TICK_S * 1.5);
    switch (m_state) {
        case State::CLIMBING:
            if (pos.z >= m_cruiseAlt) {
                m_ctrl.SetClimb(0.0);
                m_state = State::CRUISING;
                AdvanceToNextTarget();
            }
            break;
        case State::CRUISING: {
            Vector tgt = m_targets[m_targetIdx];
            double dist = std::hypot(tgt.x - pos.x, tgt.y - pos.y);
            if (dist <= arriveR) {
                // Baselines (no ground intelligence) don't know which cell holds
                // the victim, so they dwell-and-dump the full dataset at every
                // visited cell. Proposed just keeps sweeping (FAST spreads
                // recognition; DATA waits for a summon).
                if (m_scheme != Scheme::PROPOSED && !m_fullset.empty()) {
                    m_ctrl.Hover();
                    m_state = State::DELIVERING;
                    m_deliverMode = DeliverMode::WAYPOINT;
                    DeliverFullData();
                    break;
                }
                m_targetIdx++;
                if (m_targetIdx >= m_targets.size()) {
                    m_state = State::LANDING;
                    m_ctrl.Hover();
                    m_ctrl.SetClimb(-CLIMB_RATE_MPS);
                } else {
                    AdvanceToNextTarget();
                }
            }
            break;
        }
        case State::DIVERTING: {
            double dist = std::hypot(m_divertTarget.x - pos.x, m_divertTarget.y - pos.y);
            double headingDeg = std::atan2(m_divertTarget.y - pos.y,
                                           m_divertTarget.x - pos.x) * 180.0 / M_PI;
            m_ctrl.Turn(headingDeg);
            m_ctrl.Forward(m_cruiseSpeed);
            if (dist <= arriveR) {
                m_ctrl.Hover();
                m_state = State::DELIVERING;
                m_deliverMode = DeliverMode::DIVERT;
                if (m_metrics)
                    m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, RoleStr(m_role),
                                     "deliver_start", "", pos.x, pos.y, pos.z);
                DeliverFullData();
            }
            break;
        }
        case State::LANDING:
            if (pos.z <= 0.1) {
                m_ctrl.SetClimb(0.0); m_ctrl.Hover();
                m_state = State::DONE;
                return;
            }
            break;
        case State::DELIVERING:   // delivery scheduled separately; just hold
        case State::IDLE:
        case State::DONE:
            if (m_state == State::DONE || m_state == State::IDLE) return;
            break;
    }
    m_controlEvent = Simulator::Schedule(Seconds(CONTROL_TICK_S), &SarUavApp::ControlTick, this);
}

void SarUavApp::LogTraj() {
    if (m_metrics) {
        Vector p = m_ctrl.GetPosition();
        m_metrics->Trajectory(Simulator::Now().GetSeconds(), m_nodeId, RoleStr(m_role),
                              p.x, p.y, p.z);
    }
    if (m_state != State::DONE)
        Simulator::Schedule(Seconds(TRAJ_LOG_S), &SarUavApp::LogTraj, this);
}

// ---- dissemination --------------------------------------------------------
void SarUavApp::DisseminateTick() {
    bool sweeping = (m_state == State::CRUISING);
    // Continuous low-rate broadcast spreads cheap RECOGNITION cues. Only the
    // proposed FAST team does this; DATA holds data for on-demand delivery, and
    // baselines instead dwell-and-dump full data at each cell (see ControlTick).
    bool disseminate = (m_scheme == Scheme::PROPOSED && m_role == UavRole::FAST);
    if (sweeping && disseminate && !m_carried.empty()) {
        const sar::Fragment& f = m_carried[m_disFragIdx];
        SendFragChunk(f.id, m_disSeq, f.numChunks, f.cls);
        m_disSeq++;
        if (m_disSeq >= f.numChunks) {
            m_disSeq = 0;
            m_disFragIdx = (m_disFragIdx + 1) % m_carried.size();
        }
    }
    if (m_state != State::DONE)
        m_disEvent = Simulator::Schedule(Seconds(sar::SEND_STAGGER_S),
                                         &SarUavApp::DisseminateTick, this);
}

void SarUavApp::SendFragChunk(uint16_t fragId, uint16_t seq, uint16_t total, FragClass cls) {
    if (!m_device) return;
    uint32_t payloadLen = sar::CHUNK_PAYLOAD;  // opaque bytes (CV not simulated)
    std::vector<uint8_t> buf(sar::DATA_FRAG_HDR + payloadLen, 0);
    uint8_t* p = buf.data();
    *p++ = (uint8_t)MsgType::SAR_DATA_FRAG;
    *p++ = sar::BROADCAST_ID;
    std::memcpy(p, &fragId, 2); p += 2;
    std::memcpy(p, &seq, 2);    p += 2;
    std::memcpy(p, &total, 2);  p += 2;
    *p++ = (uint8_t)cls;
    Ptr<Packet> pkt = Create<Packet>(buf.data(), buf.size());
    bool sent = m_device->Send(pkt, Mac16Address("ff:ff"), 0x00);
    if (sent && m_metrics) m_metrics->AddPacketSent();
}

// ---- emergency response ---------------------------------------------------
void SarUavApp::TryClaimAndDivert(double x, double y) {
    if (m_claimedEvent || m_state == State::DELIVERING) return;
    if (m_claimToken) {
        if (*m_claimToken == -1) *m_claimToken = static_cast<int32_t>(m_nodeId);
        if (*m_claimToken != static_cast<int32_t>(m_nodeId)) return;  // another UAV owns it
    }
    DivertTo(x, y);
}

void SarUavApp::DivertTo(double x, double y) {
    m_claimedEvent = true;
    Vector pos = m_ctrl.GetPosition();
    m_divertTarget = Vector(x, y, m_cruiseAlt);
    m_divertStartDist = std::hypot(x - pos.x, y - pos.y);
    m_state = State::DIVERTING;
    if (m_metrics) {
        m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, RoleStr(m_role),
                         "divert", "to victim cell", pos.x, pos.y, pos.z);
        m_metrics->AddRouteDeviation(m_divertStartDist);
    }
    LogT("sar-uav[" + std::to_string(m_nodeId) + "]")
        << "DIVERT to (" << x << "," << y << ") dist=" << m_divertStartDist << "m";
}

void SarUavApp::DeliverFullData() {
    // Push every chunk of the full dataset to the target, staggered.
    m_deliverFragIdx = 0;
    m_deliverSeq = 0;
    SendFullChunk(0, 0);
}

void SarUavApp::SendFullChunk(size_t fragIdx, uint16_t seq) {
    if (fragIdx >= m_fullset.size()) {
        if (m_deliverMode == DeliverMode::WAYPOINT) {
            // baseline: resume sweep to the next cell
            m_targetIdx++;
            if (m_targetIdx >= m_targets.size()) {
                m_state = State::LANDING;
                m_ctrl.SetClimb(-CLIMB_RATE_MPS);
            } else {
                m_state = State::CRUISING;
                AdvanceToNextTarget();
            }
        } else {
            // proposed summoned delivery finished -> land
            m_state = State::LANDING;
            m_ctrl.SetClimb(-CLIMB_RATE_MPS);
        }
        m_controlEvent = Simulator::Schedule(Seconds(CONTROL_TICK_S), &SarUavApp::ControlTick, this);
        return;
    }
    const sar::Fragment& f = m_fullset[fragIdx];
    if (m_device) {
        std::vector<uint8_t> buf(sar::DATA_FRAG_HDR + sar::CHUNK_PAYLOAD, 0);
        uint8_t* p = buf.data();
        *p++ = (uint8_t)MsgType::FULLDATA_FRAG;
        *p++ = sar::BROADCAST_ID;
        std::memcpy(p, &f.id, 2); p += 2;
        std::memcpy(p, &seq, 2);  p += 2;
        std::memcpy(p, &f.numChunks, 2); p += 2;
        *p++ = (uint8_t)FragClass::FULL;
        Ptr<Packet> pkt = Create<Packet>(buf.data(), buf.size());
        if (m_device->Send(pkt, Mac16Address("ff:ff"), 0x00) && m_metrics)
            m_metrics->AddPacketSent();
    }
    uint16_t nextSeq = seq + 1;
    size_t nextFrag = fragIdx;
    if (nextSeq >= f.numChunks) { nextSeq = 0; nextFrag = fragIdx + 1; }
    Simulator::Schedule(Seconds(DELIVER_STAGGER_S), &SarUavApp::SendFullChunk,
                        this, nextFrag, nextSeq);
}

// ---- RX -------------------------------------------------------------------
bool SarUavApp::OnReceive(Ptr<NetDevice>, Ptr<const Packet> pkt, uint16_t, const Address&) {
    uint32_t sz = pkt->GetSize();
    if (sz < 2) return true;
    std::vector<uint8_t> buf(sz);
    pkt->CopyData(buf.data(), sz);
    uint8_t type = buf[0];

    if (type == (uint8_t)MsgType::EMERGENCY_BEACON && sz >= sar::BEACON_LEN) {
        // [type][0xFF][evtId:u16][cellId:u8][x:i16][y:i16][aoiMs:u16][prio:u8]
        int16_t xdm, ydm;
        std::memcpy(&xdm, &buf[5], 2);
        std::memcpy(&ydm, &buf[7], 2);
        double x = xdm / 10.0, y = ydm / 10.0;
        if (m_scheme != Scheme::PROPOSED) return true;
        if (m_role == UavRole::DATA) {
            TryClaimAndDivert(x, y);
        } else if (m_role == UavRole::FAST) {
            // Relay to DATA UAVs that may be out of the ground node's range.
            std::vector<uint8_t> relay(buf.begin(), buf.end());
            relay[0] = (uint8_t)MsgType::A2A_BEACON_RELAY;
            Ptr<Packet> rp = Create<Packet>(relay.data(), relay.size());
            if (m_device) m_device->Send(rp, Mac16Address("ff:ff"), 0x00);
            if (m_metrics) m_metrics->AddCustodyHandoff();
        }
    } else if (type == (uint8_t)MsgType::A2A_BEACON_RELAY && sz >= sar::BEACON_LEN) {
        int16_t xdm, ydm;
        std::memcpy(&xdm, &buf[5], 2);
        std::memcpy(&ydm, &buf[7], 2);
        if (m_scheme == Scheme::PROPOSED && m_role == UavRole::DATA) {
            TryClaimAndDivert(xdm / 10.0, ydm / 10.0);
        }
    }
    return true;
}

}  // namespace ns3::wsn::uav
