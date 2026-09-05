#ifndef UAV_SAR_P1_PARTITION_H
#define UAV_SAR_P1_PARTITION_H

// T1: split the cluster heads among the aircraft.
//
// The input is the CH set and nothing else. N1 and N2 decide that: no suspect
// exists before the flight, so there is no subset worth preferring, and EVERY
// cell that can host a head must be served. The heterogeneity is entirely in
// theta_n -- how much reference each head needs -- not in which head deserves a
// visit.
//
// Two variants that differ in KIND, not in tuning. Both are implemented and both
// are measured, because comparing them under a kinematic constraint is the part
// nobody has done:
//
//   CREDIT   partition first, route afterwards. Each aircraft is an account with
//            a budget; regions grow by taking adjacent cells and then trade to
//            level out. Seeds are placed artificially, because every classical
//            partitioning scheme distinguishes vehicles BY THEIR DEPOTS and
//            degenerates when they all start from the same place -- which is
//            this deployment.
//
//   SPLIT    route first, cut afterwards. One Euclidean tour through every head,
//            then cut it into M arcs of equal cost. For a FIXED sequence the
//            min-max cut is solvable exactly by bisection on the bound, so this
//            half is not a heuristic.
//
// ---------------------------------------------------------------------------
// THE YARDSTICK, AND WHAT IT COSTS
// ---------------------------------------------------------------------------
// T1 scores blocks in EUCLIDEAN travel, as specified: the kinematic cost is
// T2's business and T4 closes the loop with the offsets the real route produced.
// That is a deliberate staging, not an oversight -- but it is also not free, and
// this project has been bitten by exactly this before. So the module also
// exposes a Dubins measurement of the same partition, and the harness reports
// the gap. An estimator that ranks blocks differently from the way they fly is
// a partition that looks balanced and is not.
//
// Both variants are scored on the SAME yardstick, so neither is flattered.
//
// The depot legs are INSIDE the balancing, both variants. Cutting a tour into
// equal-cost arcs and attaching the legs afterwards balances a quantity nobody
// flies: the far arc pays kilometres the near arc does not.

#include "p1-demand.h"
#include "p1-params.h"

#include <cstdint>
#include <map>
#include <vector>

namespace ns3::uavsar::p1 {

struct Depot {
    double x = 0, y = 0;
};

struct Block {
    std::vector<int32_t> cells;    // visit order, as the estimate assumed it
    double travelS = 0.0;          // Euclidean, including BOTH depot legs
    double serviceS = 0.0;         // sum of c_n
    double TotalS() const { return travelS + serviceS; }
};

struct Partition {
    std::vector<Block> vehicles;
    double makespanS = 0.0;        // the slowest aircraft -- what the mission costs
    double imbalancePct = 0.0;     // (max - min) / max
    const char* method = "";
    bool contiguous = false;
};

// Nearest-neighbour order from the depot, then Euclidean length including both
// depot legs, plus the service seconds. This is the yardstick T1 optimises.
Block EstimateBlock(const std::vector<int32_t>& cells,
                    const std::map<int32_t, Demand>& demands, const Depot& depot);

// The same block, measured the way it will actually be flown: Dubins hops with
// the heading at each head taken from the direction of travel. Reported, never
// optimised against -- the gap between this and EstimateBlock is what the
// staging costs.
double DubinsTravelS(const Block& b, const std::map<int32_t, Demand>& demands,
                     const Depot& depot, double turnRadiusM);

Partition PartitionCredit(const std::map<int32_t, Demand>& demands,
                          const CellPlan& plan, const Depot& depot,
                          uint32_t vehicles, bool contiguous);

Partition PartitionSplit(const std::map<int32_t, Demand>& demands,
                         const Depot& depot, uint32_t vehicles);

}  // namespace ns3::uavsar::p1

#endif  // UAV_SAR_P1_PARTITION_H
