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
#include <sstream>

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
    CreateUavNodes(m_config.numUavs);
    InstallRadios();  // Unified: installs both ground and UAV nodes on shared channel
    BuildTopology();
    SelectCandidatesAndFragments();
    DistributeFragmentsToUavs();  // Enable load-balanced fragment distribution
    AdjustUavSpeedByLoad();       // Phase 1: Adjust speeds by fragment load
    ScheduleUavFlights();
    InstallApplications();
    InstallUavApplications();

    m_results.totalNodes = m_groundNodes.GetN();
    m_results.candidateNodes = m_candidateNodes.size();
}

// ============================================================================
// WsnNetworkHelper::CreateNodes()
// ============================================================================

void WsnNetworkHelper::CreateNodes() {
    // Create ground nodes in grid
    m_groundNodes = TopologyHelper::CreateGrid(m_config.gridSize, m_config.gridSpacing, 0.0);

    NS_LOG_INFO("Created " << m_groundNodes.GetN() << " ground nodes");
}

void WsnNetworkHelper::CreateUavNodes(uint32_t count) {
    m_uavNodes.Create(count);
    
    MobilityHelper mobility;
    mobility.SetMobilityModel("ns3::WaypointMobilityModel");
    mobility.Install(m_uavNodes);

    for (uint32_t i = 0; i < count; i++) {
        Vector startPos;
        double gridDiameter = (m_config.gridSize - 1) * m_config.gridSpacing;
        double centerX = gridDiameter / 2.0;
        
        if (i < m_config.uavStartingX.size() && i < m_config.uavStartingY.size() && i < m_config.uavStartingZ.size()) {
            startPos = Vector(m_config.uavStartingX[i], m_config.uavStartingY[i], m_config.uavStartingZ[i]);
        } else {
            // Phase 1: All UAVs start from same position (center-bottom, outside grid)
            // Different speeds create temporal staggering as they visit the entire network
            startPos = Vector(centerX, -200.0, m_config.uavAltitude);
        }
        
        auto uavMobility = m_uavNodes.Get(i)->GetObject<MobilityModel>();
        uavMobility->SetPosition(startPos);
        
        NS_LOG_INFO("UAV " << i << " initial position: (" << startPos.x << ", " << startPos.y << ", " << startPos.z << ")");
    }
    NS_LOG_INFO("Created " << count << " UAV nodes");
}

// ============================================================================
// WsnNetworkHelper::InstallRadios()
// ============================================================================
// Unified radio installation for all nodes (ground + UAV) on shared channel
// This ensures all devices use the same SpectrumChannel object for communication
// ============================================================================

void WsnNetworkHelper::InstallRadios() {
    // Create SINGLE helper instance and SINGLE channel for ALL nodes
    wsn::Cc2420Helper cc2420;

    // Create shared channel ONCE (used by both ground and UAV nodes)
    m_channel = cc2420.CreateChannel();
    m_context.spectrumChannel = m_channel;

    // Configure PHY attributes (applied uniformly to all nodes)
    cc2420.SetPhyAttribute("TxPower", DoubleValue(params::TX_POWER_DBM));
    cc2420.SetPhyAttribute("RxSensitivity", DoubleValue(params::RX_SENSITIVITY_DBM));
    cc2420.SetPhyAttribute("PerfectChannel", BooleanValue(m_config.usePerfectChannel));
    cc2420.SetPhyAttribute("EnableShadowing", BooleanValue(!m_config.usePerfectChannel));

    // Set channel for this helper
    cc2420.SetChannel(m_channel);

    // Install on GROUND nodes using same helper and channel
    m_groundDevices = cc2420.Install(m_groundNodes);
    m_context.groundDevices = m_groundDevices;

    NS_LOG_INFO("Radios installed on " << m_groundNodes.GetN() << " ground nodes");

    // Install on UAV nodes using SAME helper and SAME channel
    // This is the critical fix: all devices share m_channel object
    m_uavDevices = cc2420.Install(m_uavNodes);
    m_context.uavDevices = m_uavDevices;

    NS_LOG_INFO("Radios installed on " << m_uavNodes.GetN() << " UAV nodes");
    NS_LOG_INFO("All nodes (ground + UAV) on shared channel: " << m_channel);
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

    // Generate fragments with random sizes for load-balanced distribution to UAVs
    m_fragments = FragmentCollection::GenerateWithSizes(
        m_config.numFragments,
        m_config.fragmentMinSizeBytes,
        m_config.fragmentMaxSizeBytes,
        m_config.seed);
    m_results.fragmentsFromUav = 0;  // Will accumulate during sim

    NS_LOG_INFO("Selected " << m_candidateNodes.size() << " candidate nodes");
    NS_LOG_INFO("Detection node (n*) = " << m_detectionNodeId);
    NS_LOG_INFO("Generated " << m_config.numFragments << " fragments");
}

