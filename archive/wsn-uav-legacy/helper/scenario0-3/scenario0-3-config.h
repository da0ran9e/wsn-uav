#ifndef SCENARIO0_3_CONFIG_H
#define SCENARIO0_3_CONFIG_H

#include <cstdint>
#include <string>

namespace ns3::wsn::uav {

struct Scenario03Results {
    uint32_t packetsSent = 0;
    uint32_t packetsReceived = 0;
    double deliveryRate = 0.0;

    // Energy results
    double initialBatteryJ = 0.0;
    double remainingEnergyJ = 0.0;
    double totalConsumedJ = 0.0;
    double energyPerPacketJ = 0.0;

    bool passed = false;
    std::string message;
};

class Scenario03Config {
public:
    // Simulation parameters
    uint32_t simulationDurationSec = 20;
    uint32_t numFragmentsToSend = 10;
    double broadcastIntervalSec = 1.0;
    double startTimeSec = 1.0;

    // Node positions
    struct Position {
        double x, y, z;
    };
    Position uavPos = {0, 0, 20};
    Position ground0Pos = {10, 0, 0};
    Position ground1Pos = {50, 0, 0};

    // Radio parameters
    double txPowerDbm = 0.0;
    double rxSensitivityDbm = -95.0;
    uint32_t packetSizeBytes = 64;

    // Propagation model parameters
    double pathLossExponent = 3.0;
    double referenceDistance = 1.0;
    double referenceLoss = 46.6776;

    // Energy parameters
    double batteryCapacityJ = 3600.0;  // 3600J = 1Wh (typical AA battery)
    double txPowerMw = 52.0;           // TX power consumption (mW)
    double rxPowerMw = 62.0;           // RX power consumption (mW)
    double idlePowerMw = 0.02;         // Idle power consumption (mW)
    double sleepPowerMw = 0.001;       // Sleep power consumption (mW)

    Scenario03Results Run();
};

}  // namespace ns3::wsn::uav

#endif  // SCENARIO0_3_CONFIG_H
