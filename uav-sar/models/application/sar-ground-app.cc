#include "sar-ground-app.h"
#include "region-coordinator.h"
#include "../common/sar-metrics.h"
#include "../common/sar-types.h"
#include "../common/sar-params.h"

#include "ns3/core-module.h"
#include "ns3/packet.h"
#include "ns3/mac16-address.h"
#include "ns3/mobility-model.h"

#include <algorithm>
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
SarGroundApp::SarGroundApp() : m_rng(CreateObject<UniformRandomVariable>()) {}
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

void SarGroundApp::DeliverEvidence(uint16_t orig, double ev) {
    // Cell Leader is the sink: aggregate locally (its own sensing, or a report
    // that already reached it over the radio). Members send an RPT up the tree.
    if (m_isCellLeader) {
        LeaderIngest(orig, ev);   // our own sensing feeds the cell aggregate
        return;
    }
    uint8_t evQ8 = (uint8_t)std::min(255.0, ev * 255.0);
    SendRpt(orig, evQ8, m_treeParent, (uint8_t)params::kRptTtl);
}

void SarGroundApp::LeaderIngest(uint16_t orig, double ev) {
    // Cell Leader aggregates its cell's evidence (union over members). The first
    // time the cell corroborates (>= coop) it floods a SHARE so adjacent cell
    // leaders learn of it over the real radio and the region can merge across.
    double& e = m_cellEvidence[orig];
    if (ev > e) e = ev;
    if (!m_sharedFlooded) {
        double u = 0.0;
        for (auto& [n, v] : m_cellEvidence) u = 1.0 - (1.0 - u) * (1.0 - v);
        if (u >= m_coop) FloodShare();
    }
    if (m_coord) m_coord->ReportClue(orig, ev, Simulator::Now().GetSeconds());
}

void SarGroundApp::FloodShare() {
    m_sharedFlooded = true;
    double u = 0.0;
    for (auto& [n, v] : m_cellEvidence) u = 1.0 - (1.0 - u) * (1.0 - v);
    uint8_t evQ8 = (uint8_t)std::min(255.0, u * 255.0);
    SendShare(m_cellId, evQ8, (int16_t)(m_cellCx * 10), (int16_t)(m_cellCy * 10),
              (uint8_t)params::kShareTtl);
}

void SarGroundApp::SendShare(int32_t cell, uint8_t evQ8, int16_t cx, int16_t cy, uint8_t ttl) {
    if (!m_dev) return;
    std::vector<uint8_t> b(kShareLen);
    uint8_t* q = b.data();
    *q++ = (uint8_t)Msg::SHARE;
    uint16_t c = (uint16_t)cell; std::memcpy(q, &c, 2); q += 2;
    *q++ = evQ8;
    std::memcpy(q, &cx, 2); q += 2;
    std::memcpy(q, &cy, 2); q += 2;
    *q++ = ttl;
    m_dev->Send(Create<Packet>(b.data(), b.size()), Mac16Address("ff:ff"), 0);
    if (m_metrics) { m_metrics->AddSent(); m_metrics->AddSentBytes(b.size()); }
}

void SarGroundApp::SendRpt(uint16_t orig, uint8_t evQ8, int32_t nextHop, uint8_t ttl) {
    if (!m_dev || nextHop < 0) return;   // no route up (isolated / no parent)
    std::vector<uint8_t> b(kRptLen);
    uint8_t* q = b.data();
    *q++ = (uint8_t)Msg::RPT;
    uint16_t nh = (uint16_t)nextHop; std::memcpy(q, &nh, 2); q += 2;
    std::memcpy(q, &orig, 2); q += 2;
    *q++ = evQ8;
    *q++ = ttl;
    m_dev->Send(Create<Packet>(b.data(), b.size()), Mac16Address("ff:ff"), 0);
    if (m_metrics) { m_metrics->AddSent(); m_metrics->AddSentBytes(b.size()); }
}

