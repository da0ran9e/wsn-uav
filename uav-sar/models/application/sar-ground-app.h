#ifndef UAV_SAR_GROUND_APP_H
#define UAV_SAR_GROUND_APP_H

// Ground sensor node (v2 after logic review).
//   - Fragments arrive as byte-honest chunks over CUE (FAST) or FULL (DATA);
//     both paths fill the SAME per-fragment chunk set, so a fragment counts
//     exactly once however it arrived (fixes F1 double-counting).
//   - A fragment is possessed when all its chunks are held. Node evidence =
//     Confidence(possessed) * clueQuality, reported to the coordinator.
//   - CONFIRM fires only when the node possesses the ENTIRE dataset (every
//     fragment id complete) — the literal "toàn bộ dữ liệu" endpoint — and is
//     retransmitted a bounded number of times (fixes F2 single-shot loss).
//   - The region leader's SUMMON carries its OWN position, so the DATA UAV
//     delivers directly overhead (reliable point-blank link).

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
    void SetCoopThreshold(double coop) { m_coop = coop; }
    void SetIsTarget(bool t) { m_isTarget = t; }
    void SetStopOnComplete(bool s) { m_stopOnComplete = s; }
    // Designated by the region ticket: the strongest-evidence node; it alone
    // confirms the delivery (its footage is what the data is checked against).
    void SetVerifier(bool v) { m_isVerifier = v; }

    // Called on the region leader; (cx,cy) = the verifier's position, embedded
    // in the SUMMON so the DATA UAV delivers directly over the verifier.
    void StartSummon(uint16_t regionId, double cx, double cy);

    bool OnReceive(ns3::Ptr<ns3::NetDevice> dev, ns3::Ptr<const ns3::Packet> pkt,
                   uint16_t proto, const ns3::Address& from);

private:
    void StartApplication() override;
    void StopApplication() override;
    void BeaconTick();
    void SendConfirm();                 // retried kConfirmRetries times
    double PossessedConfidence() const;
    bool HasEntireDataset() const;

    uint32_t m_nodeId = 0;
    ns3::Ptr<ns3::NetDevice> m_dev;
    SarMetrics* m_metrics = nullptr;
    RegionCoordinator* m_coord = nullptr;

    std::map<uint16_t, Fragment> m_byId;                 // full profile (briefing)
    std::map<uint16_t, std::set<uint16_t>> m_chunks;     // fragId -> received seqs
    std::map<uint16_t, uint16_t> m_totals;               // fragId -> total chunks
    std::set<uint16_t> m_have;                           // complete fragment ids
    double m_clueQuality = 0.0;
    double m_coop = 0.30;

    bool m_isLeader = false;
    bool m_isTarget = false;
    bool m_isVerifier = false;
    bool m_stopOnComplete = false;
    bool m_confirmed = false;
    uint16_t m_regionId = 0;
    double m_cx = 0, m_cy = 0;   // beacon coords = verifier position
    uint32_t m_beacons = 0;
    uint32_t m_confirmsSent = 0;
    ns3::EventId m_beaconEvent;
    ns3::EventId m_confirmEvent;
};

}  // namespace ns3::uavsar

#endif  // UAV_SAR_GROUND_APP_H
