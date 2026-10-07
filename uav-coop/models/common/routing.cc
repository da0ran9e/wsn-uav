#include "routing.h"

#include <algorithm>
#include <cmath>
#include <deque>
#include <queue>
#include <set>
#include <tuple>

namespace ns3::uavcoop {

namespace {

struct Cost {
    uint32_t hops = kNoRoute;
    double metres = 0;
    bool operator<(const Cost& o) const {
        if (hops != o.hops) return hops < o.hops;
        return metres < o.metres - 1e-9;
    }
};

double Dist(const SensorNode& a, const SensorNode& b) {
    return std::hypot(a.pos.x - b.pos.x, a.pos.y - b.pos.y);
}

// Shortest routes from every allowed node to the nearest of `targets`, over links
// between allowed nodes. next[v]: the next hop from v toward the targets; entry[v]:
// the target it ends at. Ties: lower predecessor index.
void Search(const std::vector<SensorNode>& nodes, const std::vector<std::vector<int32_t>>& links,
            const std::vector<char>& allowed, const std::vector<int32_t>& targets,
            std::vector<Cost>& cost, std::vector<int32_t>& next, std::vector<int32_t>& entry) {
    using Item = std::tuple<uint32_t, double, int32_t>;   // hops, metres, node
    std::priority_queue<Item, std::vector<Item>, std::greater<Item>> pq;
    for (int32_t t : targets) {
        cost[t] = {0, 0.0};
        next[t] = kNoHop;
        entry[t] = t;
        pq.push({0, 0.0, t});
    }
    std::vector<char> done(nodes.size(), 0);
    while (!pq.empty()) {
        const auto [h, m, u] = pq.top();
        pq.pop();
        if (done[u]) continue;
        done[u] = 1;
        for (int32_t v : links[u]) {
            if (!allowed[v] || done[v]) continue;
            const Cost c{h + 1, m + Dist(nodes[u], nodes[v])};
            const bool tie = !(c < cost[v]) && !(cost[v] < c);
            if (c < cost[v] || (tie && u < next[v])) {
                cost[v] = c;
                next[v] = u;
                entry[v] = entry[u];
                pq.push({c.hops, c.metres, v});
            }
        }
    }
}

}  // namespace

Routing BuildRouting(const std::vector<SensorNode>& nodes, size_t ch, double range) {
    const size_t n = nodes.size();
    Routing R;
    R.links.assign(n, {});
    R.table.assign(n, {});
    // Links, by bucketing into range x range squares.
    std::map<std::pair<int64_t, int64_t>, std::vector<int32_t>> bucket;
    auto key = [&](const Point& p) {
        return std::make_pair((int64_t)std::floor(p.x / range), (int64_t)std::floor(p.y / range));
    };
    for (size_t i = 0; i < n; ++i) bucket[key(nodes[i].pos)].push_back((int32_t)i);
    for (size_t i = 0; i < n; ++i) {
        const auto [bx, by] = key(nodes[i].pos);
        for (int64_t dx = -1; dx <= 1; ++dx)
            for (int64_t dy = -1; dy <= 1; ++dy) {
                auto it = bucket.find({bx + dx, by + dy});
                if (it == bucket.end()) continue;
                for (int32_t j : it->second)
                    if ((size_t)j != i && Dist(nodes[i], nodes[j]) <= range) R.links[i].push_back(j);
            }
        std::sort(R.links[i].begin(), R.links[i].end());
    }

    std::map<Hex, std::vector<int32_t>> members;
    std::map<Hex, int32_t> cl;
    for (size_t i = 0; i < n; ++i) {
        members[nodes[i].cell].push_back((int32_t)i);
        if (nodes[i].isCL) cl[nodes[i].cell] = (int32_t)i;
    }

    std::vector<Cost> cost(n);
    std::vector<int32_t> next(n), entry(n);
    std::vector<char> allowed(n, 0);
    auto reset = [&] {
        std::fill(cost.begin(), cost.end(), Cost{});
        std::fill(next.begin(), next.end(), kNoHop);
        std::fill(entry.begin(), entry.end(), kNoHop);
        std::fill(allowed.begin(), allowed.end(), 0);
    };
    auto store = [&](int32_t v, CellHop& h) {
        if (cost[v].hops == kNoRoute) return;
        h.next = next[v];
        h.hops = cost[v].hops;
        h.metres = cost[v].metres;
        h.entry = entry[v];
    };

    for (const auto& [A, mem] : members) {
        // toCL: inside the cell.
        reset();
        for (int32_t v : mem) allowed[v] = 1;
        Search(nodes, R.links, allowed, {cl.at(A)}, cost, next, entry);
        for (int32_t v : mem) store(v, R.table[v].toCL);
        // toCell[B]: inside A and B, for every adjacent cell B that has nodes.
        for (const Hex& B : HexGrid::Neighbours(A)) {
            auto it = members.find(B);
            if (it == members.end()) continue;
            reset();
            for (int32_t v : mem) allowed[v] = 1;
            for (int32_t v : it->second) allowed[v] = 1;
            Search(nodes, R.links, allowed, it->second, cost, next, entry);
            for (int32_t v : mem) store(v, R.table[v].toCell[B]);
        }
    }

    // Main route: shortest route to the CH when every node may only forward along one
    // of its own stored next hops (toCL or a toCell). Dijkstra from the CH backwards
    // over those edges; each node's main next hop is the stored one on its shortest.
    std::vector<Cost> D(n);
    std::vector<std::vector<std::pair<int32_t, int32_t>>> back(n);   // next -> (v, choice)
    std::vector<std::vector<std::pair<int32_t, Hex>>> choice(n);     // v: (next, cell or CL)
    for (size_t v = 0; v < n; ++v) {
        const RouteTable& t = R.table[v];
        if (t.toCL.next != kNoHop) choice[v].push_back({t.toCL.next, nodes[v].cell});
        for (const auto& [B, h] : t.toCell)
            if (h.next != kNoHop) choice[v].push_back({h.next, B});
        for (size_t c = 0; c < choice[v].size(); ++c)
            back[choice[v][c].first].push_back({(int32_t)v, (int32_t)c});
    }
    using Item = std::tuple<uint32_t, double, int32_t>;
    std::priority_queue<Item, std::vector<Item>, std::greater<Item>> pq;
    D[ch] = {0, 0.0};
    pq.push({0, 0.0, (int32_t)ch});
    std::vector<char> done(n, 0);
    while (!pq.empty()) {
        const auto [hh, mm, u] = pq.top();
        pq.pop();
        if (done[u]) continue;
        done[u] = 1;
        for (const auto& [v, c] : back[u]) {
            if (done[v]) continue;
            const Cost cc{hh + 1, mm + Dist(nodes[u], nodes[v])};
            if (cc < D[v]) {
                D[v] = cc;
                R.table[v].mainNext = u;
                R.table[v].mainViaCL = choice[v][c].second == nodes[v].cell;
                R.table[v].mainCell = choice[v][c].second;
                pq.push({cc.hops, cc.metres, v});
            }
        }
    }
    for (size_t v = 0; v < n; ++v) {
        R.table[v].hopsToCH = D[v].hops;
        R.table[v].metresToCH = D[v].hops == kNoRoute ? 0 : D[v].metres;
    }
    return R;
}

std::vector<uint32_t> FreeHops(const Routing& r, size_t to) {
    std::vector<uint32_t> h(r.links.size(), kNoRoute);
    std::deque<size_t> q{to};
    h[to] = 0;
    while (!q.empty()) {
        const size_t u = q.front();
        q.pop_front();
        for (int32_t v : r.links[u])
            if (h[v] == kNoRoute) { h[v] = h[u] + 1; q.push_back(v); }
    }
    return h;
}

}  // namespace ns3::uavcoop
