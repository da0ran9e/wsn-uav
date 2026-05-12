#include "ns3/command-line.h"
#include "ns3/core-module.h"

#include "../helper/scenario1/scenario1-config.h"

using namespace ns3;
using namespace ns3::wsn::uav;

int main(int argc, char* argv[]) {
    CommandLine cmd;

    uint32_t gridSize = 10;
    double gridSpacing = 20.0;
    double simTime = 20.0;
    double uavHeight = 20.0;

    cmd.AddValue("gridSize", "N×N grid size", gridSize);
    cmd.AddValue("gridSpacing", "Grid spacing in meters", gridSpacing);
    cmd.AddValue("simTime", "Simulation duration in seconds", simTime);
    cmd.AddValue("uavHeight", "UAV altitude in meters", uavHeight);

    cmd.Parse(argc, argv);

    Scenario1Config config;
    config.gridSize = gridSize;
    config.gridSpacing = gridSpacing;
    config.simulationDurationSec = simTime;
    config.uavStartHeight = uavHeight;

    // Three-step workflow
    config.Build();     // Step 1: Build network
    config.Schedule();  // Step 2: Schedule events
    config.Run();       // Step 3: Run simulation

    return 0;
}
