#include "p1-refine.h"

#include <algorithm>
#include <cmath>
#include <limits>

namespace ns3::uavsar::p1 {

namespace {

// Dose a cell picks up from the GEOMETRY of a flown path, at cruise speed.
//
// Cruise, deliberately, and this is the correction that makes the loop mean
// anything. Measuring the dose of the OPTIMISED profile and subtracting it from
// demand is circular: the profile was built to satisfy exactly those cells, so
// every cell looks satisfied, its demand is written down, and after a few rounds
// the planner has argued itself into flying nothing.
//
// What T4 is actually looking for is the dose a cell gets FOR FREE -- because it
// happens to lie near a path the aircraft was flying anyway, at the speed it
// would hold if that cell did not exist. That is a property of the route's
// GEOMETRY, not of the profile built on top of it, so it is measured at cruise
// and it cannot decay to zero on its own.
double FreeDoseAt(const SpeedPlan& sp, const DoseModel& dose, double x, double y) {
    double got = 0.0;
    for (const SpeedSegment& s : sp.segments)
        got += kRefTxBytesPerS * s.lengthM *
               dose.Prx(std::hypot(s.x - x, s.y - y)) / kCruiseMps;
    return got;
}

// Closest the flown path comes to a point: the offset T0 should have been
// charging all along.
double ClosestOffset(const SpeedPlan& sp, double x, double y) {
    double best = std::numeric_limits<double>::infinity();
    for (const SpeedSegment& s : sp.segments)
        best = std::min(best, std::hypot(s.x - x, s.y - y));
    return best == std::numeric_limits<double>::infinity() ? 0.0 : best;
}

}  // namespace

Plan Refine(const std::map<int32_t, Demand>& demands0, const CellPlan& cells,
            const DoseModel& dose, const Config& depot, uint32_t vehicles,
            double R, uint32_t maxIters, double tolPct, double damping) {
    Plan out;
    std::map<int32_t, Demand> cur = demands0;
    std::map<int32_t, double> theta0;
    for (const auto& [cid, d] : cur) theta0[cid] = d.theta;

    double prevMakespan = std::numeric_limits<double>::infinity();
    double bestMakespan = std::numeric_limits<double>::infinity();
    for (uint32_t it = 0; it < maxIters; ++it) {
        for (auto& [cid, d] : cur) ServiceCost(d, 0.0, dose);   // offsets applied below

        Partition part = PartitionCredit(cur, cells, depot, vehicles, R, false);
        std::vector<Tour> tours;
        std::vector<SpeedPlan> speeds;
        double makespan = 0.0, flight = 0.0;
        uint32_t infeasible = 0;
        for (const Route& r : part.vehicles) {
            Tour t = SolveTour(r.cells, cur, depot, R);
            SpeedPlan sp = PlanSpeed(t, cur, dose, R);
            // An infeasible profile is information, not a failure: this tour
            // cannot deliver at any admissible speed, so the cost of the
            // vehicle falls back on T0's orbit model, which is what the aircraft
            // would actually have to do.
            const double cost = sp.solved ? sp.totalTimeS : t.TotalS();
            if (!sp.solved) infeasible++;
            makespan = std::max(makespan, cost);
            flight += t.flightM;
            tours.push_back(std::move(t));
            speeds.push_back(std::move(sp));
        }

        // --- measure what was actually delivered, everywhere -----------------
        uint32_t dropped = 0, served = 0;
        std::map<int32_t, double> got, offset;
        for (const auto& [cid, d] : cur) {
            if (theta0[cid] <= 0.0) continue;
            double g = 0.0;
            double off = std::numeric_limits<double>::infinity();
            for (const SpeedPlan& sp : speeds) {
                // Geometry only: an infeasible profile still describes a path
                // that would be flown, and the free dose along it is real.
                g += FreeDoseAt(sp, dose, d.x, d.y);
                off = std::min(off, ClosestOffset(sp, d.x, d.y));
            }
            got[cid] = g;
            offset[cid] = std::isfinite(off) ? off : 0.0;
        }

        RefineStep step;
        step.iteration = it;
        step.makespanS = makespan;
        step.flightM = flight;
        step.infeasibleVehicles = infeasible;

        // Validity: is every cell this plan declined to visit actually covered
        // by the route it built? A plan that fails this has retired work it is
        // not doing, and its makespan is a number for a mission that does not
        // happen.
        for (const auto& [cid, d] : cur) {
            if (theta0[cid] <= 0.0 || d.theta > 0.0) continue;   // visited or N/A
            if (got.count(cid) && got[cid] >= theta0[cid]) continue;
            step.uncovered++;
        }
        step.selfConsistent = (step.uncovered == 0) && (infeasible == 0);
        if (step.selfConsistent) out.consistentIterates++;

        // --- revise demand ---------------------------------------------------
        // Retirement is a DISCRETE decision and damping must not blur it: a cell
        // whose free dose already covers it is done, and averaging it back to a
        // small positive demand keeps it in the routing problem for ever.
        // Damping applies only to PARTIAL reductions, which are the ones that
        // oscillate.
        for (auto& [cid, d] : cur) {
            if (theta0[cid] <= 0.0) continue;
            const double delivered = got.count(cid) ? got[cid] : 0.0;
            const double residual = theta0[cid] - delivered;
            if (residual <= 0.0) {
                d.theta = 0.0; d.penaltyS = 0.0; d.serveMps = 0.0; d.orbits = 0;
                dropped++;
                continue;
            }
            d.theta = (1.0 - damping) * d.theta + damping * residual;
            served++;
            ServiceCost(d, offset.count(cid) ? offset[cid] : 0.0, dose);
        }
        step.servedCells = served;
        step.droppedBySurplus = dropped;
        out.history.push_back(step);

        // KEEP THE BEST, not the last. The loop is not a contraction: retiring a
        // cell moves the route away from it, the cell comes back, and the two
        // states alternate. Measured here as 214 -> 111 -> 81 -> 59 -> 74 -> 93
        // over six rounds. Damping slows the swing without removing it, so what
        // is returned is the best plan seen rather than whichever one the
        // iteration cap happened to land on.
        if (step.selfConsistent && makespan < bestMakespan) {
            bestMakespan = makespan;
            out.partition = part;
            out.tours = tours;
            out.speeds = speeds;
            out.bestIteration = it;
        }
        if (std::fabs(prevMakespan - makespan) <= tolPct / 100.0 * makespan) {
            out.converged = true;
            break;
        }
        prevMakespan = makespan;
    }
    out.feasible = std::isfinite(bestMakespan);
    out.makespanS = out.feasible ? bestMakespan : 0.0;
    out.demands = std::move(cur);
    return out;
}

}  // namespace ns3::uavsar::p1
