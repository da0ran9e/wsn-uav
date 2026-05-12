#ifndef SCENARIO0_2_CONFIG_H
#define SCENARIO0_2_CONFIG_H

#include <cstdint>
#include <string>

namespace ns3::wsn::uav {

struct Scenario02Results {
    uint32_t packetsSent = 0;
    uint32_t packetsReceived = 0;
    double deliveryRate = 0.0;
    bool passed = false;
    std::string message;
};

class Scenario02Config {
public:
    // Configuration parameters
    uint32_t simulationDurationSec = 10;
    uint32_t numFragmentsToSend = 5;
    double broadcastIntervalSec = 1.0;
    double startTimeSec = 2.0;

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

    Scenario02Results Run();
};

}  // namespace ns3::wsn::uav

#endif  // SCENARIO0_2_CONFIG_H
