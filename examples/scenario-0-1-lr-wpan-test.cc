/*
 * Scenario 0.1: Native LR-WPAN Radio Communication Test
 *
 * Purpose: Test native NS-3 LR-WPAN module (802.15.4) instead of CC2420
 * Setup: 3 nodes (1 UAV, 2 ground) - same as scenario-0
 * Goal: Verify LR-WPAN works, compare with CC2420, demonstrate flexibility
 *
 * Usage:
 *   ns3 run "scenario-0-1-lr-wpan-test"
 *   ns3 run "scenario-0-1-lr-wpan-test -- --numFragments=10 --simTime=20"
 */

#include "ns3/core-module.h"
#include "../helper/scenario0-1/scenario0-1-config.h"

using namespace ns3;

int main(int argc, char* argv[]) {
    ns3::wsn::uav::Scenario01Config config;

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
