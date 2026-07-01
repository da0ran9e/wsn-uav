#ifndef BASESTATION_APP_H
#define BASESTATION_APP_H

#include "../common/semantic-fragment.h"

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

    // Send the semantic fragment profile (metadata + data volume) to the UAV.
    // Scheduled automatically after the topology dispatch completes.
    void DispatchFragmentData();

    // Handle ACKs and other incoming application packets from UAV.
    bool OnMessageReceived(ns3::Ptr<ns3::NetDevice> dev,
                           ns3::Ptr<const ns3::Packet> pkt,
                           uint16_t proto,
                           const ns3::Address& from);

private:
    void SendOneTopologyPacket(uint32_t pktIdx, bool retransmission);
    void ScheduleTopologyRetransmissionPass();
    void SendOneDataPacket(uint32_t pktIdx, bool retransmission);
    void ScheduleDataRetransmissionPass();

    void StartApplication() override;
    void StopApplication() override;

    uint32_t m_nodeId;
    ns3::Ptr<ns3::NetDevice> m_device;
    ns3::NodeContainer m_sensorNodes;
    ns3::NodeContainer m_uavNode;
    TargetProfile m_profile;  // semantic fragment package, built at startup

    std::vector<std::vector<uint8_t>> m_topologyPackets;
    bool m_topologyTransferComplete = false;

    struct DataPacketRecord {
        std::vector<uint8_t> buf;
        uint16_t fragId = 0;
        uint32_t chunkOffset = 0;
        bool acked = false;
    };
    std::vector<DataPacketRecord> m_dataPackets;
    bool m_dataTransferComplete = false;
};

}  // namespace ns3::wsn::uav

#endif  // BASESTATION_APP_H
