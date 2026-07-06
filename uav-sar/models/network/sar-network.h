#ifndef UAV_SAR_NETWORK_H
#define UAV_SAR_NETWORK_H

// Scenario network: 1 BS (edge) + M UAVs + N×N ground sensors on ONE shared
// LR-WPAN channel with a realistic air/ground propagation stack
// (AirGroundLoss + Nakagami fading + log-normal shadowing). Node-id order is
// fixed: BS=0, UAVs=1..M, sensors after.

#include "ns3/node-container.h"
#include "ns3/net-device-container.h"
#include "ns3/lr-wpan-helper.h"
#include "ns3/spectrum-channel.h"
#include "ns3/ptr.h"
#include "ns3/vector.h"

#include <cstdint>
#include <vector>

namespace ns3::uavsar {

// Build the shared realistic channel (reused by the scenario and the channel
// smoke test). Deterministic path loss + Nakagami small-scale fading +
// log-normal shadowing + constant-speed delay.
ns3::Ptr<ns3::SpectrumChannel> BuildSarChannel();

// LrWpanHelper only assigns EXTENDED (64-bit) addresses; short 16-bit
// addresses stay at the default, so every device would share one address and
// MAC unicast filtering would never filter. Assign unique short addresses.
// Returns the next free address value.
uint16_t AssignShortAddresses(const ns3::NetDeviceContainer& devs, uint16_t first);

struct SarNetworkConfig {
    uint32_t gridSize = 8;
    double gridSpacing = 20.0;   // m
    uint32_t numUav = 4;
    ns3::Vector bsPos{-200.0, -200.0, 0.0};
    double uavStartAltitude = 0.0;   // launch from the ground; the app climbs
};

struct SarNetworkSetup {
    ns3::NodeContainer bs;
    ns3::NodeContainer uavs;
    ns3::NodeContainer sensors;
    ns3::NetDeviceContainer bsDev;
    ns3::NetDeviceContainer uavDevs;
    ns3::NetDeviceContainer sensorDevs;
    uint32_t bsId = 0;
    uint32_t firstUavId = 0;
    uint32_t firstSensorId = 0;
    std::vector<ns3::Vector> sensorPositions;   // for the substrate layer
};

class SarNetwork {
public:
    explicit SarNetwork(const SarNetworkConfig& cfg) : m_cfg(cfg) {}
    // lrWpan is borrowed and MUST outlive the simulation.
    SarNetworkSetup Build(ns3::LrWpanHelper& lrWpan);

private:
    SarNetworkConfig m_cfg;
};

}  // namespace ns3::uavsar

#endif  // UAV_SAR_NETWORK_H
