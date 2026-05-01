#include "trajectory-helper.h"
#include "ns3/mobility-model.h"
#include <cmath>
#include <algorithm>
#include <limits>
#include <numeric>
#include <iterator>

namespace ns3 {
namespace wsn {
namespace uav {

// ============================================================================
// TrajectoryHelper::PlanGmc() - Greedy Maximum Coverage
// ============================================================================

std::vector<Waypoint> TrajectoryHelper::PlanGmc(
    const std::set<uint32_t>& candidateNodes,
    const NodeContainer& allNodes,
    const std::map<uint32_t, int32_t>& nodeToCell,
    const Vector& startPos,
    double uavSpeed,
    const GmcConfig& cfg) {

    std::vector<Waypoint> waypoints;
    if (candidateNodes.empty()) return waypoints;

    // Simplified K-means approach: compute centroids and visit in nearest-neighbor order
    uint32_t k = std::min(cfg.maxCentroids, (uint32_t)std::max(1u, (uint32_t)(candidateNodes.size() / 8)));
    auto centroids = ComputeKMeansCentroids(candidateNodes, allNodes, k);

    // Nearest-neighbor visiting of centroids
    std::set<size_t> visited;
    Vector currentPos = startPos;
    double cumulativeTime = 0.0;

    while (visited.size() < centroids.size()) {
        // Find nearest unvisited centroid
        size_t nearest = 0;
        double minDist = std::numeric_limits<double>::max();

        for (size_t i = 0; i < centroids.size(); i++) {
            if (visited.count(i)) continue;
            double dist = CalculateDistance(currentPos, centroids[i]);
            if (dist < minDist) {
                minDist = dist;
                nearest = i;
            }
        }

        visited.insert(nearest);
        double travelTime = minDist / uavSpeed;
        cumulativeTime += travelTime;

        Waypoint wp;
        wp.x = centroids[nearest].x;
        wp.y = centroids[nearest].y;
        wp.z = centroids[nearest].z;
        wp.arrivalTimeSec = cumulativeTime;

        waypoints.push_back(wp);
        currentPos = centroids[nearest];
    }

    // Return to starting position
    double returnDist = CalculateDistance(currentPos, startPos);
    double returnTime = returnDist / uavSpeed;
    cumulativeTime += returnTime;

    Waypoint returnWp;
    returnWp.x = startPos.x;
    returnWp.y = startPos.y;
    returnWp.z = startPos.z;
    returnWp.arrivalTimeSec = cumulativeTime;
    waypoints.push_back(returnWp);

    return waypoints;
}

// ============================================================================
// TrajectoryHelper::PlanNearestNeighbor()
// ============================================================================

std::vector<Waypoint> TrajectoryHelper::PlanNearestNeighbor(
    const std::set<uint32_t>& candidateNodes,
    const NodeContainer& allNodes,
    const Vector& startPos,
    double uavSpeed) {
    
    std::vector<Waypoint> waypoints;
    std::set<uint32_t> visited;
    Vector currentPos = startPos;
    
    while (visited.size() < candidateNodes.size()) {
        // Find nearest unvisited candidate
        uint32_t nearest = UINT32_MAX;
        double minDist = std::numeric_limits<double>::max();
        
        for (uint32_t nodeId : candidateNodes) {
            if (visited.count(nodeId)) continue;
            
            auto mob = allNodes.Get(nodeId)->GetObject<MobilityModel>();
            Vector pos = mob->GetPosition();
            double dist = CalculateDistance(currentPos, pos);
            
            if (dist < minDist) {
                minDist = dist;
                nearest = nodeId;
            }
        }
        
        if (nearest == UINT32_MAX) break;
        
        // Add waypoint
        auto mob = allNodes.Get(nearest)->GetObject<MobilityModel>();
        Vector pos = mob->GetPosition();
        double arrivalTime = minDist / uavSpeed;
        
        Waypoint wp;
        wp.x = pos.x;
        wp.y = pos.y;
        wp.z = pos.z;
        wp.arrivalTimeSec = waypoints.empty() ? arrivalTime : 
                             (waypoints.back().arrivalTimeSec + arrivalTime);
        
        waypoints.push_back(wp);
        visited.insert(nearest);
        currentPos = pos;
    }

    // Return to starting position
    double returnDist = CalculateDistance(currentPos, startPos);
    double returnTime = returnDist / uavSpeed;

    Waypoint returnWp;
    returnWp.x = startPos.x;
    returnWp.y = startPos.y;
    returnWp.z = startPos.z;
    returnWp.arrivalTimeSec = waypoints.empty() ? returnTime :
                               (waypoints.back().arrivalTimeSec + returnTime);

    waypoints.push_back(returnWp);

    return waypoints;
}

// ============================================================================
// TrajectoryHelper::ComputePathLength()
// ============================================================================

double TrajectoryHelper::ComputePathLength(const std::vector<Waypoint>& waypoints,
                                           const Vector& startPos) {
    if (waypoints.empty()) return 0.0;
    
    double length = 0.0;
    Vector current = startPos;
    
    for (const auto& wp : waypoints) {
        Vector next(wp.x, wp.y, wp.z);
        length += CalculateDistance(current, next);
        current = next;
    }
    
    return length;
}

// ============================================================================
// TrajectoryHelper::ComputeKMeansCentroids()
// ============================================================================

std::vector<Vector> TrajectoryHelper::ComputeKMeansCentroids(
    const std::set<uint32_t>& nodes,
    const NodeContainer& allNodes,
    uint32_t k,
    uint32_t maxIterations) {

    if (nodes.size() < k) {
        std::vector<Vector> result;
        for (uint32_t nodeId : nodes) {
            auto mob = allNodes.Get(nodeId)->GetObject<MobilityModel>();
            result.push_back(mob->GetPosition());
        }
        return result;
    }

    // Collect positions
    std::vector<Vector> positions;
    std::vector<uint32_t> nodeIds;
    for (uint32_t nodeId : nodes) {
        auto mob = allNodes.Get(nodeId)->GetObject<MobilityModel>();
        positions.push_back(mob->GetPosition());
        nodeIds.push_back(nodeId);
    }

    // Initialize centroids: spread across positions
    std::vector<Vector> centroids;
    for (uint32_t i = 0; i < k && i < positions.size(); i++) {
        centroids.push_back(positions[i * positions.size() / k]);
    }

    // K-means iteration
    for (uint32_t iter = 0; iter < maxIterations; iter++) {
        // Assign each point to nearest centroid
        std::vector<std::vector<Vector>> clusters(k);
        for (size_t i = 0; i < positions.size(); i++) {
            double minDist = std::numeric_limits<double>::max();
            uint32_t bestCluster = 0;

            for (uint32_t j = 0; j < k; j++) {
                double dist = CalculateDistance(positions[i], centroids[j]);
                if (dist < minDist) {
                    minDist = dist;
                    bestCluster = j;
                }
            }
            clusters[bestCluster].push_back(positions[i]);
        }

        // Recompute centroids
        std::vector<Vector> newCentroids;
        for (uint32_t j = 0; j < k; j++) {
            if (clusters[j].empty()) {
                newCentroids.push_back(centroids[j]);  // Keep old centroid if empty
            } else {
                Vector sum(0, 0, 0);
                for (const auto& p : clusters[j]) {
                    sum.x += p.x;
                    sum.y += p.y;
                    sum.z += p.z;
                }
                sum.x /= clusters[j].size();
                sum.y /= clusters[j].size();
                sum.z /= clusters[j].size();
                newCentroids.push_back(sum);
            }
        }

        // Check convergence
        bool converged = true;
        for (uint32_t j = 0; j < k; j++) {
            if (CalculateDistance(centroids[j], newCentroids[j]) > 0.1) {
                converged = false;
                break;
            }
        }

        centroids = newCentroids;
        if (converged) break;
    }

    return centroids;
}

// ============================================================================
// TrajectoryHelper::ComputeCoverageSet()
// ============================================================================

std::set<uint32_t> TrajectoryHelper::ComputeCoverageSet(
    const Vector& waypointPos,
    const std::set<uint32_t>& candidates,
    const NodeContainer& allNodes,
    double broadcastRadius) {
    
    std::set<uint32_t> coverage;
    
    for (uint32_t nodeId : candidates) {
        auto mob = allNodes.Get(nodeId)->GetObject<MobilityModel>();
        Vector nodePos = mob->GetPosition();
        double dist = CalculateDistance(waypointPos, nodePos);
        
        if (dist <= broadcastRadius) {
            coverage.insert(nodeId);
        }
    }
    
    return coverage;
}

// ============================================================================
// TrajectoryHelper::ExpandWithCellAware()
// ============================================================================

std::set<uint32_t> TrajectoryHelper::ExpandWithCellAware(
    const std::set<uint32_t>& initialCoverage,
    const std::map<uint32_t, int32_t>& nodeToCell,
    const std::set<uint32_t>& allCandidates,
    double threshold) {
    
    std::set<uint32_t> expanded = initialCoverage;
    
    // Count coverage per cell
    std::map<int32_t, uint32_t> cellCovered;
    std::map<int32_t, uint32_t> cellTotal;
    
    for (uint32_t nodeId : allCandidates) {
        auto it = nodeToCell.find(nodeId);
        if (it == nodeToCell.end()) continue;
        
        int32_t cellId = it->second;
        cellTotal[cellId]++;
        
        if (initialCoverage.count(nodeId)) {
            cellCovered[cellId]++;
        }
    }
    
    // Expand to full cells with >=threshold coverage
    for (const auto& [cellId, covered] : cellCovered) {
        double coverageRatio = static_cast<double>(covered) / cellTotal[cellId];

        if (coverageRatio >= threshold) {
            // Add all nodes in this cell
            for (uint32_t nodeId : allCandidates) {
                auto it = nodeToCell.find(nodeId);
                if (it != nodeToCell.end() && it->second == cellId) {
                    expanded.insert(nodeId);
                }
            }
        }
    }
    
    return expanded;
}

}  // namespace uav
}  // namespace wsn
}  // namespace ns3
