#ifndef UAV_SAR_INTER_CELL_ROUTING_H
#define UAV_SAR_INTER_CELL_ROUTING_H

// Inter-cell routing over the PECEE cell substrate (NEW; main had none).
// Enables cross-cell cooperation: cell leaders in different cells can exchange
// clue evidence so multiple cameras spanning several cells produce ONE summon.
//
//   - Cell Gateway (CGW): for each adjacent cell pair (A,B), the boundary node
//     in A (and its peer in B) that best bridges the two, preferring nodes near
//     their own leaders and a short cross-cell link.
//   - CellRoute: shortest cell-hop path over the cell-adjacency graph.
//   - LeaderPath: full ground node path CL(A) → … → CL(B), stitched through the
//     intra-cell trees and the CGW links (for costing via the cooperation model).

#include "cell-grid.h"

#include <cstdint>
#include <map>
#include <vector>

namespace ns3::uavsar {

struct GatewayLink {
    uint32_t localGw = 0;   // boundary node in the source cell
    uint32_t remoteGw = 0;  // its peer in the adjacent cell
    double linkDist = 0;    // cross-cell link length (m)
};

struct InterCellRouting {
    // gateway[A][B] = how to step from cell A into adjacent cell B.
    std::map<int32_t, std::map<int32_t, GatewayLink>> gateway;
};

InterCellRouting BuildInterCellRouting(const CellGridPlan& plan);

// Shortest cell-hop path (inclusive of src and dst). Empty if unreachable.
std::vector<int32_t> CellRoute(const CellGridPlan& plan,
                               int32_t srcCell, int32_t dstCell);

// Full ground node path from leader(srcCell) to leader(dstCell), stitched via
// intra-cell trees + CGW hops. Empty if unreachable.
std::vector<uint32_t> LeaderPath(const CellGridPlan& plan,
                                 const InterCellRouting& routing,
                                 int32_t srcCell, int32_t dstCell);

}  // namespace ns3::uavsar

#endif  // UAV_SAR_INTER_CELL_ROUTING_H
