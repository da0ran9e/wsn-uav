#ifndef UAV_SAR_BS_APP_H
#define UAV_SAR_BS_APP_H

// Base station: receives the UAV's small end-of-mission report. That reception
// stamps the primary metric (timeToReportAtBS) and ends the run. Fleet schemes
// with independent per-UAV missions (tsp-mc bands) only complete when EVERY
// UAV has reported — the BS counts distinct reporters by radio address.

#include "ns3/application.h"
#include "ns3/net-device.h"
#include "ns3/ptr.h"
#include "ns3/address.h"

#include <cstdint>
#include <set>

namespace ns3::uavsar {

class SarMetrics;

class SarBsApp : public ns3::Application {
public:
    static ns3::TypeId GetTypeId();
    SarBsApp() = default;
    ~SarBsApp() override = default;

    void SetNodeId(uint32_t id) { m_nodeId = id; }
    void SetMetrics(SarMetrics* m) { m_metrics = m; }
    // Mission needs this many DISTINCT reporting UAVs to complete (default 1:
    // proposed/summoned schemes close on the first report).
    void SetExpectedReports(uint32_t n) { m_expected = n; }

    bool OnReceive(ns3::Ptr<ns3::NetDevice> dev, ns3::Ptr<const ns3::Packet> pkt,
                   uint16_t proto, const ns3::Address& from);

private:
    void StartApplication() override {}
    void StopApplication() override {}
    uint32_t m_nodeId = 0;
    SarMetrics* m_metrics = nullptr;
    uint32_t m_expected = 1;
    bool m_reported = false;
    std::set<ns3::Address> m_reporters;
};

}  // namespace ns3::uavsar

#endif  // UAV_SAR_BS_APP_H