// ============================================================================
// WsnNetworkHelper::DistributeFragmentsToUavs()
// ============================================================================

void WsnNetworkHelper::DistributeFragmentsToUavs() {
    uint32_t numUavs = m_config.numUavs;
    auto allFragIds = m_fragments.GetIds();  // sorted by size: largest first
    uint32_t total = allFragIds.size();

    if (total == 0 || numUavs == 0) return;

    // Phase 1: Round-robin distribution by size
    // Fragment 0 → UAV0, Fragment 1 → UAV1, Fragment 2 → UAV2, Fragment 3 → UAV0, ...
    // Result: UAV0 gets heaviest frags, UAV2 gets lightest frags
    // Each UAV carries a unique subset for load balancing + ground cooperation
    std::vector<std::vector<uint32_t>> uavFragSets(numUavs);
    for (uint32_t i = 0; i < total; i++) {
        uavFragSets[i % numUavs].push_back(allFragIds[i]);
    }

    for (uint32_t uavId = 0; uavId < numUavs; uavId++) {
        FragmentCollection uavFrags;
        uint32_t totalBytes = 0;
        for (uint32_t fragId : uavFragSets[uavId]) {
            const Fragment* frag = m_fragments.Get(fragId);
            if (frag) {
                uavFrags.Add(*frag);
                totalBytes += frag->sizeBytes;
            }
        }
        m_uavFragments[uavId] = uavFrags;
        m_results.uavFragmentIds[uavId] = uavFragSets[uavId];
        NS_LOG_INFO("UAV " << uavId << " assigned " << uavFragSets[uavId].size()
                           << " fragments, total " << totalBytes << " bytes");
    }

    // Record fragment sizes in results
    for (auto fragId : allFragIds) {
        const Fragment* frag = m_fragments.Get(fragId);
        if (frag) m_results.fragmentSizesBytes[fragId] = frag->sizeBytes;
    }
}

// ============================================================================
// WsnNetworkHelper::AdjustUavSpeedByLoad() (Phase 1)
// ============================================================================

void WsnNetworkHelper::AdjustUavSpeedByLoad() {
    uint32_t numUavs = m_config.numUavs;

    if (!m_config.useLoadBasedSpeed || numUavs <= 1) {
        // Single UAV or disabled: use base speed for all
        for (uint32_t i = 0; i < numUavs; i++) {
            m_uavSpeeds[i] = m_config.uavSpeed;
        }
        return;
    }

    // Calculate total bytes per UAV
    std::vector<uint32_t> uavBytes(numUavs, 0);
    uint32_t maxBytes = 0;
    for (uint32_t uavId = 0; uavId < numUavs; uavId++) {
        for (uint32_t fragId : m_results.uavFragmentIds[uavId]) {
            const Fragment* frag = m_fragments.Get(fragId);
            if (frag) uavBytes[uavId] += frag->sizeBytes;
        }
        maxBytes = std::max(maxBytes, uavBytes[uavId]);
    }

    if (maxBytes == 0) {
        for (uint32_t i = 0; i < numUavs; i++) m_uavSpeeds[i] = m_config.uavSpeed;
        return;
    }

    // Speed = base * (maxFactor - (maxFactor - minFactor) * loadFraction)
    for (uint32_t uavId = 0; uavId < numUavs; uavId++) {
        double loadFrac = (double)uavBytes[uavId] / maxBytes;
        double factor = m_config.maxSpeedFactor -
                        (m_config.maxSpeedFactor - m_config.minSpeedFactor) * loadFrac;
        m_uavSpeeds[uavId] = m_config.uavSpeed * factor;
        NS_LOG_INFO("UAV " << uavId << " load: " << uavBytes[uavId]
                           << " bytes, speed factor: " << factor
                           << ", adjusted speed: " << m_uavSpeeds[uavId] << " m/s");
    }
}

// ============================================================================
// WsnNetworkHelper::PlanTrajectory()
// ============================================================================

