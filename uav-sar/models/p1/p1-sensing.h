#ifndef UAV_SAR_P1_SENSING_H
#define UAV_SAR_P1_SENSING_H

// What a ground node can do, and where each capability binds in Phase 1.
//
// N3 decides the shape of this: THE CLUSTER HEAD IS THE MATCHING SUBJECT. It
// matches its OWN observation against the reference it receives, and no data
// moves inside the cluster during this phase. So a node's capabilities matter
// only insofar as that node might be the head.
//
//   camera    can it observe at all   -> MANDATORY for headship. A head without
//                                       a camera has nothing to match, so this
//                                       is a hard filter, not a weight.
//
//   obs       feature quality          -> better features carry more Chernoff
//                                       information per unit of reference, so
//                                       the cell needs LESS of it.
//
//   cpu       matcher strength         -> a stronger matcher extracts more
//                                       information from the SAME reference, so
//                                       again the cell needs less. Second
//                                       priority in the election, and the second
//                                       source of demand heterogeneity.
//
//   rxBps     receive rate             -> how fast the head can take the
//                                       reference off the air while the aircraft
//                                       is overhead. Not in the P0.5 objective
//                                       yet: TODO(param) whether it binds at all
//                                       once the file size is fixed.
//
// obs SCALES RANGE, NOT GAIN. That distinction was measured on the old system
// and getting it wrong collapsed detection completely: as a gain multiplier, a
// weak sensor standing on top of the target still reported nothing. A weak
// sensor sees the same thing -- it just has to be closer.

#include "p1-params.h"
#include "p1-types.h"

#include <cstdint>
#include <map>
#include <vector>

namespace ns3::uavsar::p1 {

struct Node {
    uint32_t id = 0;
    double   x = 0, y = 0;
    double   obs = 0.0;        // [0,1]; 0 = no camera
    double   cpu = 0.0;        // [0,1]; fraction of the matcher it can run
    double   rxBps = 0.0;      // sustained receive rate

    // The only eligibility test for headship. Everything else is a priority.
    bool HasCamera() const { return obs > 0.0; }

    // Chernoff information per unit of reference. Both terms raise it and both
    // are necessary -- features with no matcher decide nothing, a matcher with
    // no features has nothing to decide on -- so they multiply.
    // TODO(param): the functional form is a placeholder until the Chernoff
    // derivation fixes it. What is load-bearing is that BOTH capabilities enter.
    double Information() const {
        const double i = obs * cpu;
        return i > 0.05 ? i : 0.05;
    }

    // NOTE there is no ElectScore() here any more. Under P0.5 the election
    // objective is c(theta(I_v)) + weave time -- BOTH IN SECONDS -- and it needs
    // the cell geometry, which a node does not have. Building it in p1-cells.cc
    // is what removes the hand-set weight that every LEACH/HEED-style rule has
    // to choose between incommensurable quantities.
};

// Deterministic given the seed. Positions come from the caller; capabilities are
// drawn here.
std::vector<Node> BuildNodes(const std::vector<std::pair<double, double>>& xy,
                             uint32_t seed);

// Every node identical and fully capable -- the homogeneous world, for the
// ablation that shows what heterogeneity actually costs.
std::vector<Node> BuildUniformNodes(const std::vector<std::pair<double, double>>& xy);

}  // namespace ns3::uavsar::p1

#endif  // UAV_SAR_P1_SENSING_H
