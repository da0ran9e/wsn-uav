#include "sar-ground-app.h"
#include "../common/sar-metrics.h"
#include "../common/sar-types.h"
#include "../common/sar-params.h"

#include "ns3/core-module.h"
#include "ns3/packet.h"
#include "ns3/mac16-address.h"
#include "ns3/mobility-model.h"

#include <algorithm>
#include <cstdio>
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
    Simulator::Cancel(m_electEvent);
    Simulator::Cancel(m_rptRepeatEvent);
    Simulator::Cancel(m_echoEvent);
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
    if (m_byId.empty()) return false;
    if (m_codedRecovery) {
        // Rateless: any ~1.05x file-worth of symbols reconstructs the file, so
        // duplicates are useful. Count total received chunks against the coded
        // overhead threshold rather than requiring every distinct index.
        uint32_t need = 0;
        for (const auto& [id, f] : m_byId)
            need += std::max(1u, (f.sizeBytes + kChunkBytes - 1) / kChunkBytes);
        return m_chunksRx >= (uint32_t)(1.05 * need);
    }
    return m_have.size() >= m_byId.size();
}

double SarGroundApp::PossessedFraction() const {
    if (m_byId.empty()) return 0.0;
    double have = 0, total = 0;
    for (const auto& [id, f] : m_byId) {
        total += f.sizeBytes;
        auto it = m_chunks.find(id);
        if (it == m_chunks.end()) continue;
        uint32_t tot = std::max(1u, (f.sizeBytes + kChunkBytes - 1) / kChunkBytes);
        have += std::min(1.0, (double)it->second.size() / tot) * f.sizeBytes;
    }
    return total > 0 ? have / total : 0.0;
}

double SarGroundApp::CellAggregate() const {
    double u = 0.0;
    for (auto& [n, ne] : m_cellEvidence) u = 1.0 - (1.0 - u) * (1.0 - ne.ev);
    return u;
}

// ---- report path: my own evidence up to the Cell Leader --------------------

void SarGroundApp::DeliverEvidence(double ev) {
    Vector p = GetNode()->GetObject<MobilityModel>()->GetPosition();
    // audit M9/W3: a node reports the position its GPS believes it is at. The
    // offset is drawn ONCE per node (a receiver's bias is a property of where it
    // sits under the canopy, not of when it happens to transmit) -- redrawing it
    // per report would let the leader average the error away for free.
    double rx = p.x + m_gpsBiasX, ry = p.y + m_gpsBiasY;
    if (m_isCellLeader) {
        LeaderIngest((uint16_t)m_nodeId, ev, rx, ry);   // local sensing
        return;
    }
    uint8_t evQ8 = (uint8_t)std::min(255.0, ev * 255.0);
    SendRpt((uint16_t)m_nodeId, evQ8, (int16_t)(rx * 10), (int16_t)(ry * 10),
            m_treeParent, (uint8_t)params::kRptTtl);
}

void SarGroundApp::SendRpt(uint16_t orig, uint8_t evQ8, int16_t x, int16_t y,
                           int32_t nextHop, uint8_t ttl) {
    if (!m_dev || nextHop < 0) return;   // no route up (isolated / no parent)
    std::vector<uint8_t> b(kRptLen);
    uint8_t* q = b.data();
    *q++ = (uint8_t)Msg::RPT;
    uint16_t nh = (uint16_t)nextHop; std::memcpy(q, &nh, 2); q += 2;
    std::memcpy(q, &orig, 2); q += 2;
    *q++ = evQ8;
    *q++ = ttl;
    std::memcpy(q, &x, 2); q += 2;
    std::memcpy(q, &y, 2); q += 2;
    m_dev->Send(Create<Packet>(b.data(), b.size()), Mac16Address("ff:ff"), 0);
    if (m_metrics) { m_metrics->AddSent(); m_metrics->AddSentBytes(b.size()); }
}

bool SarGroundApp::InAimScope(double x, double y) const {
    // Ground this leader plausibly knows about: within kAimScopeM of its own
    // cell centre. 0 disables the bound (the pre-fix behaviour, kept as the
    // ablation).
    if (m_aimScope <= 0) return true;
    return std::hypot(x - m_cellCx, y - m_cellCy) <= m_aimScope;
}

bool SarGroundApp::ClaimedNearby(double x, double y) const {
    if (m_electScope <= 0) return !m_claimedAims.empty();   // unscoped ablation
    for (const auto& [ax, ay] : m_claimedAims)
        if (std::hypot(ax - x, ay - y) <= m_electScope) return true;
    return false;
}

bool SarGroundApp::BestAim(double& bx, double& by) const {
    // The point this leader would summon to if it elected right now, from the
    // same two sources the elect path uses: its own members' RPTs and each
    // neighbouring cell's peak reporter carried by SHARE.
    //
    // It has to be computable OUTSIDE the elect path, because the stand-down
    // check needs it: a leader deciding whether another cell's claim is "about
    // the same place" must compare aims, not positions. Comparing against its
    // own CELL CENTRE was the bug -- SHARE carries neighbour peaks, so a cell
    // 250 m away can legitimately aim at the same peak, and a centre-based test
    // calls that a different place every time.
    double best = -1;
    for (const auto& [n, ne] : m_cellEvidence)
        if (ne.ev > best && InAimScope(ne.x, ne.y)) { best = ne.ev; bx = ne.x; by = ne.y; }
    for (const auto& [c, nb] : m_neighborEv)
        if (nb.peak > best && InAimScope(nb.x, nb.y)) { best = nb.peak; bx = nb.x; by = nb.y; }
    return best > 0;
}

