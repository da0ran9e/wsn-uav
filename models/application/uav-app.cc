#include "uav-app.h"
#include "../common/log.h"

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"
#include "ns3/random-variable-stream.h"

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
constexpr double DATA_RATE_BPS          = 250000.0;  // LR-WPAN 2.4GHz O-QPSK
constexpr double MIN_CONTACT_WINDOW_S   = 1.0;       // speed-planning floor only
constexpr uint32_t L0_DATA_HDR       = 5;    // msgType+fragId:u16+subIdx+subTotal
constexpr uint32_t L0_DATA_BYTES     = 92;   // L0 data sub-packet on the air
constexpr uint32_t L0_SEMANTIC_BYTES = 100;  // L0 semantic preamble on the air
}  // namespace

NS_OBJECT_ENSURE_REGISTERED(UavApp);

TypeId UavApp::GetTypeId() {
    static TypeId tid = TypeId("ns3::wsn::uav::UavApp")
                            .SetParent<Application>()
                            .SetGroupName("wsn-uav")
                            .AddConstructor<UavApp>()
                            .AddAttribute("MaxCruiseSpeedMps",
                                          "Maximum horizontal UAV cruise speed in meters per second.",
                                          DoubleValue(20.0),
                                          MakeDoubleAccessor(&UavApp::m_maxCruiseSpeedMps),
                                          MakeDoubleChecker<double>(0.0));
    return tid;
}

UavApp::UavApp()
    : m_nodeId(0),
      // Pre-flight calibration: assumed values matching Scenario1Network radio
      // setup. UAV "knows" these from ground briefing, not from runtime probes.
      m_txPowerDbm(0.0),
      m_rxSensitivityDbm(-95.0),
      m_pathLossExponent(2.2),  // A2G LoS — matches A2GLogDistanceLossModel
      m_refDistance(1.0),
      m_refLossDb(46.6),
      m_broadcastRadius(0.0),
      m_flightPathModel(FlightPathModel::CELL_AWARE_GMC),
      m_broadcastModel(BroadcastModel::CYCLIC),
      m_randomWaypointBudget(64),
      m_cruiseAltitude(20.0),
      m_cruiseSpeed(20.0),
      m_maxCruiseSpeedMps(20.0),
      m_plannedPathLengthMeters(0.0),
      m_takeoffTimeSec(-1.0),
      m_landingTimeSec(-1.0),
      m_appStarted(false),
      m_ctrlAttached(false),
      m_flightScheduled(false),
      m_takeoffPending(false),
      m_topoTotalExpected(0),
      m_topoReceived(0),
      m_targetIdx(0),
      m_bsNodeId(0),
      m_hasBsAddress(false),
      m_topologyComplete(false),
      m_dataComplete(false),
      m_numDataFragmentsExpected(0),
      m_l0BroadcastPeriod(0.0),
      m_l0BroadcastActive(false),
      m_state(FlightState::IDLE) {
}

UavApp::~UavApp() {
}

void UavApp::SetNodeId(uint32_t id) { m_nodeId = id; }
void UavApp::SetNetDevice(Ptr<NetDevice> dev) { m_device = dev; }
void UavApp::SetGroundNodeDestinations(const std::vector<uint32_t>& nodeIds,
                                       const std::vector<Address>& addresses) {
    m_groundNodeIds = nodeIds;
    m_groundNodeAddresses = addresses;
}
void UavApp::SetFlightPathModel(FlightPathModel model) { m_flightPathModel = model; }
void UavApp::SetBroadcastModel(BroadcastModel model) { m_broadcastModel = model; }
void UavApp::SetRandomWaypointBudget(uint32_t budget) { m_randomWaypointBudget = budget; }

const char* UavApp::FlightPathModelName() const {
    switch (m_flightPathModel) {
        case FlightPathModel::CELL_AWARE_GMC: return "cell-aware-gmc";
        case FlightPathModel::PER_NODE_GMC: return "per-node-gmc";
        case FlightPathModel::NEAREST_NEIGHBOR: return "nearest-neighbor";
        case FlightPathModel::CELL_CENTROID_SWEEP: return "cell-centroid-sweep";
        case FlightPathModel::RANDOM_WAYPOINT: return "random-waypoint";
    }
    return "unknown";
}

const char* UavApp::BroadcastModelName() const {
    switch (m_broadcastModel) {
        case BroadcastModel::CYCLIC: return "cyclic";
        case BroadcastModel::RANDOM: return "random";
        case BroadcastModel::UNICAST_FULL: return "unicast-full";
        case BroadcastModel::UTILITY_WEIGHTED: return "utility-weighted";
    }
    return "unknown";
}

