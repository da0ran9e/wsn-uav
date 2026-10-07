#include "region.h"

#include <algorithm>
#include <cmath>
#include <deque>
#include <unordered_set>

namespace ns3::uavcoop {

Region GrowRegion(uint32_t nCells, const Hex& seed, CoopRng& rng,
                  const std::unordered_set<Hex, HexHash>* allowed) {
    Region reg;
    std::unordered_set<Hex, HexHash> in, onFrontier;
    std::vector<Hex> frontier;
    auto add = [&](const Hex& h) {
        reg.cells.push_back(h);
        in.insert(h);
        for (const Hex& n : HexGrid::Neighbours(h))
            if (!in.count(n) && !onFrontier.count(n) && (!allowed || allowed->count(n))) {
                onFrontier.insert(n);
                frontier.push_back(n);
            }
    };
    reg.frontierSize.push_back(0);
    add(seed);
    while (reg.cells.size() < nCells && !frontier.empty()) {
        reg.frontierSize.push_back((uint32_t)frontier.size());
        const uint64_t k = rng.Below(frontier.size());
        const Hex h = frontier[k];
        frontier[k] = frontier.back();     // O(1) removal; order of the rest is irrelevant
        frontier.pop_back();
        onFrontier.erase(h);
        add(h);
    }
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

namespace ns3::uavcoop {

Region MakeRegion(const HexGrid& g, uint32_t nCells, double convexity, double maxAspect,
                  CoopRng& rng) {
    const Hex origin{0, 0};
    if (convexity <= 0.0) return GrowRegion(nCells, origin, rng);   // free, as in step 1

    const double aspect = rng.Uniform(1.0, maxAspect);
    const double theta = rng.Uniform(0.0, M_PI);
    const uint32_t m = (uint32_t)std::lround(nCells / std::min(1.0, convexity));
    // Candidate window: far enough for an ellipse of m cells at the largest aspect.
    const int32_t K = (int32_t)std::ceil(2.0 * std::sqrt((double)m) * std::sqrt(maxAspect)) + 3;
    struct Cand { double d2; Hex h; };
    std::vector<Cand> cand;
    const double c = std::cos(theta), s = std::sin(theta);
    for (int32_t q = -K; q <= K; ++q)
        for (int32_t r = -K; r <= K; ++r) {
            const Hex h{q, r};
            if (HexGrid::Distance(origin, h) > K) continue;
            const Point p = g.Centre(h);
            const double u = p.x * c + p.y * s, v = -p.x * s + p.y * c;
            cand.push_back({u * u / aspect + v * v * aspect, h});
        }
    std::sort(cand.begin(), cand.end(), [](const Cand& a, const Cand& b) {
        return a.d2 != b.d2 ? a.d2 < b.d2 : a.h < b.h;
    });
    Region reg;
    reg.aspect = aspect;
    reg.thetaRad = theta;
    for (uint32_t i = 0; i < m; ++i) reg.envelope.push_back(cand[i].h);

    if (m == nCells) {
        // Fully convex: the region is the envelope, listed from the centre outwards.
        reg.cells = reg.envelope;
        reg.frontierSize.assign(nCells, 0);
        return reg;
    }
    std::unordered_set<Hex, HexHash> allowed(reg.envelope.begin(), reg.envelope.end());
    Region grown = GrowRegion(nCells, origin, rng, &allowed);
    grown.envelope = reg.envelope;
    grown.aspect = aspect;
    grown.thetaRad = theta;
    return grown;
}

double Convexity(const HexGrid& g, const std::vector<Hex>& cells) {
    // Convex hull of the centres (Andrew's monotone chain).
    std::vector<Point> pts;
    for (const Hex& h : cells) pts.push_back(g.Centre(h));
    std::sort(pts.begin(), pts.end(), [](const Point& a, const Point& b) {
        return a.x != b.x ? a.x < b.x : a.y < b.y;
    });
    auto cross = [](const Point& o, const Point& a, const Point& b) {
        return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x);
    };
    std::vector<Point> hull;
    if (pts.size() < 3) return 1.0;
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
            if (cross(hull[i], hull[(i + 1) % hull.size()], p) < -eps) return false;
        return true;
    };
    int32_t qmin = 1 << 30, qmax = -(1 << 30), rmin = 1 << 30, rmax = -(1 << 30);
    for (const Hex& h : cells) {
        qmin = std::min(qmin, h.q); qmax = std::max(qmax, h.q);
        rmin = std::min(rmin, h.r); rmax = std::max(rmax, h.r);
    }
    uint64_t inHull = 0;
    for (int32_t q = qmin - 1; q <= qmax + 1; ++q)
        for (int32_t r = rmin - 1; r <= rmax + 1; ++r)
            if (inside(g.Centre({q, r}))) inHull++;
    return (double)cells.size() / (double)inHull;
}

}  // namespace ns3::uavcoop