double SarGroundApp::ClueNow() const {
    // The node judges its own footage against whatever reference it holds. With
    // only cue fragments that is a weak test and a similar-looking object passes
    // it; with the complete dataset the test is sharp. Linear in possession, so
    // there is no hidden threshold effect -- the node never knows which regime
    // it is in, it just reads a better number as more data arrives.
    if (m_clueQualityFull < 0.0) return m_clueQuality;
    // D31: weight by how much of the REFERENCE this node holds, not by the union
    // recognition confidence. The cue fragments are 7% of the dataset; scoring
    // them at 0.926 meant a node was treated as almost fully informed before any
    // full-data chunk arrived, so a confusable object was resolved away at the
    // cue stage and the ambiguity axis measured as a no-op (M=0 and M=4 gave
    // byte-identical runs on 11 of 12 seeds).
    double c = PossessedFraction();
    return m_clueQuality + c * (m_clueQualityFull - m_clueQuality);
}

void SarGroundApp::SendEcho() {
    // audit W4: the closed-loop non-cooperative arm's ENTIRE feedback path. One
    // hop, straight up to whichever UAV happens to be in range -- no tree, no
    // flood, no leader, no election. A node whose evidence rises while no UAV is
    // overhead is simply never heard, which is precisely the failure the
    // cooperative substrate exists to prevent, so this arm isolates the value of
    // that substrate rather than the value of feedback in general.
    if (!m_dev || m_echoesSent >= params::kEchoRepeatMax) return;
    Vector p = GetNode()->GetObject<MobilityModel>()->GetPosition();
    double rx = p.x + m_gpsBiasX, ry = p.y + m_gpsBiasY;   // same GPS error as RPT
    double eff = PossessedConfidence() * ClueNow();
    std::vector<uint8_t> b(kEchoLen);
    uint8_t* q = b.data();
    *q++ = (uint8_t)Msg::ECHO;
    uint16_t orig = (uint16_t)m_nodeId; std::memcpy(q, &orig, 2); q += 2;
    *q++ = (uint8_t)std::min(255.0, eff * 255.0);
    int16_t x = (int16_t)(rx * 10), y = (int16_t)(ry * 10);
    std::memcpy(q, &x, 2); q += 2; std::memcpy(q, &y, 2);
    m_dev->Send(Create<Packet>(b.data(), b.size()), Mac16Address("ff:ff"), 0);
    if (m_metrics) { m_metrics->AddSent(); m_metrics->AddSentBytes(b.size()); }
    m_echoesSent++;
    m_echoEvent = Simulator::Schedule(Seconds(params::kEchoRepeatS),
                                      &SarGroundApp::SendEcho, this);
}

// ---- Cell Leader: aggregate, share, elect ----------------------------------

void SarGroundApp::LeaderIngest(uint16_t orig, double ev, double x, double y) {
    const double aggBefore = CellAggregate();
    NodeEv& ne = m_cellEvidence[orig];
    if (ev > ne.ev) { ne.ev = ev; ne.x = x; ne.y = y; }
    // audit A10: the adaptive window fires on a quiet interval, so "quiet" has to
    // be defined here. Only a MEANINGFUL increase counts — otherwise the long
    // tail of tiny refinements would keep deferring the decision forever.
    if (CellAggregate() - aggBefore > params::kEvidenceGrowEps)
        m_lastGrowthS = Simulator::Now().GetSeconds();
    // A member's report that actually reached the CL over the radio is one real
    // intra-cell cooperative delivery (our own sensing is not a "share").
    if (orig != (uint16_t)m_nodeId && m_metrics) {
        m_metrics->AddIntraShare();
        char det[48]; std::snprintf(det, sizeof det, "ev=%.2f -> CL %u", ev, m_nodeId);
        m_metrics->Event(Simulator::Now().GetSeconds(), orig, "node", "clue_report", det, x, y, 0);
    }
    // Flood (or re-flood) our current cell strength so neighbours can compare —
    // the first flood at coop, then again each time evidence grows notably.
    double agg = CellAggregate();
    if (agg >= m_coop && agg >= m_lastFloodEv + 0.20) FloodShare();
    MaybeElect();
}

void SarGroundApp::FloodShare() {
    m_sharedFlooded = true;
    m_lastFloodEv = CellAggregate();
    uint8_t evQ8 = (uint8_t)std::min(255.0, CellAggregate() * 255.0);
    // audit A5: share the cell's STRONGEST REPORTER position, not the cell
    // centre. Two reasons. (1) The centre is true survey geometry, so a
    // neighbour mixing it with GPS-biased member positions was estimating from
    // partly noise-free data — the centroid ablation was being flattered.
    // (2) audit A4: a neighbour could previously learn only "cell 7 is hot",
    // never "the hot thing in cell 7 is at (x,y)", which capped any aiming rule
    // at one cell's resolution. Fall back to the centre only when this leader
    // has heard from nobody.
    double sx = m_cellCx, sy = m_cellCy, best = 0;
    for (const auto& [n, ne] : m_cellEvidence)
        if (ne.ev > best) { best = ne.ev; sx = ne.x; sy = ne.y; }
    SendShare(m_cellId, evQ8, (uint8_t)std::min(255.0, best * 255.0),
              (int16_t)(sx * 10), (int16_t)(sy * 10), (uint8_t)params::kShareTtl);
}