double UavApp::ComputeL0AirtimeSeconds(uint32_t packetBytes) const {
    return (packetBytes * 8.0) / DATA_RATE_BPS;
}

void UavApp::StartApplication() {
    m_appStarted = true;
    LogT("UAV") << "started, waiting for topology from BS";
    if (!m_ctrlAttached) {
        m_ctrl.AttachTo(GetNode());
        m_ctrlAttached = true;
    }
    if (m_takeoffPending) {
        MaybeScheduleTakeoff();
    }
}

void UavApp::StopApplication() {
    m_appStarted = false;
    m_takeoffPending = false;
    m_l0BroadcastActive = false;
    m_dissemination.Stop();
    LogT("UAV") << "stopped";
    Simulator::Cancel(m_takeoffEvent);
    Simulator::Cancel(m_broadcastEvent);
    Simulator::Cancel(m_controlEvent);
    m_ctrl.Hover();
    m_ctrl.SetClimb(0.0);
}

void UavApp::TakeOff() {
    if (!m_appStarted || !m_ctrlAttached) {
        m_takeoffPending = (m_topologyComplete && m_dataComplete);
        m_flightScheduled = false;
        LogT("UAV") << "defer takeoff (appStarted=" << (m_appStarted ? 1 : 0)
                    << ", ctrlAttached=" << (m_ctrlAttached ? 1 : 0) << ")";
        return;
    }
    if (m_state != FlightState::IDLE) {
        LogT("UAV") << "ignore takeoff (state=" << static_cast<int>(m_state) << ")";
        return;
    }

    LogT("UAV") << "takeoff: " << m_sensorPositions.size() << " sensors, cruiseZ="
                << m_cruiseAltitude << "m";
    m_takeoffTimeSec = Simulator::Now().GetSeconds();
    m_landingTimeSec = -1.0;

    ComputeBroadcastRadius();
    ComputeFlightSpeed();
    BuildMission();
    UpdatePlannedPathLength();
    if (m_targets.empty()) {
        LogT("UAV") << "no targets, abort takeoff";
        return;
    }

    std::vector<Fragment> l0Fragments;
    for (const Fragment& f : m_dataFragments) {
        if (f.layer == SemanticLayer::IDENTITY_CUE) l0Fragments.push_back(f);
    }
    uint32_t dataSubPackets = 0;
    if (!l0Fragments.empty()) {
        uint32_t fragBytes = l0Fragments.front().sizeBytes;
        uint32_t subPayload = L0_DATA_BYTES - L0_DATA_HDR;
        dataSubPackets = (fragBytes + subPayload - 1) / subPayload;
        if (dataSubPackets == 0) dataSubPackets = 1;
        // Ground reassembly uses a u32 sub-mask, so cap at 32.
        if (dataSubPackets > 32) dataSubPackets = 32;
    }

    UavDisseminationConfig disseminationCfg;
    disseminationCfg.model = m_broadcastModel;
    disseminationCfg.fragments = l0Fragments;
    disseminationCfg.dataSubPacketsPerFragment = dataSubPackets;
    disseminationCfg.sensorPositions = m_sensorPositions;
    disseminationCfg.groundNodeIds = m_groundNodeIds;
    disseminationCfg.groundNodeAddresses = m_groundNodeAddresses;
    disseminationCfg.radiusMeters = m_broadcastRadius;
    m_dissemination.Start(disseminationCfg);

    uint32_t fragBytes = l0Fragments.empty() ? 0u : l0Fragments.front().sizeBytes;
    LogT("UAV") << "search dissemination model=" << m_dissemination.ModelName()
                << ": " << l0Fragments.size()
                << " fragments x " << fragBytes << "B (master "
                << (l0Fragments.size() * fragBytes / 1024) << "KB), "
                << dataSubPackets << " data sub-packets + 1 semantic / fragment";
    if (m_broadcastModel == BroadcastModel::UNICAST_FULL) {
        LogT("UAV") << "full-clip unicast baseline: "
                    << m_sensorPositions.size() << " candidate nodes, "
                    << m_groundNodeAddresses.size() << " known MAC destinations";
    }

    // Begin climb. Heading + horizontal speed stay 0 until we reach cruise alt.
    m_state = FlightState::CLIMBING;
    m_takeoffPending = false;
    m_l0BroadcastActive = m_dissemination.IsActive();
    m_ctrl.Hover();
    m_ctrl.SetClimb(CLIMB_RATE_MPS);
    LogT("UAV") << "CMD climb at " << CLIMB_RATE_MPS << " m/s to " << m_cruiseAltitude << "m";

    m_controlEvent = Simulator::Schedule(Seconds(CONTROL_TICK_S), &UavApp::ControlTick, this);
    LogPosition();
}

