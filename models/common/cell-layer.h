#ifndef WSN_UAV_CELL_LAYER_H
#define WSN_UAV_CELL_LAYER_H

#include "ns3/node-container.h"
#include "ns3/vector.h"

#include <cstdint>
#include <map>
#include <set>
#include <vector>

namespace ns3::wsn::uav {

struct CellLayerConfig {
    double cellSizeMeters = 60.0;
    double neighborRangeMeters = 120.0;
    double originX = 0.0;
    double originY = 0.0;
    uint32_t colorCount = 6;
};

struct CellRoutingInfo {
    uint32_t nodeId = 0;
    int32_t cellId = -1;
    uint32_t cellColor = 0;
    uint32_t cellLeaderId = 0;
    bool isCellLeader = false;
    bool isIsolated = false;
    int32_t parentId = -1;     // next hop toward the cell leader; -1 for leader/unreachable
    uint32_t hopToLeader = 0;  // 0 for leader, max uint32_t for unreachable
    ns3::Vector position;
    std::set<uint32_t> neighbors;
    std::set<uint32_t> twoHopNeighbors;
    std::set<uint32_t> cellPeers;
    std::map<uint32_t, double> neighborDistance;
};

struct CellLayerPlan {
    CellLayerConfig config;
    std::map<uint32_t, CellRoutingInfo> nodes;
    std::map<int32_t, std::vector<uint32_t>> nodesByCell;
    std::map<int32_t, uint32_t> leaderByCell;
};

CellLayerPlan BuildCellLayerPlan(const ns3::NodeContainer& groundNodes,
                                 const CellLayerConfig& config);

}  // namespace ns3::wsn::uav

#endif  // WSN_UAV_CELL_LAYER_H
