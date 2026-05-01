/*
 * Topology helper: grid creation, cell assignment, candidate selection
 */

#ifndef WSN_UAV_TOPOLOGY_HELPER_H
#define WSN_UAV_TOPOLOGY_HELPER_H

#include "ns3/node-container.h"
#include "ns3/vector.h"
#include <cstdint>
#include <map>
#include <set>

namespace ns3 {
namespace wsn {
namespace uav {

// ============================================================================
// CellInfo Structure
// ============================================================================

struct CellInfo {
    std::map<uint32_t, int32_t> nodeToCell;       // nodeId → cellId
    std::map<int32_t, uint32_t> cellLeader;       // cellId → leader nodeId
    std::map<uint32_t, std::set<uint32_t>> neighbors;  // nodeId → neighbor nodeIds
    std::map<uint32_t, uint32_t> bfsLevel;        // nodeId → hop count to cell leader
};

// ============================================================================
// TopologyHelper Class (static utility methods)
// ============================================================================

class TopologyHelper {
public:
    // Create grid of N nodes (NxN layout with spacing s)
    static NodeContainer CreateGrid(uint32_t gridSize, double spacing, double z = 0.0);
    
    // Assign hex cell IDs and elect leaders
    static CellInfo BuildCellStructure(NodeContainer nodes, double cellRadius);
    
    // Select candidate nodes (suspicious region) - random seed-based
    static std::set<uint32_t> SelectCandidates(const NodeContainer& nodes,
                                               const CellInfo& cells,
                                               double fraction,
                                               uint32_t seed);
    
    // Pick detection node (n*) - the seed node of suspicious region
    static uint32_t SelectDetectionNode(const std::set<uint32_t>& candidates, uint32_t seed);
    
    // Find neighbors within radius for all nodes
    static std::map<uint32_t, std::set<uint32_t>> FindNeighbors(const NodeContainer& nodes,
                                                                  double radius);
    
private:
    // Hex grid coordinate assignment
    static int32_t ComputeHexCellId(const Vector& pos, double cellRadius);
    
    // Compute fitness score for cell leader election
    static double ComputeLeaderFitness(const Vector& nodePos, const Vector& cellCentroid);
    
    // Compute cell centroid from member positions
    static Vector ComputeCellCentroid(const std::set<uint32_t>& members,
                                     const NodeContainer& nodes);
};

}  // namespace uav
}  // namespace wsn
}  // namespace ns3

#endif  // WSN_UAV_TOPOLOGY_HELPER_H
