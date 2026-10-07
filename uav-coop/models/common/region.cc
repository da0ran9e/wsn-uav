#include "region.h"

#include <algorithm>
#include <cmath>
#include <deque>

namespace ns3::uavcoop {

Region GrowRegion(uint32_t nCells, const Hex& seed, CoopRng& rng) {
    Region reg;
    std::unordered_set<Hex, HexHash> in, onFrontier;
    std::vector<Hex> frontier;
    auto add = [&](const Hex& h) {
        reg.cells.push_back(h);
        in.insert(h);
        for (const Hex& n : HexGrid::Neighbours(h))
            if (!in.count(n) && !onFrontier.count(n)) {
                onFrontier.insert(n);
                frontier.push_back(n);
            }
    };
    reg.frontierSize.push_back(0);
    add(seed);
    while (reg.cells.size() < nCells) {
        reg.frontierSize.push_back((uint32_t)frontier.size());
        const uint64_t k = rng.Below(frontier.size());
        const Hex h = frontier[k];
        frontier[k] = frontier.back();     // O(1) removal; order of the rest is irrelevant
        frontier.pop_back();
        onFrontier.erase(h);
        add(h);
    }
    reg.nGrown = (uint32_t)reg.cells.size();
    return reg;
}

std::vector<Hex> HullCells(const HexGrid& g, const std::vector<Hex>& cells) {
    std::vector<Point> pts;
    for (const Hex& h : cells) pts.push_back(g.Centre(h));
    if (pts.size() < 3) return cells;
    std::sort(pts.begin(), pts.end(), [](const Point& a, const Point& b) {
        return a.x != b.x ? a.x < b.x : a.y < b.y;
    });
    auto cross = [](const Point& o, const Point& a, const Point& b) {
        return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x);
    };
    std::vector<Point> hull;   // Andrew's monotone chain, counter-clockwise
    for (int pass = 0; pass < 2; ++pass) {
        const size_t start = hull.size();
        for (size_t i = 0; i < pts.size(); ++i) {
            const Point& p = pass == 0 ? pts[i] : pts[pts.size() - 1 - i];
            while (hull.size() >= start + 2 && cross(hull[hull.size() - 2], hull.back(), p) <= 0)
                hull.pop_back();
            hull.push_back(p);
        }
        hull.pop_back();
    }
    const double eps = 1e-6 * g.Width();
    auto inside = [&](const Point& p) {
        for (size_t i = 0; i < hull.size(); ++i)
            if (cross(hull[i], hull[(i + 1) % hull.size()], p) < -eps * g.Width()) return false;
        return true;
    };
    // Axial coordinates are linear in position, so every lattice point in the hull
    // lies in the axial box of the cells.
    int32_t qmin = 1 << 30, qmax = -(1 << 30), rmin = 1 << 30, rmax = -(1 << 30);
    for (const Hex& h : cells) {
        qmin = std::min(qmin, h.q); qmax = std::max(qmax, h.q);
        rmin = std::min(rmin, h.r); rmax = std::max(rmax, h.r);
    }
    std::vector<Hex> out;
    for (int32_t q = qmin; q <= qmax; ++q)
        for (int32_t r = rmin; r <= rmax; ++r)
            if (inside(g.Centre({q, r}))) out.push_back({q, r});
    return out;
}

double Convexity(const HexGrid& g, const std::vector<Hex>& cells) {
    return (double)cells.size() / (double)HullCells(g, cells).size();
}

Region MakeRegion(const HexGrid& g, uint32_t nCells, double kappa, CoopRng& rng) {
    Region reg = GrowRegion(nCells, {0, 0}, rng);
    const std::vector<Hex> hull = HullCells(g, reg.cells);
    reg.rawConvexity = (double)reg.cells.size() / hull.size();
    const size_t target = (size_t)std::ceil(kappa * hull.size() - 1e-9);
    std::unordered_set<Hex, HexHash> in(reg.cells.begin(), reg.cells.end());
    std::vector<Hex> todo;   // the concavities
    for (const Hex& h : hull)
        if (!in.count(h)) todo.push_back(h);
    while (reg.cells.size() < target && !todo.empty()) {
        // The concave cell most enclosed by the region; ties at random.
        int best = -1;
        std::vector<size_t> tied;
        for (size_t i = 0; i < todo.size(); ++i) {
            int k = 0;
            for (const Hex& n : HexGrid::Neighbours(todo[i])) k += in.count(n) ? 1 : 0;
            if (k > best) { best = k; tied.clear(); }
            if (k == best) tied.push_back(i);
        }
        const size_t pick = tied[rng.Below(tied.size())];
        reg.cells.push_back(todo[pick]);
        in.insert(todo[pick]);
        todo[pick] = todo.back();
        todo.pop_back();
    }
    reg.convexity = (double)reg.cells.size() / hull.size();
    return reg;
}

std::vector<Hex> Holes(const Region& reg) {
    std::unordered_set<Hex, HexHash> in(reg.cells.begin(), reg.cells.end());
    int32_t qmin = 1 << 30, qmax = -(1 << 30), rmin = 1 << 30, rmax = -(1 << 30);
    for (const Hex& h : reg.cells) {
        qmin = std::min(qmin, h.q); qmax = std::max(qmax, h.q);
        rmin = std::min(rmin, h.r); rmax = std::max(rmax, h.r);
    }
    // Flood the outside from a box one cell larger than the region.
    auto inBox = [&](const Hex& h) {
        return h.q >= qmin - 1 && h.q <= qmax + 1 && h.r >= rmin - 1 && h.r <= rmax + 1;
    };
    std::unordered_set<Hex, HexHash> outside;
    std::deque<Hex> todo{{qmin - 1, rmin - 1}};
    outside.insert(todo.front());
    while (!todo.empty()) {
        const Hex h = todo.front();
        todo.pop_front();
        for (const Hex& n : HexGrid::Neighbours(h))
            if (inBox(n) && !in.count(n) && !outside.count(n)) {
                outside.insert(n);
                todo.push_back(n);
            }
    }
    std::vector<Hex> holes;
    for (int32_t q = qmin; q <= qmax; ++q)
        for (int32_t r = rmin; r <= rmax; ++r) {
            const Hex h{q, r};
            if (!in.count(h) && !outside.count(h)) holes.push_back(h);
        }
    return holes;
}

bool IsConnected(const std::vector<Hex>& cells) {
    if (cells.empty()) return true;
    std::unordered_set<Hex, HexHash> in(cells.begin(), cells.end()), seen{cells[0]};
    std::deque<Hex> todo{cells[0]};
    while (!todo.empty()) {
        const Hex h = todo.front();
        todo.pop_front();
        for (const Hex& n : HexGrid::Neighbours(h))
            if (in.count(n) && !seen.count(n)) {
                seen.insert(n);
                todo.push_back(n);
            }
    }
    return seen.size() == in.size();
}

}  // namespace ns3::uavcoop