void SarGroundApp::SendRclaim(int32_t cell, uint8_t evQ8, uint8_t peakQ8,
                              int16_t cx, int16_t cy, uint8_t ttl) {
    if (!m_dev) return;
    std::vector<uint8_t> b(kRclaimLen);
    uint8_t* q = b.data();
    *q++ = (uint8_t)Msg::RCLAIM;
    uint16_t c = (uint16_t)cell; std::memcpy(q, &c, 2); q += 2;
    *q++ = evQ8; *q++ = peakQ8;
    std::memcpy(q, &cx, 2); q += 2;
    std::memcpy(q, &cy, 2); q += 2;
    *q++ = ttl;
    m_dev->Send(Create<Packet>(b.data(), b.size()), Mac16Address("ff:ff"), 0);
    if (m_metrics) { m_metrics->AddSent(); m_metrics->AddSentBytes(b.size()); }
}

void SarGroundApp::SendShare(int32_t cell, uint8_t evQ8, uint8_t peakQ8,
                             int16_t cx, int16_t cy, uint8_t ttl) {
    if (!m_dev) return;
    std::vector<uint8_t> b(kShareLen);
    uint8_t* q = b.data();
    *q++ = (uint8_t)Msg::SHARE;
    uint16_t c = (uint16_t)cell; std::memcpy(q, &c, 2); q += 2;
    *q++ = evQ8; *q++ = peakQ8;
    std::memcpy(q, &cx, 2); q += 2;
    std::memcpy(q, &cy, 2); q += 2;
    *q++ = ttl;
    m_dev->Send(Create<Packet>(b.data(), b.size()), Mac16Address("ff:ff"), 0);
    if (m_metrics) { m_metrics->AddSent(); m_metrics->AddSentBytes(b.size()); }
}

void SarGroundApp::RptRepeatTick() {
    // stop once the region is being handled (SUMMON heard) or the quota is spent.
    if (m_regionFormed || m_rptRepeats >= params::kRptRepeatMax) return;
    m_rptRepeats++;
    DeliverEvidence(m_lastEff);
    m_rptRepeatEvent = Simulator::Schedule(Seconds(params::kRptRepeatS),
                                           &SarGroundApp::RptRepeatTick, this);
}

void SarGroundApp::MaybeElect() {
    if (!m_cooperative || !m_isCellLeader) return;
    if (m_regionFormed) return;
    double agg = CellAggregate();
    if (agg < params::kAlertThreshold) return;
    double now = Simulator::Now().GetSeconds();
    if (m_alertAtS < 0) m_alertAtS = now;

    // Distributed election: stronger cells wait less, so the strongest fires its
    // SUMMON first; every other leader suppresses on hearing it (merge). No
    // central brain, no global view — only what reached us over the radio.
    // audit M4/S5: apply the window first, then the evidence-ordered backoff on
    // top of it, so co-alerted cells do not fire at the identical instant.
    double backoff = params::kElectBackoffS * (1.0 - agg) +
                     m_rng->GetValue(0.0, params::kFwdStaggerMaxS);

    if (!m_adaptiveWindow) {
        if (m_electScheduled) return;               // fixed window: schedule once
        m_electScheduled = true;
        double fireAt = std::max(now, m_minObserveS) + backoff;
        m_electEvent = Simulator::Schedule(Seconds(fireAt - now), &SarGroundApp::Elect, this);
        return;
    }

    // audit A10: adaptive window. Fire once this cell's OWN evidence has stopped
    // growing — the condition the wall-clock window was only a proxy for — with
    // --minObserve kept as a floor and kElectDeadlineS as a ceiling so a cell
    // whose evidence never settles cannot starve. Rescheduling on every growth
    // is what makes it adapt: a big grid keeps feeding the leader for longer and
    // so defers the decision for longer, with no knowledge of the grid at all.
    double quietUntil = m_lastGrowthS + params::kEvidenceStableS;
    double deadline = m_alertAtS + params::kElectDeadlineS;
    double fireAt = std::min(deadline, std::max(quietUntil, m_minObserveS)) + backoff;
    if (m_electScheduled && m_electEvent.IsPending()) {
        // already waiting; only push it out if new evidence justifies that
        if (fireAt <= m_electFireAtS + 1e-9) return;
        Simulator::Cancel(m_electEvent);
    }
    m_electScheduled = true;
    m_electFireAtS = fireAt;
    m_electEvent = Simulator::Schedule(Seconds(std::max(0.0, fireAt - now)),
                                       &SarGroundApp::Elect, this);
}

