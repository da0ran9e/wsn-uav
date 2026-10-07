// Random sensor nodes inside a region of cells.
//
// Density is set by the spacing s: one node per s^2 of area, so the region holds
// round(area / s^2) nodes. Placement is uniform over the region (every point equally
// likely, independently): pick a cell uniformly -- all cells have the same area --
// then a uniform point inside its hexagon by rejection from the bounding box.
// Uniform means clumps and gaps are expected; it is not a jittered grid.

#ifndef UAVCOOP_DEPLOY_H
#define UAVCOOP_DEPLOY_H

#include "coop-rng.h"
#include "hex-grid.h"
#include "region.h"

#include <cstdint>
#include <vector>

namespace ns3::uavcoop {

struct SensorNode {
    uint32_t id = 0;
    Point pos;
    Hex cell;
};

uint32_t NodeCount(const HexGrid& g, const Region& reg, double spacingM);
std::vector<SensorNode> DeployNodes(const HexGrid& g, const Region& reg, double spacingM,
                                    CoopRng& rng);

}  // namespace ns3::uavcoop

#endif
