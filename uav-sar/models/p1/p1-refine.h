#ifndef UAV_SAR_P1_REFINE_H
#define UAV_SAR_P1_REFINE_H

// T4: close the loop that T0 had to cut.
//
// T0 charges a cell for being served, but that charge depends on the OFFSET at
// which the aircraft passes, which depends on the route, which needed the charge
// to be planned. The first pass cuts the loop by assuming the route goes through
// the cell centre. T4 re-enters with the offsets the route actually produced.
//
// The other half is surplus. A route flown for one cell sprays reference over
// every cell near it, and a cell that collects enough incidentally does not need
// to be visited at all. That is not a rounding effect: it is the reason a good
// route is worth more than the sum of its visits, and ignoring it makes the
// planner pay twice for coverage it already has.
//
//   1  measure the dose every class-A cell actually receives from the plan
//   2  reduce each cell's remaining demand by what it already has
//   3  recompute service cost at the offsets the routes really flew
//   4  re-partition, re-route, re-profile
//   5  stop when the makespan stops moving
//
// Step 2 oscillates, and damping alone does not stop it: drop a cell because
// the route covers it incidentally, the route shortens, the cell is uncovered
// again, and the two states alternate. Measured here as
// 214 -> 111 -> 81 -> 59 -> 74 -> 93 over six rounds.
//
// The fix is not more damping, it is a VALIDITY TEST. A plan is self-consistent
// only if every cell it chose not to visit is still covered by the route it
// actually built. An iterate that fails that is not a worse plan -- it is not a
// plan at all, and it must not be eligible to be returned. The loop therefore
// searches over demand sets and returns the best SELF-CONSISTENT plan it found,
// which is a well-defined answer even though the iteration itself does not
// converge monotonically.

#include "p1-demand.h"
#include "p1-partition.h"
#include "p1-route.h"
#include "p1-speed.h"

#include <cstdint>
#include <map>
#include <vector>

namespace ns3::uavsar::p1 {

struct RefineStep {
    uint32_t iteration = 0;
    double   makespanS = 0.0;
    double   flightM = 0.0;
    uint32_t planCells = 0;        // cells THIS plan actually visited
    uint32_t servedCells = 0;      // cells still owed after the revision
    uint32_t droppedBySurplus = 0; // cells retired because the routes covered them
    uint32_t infeasibleVehicles = 0;
    // A plan is SELF-CONSISTENT when every cell it decided not to visit is
    // still covered by the route it actually built. Retiring a cell shortens
    // the route, which can uncover the very cell that was retired -- so a plan
    // that fails this test is not a worse plan, it is not a plan at all.
    bool selfConsistent = false;
    uint32_t uncovered = 0;
};

struct Plan {
    Partition partition;
    std::vector<Tour> tours;
    std::vector<SpeedPlan> speeds;
    std::map<int32_t, Demand> demands;      // after the last revision
    // The demand set the RETURNED plan was built from. Not the same thing: the
    // plan comes from the best iterate and the revision keeps going afterwards,
    // so reading service costs out of `demands` describes a plan that was never
    // built.
    std::map<int32_t, Demand> bestDemands;
    std::vector<RefineStep> history;
    double makespanS = 0.0;      // best SELF-CONSISTENT iterate, not the last
    uint32_t bestIteration = 0;
    uint32_t consistentIterates = 0;
    bool converged = false;
    bool feasible = false;       // at least one self-consistent plan was found
};

// `damping` in (0,1]: 1.0 replaces demand outright, lower values average it with
// the previous value.
Plan Refine(const std::map<int32_t, Demand>& demands0, const CellPlan& cells,
            const DoseModel& dose, const Config& depot, uint32_t vehicles,
            double turnRadiusM, uint32_t maxIters = 6, double tolPct = 1.0,
            double damping = 0.6);

}  // namespace ns3::uavsar::p1

#endif  // UAV_SAR_P1_REFINE_H
