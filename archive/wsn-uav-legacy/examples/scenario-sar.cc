#include "ns3/command-line.h"
#include "ns3/core-module.h"

#include "../helper/sar/sar-config.h"

#include <string>

using namespace ns3;
using namespace ns3::wsn::uav;

int main(int argc, char* argv[]) {
    uint32_t gridSize = 8;
    double gridSpacing = 20.0;
    uint32_t numUav = 4;
    uint32_t numFrag = 12;
    uint32_t maxFragBytes = 4000;
    uint32_t seed = 1;
    double simTime = 120.0;
    std::string scheme = "proposed";      // proposed | single | nocoop
    uint32_t confirmNeighbors = 1;
    double confirmTimeout = 0.5;
    uint32_t beaconQuota = 60;
    std::string outputDir = "";

    CommandLine cmd;
    cmd.AddValue("gridSize", "N x N sensor grid", gridSize);
    cmd.AddValue("gridSpacing", "Grid spacing (m)", gridSpacing);
    cmd.AddValue("numUav", "Number of UAVs", numUav);
    cmd.AddValue("numFrag", "Number of search-data fragments", numFrag);
    cmd.AddValue("maxFragBytes", "Largest fragment size (bytes)", maxFragBytes);
    cmd.AddValue("seed", "RNG run seed", seed);
    cmd.AddValue("simTime", "Simulation duration (s)", simTime);
    cmd.AddValue("scheme", "proposed | single | nocoop", scheme);
    cmd.AddValue("confirmNeighbors", "neighbours required before beacon", confirmNeighbors);
    cmd.AddValue("confirmTimeout", "confirm deadline (s)", confirmTimeout);
    cmd.AddValue("beaconQuota", "max beacons per event", beaconQuota);
    cmd.AddValue("outputDir", "results output dir", outputDir);
    cmd.Parse(argc, argv);

    SarConfig cfg;
    cfg.gridSize = gridSize;
    cfg.gridSpacing = gridSpacing;
    cfg.numUav = numUav;
    cfg.numFrag = numFrag;
    cfg.maxFragBytes = maxFragBytes;
    cfg.seed = seed;
    cfg.simTime = simTime;
    cfg.confirmNeighbors = confirmNeighbors;
    cfg.confirmTimeout = confirmTimeout;
    cfg.beaconQuota = beaconQuota;
    if (scheme == "single") cfg.scheme = sar::Scheme::SINGLE;
    else if (scheme == "nocoop") cfg.scheme = sar::Scheme::NOCOOP;
    else cfg.scheme = sar::Scheme::PROPOSED;

    if (outputDir.empty())
        outputDir = "data/results/scenario-sar/" + scheme + "/run-" + std::to_string(seed);
    cfg.outputDir = outputDir;

    cfg.Build();
    cfg.Schedule();
    cfg.Run();
    return 0;
}
