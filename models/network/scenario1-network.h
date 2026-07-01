#ifndef SCENARIO1_NETWORK_H
#define SCENARIO1_NETWORK_H

#include "ns3/node-container.h"
#include "ns3/net-device-container.h"
#include "ns3/ptr.h"
#include "ns3/lr-wpan-helper.h"

namespace ns3::wsn::uav {

struct NetworkPosition {
    double x;
    double y;
    double z;
};

struct NetworkConfig {
    // Topology
    uint32_t gridSize = 10;
    double gridSpacing = 45.0;
    NetworkPosition baseStationPos{-100.0, -100.0, 0.0};
    NetworkPosition uavStartPos{-100.0, -100.0, 20.0};

    // Radio
    double txPowerDbm = 0.0;
    double rxSensitivityDbm = -95.0;
    double pathLossExponent = 3.0;
    double referenceDistance = 1.0;
    double referenceLoss = 46.6;
};

struct NetworkSetup {
    ns3::NodeContainer sensorNodes;
    ns3::NodeContainer baseStationNode;
    ns3::NodeContainer uavNode;

    ns3::NetDeviceContainer sensorDevices;
    ns3::NetDeviceContainer baseStationDevice;
    ns3::NetDeviceContainer uavDevice;

    uint32_t bsNodeId;
    uint32_t uavNodeId;
};

class Scenario1Network {
public:
    explicit Scenario1Network(const NetworkConfig& cfg);

    // Builds the network. `lrWpan` is borrowed by reference and MUST outlive
    // the simulation: its destructor disposes the channel (NS-3 LrWpanHelper
    // behaviour), so destroying it early breaks all RX paths.
    NetworkSetup Build(ns3::LrWpanHelper& lrWpan);

private:
    NetworkConfig m_cfg;

    void CreateNodes(NetworkSetup& setup);
    void SetupMobility(NetworkSetup& setup);
    void InstallRadio(NetworkSetup& setup, ns3::LrWpanHelper& lrWpan);
};

}  // namespace ns3::wsn::uav

#endif  // SCENARIO1_NETWORK_H
