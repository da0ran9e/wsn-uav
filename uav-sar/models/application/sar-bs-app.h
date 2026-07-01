#ifndef UAV_SAR_BS_APP_H
#define UAV_SAR_BS_APP_H

// Base station: receives the UAV's small end-of-mission report. That reception
// stamps the primary metric (timeToReportAtBS) and ends the run.

#include "ns3/application.h"
#include "ns3/net-device.h"
#include "ns3/ptr.h"
#include "ns3/address.h"

#include <cstdint>

namespace ns3::uavsar {

class SarMetrics;

class SarBsApp : public ns3::Application {
public:
    static ns3::TypeId GetTypeId();
    SarBsApp() = default;
    ~SarBsApp() override = default;

    void SetNodeId(uint32_t id) { m_nodeId = id; }
    void SetMetrics(SarMetrics* m) { m_metrics = m; }

    bool OnReceive(ns3::Ptr<ns3::NetDevice> dev, ns3::Ptr<const ns3::Packet> pkt,
                   uint16_t proto, const ns3::Address& from);

private:
    void StartApplication() override {}
    void StopApplication() override {}
    uint32_t m_nodeId = 0;
    SarMetrics* m_metrics = nullptr;
    bool m_reported = false;
};

}  // namespace ns3::uavsar

#endif  // UAV_SAR_BS_APP_H
