#include "uav-app.h"
#include "../common/log.h"

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"

#include <algorithm>
#include <cmath>
#include <cstring>
#include <limits>
#include <vector>

using namespace ns3;

namespace ns3::wsn::uav {

namespace {
constexpr double CONTROL_TICK_S    = 0.1;   // autopilot loop period
constexpr double ARRIVAL_RADIUS_M  = 1.0;   // "close enough" threshold to switch target
constexpr double CLIMB_RATE_MPS    = 5.0;   // vertical speed during CLIMBING / LANDING
constexpr double LOG_POS_PERIOD_S  = 2.0;
constexpr double GMC_ALPHA         = 1.0;   // cost weight in GMC scoring
}  // namespace

NS_OBJECT_ENSURE_REGISTERED(UavApp);

TypeId UavApp::GetTypeId() {
    static TypeId tid = TypeId("ns3::wsn::uav::UavApp")
                            .SetParent<Application>()
                            .SetGroupName("wsn-uav")
                            .AddConstructor<UavApp>();
    return tid;
}

UavApp::UavApp()
    : m_nodeId(0),
      m_broadcastInterval(1.0),
      m_numFragments(10),
      m_nextFragIdx(0),
      // Pre-flight calibration: assumed values matching Scenario1Network radio
      // setup. UAV "knows" these from ground briefing, not from runtime probes.
      m_txPowerDbm(0.0),
      m_rxSensitivityDbm(-95.0),
      m_pathLossExponent(3.0),
      m_refDistance(1.0),
      m_refLossDb(46.6),
      m_broadcastRadius(0.0),
      m_cruiseAltitude(20.0),
      m_cruiseSpeed(20.0),
      m_flightScheduled(false),
      m_topoTotalExpected(0),
      m_topoReceived(0),
      m_targetIdx(0),
      m_bsNodeId(0),
      m_hasBsAddress(false),
      m_topologyComplete(false),
      m_state(FlightState::IDLE) {
}

UavApp::~UavApp() {
}

void UavApp::SetNodeId(uint32_t id) { m_nodeId = id; }
void UavApp::SetNetDevice(Ptr<NetDevice> dev) { m_device = dev; }
void UavApp::SetBroadcastInterval(double interval) { m_broadcastInterval = interval; }
void UavApp::SetNumFragments(uint32_t count) { m_numFragments = count; }

void UavApp::StartApplication() {
    LogT("UAV") << "started, waiting for topology from BS";
    m_ctrl.AttachTo(GetNode());
}

void UavApp::StopApplication() {
    LogT("UAV") << "stopped";
    Simulator::Cancel(m_broadcastEvent);
    Simulator::Cancel(m_controlEvent);
    m_ctrl.Hover();
    m_ctrl.SetClimb(0.0);
}

void UavApp::TakeOff() {
    LogT("UAV") << "takeoff: " << m_sensorPositions.size() << " sensors, cruiseZ="
                << m_cruiseAltitude << "m";

    ComputeBroadcastRadius();
    BuildMission();
    if (m_targets.empty()) {
        LogT("UAV") << "no targets, abort takeoff";
        return;
    }

    // Begin climb. Heading + horizontal speed stay 0 until we reach cruise alt.
    m_state = FlightState::CLIMBING;
    m_ctrl.Hover();
    m_ctrl.SetClimb(CLIMB_RATE_MPS);
    LogT("UAV") << "CMD climb at " << CLIMB_RATE_MPS << " m/s to " << m_cruiseAltitude << "m";

    m_controlEvent = Simulator::Schedule(Seconds(CONTROL_TICK_S), &UavApp::ControlTick, this);
    LogPosition();
}

void UavApp::ComputeBroadcastRadius() {
    // Solve LogDistance for the distance at which RX power == sensitivity:
    //   PL(d) = refLoss + 10 n log10(d / refDist)
    //   RxPower = TxPower - PL(d_max) = sensitivity
    //   => d_max = refDist * 10^((TxPower - sensitivity - refLoss) / (10 n))
    // UAV altitude is included implicitly because the GMC distance check
    // uses 2D ground distance (the equation gives the slant range); at
    // altitude=20m and d_max ~50m the horizontal coverage radius is
    // sqrt(d_max^2 - alt^2). We keep the slant-range conservative-bound here.
    double exponent = (m_txPowerDbm - m_rxSensitivityDbm - m_refLossDb)
                       / (10.0 * m_pathLossExponent);
    double slant = m_refDistance * std::pow(10.0, exponent);
    double horiz = (slant > m_cruiseAltitude)
                       ? std::sqrt(slant * slant - m_cruiseAltitude * m_cruiseAltitude)
                       : 0.0;
    m_broadcastRadius = horiz;
    LogT("UAV") << "broadcast radius: slant=" << slant << "m, horizontal@"
                << m_cruiseAltitude << "m=" << horiz
                << "m (n=" << m_pathLossExponent << ", refLoss=" << m_refLossDb
                << "dB, TxP=" << m_txPowerDbm << "dBm, RxS=" << m_rxSensitivityDbm << "dBm)";
}

void UavApp::BuildMission() {
    // Simplified GMC: greedy maximum coverage over sensor positions.
    //   candidates = all sensor positions (lifted to cruise altitude)
    //   while not all sensors covered:
    //     pick c maximizing  |cov(c)\covered| / (1 + alpha * dist(last,c)/speed)
    m_targets.clear();
    m_targetIdx = 0;

    const size_t N = m_sensorPositions.size();
    if (N == 0 || m_broadcastRadius <= 0.0) {
        LogT("UAV") << "GMC abort: sensors=" << N << " radius=" << m_broadcastRadius;
        return;
    }

    // Precompute coverage sets cov[i] = sensors within radius of candidate i.
    // Candidate i is at sensor i's (x,y) at cruise altitude.
    const double r2 = m_broadcastRadius * m_broadcastRadius;
    std::vector<std::vector<uint32_t>> cov(N);
    for (size_t i = 0; i < N; i++) {
        for (size_t j = 0; j < N; j++) {
            double dx = m_sensorPositions[i].x - m_sensorPositions[j].x;
            double dy = m_sensorPositions[i].y - m_sensorPositions[j].y;
            if (dx * dx + dy * dy <= r2) cov[i].push_back(j);
        }
    }

    std::vector<bool> covered(N, false);
    std::vector<bool> used(N, false);
    size_t coveredCount = 0;
    Vector last = m_ctrl.GetPosition();  // current UAV pos (post-climb cruise alt)

    while (coveredCount < N) {
        double bestScore = -1.0;
        int bestIdx = -1;
        uint32_t bestGain = 0;
        for (size_t i = 0; i < N; i++) {
            if (used[i]) continue;
            uint32_t gain = 0;
            for (uint32_t s : cov[i]) if (!covered[s]) gain++;
            if (gain == 0) continue;
            double dx = m_sensorPositions[i].x - last.x;
            double dy = m_sensorPositions[i].y - last.y;
            double dist = std::sqrt(dx * dx + dy * dy);
            double score = static_cast<double>(gain)
                           / (1.0 + GMC_ALPHA * dist / m_cruiseSpeed);
            if (score > bestScore) {
                bestScore = score;
                bestIdx = static_cast<int>(i);
                bestGain = gain;
            }
        }
        if (bestIdx < 0) break;  // no remaining gain — shouldn't happen if r>0
        Vector wp(m_sensorPositions[bestIdx].x,
                  m_sensorPositions[bestIdx].y,
                  m_cruiseAltitude);
        m_targets.push_back(wp);
        used[bestIdx] = true;
        for (uint32_t s : cov[bestIdx]) {
            if (!covered[s]) { covered[s] = true; coveredCount++; }
        }
        last = wp;
        LogT("UAV") << "GMC pick wp[" << m_targets.size() - 1 << "]=("
                    << wp.x << "," << wp.y << ") gain=" << bestGain
                    << " covered=" << coveredCount << "/" << N;
    }

    LogT("UAV") << "mission built (GMC): " << m_targets.size() << " waypoints, "
                << "broadcast radius=" << m_broadcastRadius << "m, covered "
                << coveredCount << "/" << N << " sensors";
}

bool UavApp::AdvanceToNextTarget() {
    if (m_targetIdx >= m_targets.size()) return false;

    Vector pos = m_ctrl.GetPosition();
    Vector tgt = m_targets[m_targetIdx];
    double dx = tgt.x - pos.x;
    double dy = tgt.y - pos.y;
    double headingDeg = std::atan2(dy, dx) * 180.0 / M_PI;

    m_ctrl.Turn(headingDeg);
    m_ctrl.Forward(m_cruiseSpeed);
    LogT("UAV") << "CMD turn " << headingDeg << "° + forward " << m_cruiseSpeed
                << " m/s -> target[" << m_targetIdx << "]=("
                << tgt.x << "," << tgt.y << ")";
    return true;
}

void UavApp::ControlTick() {
    Vector pos = m_ctrl.GetPosition();

    switch (m_state) {
        case FlightState::CLIMBING: {
            if (pos.z >= m_cruiseAltitude) {
                m_ctrl.SetClimb(0.0);
                LogT("UAV") << "reached cruise altitude " << pos.z << "m, begin sweep";
                m_state = FlightState::CRUISING;
                AdvanceToNextTarget();
            }
            break;
        }
        case FlightState::CRUISING: {
            Vector tgt = m_targets[m_targetIdx];
            double dx = tgt.x - pos.x;
            double dy = tgt.y - pos.y;
            double dist = std::sqrt(dx * dx + dy * dy);
            if (dist <= ARRIVAL_RADIUS_M) {
                LogT("UAV") << "reached target[" << m_targetIdx << "] (dist="
                            << dist << "m)";
                m_targetIdx++;
                if (m_targetIdx >= m_targets.size()) {
                    LogT("UAV") << "mission complete, begin landing";
                    m_state = FlightState::LANDING;
                    m_ctrl.Hover();
                    m_ctrl.SetClimb(-CLIMB_RATE_MPS);
                } else {
                    AdvanceToNextTarget();
                }
            }
            break;
        }
        case FlightState::LANDING: {
            if (pos.z <= 0.1) {
                m_ctrl.SetClimb(0.0);
                m_ctrl.Hover();
                m_state = FlightState::DONE;
                LogT("UAV") << "landed at (" << pos.x << "," << pos.y << "," << pos.z << ")";
                return;  // stop scheduling
            }
            break;
        }
        case FlightState::IDLE:
        case FlightState::DONE:
            return;
    }

    m_controlEvent = Simulator::Schedule(Seconds(CONTROL_TICK_S), &UavApp::ControlTick, this);
}

void UavApp::LogPosition() {
    Vector p = m_ctrl.GetPosition();
    LogT("UAV") << "pos=(" << p.x << "," << p.y << "," << p.z
                << ") heading=" << m_ctrl.GetHeadingDeg()
                << "° speed=" << m_ctrl.GetSpeedMps()
                << " m/s vz=" << m_ctrl.GetClimbMps() << " m/s";
    if (m_state != FlightState::DONE) {
        Simulator::Schedule(Seconds(LOG_POS_PERIOD_S), &UavApp::LogPosition, this);
    }
}

void UavApp::DoBroadcast() {
    LogT("UAV") << "TX fragment #" << m_nextFragIdx;
    m_nextFragIdx++;
    if (m_nextFragIdx < m_numFragments) {
        m_broadcastEvent = Simulator::Schedule(Seconds(m_broadcastInterval), &UavApp::DoBroadcast, this);
    }
}

void UavApp::SendTopologyAck(bool complete) {
    if (!m_device || !m_hasBsAddress) {
        LogT("UAV") << "skip topology ACK (missing BS address)";
        return;
    }

    constexpr uint32_t ACK_HDR = 1 + 1 + 2 + 2 + 1;
    std::vector<uint8_t> buf(ACK_HDR);
    uint8_t* p = buf.data();
    *p++ = static_cast<uint8_t>(MsgType::TOPO_ACK);
    *p++ = m_bsNodeId;

    uint16_t receivedSensors = static_cast<uint16_t>(
        std::min<uint32_t>(m_topoReceived, std::numeric_limits<uint16_t>::max()));
    uint16_t totalSensors = static_cast<uint16_t>(
        std::min<uint32_t>(m_sensorPositions.size(), std::numeric_limits<uint16_t>::max()));
    std::memcpy(p, &receivedSensors, sizeof(receivedSensors)); p += sizeof(receivedSensors);
    std::memcpy(p, &totalSensors, sizeof(totalSensors)); p += sizeof(totalSensors);
    *p++ = complete ? 1 : 0;

    Ptr<Packet> ack = Create<Packet>(buf.data(), buf.size());
    bool sent = m_device->Send(ack, m_bsAddress, 0x00);
    LogT("UAV") << "TX topology ACK progress=" << m_topoReceived
                << "/" << m_sensorPositions.size()
                << " complete=" << (complete ? 1 : 0)
                << " sent=" << (sent ? "OK" : "FAIL");
}

bool UavApp::OnMessageReceived(ns3::Ptr<ns3::NetDevice> dev,
                               ns3::Ptr<const ns3::Packet> pkt,
                               uint16_t proto,
                               const ns3::Address& from) {
    (void)dev;
    (void)proto;
    uint32_t pktSize = pkt->GetSize();
    // Topology packet header:
    // [msgType:u8][destId:u8][totalCount:u16][thisCount:u8][startIdx:u16] = 7B
    constexpr uint32_t HDR   = 1 + 1 + 2 + 1 + 2;
    constexpr uint32_t ENTRY = 1 + 6;

    if (pktSize < 1) {
        LogT("UAV") << "RX packet (empty payload)";
        return true;
    }

    std::vector<uint8_t> buf(pktSize);
    pkt->CopyData(buf.data(), pktSize);
    const uint8_t* p = buf.data();
    uint8_t msgType = *p++;
    if (msgType == static_cast<uint8_t>(MsgType::TOPO_ACK)) {
        LogT("UAV") << "ignore incoming topology ACK";
        return true;
    }
    if (msgType != static_cast<uint8_t>(MsgType::TOPO_FRAGMENT)) {
        LogT("UAV") << "drop packet (unsupported msgType=" << static_cast<int>(msgType) << ")";
        return true;
    }
    if (pktSize < HDR + ENTRY) {
        LogT("UAV") << "RX packet (size=" << pktSize << "B, too small for topology)";
        return true;
    }

    uint8_t destId = *p++;
    uint16_t totalCount;
    std::memcpy(&totalCount, p, 2); p += 2;
    uint8_t thisCount = *p++;
    uint16_t startIdx;
    std::memcpy(&startIdx, p, 2); p += 2;

    if (destId != m_nodeId) {
        LogT("UAV") << "drop packet (destId=" << (int)destId << " not me)";
        return true;
    }
    if (pktSize != HDR + thisCount * ENTRY) {
        LogT("UAV") << "drop packet (size mismatch: pkt=" << pktSize
                    << " expected=" << (HDR + thisCount * ENTRY) << ")";
        return true;
    }
    if (startIdx + thisCount > totalCount) {
        LogT("UAV") << "drop packet (fragment range exceeds totalCount)";
        return true;
    }

    m_bsAddress = from;
    m_hasBsAddress = true;

    // First fragment we see: size the buffer for the full topology. Index 0
    // and 1 are BS and UAV; everything from index 2 onward is a sensor.
    // We allocate a sparse marker vector so we can detect duplicates and
    // accept fragments in any order.
    if (m_topoTotalExpected == 0) {
        m_topoTotalExpected = totalCount;
        // Each sensor's position is stored only if its absolute index >= 2.
        // Reserve enough slots; we'll fill them by absolute index.
        m_sensorPositions.assign(totalCount >= 2 ? totalCount - 2 : 0,
                                  Vector(0, 0, 0));
        m_sensorSlotFilled.assign(m_sensorPositions.size(), false);
        m_topoReceived = 0;
    } else if (m_topoTotalExpected != totalCount) {
        LogT("UAV") << "drop packet (totalCount mismatch)";
        return true;
    }

    LogT("UAV") << "RX topology fragment start=" << startIdx
                << " count=" << (int)thisCount << " (total=" << totalCount << ")";

    for (uint32_t i = 0; i < thisCount; i++) {
        uint8_t id = *p++;
        int16_t xdm, ydm, zdm;
        std::memcpy(&xdm, p, 2); p += 2;
        std::memcpy(&ydm, p, 2); p += 2;
        std::memcpy(&zdm, p, 2); p += 2;
        double x = xdm / 10.0;
        double y = ydm / 10.0;
        double z = zdm / 10.0;
        uint32_t absIdx = startIdx + i;
        if (absIdx == 0) {
            m_bsNodeId = id;
        }
        if (absIdx >= 2 && absIdx - 2 < m_sensorPositions.size()) {
            uint32_t sensorIdx = absIdx - 2;
            m_sensorPositions[sensorIdx] = Vector(x, y, z);
            if (!m_sensorSlotFilled[sensorIdx]) {
                m_sensorSlotFilled[sensorIdx] = true;
                m_topoReceived++;
            }
        }
    }

    bool completeNow = (m_topoReceived >= m_sensorPositions.size());
    SendTopologyAck(completeNow);

    if (completeNow && !m_topologyComplete) {
        m_topologyComplete = true;
    }

    if (completeNow && !m_flightScheduled) {
        m_flightScheduled = true;
        constexpr double prepDelay = 2.0;
        Simulator::Schedule(Seconds(prepDelay), &UavApp::TakeOff, this);
        LogT("UAV") << "topology complete (" << m_topoReceived << "/"
                    << m_sensorPositions.size()
                    << "), " << m_sensorPositions.size()
                    << " sensors stored, flight scheduled in " << prepDelay << "s";
    }
    return true;
}

}  // namespace ns3::wsn::uav
