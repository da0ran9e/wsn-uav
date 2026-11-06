#ifndef BASESTATION_APP_H
#define BASESTATION_APP_H

#include "ns3/application.h"
#include "ns3/net-device.h"
#include "ns3/node-container.h"
#include "ns3/ptr.h"

#include <cstdint>
#include <vector>

namespace ns3::wsn::uav {

class BaseStationApp : public Application {
public:
    static TypeId GetTypeId();

    BaseStationApp();
    virtual ~BaseStationApp();

    // Configuration
    void SetNodeId(uint32_t id);
    void SetNetDevice(ns3::Ptr<ns3::NetDevice> dev);

    // Set node containers for topology info
    void SetSensorNodes(const ns3::NodeContainer& nodes) { m_sensorNodes = nodes; }
    void SetUavNode(const ns3::NodeContainer& node) { m_uavNode = node; }

    // Broadcast topology (node positions) to UAV
    void BroadcastTopology();

    // Handle ACKs and other incoming application packets from UAV.
    bool OnMessageReceived(ns3::Ptr<ns3::NetDevice> dev,
                           ns3::Ptr<const ns3::Packet> pkt,
                           uint16_t proto,
                           const ns3::Address& from);

private:
    void SendOneTopologyPacket(std::vector<uint8_t> buf, uint32_t pktIdx,
                               uint32_t numPackets);

    void StartApplication() override;
    void StopApplication() override;

    uint32_t m_nodeId;
    ns3::Ptr<ns3::NetDevice> m_device;
    ns3::NodeContainer m_sensorNodes;
    ns3::NodeContainer m_uavNode;
};

}  // namespace ns3::wsn::uav

#endif  // BASESTATION_APP_H
