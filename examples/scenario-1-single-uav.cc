/*
 * Scenario 1: Single UAV, Grid-based Ground Network
 *
 * Simulates a single UAV disseminating K fragments over an N×N grid of ground nodes.
 * Tests paper baseline (Fig.3): Tdetect vs. grid size N ∈ {100, 400, 900, 1225}.
 *
 * Usage:
 *   ./ns3 run scenario-1-single-uav -- --gridSize=10 --numFragments=10 --seed=1 --runId=1
 *
 * Output:
 *   data/results/scenario-1/run-001/
 *     ├── metrics.csv (Tdetect, pathLength, cooperationGain)
 *     ├── trajectories.csv (UAV position trace)
 *     ├── packets.csv (individual packet records)
 *     └── config.txt (simulation parameters)
 */

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"
#include "ns3/spectrum-module.h"

// WSN-UAV module headers
#include "../helper/wsn-network-helper.h"
#include "../helper/result-writer.h"
#include "../helper/topology-helper.h"
#include "../helper/trajectory-helper.h"
#include "../models/application/fragment-dissemination-app.h"
#include "../models/application/fragment-model.h"
#include "../models/common/statistics-collector.h"
#include "../models/common/parameters.h"
#include "../models/common/types.h"

#include <iostream>
#include <sstream>
#include <iomanip>

using namespace ns3;
using namespace ns3::wsn::uav;

NS_LOG_COMPONENT_DEFINE("Scenario1SingleUav");

