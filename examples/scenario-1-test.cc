#include "ns3/command-line.h"
#include "ns3/core-module.h"

#include "../helper/scenario1/scenario1-config.h"

using namespace ns3;
using namespace ns3::wsn::uav;

int main(int argc, char* argv[]) {
    CommandLine cmd;

    uint32_t gridSize = 10;
    double gridSpacing = 45.0;  // match example4 paper testbed
    double simTime = 1800.0;
    double uavHeight = 20.0;
    double cellSize = 80.0;
    double cellNeighborRange = 120.0;
    uint32_t cellColors = 6;
    int32_t clueTargetNodeId = -1;
    uint32_t clueSeed = 20260525;
    double clueStrongRadius = 40.0;
    double clueWeakRadius = 80.0;
    double clueDecay = 60.0;
    double clueMaxBlurredQuality = 0.65;
    double clueFalsePositiveRate = 0.08;
    bool inCellCoop = true;
    double inCellCoopInterval = 5.0;
    double inCellCoopStopRatio = 0.80;
    bool interCellCoop = true;
    uint32_t interCellCoopEveryRounds = 3;
    double interCellCoopRange = 130.0;
    double coopAlertRatio = 0.75;
    double detectionAlertThreshold = 0.75;
    uint32_t coopInCellPacketBudget = 64;
    uint32_t coopInterCellPacketBudget = 160;
    double coopInCellManifestSuccess = 0.98;
    double coopInterCellManifestSuccess = 0.95;
    double coopInCellSuccess = 0.92;
    double coopInterCellSuccess = 0.82;
    std::string detectionModel = "clue-weighted";
    std::string flightPathModel = "cell-aware-gmc";
    std::string broadcastModel = "cyclic";
    uint32_t randomWaypointBudget = 64;

    cmd.AddValue("gridSize", "N×N grid size", gridSize);
    cmd.AddValue("gridSpacing", "Grid spacing in meters", gridSpacing);
    cmd.AddValue("simTime", "Simulation duration in seconds", simTime);
    cmd.AddValue("uavHeight", "UAV altitude in meters", uavHeight);
    cmd.AddValue("cellSize", "Cell size in meters for BS bootstrap cell layer", cellSize);
    cmd.AddValue("cellNeighborRange", "Neighbor range in meters for cell-layer routing graph", cellNeighborRange);
    cmd.AddValue("cellColors", "Number of cell colors for scheduling/visualization", cellColors);
    cmd.AddValue("clueTargetNodeId", "Ground node id with the exact clue (-1 selects center-most node)", clueTargetNodeId);
    cmd.AddValue("clueSeed", "Deterministic seed for blurred/false-positive clue placement", clueSeed);
    cmd.AddValue("clueStrongRadius", "Radius in meters for strong blurred clues around target", clueStrongRadius);
    cmd.AddValue("clueWeakRadius", "Radius in meters for weak blurred clues around target", clueWeakRadius);
    cmd.AddValue("clueDecay", "Exponential clue-quality decay distance in meters", clueDecay);
    cmd.AddValue("clueMaxBlurredQuality", "Maximum non-target clue quality", clueMaxBlurredQuality);
    cmd.AddValue("clueFalsePositiveRate", "Background false-positive probability outside weak radius", clueFalsePositiveRate);
    cmd.AddValue("inCellCoop", "Enable abstract free cooperation inside each cell", inCellCoop);
    cmd.AddValue("inCellCoopInterval", "In-cell cooperation round interval in seconds", inCellCoopInterval);
    cmd.AddValue("inCellCoopStopRatio", "Nodes at or above this L0 ratio stop pulling in-cell fragments", inCellCoopStopRatio);
    cmd.AddValue("interCellCoop", "Enable abstract gateway-to-gateway cooperation between adjacent cells", interCellCoop);
    cmd.AddValue("interCellCoopEveryRounds", "Run inter-cell cooperation every N in-cell rounds", interCellCoopEveryRounds);
    cmd.AddValue("interCellCoopRange", "Cell-centroid range in meters for gateway-to-gateway cooperation", interCellCoopRange);
    cmd.AddValue("coopAlertRatio", "Cells/nodes above this fragment ratio stop requesting cross-cell fragments", coopAlertRatio);
    cmd.AddValue("detectionAlertThreshold", "Recognition/confidence threshold for detection time", detectionAlertThreshold);
    cmd.AddValue("detectionModel", "Detection model: fragment-ratio, clue-weighted, noisy-or", detectionModel);
    cmd.AddValue("flightPathModel", "Flight path model: cell-aware-gmc, per-node-gmc, cell-centroid-sweep, random-waypoint, nearest-neighbor", flightPathModel);
    cmd.AddValue("broadcastModel", "Broadcast model: cyclic, random, utility-weighted, unicast-full", broadcastModel);
    cmd.AddValue("randomWaypointBudget", "Max random waypoints (0 = one per non-empty cell)", randomWaypointBudget);
    cmd.AddValue("coopInCellPacketBudget", "Cooperation data-packet budget per node per in-cell round", coopInCellPacketBudget);
    cmd.AddValue("coopInterCellPacketBudget", "Cooperation data-packet budget per node per inter-cell round", coopInterCellPacketBudget);
    cmd.AddValue("coopInCellManifestSuccess", "Manifest packet success probability for in-cell cooperation", coopInCellManifestSuccess);
    cmd.AddValue("coopInterCellManifestSuccess", "Manifest packet success probability for inter-cell cooperation", coopInterCellManifestSuccess);
    cmd.AddValue("coopInCellSuccess", "Target full-fragment success probability after in-cell packet-level cooperation", coopInCellSuccess);
    cmd.AddValue("coopInterCellSuccess", "Target full-fragment success probability after inter-cell packet-level cooperation", coopInterCellSuccess);

    cmd.Parse(argc, argv);

    Scenario1Config config;
    config.gridSize = gridSize;
    config.gridSpacing = gridSpacing;
    config.simulationDurationSec = simTime;
    config.uavStartHeight = uavHeight;
    config.cellSizeMeters = cellSize;
    config.cellNeighborRangeMeters = cellNeighborRange;
    config.cellColorCount = cellColors;
    config.clueTargetNodeId = clueTargetNodeId;
    config.clueSeed = clueSeed;
    config.clueStrongRadiusMeters = clueStrongRadius;
    config.clueWeakRadiusMeters = clueWeakRadius;
    config.clueDecayMeters = clueDecay;
    config.clueMaxBlurredQuality = clueMaxBlurredQuality;
    config.clueFalsePositiveRate = clueFalsePositiveRate;
    config.inCellCooperationEnabled = inCellCoop;
    config.inCellCooperationIntervalSec = inCellCoopInterval;
    config.inCellCooperationStopRatio = inCellCoopStopRatio;
    config.interCellCooperationEnabled = interCellCoop;
    config.interCellCooperationEveryRounds = interCellCoopEveryRounds;
    config.interCellCooperationRangeMeters = interCellCoopRange;
    config.cooperationAlertRatio = coopAlertRatio;
    config.detectionAlertThreshold = detectionAlertThreshold;
    config.coopInCellPacketBudgetPerNode = coopInCellPacketBudget;
    config.coopInterCellPacketBudgetPerNode = coopInterCellPacketBudget;
    config.coopInCellManifestSuccessProb = coopInCellManifestSuccess;
    config.coopInterCellManifestSuccessProb = coopInterCellManifestSuccess;
    config.coopInCellFragmentSuccessProb = coopInCellSuccess;
    config.coopInterCellFragmentSuccessProb = coopInterCellSuccess;
    config.randomWaypointBudget = randomWaypointBudget;
    if (detectionModel == "fragment-ratio") {
        config.detectionModel = DetectionModel::FRAGMENT_RATIO;
    } else if (detectionModel == "clue-weighted") {
        config.detectionModel = DetectionModel::CLUE_WEIGHTED;
    } else if (detectionModel == "noisy-or") {
        config.detectionModel = DetectionModel::NOISY_OR;
    } else {
        NS_ABORT_MSG("Unknown detectionModel=" << detectionModel
                     << " (expected fragment-ratio, clue-weighted, noisy-or)");
    }
    if (flightPathModel == "cell-aware-gmc") {
        config.flightPathModel = FlightPathModel::CELL_AWARE_GMC;
    } else if (flightPathModel == "per-node-gmc") {
        config.flightPathModel = FlightPathModel::PER_NODE_GMC;
    } else if (flightPathModel == "nearest-neighbor") {
        config.flightPathModel = FlightPathModel::NEAREST_NEIGHBOR;
    } else if (flightPathModel == "cell-centroid-sweep") {
        config.flightPathModel = FlightPathModel::CELL_CENTROID_SWEEP;
    } else if (flightPathModel == "random-waypoint") {
        config.flightPathModel = FlightPathModel::RANDOM_WAYPOINT;
    } else {
        NS_ABORT_MSG("Unknown flightPathModel=" << flightPathModel
                     << " (expected cell-aware-gmc, per-node-gmc, cell-centroid-sweep, random-waypoint, nearest-neighbor)");
    }
    if (broadcastModel == "cyclic") {
        config.broadcastModel = BroadcastModel::CYCLIC;
    } else if (broadcastModel == "random") {
        config.broadcastModel = BroadcastModel::RANDOM;
    } else if (broadcastModel == "unicast-full") {
        config.broadcastModel = BroadcastModel::UNICAST_FULL;
    } else if (broadcastModel == "utility-weighted") {
        config.broadcastModel = BroadcastModel::UTILITY_WEIGHTED;
    } else {
        NS_ABORT_MSG("Unknown broadcastModel=" << broadcastModel
                     << " (expected cyclic, random, utility-weighted, unicast-full)");
    }

    // Three-step workflow
    config.Build();     // Step 1: Build network
    config.Schedule();  // Step 2: Schedule events
    config.Run();       // Step 3: Run simulation

    return 0;
}
