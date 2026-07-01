#ifndef SCENARIO1_CONFIG_H
#define SCENARIO1_CONFIG_H

#include "../../models/network/scenario1-network.h"
#include "../../models/common/local-clue.h"
#include "../../models/common/cooperation-phy-mac.h"
#include "../../models/application/basestation-app.h"
#include "../../models/application/uav-app.h"
#include "../../models/application/ground-node-app.h"

#include "ns3/ptr.h"
#include "ns3/lr-wpan-helper.h"
#include "ns3/event-id.h"

#include <cstdint>
#include <string>
#include <vector>
#include <memory>

namespace ns3::wsn::uav {

enum class DetectionModel : uint8_t {
    FRAGMENT_RATIO = 0,
    CLUE_WEIGHTED  = 1,
    NOISY_OR       = 2,
};

struct Scenario1Results {
    bool passed = false;
    std::string message;
    uint32_t packetsSent = 0;
    uint32_t packetsReceived = 0;
    double deliveryRate = 0.0;
};

class Scenario1Config {
public:
    // Network parameters
    uint32_t gridSize = 10;
    double gridSpacing = 45.0;  // match example4 paper testbed
    double uavStartHeight = 20.0;
    double cellSizeMeters = 80.0;
    double cellNeighborRangeMeters = 120.0;
    uint32_t cellColorCount = 6;
    int32_t clueTargetNodeId = -1;
    uint32_t clueSeed = 20260525;
    double clueStrongRadiusMeters = 40.0;
    double clueWeakRadiusMeters = 80.0;
    double clueDecayMeters = 60.0;
    double clueMaxBlurredQuality = 0.65;
    double clueFalsePositiveRate = 0.08;
    bool inCellCooperationEnabled = true;
    double inCellCooperationStartSec = 1.0;
    double inCellCooperationIntervalSec = 5.0;
    double inCellCooperationStopRatio = 0.80;
    bool interCellCooperationEnabled = true;
    uint32_t interCellCooperationEveryRounds = 3;
    double interCellCooperationRangeMeters = 130.0;
    double cooperationAlertRatio = 0.75;
    double detectionAlertThreshold = 0.75;
    DetectionModel detectionModel = DetectionModel::CLUE_WEIGHTED;
    FlightPathModel flightPathModel = FlightPathModel::CELL_AWARE_GMC;
    BroadcastModel broadcastModel = BroadcastModel::CYCLIC;
    uint32_t randomWaypointBudget = 64;
    uint32_t coopInCellPacketBudgetPerNode = 64;
    uint32_t coopInterCellPacketBudgetPerNode = 160;
    double coopInCellManifestSuccessProb = 0.98;
    double coopInterCellManifestSuccessProb = 0.95;
    double coopInCellFragmentSuccessProb = 0.92;
    double coopInterCellFragmentSuccessProb = 0.82;

    // Simulation parameters
    double startTimeSec = 1.0;
    uint32_t numFragmentsToSend = 10;
    double broadcastIntervalSec = 1.0;
    double simulationDurationSec = 1800.0;

    // Scenario name; log file is created under
    //   src/wsn-uav/docs/visualize/result/<scenarioName>/<dd-MM-yy>/<hh-mm-ss>.md
    std::string scenarioName = "scenario1";

    // Three-step workflow
    void Build();     // Step 1: Build network from model
    void Schedule();  // Step 2: Schedule events
    void Run();       // Step 3: Run simulation

private:
    NetworkSetup m_setup;

    // LrWpanHelper MUST live for entire simulation. Its destructor calls
    // m_channel->Dispose() which clears the channel's PHY list, breaking RX.
    std::unique_ptr<ns3::LrWpanHelper> m_lrWpan;

    // Application references
    ns3::Ptr<BaseStationApp> m_bsApp;
    ns3::Ptr<UavApp> m_uavApp;
    std::vector<ns3::Ptr<GroundNodeApp>> m_groundApps;
    LocalCluePlan m_cluePlan;
    CooperationPhyMacModel m_coopPhyMac;
    ns3::EventId m_inCellCoopEvent;
    uint32_t m_inCellCoopRounds = 0;
    uint64_t m_inCellCoopFragmentTransfers = 0;
    uint64_t m_interCellCoopFragmentTransfers = 0;
    bool m_detectionReached = false;
    double m_detectionTimeSec = -1.0;
    uint32_t m_detectionNodeId = 0;
    double m_detectionConfidence = 0.0;

    // Helper functions
    void RandomDelayedStartUp(double delayThreshold);
    void BuildAndInstallCellLayer();
    void BuildAndInstallLocalClues();
    void ScheduleInCellCooperation();
    void RunInCellCooperationRound();
    uint32_t ApplyCoopTransfer(ns3::Ptr<GroundNodeApp> app,
                               const std::set<uint16_t>& offeredFragments,
                               CooperationLinkType linkType);
    double ComputeNodeDetectionScore(ns3::Ptr<GroundNodeApp> app, uint32_t fragTotal) const;
    double ComputeNodeFalseAlarm(ns3::Ptr<GroundNodeApp> app, uint32_t fragTotal) const;
    std::string DetectionModelName() const;
    void CheckDetection(uint32_t fragTotal, const char* source);

    // Phase 4: aggregate PHY/MAC trace counters across all LrWpanNetDevices.
    // Single-threaded sim, plain uint64_t is fine. Reset in Build().
    uint64_t m_phyTxBegin = 0;
    uint64_t m_phyRxBegin = 0;
    uint64_t m_phyRxDrop  = 0;
    uint64_t m_macTx = 0;
    uint64_t m_macTxOk = 0;
    uint64_t m_macTxEnqueue = 0;
    uint64_t m_macTxDequeue = 0;
    uint64_t m_macSentPkt = 0;
    uint64_t m_macTxDrop  = 0;
    uint64_t m_macTraceConnectFail = 0;
    // From MacSentPkt(packet, retries, backoffs): sum of retry counts across
    // successfully delivered unicast frames (proxy for retransmission load).
    uint64_t m_macRetries = 0;
    uint64_t m_macBackoffs = 0;

    void ConnectPhyMacCounters();
};

}  // namespace ns3::wsn::uav

#endif  // SCENARIO1_CONFIG_H