void SarGroundApp::Elect() {
    if (m_regionFormed) return;                    // someone summoned first
    // Defer to a stronger nearby cell: if a neighbour has SHARE'd higher evidence
    // than ours, let IT summon (its SUMMON will suppress us). Bounded retries so a
    // silent neighbour can't stall us forever. This picks the strongest cell
    // instead of merely the earliest to cross the alert (distributed region window).
    double agg = CellAggregate(), maxNb = 0;
    for (auto& [c, nb] : m_neighborEv) maxNb = std::max(maxNb, nb.ev);
    if (maxNb > agg + 0.05 && m_deferCount < 3) {
        m_deferCount++;
        m_electEvent = Simulator::Schedule(Seconds(params::kElectBackoffS),
                                           &SarGroundApp::Elect, this);
        return;
    }
    // Delivery target = cross-cell interpolation of the evidence peak, built ONLY
    // from what reached this leader over the radio:
    //  - fine grain: my members' RPTs (per-node evidence + self-reported GPS),
    //  - coarse grain: neighbouring cells' SHAREs (cell aggregate + cell centre).
    // Weighting by evidence^2 concentrates on the high-evidence cluster; the
    // neighbour terms pull the estimate toward the true peak when the victim sits
    // near a cell boundary (the diagnosed ~1-cell-hop error mode).
    // Rank every candidate this leader has heard of, strongest first: its own
    // members (evidence + GPS-reported position) and each neighbouring cell's
    // peak reporter. The ranking is what makes a failed delivery recoverable —
    // without it, a wrong first guess was terminal (see kRetargetAfterS).
    m_candidates.clear();
    for (const auto& [n, ne] : m_cellEvidence)
        if (InAimScope(ne.x, ne.y)) m_candidates.push_back({ne.ev, ne.x, ne.y});
    for (const auto& [c, nb] : m_neighborEv)
        if (nb.peak > 0 && InAimScope(nb.x, nb.y))
            m_candidates.push_back({nb.peak, nb.x, nb.y});
    std::sort(m_candidates.begin(), m_candidates.end(),
              [](const Cand& a, const Cand& b) { return a.ev > b.ev; });
    m_candIdx = 0;

    if (m_aimArgmax) {
        // Aim at the single strongest reporter anywhere in the region.
        // audit A4: the search used to cover only this leader's OWN cell
        // members, because a neighbour's SHARE carried nothing but the cell
        // centre. The fix was therefore structurally capped at "best node
        // inside one 80 m cell" no matter how good the estimator was. SHARE now
        // carries each cell's peak reporter and its evidence, so a leader whose
        // neighbour saw something stronger aims THERE instead.
        double bestEv = -1, ax = m_cellCx, ay = m_cellCy;
        for (auto& [n, ne] : m_cellEvidence)
            if (ne.ev > bestEv && InAimScope(ne.x, ne.y)) { bestEv = ne.ev; ax = ne.x; ay = ne.y; }
        for (auto& [c, nb] : m_neighborEv)
            if (nb.peak > bestEv && InAimScope(nb.x, nb.y)) { bestEv = nb.peak; ax = nb.x; ay = nb.y; }
        // D30: the stand-down decision belongs HERE, where an aim finally exists
        // to compare against, not at the moment a claim arrived.
        if (m_electSuppress && ClaimedNearby(ax, ay)) {
            m_regionFormed = true;
            if (m_metrics) {
                Vector p = GetNode()->GetObject<MobilityModel>()->GetPosition();
                char det[64];
                std::snprintf(det, sizeof det, "c%d yields at elect", m_cellId);
                m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "CL",
                                 "elect_yield", det, p.x, p.y, 0);
            }
            return;
        }
        if (m_metrics) {
            m_metrics->MarkLocalize(Simulator::Now().GetSeconds());
            m_metrics->SetRegionCells((uint32_t)(1 + m_regionNeighbors.size()));
        }
        StartSummon(ax, ay);
        return;
    }
    double wx = 0, wy = 0, ws = 0;
    for (auto& [n, ne] : m_cellEvidence) {
        double w = ne.ev * ne.ev;
        wx += w * ne.x; wy += w * ne.y; ws += w;
    }
    for (auto& [c, nb] : m_neighborEv) {
        double w = nb.ev * nb.ev;
        wx += w * nb.x; wy += w * nb.y; ws += w;
    }
    double vx = ws > 0 ? wx / ws : m_cellCx, vy = ws > 0 ? wy / ws : m_cellCy;
    if (m_electSuppress && ClaimedNearby(vx, vy)) { m_regionFormed = true; return; }
    if (m_metrics) {
        m_metrics->MarkLocalize(Simulator::Now().GetSeconds());
        m_metrics->SetRegionCells((uint32_t)(1 + m_regionNeighbors.size()));
    }
    StartSummon(vx, vy);
}

// ---- region-leader beaconing + closure -------------------------------------

