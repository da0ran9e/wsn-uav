#include "cell-grid.h"

#include <algorithm>
#include <cmath>
#include <limits>
#include <queue>

namespace ns3::uavsar {

namespace hex {

// Pointy-top axial coordinates (redblobgames convention), size = circumradius.
void WorldToAxial(double x, double y, double size, int32_t& q, int32_t& r) {
    double fq = (std::sqrt(3.0) / 3.0 * x - 1.0 / 3.0 * y) / size;
    double fr = (2.0 / 3.0 * y) / size;
    // cube rounding to keep q + r + s == 0
    double fs = -fq - fr;
    int32_t rq = (int32_t)std::lround(fq);
    int32_t rr = (int32_t)std::lround(fr);
    int32_t rs = (int32_t)std::lround(fs);
    double dq = std::fabs(rq - fq), dr = std::fabs(rr - fr), ds = std::fabs(rs - fs);
    if (dq > dr && dq > ds) rq = -rr - rs;
    else if (dr > ds)       rr = -rq - rs;
    q = rq;
    r = rr;
}

void AxialToCenter(int32_t q, int32_t r, double size, double& cx, double& cy) {
    cx = size * (std::sqrt(3.0) * q + std::sqrt(3.0) / 2.0 * r);
    cy = size * (1.5 * r);
}

}  // namespace hex

namespace {
double Dist(double ax, double ay, double bx, double by) {
    double dx = ax - bx, dy = ay - by;
    return std::sqrt(dx * dx + dy * dy);
}
}  // namespace

CellGridPlan BuildCellGrid(const std::vector<NodePos>& in, const CellGridConfig& cfg) {
    CellGridPlan plan;
    plan.config = cfg;

    // 1) assign each node to a hex cell; allocate sequential cell ids.
    std::map<std::pair<int32_t, int32_t>, int32_t> idByQR;
    int32_t nextCell = 0;
    for (const auto& np : in) {
        CellNodeInfo info;
        info.id = np.id;
        info.x = np.x;
        info.y = np.y;
        int32_t q, r;
        hex::WorldToAxial(np.x, np.y, cfg.cellRadius, q, r);
        auto key = std::make_pair(q, r);
        auto [it, inserted] = idByQR.emplace(key, nextCell);
        if (inserted) {
            nextCell++;
            CellInfo c;
            c.cellId = it->second;
            c.q = q;
            c.r = r;
            hex::AxialToCenter(q, r, cfg.cellRadius, c.centerX, c.centerY);
            plan.cells.emplace(c.cellId, c);
        }
        info.cellId = it->second;
        plan.cells[info.cellId].members.push_back(np.id);
        plan.nodes.emplace(np.id, std::move(info));
    }

    // 2) neighbor graph within neighborRange (O(n^2); fine for sim sizes).
    for (auto a = plan.nodes.begin(); a != plan.nodes.end(); ++a) {
        auto b = a;
        for (++b; b != plan.nodes.end(); ++b) {
            if (Dist(a->second.x, a->second.y, b->second.x, b->second.y) <= cfg.neighborRange) {
                a->second.neighbors.insert(b->first);
                b->second.neighbors.insert(a->first);
            }
        }
    }

    // 3) elect leader = member closest to cell centroid (tie -> lowest id).
    for (auto& [cellId, cell] : plan.cells) {
        if (cell.members.empty()) continue;
        double sx = 0, sy = 0;
        for (uint32_t m : cell.members) { sx += plan.nodes[m].x; sy += plan.nodes[m].y; }
        double gx = sx / cell.members.size(), gy = sy / cell.members.size();
        uint32_t leader = cell.members.front();
        double best = std::numeric_limits<double>::max();
        for (uint32_t m : cell.members) {
            double d = Dist(plan.nodes[m].x, plan.nodes[m].y, gx, gy);
            if (d < best - 1e-9 || (std::fabs(d - best) <= 1e-9 && m < leader)) {
                best = d;
                leader = m;
            }
        }
        cell.leaderId = leader;
        for (uint32_t m : cell.members) {
            plan.nodes[m].leaderId = leader;
            plan.nodes[m].isLeader = (m == leader);
        }
    }

    // 4) intra-cell routing tree: BFS from leader over in-cell neighbor links.
    for (auto& [cellId, cell] : plan.cells) {
        uint32_t leader = cell.leaderId;
        if (cell.members.empty()) continue;
        plan.nodes[leader].hopToLeader = 0;
        plan.nodes[leader].parentId = -1;
        std::queue<uint32_t> bfs;
        bfs.push(leader);
        while (!bfs.empty()) {
            uint32_t cur = bfs.front();
            bfs.pop();
            uint32_t nh = plan.nodes[cur].hopToLeader + 1;
            for (uint32_t nb : plan.nodes[cur].neighbors) {
                auto it = plan.nodes.find(nb);
                if (it == plan.nodes.end() || it->second.cellId != cellId) continue;
                if (it->second.hopToLeader <= nh) continue;
                it->second.hopToLeader = nh;
                it->second.parentId = (int32_t)cur;
                bfs.push(nb);
            }
        }
    }

    // 5) cell adjacency (radio-based): cells sharing a cross-cell neighbor link.
    for (const auto& [id, info] : plan.nodes) {
        for (uint32_t nb : info.neighbors) {
            int32_t other = plan.nodes[nb].cellId;
            if (other != info.cellId) {
                plan.cells[info.cellId].adjacentCells.insert(other);
                plan.cells[other].adjacentCells.insert(info.cellId);
            }
        }
    }

    // 6) greedy coloring over the cell-adjacency graph (adjacent cells differ).
    uint32_t maxColor = 0;
    for (auto& [cellId, cell] : plan.cells) {
        std::set<uint32_t> used;
        for (int32_t adj : cell.adjacentCells) {
            // colors already assigned to lower-processed neighbors
            auto it = plan.cells.find(adj);
            if (it != plan.cells.end() && it->first < cellId) used.insert(it->second.color);
        }
        uint32_t c = 0;
        while (used.count(c)) c++;
        cell.color = c;
        maxColor = std::max(maxColor, c);
        for (uint32_t m : cell.members) plan.nodes[m].cellColor = c;
    }
    plan.colorCount = plan.cells.empty() ? 0 : maxColor + 1;

    return plan;
}

}  // namespace ns3::uavsar