int
main(int argc, char* argv[])
{
    // =========================================================================
    // Default Configuration
    // =========================================================================
    SimulationConfig config;

    // =========================================================================
    // CLI Parsing
    // =========================================================================
    CommandLine cmd(__FILE__);
    cmd.AddValue("gridSize",
                 "Size of ground node grid (N×N), determines N = gridSize^2",
                 config.gridSize);
    cmd.AddValue("gridSpacing",
                 "Spacing between ground nodes in meters (default: 20m from paper)",
                 config.gridSpacing);
    cmd.AddValue("numFragments",
                 "Number of file fragments to generate (default: 10)",
                 config.numFragments);
    cmd.AddValue("uavAltitude",
                 "UAV flight altitude in meters (default: 20m)",
                 config.uavAltitude);
    cmd.AddValue("uavSpeed",
                 "UAV speed in m/s (default: 20 m/s)",
                 config.uavSpeed);
    cmd.AddValue("broadcastInterval",
                 "Interval between UAV fragment broadcasts in seconds",
                 config.broadcastInterval);
    cmd.AddValue("startupDuration",
                 "Duration of startup phase before UAV flight (seconds)",
                 config.startupDuration);
    cmd.AddValue("cooperationThreshold",
                 "Confidence threshold for cooperation trigger [0,1]",
                 config.cooperationThreshold);
    cmd.AddValue("alertThreshold",
                 "Confidence threshold for detection alert [0,1]",
                 config.alertThreshold);
    cmd.AddValue("suspiciousPercent",
                 "Fraction of network to mark as suspicious region [0,1]",
                 config.suspiciousPercent);
    cmd.AddValue("simTime",
                 "Total simulation duration in seconds",
                 config.simTime);
    cmd.AddValue("seed",
                 "Random seed for RNG reproducibility",
                 config.seed);
    cmd.AddValue("runId",
                 "Run ID for batch experiments",
                 config.runId);
    cmd.AddValue("outputDir",
                 "Output directory for results (default: data/results/scenario-1/run-NNN)",
                 config.outputDir);
    cmd.AddValue("usePerfectChannel",
                 "Use perfect (ideal) channel model, bypass path loss/BER calculations",
                 config.usePerfectChannel);
    cmd.AddValue("useGmc",
                 "Use Greedy Maximum Coverage trajectory planning (true) or nearest-neighbor (false)",
                 config.useGmc);

    cmd.Parse(argc, argv);

    // =========================================================================
    // Default Output Directory if Not Specified
    // =========================================================================
    if (config.outputDir == "src/wsn-uav/results/scenario-1/run-001")
    {
        std::ostringstream oss;
        oss << "src/wsn-uav/results/scenario-1/run-" << std::setfill('0') << std::setw(3) << config.runId;
        config.outputDir = oss.str();
    }

    // =========================================================================
    // Logging Configuration
    // =========================================================================
    LogComponentEnable("Scenario1SingleUav", LOG_LEVEL_INFO);
    LogComponentEnable("WsnNetworkHelper", LOG_LEVEL_INFO);
    LogComponentEnable("FragmentDisseminationApp", LOG_LEVEL_INFO);

    // =========================================================================
    // Configuration Validation
    // =========================================================================
    std::string validationError;
    if (!config.Validate(validationError))
    {
        NS_LOG_ERROR("Configuration validation failed: " << validationError);
        std::cerr << "ERROR: " << validationError << std::endl;
        return 1;
    }

    // =========================================================================
    // Simulation Info
    // =========================================================================
    uint32_t totalNodes = config.gridSize * config.gridSize;
    NS_LOG_INFO("=== Scenario 1: Single UAV Fragment Dissemination ===");
    NS_LOG_INFO("Grid Configuration:");
    NS_LOG_INFO("  Grid size: " << config.gridSize << " × " << config.gridSize
                                 << " = " << totalNodes << " nodes");
    NS_LOG_INFO("  Spacing: " << config.gridSpacing << " m");
    NS_LOG_INFO("  Area: " << (config.gridSpacing * (config.gridSize - 1)) << " × "
                           << (config.gridSpacing * (config.gridSize - 1)) << " m²");
    NS_LOG_INFO("");
    NS_LOG_INFO("Fragment & Network:");
    NS_LOG_INFO("  Fragments: " << config.numFragments);
    NS_LOG_INFO("  Master file confidence: 0.90");
    NS_LOG_INFO("  Cooperation threshold (τ_coop): " << config.cooperationThreshold);
    NS_LOG_INFO("  Alert threshold (τ_alert): " << config.alertThreshold);
    NS_LOG_INFO("  Suspicious region: " << (config.suspiciousPercent * 100.0) << "%");
    NS_LOG_INFO("");
    NS_LOG_INFO("UAV Flight:");
    NS_LOG_INFO("  Altitude: " << config.uavAltitude << " m");
    NS_LOG_INFO("  Speed: " << config.uavSpeed << " m/s");
    NS_LOG_INFO("  Broadcast interval: " << config.broadcastInterval << " s");
    NS_LOG_INFO("  Trajectory planning: " << (config.useGmc ? "GMC (greedy set-cover)" : "Nearest-neighbor"));
    NS_LOG_INFO("");
    NS_LOG_INFO("Timing:");
    NS_LOG_INFO("  Startup duration: " << config.startupDuration << " s");
    NS_LOG_INFO("  Simulation time: " << config.simTime << " s");
    NS_LOG_INFO("  Seed: " << config.seed << ", Run ID: " << config.runId);
    NS_LOG_INFO("");
    NS_LOG_INFO("Channel:");
    NS_LOG_INFO("  Model: " << (config.usePerfectChannel ? "Perfect (ideal)" : "CC2420 with path loss & BER"));
    NS_LOG_INFO("");
    NS_LOG_INFO("Output: " << config.outputDir);

    // =========================================================================
    // Run Simulation
    // =========================================================================
    WsnNetworkHelper helper(config);

    NS_LOG_INFO("Building network...");
    helper.Build();

    NS_LOG_INFO("Scheduling events...");
    helper.Schedule();

    NS_LOG_INFO("Running simulation...");
    helper.Run();

    // =========================================================================
    // Collect Results
    // =========================================================================
    const SimulationResults& results = helper.GetResults();
    Ptr<StatisticsCollector> stats = helper.GetStats();

    // =========================================================================
    // Write Results
    // =========================================================================
    NS_LOG_INFO("Writing results...");
    ResultWriter writer(config.outputDir);
    writer.Initialize();
    writer.WriteMetrics(results, config);
    writer.WriteTrajectories(stats);
    writer.WritePackets(stats, helper.GetGroundNodes());
    writer.WriteConfig(config);
    writer.WriteVisualizationData(results, config, helper.GetGroundNodes(), stats,
                                   results.candidateNodeIds);

    // =========================================================================
    // Print Summary
    // =========================================================================
    NS_LOG_INFO("");
    NS_LOG_INFO("=== RESULTS SUMMARY ===");
    if (results.detected)
    {
        NS_LOG_INFO("Detection: YES");
        NS_LOG_INFO("Detection time (Tdetect): " << std::fixed << std::setprecision(3)
                                                   << results.detectionTime << " s");
        NS_LOG_INFO("Detection node: " << results.detectionNodeId);
    }
    else
    {
        NS_LOG_INFO("Detection: NO (timeout at " << config.simTime << " s)");
    }

    NS_LOG_INFO("UAV path length: " << std::fixed << std::setprecision(2)
                                     << results.uavPathLength << " m");
    NS_LOG_INFO("Cooperation gain: " << std::fixed << std::setprecision(1)
                                      << (results.cooperationGain * 100.0) << "%");
    NS_LOG_INFO("Candidate nodes: " << results.candidateNodes << " / " << totalNodes);
    NS_LOG_INFO("");
    NS_LOG_INFO("Output files:");
    NS_LOG_INFO("  " << config.outputDir << "/metrics.csv");
    NS_LOG_INFO("  " << config.outputDir << "/trajectories.csv");
    NS_LOG_INFO("  " << config.outputDir << "/packets.csv");
    NS_LOG_INFO("  " << config.outputDir << "/config.txt");
    NS_LOG_INFO("  " << config.outputDir << "/wsn-uav-result.html (✓ Canvas visualization - Open this!)");

    return 0;
}
