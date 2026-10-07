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

// CH: the strongest node among those at least `margin` from the cluster's edge
// (edgeDist[i] for node i). CL: the strongest node of each cell that has any, except
// that the CH leads its own cell. Ties go to the lower id. Positions and capabilities
// are not touched: the margin only narrows who may be CH.
// Returns the index of the CH, or nodes.size() if no node is far enough in.
size_t AssignRoles(std::vector<SensorNode>& nodes, const std::vector<double>& edgeDist,
                   double margin);

}  // namespace ns3::uavcoop

#endif
