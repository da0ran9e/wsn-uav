#include "inter-cell-routing.h"

#include <algorithm>
#include <cmath>
#include <map>
#include <queue>

namespace ns3::uavsar {

namespace {
double Dist(const CellNodeInfo& a, const CellNodeInfo& b) {
    double dx = a.x - b.x, dy = a.y - b.y;
    return std::sqrt(dx * dx + dy * dy);
}

// Intra-cell path from node up to its cell leader, following parent pointers.
std::vector<uint32_t> UpToLeader(const CellGridPlan& plan, uint32_t node) {
    std::vector<uint32_t> path;
    int32_t cur = (int32_t)node;
    while (cur >= 0) {
        path.push_back((uint32_t)cur);
        const auto& info = plan.nodes.at((uint32_t)cur);
        if (info.isLeader) break;
        cur = info.parentId;
    }
    return path;  // node ... leader
}
}  // namespace

InterCellRouting BuildInterCellRouting(const CellGridPlan& plan) {
    InterCellRouting r;

    // For each directed adjacent pair (A,B) pick the best bridging node pair:
    // minimize (hopToLeader[a] + hopToLeader[b], crossLinkDist, a, b) so the
    // gateway sits close to both leaders with a short cross-cell hop.
    for (const auto& [cellIdA, cellA] : plan.cells) {
        for (int32_t cellIdB : cellA.adjacentCells) {
            GatewayLink best;
            bool found = false;
            double bestKey1 = 0, bestKey2 = 0;

            for (uint32_t a : cellA.members) {
                const auto& na = plan.nodes.at(a);
                for (uint32_t nb : na.neighbors) {
                    const auto& nbi = plan.nodes.at(nb);
                    if (nbi.cellId != cellIdB) continue;
                    double d = Dist(na, nbi);
                    double hopSum = (double)(na.hopToLeader == 0xFFFFFFFF ? 1e9 : na.hopToLeader)
                                  + (double)(nbi.hopToLeader == 0xFFFFFFFF ? 1e9 : nbi.hopToLeader);
                    bool better =
                        !found ||
                        hopSum < bestKey1 - 1e-9 ||
                        (std::fabs(hopSum - bestKey1) <= 1e-9 && d < bestKey2 - 1e-9) ||
                        (std::fabs(hopSum - bestKey1) <= 1e-9 && std::fabs(d - bestKey2) <= 1e-9 &&
                         (a < best.localGw || (a == best.localGw && nb < best.remoteGw)));
                    if (better) {
                        best.localGw = a;
                        best.remoteGw = nb;
                        best.linkDist = d;
                        bestKey1 = hopSum;
                        bestKey2 = d;
                        found = true;
                    }
                }
            }
            if (found) r.gateway[cellIdA][cellIdB] = best;
        }
    }
    return r;
}

std::vector<int32_t> CellRoute(const CellGridPlan& plan, int32_t srcCell, int32_t dstCell) {
    std::vector<int32_t> path;
    if (plan.cells.find(srcCell) == plan.cells.end() ||
        plan.cells.find(dstCell) == plan.cells.end()) {
        return path;
    }
    if (srcCell == dstCell) { path.push_back(srcCell); return path; }

    std::map<int32_t, int32_t> prev;  // cell -> predecessor cell
    std::queue<int32_t> q;
    q.push(srcCell);
    prev[srcCell] = srcCell;
    bool reached = false;
    while (!q.empty() && !reached) {
        int32_t cur = q.front();
        q.pop();
        for (int32_t nb : plan.cells.at(cur).adjacentCells) {
            if (prev.count(nb)) continue;
            prev[nb] = cur;
            if (nb == dstCell) { reached = true; break; }
            q.push(nb);
        }
    }
    if (!prev.count(dstCell)) return path;  // unreachable

    // reconstruct
    for (int32_t c = dstCell; ; c = prev[c]) {
        path.push_back(c);
        if (c == srcCell) break;
    }
    std::reverse(path.begin(), path.end());
    return path;
}

std::vector<uint32_t> LeaderPath(const CellGridPlan& plan, const InterCellRouting& routing,
                                 int32_t srcCell, int32_t dstCell) {
    std::vector<uint32_t> nodePath;
    std::vector<int32_t> cells = CellRoute(plan, srcCell, dstCell);
    if (cells.empty()) return nodePath;

    auto pushUnique = [&](uint32_t n) {
        if (nodePath.empty() || nodePath.back() != n) nodePath.push_back(n);
    };

    // Start at src leader.
    uint32_t curNode = plan.cells.at(srcCell).leaderId;
    pushUnique(curNode);

    for (size_t i = 0; i + 1 < cells.size(); i++) {
        int32_t A = cells[i], B = cells[i + 1];
        auto itA = routing.gateway.find(A);
        if (itA == routing.gateway.end() || itA->second.find(B) == itA->second.end())
            return {};  // missing gateway -> no path
        const GatewayLink& gl = itA->second.at(B);

        // curNode -> gateway localGw within cell A: go up to leader then down?
        // Our intra tree only encodes child->parent(->leader). Simplest robust
        // path within a cell: curNode -> leader(A) -> localGw via reversed
        // up-paths (leader is common ancestor).
        std::vector<uint32_t> upCur = UpToLeader(plan, curNode);      // curNode..leaderA
        std::vector<uint32_t> upGw = UpToLeader(plan, gl.localGw);    // localGw..leaderA
        for (uint32_t n : upCur) pushUnique(n);                       // to leaderA
        for (auto it = upGw.rbegin(); it != upGw.rend(); ++it) pushUnique(*it); // leaderA down to localGw
        pushUnique(gl.remoteGw);                                      // cross-cell hop
        curNode = gl.remoteGw;                                        // now in cell B
    }

    // Finally curNode (in dstCell) -> leader(dstCell).
    std::vector<uint32_t> up = UpToLeader(plan, curNode);
    for (uint32_t n : up) pushUnique(n);
    return nodePath;
}

}  // namespace ns3::uavsar
