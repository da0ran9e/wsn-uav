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

    // Calculate grid extent from node positions
    double minX = std::numeric_limits<double>::max(), maxX = -std::numeric_limits<double>::max();
    double minY = std::numeric_limits<double>::max(), maxY = -std::numeric_limits<double>::max();
    for (uint32_t nodeId : candidateNodes) {
        Vector pos = allNodes.Get(nodeId)->GetObject<MobilityModel>()->GetPosition();
        minX = std::min(minX, pos.x);
        maxX = std::max(maxX, pos.x);
        minY = std::min(minY, pos.y);
        maxY = std::max(maxY, pos.y);
    }

    double gridWidth = maxX - minX;
    double gridHeight = maxY - minY;
    double gridDiameter = std::max(gridWidth, gridHeight);

    // Calculate k dynamically: ensure no gap between waypoints
    // k must be sufficient so that 2 * broadcastRadius >= gridDiameter / k
    // Therefore: k >= gridDiameter / (2 * broadcastRadius)
    uint32_t minCentroids = (uint32_t)std::ceil(gridDiameter / (2.0 * cfg.broadcastRadius));

    // Also consider nodes density: at least 1 centroid per 8 nodes
    uint32_t nodeBasedCentroids = (uint32_t)std::max(1u, (uint32_t)(candidateNodes.size() / 8));

    // Take the maximum to ensure full coverage
    uint32_t k = std::max(minCentroids, nodeBasedCentroids);
    k = std::min(k, cfg.maxCentroids);  // Cap at maxCentroids for performance

    // Phase 1: Dynamic k per UAV based on speed
    // Faster UAVs handle more complex paths (higher k)
    // Assign different k for each UAV based on relative speed percentile
    if (cfg.uavSpeed > 0) {
        // Thresholds are flexible; use percentiles relative to expected speed range
        // For base speed 80 m/s: slow≈48, medium≈52, fast≈62
        double speedFactor = 0.8;  // slow UAV default
        if (cfg.uavSpeed >= 60.0) {
            speedFactor = 1.2;  // fast UAV
        } else if (cfg.uavSpeed >= 50.0) {
            speedFactor = 1.0;  // medium UAV
        }
        uint32_t speedAdjustedK = (uint32_t)std::ceil(k * speedFactor);
        k = std::min(speedAdjustedK, cfg.maxCentroids);
    }

    // Debug: Print k calculation
    std::cerr << "[GMC] gridDiameter=" << gridDiameter << "m, speed=" << cfg.uavSpeed << " m/s, "
              << "minCentroids=" << minCentroids << ", nodeBasedCentroids=" << nodeBasedCentroids
              << ", speedAdjustedK=" << k << ", maxCentroids=" << cfg.maxCentroids << std::endl;

    auto centroids = ComputeKMeansCentroids(candidateNodes, allNodes, k, 10, cfg.randomSeed);

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
        wp.z = startPos.z;  // Keep UAV at specified altitude instead of dropping to Z=0
        wp.arrivalTimeSec = cumulativeTime;

        waypoints.push_back(wp);
        currentPos = Vector(centroids[nearest].x, centroids[nearest].y, startPos.z);
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
        wp.z = startPos.z; // Keep UAV at specified altitude
        wp.arrivalTimeSec = waypoints.empty() ? arrivalTime : 
                             (waypoints.back().arrivalTimeSec + arrivalTime);
        
        waypoints.push_back(wp);
        visited.insert(nearest);
        currentPos = Vector(pos.x, pos.y, startPos.z);
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
    uint32_t maxIterations,
    uint32_t randomSeed) {

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

    // Initialize centroids: random selection if seed > 0, else spread across positions
    std::vector<Vector> centroids;
    if (randomSeed > 0) {
        // Random initialization: pick k random positions as initial centroids
        srand(randomSeed);
        std::vector<bool> used(positions.size(), false);
        for (uint32_t i = 0; i < k && i < positions.size(); i++) {
            uint32_t randomIdx;
            do {
                randomIdx = rand() % positions.size();
            } while (used[randomIdx] && i < positions.size());
            used[randomIdx] = true;
            centroids.push_back(positions[randomIdx]);
        }
    } else {
        // Spread initialization: space centroids evenly
        for (uint32_t i = 0; i < k && i < positions.size(); i++) {
            centroids.push_back(positions[i * positions.size() / k]);
        }
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