void UavApp::ComputeFlightSpeed() {
    // Broadcasts run back-to-back; use the larger (semantic) packet for the
    // conservative period.
    uint32_t pktBytes = std::max(L0_SEMANTIC_BYTES, L0_DATA_BYTES);
    double airtime = ComputeL0AirtimeSeconds(pktBytes);
    m_l0BroadcastPeriod = airtime;

    // Flight speed: a node on the path stays in range 2*r_main/v. Require the
    // window >= MIN_CONTACT_WINDOW_S floor (raw airtime is too small to bind).
    // Planned speed is capped by the physical max.
    double contactWindow = std::max(airtime, MIN_CONTACT_WINDOW_S);
    double plannedSpeed = 2.0 * m_broadcastRadius / contactWindow;
    m_cruiseSpeed = std::min(plannedSpeed, m_maxCruiseSpeedMps);

    LogT("UAV") << "flight speed: L0 packet=" << pktBytes << "B airtime="
                << airtime * 1000.0 << "ms, contact window=" << contactWindow
                << "s, r_main=" << m_broadcastRadius << "m, planned="
                << plannedSpeed << " m/s, max=" << m_maxCruiseSpeedMps
                << " m/s, final=" << m_cruiseSpeed << " m/s";
}

void UavApp::TransmitSearchPacket() {
    if (!m_l0BroadcastActive || !m_device || !m_dissemination.IsActive()) return;

    UavDisseminationPacket tx = m_dissemination.NextPacket(m_ctrl.GetPosition());
    if (tx.valid) {
        Ptr<Packet> pkt = Create<Packet>(tx.payload.data(), tx.payload.size());
        bool sent = m_device->Send(pkt, tx.destination, 0x00);
        m_dissemination.NotifyTxResult(sent);
    }

    if (m_l0BroadcastActive && m_appStarted) {
        m_broadcastEvent = Simulator::Schedule(Seconds(m_l0BroadcastPeriod),
                                               &UavApp::TransmitSearchPacket, this);
    }
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
    LogT("UAV") << "flight path model=" << FlightPathModelName();
    switch (m_flightPathModel) {
        case FlightPathModel::CELL_AWARE_GMC:
            BuildCellAwareGmcMission();
            return;
        case FlightPathModel::PER_NODE_GMC:
            BuildPerNodeGmcMission();
            return;
        case FlightPathModel::NEAREST_NEIGHBOR:
            BuildNearestNeighborMission();
            return;
        case FlightPathModel::CELL_CENTROID_SWEEP:
            BuildCellCentroidSweepMission();
            return;
        case FlightPathModel::RANDOM_WAYPOINT:
            BuildRandomWaypointMission();
            return;
    }
}

