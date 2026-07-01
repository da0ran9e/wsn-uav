#ifndef UAV_SAR_CELL_GRID_H
#define UAV_SAR_CELL_GRID_H

// PECEE-style ground cell substrate (clean reimplementation; ref: main's
// cell-layer + hex-cells-reference, with fixes):
//   - HEXAGONAL cells (pointy-top axial), used consistently (main left hex unused).
//   - Cell Leader = node CLOSEST TO CELL CENTROID (main used lowest id — arbitrary).
//   - Cell color = proper greedy coloring over the actual cell-adjacency graph so
//     adjacent cells always differ (main used cellId%6 — no such guarantee).
//   - Intra-cell routing tree: BFS from leader over in-cell neighbor links.
//
// Deliberately ns-3-INDEPENDENT: operates on plain (id,x,y) positions so it can
// be unit-tested standalone. The network layer feeds it node positions.

#include <cstdint>
#include <map>
#include <set>
#include <vector>

namespace ns3::uavsar {

struct NodePos {
    uint32_t id;
    double x;
    double y;
};

struct CellGridConfig {
    double cellRadius = 80.0;      // hex circumradius (m)
    double neighborRange = 80.0;   // ground link range (m)
};

struct CellNodeInfo {
    uint32_t id = 0;
    double x = 0, y = 0;
    int32_t cellId = -1;
    uint32_t cellColor = 0;
    uint32_t leaderId = 0;
    bool isLeader = false;
    int32_t parentId = -1;                 // next hop toward leader; -1 = leader/unreachable
    uint32_t hopToLeader = 0xFFFFFFFF;     // 0 = leader; max = unreachable
    std::set<uint32_t> neighbors;          // ids within neighborRange (any cell)
};

struct CellInfo {
    int32_t cellId = -1;
    int32_t q = 0, r = 0;                  // axial coords
    double centerX = 0, centerY = 0;
    uint32_t leaderId = 0;
    uint32_t color = 0;
    std::vector<uint32_t> members;
    std::set<int32_t> adjacentCells;       // radio-adjacent cells (share a cross-cell link)
};

struct CellGridPlan {
    CellGridConfig config;
    std::map<uint32_t, CellNodeInfo> nodes;   // by node id
    std::map<int32_t, CellInfo> cells;        // by cell id
    uint32_t colorCount = 0;                   // colors used
};

// Build the full plan from node positions.
CellGridPlan BuildCellGrid(const std::vector<NodePos>& nodes,
                           const CellGridConfig& cfg);

// --- hex helpers (pointy-top axial, size = cellRadius) ---------------------
namespace hex {
void   WorldToAxial(double x, double y, double size, int32_t& q, int32_t& r);
void   AxialToCenter(int32_t q, int32_t r, double size, double& cx, double& cy);
}  // namespace hex

}  // namespace ns3::uavsar

#endif  // UAV_SAR_CELL_GRID_H
