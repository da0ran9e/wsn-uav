// An open Dubins flight path through points visited in a given order.
//
// The heading at each point is chosen to make the path shortest, among the headings
// that point's predicate allows (an empty predicate allows all). Headings: every
// 1 degree at every point (exhaustive over the allowed grid, exact for the grid), then
// coordinate descent down to 0.01 degree, staying allowed.

#ifndef UAVCOOP_PATH_H
#define UAVCOOP_PATH_H

#include "dubins.h"
#include "hex-grid.h"

#include <functional>
#include <vector>

namespace ns3::uavcoop {

using HeadingOk = std::function<bool(double th)>;

struct Path {
    std::vector<Pose> poses;         // the pose at each point, in order
    std::vector<DubinsPath> legs;    // legs[i]: poses[i] -> poses[i+1]
    double length = 0, gridLength = 0;   // after refinement / best on the 1-degree grid
};

// Empty result (no poses) if some point allows no heading on the grid.
Path PlanPath(const std::vector<Point>& pts, double rho, const std::vector<HeadingOk>& ok);

}  // namespace ns3::uavcoop

#endif
