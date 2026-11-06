#ifndef SCENARIO0_1_CONFIG_H
#define SCENARIO0_1_CONFIG_H

#include <cstdint>
#include <string>

namespace ns3::wsn::uav {

struct Scenario01Results {
    uint32_t packetsSent = 0;
    uint32_t packetsReceived = 0;
    double deliveryRate = 0.0;
    bool passed = false;
    std::string message;
};

class Scenario01Config {
public:
    // Configuration parameters (settable before Run())
    uint32_t simulationDurationSec = 10;
    uint32_t numFragmentsToSend = 5;
    double broadcastIntervalSec = 1.0;
    double startTimeSec = 2.0;

    // Node positions
    struct Position {
        double x, y, z;
    };
    Position uavPos = {0, 0, 20};      // UAV at (0,0,20)
    Position ground0Pos = {10, 0, 0};   // Ground0 at (10,0,0)
    Position ground1Pos = {50, 0, 0};   // Ground1 at (50,0,0)

    // Radio parameters
    double txPowerDbm = 0.0;
    double rxSensitivityDbm = -95.0;
    uint32_t packetSizeBytes = 64;

    // Propagation model parameters
    double pathLossExponent = 3.0;
    double referenceDistance = 1.0;
    double referenceLoss = 46.6776;

    Scenario01Results Run();
};

}  // namespace ns3::wsn::uav

#endif  // SCENARIO0_1_CONFIG_H
