// End-to-end SAR scenario entry point.
#include "ns3/core-module.h"
#include "../helper/sar-config.h"

#include <iostream>
#include <string>

using namespace ns3;
using namespace ns3::uavsar;

int main(int argc, char* argv[]) {
    SarScenarioConfig cfg;
    std::string outputDir;
    CommandLine cmd;
    cmd.AddValue("gridSize", "N x N sensor grid", cfg.gridSize);
    cmd.AddValue("gridSpacing", "sensor spacing (m)", cfg.gridSpacing);
    cmd.AddValue("numUav", "number of UAVs", cfg.numUav);
    cmd.AddValue("fastRatio", "fraction of UAVs on the FAST team", cfg.fastRatio);
    cmd.AddValue("seed", "RNG run seed", cfg.seed);
    cmd.AddValue("simTime", "sim duration (s)", cfg.simTime);
    cmd.AddValue("minObserve", "proposed: hold first summon until this time (s)", cfg.minObserveS);
    cmd.AddValue("clueDecay", "clue-field decay / on-node sensing range (m)", cfg.clueDecayM);
    cmd.AddValue("mcRedundancy", "tsp-mc: coded-multicast overhead factor", cfg.mcRedundancy);
    cmd.AddValue("mcRadius", "tsp-mc: VBS coverage radius m (0=design default)", cfg.mcRadiusM);
    cmd.AddValue("fastSpeed", "FAST UAV cruise m/s (0 = common speed)", cfg.fastSpeedMps);
    cmd.AddValue("dataSpeed", "DATA UAV cruise m/s (0 = common speed)", cfg.dataSpeedMps);
    cmd.AddValue("allHome", "mission completes only when EVERY UAV reported", cfg.allHome);
    cmd.AddValue("codedMulticast", "tsp-mc: rateless recovery (Zeng'18 semantics)", cfg.codedMulticast);
    cmd.AddValue("aimArgmax", "aim at strongest reporter (default; 0 = centroid ablation)", cfg.aimArgmax);
    cmd.AddValue("electSuppress", "flood the election stand-down (0 = ablation)", cfg.electSuppress);
    cmd.AddValue("adaptiveWindow", "summon when evidence settles (0 = fixed --minObserve)", cfg.adaptiveWindow);
    cmd.AddValue("dataPatrol", "DATA UAVs patrol+cue while waiting (0 = park)", cfg.dataPatrol);
    cmd.AddValue("deliverDwell", "min delivery dwell s (0 = design default)", cfg.deliverDwellS);
    cmd.AddValue("senseSigma", "detector noise sigma on clue quality (0 = ideal)", cfg.senseSigma);
    cmd.AddValue("gpsSigma", "per-node GPS error sigma in m (0 = exact)", cfg.gpsSigmaM);
    cmd.AddValue("victimOnNode", "victim sits exactly on a sensor (0 = continuous)", cfg.victimOnNode);
    cmd.AddValue("clutterCount", "confusable objects matching the reference data (0 = uniqueness)", cfg.clutterCount);
    cmd.AddValue("clutterSimMin", "min similarity of a confusable object", cfg.clutterSimMin);
    cmd.AddValue("clutterSimMax", "max similarity (1.0 = indistinguishable)", cfg.clutterSimMax);
    cmd.AddValue("scheme", "proposed | closed-loop | nocoop | pure-uav | tsp-mc", cfg.scheme);
    cmd.AddValue("outputDir", "results dir", outputDir);
    cmd.Parse(argc, argv);

    if (cfg.scheme != "proposed" && cfg.scheme != "nocoop" && cfg.scheme != "pure-uav" &&
        cfg.scheme != "tsp-mc" && cfg.scheme != "closed-loop") {
        std::cerr << "unknown --scheme=" << cfg.scheme
                  << " (expected proposed | closed-loop | nocoop | pure-uav | tsp-mc)\n";
        return 1;
    }

    if (outputDir.empty())
        outputDir = "data/results/uav-sar/" + cfg.scheme + "/run-" + std::to_string(cfg.seed);
    cfg.outputDir = outputDir;

    SarScenario sc;
    sc.Run(cfg);
    return 0;
}