void UavApp::BuildCellAwareGmcMission() {
    // Cell-aware GMC (matches example4 scenario4 COOP_GMC):
    //   * Greedy max-coverage at the main broadcast radius.
    //   * Coverage is tracked per node AND per cell.
    //   * When >=CELL_THRESHOLD fraction of a cell's nodes are within r_main of
    //     a chosen waypoint, the entire cell is claimed (its remaining nodes
    //     become "covered" — cooperation will fill them in at runtime).
    //   * Termination: every non-empty cell is claimed.
    m_targets.clear();
    m_targetIdx = 0;

    const size_t N = m_sensorPositions.size();
    if (N == 0 || m_broadcastRadius <= 0.0) {
        LogT("UAV") << "GMC abort: sensors=" << N << " radius=" << m_broadcastRadius;
        return;
    }

    const double rMain  = m_broadcastRadius;
    const double rMain2 = rMain * rMain;
    constexpr double CELL_SIZE_M    = 80.0;  // match Scenario1Config::cellSizeMeters
    constexpr double CELL_THRESHOLD = 0.30;  // 30% rule

    // Precompute per-candidate coverage (main range only).
    std::vector<std::vector<uint32_t>> cov(N);
    for (size_t i = 0; i < N; i++) {
        for (size_t j = 0; j < N; j++) {
            double dx = m_sensorPositions[i].x - m_sensorPositions[j].x;
            double dy = m_sensorPositions[i].y - m_sensorPositions[j].y;
            if (dx * dx + dy * dy <= rMain2) cov[i].push_back(j);
        }
    }

    // Cell mapping: pack (cx, cy) into a uint64 key.
    auto cellKey = [](const Vector& p) -> uint64_t {
        int32_t cx = static_cast<int32_t>(std::floor(p.x / CELL_SIZE_M));
        int32_t cy = static_cast<int32_t>(std::floor(p.y / CELL_SIZE_M));
        return (static_cast<uint64_t>(static_cast<uint32_t>(cx)) << 32) |
                static_cast<uint32_t>(cy);
    };
    std::vector<uint64_t> nodeCell(N);
    std::map<uint64_t, std::vector<uint32_t>> cellMembers;
    for (size_t i = 0; i < N; i++) {
        nodeCell[i] = cellKey(m_sensorPositions[i]);
        cellMembers[nodeCell[i]].push_back(static_cast<uint32_t>(i));
    }
    const size_t totalCells = cellMembers.size();

    std::vector<bool> covered(N, false);
    std::vector<bool> used(N, false);
    std::set<uint64_t> claimedCells;
    size_t coveredCount = 0;
    Vector last = m_ctrl.GetPosition();

    // After any new node is marked covered, sweep cells: any cell whose
    // currently-covered count >= ceil(threshold * size) gets claimed (the rest
    // of its members are marked covered too).
    auto claimSweep = [&]() {
        bool changed = true;
        while (changed) {
            changed = false;
            for (auto& [key, members] : cellMembers) {
                if (claimedCells.count(key)) continue;
                size_t cnt = 0;
                for (uint32_t m : members) if (covered[m]) cnt++;
                size_t needed = static_cast<size_t>(
                    std::ceil(CELL_THRESHOLD * static_cast<double>(members.size())));
                if (cnt >= needed) {
                    for (uint32_t m : members) {
                        if (!covered[m]) { covered[m] = true; coveredCount++; }
                    }
                    claimedCells.insert(key);
                    changed = true;
                }
            }
        }
    };

    auto greedyStep = [&]() -> bool {
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
        if (bestIdx < 0) return false;
        Vector wp(m_sensorPositions[bestIdx].x,
                  m_sensorPositions[bestIdx].y,
                  m_cruiseAltitude);
        m_targets.push_back(wp);
        used[bestIdx] = true;
        for (uint32_t s : cov[bestIdx]) {
            if (!covered[s]) { covered[s] = true; coveredCount++; }
        }
        last = wp;
        claimSweep();
        LogT("UAV") << "GMC pick wp[" << m_targets.size() - 1
                    << "]=(" << wp.x << "," << wp.y << ") gain=" << bestGain
                    << " nodes=" << coveredCount << "/" << N
                    << " cells=" << claimedCells.size() << "/" << totalCells;
        return true;
    };

    while (claimedCells.size() < totalCells) {
        if (!greedyStep()) break;
    }

    LogT("UAV") << "mission built (cell-aware GMC): " << m_targets.size()
                << " waypoints, rMain=" << rMain << "m, cellSize=" << CELL_SIZE_M
                << "m, threshold=" << (CELL_THRESHOLD * 100.0)
                << "%, cells " << claimedCells.size() << "/" << totalCells
                << ", nodes " << coveredCount << "/" << N;
}

void UavApp::BuildPerNodeGmcMission() {
    m_targets.clear();
    m_targetIdx = 0;

    const size_t N = m_sensorPositions.size();
    if (N == 0 || m_broadcastRadius <= 0.0) {
        LogT("UAV") << "GMC abort: sensors=" << N << " radius=" << m_broadcastRadius;
        return;
    }

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
    Vector last = m_ctrl.GetPosition();

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
        if (bestIdx < 0) break;

        Vector wp(m_sensorPositions[bestIdx].x, m_sensorPositions[bestIdx].y, m_cruiseAltitude);
        m_targets.push_back(wp);
        used[bestIdx] = true;
        for (uint32_t s : cov[bestIdx]) {
            if (!covered[s]) { covered[s] = true; coveredCount++; }
        }
        last = wp;
        LogT("UAV") << "per-node GMC pick wp[" << m_targets.size() - 1
                    << "]=(" << wp.x << "," << wp.y << ") gain=" << bestGain
                    << " nodes=" << coveredCount << "/" << N;
    }

    LogT("UAV") << "mission built (per-node GMC): " << m_targets.size()
                << " waypoints, rMain=" << m_broadcastRadius
                << "m, nodes " << coveredCount << "/" << N;
}

