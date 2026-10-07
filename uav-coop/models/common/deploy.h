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
    // Capabilities, dimensionless. Observation and computation may be 0 (a node that
    // cannot sense, or cannot process); communication is always > 0.
    double obs = 0.0, cpu = 0.0, comm = 0.0;
    bool isCH = false, isCL = false;
    // Strength: high only when ALL three are high, so a node weak in any one
    // capability cannot lead. (Same form as uav-sar's capability = product.)
    double Score() const { return obs * cpu * comm; }
};

uint32_t NodeCount(const HexGrid& g, const Region& reg, double spacingM);
std::vector<SensorNode> DeployNodes(const HexGrid& g, const Region& reg, double spacingM,
                                    CoopRng& rng);

// obs ~ U[0, 1), cpu ~ U[0, 1), comm ~ U(0, 1].
void AssignCapabilities(std::vector<SensorNode>& nodes, CoopRng& rng);

// CH: the strongest node of the whole region. CL: the strongest node of each cell
// that has any (the CH is also its own cell's CL). Ties go to the lower id.
// Returns the index of the CH.
size_t AssignRoles(std::vector<SensorNode>& nodes);

}  // namespace ns3::uavcoop

#endif