void WsnNetworkHelper::ScheduleUavFlights() {
    uint32_t numUavs = m_uavNodes.GetN();

    // Phase 1: All UAVs visit ALL candidate nodes (full network coverage)
    // Different fragment loads + speeds create temporal staggering
    // All UAVs start from same position, fly through entire network
    std::vector<std::set<uint32_t>> partitionedCandidates(numUavs);

    // Each UAV gets all candidates (no partitioning)
    for (uint32_t uavId = 0; uavId < numUavs; uavId++) {
        partitionedCandidates[uavId] = m_candidateNodes;
    }

    for (uint32_t uavId = 0; uavId < numUavs; uavId++) {
        auto uavMobility = m_uavNodes.Get(uavId)->GetObject<MobilityModel>();
        Vector physicalStartPos = uavMobility->GetPosition();

        // Phase 1: Create directional offsets for each UAV to fly in different directions
        // While all UAVs physically start at same position, they bias toward different regions
        double gridDiameter = (m_config.gridSize - 1) * m_config.gridSpacing;
        Vector directionalStartPos = physicalStartPos;

        if (numUavs > 1 && m_config.useDirectionalBias) {
            // Phase 1: Optional directional bias to explore different trajectory patterns
            // Empirical tradeoff: ±30m offset → ~20.6s detection (vs 17.7s baseline, 16% slower)
            std::vector<Vector> directionalOffsets = {
                Vector(-30, -30, 0),       // UAV 0: bias toward bottom-left
                Vector(30, -30, 0),        // UAV 1: bias toward bottom-right
                Vector(0, 30, 0),          // UAV 2: bias toward top
                Vector(0, 0, 0),           // UAV 3: no bias (if exists)
            };
            if (uavId < directionalOffsets.size()) {
                directionalStartPos = Vector(
                    physicalStartPos.x + directionalOffsets[uavId].x,
                    physicalStartPos.y + directionalOffsets[uavId].y,
                    physicalStartPos.z);
            }
        }

        NS_LOG_INFO("UAV " << uavId << " physical start: (" << physicalStartPos.x << ", " << physicalStartPos.y << ", " << physicalStartPos.z << ")");
        NS_LOG_INFO("UAV " << uavId << " trajectory bias: (" << directionalStartPos.x << ", " << directionalStartPos.y << ")");
        if (numUavs > 1) {
            NS_LOG_INFO("UAV " << uavId << " assigned " << partitionedCandidates[uavId].size() << " target nodes");
        }

        // Use per-UAV adjusted speed if available, otherwise fall back to base speed (Phase 1)
        double uavSpeed = m_uavSpeeds.count(uavId) ? m_uavSpeeds[uavId] : m_config.uavSpeed;

        std::vector<Waypoint> waypoints;
        if (m_config.useGmc) {
            GmcConfig gmcCfg;
            gmcCfg.broadcastRadius = params::UAV_BROADCAST_RADIUS;
            gmcCfg.alpha = params::GMC_ALPHA;
            gmcCfg.cellCoverageThreshold = params::CELL_COVERAGE_THRESHOLD;
            gmcCfg.maxCentroids = params::MAX_KMEANS_CENTROIDS;  // Use dynamic max from parameters
            gmcCfg.uavSpeed = uavSpeed;  // Phase 1: Dynamic k per UAV based on speed
            gmcCfg.randomSeed = uavId + 1000 + m_config.seed;  // Phase 1: Random path per UAV

            std::set<uint32_t> targets = (numUavs > 1) ? partitionedCandidates[uavId] : m_candidateNodes;

            // Use directional bias for trajectory planning instead of physical start position
            waypoints = TrajectoryHelper::PlanGmc(
                targets, m_groundNodes, m_cellInfo.nodeToCell,
                directionalStartPos, uavSpeed, gmcCfg);
        } else {
            std::set<uint32_t> targets = (numUavs > 1) ? partitionedCandidates[uavId] : m_candidateNodes;
            waypoints = TrajectoryHelper::PlanNearestNeighbor(
                targets, m_groundNodes, directionalStartPos, uavSpeed);
        }

        // Fix return waypoint: UAV must return to physical start position, not directional offset
        if (!waypoints.empty() && m_config.useDirectionalBias && numUavs > 1) {
            // Last waypoint should be physical start position, not directional start position
            double returnDist = CalculateDistance(
                Vector(waypoints[waypoints.size()-2].x, waypoints[waypoints.size()-2].y, physicalStartPos.z),
                physicalStartPos);
            double returnTime = returnDist / uavSpeed;
            waypoints.back().x = physicalStartPos.x;
            waypoints.back().y = physicalStartPos.y;
            waypoints.back().z = physicalStartPos.z;
            if (waypoints.size() > 1) {
                waypoints.back().arrivalTimeSec = waypoints[waypoints.size()-2].arrivalTimeSec + returnTime;
            }
        }

        m_uavWaypoints[uavId] = waypoints;
        double pathLen = TrajectoryHelper::ComputePathLength(waypoints, physicalStartPos);
        m_results.uavPathLengths[uavId] = pathLen;
        m_results.totalUavPathLength += pathLen;

        NS_LOG_INFO("UAV " << uavId << " trajectory planned: " << waypoints.size() << " waypoints, "
                    << pathLen << "m total distance");
    }
}