void UavApp::BuildNearestNeighborMission() {
    m_targets.clear();
    m_targetIdx = 0;

    const size_t N = m_sensorPositions.size();
    if (N == 0) {
        LogT("UAV") << "nearest-neighbor abort: sensors=0";
        return;
    }

    std::vector<bool> visited(N, false);
    Vector last = m_ctrl.GetPosition();
    for (size_t step = 0; step < N; step++) {
        double bestDist = std::numeric_limits<double>::max();
        int bestIdx = -1;
        for (size_t i = 0; i < N; i++) {
            if (visited[i]) continue;
            double dx = m_sensorPositions[i].x - last.x;
            double dy = m_sensorPositions[i].y - last.y;
            double dist = std::sqrt(dx * dx + dy * dy);
            if (dist < bestDist) {
                bestDist = dist;
                bestIdx = static_cast<int>(i);
            }
        }
        if (bestIdx < 0) break;
        visited[bestIdx] = true;
        Vector wp(m_sensorPositions[bestIdx].x, m_sensorPositions[bestIdx].y, m_cruiseAltitude);
        m_targets.push_back(wp);
        last = wp;
        if (step < 12 || step + 1 == N) {
            LogT("UAV") << "NN pick wp[" << m_targets.size() - 1
                        << "]=(" << wp.x << "," << wp.y << ") dist=" << bestDist;
        }
    }

    LogT("UAV") << "mission built (nearest-neighbor): " << m_targets.size()
                << " waypoints";
}

void UavApp::BuildCellCentroidSweepMission() {
    m_targets.clear();
    m_targetIdx = 0;

    const size_t N = m_sensorPositions.size();
    if (N == 0) {
        LogT("UAV") << "cell-centroid sweep abort: sensors=0";
        return;
    }

    constexpr double CELL_SIZE_M = 80.0;  // match Scenario1Config::cellSizeMeters
    struct CellAgg {
        double sumX = 0.0;
        double sumY = 0.0;
        uint32_t count = 0;
    };
    auto cellKey = [](const Vector& p) -> uint64_t {
        int32_t cx = static_cast<int32_t>(std::floor(p.x / CELL_SIZE_M));
        int32_t cy = static_cast<int32_t>(std::floor(p.y / CELL_SIZE_M));
        return (static_cast<uint64_t>(static_cast<uint32_t>(cx)) << 32) |
               static_cast<uint32_t>(cy);
    };

    std::map<uint64_t, CellAgg> cells;
    for (const Vector& p : m_sensorPositions) {
        CellAgg& agg = cells[cellKey(p)];
        agg.sumX += p.x;
        agg.sumY += p.y;
        agg.count++;
    }

    std::vector<Vector> centroids;
    centroids.reserve(cells.size());
    for (const auto& [_, agg] : cells) {
        if (agg.count == 0) continue;
        centroids.emplace_back(agg.sumX / agg.count,
                               agg.sumY / agg.count,
                               m_cruiseAltitude);
    }

    std::vector<bool> visited(centroids.size(), false);
    Vector last = m_ctrl.GetPosition();
    for (size_t step = 0; step < centroids.size(); ++step) {
        double bestDist = std::numeric_limits<double>::max();
        int bestIdx = -1;
        for (size_t i = 0; i < centroids.size(); ++i) {
            if (visited[i]) continue;
            double dx = centroids[i].x - last.x;
            double dy = centroids[i].y - last.y;
            double dist = std::sqrt(dx * dx + dy * dy);
            if (dist < bestDist) {
                bestDist = dist;
                bestIdx = static_cast<int>(i);
            }
        }
        if (bestIdx < 0) break;
        visited[bestIdx] = true;
        Vector wp = centroids[bestIdx];
        m_targets.push_back(wp);
        last = wp;
        LogT("UAV") << "centroid sweep pick wp[" << m_targets.size() - 1
                    << "]=(" << wp.x << "," << wp.y << ") dist=" << bestDist;
    }

    LogT("UAV") << "mission built (cell-centroid-sweep): " << m_targets.size()
                << " waypoints, cellSize=" << CELL_SIZE_M
                << "m, nonEmptyCells=" << cells.size();
}

