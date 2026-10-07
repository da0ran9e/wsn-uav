#include "region.h"

#include <algorithm>
#include <deque>
#include <unordered_set>

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
