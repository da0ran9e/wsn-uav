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
void SarGroundApp::StopApplication() {
    Simulator::Cancel(m_beaconEvent);
    Simulator::Cancel(m_confirmEvent);
}

double SarGroundApp::PossessedConfidence() const {
    std::vector<Fragment> got;
    got.reserve(m_have.size());
    for (uint16_t id : m_have) {
        auto it = m_byId.find(id);
        if (it != m_byId.end()) got.push_back(it->second);
    }
    return TargetProfile::Confidence(got);
}

bool SarGroundApp::HasEntireDataset() const {
    return !m_byId.empty() && m_have.size() >= m_byId.size();
}

void SarGroundApp::StartSummon(uint16_t regionId, double cx, double cy) {
    m_isLeader = true;
    m_regionId = regionId;
    m_cx = cx;
    m_cy = cy;
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
        // SUMMON carries the VERIFIER's position: the DATA UAV delivers
        // directly over the node that must check the data (reliable link).
        std::vector<uint8_t> b(kSummonLen);
        uint8_t* q = b.data();
        *q++ = (uint8_t)Msg::SUMMON;
        *q++ = kBroadcast;
        std::memcpy(q, &m_regionId, 2); q += 2;
        int16_t cx = (int16_t)(m_cx * 10), cy = (int16_t)(m_cy * 10);
        std::memcpy(q, &cx, 2); q += 2;
        std::memcpy(q, &cy, 2); q += 2;
        m_dev->Send(Create<Packet>(b.data(), b.size()), Mac16Address("ff:ff"), 0);
        if (m_metrics) {
            m_metrics->AddBeacon();
            m_metrics->AddSent();
            m_metrics->AddSentBytes(b.size());
        }
    }
    m_beacons++;
    m_beaconEvent = Simulator::Schedule(Seconds(params::kBeaconIntervalS),
                                        &SarGroundApp::BeaconTick, this);
}

void SarGroundApp::SendConfirm() {
    if (m_confirmsSent >= params::kConfirmRetries) return;
    if (m_dev) {
        std::vector<uint8_t> c(kConfirmLen);
        uint8_t* q = c.data();
        *q++ = (uint8_t)Msg::CONFIRM;
        *q++ = kBroadcast;
        std::memcpy(q, &m_regionId, 2); q += 2;
        *q++ = (uint8_t)(m_nodeId & 0xFF);
        m_dev->Send(Create<Packet>(c.data(), c.size()), Mac16Address("ff:ff"), 0);
        if (m_metrics) { m_metrics->AddSent(); m_metrics->AddSentBytes(c.size()); }
    }
    m_confirmsSent++;
    m_confirmEvent = Simulator::Schedule(Seconds(params::kConfirmRetryS),
                                         &SarGroundApp::SendConfirm, this);
}

bool SarGroundApp::OnReceive(Ptr<NetDevice>, Ptr<const Packet> pkt, uint16_t, const Address&) {
    uint32_t sz = pkt->GetSize();
    if (sz < 2) return true;
    std::vector<uint8_t> b(sz);
    pkt->CopyData(b.data(), sz);
    uint8_t type = b[0];

    if ((type == (uint8_t)Msg::CUE || type == (uint8_t)Msg::FULL) && sz >= kChunkHdr) {
        uint16_t fragId, seq, total;
        std::memcpy(&fragId, &b[2], 2);
        std::memcpy(&seq, &b[4], 2);
        std::memcpy(&total, &b[6], 2);
        if (m_metrics) { m_metrics->AddRecv(); m_metrics->AddRecvBytes(sz); }

        bool wasComplete = m_have.count(fragId) > 0;
        m_chunks[fragId].insert(seq);
        m_totals[fragId] = total;
        if (!wasComplete && m_chunks[fragId].size() >= total) {
            m_have.insert(fragId);

            // New fragment possessed -> evidence may have grown; report to CL.
            if (m_coord) {
                double eff = PossessedConfidence() * m_clueQuality;
                if (eff >= m_coop)
                    m_coord->ReportClue(m_nodeId, eff, Simulator::Now().GetSeconds());
            }

            // Loop closure on holding the ENTIRE dataset (every fragment id).
            //  - metric timeToCompleteData = the VICTIM's node (ground truth).
            //  - control-plane CONFIRM = the designated VERIFIER only (the
            //    strongest-evidence node the summon ticket named); its footage
            //    is what the data is checked against, so the DATA UAV must not
            //    stop before IT has everything. Retried against packet loss.
            if (!m_confirmed && HasEntireDataset()) {
                m_confirmed = true;
                Simulator::Cancel(m_beaconEvent);
                Vector p = GetNode()->GetObject<MobilityModel>()->GetPosition();
                if (m_metrics && (m_isTarget || m_isVerifier)) {
                    if (m_isTarget) m_metrics->MarkCompleteData(Simulator::Now().GetSeconds());
                    m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId,
                                     m_isVerifier ? "verifier" : "target", "confirm",
                                     "entire dataset received", p.x, p.y, p.z);
                }
                if (m_coord && m_isVerifier) SendConfirm();  // retried broadcast
                if (m_stopOnComplete && m_isTarget) Simulator::Stop(Seconds(0.5));
            }
        }
    }
    return true;
}

}  // namespace ns3::uavsar