void UavApp::BuildRandomWaypointMission() {
    m_targets.clear();
    m_targetIdx = 0;

    const size_t N = m_sensorPositions.size();
    if (N == 0) {
        LogT("UAV") << "random-waypoint abort: sensors=0";
        return;
    }

    constexpr double CELL_SIZE_M = 80.0;  // match Scenario1Config::cellSizeMeters
    std::set<uint64_t> nonEmptyCells;
    double minX = m_sensorPositions.front().x;
    double maxX = m_sensorPositions.front().x;
    double minY = m_sensorPositions.front().y;
    double maxY = m_sensorPositions.front().y;
    auto cellKey = [](const Vector& p) -> uint64_t {
        int32_t cx = static_cast<int32_t>(std::floor(p.x / CELL_SIZE_M));
        int32_t cy = static_cast<int32_t>(std::floor(p.y / CELL_SIZE_M));
        return (static_cast<uint64_t>(static_cast<uint32_t>(cx)) << 32) |
               static_cast<uint32_t>(cy);
    };
    for (const Vector& p : m_sensorPositions) {
        nonEmptyCells.insert(cellKey(p));
        minX = std::min(minX, p.x);
        maxX = std::max(maxX, p.x);
        minY = std::min(minY, p.y);
        maxY = std::max(maxY, p.y);
    }

    uint32_t waypointCount = static_cast<uint32_t>(std::max<size_t>(1, nonEmptyCells.size()));
    if (m_randomWaypointBudget > 0) {
        waypointCount = std::min(waypointCount, m_randomWaypointBudget);
    }
    Ptr<UniformRandomVariable> rng = CreateObject<UniformRandomVariable>();
    // Fixed stream so random-waypoint is reproducible across runs.
    rng->SetStream(20260527);

    for (uint32_t i = 0; i < waypointCount; ++i) {
        double x = rng->GetValue(minX, maxX);
        double y = rng->GetValue(minY, maxY);
        m_targets.emplace_back(x, y, m_cruiseAltitude);
        if (i < 12 || i + 1 == waypointCount) {
            LogT("UAV") << "random waypoint pick wp[" << i
                        << "]=(" << x << "," << y << ")";
        }
    }

    LogT("UAV") << "mission built (random-waypoint): " << m_targets.size()
                << " waypoints, area=[(" << minX << "," << minY
                << ")-(" << maxX << "," << maxY << ")]"
                << ", matchedWaypointBudget=" << waypointCount
                << " budgetCap=" << m_randomWaypointBudget
                << " nonEmptyCells=" << nonEmptyCells.size();
}

