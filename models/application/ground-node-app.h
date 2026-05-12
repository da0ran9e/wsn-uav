#ifndef GROUND_NODE_APP_H
#define GROUND_NODE_APP_H

#include "ns3/application.h"
#include "ns3/net-device.h"
#include "ns3/ptr.h"
#include "ns3/event-id.h"

namespace ns3::wsn::uav {

class GroundNodeApp : public Application {
public:
    static TypeId GetTypeId();

    GroundNodeApp();
    virtual ~GroundNodeApp();

    // Configuration
    void SetNodeId(uint32_t id);
    void SetNetDevice(ns3::Ptr<ns3::NetDevice> dev);

    // Broadcast beacon
    void SendBeacon();

private:
    void StartApplication() override;
    void StopApplication() override;

    // Callback for packet reception
    bool OnReceive(ns3::Ptr<ns3::NetDevice> dev,
                   ns3::Ptr<const ns3::Packet> pkt,
                   uint16_t proto,
                   const ns3::Address& from);

    uint32_t m_nodeId;
    ns3::Ptr<ns3::NetDevice> m_device;
};

}  // namespace ns3::wsn::uav

#endif  // GROUND_NODE_APP_H
