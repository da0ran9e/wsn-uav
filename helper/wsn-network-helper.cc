#include "wsn-network-helper.h"
#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"
#include "ns3/cc2420-helper.h"
#include "ns3/cc2420-net-device.h"
#include "ns3/cc2420-mac.h"
#include "../models/application/fragment-dissemination-app.h"
#include "../models/common/parameters.h"
#include <cmath>

NS_LOG_COMPONENT_DEFINE("WsnNetworkHelper");

namespace ns3 {
namespace wsn {
namespace uav {

// ============================================================================
// SimulationConfig::Validate()
// ============================================================================

bool SimulationConfig::Validate(std::string& errMsg) const {
    if (gridSize < 2) {
        errMsg = "gridSize must be >= 2";
        return false;
    }
    if (gridSpacing <= 0) {
        errMsg = "gridSpacing must be > 0";
        return false;
    }
    if (numFragments < 1) {
        errMsg = "numFragments must be >= 1";
        return false;
    }
    if (uavSpeed <= 0) {
        errMsg = "uavSpeed must be > 0";
        return false;
    }
    if (alertThreshold < cooperationThreshold) {
        errMsg = "alertThreshold must be >= cooperationThreshold";
        return false;
    }
    if (suspiciousPercent <= 0 || suspiciousPercent > 1) {
        errMsg = "suspiciousPercent must be in (0, 1]";
        return false;
    }
    return true;
}

// ============================================================================
// WsnNetworkHelper Constructor
// ============================================================================

WsnNetworkHelper::WsnNetworkHelper(const SimulationConfig& config)
    : m_config(config) {
    m_stats = CreateObject<StatisticsCollector>();
    
    // Set random seed
    RngSeedManager::SetSeed(config.seed);
}

WsnNetworkHelper::~WsnNetworkHelper() {}

// ============================================================================
// WsnNetworkHelper::Build()
// ============================================================================

void WsnNetworkHelper::Build() {
    NS_LOG_INFO("Building network: " << m_config.gridSize << "x" << m_config.gridSize 
                << " nodes, " << m_config.numFragments << " fragments");
    
    CreateNodes();
    InstallRadios();
    BuildTopology();
    SelectCandidatesAndFragments();
    PlanTrajectory();
    InstallApplications();
    
    m_results.totalNodes = m_groundNodes.GetN();
    m_results.candidateNodes = m_candidateNodes.size();
}

// ============================================================================
// WsnNetworkHelper::CreateNodes()
// ============================================================================

void WsnNetworkHelper::CreateNodes() {
    // Create ground nodes in grid
    m_groundNodes = TopologyHelper::CreateGrid(m_config.gridSize, m_config.gridSpacing, 0.0);

    // Create UAV node at altitude
    m_uavNode = CreateObject<Node>();
    MobilityHelper mobility;
    mobility.SetMobilityModel("ns3::WaypointMobilityModel");
    mobility.Install(NodeContainer(m_uavNode));

    // Calculate UAV starting position: 200m OUTSIDE network boundary (negative coordinates - south)
    double gridDiameter = (m_config.gridSize - 1) * m_config.gridSpacing;
    double centerX = gridDiameter / 2.0;

    // Start 200m south of network (negative Y)
    Vector initialUavPos(centerX, -200.0, m_config.uavAltitude);

    auto uavMobility = m_uavNode->GetObject<MobilityModel>();
    uavMobility->SetPosition(initialUavPos);

    NS_LOG_INFO("Created " << m_groundNodes.GetN() << " ground nodes + 1 UAV");
    NS_LOG_INFO("UAV initial position: (" << initialUavPos.x << ", " << initialUavPos.y << ", " << initialUavPos.z << ")");
}

// ============================================================================
// WsnNetworkHelper::InstallRadios()
// ============================================================================

void WsnNetworkHelper::InstallRadios() {
    // Use CC2420 from wsn module
    wsn::Cc2420Helper cc2420;

    // Create channel
    auto channel = cc2420.CreateChannel();

    // Configure PHY
    cc2420.SetPhyAttribute("TxPower", DoubleValue(params::TX_POWER_DBM));
    cc2420.SetPhyAttribute("RxSensitivity", DoubleValue(params::RX_SENSITIVITY_DBM));
    cc2420.SetPhyAttribute("PerfectChannel", BooleanValue(m_config.usePerfectChannel));
    cc2420.SetPhyAttribute("EnableShadowing", BooleanValue(!m_config.usePerfectChannel));

    cc2420.SetChannel(channel);

    // Install on nodes
    m_groundDevices = cc2420.Install(m_groundNodes);
    m_uavDevices = cc2420.Install(NodeContainer(m_uavNode));

    NS_LOG_INFO("Radios installed on " << m_groundNodes.GetN() << " ground nodes + UAV");
}

// ============================================================================
// WsnNetworkHelper::BuildTopology()
// ============================================================================

void WsnNetworkHelper::BuildTopology() {
    m_cellInfo = TopologyHelper::BuildCellStructure(m_groundNodes, params::HEX_CELL_RADIUS);
    NS_LOG_INFO("Cell structure built");
}

// ============================================================================
// WsnNetworkHelper::SelectCandidatesAndFragments()
// ============================================================================

void WsnNetworkHelper::SelectCandidatesAndFragments() {
    // Select candidate nodes (suspicious region)
    m_candidateNodes = TopologyHelper::SelectCandidates(
        m_groundNodes, m_cellInfo, m_config.suspiciousPercent, m_config.seed);

    // Store candidate node IDs in results for later use (survives Simulator::Destroy())
    m_results.candidateNodeIds = m_candidateNodes;

    // Pick detection node (n* = suspicious seed)
    m_detectionNodeId = TopologyHelper::SelectDetectionNode(m_candidateNodes, m_config.seed);
    m_results.detectionNodeId = m_detectionNodeId;

    // Generate fragments
    m_fragments = FragmentCollection::Generate(m_config.numFragments);
    m_results.fragmentsFromUav = 0;  // Will accumulate during sim

    NS_LOG_INFO("Selected " << m_candidateNodes.size() << " candidate nodes");
    NS_LOG_INFO("Detection node (n*) = " << m_detectionNodeId);
    NS_LOG_INFO("Generated " << m_config.numFragments << " fragments");
}

// ============================================================================
// WsnNetworkHelper::PlanTrajectory()
// ============================================================================

void WsnNetworkHelper::PlanTrajectory() {
    // Calculate UAV starting position: 200m OUTSIDE network boundary (negative coordinates - south)
    double gridDiameter = (m_config.gridSize - 1) * m_config.gridSpacing;
    double centerX = gridDiameter / 2.0;

    // Start 200m south of network (negative Y)
    Vector startPos(centerX, -200.0, m_config.uavAltitude);

    NS_LOG_INFO("UAV starting position: (" << startPos.x << ", " << startPos.y << ", " << startPos.z << ")");
    NS_LOG_INFO("Network bounds: X[0, " << gridDiameter << "], Y[0, " << gridDiameter << "]");
    NS_LOG_INFO("UAV position: OUTSIDE network (Y = " << startPos.y << "m < 0)");
    NS_LOG_INFO("UAV distance from boundary: 200m (south)");

    if (m_config.useGmc) {
        GmcConfig gmcCfg;
        gmcCfg.broadcastRadius = params::UAV_BROADCAST_RADIUS;
        gmcCfg.alpha = params::GMC_ALPHA;
        gmcCfg.cellCoverageThreshold = params::CELL_COVERAGE_THRESHOLD;

        m_uavWaypoints = TrajectoryHelper::PlanGmc(
            m_candidateNodes, m_groundNodes, m_cellInfo.nodeToCell,
            startPos, m_config.uavSpeed, gmcCfg);
    } else {
        m_uavWaypoints = TrajectoryHelper::PlanNearestNeighbor(
            m_candidateNodes, m_groundNodes, startPos, m_config.uavSpeed);
    }

    m_results.uavPathLength = TrajectoryHelper::ComputePathLength(m_uavWaypoints, startPos);

    NS_LOG_INFO("UAV trajectory planned: " << m_uavWaypoints.size() << " waypoints, "
                << m_results.uavPathLength << "m total distance");
}

// ============================================================================
// WsnNetworkHelper::InstallApplications()
// ============================================================================

void WsnNetworkHelper::InstallApplications() {
    // Install UAV application
    auto uavApp = CreateObject<FragmentDisseminationApp>();
    m_uavNode->AddApplication(uavApp);

    uavApp->SetRole(FragmentDisseminationApp::Role::UAV_BROADCASTER);
    uavApp->SetNodeId(m_groundNodes.GetN() + 1);  // nodeId after ground nodes
    uavApp->SetFragments(m_fragments);
    uavApp->SetExpectedFragmentCount(m_config.numFragments);
    uavApp->SetThresholds(m_config.cooperationThreshold, m_config.alertThreshold);
    uavApp->SetGroundNodeCount(m_groundNodes.GetN());  // For UAV identification
    uavApp->SetStatisticsCollector(m_stats);
    uavApp->SetNetDevice(m_uavDevices.Get(0));  // Set UAV device
    uavApp->SetStartTime(Seconds(m_config.startupDuration));
    uavApp->SetStopTime(Seconds(m_config.simTime));

    // Wire UAV MAC RX callback
    auto uavDev = DynamicCast<wsn::Cc2420NetDevice>(m_uavDevices.Get(0));
    if (uavDev) {
        auto uavMac = uavDev->GetMac();
        if (uavMac) {
            uint32_t uavNodeId = m_uavNode->GetId();
            uavMac->SetMcpsDataIndicationCallback(
                [this, uavNodeId](Ptr<Packet> pkt, Mac16Address src, double rssi) {
                    this->OnUavNodeMacIndication(uavNodeId, pkt, src, rssi);
                });
        }
    }

    // Install ground node applications
    for (uint32_t i = 0; i < m_groundNodes.GetN(); i++) {
        auto groundApp = CreateObject<FragmentDisseminationApp>();
        m_groundNodes.Get(i)->AddApplication(groundApp);

        groundApp->SetRole(FragmentDisseminationApp::Role::GROUND_NODE);
        groundApp->SetNodeId(i);
        groundApp->SetFragments(m_fragments);
        groundApp->SetExpectedFragmentCount(m_config.numFragments);
        groundApp->SetDetectionNodeId(m_detectionNodeId);
        groundApp->SetThresholds(m_config.cooperationThreshold, m_config.alertThreshold);

        // BFS level for cooperation stagger (simplified)
        uint32_t bfsLevel = 0;  // TODO: compute actual BFS level from cell leader
        groundApp->SetBfsLevel(bfsLevel);

        groundApp->SetGroundNodeCount(m_groundNodes.GetN());  // For UAV identification
        groundApp->SetStatisticsCollector(m_stats);
        groundApp->SetDetectionCallback(
            MakeCallback(&WsnNetworkHelper::OnDetection, this));
        groundApp->SetNetDevice(m_groundDevices.Get(i));  // Set ground node device

        groundApp->SetStartTime(Seconds(m_config.startupDuration + 0.1));
        groundApp->SetStopTime(Seconds(m_config.simTime));

        // Wire ground node MAC RX callback
        auto groundDev = DynamicCast<wsn::Cc2420NetDevice>(m_groundDevices.Get(i));
        if (groundDev) {
            auto groundMac = groundDev->GetMac();
            if (groundMac) {
                uint32_t nodeId = i;
                groundMac->SetMcpsDataIndicationCallback(
                    [this, nodeId](Ptr<Packet> pkt, Mac16Address src, double rssi) {
                        this->OnGroundNodeMacIndication(nodeId, pkt, src, rssi);
                    });
            }
        }
    }

    NS_LOG_INFO("Applications installed on " << (m_groundNodes.GetN() + 1) << " nodes");
}

// ============================================================================
// WsnNetworkHelper::Schedule()
// ============================================================================

void WsnNetworkHelper::Schedule() {
    // Schedule UAV waypoint visits
    Ptr<WaypointMobilityModel> uavMobility = m_uavNode->GetObject<WaypointMobilityModel>();

    // Calculate starting position (200m south of network)
    double gridDiameter = (m_config.gridSize - 1) * m_config.gridSpacing;
    double centerX = gridDiameter / 2.0;
    Vector startPos(centerX, -200.0, m_config.uavAltitude);

    // Add explicit starting waypoint so WaypointMobilityModel starts from correct position
    uavMobility->AddWaypoint(ns3::Waypoint(Seconds(m_config.startupDuration), startPos));

    // Add trajectory waypoints from GMC planning
    for (const auto& waypoint : m_uavWaypoints) {
        Time arrivalTime = Seconds(m_config.startupDuration + waypoint.arrivalTimeSec);
        Vector waypointPos(waypoint.x, waypoint.y, waypoint.z);

        uavMobility->AddWaypoint(ns3::Waypoint(arrivalTime, waypointPos));
    }

    // Schedule periodic UAV position recording
    for (double t = 0; t < m_config.simTime; t += 1.0) {
        Simulator::Schedule(Seconds(t), [this]() {
            auto mob = m_uavNode->GetObject<MobilityModel>();
            if (mob) {
                Vector pos = mob->GetPosition();
                m_stats->RecordUavPosition(Simulator::Now().GetSeconds(), pos);
            }
        });
    }

    NS_LOG_INFO("UAV waypoints scheduled");
}

// ============================================================================
// WsnNetworkHelper::Run()
// ============================================================================

void WsnNetworkHelper::Run() {
    NS_LOG_INFO("Running simulation for " << m_config.simTime << " seconds");

    Simulator::Run();
    // Note: Do NOT call Simulator::Destroy() here - it will be called in the scenario file
    // after all results have been collected. Destroying too early invalidates member variables.

    // Collect results
    if (m_stats->IsDetected()) {
        m_results.detected = true;
        m_results.detectionTime = m_stats->GetDetectionTime();
        m_results.detectionNodeId = m_stats->GetDetectionNodeId();
    }

    NS_LOG_INFO("Simulation complete. Detected=" << m_results.detected
                << ", Tdetect=" << m_results.detectionTime << "s");
}

// ============================================================================
// WsnNetworkHelper::OnDetection()
// ============================================================================

void WsnNetworkHelper::OnDetection(uint32_t nodeId, double timeSeconds) {
    NS_LOG_INFO("Detection callback: node " << nodeId << " at t=" << timeSeconds << "s");
}

// ============================================================================
// WsnNetworkHelper::OnGroundNodeMacIndication()
// ============================================================================

void WsnNetworkHelper::OnGroundNodeMacIndication(uint32_t nodeId, Ptr<Packet> packet,
                                                 Mac16Address source, double rssiDbm) {
    if (!packet || nodeId >= m_groundNodes.GetN()) {
        return;
    }

    auto app = DynamicCast<FragmentDisseminationApp>(m_groundNodes.Get(nodeId)->GetApplication(0));
    if (app) {
        app->OnPacketReceived(packet, rssiDbm);
    }
}

// ============================================================================
// WsnNetworkHelper::OnUavNodeMacIndication()
// ============================================================================

void WsnNetworkHelper::OnUavNodeMacIndication(uint32_t nodeId, Ptr<Packet> packet,
                                              Mac16Address source, double rssiDbm) {
    if (!packet || !m_uavNode || m_uavNode->GetId() != nodeId) {
        return;
    }

    auto app = DynamicCast<FragmentDisseminationApp>(m_uavNode->GetApplication(0));
    if (app) {
        app->OnPacketReceived(packet, rssiDbm);
    }
}

// ============================================================================
// WsnNetworkHelper::OnPacketDropped()
// ============================================================================

void WsnNetworkHelper::OnPacketDropped(uint32_t srcNodeId, uint32_t dstNodeId, uint32_t fragmentId) {
    // Contact window rejection is "transmission not attempted", not a packet drop
    // Real drops (due to channel loss/RSSI) are handled by PHY layer, not recorded here
    // So we don't track MAC-level contact window rejections in statistics
    NS_LOG_DEBUG("Contact window rejected: src=" << srcNodeId << " fragId=" << fragmentId);
}

}  // namespace uav
}  // namespace wsn
}  // namespace ns3
