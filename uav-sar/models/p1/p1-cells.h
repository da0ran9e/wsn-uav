#ifndef UAV_SAR_P1_CELLS_H
#define UAV_SAR_P1_CELLS_H

// Phase 0, done in ONE pass: partition, elect, classify, route inside the cell.
//
// The order matters and is the reason this is not the old substrate with a
// second election bolted on. The leader is elected FIRST, by capability, and the
// intra-cell tree is then rooted at that leader. Electing a leader for one
// reason and routing from a leader chosen for another leaves two leaders in the
// system, and every hop count computed afterwards is wrong by an amount nobody
// measures.
//
//   partition   hex cells of circumradius R_c (p1-hex.h)
//   elect       highest ElectScore among nodes that CAN MATCH; if none can, the
//               highest among everyone, because the cell still has to get its
//               Tier-1 report out
//   classify    A = someone can match; B = someone images but nobody can match;
//               C = nobody images
//   route       BFS over in-cell links, rooted at the elected leader
//
// What Phase 0 hands to Phase 1 is not "a list of clusters". It is:
//   - the set of class-A cells, which is the ONLY set the aircraft may spend
//     time on, and
//   - the row pitch h = 1.5 R_c, which is the quantity that ties cell size to
//     the aircraft's turn radius and makes the design rule statable at all.

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
    int32_t  parent = -1;          // next hop toward the leader; -1 = leader
    uint32_t hops = 0xFFFFFFFFu;   // 0 = leader; max = unreachable inside the cell
};

struct Cell {
    int32_t   id = -1;
    int32_t   q = 0, r = 0;
    double    cx = 0, cy = 0;
    CellClass cls = CellClass::C;
    uint32_t  leader = 0;
    bool      hasLeader = false;
    double    leaderScore = 0.0;
    std::vector<CellMember> members;
    uint32_t  imagers = 0;
    uint32_t  matchers = 0;        // nodes that could run the match
    uint32_t  unreachable = 0;     // members the leader cannot reach in-cell
    // Seconds for the reference to reach every matcher in the cell from the
    // leader, store and forward. One of the three competing pressures on R_c.
    double    tLocalS = 0.0;
};

struct CellPlan {
    double cellRadiusM = 0;
    std::map<int32_t, Cell> cells;
    std::map<uint32_t, int32_t> cellOfNode;
    uint32_t nA = 0, nB = 0, nC = 0;

    std::vector<int32_t> ClassACells() const;
    double RowPitchM() const { return hex::RowPitch(cellRadiusM); }
};

CellPlan BuildCells(const std::vector<Node>& nodes, double cellRadiusM,
                    double groundRangeM);

// Spread of leader capability across cells (coefficient of variation). This is
// the number that has to move for the capability-weighted election to be worth
// claiming as anything -- and the spec is explicit that it is a SECONDARY
// contribution, so it should be reported honestly and not oversold.
double LeaderScoreCv(const CellPlan& plan);

// Seconds to push `bytes` from the leader to every matcher in the cell.
double LocalDisseminationS(const Cell& cell, const std::vector<Node>& nodes,
                           double bytes);

}  // namespace ns3::uavsar::p1

#endif  // UAV_SAR_P1_CELLS_H
