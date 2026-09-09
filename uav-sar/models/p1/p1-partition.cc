#include "p1-partition.h"

#include <algorithm>
#include <cmath>
#include <limits>

namespace ns3::uavsar::p1 {

std::map<int32_t, RowWork> BuildRows(const CellPlan& plan,
                                     const std::map<int32_t, Demand>& demands) {
    std::map<int32_t, RowWork> out;
    for (const auto& [row, cells] : plan.cellsByRow) {
        RowWork w;
        w.row = row;
        double lo = std::numeric_limits<double>::infinity(), hi = -lo;
        for (int32_t cid : cells) {
            const Cell& c = plan.cells.at(cid);
            double u, ww;
            plan.field.ToRowFrame(c.cx, c.cy, u, ww);
            lo = std::min(lo, u);
            hi = std::max(hi, u);
            const auto di = demands.find(cid);
            if (di != demands.end() && di->second.theta > 0) {
                w.serviceS += di->second.CostS();
                w.heads++;
            }
        }
        // The row is flown from the first cell to the last, plus half a pitch of
        // run-in and run-out so the weave has somewhere to start and finish.
        w.lengthM = (hi - lo) + plan.cellPitchM;
        out[row] = w;
    }
    return out;
}

Block CostBlock(const std::vector<int32_t>& rows,
                const std::map<int32_t, RowWork>& work, const CellPlan& plan,
                const Depot& depot, double rho) {
    Block b;
    b.rows = rows;
    if (rows.empty()) return b;
    std::vector<int32_t> ord = rows;
    std::sort(ord.begin(), ord.end());
    b.rows = ord;
    for (int32_t r : ord) b.workS += work.at(r).WeightS();
    for (size_t i = 0; i + 1 < ord.size(); ++i)
        b.changeS += RowChangeM(std::abs(ord[i + 1] - ord[i]) * plan.rowPitchM, rho)
                     / kCruiseMps;
    // Depot legs: out to the nearest end of the first row and back from the last.
    auto rowPoint = [&](int32_t r) {
        double x, y;
        plan.field.FromRowFrame(0.0, plan.RowLineW(r), x, y);
        return std::make_pair(x, y);
    };
    const auto p0 = rowPoint(ord.front());
    const auto p1 = rowPoint(ord.back());
    b.depotS = (std::hypot(p0.first - depot.x, p0.second - depot.y) +
                std::hypot(p1.first - depot.x, p1.second - depot.y)) / kCruiseMps;
    return b;
}

namespace {

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

Partition PartitionCredit(const std::map<int32_t, RowWork>& work,
                          const CellPlan& plan, const Depot& depot,
                          uint32_t vehicles, double rho, bool contiguous) {
    Partition p;
    p.method = "credit";
    p.contiguous = contiguous;
    if (vehicles == 0) return p;
    p.vehicles.resize(vehicles);

    std::vector<int32_t> rows;
    for (const auto& [r, w] : work) rows.push_back(r);
    if (rows.empty()) return p;

    // Seeds evenly spaced by ROW INDEX. With a shared depot the vehicles are not
    // separated by where they start, so the seeds have to do that job.
    //
    // There can be FEWER ROWS THAN AIRCRAFT -- a wide cell radius over a narrow
    // field gives three rows for four vehicles -- and then the even spacing
    // collides, two vehicles seed on the same row, and that row is flown twice.
    // Seeding only min(M, |rows|) vehicles leaves the surplus idle, which is the
    // right answer: a row cannot be shared.
    std::vector<std::vector<int32_t>> own(vehicles);
    std::map<int32_t, int32_t> owner;
    const uint32_t nSeed = (uint32_t)std::min<size_t>(vehicles, rows.size());
    for (uint32_t v = 0; v < nSeed; ++v) {
        const size_t k = rows.size() * v / nSeed;
        own[v].push_back(rows[k]);
        owner[rows[k]] = (int32_t)v;
    }

    while (owner.size() < rows.size()) {
        uint32_t v = 0;
        double least = std::numeric_limits<double>::infinity();
        std::vector<double> cur(vehicles);
        for (uint32_t k = 0; k < vehicles; ++k) {
            cur[k] = CostBlock(own[k], work, plan, depot, rho).TotalS();
            if (cur[k] < least) { least = cur[k]; v = k; }
        }
        // A ROW INDEX CAN BE NEGATIVE: the grid is laid out in the row frame and
        // axial coordinates run either side of the origin. So "not found" needs
        // its own flag -- a `pick < 0` sentinel treats row -2 as a failure, falls
        // into the fallback, picks row -2 again, and breaks out of the loop with
        // rows still unassigned. That is exactly what happened: 3 of 5 rows flown.
        int32_t pick = 0;
        bool havePick = false;
        double bestDelta = std::numeric_limits<double>::infinity();
        for (int32_t r : rows) {
            if (owner.count(r)) continue;
            if (contiguous) {
                bool touches = false;
                for (int32_t mine : own[v]) if (std::abs(mine - r) == 1) { touches = true; break; }
                if (!touches) continue;
            }
            std::vector<int32_t> trial = own[v];
            trial.push_back(r);
            const double delta = CostBlock(trial, work, plan, depot, rho).TotalS() - cur[v];
            if (delta < bestDelta) { bestDelta = delta; pick = r; havePick = true; }
        }
        if (!havePick) {
            for (int32_t r : rows)
                if (!owner.count(r)) { pick = r; havePick = true; break; }
            if (!havePick) break;
        }
        owner[pick] = (int32_t)v;
        own[v].push_back(pick);
    }

    for (int iter = 0; iter < 200; ++iter) {
        std::vector<double> cur(vehicles);
        for (uint32_t k = 0; k < vehicles; ++k)
            cur[k] = CostBlock(own[k], work, plan, depot, rho).TotalS();
        const size_t hi = std::max_element(cur.begin(), cur.end()) - cur.begin();
        const size_t lo = std::min_element(cur.begin(), cur.end()) - cur.begin();
        if (hi == lo) break;
        const double before = cur[hi];
        bool moved = false;
        for (size_t i = 0; i < own[hi].size() && !moved; ++i) {
            std::vector<int32_t> a = own[hi], b = own[lo];
            const int32_t r = a[i];
            if (contiguous) {
                bool touches = false;
                for (int32_t mine : b) if (std::abs(mine - r) == 1) { touches = true; break; }
                if (!touches) continue;
            }
            a.erase(a.begin() + i);
            b.push_back(r);
            const double na = CostBlock(a, work, plan, depot, rho).TotalS();
            const double nb = CostBlock(b, work, plan, depot, rho).TotalS();
            if (std::max(na, nb) < before - 1e-9) { own[hi] = a; own[lo] = b; moved = true; }
        }
        if (!moved) break;
    }

    for (uint32_t v = 0; v < vehicles; ++v)
        p.vehicles[v] = CostBlock(own[v], work, plan, depot, rho);
    Score(p);
    return p;
}

Partition PartitionSplit(const std::map<int32_t, RowWork>& work,
                         const CellPlan& plan, const Depot& depot,
                         uint32_t vehicles, double rho) {
    Partition p;
    p.method = "split";
    p.contiguous = true;             // consecutive rows, by construction
    if (vehicles == 0) return p;
    p.vehicles.resize(vehicles);

    std::vector<int32_t> rows;
    for (const auto& [r, w] : work) rows.push_back(r);
    if (rows.empty()) return p;
    std::sort(rows.begin(), rows.end());

    // Min-max cut of the row sequence into M contiguous runs: bisection on the
    // bound with a greedy feasibility test. Exact for a fixed sequence. The
    // depot legs are inside the cost, not attached afterwards -- balancing arc
    // cost alone balances a quantity nobody flies.
    auto arc = [&](size_t i, size_t j) {
        return CostBlock({rows.begin() + i, rows.begin() + j}, work, plan, depot, rho)
            .TotalS();
    };
    auto feasible = [&](double bound, std::vector<size_t>& cuts) {
        cuts.clear();
        size_t i = 0;
        while (i < rows.size()) {
            size_t j = i;
            while (j < rows.size() && arc(i, j + 1) <= bound) j++;
            if (j == i) return false;
            cuts.push_back(j);
            i = j;
            if (cuts.size() > vehicles) return false;
        }
        return cuts.size() <= vehicles;
    };

    double lo = 0.0, hi = arc(0, rows.size());
    std::vector<size_t> cuts, best;
    if (!feasible(hi, best)) { for (size_t i = 1; i <= rows.size(); ++i) best.push_back(i); }
    for (int it = 0; it < 60; ++it) {
        const double mid = 0.5 * (lo + hi);
        if (feasible(mid, cuts)) { hi = mid; best = cuts; }
        else                     { lo = mid; }
    }

    size_t i = 0;
    for (uint32_t v = 0; v < vehicles; ++v) {
        const size_t j = v < best.size() ? best[v] : rows.size();
        p.vehicles[v] = CostBlock({rows.begin() + i, rows.begin() + std::max(i, j)},
                                  work, plan, depot, rho);
        i = std::max(i, j);
    }
    Score(p);
    return p;
}

}  // namespace ns3::uavsar::p1
