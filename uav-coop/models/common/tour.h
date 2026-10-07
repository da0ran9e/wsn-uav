// A Dubins flight path through a handful of points.
//
// The headings at the points are free and so is the visiting order; both are chosen
// to make the path shortest. Closed (the default): a loop the fixed-wing can fly over
// and over -- with 3 points only the two directions of travel differ. Open: a single
// pass, start and end anywhere among the points.
//
// Headings: every 1 degree at every point (exhaustive over the grid, exact for the
// grid), then coordinate descent down to 0.01 degree.

#ifndef UAVCOOP_TOUR_H
#define UAVCOOP_TOUR_H

#include "dubins.h"
#include "hex-grid.h"

#include <vector>

namespace ns3::uavcoop {

struct Tour {
    std::vector<int> order;          // indices into the input points, in flying order
    std::vector<Pose> poses;         // the pose at each point, in flying order
    std::vector<DubinsPath> legs;    // legs[i]: poses[i] -> poses[i+1] (closed: last -> first)
    bool closed = true;
    double length = 0, gridLength = 0;   // after refinement / best on the 1-degree grid
};

Tour PlanTour(const std::vector<Point>& pts, double rho, bool closed);

}  // namespace ns3::uavcoop

#endif
