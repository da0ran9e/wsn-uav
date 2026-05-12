/*
 * Scenario 0.2: Custom Network Layer over LR-WPAN
 *
 * Purpose: Test custom network layer (Layer 3) on top of LR-WPAN MAC/PHY
 * Setup: 3 nodes (1 UAV, 2 ground) - same topology as scenario-0
 * Goal: Demonstrate network layer packet handling, routing headers, neighbor tracking
 *
 * Usage:
 *   ns3 run scenario-0-2-custom-network-test
 *   ns3 run "scenario-0-2-custom-network-test --numFragments=3 --simTime=15"
 */

#include "ns3/core-module.h"
#include "../helper/scenario0-2/scenario0-2-config.h"

using namespace ns3;

int main(int argc, char* argv[]) {
    ns3::wsn::uav::Scenario02Config config;

    CommandLine cmd;
    cmd.AddValue("simTime", "Simulation duration (seconds)", config.simulationDurationSec);
    cmd.AddValue("numFragments", "Number of packets to send", config.numFragmentsToSend);
    cmd.AddValue("broadcastInterval", "Broadcast interval (seconds)", config.broadcastIntervalSec);
    cmd.AddValue("startTime", "Start broadcast time (seconds)", config.startTimeSec);
    cmd.AddValue("txPower", "TX power (dBm)", config.txPowerDbm);
    cmd.AddValue("rxSensitivity", "RX sensitivity (dBm)", config.rxSensitivityDbm);
    cmd.Parse(argc, argv);

    auto results = config.Run();

    return results.passed ? 0 : 1;
}
