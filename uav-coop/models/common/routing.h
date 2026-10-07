// Pre-built routes over the cell overlay (PECEE elastic clustering).
//
// Two nodes are linked if they are at most `range` apart. Every node stores:
//   toCL           next hop toward its own cell's CL, along links inside the cell
//   toCell[B]      for each adjacent cell B of the region: next hop toward the
//                  nearest node of B, along links inside its own cell and B
//   main           which of those stored next hops starts the shortest route to the
//                  CH, when every node on the way also forwards along one of its own
//                  stored next hops. (The CH is its cell's CL, so inside the CH's cell
//                  this is normally toCL.)
// "Shortest" is fewest hops, ties broken by fewer metres.
//
// The main route is loop-free: every hop along it lowers the remaining hop count by
// exactly one (checked by the caller).

#ifndef UAVCOOP_ROUTING_H
#define UAVCOOP_ROUTING_H

#include "deploy.h"
#include "hex-grid.h"

#include <cstdint>
#include <limits>
#include <map>
#include <vector>

namespace ns3::uavcoop {

constexpr int32_t kNoHop = -1;
constexpr uint32_t kNoRoute = std::numeric_limits<uint32_t>::max();

struct CellHop {
    int32_t next = kNoHop;      // node index
    uint32_t hops = kNoRoute;   // hops until the first node of the target
    double metres = 0;
    int32_t entry = kNoHop;     // the first node reached in the target cell
};

struct RouteTable {
    CellHop toCL;                       // entry = the CL
    std::map<Hex, CellHop> toCell;      // one per adjacent region cell
    int32_t mainNext = kNoHop;          // the main route's next hop
    bool mainViaCL = false;             // true: toCL; false: toCell[mainCell]
    Hex mainCell;
    uint32_t hopsToCH = kNoRoute;
    double metresToCH = 0;
};

struct Routing {
    std::vector<std::vector<int32_t>> links;   // neighbours of each node, by index
    std::vector<RouteTable> table;
};

Routing BuildRouting(const std::vector<SensorNode>& nodes, size_t ch, double range);

// Hops from every node to `to` over all links, ignoring cells (a lower bound).
std::vector<uint32_t> FreeHops(const Routing& r, size_t to);

}  // namespace ns3::uavcoop

#endif
