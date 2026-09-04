#ifndef UAV_SAR_P1_SPEED_H
#define UAV_SAR_P1_SPEED_H

// T3: how fast to fly, metre by metre along a tour that is already fixed.
//
// The tour is cut into short segments and the variable is the INVERSE of speed.
// Under that change of variable everything the problem needs is linear:
//
//   total time      = sum of (segment length x inverse speed)      linear
//   dose at cell n  = lambda_tx x sum of (length x p(d) x inv v)   linear
//   speed box       = inverse speed between 1/vmax and 1/vmin      linear
//
// so T3 is a LINEAR PROGRAM and is solved, not approximated. The change of
// variable is standard in trajectory optimisation; what is worth saying is that
// THE DOSE CONSTRAINT SURVIVES IT. A throughput constraint would not: throughput
// is a rate, and a rate constraint in inverse speed is not linear. Dose is an
// integral of a rate over time, which is exactly what the substitution linearises.
//
// The dual variable of each dose row says which cell the optimum is pressed
// against. That is the signal T4 uses to know where a revision would pay,
// instead of revising everything and hoping.
//
// KINEMATIC COUPLING, stated because it is easy to miss: the turn radius
// depends on speed, rho = v^2 / (g tan phi). T2 fixed the geometry at ONE
// radius, so letting T3 choose a different speed on a TURN would invalidate the
// path T2 planned. Speed is therefore free only on straight segments, and turns
// are held at the radius the tour was planned with. Without that the two stages
// would each be right on their own and wrong together.

#include "p1-demand.h"
#include "p1-lp.h"
#include "p1-route.h"

#include <cstdint>
#include <map>
#include <vector>

namespace ns3::uavsar::p1 {

struct SpeedSegment {
    double x = 0, y = 0;        // midpoint
    double lengthM = 0.0;
    bool   turning = false;     // speed pinned: rho depends on v (see header)
    double speedMps = 0.0;
};

struct SpeedPlan {
    std::vector<SpeedSegment> segments;
    std::map<int32_t, double> doseBytes;    // delivered per cell
    std::map<int32_t, double> shadow;       // dual price per cell; >0 = binding
    double totalTimeS = 0.0;
    bool   solved = false;
    bool   infeasible = false;
    uint32_t lpRows = 0, lpCols = 0, lpIterations = 0;
};

// `stepM` is the segment length the tour is cut into.
SpeedPlan PlanSpeed(const Tour& tour, const std::map<int32_t, Demand>& demands,
                    const DoseModel& dose, double turnRadiusM, double stepM = 25.0);

}  // namespace ns3::uavsar::p1

#endif  // UAV_SAR_P1_SPEED_H
