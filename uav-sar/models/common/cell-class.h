#ifndef UAV_SAR_CELL_CLASS_H
#define UAV_SAR_CELL_CLASS_H

// Phase 0.2 and 0.3: who leads each cell, and what each cell is FOR.
//
// The cell substrate (cell-grid.h) answers "which nodes are together". It does
// not answer the question Phase 1 actually needs, which is: WHICH CELLS ARE
// WORTH FLYING TO. Those are different questions, and conflating them is what
// makes a sweep planner spend flight time where no amount of reference data can
// buy an answer.
//
// Two changes to the substrate, in order:
//
//   0.2  The leader is elected by CAPABILITY, not by proximity to the centroid
//        (cell-grid.h) and not by residual energy (PECEE). The leader is the
//        node that has to run the match, so the election must be about that.
//        Modality is a HARD FILTER, not a weight: a thermal leader holding a
//        visual reference has nothing to compare against, and no amount of
//        compute fixes it.
//
//   0.3  Each cell is labelled A / B / C:
//          A  holds a node that can DISCRIMINATE -- right modality and enough
//             compute to run the matcher. Only these consume aircraft time.
//          B  can detect but can never discriminate. It contributes to Tier 1
//             and to nothing else. Sending it reference data is pure waste.
//          C  scalar sensors only. Contributes nothing at this phase.
//
// INTERPRETATION, flagged: the written spec defines class A by modality alone.
// This adds "and enough compute to run the matcher" (kCpuConfirmMin, already in
// node-capability.h), because a cell that cannot run the match will never
// discriminate either -- which is the spec's own reason for excluding B. If that
// is not wanted, set kCpuConfirmMin to 0 and the two definitions coincide.

#include "cell-grid.h"
#include "node-capability.h"

#include <cstdint>
#include <map>
#include <vector>

namespace ns3::uavsar {

enum class CellClass : uint8_t {
    A = 0,   // detect AND discriminate -> needs reference
    B = 1,   // detect only             -> never send reference
    C = 2,   // neither
};

const char* CellClassName(CellClass c);

struct CellRole {
    int32_t   cellId = -1;
    CellClass cls = CellClass::C;
    uint32_t  leaderId = 0;      // capability-elected; 0 if the cell is empty
    double    leaderScore = 0.0;
    // Best discriminating node in the cell, which is what makes it class A.
    // Equal to leaderId whenever the election found one.
    uint32_t  matcherId = 0;
    // How far the reference has to travel inside the cell to reach the matcher,
    // in hops over the intra-cell tree. Feeds the T_local(R_c) curve.
    uint32_t  matcherHops = 0;
    uint32_t  members = 0;
    uint32_t  imagingMembers = 0;
};

struct CellRolePlan {
    std::map<int32_t, CellRole> roles;
    uint32_t nA = 0, nB = 0, nC = 0;
};

// Elect leaders and label cells. Does not modify the grid plan; the caller
// decides whether to adopt the new leaders (adopting them changes intra-cell
// routing, so it is a separate, explicit step).
CellRolePlan BuildCellRoles(const CellGridPlan& grid,
                            const std::map<uint32_t, NodeCapability>& caps);

// Spread of screening capability across cells. This is the number that has to
// move for the capability-weighted election to be worth claiming as anything --
// see the note in the spec that it is a SECONDARY contribution.
// Returns the coefficient of variation of per-cell leader score.
double LeaderScoreCv(const CellRolePlan& plan);

}  // namespace ns3::uavsar

#endif  // UAV_SAR_CELL_CLASS_H
