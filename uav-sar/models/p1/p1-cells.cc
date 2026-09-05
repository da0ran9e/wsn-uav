#include "p1-cells.h"

#include <algorithm>
#include <cmath>
#include <deque>

namespace ns3::uavsar::p1 {

std::vector<int32_t> CellPlan::ServedCells() const {
    std::vector<int32_t> out;
    for (const auto& [cid, c] : cells)
        if (c.cls == CellClass::SERVED) out.push_back(cid);
    return out;
}

CellPlan BuildCells(const std::vector<Node>& nodes, double cellRadiusM,
                    double groundRangeM) {
    CellPlan plan;
    plan.cellRadiusM = cellRadiusM;

    // --- partition ---------------------------------------------------------
    std::map<std::pair<int32_t, int32_t>, int32_t> byAxial;
    std::map<uint32_t, const Node*> byId;
    for (const Node& n : nodes) {
        byId[n.id] = &n;
        int32_t q, r;
        hex::WorldToAxial(n.x, n.y, cellRadiusM, q, r);
        auto key = std::make_pair(q, r);
        auto it = byAxial.find(key);
        if (it == byAxial.end()) {
            const int32_t cid = (int32_t)plan.cells.size();
            byAxial[key] = cid;
            Cell c;
            c.id = cid;
            c.q = q;
            c.r = r;
            hex::AxialToCentre(q, r, cellRadiusM, c.cx, c.cy);
            plan.cells[cid] = c;
            it = byAxial.find(key);
        }
        plan.cells[it->second].members.push_back(CellMember{n.id, -1, 0xFFFFFFFFu});
        plan.cellOfNode[n.id] = it->second;
    }

    for (auto& [cid, c] : plan.cells) {
        // --- elect ---------------------------------------------------------
        // Having a camera is a HARD FILTER applied before any weighting. Under
        // N3 the head is the matching subject, so a head without a camera is not
        // a cheaper head -- it is a different job, and one nobody can do.
        double best = -1.0;
        uint32_t bestId = 0;
        bool found = false;
        for (const CellMember& m : c.members) {
            const Node& n = *byId[m.id];
            if (!n.HasCamera()) continue;
            c.cameras++;
            const double s = n.ElectScore();
            if (s > best) { best = s; bestId = n.id; found = true; }
        }
        c.cls = found ? CellClass::SERVED : CellClass::BARREN;
        c.hasLeader = found;
        c.leader = bestId;
        c.leaderScore = found ? best : 0.0;
        if (found) plan.nServed++; else plan.nBarren++;

        // --- route, rooted at the elected leader ---------------------------
        if (!c.hasLeader) { c.unreachable = (uint32_t)c.members.size(); continue; }
        std::map<uint32_t, size_t> slot;
        for (size_t i = 0; i < c.members.size(); ++i) slot[c.members[i].id] = i;
        c.members[slot[c.leader]].hops = 0;
        c.members[slot[c.leader]].parent = -1;
        std::deque<uint32_t> q{c.leader};
        while (!q.empty()) {
            const uint32_t cur = q.front();
            q.pop_front();
            const Node& a = *byId[cur];
            const uint32_t d = c.members[slot[cur]].hops;
            for (CellMember& m : c.members) {
                if (m.hops != 0xFFFFFFFFu) continue;
                const Node& b = *byId[m.id];
                if (std::hypot(a.x - b.x, a.y - b.y) > groundRangeM) continue;
                m.hops = d + 1;
                m.parent = (int32_t)cur;
                q.push_back(m.id);
            }
        }
        for (const CellMember& m : c.members)
            if (m.hops == 0xFFFFFFFFu) c.unreachable++;

    }
    return plan;
}

double LeaderScoreCv(const CellPlan& plan) {
    double s = 0, s2 = 0;
    uint32_t n = 0;
    for (const auto& [cid, c] : plan.cells) {
        if (!c.hasLeader) continue;
        s += c.leaderScore;
        s2 += c.leaderScore * c.leaderScore;
        n++;
    }
    if (!n) return 0.0;
    const double mean = s / n;
    if (mean <= 0.0) return 0.0;
    return std::sqrt(std::max(0.0, s2 / n - mean * mean)) / mean;
}

}  // namespace ns3::uavsar::p1
