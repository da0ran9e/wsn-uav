#ifndef WSN_UAV_SAR_NETWORK_H
#define WSN_UAV_SAR_NETWORK_H

// Network builder for the SAR scenario: 1 BS at the edge + M UAVs + N×N ground
// sensors, all on ONE shared LR-WPAN channel. Mirrors Scenario1Network but with
// a multi-UAV fleet. Node-ID order is fixed: BS=0, UAVs=1..M, sensors after.

#include "ns3/node-container.h"
#include "ns3/net-device-container.h"
#include "ns3/ptr.h"
#include "ns3/lr-wpan-helper.h"

#include <cstdint>

namespace ns3::wsn::uav {

struct SarNetPosition { double x, y, z; };

struct SarNetworkConfig {
    uint32_t gridSize = 8;
    double gridSpacing = 20.0;
    uint32_t numUav = 4;
    SarNetPosition baseStationPos{-200.0, -200.0, 0.0};
    SarNetPosition uavStartPos{-200.0, -200.0, 20.0};

    double txPowerDbm = 0.0;
    double rxSensitivityDbm = -95.0;
    double pathLossExponent = 3.0;
    double referenceDistance = 1.0;
    double referenceLoss = 46.6;
};

struct SarNetworkSetup {
    ns3::NodeContainer sensorNodes;
    ns3::NodeContainer baseStationNode;
    ns3::NodeContainer uavNodes;          // M UAVs

    ns3::NetDeviceContainer sensorDevices;
    ns3::NetDeviceContainer baseStationDevice;
    ns3::NetDeviceContainer uavDevices;   // M devices

    uint32_t bsNodeId = 0;
    uint32_t firstUavNodeId = 0;
    uint32_t firstSensorNodeId = 0;
};

class SarNetwork {
public:
    explicit SarNetwork(const SarNetworkConfig& cfg);

    // `lrWpan` is borrowed and MUST outlive the simulation (its destructor
    // disposes the channel, breaking all RX). Keep it on the orchestrator.
    SarNetworkSetup Build(ns3::LrWpanHelper& lrWpan);

private:
    SarNetworkConfig m_cfg;
    void CreateNodes(SarNetworkSetup& s);
    void SetupMobility(SarNetworkSetup& s);
    void InstallRadio(SarNetworkSetup& s, ns3::LrWpanHelper& lrWpan);
};

}  // namespace ns3::wsn::uav

#endif  // WSN_UAV_SAR_NETWORK_H
