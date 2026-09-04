#include "p1-speed.h"

#include <algorithm>
#include <cmath>

namespace ns3::uavsar::p1 {

SpeedPlan PlanSpeed(const Tour& tour, const std::map<int32_t, Demand>& demands,
                    const DoseModel& dose, double R, double stepM) {
    SpeedPlan plan;
    if (tour.legs.empty()) return plan;

    // --- cut the flown path into segments ---------------------------------
    Config prev = tour.depot;
    auto cut = [&](const Config& from, const Config& to) {
        const DubinsPath p = Dubins(from, to, R);
        if (!p.valid) return;
        const int n = std::max(1, (int)std::ceil(p.length / stepM));
        Config a = from;
        for (int k = 1; k <= n; ++k) {
            const Config b = Integrate(from, p, R, (double)k / n);
            SpeedSegment s;
            s.lengthM = p.length / n;
            s.x = 0.5 * (a.x + b.x);
            s.y = 0.5 * (a.y + b.y);
            // Which part of the word this piece falls in decides whether speed
            // may move here at all.
            const double f = ((double)k - 0.5) / n;
            const double t = f * (p.seg[0] + p.seg[1] + p.seg[2]);
            const char* w = WordName(p.word);
            s.turning = t <= p.seg[0] ? w[0] != 'S'
                      : t <= p.seg[0] + p.seg[1] ? w[1] != 'S'
                                                 : w[2] != 'S';
            plan.segments.push_back(s);
            a = b;
        }
    };
    for (const Leg& l : tour.legs) { cut(prev, l.cfg); prev = l.cfg; }
    cut(prev, tour.depot);

    const size_t n = plan.segments.size();
    const double uMin = 1.0 / kMaxMps, uMax = 1.0 / kMinMps;
    const double uTurn = 1.0 / kCruiseMps;

    // --- build the LP  (variables w_i = u_i - uMin >= 0) -------------------
    std::vector<int32_t> cells;
    for (const Leg& l : tour.legs)
        if (demands.at(l.cellId).theta > 0) cells.push_back(l.cellId);

    std::vector<std::vector<double>> A;
    std::vector<double> b, c(n, 0.0);
    for (size_t i = 0; i < n; ++i) c[i] = plan.segments[i].lengthM;

    // box: w_i <= (turning ? uTurn : uMax) - uMin
    for (size_t i = 0; i < n; ++i) {
        std::vector<double> row(n, 0.0);
        row[i] = 1.0;
        A.push_back(row);
        b.push_back((plan.segments[i].turning ? uTurn : uMax) - uMin);
    }
    // turns are PINNED to the planned radius: w_i >= uTurn - uMin as well
    for (size_t i = 0; i < n; ++i) {
        if (!plan.segments[i].turning) continue;
        std::vector<double> row(n, 0.0);
        row[i] = -1.0;
        A.push_back(row);
        b.push_back(-(uTurn - uMin));
    }
    // dose: sum_i a_ni u_i >= theta_n , as  -sum a_ni w_i <= -(theta - uMin sum a)
    for (int32_t cid : cells) {
        const Demand& d = demands.at(cid);
        std::vector<double> a(n, 0.0);
        double base = 0.0;
        for (size_t i = 0; i < n; ++i) {
            const SpeedSegment& s = plan.segments[i];
            a[i] = kRefTxBytesPerS * s.lengthM * dose.Prx(std::hypot(s.x - d.x, s.y - d.y));
            base += a[i] * uMin;
        }
        std::vector<double> row(n, 0.0);
        for (size_t i = 0; i < n; ++i) row[i] = -a[i];
        A.push_back(row);
        b.push_back(-(d.theta - base));
    }

    const LpResult lp = SolveLp(A, b, c);
    plan.lpRows = (uint32_t)A.size();
    plan.lpCols = (uint32_t)n;
    plan.lpIterations = lp.iterations;
    plan.infeasible = lp.infeasible;
    plan.solved = lp.ok;
    if (!lp.ok) return plan;

    for (size_t i = 0; i < n; ++i) {
        const double u = uMin + lp.x[i];
        plan.segments[i].speedMps = u > 0 ? 1.0 / u : kCruiseMps;
        plan.totalTimeS += plan.segments[i].lengthM * u;
    }
    // delivered dose, recomputed from the answer rather than read off the LP
    for (int32_t cid : cells) {
        const Demand& d = demands.at(cid);
        double got = 0;
        for (const SpeedSegment& s : plan.segments)
            got += kRefTxBytesPerS * s.lengthM * dose.Prx(std::hypot(s.x - d.x, s.y - d.y))
                   / s.speedMps;
        plan.doseBytes[cid] = got;
    }
    const size_t doseRow0 = A.size() - cells.size();
    for (size_t k = 0; k < cells.size(); ++k)
        plan.shadow[cells[k]] = lp.dual[doseRow0 + k];
    return plan;
}

}  // namespace ns3::uavsar::p1
