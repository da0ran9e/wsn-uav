#ifndef BASESTATION_APP_H
#define BASESTATION_APP_H

#include "ns3/application.h"
#include "ns3/net-device.h"
#include "ns3/ptr.h"

namespace ns3::wsn::uav {

class BaseStationApp : public Application {
public:
    static TypeId GetTypeId();

    BaseStationApp();
    virtual ~BaseStationApp();

    // Configuration
    void SetNodeId(uint32_t id);
    void SetNetDevice(ns3::Ptr<ns3::NetDevice> dev);

private:
    void StartApplication() override;
    void StopApplication() override;

    uint32_t m_nodeId;
    ns3::Ptr<ns3::NetDevice> m_device;
};

}  // namespace ns3::wsn::uav

#endif  // BASESTATION_APP_H
