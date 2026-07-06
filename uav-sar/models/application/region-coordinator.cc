#include "region-coordinator.h"
#include "../common/sar-metrics.h"
#include "../common/sar-params.h"

#include "ns3/simulator.h"
#include "ns3/nstime.h"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <queue>
#include <set>
#include <string>

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
    if (m_plan->nodes.find(nodeId) == m_plan->nodes.end()) return;

    // The evidence has already crossed the REAL radio to reach this node's Cell
    // Leader (RPT, forwarded up the cell tree; the CL relays it here) — or it is
    // the CL's own local evidence. Aggregate it directly: the intra-cell
    // transport loss/latency is now the channel's, not a probability/delay proxy.
    EvidenceArrive(nodeId, evidence);
}

void RegionCoordinator::RecordShare(int32_t fromCell, int32_t toCell) {
    if (m_summoned) return;
    m_shareEdges.emplace(fromCell, toCell);
}

void RegionCoordinator::EvidenceArrive(uint32_t nodeId, double evidence) {
    if (m_summoned) return;
    double& e = m_nodeEvidence[nodeId];
    if (evidence > e) e = evidence;
    if (m_metrics) {
        m_metrics->AddIntraShare();
        // viz: node -> its CL up the intra-cell tree. No commas in detail so
        // the CSV row stays unquoted for simple parsers.
        const CellNodeInfo& ni = m_plan->nodes.at(nodeId);
        const CellInfo& ci = m_plan->cells.at(ni.cellId);
        const CellNodeInfo& li = m_plan->nodes.at(ci.leaderId);
        char det[64];
        std::snprintf(det, sizeof det, "ev=%.2f dst=%u@%.0f;%.0f",
                      evidence, ci.leaderId, li.x, li.y);
        m_metrics->Event(ns3::Simulator::Now().GetSeconds(), nodeId, "node",
                         "clue_report", det, ni.x, ni.y, 0);
    }

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
            // The corroborating cell's SHARE must have physically reached a
            // leader across the boundary over the real radio (either direction
            // of the flood) — no probability proxy any more.
            if (!m_shareEdges.count({c, adj}) && !m_shareEdges.count({adj, c}))
                continue;
            interOk++;
            region.insert(adj);
            bfs.push(adj);
            if (m_metrics) {  // viz: CL(c) -> CL(adj) through the CGW link
                const CellNodeInfo& sl = m_plan->nodes.at(cit->second.leaderId);
                const CellNodeInfo& dl =
                    m_plan->nodes.at(m_plan->cells.at(adj).leaderId);
                char det[64];
                std::snprintf(det, sizeof det, "c%d->c%d dst=%u@%.0f;%.0f",
                              c, adj, m_plan->cells.at(adj).leaderId, dl.x, dl.y);
                m_metrics->Event(ns3::Simulator::Now().GetSeconds(),
                                 cit->second.leaderId, "CL", "share", det,
                                 sl.x, sl.y, 0);
            }
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

    // Verifier = strongest-evidence node inside the region (tie: lowest id).
    uint32_t verifier = m_plan->cells.at(leaderCell).leaderId;
    double bestNodeEv = -1;
    for (auto& [nid, ev] : m_nodeEvidence) {
        int32_t c = m_plan->nodes.at(nid).cellId;
        if (!region.count(c)) continue;
        if (ev > bestNodeEv + 1e-9 ||
            (std::fabs(ev - bestNodeEv) <= 1e-9 && nid < verifier)) {
            bestNodeEv = ev;
            verifier = nid;
        }
    }

    if (m_metrics) {
        m_metrics->SetRegionCells((uint32_t)region.size());
        for (uint32_t i = 0; i < interOk; i++) m_metrics->AddInterShare();
        m_metrics->MarkLocalize(ns3::Simulator::Now().GetSeconds());
        // viz: the formed region — cell ids + verifier, at the weighted centroid.
        std::string cellsStr;
        for (int32_t c : region)
            cellsStr += (cellsStr.empty() ? "" : ";") + std::to_string(c);
        m_metrics->Event(ns3::Simulator::Now().GetSeconds(),
                         m_plan->cells.at(leaderCell).leaderId, "CL", "region",
                         "cells=" + cellsStr + " verifier=" + std::to_string(verifier),
                         ws > 0 ? wx / ws : 0, ws > 0 ? wy / ws : 0, 0);
    }

    m_summoned = true;
    std::vector<uint32_t> leaders;
    for (int32_t c : region) leaders.push_back(m_plan->cells.at(c).leaderId);
    if (m_onSummon) m_onSummon(leaders, verifier, 1);
}

}  // namespace ns3::uavsar
