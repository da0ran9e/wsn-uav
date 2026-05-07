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
#include "ns3/spectrum-channel.h"
#include "topology-helper.h"
#include "trajectory-helper.h"
#include "result-writer.h"
#include "../models/common/statistics-collector.h"
#include "../models/common/types.h"
#include "../models/application/fragment-model.h"
#include "../models/mac/wsn-uav-mac.h"
#include "../models/application/fragment-dissemination-app.h"
#include <string>
#include <map>
#include <set>

namespace ns3 {
namespace wsn {
namespace uav {

// ============================================================================
// Build Context: Centralized Simulation State
// ============================================================================

struct BuildContext {
    // Topology
    ns3::NodeContainer groundNodes;
    ns3::NodeContainer uavNodes;

    // Radio infrastructure (SHARED)
    // All nodes (ground + UAV) attached to same channel object for communication
    ns3::Ptr<ns3::SpectrumChannel> spectrumChannel;

    // Devices
    ns3::NetDeviceContainer groundDevices;
    ns3::NetDeviceContainer uavDevices;
};

// ============================================================================
// Simulation Configuration
// ============================================================================

struct SimulationConfig {
    // Network
    uint32_t gridSize = 10;
    double gridSpacing = 20.0;
    
    // Fragments
    uint32_t numFragments = 10;
    uint32_t fragmentMinSizeBytes = 1000;   // 1 KB min
    uint32_t fragmentMaxSizeBytes = 20000;  // 20 KB max
    
    // UAV
    uint32_t numUavs = 1;  // Scenario 1 uses 1 UAV
    std::vector<double> uavStartingX = {};
    std::vector<double> uavStartingY = {};
    std::vector<double> uavStartingZ = {};
    bool validatePerUavConfig = false;
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

    // Size-based UAV speed adjustment (Phase 1)
    bool useLoadBasedSpeed = true;
    double minSpeedFactor = 0.4;   // 40% of base speed for heaviest UAV (increased difference)
    double maxSpeedFactor = 1.2;   // 120% of base speed for lightest UAV (doubled speed spread)

    // Directional trajectory bias (Phase 1: experimental)
    // Tradeoff: ±30m offsets → ~20.6s detection (vs 17.7s baseline, 16% slower)
    bool useDirectionalBias = false;  // Disabled by default; opt-in for testing

    bool Validate(std::string& errMsg) const;
};

// ============================================================================
// Simulation Results
// ============================================================================

struct SimulationResults {
    bool detected = false;
    double detectionTime = -1.0;  // -1 = not detected
    uint32_t detectionNodeId = 0;
    std::map<uint32_t, double> uavPathLengths;
    double totalUavPathLength = 0.0;
    double cooperationOverlapRatio = 0.0;
    std::map<uint32_t, uint32_t> fragmentsPerUav;
    double cooperationGain = 0.0;  // fragsFromCoop / total
    std::map<uint32_t, std::vector<uint32_t>> uavFragmentIds;   // per-UAV fragment IDs
    std::map<uint32_t, uint32_t> fragmentSizesBytes;            // fragmentId → size
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
    // Configuration and state
    SimulationConfig m_config;
    SimulationResults m_results;
    Ptr<StatisticsCollector> m_stats;
    BuildContext m_context;  // Centralized simulation state

    // Nodes and devices (references to context)
    NodeContainer m_groundNodes;
    NodeContainer m_uavNodes;
    NetDeviceContainer m_groundDevices;
    NetDeviceContainer m_uavDevices;
    Ptr<SpectrumChannel> m_channel;  // Shared channel for all nodes

    // MAC layers
    std::map<uint32_t, Ptr<WsnUavMac>> m_groundMacs;  // nodeId -> WsnUavMac
    std::map<uint32_t, Ptr<WsnUavMac>> m_uavMacs;

    // Topology information
    CellInfo m_cellInfo;
    std::set<uint32_t> m_candidateNodes;
    uint32_t m_detectionNodeId = 0;

    // Fragments and trajectory
    FragmentCollection m_fragments;
    std::map<uint32_t, FragmentCollection> m_uavFragments;  // per-UAV fragment subset
    std::map<uint32_t, std::vector<Waypoint>> m_uavWaypoints;
    std::map<uint32_t, double> m_uavSpeeds;  // per-UAV adjusted speed (Phase 1)
    std::map<uint32_t, Ptr<FragmentDisseminationApp>> m_uavApps;
    std::map<uint32_t, uint32_t> m_groundNodeRegion;  // ground_node_id -> assigned_uav_id (for spatial filtering)

    // Build steps
    void CreateNodes();
    void InstallRadios();  // Unified: installs all nodes (ground + UAV) on shared channel
    void BuildTopology();
    void SelectCandidatesAndFragments();
    void PlanTrajectory();
    void InstallApplications();

    // Multi-UAV methods
    uint32_t GetUavCount() const { return m_uavNodes.GetN(); }
    void CreateUavNodes(uint32_t count);
    void InstallUavApplications();
    void ScheduleUavFlights();
    void DistributeFragmentsToUavs();
    void AdjustUavSpeedByLoad();  // Phase 1: Adjust speeds based on fragment load
    void OnUavDetection(uint32_t uavId, uint32_t nodeId, double timeSeconds);

    // Packet drop callback
    void OnPacketDropped(uint32_t srcNodeId, uint32_t dstNodeId, uint32_t fragmentId);

    // Callbacks
    static void OnDetection(uint32_t nodeId, double timeSeconds);
};

}  // namespace uav
}  // namespace wsn
}  // namespace ns3

#endif  // WSN_UAV_NETWORK_HELPER_H
