#ifndef WSN_UAV_SAR_GROUND_APP_H
#define WSN_UAV_SAR_GROUND_APP_H

// SAR ground sensor node. Accumulates search-data fragment chunks broadcast by
// UAVs and tracks dataset completeness. The TARGET node (nearest the victim),
// on receiving a recognition fragment, simulates a clue, corroborates it with
// neighbours, then emits an emergency beacon to summon a DATA UAV. Completeness
// of the full dataset stamps the primary metric (time-to-complete-data).
// Detection/CV is NOT simulated — only the networking decisions.

#include "../common/sar-types.h"

#include "ns3/application.h"
#include "ns3/net-device.h"
#include "ns3/ptr.h"
#include "ns3/event-id.h"
#include "ns3/address.h"

#include <cstdint>
#include <map>
#include <set>

namespace ns3::wsn::uav {

class SarMetrics;

class SarGroundApp : public ns3::Application {
public:
    static ns3::TypeId GetTypeId();
    SarGroundApp();
    ~SarGroundApp() override;

    void SetNodeId(uint32_t id) { m_nodeId = id; }
    void SetNetDevice(ns3::Ptr<ns3::NetDevice> dev) { m_device = dev; }
    void SetIsTarget(bool t) { m_isTarget = t; }
    void SetExpectedFragments(uint32_t k) { m_expectedFrags = k; }
    void SetScheme(sar::Scheme s) { m_scheme = s; }
    void SetMetrics(SarMetrics* m) { m_metrics = m; }
    void SetConfirmPolicy(uint32_t neighbors, double timeout, uint32_t beaconQuota) {
        m_confirmNeighbors = neighbors; m_confirmTimeout = timeout; m_beaconQuota = beaconQuota;
    }

    bool OnReceive(ns3::Ptr<ns3::NetDevice> dev, ns3::Ptr<const ns3::Packet> pkt,
                   uint16_t proto, const ns3::Address& from);

private:
    void StartApplication() override;
    void StopApplication() override;

    void Detect();                 // target: clue found
    void RequestConfirmation();
    void ConfirmTimeout();
    void Confirmed();
    void BeaconLoop();
    void CheckComplete();

    uint32_t m_nodeId = 0;
    ns3::Ptr<ns3::NetDevice> m_device;
    bool m_isTarget = false;
    uint32_t m_expectedFrags = 0;
    sar::Scheme m_scheme = sar::Scheme::PROPOSED;
    SarMetrics* m_metrics = nullptr;

    uint32_t m_confirmNeighbors = 1;
    double m_confirmTimeout = 0.5;
    uint32_t m_beaconQuota = 3;

    // fragment accumulation: fragId -> set of received chunk seqs; + total
    std::map<uint16_t, std::set<uint16_t>> m_chunks;
    std::map<uint16_t, uint16_t> m_fragTotal;
    std::set<uint16_t> m_completeFrags;

    // target state machine
    bool m_detected = false;
    bool m_confirmed = false;
    bool m_completed = false;
    uint32_t m_confirmAcks = 0;
    uint32_t m_beaconsSent = 0;
    uint16_t m_evtId = 1;

    ns3::EventId m_confirmTimer;
    ns3::EventId m_beaconEvent;
};

}  // namespace ns3::wsn::uav

#endif  // WSN_UAV_SAR_GROUND_APP_H
