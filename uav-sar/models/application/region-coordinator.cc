#include "region-coordinator.h"
#include "../common/sar-metrics.h"
#include "../common/sar-params.h"

#include "ns3/simulator.h"
#include "ns3/nstime.h"

#include <algorithm>
#include <cmath>
#include <queue>
#include <set>

namespace ns3::uavsar {

void RegionCoordinator::Init(const CellGridPlan* plan, const InterCellRouting* routing,
                             SarMetrics* metrics, double alertThreshold,
                             double coopThreshold, uint32_t seed, SummonCb cb) {
    m_plan = plan;
    m_routing = routing;
    m_metrics = metrics;
    m_alert = alertThreshold;
    m_coop = coopThreshold;
    m_rng.seed(seed + 1000);
    m_onSummon = std::move(cb);
}

void RegionCoordinator::ReportClue(uint32_t nodeId, double evidence, double /*tNow*/) {
    if (m_summoned || !m_plan) return;
    auto it = m_plan->nodes.find(nodeId);
    if (it == m_plan->nodes.end()) return;

    // Transport up the intra-cell tree: per-hop delay; success p_intra.
    // A failed report is simply lost — the node will report again on its next
    // fragment completion (natural retry).
    if (m_u01(m_rng) > params::kCoopSuccIntra) return;
    uint32_t hops = it->second.hopToLeader;
    if (hops == 0xFFFFFFFF) hops = 1;  // isolated-in-cell: treat as one lossy hop
    double delay = std::max<uint32_t>(1, hops) * params::kHopDelayS;
    ns3::Simulator::Schedule(ns3::Seconds(delay),
                             &RegionCoordinator::EvidenceArrive, this, nodeId, evidence);
}

void RegionCoordinator::EvidenceArrive(uint32_t nodeId, double evidence) {
    if (m_summoned) return;
    double& e = m_nodeEvidence[nodeId];
    if (evidence > e) e = evidence;
    if (m_metrics) m_metrics->AddIntraShare();

    if (m_windowOpen) return;

    // Open the region window once any cell's aggregate crosses alert.
    std::map<int32_t, double> cellEv;
    for (auto& [nid, ev] : m_nodeEvidence) {
        int32_t c = m_plan->nodes.at(nid).cellId;
        double& agg = cellEv[c];
        agg = 1.0 - (1.0 - agg) * (1.0 - ev);
    }
    for (auto& [c, ev] : cellEv) {
        if (ev >= m_alert) {
            m_windowOpen = true;
            ns3::Simulator::Schedule(ns3::Seconds(params::kRegionWindowS),
                                     &RegionCoordinator::CloseWindow, this);
            return;
        }
    }
}

void RegionCoordinator::CloseWindow() {
    if (m_summoned) return;

    // Aggregate evidence per cell (union-prob over reporting members).
    std::map<int32_t, double> cellEv;
    for (auto& [nid, ev] : m_nodeEvidence) {
        int32_t c = m_plan->nodes.at(nid).cellId;
        double& agg = cellEv[c];
        agg = 1.0 - (1.0 - agg) * (1.0 - ev);
    }

    int32_t seedCell = -1;
    double best = 0;
    for (auto& [c, e] : cellEv)
        if (e >= m_alert && e > best) { best = e; seedCell = c; }
    if (seedCell < 0) { m_windowOpen = false; return; }  // evidence faded? re-arm

    // Grow the region across adjacency through corroborating clue-cells, but
    // each cross-cell share succeeds only with p_inter (through the CGW link).
    std::set<int32_t> region;
    std::queue<int32_t> bfs;
    region.insert(seedCell);
    bfs.push(seedCell);
    uint32_t interOk = 0;
    while (!bfs.empty()) {
        int32_t c = bfs.front();
        bfs.pop();
        auto cit = m_plan->cells.find(c);
        if (cit == m_plan->cells.end()) continue;
        for (int32_t adj : cit->second.adjacentCells) {
            if (region.count(adj)) continue;
            auto eit = cellEv.find(adj);
            if (eit == cellEv.end() || eit->second < m_coop) continue;
            // gateway must exist and the share must survive the inter-cell link
            bool hasGw = m_routing && m_routing->gateway.count(c) &&
                         m_routing->gateway.at(c).count(adj);
            if (!hasGw) continue;
            if (m_u01(m_rng) > params::kCoopSuccInter) continue;  // share lost
            interOk++;
            region.insert(adj);
            bfs.push(adj);
        }
    }

    // Elect the region leader = clue-cell with max evidence (tie: lowest id).
    int32_t leaderCell = seedCell;
    double leaderEv = cellEv[seedCell];
    for (int32_t c : region) {
        double e = cellEv[c];
        if (e > leaderEv + 1e-9 || (std::fabs(e - leaderEv) <= 1e-9 && c < leaderCell)) {
            leaderEv = e;
            leaderCell = c;
        }
    }

    // Evidence-weighted centroid (metrics/log; the summon itself carries the
    // leader's own position).
    double wx = 0, wy = 0, ws = 0;
    for (int32_t c : region) {
        const CellInfo& ci = m_plan->cells.at(c);
        double w = cellEv[c];
        wx += w * ci.centerX;
        wy += w * ci.centerY;
        ws += w;
    }

    if (m_metrics) {
        m_metrics->SetRegionCells((uint32_t)region.size());
        for (uint32_t i = 0; i < interOk; i++) m_metrics->AddInterShare();
        m_metrics->MarkLocalize(ns3::Simulator::Now().GetSeconds());
    }

    m_summoned = true;
    uint32_t leaderNode = m_plan->cells.at(leaderCell).leaderId;
    if (m_onSummon)
        m_onSummon(leaderNode, 1, ws > 0 ? wx / ws : 0, ws > 0 ? wy / ws : 0);
}

}  // namespace ns3::uavsar
