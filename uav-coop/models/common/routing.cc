#include "routing.h"

#include <algorithm>
#include <cmath>
#include <deque>
#include <functional>
#include <queue>
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

void AddLink(std::vector<std::vector<int32_t>>& links, int32_t a, int32_t b) {
    links[a].insert(std::upper_bound(links[a].begin(), links[a].end(), b), b);
    links[b].insert(std::upper_bound(links[b].begin(), links[b].end(), a), a);
}

// Shortest routes (hops, then metres) from every node of `in` to `target`, over links
// between nodes of `in`. next[v]: the next hop from v toward the target. Ties: lower
// predecessor index.
void Search(const std::vector<SensorNode>& nodes, const std::vector<std::vector<int32_t>>& links,
            const std::vector<char>& in, int32_t target, std::vector<Cost>& cost,
            std::vector<int32_t>& next) {
    using Item = std::tuple<uint32_t, double, int32_t>;
    std::priority_queue<Item, std::vector<Item>, std::greater<Item>> pq;
    cost[target] = {0, 0.0};
    next[target] = kNoHop;
    pq.push({0, 0.0, target});
    std::vector<char> done(nodes.size(), 0);
    while (!pq.empty()) {
        const auto [h, m, u] = pq.top();
        pq.pop();
        if (done[u]) continue;
        done[u] = 1;
        for (int32_t v : links[u]) {
            if (!in[v] || done[v]) continue;
            const Cost c{h + 1, m + Dist(nodes[u], nodes[v])};
            const bool tie = !(c < cost[v]) && !(cost[v] < c);
            if (c < cost[v] || (tie && u < next[v])) {
                cost[v] = c;
                next[v] = u;
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
    // ---- links in range, by bucketing into range x range squares ------------
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

    // ---- every cell in one piece: join its components by the shortest links ----
    // Kruskal over all in-cell pairs, starting from the in-range components.
    for (const auto& [A, mem] : members) {
        std::map<int32_t, int32_t> parent;
        for (int32_t v : mem) parent[v] = v;
        std::function<int32_t(int32_t)> find = [&](int32_t v) {
            return parent[v] == v ? v : parent[v] = find(parent[v]);
        };
        for (int32_t u : mem)
            for (int32_t v : R.links[u])
                if (nodes[v].cell == A) parent[find(u)] = find(v);
        std::vector<std::tuple<double, int32_t, int32_t>> pairs;
        for (size_t x = 0; x < mem.size(); ++x)
            for (size_t y = x + 1; y < mem.size(); ++y)
                if (find(mem[x]) != find(mem[y]))
                    pairs.push_back({Dist(nodes[mem[x]], nodes[mem[y]]), mem[x], mem[y]});
        std::sort(pairs.begin(), pairs.end());
        for (const auto& [d, u, v] : pairs) {
            if (find(u) == find(v)) continue;
            parent[find(u)] = find(v);
            AddLink(R.links, u, v);
            R.bridges.push_back({u, v, d, false});
        }
    }

    // ---- toCL, inside the cell ------------------------------------------------
    std::vector<Cost> cost(n);
    std::vector<int32_t> next(n);
    std::vector<char> in(n, 0);
    auto inCell = [&](const std::vector<int32_t>& mem) {
        std::fill(cost.begin(), cost.end(), Cost{});
        std::fill(next.begin(), next.end(), kNoHop);
        std::fill(in.begin(), in.end(), 0);
        for (int32_t v : mem) in[v] = 1;
    };
    for (const auto& [A, mem] : members) {
        inCell(mem);
        Search(nodes, R.links, in, cl.at(A), cost, next);
        for (int32_t v : mem) R.table[v].toCL = {next[v], cost[v].hops, cost[v].metres};
    }

    // ---- one gateway per pair of adjacent cells -------------------------------
    for (const auto& [A, memA] : members)
        for (const Hex& B : HexGrid::Neighbours(A)) {
            if (!(A < B) || !members.count(B)) continue;
            const std::vector<int32_t>& memB = members.at(B);
            Gateway best;
            std::tuple<uint32_t, double, int32_t, int32_t> bestKey{kNoRoute, 0, 0, 0};
            double nearest = 1e18;
            int32_t na = kNoHop, nb = kNoHop;
            for (int32_t a : memA)
                for (int32_t b : memB) {
                    const double d = Dist(nodes[a], nodes[b]);
                    if (d < nearest) { nearest = d; na = a; nb = b; }
                    if (d > range) continue;
                    const auto k = std::make_tuple(R.table[a].toCL.hops + R.table[b].toCL.hops, d, a, b);
                    if (best.a == kNoHop || k < bestKey) { bestKey = k; best = {a, b, d, false}; }
                }
            if (best.a == kNoHop) {   // no cross link in range: bridge the nearest pair
                best = {na, nb, nearest, true};
                AddLink(R.links, na, nb);
                R.bridges.push_back({na, nb, nearest, true});
            }
            R.gateway[{A, B}] = best;
            R.gateway[{B, A}] = {best.b, best.a, best.metres, best.bridge};
        }

    // ---- toCell[B]: inside the cell to the gateway a, then a -> b -------------
    for (const auto& [A, mem] : members)
        for (const Hex& B : HexGrid::Neighbours(A)) {
            auto g = R.gateway.find({A, B});
            if (g == R.gateway.end()) continue;
            inCell(mem);
            Search(nodes, R.links, in, g->second.a, cost, next);
            for (int32_t v : mem) {
                CellHop& h = R.table[v].toCell[B];
                h.hops = cost[v].hops + 1;
                h.metres = cost[v].metres + g->second.metres;
                h.next = v == g->second.a ? g->second.b : next[v];
            }
        }

    // ---- main route: shortest to the CH over each node's own stored next hops ----
    // Dijkstra from the CH backwards over those edges.
    std::vector<Cost> D(n);
    std::vector<std::vector<std::pair<int32_t, int32_t>>> back(n);   // next -> (v, choice)
    std::vector<std::vector<std::pair<int32_t, Hex>>> choice(n);     // v: (next, cell; own = CL)
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