void SarGroundApp::StartSummon(double cx, double cy) {
    m_isLeader = true;
    m_regionFormed = true;
    m_cx = cx; m_cy = cy;
    // The region id identifies the ELECTED LEADER, not a constant. It used to be
    // hardcoded to 1 for every leader, so a delivering UAV could not tell its own
    // leader's re-aim from an unrelated cell's summon -- and was dragged around
    // by foreign summons (37 re-diverts against 9 real retargets, which is what
    // degraded the fix). Binding to one leader is what makes the fallback safe.
    m_regionId = (uint16_t)(m_cellId & 0xFFFF);
    // audit B2: announce the win on the flood plane, which is the only plane that
    // physically reaches the other cell leaders. Without this the election's
    // suppression half never arrived and every alerting cell summoned its own
    // UAV -- the redundant deliveries that inflated the proposed scheme's
    // packet count and split the fleet across duplicate regions.
    if (m_electSuppress) {
        m_rclaimSeen.insert((uint16_t)m_cellId);
        SendRclaim(m_cellId, (uint8_t)std::min(255.0, CellAggregate() * 255.0), 0,
                   (int16_t)(cx * 10), (int16_t)(cy * 10), (uint8_t)params::kShareTtl);
    }
    if (m_metrics) {
        Vector p = GetNode()->GetObject<MobilityModel>()->GetPosition();
        char det[64];
        std::snprintf(det, sizeof det, "target=%.1f;%.1f", cx, cy);
        m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "CL",
                         "summon_start", det, p.x, p.y, p.z);
    }
    BeaconTick();
    Simulator::Schedule(Seconds(params::kRetargetAfterS), &SarGroundApp::MaybeRetarget, this);
}

void SarGroundApp::MaybeRetarget() {
    // No CONFIRM within kRetargetAfterS of the summon means the delivery landed
    // somewhere the victim could not decode it. The leader still holds a ranked
    // candidate list, so it re-aims at the next one and keeps beaconing; the
    // DATA UAV overhead picks the new coordinates off the SUMMON. Bounded by
    // kMaxRetargets, otherwise this degenerates into a slow blind sweep.
    if (m_confirmed || m_confirmHeard || m_retargets >= params::kMaxRetargets) return;
    if (m_candIdx + 1 >= m_candidates.size()) return;     // nothing left to try
    m_candIdx++;
    m_retargets++;
    m_cx = m_candidates[m_candIdx].x;
    m_cy = m_candidates[m_candIdx].y;
    if (m_metrics) {
        Vector p = GetNode()->GetObject<MobilityModel>()->GetPosition();
        char det[80];
        std::snprintf(det, sizeof det, "no confirm; candidate %u -> %.1f;%.1f",
                      (unsigned)m_candIdx, m_cx, m_cy);
        m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "CL",
                         "retarget", det, p.x, p.y, p.z);
    }
    // A re-aim is useless if nothing is announcing it. The beacon may have been
    // cancelled or run down by the time a REJECT arrives, so restart it here.
    if (!m_beaconEvent.IsPending()) BeaconTick();
    Simulator::Schedule(Seconds(params::kRetargetAfterS), &SarGroundApp::MaybeRetarget, this);
}

void SarGroundApp::BeaconTick() {
    if (m_confirmed || m_confirmHeard) return;
    if (m_dev) {
        std::vector<uint8_t> b(kSummonLen);
        uint8_t* q = b.data();
        *q++ = (uint8_t)Msg::SUMMON;
        *q++ = kBroadcast;
        std::memcpy(q, &m_regionId, 2); q += 2;
        int16_t cx = (int16_t)(m_cx * 10), cy = (int16_t)(m_cy * 10);
        std::memcpy(q, &cx, 2); q += 2;
        std::memcpy(q, &cy, 2); q += 2;
        m_dev->Send(Create<Packet>(b.data(), b.size()), Mac16Address("ff:ff"), 0);
        if (m_metrics) { m_metrics->AddBeacon(); m_metrics->AddSent(); m_metrics->AddSentBytes(b.size()); }
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
        // D30: a non-leader stamps the region it heard summoned, not the
        // default 1, so closure is attributable to a place.
        uint16_t rid = m_isLeader ? m_regionId : m_heardRegionId;
        std::memcpy(q, &rid, 2); q += 2;
        *q++ = (uint8_t)(m_nodeId & 0xFF);
        m_dev->Send(Create<Packet>(c.data(), c.size()), Mac16Address("ff:ff"), 0);
        if (m_metrics) { m_metrics->AddSent(); m_metrics->AddSentBytes(c.size()); }
    }
    m_confirmsSent++;
    m_confirmEvent = Simulator::Schedule(Seconds(params::kConfirmRetryS),
                                         &SarGroundApp::SendConfirm, this);
}

void SarGroundApp::SendReject() {
    // The negative half of loop closure. Only a node holding the COMPLETE
    // reference can send this, which is the whole point: the cue fragments a
    // false positive matched on cannot rule it out, the full dataset can. It
    // lets the fleet leave a wrong region on evidence rather than on a timeout,
    // and it is also the honest fix for the closure bug in STATUS.md open
    // problem 2 -- a bystander under the drop point no longer closes the loop
    // just by holding the data, it has to hold the data AND match it.
    if (m_rejectsSent >= params::kConfirmRetries) return;
    if (m_dev) {
        std::vector<uint8_t> c(kRejectLen);
        uint8_t* q = c.data();
        *q++ = (uint8_t)Msg::REJECT;
        *q++ = kBroadcast;
        // D30: a non-leader stamps the region it heard summoned, not the
        // default 1, so closure is attributable to a place.
        uint16_t rid = m_isLeader ? m_regionId : m_heardRegionId;
        std::memcpy(q, &rid, 2); q += 2;
        *q++ = (uint8_t)(m_nodeId & 0xFF);
        m_dev->Send(Create<Packet>(c.data(), c.size()), Mac16Address("ff:ff"), 0);
        if (m_metrics) { m_metrics->AddSent(); m_metrics->AddSentBytes(c.size()); }
    }
    m_rejectsSent++;
    m_rejectEvent = Simulator::Schedule(Seconds(params::kConfirmRetryS),
                                        &SarGroundApp::SendReject, this);
}

