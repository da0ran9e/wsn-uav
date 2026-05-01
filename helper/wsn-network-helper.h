/*
 * WSN Network Helper: Main orchestrator
 * Orchestrates Build → Schedule → Run simulation lifecycle
 */

#ifndef WSN_UAV_NETWORK_HELPER_H
#define WSN_UAV_NETWORK_HELPER_H

#include "ns3/node-container.h"
#include "ns3/net-device-container.h"
#include "ns3/ptr.h"
#include "ns3/mac16-address.h"
#include "ns3/packet.h"
#include "topology-helper.h"
#include "trajectory-helper.h"
#include "result-writer.h"
#include "../models/common/statistics-collector.h"
#include "../models/common/types.h"
#include "../models/application/fragment-model.h"
#include "../models/mac/wsn-uav-mac.h"
#include <string>
#include <map>
#include <set>

namespace ns3 {
namespace wsn {
namespace uav {

// ============================================================================
// Simulation Configuration
// ============================================================================

struct SimulationConfig {
    // Network
    uint32_t gridSize = 10;
    double gridSpacing = 20.0;
    
    // Fragments
    uint32_t numFragments = 10;
    
    // UAV
    uint32_t numUavs = 1;  // Scenario 1 uses 1 UAV
    double uavAltitude = 20.0;
    double uavSpeed = 20.0;
    
    // Timing
    double broadcastInterval = 0.2;
    double startupDuration = 5.0;
    double simTime = 500.0;
    
    // Thresholds
    double cooperationThreshold = 0.30;
    double alertThreshold = 0.75;
    double suspiciousPercent = 0.30;
    
    // Output
    uint32_t seed = 1;
    uint32_t runId = 1;
    std::string outputDir = "src/wsn-uav/results/scenario-1/run-001";
    
    // Options
    bool usePerfectChannel = false;
    bool useGmc = true;  // false = nearest-neighbor baseline
    
    bool Validate(std::string& errMsg) const;
};

// ============================================================================
// Simulation Results
// ============================================================================

struct SimulationResults {
    bool detected = false;
    double detectionTime = -1.0;  // -1 = not detected
    uint32_t detectionNodeId = 0;
    double uavPathLength = 0.0;
    double cooperationGain = 0.0;  // fragsFromCoop / total
    uint32_t totalNodes = 0;
    uint32_t candidateNodes = 0;
    uint32_t totalFragmentsDelivered = 0;
    uint32_t fragmentsFromUav = 0;
    uint32_t fragmentsFromCoop = 0;
    std::set<uint32_t> candidateNodeIds;  // Store actual candidate node IDs
};

// ============================================================================
// WsnNetworkHelper Class
// ============================================================================

class WsnNetworkHelper {
public:
    explicit WsnNetworkHelper(const SimulationConfig& config);
    virtual ~WsnNetworkHelper();
    
    // Simulation lifecycle
    void Build();      // Create topology, install devices, apps
    void Schedule();   // Schedule events
    void Run();        // Execute simulator
    
    // Results
    const SimulationResults& GetResults() const { return m_results; }
    Ptr<StatisticsCollector> GetStats() const { return m_stats; }
    NodeContainer GetGroundNodes() const { return m_groundNodes; }
    const std::set<uint32_t>& GetCandidateNodes() const { return m_candidateNodes; }

private:
    // MAC layer callbacks
    void OnGroundNodeMacIndication(uint32_t nodeId, Ptr<Packet> packet,
                                   Mac16Address source, double rssiDbm);
    void OnUavNodeMacIndication(uint32_t nodeId, Ptr<Packet> packet,
                                Mac16Address source, double rssiDbm);

    // Configuration and state
    SimulationConfig m_config;
    SimulationResults m_results;
    Ptr<StatisticsCollector> m_stats;
    
    // Nodes and devices
    NodeContainer m_groundNodes;
    Ptr<Node> m_uavNode;
    NetDeviceContainer m_groundDevices;
    NetDeviceContainer m_uavDevices;

    // MAC layers
    std::map<uint32_t, Ptr<WsnUavMac>> m_groundMacs;  // nodeId -> WsnUavMac
    Ptr<WsnUavMac> m_uavMac;

    // Topology information
    CellInfo m_cellInfo;
    std::set<uint32_t> m_candidateNodes;
    uint32_t m_detectionNodeId = 0;

    // Fragments and trajectory
    FragmentCollection m_fragments;
    std::vector<Waypoint> m_uavWaypoints;

    // Build steps
    void CreateNodes();
    void InstallRadios();
    void BuildTopology();
    void SelectCandidatesAndFragments();
    void PlanTrajectory();
    void InstallApplications();

    // Packet drop callback
    void OnPacketDropped(uint32_t srcNodeId, uint32_t dstNodeId, uint32_t fragmentId);

    // Callbacks
    void OnDetection(uint32_t nodeId, double timeSeconds);
};

}  // namespace uav
}  // namespace wsn
}  // namespace ns3

#endif  // WSN_UAV_NETWORK_HELPER_H
