#include "p1-cells.h"

#include <algorithm>
#include <cmath>
#include <deque>

namespace ns3::uavsar::p1 {

std::vector<int32_t> CellPlan::ClassACells() const {
    std::vector<int32_t> out;
    for (const auto& [cid, c] : cells)
        if (c.cls == CellClass::A) out.push_back(cid);
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
        // Modality is a hard filter, applied before any weighting: a leader that
        // cannot run the match is not a cheaper leader, it is a different job.
        double bestMatch = -1.0, bestAny = -1.0;
        uint32_t matchId = 0, anyId = 0;
        bool haveMatch = false, haveAny = false;
        for (const CellMember& m : c.members) {
            const Node& n = *byId[m.id];
            if (n.Images()) c.imagers++;
            if (n.CanMatch()) c.matchers++;
            const double s = n.ElectScore();
            if (s > bestAny) { bestAny = s; anyId = n.id; haveAny = true; }
            if (n.CanMatch() && s > bestMatch) { bestMatch = s; matchId = n.id; haveMatch = true; }
        }
        if (haveMatch) {
            c.cls = CellClass::A;
            c.leader = matchId;
            c.leaderScore = bestMatch;
            c.hasLeader = true;
        } else {
            c.cls = c.imagers > 0 ? CellClass::B : CellClass::C;
            c.leader = anyId;
            c.leaderScore = haveAny ? bestAny : 0.0;
            c.hasLeader = haveAny;
        }
        switch (c.cls) {
            case CellClass::A: plan.nA++; break;
            case CellClass::B: plan.nB++; break;
            default:           plan.nC++; break;
        }

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

        c.tLocalS = LocalDisseminationS(c, nodes, kThetaFullBytes);
    }
    return plan;
}

double LocalDisseminationS(const Cell& cell, const std::vector<Node>& nodes,
                           double bytes) {
    // Store and forward: a node cannot pass on what it has not finished
    // receiving, so the time to reach a member is the sum of the transfer times
    // down its path. The cell is done when its slowest MATCHER is done --
    // members that cannot run the match are not waited for, for the same reason
    // class B cells are not flown to.
    std::map<uint32_t, const Node*> byId;
    for (const Node& n : nodes) byId[n.id] = &n;
    std::map<uint32_t, const CellMember*> mem;
    for (const CellMember& m : cell.members) mem[m.id] = &m;

    double worst = 0.0;
    for (const CellMember& m : cell.members) {
        const Node* n = byId.count(m.id) ? byId.at(m.id) : nullptr;
        if (!n || !n->CanMatch() || m.hops == 0xFFFFFFFFu) continue;
        double t = 0.0;
        const CellMember* cur = &m;
        while (cur && cur->hops > 0) {
            const Node* rx = byId.at(cur->id);
            t += rx->rxBps > 0 ? bytes * 8.0 / rx->rxBps : 0.0;
            cur = cur->parent >= 0 && mem.count((uint32_t)cur->parent)
                      ? mem.at((uint32_t)cur->parent) : nullptr;
        }
        worst = std::max(worst, t);
    }
    return worst;
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
