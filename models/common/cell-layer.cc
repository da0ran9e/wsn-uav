#include "cell-layer.h"

#include "ns3/mobility-model.h"
#include "ns3/node.h"

#include <algorithm>
#include <cmath>
#include <limits>
#include <queue>

namespace ns3::wsn::uav {

namespace {

double Distance2d(const Vector& a, const Vector& b) {
    double dx = a.x - b.x;
    double dy = a.y - b.y;
    return std::sqrt(dx * dx + dy * dy);
}

std::pair<int32_t, int32_t> CellCoord(const Vector& pos, const CellLayerConfig& cfg) {
    int32_t cx = static_cast<int32_t>(std::floor((pos.x - cfg.originX) / cfg.cellSizeMeters));
    int32_t cy = static_cast<int32_t>(std::floor((pos.y - cfg.originY) / cfg.cellSizeMeters));
    return {cx, cy};
}

}  // namespace

CellLayerPlan BuildCellLayerPlan(const NodeContainer& groundNodes,
                                 const CellLayerConfig& config) {
    CellLayerPlan plan;
    plan.config = config;

    std::map<std::pair<int32_t, int32_t>, int32_t> cellIdByCoord;
    int32_t nextCellId = 0;

    for (uint32_t i = 0; i < groundNodes.GetN(); i++) {
        Ptr<Node> node = groundNodes.Get(i);
        Ptr<MobilityModel> mob = node ? node->GetObject<MobilityModel>() : nullptr;
        if (!node || !mob) continue;

        CellRoutingInfo info;
        info.nodeId = node->GetId();
        info.position = mob->GetPosition();

        auto coord = CellCoord(info.position, config);
        auto [cellIt, inserted] = cellIdByCoord.emplace(coord, nextCellId);
        if (inserted) nextCellId++;
        info.cellId = cellIt->second;
        info.cellColor = (config.colorCount > 0)
                             ? static_cast<uint32_t>(info.cellId) % config.colorCount
                             : 0;
        info.cellLeaderId = info.nodeId;
        info.hopToLeader = std::numeric_limits<uint32_t>::max();

        plan.nodes.emplace(info.nodeId, std::move(info));
    }

    for (auto itA = plan.nodes.begin(); itA != plan.nodes.end(); ++itA) {
        auto itB = itA;
        ++itB;
        for (; itB != plan.nodes.end(); ++itB) {
            double d = Distance2d(itA->second.position, itB->second.position);
            if (d <= config.neighborRangeMeters) {
                itA->second.neighbors.insert(itB->first);
                itB->second.neighbors.insert(itA->first);
                itA->second.neighborDistance[itB->first] = d;
                itB->second.neighborDistance[itA->first] = d;
            }
        }
    }

    for (const auto& [nodeId, info] : plan.nodes) {
        plan.nodesByCell[info.cellId].push_back(nodeId);
    }

    for (auto& [cellId, members] : plan.nodesByCell) {
        std::sort(members.begin(), members.end());
        uint32_t leader = members.front();
        plan.leaderByCell[cellId] = leader;
        for (uint32_t nodeId : members) {
            CellRoutingInfo& info = plan.nodes[nodeId];
            info.cellLeaderId = leader;
            info.isCellLeader = (nodeId == leader);
            for (uint32_t peerId : members) {
                if (peerId != nodeId) info.cellPeers.insert(peerId);
            }
        }
    }

    for (auto& [nodeId, info] : plan.nodes) {
        for (uint32_t neighborId : info.neighbors) {
            auto neighborIt = plan.nodes.find(neighborId);
            if (neighborIt == plan.nodes.end()) continue;
            for (uint32_t twoHopId : neighborIt->second.neighbors) {
                if (twoHopId != nodeId && info.neighbors.find(twoHopId) == info.neighbors.end()) {
                    info.twoHopNeighbors.insert(twoHopId);
                }
            }
        }
        info.isIsolated = info.neighbors.empty();
    }

    for (const auto& [cellId, members] : plan.nodesByCell) {
        uint32_t leader = plan.leaderByCell[cellId];
        std::queue<uint32_t> q;
        plan.nodes[leader].hopToLeader = 0;
        plan.nodes[leader].parentId = -1;
        q.push(leader);

        while (!q.empty()) {
            uint32_t cur = q.front();
            q.pop();
            uint32_t nextHop = plan.nodes[cur].hopToLeader + 1;

            for (uint32_t neighborId : plan.nodes[cur].neighbors) {
                auto neighborIt = plan.nodes.find(neighborId);
                if (neighborIt == plan.nodes.end() || neighborIt->second.cellId != cellId) {
                    continue;
                }
                if (neighborIt->second.hopToLeader <= nextHop) continue;

                neighborIt->second.hopToLeader = nextHop;
                neighborIt->second.parentId = static_cast<int32_t>(cur);
                q.push(neighborId);
            }
        }
    }

    return plan;
}

}  // namespace ns3::wsn::uav