bool SarGroundApp::OnReceive(Ptr<NetDevice>, Ptr<const Packet> pkt, uint16_t, const Address&) {
    uint32_t sz = pkt->GetSize();
    if (sz < 2) return true;
    std::vector<uint8_t> b(sz);
    pkt->CopyData(b.data(), sz);
    uint8_t type = b[0];

    if (type == (uint8_t)Msg::CONFIRM) {
        // A delivery closed. Go quiet AND stop the retarget chain -- m_confirmed
        // only means "I personally hold the dataset", so without this flag a
        // leader kept re-aiming after a delivery that had already succeeded.
        //
        // D30: but only for THIS region. The handler used to ignore the regionId
        // it is handed, so any confirm anywhere permanently silenced every
        // leader's beacon, election, retarget and cue-triggered re-announce --
        // the same unscoped stand-down that electScope fixed for RCLAIM and
        // never fixed here. With several candidate places that meant the first
        // one to close ended the search for all the others.
        uint16_t rid = 0xFFFF;
        if (sz >= kConfirmLen) std::memcpy(&rid, &b[2], 2);
        const uint16_t mine = m_isLeader ? m_regionId : m_heardRegionId;
        if (rid == 0xFFFF || mine == 0xFFFF || rid == mine) {
            m_confirmHeard = true;
            Simulator::Cancel(m_beaconEvent);
        }
        return true;
    }
    if (type == (uint8_t)Msg::REJECT) {
        // Somebody under the drop point now holds the whole reference and does
        // NOT match it. That is a stronger signal than the retarget timeout it
        // replaces: the timeout could only ever guess that the aim was wrong
        // after waiting past the tail of normal completion, whereas this is the
        // field telling us. Re-aim immediately, unless a CONFIRM already closed
        // the loop (a region can contain both a match and a bystander, and the
        // match wins).
        m_rejectHeard = true;
        if (m_isLeader && !m_confirmHeard && !m_confirmed) MaybeRetarget();
        return true;
    }
    if (type == (uint8_t)Msg::SUMMON && sz >= kSummonLen) {
        uint16_t rid; std::memcpy(&rid, &b[2], 2);
        int16_t sx, sy; std::memcpy(&sx, &b[4], 2); std::memcpy(&sy, &b[6], 2);
        double ax = sx / 10.0, ay = sy / 10.0;
        // D30: an ordinary node adopts the NEAREST region it has heard summoned,
        // so its CONFIRM/REJECT can say WHICH place was resolved. Before this
        // every non-leader stamped the default regionId=1 and closure could not
        // be attributed at all.
        Vector p = GetNode()->GetObject<MobilityModel>()->GetPosition();
        double d = std::hypot(ax - p.x, ay - p.y);
        if (d < m_heardAimD) {
            m_heardAimD = d; m_heardRegionId = rid; m_heardAimX = ax; m_heardAimY = ay;
        }
        // Suppression, now scoped the same way RCLAIM is: hearing a summon about
        // a DIFFERENT place is not a reason to abandon this cell's own region.
        if (!m_regionFormed) {
            m_claimedAims.push_back({ax, ay});
            double mx = 0, my = 0;
            bool samePlace = m_electScope <= 0 ||
                             (BestAim(mx, my) && std::hypot(ax - mx, ay - my) <= m_electScope);
            if (samePlace) { m_regionFormed = true; Simulator::Cancel(m_electEvent); }
        }
        return true;
    }
    if (type == (uint8_t)Msg::RCLAIM && sz >= kRclaimLen) {
        // audit B2: the same suppression, but carried by the multi-hop flood so
        // it can actually reach a leader 63-156 m away over a ~37 m radio.
        // First claim wins: the backoff is evidence-ordered, so the strongest
        // alerting cell is the one that gets to fire first.
        uint16_t origCell; std::memcpy(&origCell, &b[1], 2);
        uint8_t evQ8 = b[3], peakQ8 = b[4];
        int16_t cx, cy; std::memcpy(&cx, &b[5], 2); std::memcpy(&cy, &b[7], 2);
        uint8_t ttl = b[9];
        if (!m_rclaimSeen.insert(origCell).second) return true;   // already flooded
        if (m_metrics) { m_metrics->AddRecv(); m_metrics->AddRecvBytes(sz); }
        // Yield only if the claim is about the SAME PLACE. Without this the
        // stand-down is unscoped: whichever cell fires first silences every
        // other alerting cell in the field, including cells whose evidence comes
        // from a completely different object hundreds of metres away.
        // D30: remember the claimed AIM instead of latching a boolean. The old
        // code stood down unconditionally when this cell had no aim of its own
        // -- which is the usual case, because the first RCLAIM floods the field
        // within milliseconds of the first cell alerting, long before the others
        // have any evidence. Measured at 16x16 with four confusable objects: TEN
        // cells spanning the whole 300 m field yielded to c9 inside 30 ms, and
        // `m_regionFormed` never resets, so exactly one region could ever form
        // however many candidate places existed. Deciding at ELECTION time, when
        // this cell finally has an aim to compare, is what makes electScope
        // actually scope anything.
        double ax = cx / 10.0, ay = cy / 10.0, mx = 0, my = 0;
        if ((int32_t)origCell != m_cellId) m_claimedAims.push_back({ax, ay});
        bool samePlace = m_electScope <= 0 ||
                         (BestAim(mx, my) && std::hypot(ax - mx, ay - my) <= m_electScope);
        if ((int32_t)origCell != m_cellId && !m_regionFormed && samePlace) {
            m_regionFormed = true;
            Simulator::Cancel(m_electEvent);
            if (m_isCellLeader && m_metrics) {
                Vector p = GetNode()->GetObject<MobilityModel>()->GetPosition();
                char det[48];
                std::snprintf(det, sizeof det, "c%d yields to c%d", m_cellId, (int)origCell);
                m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "CL",
                                 "elect_yield", det, p.x, p.y, 0);
            }
        }
        if (ttl > 0)
            Simulator::Schedule(Seconds(m_rng->GetValue(0.0, params::kFwdStaggerMaxS)),
                                &SarGroundApp::SendRclaim, this, (int32_t)origCell,
                                evQ8, peakQ8, cx, cy, (uint8_t)(ttl - 1));
        return true;
    }
    if (type == (uint8_t)Msg::RPT && sz >= kRptLen) {
        uint16_t nextHop, orig;
        std::memcpy(&nextHop, &b[1], 2);
        std::memcpy(&orig, &b[3], 2);
        uint8_t evQ8 = b[5], ttl = b[6];
        int16_t x, y; std::memcpy(&x, &b[7], 2); std::memcpy(&y, &b[9], 2);
        if (nextHop != (uint16_t)m_nodeId) return true;      // not my hop
        if (m_metrics) { m_metrics->AddRecv(); m_metrics->AddRecvBytes(sz); }
        auto sit = m_rptSeen.find(orig);
        if (sit != m_rptSeen.end() && sit->second >= evQ8) return true;  // stale/dup
        m_rptSeen[orig] = evQ8;
        double ev = evQ8 / 255.0;
        if (m_isCellLeader) {
            LeaderIngest(orig, ev, x / 10.0, y / 10.0);       // reached the CL
        } else if (ttl > 0) {
            Simulator::Schedule(Seconds(m_rng->GetValue(0.0, params::kFwdStaggerMaxS)),
                                &SarGroundApp::SendRpt, this, orig, evQ8, x, y,
                                m_treeParent, (uint8_t)(ttl - 1));
        }
        return true;
    }
    if (type == (uint8_t)Msg::SHARE && sz >= kShareLen) {
        uint16_t origCell; std::memcpy(&origCell, &b[1], 2);
        uint8_t evQ8 = b[3], peakQ8 = b[4];
        int16_t cx, cy; std::memcpy(&cx, &b[5], 2); std::memcpy(&cy, &b[7], 2);
        uint8_t ttl = b[9];
        if (m_metrics) { m_metrics->AddRecv(); m_metrics->AddRecvBytes(sz); }
        auto sit = m_shareSeen.find(origCell);
        if (sit != m_shareSeen.end() && sit->second >= evQ8) return true;  // dup/stale
        m_shareSeen[origCell] = evQ8;
        // A Cell Leader hearing a corroborating (>=coop) foreign cell's SHARE =
        // the cross-cell link was carried by the real radio: count it and grow
        // this leader's region view.
        if (m_isCellLeader && (int32_t)origCell != m_cellId && (evQ8 / 255.0) >= m_coop) {
            double nev = evQ8 / 255.0;
            NbInfo& nb = m_neighborEv[(int32_t)origCell];
            if (nev > nb.ev) { nb.ev = nev; nb.peak = peakQ8 / 255.0;
                               nb.x = cx / 10.0; nb.y = cy / 10.0; }
            if (m_regionNeighbors.insert((int32_t)origCell).second && m_metrics) {
                m_metrics->AddInterShare();
                Vector p = GetNode()->GetObject<MobilityModel>()->GetPosition();
                char det[48]; std::snprintf(det, sizeof det, "c%d -> c%d", (int)origCell, m_cellId);
                m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "CL", "share", det, p.x, p.y, 0);
            }
        }
        if (ttl > 0)
            Simulator::Schedule(Seconds(m_rng->GetValue(0.0, params::kFwdStaggerMaxS)),
                                &SarGroundApp::SendShare, this, (int32_t)origCell, evQ8,
                                peakQ8, cx, cy, (uint8_t)(ttl - 1));
        return true;
    }
    if ((type == (uint8_t)Msg::CUE || type == (uint8_t)Msg::FULL) && sz >= kChunkHdr) {
        uint16_t fragId, seq, total;
        std::memcpy(&fragId, &b[2], 2);
        std::memcpy(&seq, &b[4], 2);
        std::memcpy(&total, &b[6], 2);
        if (m_metrics) { m_metrics->AddRecv(); m_metrics->AddRecvBytes(sz); }
        if (type == (uint8_t)Msg::CUE && !m_heardCue && m_metrics) {
            m_heardCue = true;
            Vector p = GetNode()->GetObject<MobilityModel>()->GetPosition();
            m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "node",
                             "cue_rx", "", p.x, p.y, p.z);
        }

        // audit: the summon has to reach the SKY, and a leader beaconing on a
        // fixed 60 s quota is beaconing into an empty sky most of the time. At
        // 40x40 the aim was computed correctly at 66 s and the first UAV did not
        // pass within earshot until ~250 s, so the delivery never happened at
        // all. A CUE chunk is direct proof that a UAV is within one hop RIGHT
        // NOW, so an elected leader re-announces on hearing one. Rate-limited to
        // one per beacon interval, and it stops the moment a CONFIRM arrives.
        if (type == (uint8_t)Msg::CUE && m_isLeader && !m_confirmHeard) {
            double now = Simulator::Now().GetSeconds();
            if (now - m_lastCueSummonS >= params::kBeaconIntervalS) {
                m_lastCueSummonS = now;
                if (!m_beaconEvent.IsPending()) BeaconTick();
            }
        }

        m_chunksRx++;                     // coded recovery counts duplicates
        bool wasComplete = m_have.count(fragId) > 0;
        m_chunks[fragId].insert(seq);
        m_totals[fragId] = total;
        if (!wasComplete && m_chunks[fragId].size() >= total) {
            m_have.insert(fragId);

            // New fragment possessed -> evidence grew; report to the Cell Leader
            // over the real radio (RPT up the cell tree). Proposed only. Keep
            // re-sending at a low rate while relevant: a single-shot report dies
            // on deep trees / large areas (standard sensor-report retry).
            if (m_echoMode) {
                // audit W4: reply directly to the sky, once, and keep repeating
                // at a low rate while a UAV might still be listening.
                double eff = PossessedConfidence() * ClueNow();
                if (eff >= m_coop && !m_echoEvent.IsPending() && m_echoesSent == 0)
                    SendEcho();
            }
            if (m_cooperative) {
                double eff = PossessedConfidence() * ClueNow();
                if (eff >= m_coop) {
                    m_lastEff = eff;
                    DeliverEvidence(eff);
                    if (!m_rptRepeatEvent.IsPending())
                        m_rptRepeatEvent = Simulator::Schedule(Seconds(params::kRptRepeatS),
                                                               &SarGroundApp::RptRepeatTick, this);
                }
            }

            // Loop closure on holding the ENTIRE dataset: any node that
            // reconstructs the full reference confirms the identity (it is under
            // the delivery, so its CONFIRM link is short/reliable).
            //
            // audit A6: what used to live here as well was a ground-truth stop
            // -- the simulation ended the moment the VICTIM node completed,
            // which is an oracle no deployed system has, and it set the
            // baselines' energy and packet totals. Audit B1 disabled it via
            // --allHome; it is now deleted outright. An oracle one flag away
            // from live is how the original bypass got published, and no
            // ablation needs this one: --allHome=0 still shortens the mission
            // by changing the COMPLETION RULE, which is a declared policy, not
            // a peek at the answer.
            if (!m_confirmed && HasEntireDataset()) {
                m_confirmed = true;
                Simulator::Cancel(m_beaconEvent);
                Vector p = GetNode()->GetObject<MobilityModel>()->GetPosition();
                if (m_isTarget && m_metrics)
                    m_metrics->MarkCompleteData(Simulator::Now().GetSeconds());
                // audit W4: the closed-loop arm confirms too. Its whole premise
                // is single-hop feedback to the UAV overhead, and CONFIRM is
                // exactly that -- without it the DATA UAV waits for a closure
                // signal that can never arrive and delivers until the horizon
                // (measured: 58k packets and a mission that never completes).
                // The BLIND baselines still do not confirm: they dwell a fixed
                // budget and have no feedback path at all, which is the point.
                if (m_cooperative || m_echoMode) {
                    // Holding the dataset is no longer sufficient to confirm --
                    // the node must still MATCH it. A node that matched on cue
                    // fragments and fails on the complete reference has just
                    // discovered it is a false positive, and says so.
                    // Identity claim, not a relevance claim: a strictly higher
                    // bar than the reporting threshold (see kConfirmThreshold).
                    bool matches = ClueNow() >= m_confirmThr;
                    if (m_metrics)
                        m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId,
                                         m_isTarget ? "target" : "node",
                                         matches ? "confirm" : "reject",
                                         matches ? "entire dataset received"
                                                 : "full data does not match",
                                         p.x, p.y, p.z);
                    if (matches) SendConfirm(); else SendReject();
                } else if (m_metrics) {
                    // multicast baselines: log every GT's completion so the
                    // fairness analysis can check the ACTUAL multicast goal
                    // (all GTs recover the file), not just the victim.
                    m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId,
                                     "node", "gt_done", "", p.x, p.y, p.z);
                }
            }
        }
    }
    return true;
}

}  // namespace ns3::uavsar
