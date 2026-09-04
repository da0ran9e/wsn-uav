#ifndef UAV_SAR_P1_PARTITION_H
#define UAV_SAR_P1_PARTITION_H

// T1: split the cells that need serving among the aircraft.
//
// Two variants that differ in KIND, not in tuning. Both are implemented and
// both are measured, because comparing them under a kinematic constraint is the
// part nobody has done:
//
//   CREDIT   partition first, route afterwards. Each aircraft is a buyer with a
//            budget; regions grow by buying cells and then trade to level out.
//            Seeds are placed artificially, because every classical partitioning
//            scheme distinguishes vehicles BY THEIR DEPOTS and degenerates when
//            they all start from the same place -- which is this deployment.
//
//   SPLIT    route first, cut afterwards. One tour through every cell, then cut
//            it into M arcs of equal cost. For a FIXED sequence the min-max cut
//            is solvable exactly by bisection on the bound, so this half is not
//            a heuristic.
//
// ---------------------------------------------------------------------------
// THE COST ESTIMATE IS THE WHOLE PROBLEM
// ---------------------------------------------------------------------------
// A partitioner is only as good as what it thinks a block costs to fly. This
// project has paid for that lesson twice: once scoring lane METRES instead of
// flown distance (56 % imbalance), and once with an estimator blind to no-fly
// zones (70 % imbalance). Both times the partition looked balanced and the
// aircraft did not.
//
// So the estimate here charges everything the aircraft actually pays:
//   - the DEPOT LEGS, out and back. Cutting a tour into equal-cost arcs and
//     attaching depot legs afterwards balances the wrong quantity: the far arc
//     pays kilometres the near arc does not. The legs are inside the bisection.
//   - TURNS, by measuring the tour with Dubins rather than in straight lines.
//   - SERVICE, the seconds T0 says each cell costs.

#include "p1-demand.h"
#include "p1-dubins.h"
#include "p1-params.h"

#include <cstdint>
#include <map>
#include <vector>

namespace ns3::uavsar::p1 {

struct Route {
    std::vector<int32_t> cells;    // visit order
    double travelS = 0.0;          // flying, including both depot legs
    double serviceS = 0.0;         // T0 penalties
    double TotalS() const { return travelS + serviceS; }
};

struct Partition {
    std::vector<Route> vehicles;
    double makespanS = 0.0;        // the slowest aircraft -- what the mission costs
    double imbalancePct = 0.0;     // (max - min) / max
    const char* method = "";
    bool contiguous = false;
};

// Nearest-neighbour order over a set of cells, then MEASURED with Dubins using
// the headings the order implies. Shared by both variants so neither is
// flattered by a cheaper yardstick than the other.
Route EstimateRoute(const std::vector<int32_t>& cells,
                    const std::map<int32_t, Demand>& demands,
                    const Config& depot, double turnRadiusM);

Partition PartitionCredit(const std::map<int32_t, Demand>& demands,
                          const CellPlan& plan, const Config& depot,
                          uint32_t vehicles, double turnRadiusM, bool contiguous);

Partition PartitionSplit(const std::map<int32_t, Demand>& demands,
                         const Config& depot, uint32_t vehicles,
                         double turnRadiusM);

}  // namespace ns3::uavsar::p1

#endif  // UAV_SAR_P1_PARTITION_H
