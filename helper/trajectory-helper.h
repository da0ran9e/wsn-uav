/*
 * Trajectory planning: GMC (Greedy Maximum Coverage) algorithm
 */

#ifndef WSN_UAV_TRAJECTORY_HELPER_H
#define WSN_UAV_TRAJECTORY_HELPER_H

#include "ns3/node-container.h"
#include "ns3/vector.h"
#include "../models/common/types.h"
#include <cstdint>
#include <set>
#include <map>
#include <vector>

namespace ns3 {
namespace wsn {
namespace uav {

// ============================================================================
// GMC Configuration
// ============================================================================

struct GmcConfig {
    double broadcastRadius = 50.0;       // Rb - coverage radius
    double alpha = 1.0;                   // coverage/cost tradeoff
    double cellCoverageThreshold = 0.30;  // β - cell expansion threshold
    bool useCellAware = true;             // enable cell-aware expansion
    bool useKMeans = true;                // add k-means centroids
    uint32_t maxCentroids = 8;            // max k for k-means
};

// ============================================================================
// TrajectoryHelper Class (static utility methods)
// ============================================================================

class TrajectoryHelper {
public:
    // Plan GMC trajectory: greedy set-cover with k-means + cell-aware expansion
    static std::vector<Waypoint> PlanGmc(
        const std::set<uint32_t>& candidateNodes,
        const NodeContainer& allNodes,
        const std::map<uint32_t, int32_t>& nodeToCell,
        const Vector& startPos,
        double uavSpeed,
        const GmcConfig& cfg = {});
    
    // Simple baseline: nearest-neighbor order
    static std::vector<Waypoint> PlanNearestNeighbor(
        const std::set<uint32_t>& candidateNodes,
        const NodeContainer& allNodes,
        const Vector& startPos,
        double uavSpeed);
    
    // Compute total path length
    static double ComputePathLength(const std::vector<Waypoint>& waypoints,
                                    const Vector& startPos);
    
private:
    // K-means clustering for centroid generation
    static std::vector<Vector> ComputeKMeansCentroids(
        const std::set<uint32_t>& nodes,
        const NodeContainer& allNodes,
        uint32_t k,
        uint32_t maxIterations = 10);
    
    // Compute coverage set for a waypoint (nodes within broadcastRadius)
    static std::set<uint32_t> ComputeCoverageSet(
        const Vector& waypointPos,
        const std::set<uint32_t>& candidates,
        const NodeContainer& allNodes,
        double broadcastRadius);
    
    // Expand coverage set with cell-aware logic
    static std::set<uint32_t> ExpandWithCellAware(
        const std::set<uint32_t>& initialCoverage,
        const std::map<uint32_t, int32_t>& nodeToCell,
        const std::set<uint32_t>& allCandidates,
        double threshold);
};

}  // namespace uav
}  // namespace wsn
}  // namespace ns3

#endif  // WSN_UAV_TRAJECTORY_HELPER_H
