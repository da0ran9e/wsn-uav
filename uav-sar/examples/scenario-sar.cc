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
    cmd.AddValue("scheme", "proposed | nocoop | pure-uav", cfg.scheme);
    cmd.AddValue("outputDir", "results dir", outputDir);
    cmd.Parse(argc, argv);

    if (cfg.scheme != "proposed" && cfg.scheme != "nocoop" && cfg.scheme != "pure-uav") {
        std::cerr << "unknown --scheme=" << cfg.scheme
                  << " (expected proposed | nocoop | pure-uav)\n";
        return 1;
    }

    if (outputDir.empty())
        outputDir = "data/results/uav-sar/" + cfg.scheme + "/run-" + std::to_string(cfg.seed);
    cfg.outputDir = outputDir;

    SarScenario sc;
    sc.Run(cfg);
    return 0;
}
