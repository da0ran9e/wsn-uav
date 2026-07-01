#ifndef UAV_SAR_GROUND_APP_H
#define UAV_SAR_GROUND_APP_H

// Ground sensor node. Receives identity cues from FAST UAVs, corroborates them
// with its local clue quality, and reports soft evidence to the region
// coordinator (its cell leader). If elected region leader it broadcasts the
// single SUMMON. Receives the full dataset from the DATA UAV and, once its
// confidence reaches the confirm threshold, broadcasts CONFIRM.

#include "../common/target-profile.h"

#include "ns3/application.h"
#include "ns3/net-device.h"
#include "ns3/event-id.h"
#include "ns3/ptr.h"
#include "ns3/address.h"

#include <cstdint>
#include <map>
#include <set>
#include <vector>

namespace ns3::uavsar {

class SarMetrics;
class RegionCoordinator;

class SarGroundApp : public ns3::Application {
public:
    static ns3::TypeId GetTypeId();
    SarGroundApp();
    ~SarGroundApp() override;

    void SetNodeId(uint32_t id) { m_nodeId = id; }
    void SetDevice(ns3::Ptr<ns3::NetDevice> d) { m_dev = d; }
    void SetMetrics(SarMetrics* m) { m_metrics = m; }
    void SetCoordinator(RegionCoordinator* c) { m_coord = c; }
    void SetProfile(const std::vector<Fragment>& frags);
    void SetClueQuality(double q) { m_clueQuality = q; }
    void SetThresholds(double coop, double confirm) { m_coop = coop; m_confirm = confirm; }

    // Called by the coordinator when this node is elected region leader.
    void StartSummon(uint16_t regionId, double cx, double cy);

    bool OnReceive(ns3::Ptr<ns3::NetDevice> dev, ns3::Ptr<const ns3::Packet> pkt,
                   uint16_t proto, const ns3::Address& from);

private:
    void StartApplication() override;
    void StopApplication() override;
    void BeaconTick();
    double ReceivedConfidence() const;

    uint32_t m_nodeId = 0;
    ns3::Ptr<ns3::NetDevice> m_dev;
    SarMetrics* m_metrics = nullptr;
    RegionCoordinator* m_coord = nullptr;

    std::map<uint16_t, Fragment> m_byId;      // fragId -> fragment (utilities)
    std::set<uint16_t> m_haveCue;             // cue frags received
    std::map<uint16_t, std::set<uint16_t>> m_fullChunks;  // fragId -> seqs
    std::set<uint16_t> m_haveFull;            // full frags completed
    double m_clueQuality = 0.0;
    double m_coop = 0.30;
    double m_confirm = 0.95;

    // region-leader summon state
    bool m_isLeader = false;
    bool m_confirmed = false;
    uint16_t m_regionId = 0;
    double m_cx = 0, m_cy = 0;
    uint32_t m_beacons = 0;
    ns3::EventId m_beaconEvent;
};

}  // namespace ns3::uavsar

#endif  // UAV_SAR_GROUND_APP_H
