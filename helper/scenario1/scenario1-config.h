#ifndef SCENARIO1_CONFIG_H
#define SCENARIO1_CONFIG_H

#include "../../models/network/scenario1-network.h"
#include "../../models/application/basestation-app.h"
#include "../../models/application/uav-app.h"
#include "../../models/application/ground-node-app.h"

#include "ns3/ptr.h"
#include "ns3/lr-wpan-helper.h"

#include <string>
#include <vector>
#include <memory>

namespace ns3::wsn::uav {

struct Scenario1Results {
    bool passed = false;
    std::string message;
    uint32_t packetsSent = 0;
    uint32_t packetsReceived = 0;
    double deliveryRate = 0.0;
};

class Scenario1Config {
public:
    // Network parameters
    uint32_t gridSize = 10;
    double gridSpacing = 20.0;
    double uavStartHeight = 20.0;

    // Simulation parameters
    double startTimeSec = 1.0;
    uint32_t numFragmentsToSend = 10;
    double broadcastIntervalSec = 1.0;
    double simulationDurationSec = 20.0;

    // Scenario name; log file is created under
    //   src/wsn-uav/docs/visualize/result/<scenarioName>/<dd-MM-yy>/<hh-mm-ss>.md
    std::string scenarioName = "scenario1";

    // Three-step workflow
    void Build();     // Step 1: Build network from model
    void Schedule();  // Step 2: Schedule events
    void Run();       // Step 3: Run simulation

private:
    NetworkSetup m_setup;

    // LrWpanHelper MUST live for entire simulation. Its destructor calls
    // m_channel->Dispose() which clears the channel's PHY list, breaking RX.
    std::unique_ptr<ns3::LrWpanHelper> m_lrWpan;

    // Application references
    ns3::Ptr<BaseStationApp> m_bsApp;
    ns3::Ptr<UavApp> m_uavApp;
    std::vector<ns3::Ptr<GroundNodeApp>> m_groundApps;

    // Helper function for staggered startup
    void RandomDelayedStartUp(double delayThreshold);
};

}  // namespace ns3::wsn::uav

#endif  // SCENARIO1_CONFIG_H