// ============================================================================
// WsnNetworkHelper::InstallApplications()
// ============================================================================

void WsnNetworkHelper::InstallApplications() {
    // Assign ground nodes to spatial regions based on X coordinate (load-balanced distribution)
    // Only for multi-UAV scenarios; single-UAV scenarios don't need filtering
    uint32_t numUavs = m_uavNodes.GetN();
    const bool enableSpatialFiltering = (numUavs > 1);
    double gridWidth = (m_config.gridSize - 1) * (double)m_config.gridSpacing;
    double stripW = numUavs > 1 ? gridWidth / numUavs : gridWidth;

    for (uint32_t i = 0; i < m_groundNodes.GetN(); i++) {
        if (enableSpatialFiltering) {
            // Determine which UAV region this ground node belongs to
            Ptr<Node> node = m_groundNodes.Get(i);
            double nx = node->GetObject<MobilityModel>()->GetPosition().x;
            uint32_t assignedUav = std::min((uint32_t)(nx / stripW), numUavs - 1);
            m_groundNodeRegion[i] = assignedUav;
        } else {
            // Single-UAV: no filtering needed, use sentinel value
            m_groundNodeRegion[i] = UINT32_MAX;
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

        // Set assigned UAV region for spatial filtering (load-balanced mode)
        groundApp->SetAssignedUavRegion(m_groundNodeRegion[i]);

        groundApp->SetGroundNodeCount(m_groundNodes.GetN());  // For UAV identification
        groundApp->SetStatisticsCollector(m_stats);
        groundApp->SetDetectionCallback(
            MakeCallback(&WsnNetworkHelper::OnDetection));
        groundApp->SetNetDevice(m_groundDevices.Get(i));  // Set ground node device

        groundApp->SetStartTime(Seconds(m_config.startupDuration + 0.1));
        groundApp->SetStopTime(Seconds(m_config.simTime));

        // Wire ground node MAC RX callback
        auto groundDev = DynamicCast<wsn::Cc2420NetDevice>(m_groundDevices.Get(i));
        if (groundDev) {
            auto groundMac = groundDev->GetMac();
            if (groundMac) {
                groundMac->SetMcpsDataIndicationCallback(
                    [groundApp](Ptr<Packet> pkt, Mac16Address src, double rssi) {
                        if (groundApp) {
                            groundApp->OnPacketReceived(pkt, rssi);
                        }
                    });
            }
        }
    }

    NS_LOG_INFO("Applications installed on " << m_groundNodes.GetN() << " ground nodes");
}

void WsnNetworkHelper::InstallUavApplications() {
    for (uint32_t uavId = 0; uavId < m_uavNodes.GetN(); uavId++) {
        auto uavApp = CreateObject<FragmentDisseminationApp>();
        m_uavNodes.Get(uavId)->AddApplication(uavApp);

        uavApp->SetRole(FragmentDisseminationApp::Role::UAV_BROADCASTER);
        uavApp->SetNodeId(m_uavNodes.Get(uavId)->GetId());

        // Use per-UAV fragment set for load-balanced distribution
        const auto& uavFrags = m_uavFragments.count(uavId) ? m_uavFragments[uavId] : m_fragments;
        uavApp->SetFragments(uavFrags);
        uavApp->SetExpectedFragmentCount(uavFrags.Size());

        uavApp->SetThresholds(m_config.cooperationThreshold, m_config.alertThreshold);
        uavApp->SetGroundNodeCount(m_groundNodes.GetN());
        uavApp->SetStatisticsCollector(m_stats);
        uavApp->SetNetDevice(m_uavDevices.Get(uavId));
        uavApp->SetStartTime(Seconds(m_config.startupDuration));
        uavApp->SetStopTime(Seconds(m_config.simTime));
        
        m_uavApps[uavId] = uavApp;

        // NOTE: UAVs should NOT receive packets - they only broadcast
        // Do NOT set MAC callback for UAVs to avoid false detections/cooperation
        auto uavDev = DynamicCast<wsn::Cc2420NetDevice>(m_uavDevices.Get(uavId));
        if (uavDev) {
            auto uavMac = uavDev->GetMac();
            if (uavMac) {
                uint32_t physicalNodeId = m_uavNodes.Get(uavId)->GetId();
                // INTENTIONALLY NOT SETTING CALLBACK FOR UAVs
                // uavMac->SetMcpsDataIndicationCallback(...)
                
                // DEBUG PACKET TRACE CALLBACK DISABLED DUE TO CRASH BUG
                // TODO: Fix null pointer dereference in callback
                /*
                auto stats = m_stats;
                uavMac->SetDebugPacketTraceCallback(
                    [stats, physicalNodeId](std::string eventName, Ptr<const Packet> pkt) {
                        if (eventName.find("DropContactWindowGoodRssi") != std::string::npos) {
                            size_t pos = eventName.find("dsts=");
                            if (pos != std::string::npos) {
                                std::string dstsStr = eventName.substr(pos + 5);
                                std::stringstream ss(dstsStr);
                                std::string item;
                                while (std::getline(ss, item, ',')) {
                                    if (!item.empty()) {
                                        uint32_t dstId = std::stoi(item);
                                        if (stats) {
                                            stats->RecordMacDrop(physicalNodeId, dstId);
                                        }
                                    }
                                }
                            }
                        }
                    });
                */
            }
        }
    }
    NS_LOG_INFO("Applications installed on " << m_uavNodes.GetN() << " UAV nodes");
}

// ============================================================================
// WsnNetworkHelper::Schedule()
// ============================================================================

void WsnNetworkHelper::Schedule() {
    for (uint32_t uavId = 0; uavId < m_uavNodes.GetN(); uavId++) {
        Ptr<WaypointMobilityModel> uavMobility = m_uavNodes.Get(uavId)->GetObject<WaypointMobilityModel>();
        Vector startPos = uavMobility->GetPosition();
        
        uavMobility->AddWaypoint(ns3::Waypoint(Seconds(m_config.startupDuration), startPos));

        for (const auto& waypoint : m_uavWaypoints[uavId]) {
            Time arrivalTime = Seconds(m_config.startupDuration + waypoint.arrivalTimeSec);
            Vector waypointPos(waypoint.x, waypoint.y, waypoint.z);
            uavMobility->AddWaypoint(ns3::Waypoint(arrivalTime, waypointPos));
        }
    }

    // Schedule periodic UAV position recording
    auto stats = m_stats;
    auto uavNodes = m_uavNodes;
    auto groundNodes = m_groundNodes;
    uint32_t numUavs = m_uavNodes.GetN();
    uint32_t numGroundNodes = m_groundNodes.GetN();

    for (double t = 0; t <= m_config.simTime; t += 1.0) {
        Simulator::Schedule(Seconds(t), [stats, uavNodes, groundNodes, numUavs, numGroundNodes]() {
            double now = Simulator::Now().GetSeconds();
            // UAV pos
            for (uint32_t uavId = 0; uavId < numUavs; uavId++) {
                auto mob = uavNodes.Get(uavId)->GetObject<MobilityModel>();
                if (mob) {
                    Vector pos = mob->GetPosition();
                    stats->RecordUavPosition(now, pos, uavId);
                }
            }
            // Node states
            for (uint32_t i = 0; i < numGroundNodes; i++) {
                auto app = DynamicCast<FragmentDisseminationApp>(groundNodes.Get(i)->GetApplication(0));
                if (app) {
                    stats->RecordNodeState(i, now, app->GetConfidenceModel().GetReceivedCount());
                }
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
        
        // Calculate cooperation gain for detection node
        auto app = DynamicCast<FragmentDisseminationApp>(
            m_groundNodes.Get(m_results.detectionNodeId)->GetApplication(0));
        if (app) {
            uint32_t fromUav = app->GetConfidenceModel().GetCountFromUav();
            uint32_t fromCoop = app->GetConfidenceModel().GetCountFromCoop();
            uint32_t total = fromUav + fromCoop;
            if (total > 0) {
                m_results.cooperationGain = static_cast<double>(fromCoop) / total;
            }
        }
    }

    NS_LOG_INFO("Simulation complete. Detected=" << m_results.detected
                << ", Tdetect=" << m_results.detectionTime << "s");
}

// ============================================================================
// WsnNetworkHelper::OnDetection()
// ============================================================================

// static method - does not require 'this' pointer
void WsnNetworkHelper::OnDetection(uint32_t nodeId, double timeSeconds) {
    NS_LOG_INFO("Detection callback: node " << nodeId << " at t=" << timeSeconds << "s");
}


void WsnNetworkHelper::OnUavDetection(uint32_t uavId, uint32_t nodeId, double timeSeconds) {
    NS_LOG_INFO("UAV Detection callback: UAV " << uavId << " at t=" << timeSeconds << "s from node " << nodeId);
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
