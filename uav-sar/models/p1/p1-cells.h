#ifndef UAV_SAR_P1_CELLS_H
#define UAV_SAR_P1_CELLS_H

// P0.2 - P0.6: cells on the rotated grid, rows, offsets, heads, demand.
//
// The order matters and is the reason this is not the old substrate with things
// bolted on. The grid is laid out ALIGNED TO psi first, so rows exist before
// anything else; every node then knows its row and its offset from it (P0.4);
// and only then is the head elected -- by an objective that already contains the
// flight cost of reaching it (P0.5).
//
// ---------------------------------------------------------------------------
// P0.5 IS THE CHANGE THAT MATTERS
// ---------------------------------------------------------------------------
//     n* = argmin  c(theta(I_v))  +  pi^2 delta_v^2 / (4 a v_cruise)
//          v in A_n
//          s.t.     delta_v <= delta_max = a^2 / (pi^2 rho)
//
// Two properties worth keeping in mind while reading the code:
//
//   * BOTH TERMS ARE SECONDS. There is no weight to choose, and therefore no
//     weight to be accused of tuning. Every LEACH- or HEED-style election picks
//     a hand-set coefficient between incommensurable quantities; this one does
//     not have one to pick.
//
//   * THE CONSTRAINT IS THE VEHICLE'S, NOT THE NETWORK'S. A head further than
//     delta_max from its row line cannot be reached by weaving -- the curvature
//     needed exceeds what the airframe can hold -- so serving it would force a
//     real Dubins detour off the row. Electing such a head is not expensive, it
//     is infeasible for the plan the rest of the pipeline assumes.
//
// F1 is the feasibility condition: some capable node must be within delta_max.
// It is NOT free. With one candidate per cell it fails about 46 % of the time
// (measured, and matching the spec's 45 %); five candidates take that to 2 %,
// ten to 0.04 %. Those numbers hold NEAR THE DESIGN POINT R_c = 4 rho / 3, where
// delta_max is 0.405 R_c; they get easier as R_c grows, because delta_max / R_c
// grows with it.

#include "p1-field.h"
#include "p1-hex.h"
#include "p1-params.h"
#include "p1-sensing.h"
#include "p1-types.h"

#include <cstdint>
#include <map>
#include <set>
#include <vector>

namespace ns3::uavsar::p1 {

struct CellMember {
    uint32_t id = 0;
    double   offsetM = 0.0;        // delta_v: distance from the row line
    bool     eligible = false;     // has a camera AND delta_v <= delta_max
    int32_t  parent = -1;
    uint32_t hops = 0xFFFFFFFFu;
};

struct Cell {
    int32_t   id = -1;
    int32_t   q = 0, r = 0;        // axial, in the ROW FRAME
    double    cx = 0, cy = 0;      // centre, world frame
    int32_t   row = 0;             // r(n): which row line this cell sits on
    CellClass cls = CellClass::BARREN;
    uint32_t  head = 0;
    bool      hasHead = false;
    double    headOffsetM = 0.0;   // delta_n
    double    headScoreS = 0.0;    // the P0.5 objective, in seconds
    std::vector<CellMember> members;
    uint32_t  cameras = 0;         // members with a camera
    uint32_t  eligible = 0;        // ... and within delta_max
    uint32_t  unreachable = 0;
};

struct CellPlan {
    double cellRadiusM = 0;
    double cellPitchM = 0;         // a = R_c sqrt(3)
    double rowPitchM = 0;          // h = 1.5 R_c
    double maxOffsetM = 0;         // delta_max
    Field  field;
    std::map<int32_t, Cell> cells;
    std::map<uint32_t, int32_t> cellOfNode;
    std::map<int32_t, std::vector<int32_t>> cellsByRow;
    uint32_t nServed = 0, nBarren = 0;
    // F1 failures: a cell with cameras, none of them reachable by weaving.
    uint32_t nInfeasible = 0;

    std::vector<int32_t> ServedCells() const;
    std::vector<int32_t> Rows() const;
    double RowLineW(int32_t row) const { return row * rowPitchM; }
};

// How the head is chosen among the ELIGIBLE nodes. FLIGHT_AWARE is P0.5; the
// others exist so that "what does the election buy" is answerable with a number.
enum class Election : uint8_t {
    FLIGHT_AWARE = 0,   // c(theta(I)) + weave time   <- P0.5, the design
    CAPABILITY   = 1,   // capability only, ignoring where the node sits
    CENTROID     = 2,   // nearest the cell centre    <- what PECEE does
    RANDOM       = 3,   // any eligible node          <- the null
};

CellPlan BuildCells(const std::vector<Node>& nodes, const Field& field,
                    double cellRadiusM, double groundRangeM,
                    double turnRadiusM,
                    Election rule = Election::FLIGHT_AWARE, uint32_t seed = 1);

// Spread of head capability across cells (coefficient of variation).
double HeadScoreCv(const CellPlan& plan);

}  // namespace ns3::uavsar::p1

#endif  // UAV_SAR_P1_CELLS_H
