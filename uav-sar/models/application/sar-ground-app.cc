#include "sar-ground-app.h"
#include "region-coordinator.h"
#include "../common/sar-metrics.h"
#include "../common/sar-types.h"
#include "../common/sar-params.h"

#include "ns3/core-module.h"
#include "ns3/packet.h"
#include "ns3/mac16-address.h"
#include "ns3/mobility-model.h"

#include <cstring>
#include <vector>

using namespace ns3;

namespace ns3::uavsar {

NS_OBJECT_ENSURE_REGISTERED(SarGroundApp);

TypeId SarGroundApp::GetTypeId() {
    static TypeId tid = TypeId("ns3::uavsar::SarGroundApp")
                            .SetParent<Application>()
                            .SetGroupName("uav-sar")
                            .AddConstructor<SarGroundApp>();
    return tid;
}
SarGroundApp::SarGroundApp() = default;
SarGroundApp::~SarGroundApp() = default;

void SarGroundApp::SetProfile(const std::vector<Fragment>& frags) {
    for (const auto& f : frags) m_byId[(uint16_t)f.id] = f;
}

void SarGroundApp::StartApplication() {}
void SarGroundApp::StopApplication() { Simulator::Cancel(m_beaconEvent); }

double SarGroundApp::ReceivedConfidence() const {
    std::vector<Fragment> got;
    for (uint16_t id : m_haveCue)  { auto it = m_byId.find(id); if (it != m_byId.end()) got.push_back(it->second); }
    for (uint16_t id : m_haveFull) { auto it = m_byId.find(id); if (it != m_byId.end()) got.push_back(it->second); }
    return TargetProfile::Confidence(got);
}

void SarGroundApp::StartSummon(uint16_t regionId, double cx, double cy) {
    m_isLeader = true;
    m_regionId = regionId;
    m_cx = cx; m_cy = cy;
    if (m_metrics) {
        Vector p = GetNode()->GetObject<MobilityModel>()->GetPosition();
        m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "CL",
                         "summon_start", "region leader", p.x, p.y, p.z);
    }
    BeaconTick();
}

void SarGroundApp::BeaconTick() {
    if (m_confirmed || m_beacons >= params::kBeaconQuota) return;
    if (m_dev) {
        std::vector<uint8_t> b(kSummonLen);
        uint8_t* p = b.data();
        *p++ = (uint8_t)Msg::SUMMON;
        *p++ = kBroadcast;
        std::memcpy(p, &m_regionId, 2); p += 2;
        int16_t cx = (int16_t)(m_cx * 10), cy = (int16_t)(m_cy * 10);
        std::memcpy(p, &cx, 2); p += 2;
        std::memcpy(p, &cy, 2); p += 2;
        m_dev->Send(Create<Packet>(b.data(), b.size()), Mac16Address("ff:ff"), 0);
        if (m_metrics) { m_metrics->AddBeacon(); m_metrics->AddSent(); }
    }
    m_beacons++;
    m_beaconEvent = Simulator::Schedule(Seconds(params::kBeaconIntervalS),
                                        &SarGroundApp::BeaconTick, this);
}

bool SarGroundApp::OnReceive(Ptr<NetDevice>, Ptr<const Packet> pkt, uint16_t, const Address&) {
    uint32_t sz = pkt->GetSize();
    if (sz < 2) return true;
    std::vector<uint8_t> b(sz);
    pkt->CopyData(b.data(), sz);
    uint8_t type = b[0];

    if (type == (uint8_t)Msg::CUE && sz >= kCueLen) {
        uint16_t fragId; std::memcpy(&fragId, &b[2], 2);
        m_haveCue.insert(fragId);
        if (m_metrics) m_metrics->AddRecv();
        // corroborate cue confidence with local clue quality, report to CL.
        double cueConf = ReceivedConfidence();  // cue-only so far
        double eff = cueConf * m_clueQuality;
        if (m_coord && eff >= m_coop)
            m_coord->ReportClue(m_nodeId, eff, Simulator::Now().GetSeconds());
    } else if (type == (uint8_t)Msg::FULL && sz >= kFullHdr) {
        uint16_t fragId, seq, total;
        std::memcpy(&fragId, &b[2], 2);
        std::memcpy(&seq, &b[4], 2);
        std::memcpy(&total, &b[6], 2);
        m_fullChunks[fragId].insert(seq);
        if (m_metrics) m_metrics->AddRecv();
        if (m_fullChunks[fragId].size() >= total) m_haveFull.insert(fragId);
        // Region leader (proposed) or the victim node (baseline) closes the loop.
        if ((m_isLeader || m_isTarget) && !m_confirmed && ReceivedConfidence() >= m_confirm) {
            m_confirmed = true;
            Simulator::Cancel(m_beaconEvent);
            Vector p = GetNode()->GetObject<MobilityModel>()->GetPosition();
            if (m_metrics) {
                m_metrics->MarkCompleteData(Simulator::Now().GetSeconds());
                m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId,
                                 m_isLeader ? "CL" : "target",
                                 "confirm", "full data received", p.x, p.y, p.z);
            }
            // Proposed: broadcast CONFIRM so the DATA UAV returns and reports.
            if (m_isLeader && m_dev) {
                std::vector<uint8_t> c(kConfirmLen);
                uint8_t* q = c.data();
                *q++ = (uint8_t)Msg::CONFIRM; *q++ = kBroadcast;
                std::memcpy(q, &m_regionId, 2); q += 2;
                *q++ = (uint8_t)(m_nodeId & 0xFF);
                m_dev->Send(Create<Packet>(c.data(), c.size()), Mac16Address("ff:ff"), 0);
                if (m_metrics) m_metrics->AddSent();
            }
            // Baselines have no report loop: end the run on complete.
            if (m_stopOnComplete) Simulator::Stop(Seconds(0.5));
        }
    }
    return true;
}

}  // namespace ns3::uavsar
