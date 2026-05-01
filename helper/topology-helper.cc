#include "topology-helper.h"
#include "ns3/random-variable-stream.h"
#include "ns3/rng-seed-manager.h"
#include "ns3/mobility-helper.h"
#include "ns3/constant-position-mobility-model.h"
#include <cmath>
#include <algorithm>

namespace ns3 {
namespace wsn {
namespace uav {

// ============================================================================
// TopologyHelper::CreateGrid()
// ============================================================================

NodeContainer TopologyHelper::CreateGrid(uint32_t gridSize, double spacing, double z) {
    NodeContainer nodes;
    nodes.Create(gridSize * gridSize);
    
    MobilityHelper mobility;
    mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    mobility.Install(nodes);
    
    // Position nodes in NxN grid
    uint32_t idx = 0;
    for (uint32_t i = 0; i < gridSize; i++) {
        for (uint32_t j = 0; j < gridSize; j++) {
            double x = i * spacing;
            double y = j * spacing;
            
            auto mob = nodes.Get(idx)->GetObject<MobilityModel>();
            mob->SetPosition(Vector(x, y, z));
            idx++;
        }
    }
    
    return nodes;
}

// ============================================================================
// TopologyHelper::BuildCellStructure()
// ============================================================================

CellInfo TopologyHelper::BuildCellStructure(NodeContainer nodes, double cellRadius) {
    CellInfo cellInfo;
    
    // 1. Assign cells based on position
    for (uint32_t i = 0; i < nodes.GetN(); i++) {
        auto mob = nodes.Get(i)->GetObject<MobilityModel>();
        int32_t cellId = ComputeHexCellId(mob->GetPosition(), cellRadius);
        cellInfo.nodeToCell[i] = cellId;
    }
    
    // 2. Find neighbors within radius
    cellInfo.neighbors = FindNeighbors(nodes, cellRadius);
    
    // 3. Elect cell leaders
    std::map<int32_t, std::set<uint32_t>> cellMembers;
    for (const auto& [nodeId, cellId] : cellInfo.nodeToCell) {
        cellMembers[cellId].insert(nodeId);
    }
    
    for (auto& [cellId, members] : cellMembers) {
        // Leader = node closest to cell centroid
        Vector centroid = ComputeCellCentroid(members, nodes);
        
        uint32_t leaderId = *members.begin();
        double minDist = std::numeric_limits<double>::max();
        
        for (uint32_t nodeId : members) {
            auto mob = nodes.Get(nodeId)->GetObject<MobilityModel>();
            Vector pos = mob->GetPosition();
            double dist = CalculateDistance(pos, centroid);
            
            if (dist < minDist) {
                minDist = dist;
                leaderId = nodeId;
            }
        }
        
        cellInfo.cellLeader[cellId] = leaderId;
    }
    
    // 4. Compute BFS levels from cell leaders
    for (const auto& [nodeId, cellId] : cellInfo.nodeToCell) {
        cellInfo.bfsLevel[nodeId] = 0;  // Simplified: no tree depth for now
    }
    
    return cellInfo;
}

// ============================================================================
// TopologyHelper::SelectCandidates()
// ============================================================================

std::set<uint32_t> TopologyHelper::SelectCandidates(const NodeContainer& nodes,
                                                     const CellInfo& cells,
                                                     double fraction,
                                                     uint32_t seed) {
    std::set<uint32_t> candidates;
    uint32_t targetCount = static_cast<uint32_t>(nodes.GetN() * fraction);

    // Random selection: pick random starting node, then BFS expansion
    Ptr<UniformRandomVariable> rng = CreateObject<UniformRandomVariable>();
    rng->SetStream(seed);

    // Start with random node
    uint32_t seedNodeId = static_cast<uint32_t>(rng->GetValue(0, nodes.GetN()));

    // BFS expansion from seed
    std::set<uint32_t> visited;
    std::queue<uint32_t> frontier;

    frontier.push(seedNodeId);
    visited.insert(seedNodeId);
    candidates.insert(seedNodeId);

    while (!frontier.empty() && candidates.size() < targetCount) {
        uint32_t current = frontier.front();
        frontier.pop();

        // Add neighbors from same or adjacent cells
        auto it = cells.neighbors.find(current);
        if (it != cells.neighbors.end()) {
            for (uint32_t neighbor : it->second) {
                if (visited.count(neighbor) == 0) {
                    visited.insert(neighbor);
                    candidates.insert(neighbor);
                    frontier.push(neighbor);

                    if (candidates.size() >= targetCount) break;
                }
            }
        }
    }

    return candidates;
}

// ============================================================================
// TopologyHelper::SelectDetectionNode()
// ============================================================================

uint32_t TopologyHelper::SelectDetectionNode(const std::set<uint32_t>& candidates, uint32_t seed) {
    Ptr<UniformRandomVariable> rng = CreateObject<UniformRandomVariable>();
    rng->SetStream(seed);
    
    auto it = candidates.begin();
    uint32_t idx = static_cast<uint32_t>(rng->GetValue(0, candidates.size()));
    std::advance(it, idx);
    
    return *it;
}

// ============================================================================
// TopologyHelper::FindNeighbors()
// ============================================================================

std::map<uint32_t, std::set<uint32_t>> TopologyHelper::FindNeighbors(const NodeContainer& nodes,
                                                                      double radius) {
    std::map<uint32_t, std::set<uint32_t>> neighbors;
    
    for (uint32_t i = 0; i < nodes.GetN(); i++) {
        auto mobI = nodes.Get(i)->GetObject<MobilityModel>();
        Vector posI = mobI->GetPosition();
        
        for (uint32_t j = 0; j < nodes.GetN(); j++) {
            if (i == j) continue;
            
            auto mobJ = nodes.Get(j)->GetObject<MobilityModel>();
            Vector posJ = mobJ->GetPosition();
            
            double dist = CalculateDistance(posI, posJ);
            if (dist <= radius) {
                neighbors[i].insert(j);
            }
        }
    }
    
    return neighbors;
}

// ============================================================================
// TopologyHelper::ComputeHexCellId()
// ============================================================================

int32_t TopologyHelper::ComputeHexCellId(const Vector& pos, double cellRadius) {
    // Simplified hex grid: q*prime + r where q,r from axial coordinates
    int32_t q = static_cast<int32_t>(pos.x / cellRadius);
    int32_t r = static_cast<int32_t>(pos.y / cellRadius);
    
    return q * 1000 + r;  // Simple hash
}

// ============================================================================
// TopologyHelper::ComputeCellCentroid()
// ============================================================================

Vector TopologyHelper::ComputeCellCentroid(const std::set<uint32_t>& members,
                                           const NodeContainer& nodes) {
    if (members.empty()) return Vector(0, 0, 0);
    
    double sumX = 0, sumY = 0, sumZ = 0;
    for (uint32_t nodeId : members) {
        auto mob = nodes.Get(nodeId)->GetObject<MobilityModel>();
        Vector pos = mob->GetPosition();
        sumX += pos.x;
        sumY += pos.y;
        sumZ += pos.z;
    }
    
    return Vector(sumX / members.size(), sumY / members.size(), sumZ / members.size());
}

}  // namespace uav
}  // namespace wsn
}  // namespace ns3
