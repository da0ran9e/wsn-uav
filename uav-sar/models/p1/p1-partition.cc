#include "p1-partition.h"

#include "p1-dubins.h"

#include <algorithm>
#include <cmath>
#include <limits>
#include <set>

namespace ns3::uavsar::p1 {

namespace {

std::vector<int32_t> NearestNeighbour(const std::vector<int32_t>& cells,
                                      const std::map<int32_t, Demand>& demands,
                                      const Depot& depot) {
    std::vector<int32_t> left = cells, out;
    double cx = depot.x, cy = depot.y;
    while (!left.empty()) {
        size_t best = 0;
        double bd = std::numeric_limits<double>::infinity();
        for (size_t i = 0; i < left.size(); ++i) {
            const Demand& d = demands.at(left[i]);
            const double dd = std::hypot(d.x - cx, d.y - cy);
            if (dd < bd) { bd = dd; best = i; }
        }
        out.push_back(left[best]);
        cx = demands.at(left[best]).x;
        cy = demands.at(left[best]).y;
        left.erase(left.begin() + best);
    }
    return out;
}

// Euclidean length of a fixed order, WITH both depot legs.
double EuclidM(const std::vector<int32_t>& order,
               const std::map<int32_t, Demand>& demands, const Depot& depot) {
    if (order.empty()) return 0.0;
    double m = 0.0, px = depot.x, py = depot.y;
    for (int32_t c : order) {
        const Demand& d = demands.at(c);
        m += std::hypot(d.x - px, d.y - py);
        px = d.x; py = d.y;
    }
    return m + std::hypot(depot.x - px, depot.y - py);
}

void Score(Partition& p) {
    double mx = 0, mn = std::numeric_limits<double>::infinity();
    for (const Block& b : p.vehicles) {
        mx = std::max(mx, b.TotalS());
        mn = std::min(mn, b.TotalS());
    }
    p.makespanS = mx;
    p.imbalancePct = mx > 0 ? 100.0 * (mx - mn) / mx : 0.0;
}

}  // namespace

Block EstimateBlock(const std::vector<int32_t>& cells,
                    const std::map<int32_t, Demand>& demands, const Depot& depot) {
    Block b;
    b.cells = NearestNeighbour(cells, demands, depot);
    b.travelS = EuclidM(b.cells, demands, depot) / kCruiseMps;
    for (int32_t c : b.cells) b.serviceS += demands.at(c).penaltyS;
    return b;
}

double DubinsTravelS(const Block& b, const std::map<int32_t, Demand>& demands,
                     const Depot& depot, double R) {
    if (b.cells.empty()) return 0.0;
    auto hdg = [](double fx, double fy, double tx, double ty) {
        return std::atan2(ty - fy, tx - fx);
    };
    std::vector<Config> pts{Config{depot.x, depot.y, 0.0}};
    for (size_t i = 0; i < b.cells.size(); ++i) {
        const Demand& d = demands.at(b.cells[i]);
        const double px = i ? demands.at(b.cells[i - 1]).x : depot.x;
        const double py = i ? demands.at(b.cells[i - 1]).y : depot.y;
        const double nx = i + 1 < b.cells.size() ? demands.at(b.cells[i + 1]).x : depot.x;
        const double ny = i + 1 < b.cells.size() ? demands.at(b.cells[i + 1]).y : depot.y;
        // heading through the head: the bisector of arrive and leave
        const double h1 = hdg(px, py, d.x, d.y), h2 = hdg(d.x, d.y, nx, ny);
        pts.push_back({d.x, d.y, std::atan2(std::sin(h1) + std::sin(h2),
                                            std::cos(h1) + std::cos(h2))});
    }
    pts.push_back({depot.x, depot.y, 0.0});
    double m = 0.0;
    for (size_t i = 0; i + 1 < pts.size(); ++i) m += DubinsLength(pts[i], pts[i + 1], R);
    return m / kCruiseMps;
}

// ---------------------------------------------------------------------------
// CREDIT
// ---------------------------------------------------------------------------
Partition PartitionCredit(const std::map<int32_t, Demand>& demands,
                          const CellPlan& plan, const Depot& depot,
                          uint32_t vehicles, bool contiguous) {
    Partition p;
    p.method = "credit";
    p.contiguous = contiguous;
    if (vehicles == 0) return p;

    std::vector<int32_t> todo;
    for (const auto& [cid, d] : demands)
        if (d.theta > 0.0) todo.push_back(cid);
    p.vehicles.resize(vehicles);
    if (todo.empty()) return p;

    // Seeds: sort by angle about the depot and take M evenly spaced. Every
    // classical partitioner separates vehicles by their START POINTS and
    // degenerates when they share one; the seeds stand in for that separation.
    std::sort(todo.begin(), todo.end(), [&](int32_t a, int32_t b) {
        const Demand& da = demands.at(a);
        const Demand& db = demands.at(b);
        return std::atan2(da.y - depot.y, da.x - depot.x) <
               std::atan2(db.y - depot.y, db.x - depot.x);
    });

    std::map<int32_t, int32_t> owner;
    std::vector<std::vector<int32_t>> own(vehicles);
    for (uint32_t v = 0; v < vehicles; ++v) {
        const size_t k = todo.size() * v / vehicles;
        owner[todo[k]] = (int32_t)v;
        own[v].push_back(todo[k]);
    }

    auto adjacent = [&](int32_t a, int32_t b) {
        const Cell& ca = plan.cells.at(a);
        const Cell& cb = plan.cells.at(b);
        const int dq = cb.q - ca.q, dr = cb.r - ca.r;
        return (dq == 1 && dr == 0) || (dq == -1 && dr == 0) ||
               (dq == 0 && dr == 1) || (dq == 0 && dr == -1) ||
               (dq == 1 && dr == -1) || (dq == -1 && dr == 1);
    };

    // Grow: the account with the most budget left (least work taken) buys next,
    // and it buys the cell that costs IT least. Cost is measured on the WHOLE
    // block, so the detour a cell forces is charged to whoever accepts it.
    size_t placed = vehicles;
    while (placed < todo.size()) {
        uint32_t v = 0;
        double least = std::numeric_limits<double>::infinity();
        std::vector<double> cur(vehicles, 0.0);
        for (uint32_t k = 0; k < vehicles; ++k) {
            cur[k] = EstimateBlock(own[k], demands, depot).TotalS();
            if (cur[k] < least) { least = cur[k]; v = k; }
        }
        int32_t pick = -1;
        double bestDelta = std::numeric_limits<double>::infinity();
        for (int32_t cid : todo) {
            if (owner.count(cid)) continue;
            if (contiguous) {
                bool touches = false;
                for (int32_t mine : own[v]) if (adjacent(mine, cid)) { touches = true; break; }
                if (!touches) continue;
            }
            std::vector<int32_t> trial = own[v];
            trial.push_back(cid);
            const double delta = EstimateBlock(trial, demands, depot).TotalS() - cur[v];
            if (delta < bestDelta) { bestDelta = delta; pick = cid; }
        }
        if (pick < 0) {                 // contiguity blocked every choice
            for (int32_t cid : todo)
                if (!owner.count(cid)) { pick = cid; break; }
            if (pick < 0) break;
        }
        owner[pick] = (int32_t)v;
        own[v].push_back(pick);
        placed++;
    }

    // Trade: the busiest gives a cell to the least busy, while that strictly
    // reduces the makespan.
    for (int iter = 0; iter < 200; ++iter) {
        std::vector<double> cur(vehicles);
        for (uint32_t k = 0; k < vehicles; ++k)
            cur[k] = EstimateBlock(own[k], demands, depot).TotalS();
        const size_t hi = std::max_element(cur.begin(), cur.end()) - cur.begin();
        const size_t lo = std::min_element(cur.begin(), cur.end()) - cur.begin();
        if (hi == lo) break;
        const double before = cur[hi];
        bool moved = false;
        for (size_t i = 0; i < own[hi].size(); ++i) {
            std::vector<int32_t> a = own[hi], b = own[lo];
            const int32_t cid = a[i];
            if (contiguous) {
                bool touches = false;
                for (int32_t mine : b) if (adjacent(mine, cid)) { touches = true; break; }
                if (!touches) continue;
            }
            a.erase(a.begin() + i);
            b.push_back(cid);
            const double na = EstimateBlock(a, demands, depot).TotalS();
            const double nb = EstimateBlock(b, demands, depot).TotalS();
            if (std::max(na, nb) < before - 1e-9) {
                own[hi] = a; own[lo] = b; moved = true; break;
            }
        }
        if (!moved) break;
    }

    for (uint32_t v = 0; v < vehicles; ++v)
        p.vehicles[v] = EstimateBlock(own[v], demands, depot);
    Score(p);
    return p;
}

// ---------------------------------------------------------------------------
// SPLIT
// ---------------------------------------------------------------------------
Partition PartitionSplit(const std::map<int32_t, Demand>& demands,
                         const Depot& depot, uint32_t vehicles) {
    Partition p;
    p.method = "split";
    p.contiguous = true;             // arcs of one tour are contiguous by construction
    if (vehicles == 0) return p;

    std::vector<int32_t> todo;
    for (const auto& [cid, d] : demands)
        if (d.theta > 0.0) todo.push_back(cid);
    p.vehicles.resize(vehicles);
    if (todo.empty()) return p;

    const std::vector<int32_t> tour = NearestNeighbour(todo, demands, depot);

    // Min-max cut of a FIXED sequence into M contiguous arcs: bisection on the
    // bound with a greedy feasibility test. Exact, not a heuristic.
    //
    // The feasibility test costs each arc WITH ITS DEPOT LEGS -- see the header.
    auto arcCost = [&](size_t i, size_t j) {          // [i, j)
        std::vector<int32_t> a(tour.begin() + i, tour.begin() + j);
        double s = 0;
        for (int32_t c : a) s += demands.at(c).penaltyS;
        return EuclidM(a, demands, depot) / kCruiseMps + s;
    };
    auto feasible = [&](double bound, std::vector<size_t>& cuts) {
        cuts.clear();
        size_t i = 0;
        while (i < tour.size()) {
            size_t j = i;
            while (j < tour.size() && arcCost(i, j + 1) <= bound) j++;
            if (j == i) return false;                 // one cell alone exceeds it
            cuts.push_back(j);
            i = j;
            if (cuts.size() > vehicles) return false;
        }
        return cuts.size() <= vehicles;
    };

    double lo = 0.0, hi = arcCost(0, tour.size());
    std::vector<size_t> cuts, best;
    if (!feasible(hi, best)) { for (size_t i = 1; i <= tour.size(); ++i) best.push_back(i); }
    for (int it = 0; it < 60; ++it) {
        const double mid = 0.5 * (lo + hi);
        if (feasible(mid, cuts)) { hi = mid; best = cuts; }
        else                     { lo = mid; }
    }

    size_t i = 0;
    for (uint32_t v = 0; v < vehicles; ++v) {
        const size_t j = v < best.size() ? best[v] : tour.size();
        std::vector<int32_t> a(tour.begin() + i, tour.begin() + std::max(i, j));
        Block b;
        b.cells = a;
        b.travelS = EuclidM(a, demands, depot) / kCruiseMps;
        for (int32_t c : a) b.serviceS += demands.at(c).penaltyS;
        p.vehicles[v] = b;
        i = std::max(i, j);
    }
    Score(p);
    return p;
}

}  // namespace ns3::uavsar::p1