bool SarGroundApp::OnReceive(Ptr<NetDevice>, Ptr<const Packet> pkt, uint16_t, const Address&) {
    uint32_t sz = pkt->GetSize();
    if (sz < 2) return true;
    std::vector<uint8_t> b(sz);
    pkt->CopyData(b.data(), sz);
    uint8_t type = b[0];

    if (type == (uint8_t)Msg::CONFIRM) {
        // someone confirmed the delivery -> every beaconing CL goes quiet
        Simulator::Cancel(m_beaconEvent);
        return true;
    }
    if (type == (uint8_t)Msg::RPT && sz >= kRptLen) {
        uint16_t nextHop, orig;
        std::memcpy(&nextHop, &b[1], 2);
        std::memcpy(&orig, &b[3], 2);
        uint8_t evQ8 = b[5], ttl = b[6];
        if (nextHop != (uint16_t)m_nodeId) return true;      // not my hop
        if (m_metrics) { m_metrics->AddRecv(); m_metrics->AddRecvBytes(sz); }
        auto sit = m_rptSeen.find(orig);
        if (sit != m_rptSeen.end() && sit->second >= evQ8) return true;  // stale/dup
        m_rptSeen[orig] = evQ8;
        double ev = evQ8 / 255.0;
        if (m_isCellLeader) {
            // the report reached its Cell Leader over the real radio.
            LeaderIngest(orig, ev);
        } else if (ttl > 0) {
            // forward one hop further up the tree, after a small MAC-desync jitter.
            Simulator::Schedule(Seconds(m_rng->GetValue(0.0, params::kFwdStaggerMaxS)),
                                &SarGroundApp::SendRpt, this, orig, evQ8,
                                m_treeParent, (uint8_t)(ttl - 1));
        }
        return true;
    }
    if (type == (uint8_t)Msg::SHARE && sz >= kShareLen) {
        uint16_t origCell; std::memcpy(&origCell, &b[1], 2);
        uint8_t evQ8 = b[3];
        int16_t cx, cy; std::memcpy(&cx, &b[4], 2); std::memcpy(&cy, &b[6], 2);
        uint8_t ttl = b[8];
        if (m_metrics) { m_metrics->AddRecv(); m_metrics->AddRecvBytes(sz); }
        auto sit = m_shareSeen.find(origCell);
        if (sit != m_shareSeen.end() && sit->second >= evQ8) return true;  // dup/stale
        m_shareSeen[origCell] = evQ8;
        // a Cell Leader hearing ANOTHER cell's SHARE = the cross-cell link was
        // carried by the real radio; register the edge for region growth.
        if (m_isCellLeader && (int32_t)origCell != m_cellId && m_coord)
            m_coord->RecordShare((int32_t)origCell, m_cellId);
        if (ttl > 0)
            Simulator::Schedule(Seconds(m_rng->GetValue(0.0, params::kFwdStaggerMaxS)),
                                &SarGroundApp::SendShare, this, (int32_t)origCell, evQ8,
                                cx, cy, (uint8_t)(ttl - 1));
        return true;
    }
    if ((type == (uint8_t)Msg::CUE || type == (uint8_t)Msg::FULL) && sz >= kChunkHdr) {
        uint16_t fragId, seq, total;
        std::memcpy(&fragId, &b[2], 2);
        std::memcpy(&seq, &b[4], 2);
        std::memcpy(&total, &b[6], 2);
        if (m_metrics) { m_metrics->AddRecv(); m_metrics->AddRecvBytes(sz); }
        // viz: first cue ever heard by this node — the dissemination front.
        if (type == (uint8_t)Msg::CUE && !m_heardCue && m_metrics) {
            m_heardCue = true;
            Vector p = GetNode()->GetObject<MobilityModel>()->GetPosition();
            m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "node",
                             "cue_rx", "", p.x, p.y, p.z);
        }

        bool wasComplete = m_have.count(fragId) > 0;
        m_chunks[fragId].insert(seq);
        m_totals[fragId] = total;
        if (!wasComplete && m_chunks[fragId].size() >= total) {
            m_have.insert(fragId);

            // New fragment possessed -> evidence may have grown; report it to the
            // Cell Leader. This now crosses the REAL radio (RPT, forwarded up the
            // cell tree, subject to the G2G channel) unless we ARE the leader.
            if (m_coord) {
                double eff = PossessedConfidence() * m_clueQuality;
                if (eff >= m_coop)
                    DeliverEvidence((uint16_t)m_nodeId, eff);
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