void UavApp::UpdatePlannedPathLength() {
    m_plannedPathLengthMeters = 0.0;
    Vector last = m_ctrl.GetPosition();
    for (const Vector& wp : m_targets) {
        double dx = wp.x - last.x;
        double dy = wp.y - last.y;
        m_plannedPathLengthMeters += std::sqrt(dx * dx + dy * dy);
        last = wp;
    }
    LogT("UAV") << "mission cost: waypoints=" << m_targets.size()
                << " plannedPath=" << m_plannedPathLengthMeters
                << "m cruiseSpeed=" << m_cruiseSpeed << "m/s"
                << " plannedCruiseTime="
                << (m_cruiseSpeed > 0.0 ? m_plannedPathLengthMeters / m_cruiseSpeed : 0.0)
                << "s";
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
                if (m_l0BroadcastActive) {
                    TransmitSearchPacket();
                }
            }
            break;
        }
        case FlightState::CRUISING: {
            Vector tgt = m_targets[m_targetIdx];
            double dx = tgt.x - pos.x;
            double dy = tgt.y - pos.y;
            double dist = std::sqrt(dx * dx + dy * dy);
            // Arrival: inside the radius, OR the UAV has flown past the target
            // (it now lies behind the heading vector). The overshoot test is
            // required at high speed, where one control tick can step further
            // than ARRIVAL_RADIUS_M.
            double hRad = m_ctrl.GetHeadingDeg() * M_PI / 180.0;
            double ahead = dx * std::cos(hRad) + dy * std::sin(hRad);
            if (dist <= ARRIVAL_RADIUS_M || ahead <= 0.0) {
                LogT("UAV") << "reached target[" << m_targetIdx << "] (dist="
                            << dist << "m)";
                m_targetIdx++;
                if (m_targetIdx >= m_targets.size()) {
                    LogT("UAV") << "mission complete, begin landing";
                    m_state = FlightState::LANDING;
                    m_ctrl.Hover();
                    m_ctrl.SetClimb(-CLIMB_RATE_MPS);
                    if (m_l0BroadcastActive) {
                        m_l0BroadcastActive = false;
                        m_dissemination.Stop();
                        Simulator::Cancel(m_broadcastEvent);
                        LogT("UAV") << "search broadcast stopped at mission end: "
                                    << m_dissemination.TxSuccessCount() << "/"
                                    << m_dissemination.TxAttemptCount()
                                    << " packets sent OK";
                    }
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
                m_l0BroadcastActive = false;
                m_dissemination.Stop();
                m_state = FlightState::DONE;
                m_landingTimeSec = Simulator::Now().GetSeconds();
                LogT("UAV") << "landed at (" << pos.x << "," << pos.y << "," << pos.z << ")";
                LogT("UAV") << "flight complete: duration=" << FlightDurationSec()
                            << "s, plannedPath=" << m_plannedPathLengthMeters
                            << "m, waypoints=" << m_targets.size()
                            << ", searchPackets=" << m_dissemination.TxSuccessCount();
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
    if (complete || !sent) {
        LogT("UAV") << "TX topology ACK " << m_topoReceived << "/"
                    << m_sensorPositions.size()
                    << " complete=" << (complete ? 1 : 0)
                    << " sent=" << (sent ? "OK" : "FAIL");
    }
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
    if (msgType == static_cast<uint8_t>(MsgType::TOPO_ACK) ||
        msgType == static_cast<uint8_t>(MsgType::DATA_ACK)) {
        LogT("UAV") << "ignore incoming ACK (msgType=" << static_cast<int>(msgType) << ")";
        return true;
    }
    if (msgType == static_cast<uint8_t>(MsgType::DATA_FRAGMENT)) {
        ProcessDataFragment(buf, from);
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
        LogT("UAV") << "topology complete (" << m_topoReceived << "/"
                    << m_sensorPositions.size() << " sensors stored)";
        MaybeScheduleTakeoff();
    }
    return true;
}

void UavApp::ProcessDataFragment(const std::vector<uint8_t>& buf,
                                 const ns3::Address& from) {
    // Data packet header (16B):
    // [msgType:u8][destId:u8][numFragments:u8][fragId:u8][fragLayer:u8]
    // [utilityMilli:u16][fragTotalBytes:u32][chunkOffset:u32][chunkLen:u8]
    constexpr uint32_t DHDR = 1 + 1 + 1 + 1 + 1 + 2 + 4 + 4 + 1;
    uint32_t pktSize = buf.size();
    if (pktSize < DHDR) {
        LogT("UAV") << "drop data packet (size=" << pktSize << "B < header)";
        return;
    }

    const uint8_t* p = buf.data() + 1;  // skip msgType
    uint8_t destId       = *p++;
    uint8_t numFragments = *p++;
    uint8_t fragId       = *p++;
    uint8_t fragLayer    = *p++;
    uint16_t utilMilli;     std::memcpy(&utilMilli, p, 2);     p += 2;
    uint32_t fragTotalBytes; std::memcpy(&fragTotalBytes, p, 4); p += 4;
    uint32_t chunkOffset;   std::memcpy(&chunkOffset, p, 4);   p += 4;
    uint8_t chunkLen     = *p++;

    if (destId != m_nodeId) {
        LogT("UAV") << "drop data packet (destId=" << (int)destId << " not me)";
        return;
    }
    if (pktSize != DHDR + chunkLen) {
        LogT("UAV") << "drop data packet (size mismatch: pkt=" << pktSize
                    << " expected=" << (DHDR + chunkLen) << ")";
        return;
    }
    if (numFragments == 0 || fragId >= numFragments) {
        LogT("UAV") << "drop data packet (bad fragId=" << (int)fragId
                    << " numFragments=" << (int)numFragments << ")";
        return;
    }

    m_bsAddress = from;
    m_hasBsAddress = true;

    if (m_numDataFragmentsExpected == 0) {
        m_numDataFragmentsExpected = numFragments;
        m_dataFragments.assign(numFragments, Fragment{});
        m_fragReceivedBytes.assign(numFragments, 0);
        m_fragReceivedOffsets.assign(numFragments, std::set<uint32_t>{});
        m_fragSeen.assign(numFragments, false);
    } else if (m_numDataFragmentsExpected != numFragments) {
        LogT("UAV") << "drop data packet (numFragments mismatch)";
        return;
    }

    if (!m_fragSeen[fragId]) {
        m_fragSeen[fragId] = true;
        Fragment f;
        f.id        = fragId;
        f.layer     = static_cast<SemanticLayer>(fragLayer);
        f.utility   = utilMilli / 1000.0;
        f.sizeBytes = fragTotalBytes;
        m_dataFragments[fragId] = f;
    }

    // Out-of-order tolerant: dedupe by chunk offset. Realistic PHY (Nakagami
    // + shadowing) drops occasional sub-packets, so an in-order-only accept
    // would stall fragments forever. MAC retries already handle most loss,
    // but the reassembly must accept the rest in any order.
    if (m_fragReceivedOffsets[fragId].insert(chunkOffset).second) {
        m_fragReceivedBytes[fragId] += chunkLen;
    }

    uint32_t completeFrags = 0;
    for (uint32_t i = 0; i < m_numDataFragmentsExpected; i++) {
        if (m_fragSeen[i] && m_fragReceivedBytes[i] >= m_dataFragments[i].sizeBytes) {
            completeFrags++;
        }
    }
    bool dataComplete = (completeFrags == m_numDataFragmentsExpected);
    (void)fragLayer; (void)fragTotalBytes;

    SendDataAck(static_cast<uint16_t>(fragId),
                chunkOffset,
                static_cast<uint16_t>(chunkLen),
                completeFrags,
                dataComplete);

    if (dataComplete && !m_dataComplete) {
        m_dataComplete = true;
        uint32_t totalBytes = 0;
        for (const Fragment& f : m_dataFragments) totalBytes += f.sizeBytes;
        LogT("UAV") << "fragment data complete: " << m_numDataFragmentsExpected
                    << " fragments, " << totalBytes << "B";
        MaybeScheduleTakeoff();
    }
}

void UavApp::SendDataAck(uint16_t fragId,
                         uint32_t chunkOffset,
                         uint16_t chunkLen,
                         uint32_t fragmentsComplete,
                         bool complete) {
    if (!m_device || !m_hasBsAddress) {
        LogT("UAV") << "skip data ACK (missing BS address)";
        return;
    }
    constexpr uint32_t ACK_SIZE = 1 + 1 + 2 + 4 + 2 + 2 + 2 + 1;
    std::vector<uint8_t> buf(ACK_SIZE);
    uint8_t* p = buf.data();
    *p++ = static_cast<uint8_t>(MsgType::DATA_ACK);
    *p++ = m_bsNodeId;
    std::memcpy(p, &fragId, sizeof(fragId)); p += sizeof(fragId);
    std::memcpy(p, &chunkOffset, sizeof(chunkOffset)); p += sizeof(chunkOffset);
    std::memcpy(p, &chunkLen, sizeof(chunkLen)); p += sizeof(chunkLen);
    uint16_t fc = static_cast<uint16_t>(
        std::min<uint32_t>(fragmentsComplete, std::numeric_limits<uint16_t>::max()));
    uint16_t ft = static_cast<uint16_t>(
        std::min<uint32_t>(m_numDataFragmentsExpected, std::numeric_limits<uint16_t>::max()));
    std::memcpy(p, &fc, 2); p += 2;
    std::memcpy(p, &ft, 2); p += 2;
    *p++ = complete ? 1 : 0;

    Ptr<Packet> ack = Create<Packet>(buf.data(), buf.size());
    bool sent = m_device->Send(ack, m_bsAddress, 0x00);
    if (complete || !sent) {
        LogT("UAV") << "TX data ACK fragmentsComplete=" << fragmentsComplete << "/"
                    << m_numDataFragmentsExpected
                    << " complete=" << (complete ? 1 : 0)
                    << " sent=" << (sent ? "OK" : "FAIL");
    }
    (void)fragId; (void)chunkOffset; (void)chunkLen;
}

void UavApp::MaybeScheduleTakeoff() {
    if (m_flightScheduled) return;
    if (!m_topologyComplete || !m_dataComplete) return;
    if (!m_appStarted || !m_ctrlAttached) {
        m_takeoffPending = true;
        LogT("UAV") << "takeoff ready, waiting for app start/controller attach";
        return;
    }
    m_flightScheduled = true;
    constexpr double prepDelay = 2.0;
    m_takeoffEvent = Simulator::Schedule(Seconds(prepDelay), &UavApp::TakeOff, this);
    LogT("UAV") << "topology + data complete, flight scheduled in "
                << prepDelay << "s";
}

}  // namespace ns3::wsn::uav
