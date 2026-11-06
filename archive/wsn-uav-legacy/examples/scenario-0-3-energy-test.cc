/*
 * Scenario 0.3: Energy-Aware LR-WPAN Simulation
 *
 * Purpose: Test custom energy model for LR-WPAN, simulate battery depletion
 * Setup: 3 nodes (1 UAV, 2 ground) with battery-powered radios
 * Goal: Track energy consumption, verify energy model accuracy
 *
 * Features:
 * - Custom SimpleEnergySource (battery model)
 * - Custom DeviceEnergyModel (power consumption tracking)
 * - State transitions (TX, RX, Idle, Sleep)
 * - Energy per state breakdown
 *
 * Usage:
 *   ns3 run scenario-0-3-energy-test
 *   ns3 run "scenario-0-3-energy-test --numFragments=20 --simTime=30"
 *   ns3 run "scenario-0-3-energy-test --batteryCapacity=7200"
 */

#include "ns3/core-module.h"
#include "../helper/scenario0-3/scenario0-3-config.h"

using namespace ns3;

int main(int argc, char* argv[]) {
    ns3::wsn::uav::Scenario03Config config;

    CommandLine cmd;
    cmd.AddValue("simTime", "Simulation duration (seconds)", config.simulationDurationSec);
    cmd.AddValue("numFragments", "Number of packets to send", config.numFragmentsToSend);
    cmd.AddValue("broadcastInterval", "Broadcast interval (seconds)", config.broadcastIntervalSec);
    cmd.AddValue("startTime", "Start broadcast time (seconds)", config.startTimeSec);
    cmd.AddValue("batteryCapacity", "Battery capacity (Joules)", config.batteryCapacityJ);
    cmd.AddValue("txPower", "TX power (mW)", config.txPowerMw);
    cmd.AddValue("rxPower", "RX power (mW)", config.rxPowerMw);
    cmd.AddValue("idlePower", "Idle power (mW)", config.idlePowerMw);
    cmd.AddValue("sleepPower", "Sleep power (mW)", config.sleepPowerMw);
    cmd.Parse(argc, argv);

    auto results = config.Run();

    return results.passed ? 0 : 1;
}
