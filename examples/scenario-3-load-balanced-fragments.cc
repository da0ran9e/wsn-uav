/*
 * Scenario 3: Load-Balanced Fragments with Size-Dependent Transmission
 *
 * Simulates 3 UAVs distributing fragments of different sizes.
 * Fragments are sorted by size (large → small) and assigned:
 *   - UAV 0: largest fragments (longer transmission time)
 *   - UAV 1: medium fragments
 *   - UAV 2: smallest fragments (shorter transmission time, faster broadcasts)
 *
 * Transmission time per fragment = (sizeBytes * 8 bits) / DATA_RATE_BPS
 *
 * Usage:
 *   ./ns3 run scenario-3-load-balanced-fragments -- --gridSize=10 --seed=1 --runId=1
 *
 * Output:
 *   src/wsn-uav/results/scenario-3/run-001/
 *     ├── metrics.csv (includes uav_X_fragment_ids, fragment_X_size_bytes)
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

NS_LOG_COMPONENT_DEFINE("Scenario3LoadBalanced");

int
main(int argc, char* argv[])
{
    // =========================================================================
    // Default Configuration
    // =========================================================================
    SimulationConfig config;
    config.numUavs = 3;  // 3 UAVs with load-balanced fragments
    config.fragmentMinSizeBytes = 1000;    // 1 KB minimum
    config.fragmentMaxSizeBytes = 20000;   // 20 KB maximum

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
    cmd.AddValue("fragmentMinSizeBytes",
                 "Minimum fragment size in bytes (default: 1000)",
                 config.fragmentMinSizeBytes);
    cmd.AddValue("fragmentMaxSizeBytes",
                 "Maximum fragment size in bytes (default: 20000)",
                 config.fragmentMaxSizeBytes);
    cmd.AddValue("uavAltitude",
                 "UAV flight altitude in meters (default: 20m)",
                 config.uavAltitude);
    cmd.AddValue("uavSpeed",
                 "UAV speed in m/s (default: 20 m/s)",
                 config.uavSpeed);
    cmd.AddValue("broadcastInterval",
                 "Base broadcast interval in seconds (fallback for sizeBytes=0)",
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
                 "Output directory for results (default: src/wsn-uav/results/scenario-3/run-NNN)",
                 config.outputDir);
    cmd.AddValue("usePerfectChannel",
                 "Use perfect (ideal) channel model, bypass path loss/BER calculations",
                 config.usePerfectChannel);
    cmd.AddValue("useGmc",
                 "Use Greedy Maximum Coverage trajectory planning (true) or nearest-neighbor (false)",
                 config.useGmc);
    cmd.AddValue("useLoadBasedSpeed",
                 "Adjust UAV speed based on fragment load (Phase 1)",
                 config.useLoadBasedSpeed);
    cmd.AddValue("minSpeedFactor",
                 "Min speed as fraction of base speed [0,1]",
                 config.minSpeedFactor);
    cmd.AddValue("maxSpeedFactor",
                 "Max speed as fraction of base speed [0,1]",
                 config.maxSpeedFactor);
    cmd.AddValue("useDirectionalBias",
                 "Apply directional trajectory bias (±30m offset per UAV) - Phase 1 experimental",
                 config.useDirectionalBias);

    cmd.Parse(argc, argv);

    // =========================================================================
    // Default Output Directory if Not Specified
    // =========================================================================
    if (config.outputDir == "src/wsn-uav/results/scenario-1/run-001")
    {
        std::ostringstream oss;
        oss << "src/wsn-uav/results/scenario-3/run-" << std::setfill('0') << std::setw(3) << config.runId;
        config.outputDir = oss.str();
    }

    // =========================================================================
    // Logging Configuration
    // =========================================================================
    LogComponentEnable("Scenario3LoadBalanced", LOG_LEVEL_INFO);
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
    NS_LOG_INFO("=== Scenario 3: Load-Balanced Fragments with Size-Dependent Transmission ===");
    NS_LOG_INFO("Grid Configuration:");
    NS_LOG_INFO("  Grid size: " << config.gridSize << " × " << config.gridSize
                                 << " = " << totalNodes << " nodes");
    NS_LOG_INFO("  Spacing: " << config.gridSpacing << " m");
    NS_LOG_INFO("  Area: " << (config.gridSpacing * (config.gridSize - 1)) << " × "
                           << (config.gridSpacing * (config.gridSize - 1)) << " m²");
    NS_LOG_INFO("");
    NS_LOG_INFO("Fragment & Network:");
    NS_LOG_INFO("  Fragments: " << config.numFragments);
    NS_LOG_INFO("  Fragment size range: " << config.fragmentMinSizeBytes << " - "
                                           << config.fragmentMaxSizeBytes << " bytes");
    NS_LOG_INFO("  Master file confidence: 0.90");
    NS_LOG_INFO("  Cooperation threshold (τ_coop): " << config.cooperationThreshold);
    NS_LOG_INFO("  Alert threshold (τ_alert): " << config.alertThreshold);
    NS_LOG_INFO("  Suspicious region: " << (config.suspiciousPercent * 100.0) << "%");
    NS_LOG_INFO("");
    NS_LOG_INFO("UAV Flight:");
    NS_LOG_INFO("  Count: " << config.numUavs << " UAVs");
    NS_LOG_INFO("  Altitude: " << config.uavAltitude << " m");
    NS_LOG_INFO("  Speed: " << config.uavSpeed << " m/s");
    NS_LOG_INFO("  Fragment distribution: Large→UAV0, Medium→UAV1, Small→UAV2");
    NS_LOG_INFO("  TX time per fragment: (sizeBytes * 8) / DATA_RATE_BPS");
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

    NS_LOG_INFO("Total UAV path length: " << std::fixed << std::setprecision(2)
                                           << results.totalUavPathLength << " m");

    // Per-UAV statistics
    for (const auto& kv : results.uavPathLengths) {
        NS_LOG_INFO("UAV " << kv.first << " path length: " << std::fixed << std::setprecision(2)
                           << kv.second << " m");
    }
    for (const auto& kv : results.uavFragmentIds) {
        std::stringstream fragStr;
        for (size_t i = 0; i < kv.second.size(); i++) {
            if (i > 0) fragStr << ", ";
            fragStr << kv.second[i];
        }
        NS_LOG_INFO("UAV " << kv.first << " fragments: " << kv.second.size()
                           << " (IDs: " << fragStr.str() << ")");
    }
    for (const auto& kv : results.fragmentSizesBytes) {
        NS_LOG_INFO("Fragment " << kv.first << " size: " << kv.second << " bytes");
    }

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
