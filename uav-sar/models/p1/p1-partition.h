#ifndef UAV_SAR_P1_PARTITION_H
#define UAV_SAR_P1_PARTITION_H

// T1: split the ROWS among the aircraft.
//
// The unit of work is a row, not a cell. That follows from the flight model: an
// aircraft entering a row flies it end to end, so a row cannot be shared and
// there is nothing finer to divide. The row's weight is everything that happens
// while flying it:
//
//     W_r = sum over the heads on row r of c_n   +   row length / v_cruise
//
// ---------------------------------------------------------------------------
// WHY CONTIGUITY IS NOT IMPOSED
// ---------------------------------------------------------------------------
// Every partitioning scheme in the literature either enforces or preserves
// contiguous regions. Here the cost of changing rows is L(|dr| h, rho), which is
// NOT monotone in |dr|: below 2 rho the turn is tight and expensive, and skipping
// a row can be cheaper than taking the next one. So a vehicle's best set of rows
// need not be a contiguous block, and forcing it to be one is a constraint the
// geometry does not ask for. Both variants are built and both are measured.
//
// T2 becomes small once T1 is done this way: with rows as the unit, the cost
// between consecutive rows depends only on the difference of their indices, so
// ordering a vehicle's rows is a permutation problem over a one-dimensional
// cost -- not a generalised TSP over heading configurations.

#include "p1-demand.h"
#include "p1-params.h"

#include <cstdint>
#include <map>
#include <vector>

namespace ns3::uavsar::p1 {

struct Depot {
    double x = 0, y = 0;
};

struct RowWork {
    int32_t row = 0;
    double  lengthM = 0.0;      // extent of the row inside the field
    double  serviceS = 0.0;     // sum of c_n over the heads on it
    uint32_t heads = 0;
    double  WeightS() const { return serviceS + lengthM / kCruiseMps; }
};

struct Block {
    std::vector<int32_t> rows;  // in the order T1 left them; T2 will reorder
    double workS = 0.0;         // sum of W_r
    double changeS = 0.0;       // row-to-row turns, in the order given
    double depotS = 0.0;        // out and back
    double TotalS() const { return workS + changeS + depotS; }
};

struct Partition {
    std::vector<Block> vehicles;
    double makespanS = 0.0;
    double imbalancePct = 0.0;
    const char* method = "";
    bool contiguous = false;
};

// Row extents and weights, from the cells and their service costs.
std::map<int32_t, RowWork> BuildRows(const CellPlan& plan,
                                     const std::map<int32_t, Demand>& demands);

// Cost of a set of rows flown in ascending index order, with both depot legs.
Block CostBlock(const std::vector<int32_t>& rows,
                const std::map<int32_t, RowWork>& work, const CellPlan& plan,
                const Depot& depot, double turnRadiusM);

Partition PartitionCredit(const std::map<int32_t, RowWork>& work,
                          const CellPlan& plan, const Depot& depot,
                          uint32_t vehicles, double turnRadiusM, bool contiguous);

Partition PartitionSplit(const std::map<int32_t, RowWork>& work,
                         const CellPlan& plan, const Depot& depot,
                         uint32_t vehicles, double turnRadiusM);

}  // namespace ns3::uavsar::p1

#endif  // UAV_SAR_P1_PARTITION_H
