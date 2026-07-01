#include "region-coordinator.h"
#include "../common/sar-metrics.h"

#include <cmath>
#include <map>
#include <queue>
#include <set>

namespace ns3::uavsar {

void RegionCoordinator::Init(const CellGridPlan* plan, const InterCellRouting* routing,
                             SarMetrics* metrics, double alertThreshold,
                             double coopThreshold, SummonCb cb) {
    m_plan = plan; m_routing = routing; m_metrics = metrics;
    m_alert = alertThreshold; m_coop = coopThreshold; m_onSummon = std::move(cb);
}

void RegionCoordinator::ReportClue(uint32_t nodeId, double evidence, double tNow) {
    if (m_summoned || !m_plan) return;
    if (m_plan->nodes.find(nodeId) == m_plan->nodes.end()) return;
    // keep the strongest evidence seen from each node (no double counting).
    double& e = m_nodeEvidence[nodeId];
    if (evidence > e) e = evidence;
    MaybeFormRegion(tNow);
}

void RegionCoordinator::MaybeFormRegion(double tNow) {
    // cell evidence = union-prob over its reporting members.
    std::map<int32_t, double> cellEv;
    std::map<int32_t, uint32_t> cellReports;
    for (auto& [nodeId, ev] : m_nodeEvidence) {
        if (ev <= 0) continue;
        int32_t c = m_plan->nodes.at(nodeId).cellId;
        double& agg = cellEv[c];
        agg = 1.0 - (1.0 - agg) * (1.0 - ev);
        cellReports[c]++;
    }

    // need at least one cell over alert to act.
    int32_t seed = -1; double best = 0;
    for (auto& [c, e] : cellEv)
        if (e >= m_alert && e > best) { best = e; seed = c; }
    if (seed < 0) return;

    // grow region over adjacency through corroborating (>=coop) clue-cells.
    std::set<int32_t> region;
    std::queue<int32_t> q;
    q.push(seed); region.insert(seed);
    uint32_t interEdges = 0;
    while (!q.empty()) {
        int32_t c = q.front(); q.pop();
        auto cit = m_plan->cells.find(c);
        if (cit == m_plan->cells.end()) continue;
        for (int32_t adj : cit->second.adjacentCells) {
            auto eit = cellEv.find(adj);
            if (eit == cellEv.end() || eit->second < m_coop) continue;
            if (region.count(adj)) continue;
            interEdges++;
            region.insert(adj); q.push(adj);
        }
    }

    // region leader = clue-cell with max evidence (tie -> lowest cellId).
    int32_t leaderCell = seed; double leaderEv = cellEv[seed];
    for (int32_t c : region) {
        double e = cellEv[c];
        if (e > leaderEv + 1e-9 || (std::fabs(e - leaderEv) <= 1e-9 && c < leaderCell)) {
            leaderEv = e; leaderCell = c;
        }
    }

    // evidence-weighted centroid + tallies.
    double wx = 0, wy = 0, ws = 0; uint32_t intraTotal = 0;
    for (int32_t c : region) {
        const CellInfo& ci = m_plan->cells.at(c);
        double w = cellEv[c];
        wx += w * ci.centerX; wy += w * ci.centerY; ws += w;
        intraTotal += cellReports[c];
    }
    double cx = ws > 0 ? wx / ws : 0, cy = ws > 0 ? wy / ws : 0;

    if (m_metrics) {
        m_metrics->SetRegionCells((uint32_t)region.size());
        for (uint32_t i = 0; i < intraTotal; i++) m_metrics->AddIntraShare();
        for (uint32_t i = 0; i < interEdges; i++) m_metrics->AddInterShare();
        m_metrics->MarkLocalize(tNow);
    }

    m_summoned = true;
    uint32_t leaderNode = m_plan->cells.at(leaderCell).leaderId;
    if (m_onSummon) m_onSummon(leaderNode, 1, cx, cy);
}

}  // namespace ns3::uavsar
