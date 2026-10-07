// Pre-built routes over the cell overlay (PECEE elastic clustering), planned centrally
// (at the BS) before the mission.
//
// Links: two nodes at most `range` apart. Planned centrally, so no node may be left
// out: inside every cell the components are joined by the shortest extra links that
// connect them (a minimum spanning forest over the components), and every pair of
// adjacent cells gets a gateway link, the shortest cross pair if none is in range.
// These "bridge" links are longer than `range`, hence weaker; they are listed.
//
// Gateways: for each pair of adjacent cells A, B there is exactly ONE link a-b
// (a in A, b in B). All traffic between A and B crosses it, both ways. Chosen among
// the cross links in range: fewest hops a->CL(A) + b->CL(B), then shortest.
//
// Every node stores:
//   toCL           next hop toward its own cell's CL, inside the cell
//   toCell[B]      for each adjacent cell B: next hop toward the gateway a of A->B,
//                  inside the cell; at a itself, the hop a->b
//   main           which of those stored next hops starts the shortest route to the
//                  CH, when every node on the way also forwards along one of its own
//                  stored next hops. (The CH is its cell's CL.)
// "Shortest" is fewest hops, ties broken by fewer metres.
//
// Every route crosses cells only at gateways, and the main route is loop-free: every
// hop lowers the remaining hop count by exactly one (checked by the caller).

#ifndef UAVCOOP_ROUTING_H
#define UAVCOOP_ROUTING_H

#include "deploy.h"
#include "hex-grid.h"

#include <cstdint>
#include <limits>
#include <map>
#include <utility>
#include <vector>

namespace ns3::uavcoop {

constexpr int32_t kNoHop = -1;
constexpr uint32_t kNoRoute = std::numeric_limits<uint32_t>::max();

struct CellHop {
    int32_t next = kNoHop;      // node index
    uint32_t hops = kNoRoute;   // hops until the target (CL, or the far gateway b)
    double metres = 0;
};

struct RouteTable {
    CellHop toCL;
    std::map<Hex, CellHop> toCell;      // one per adjacent region cell
    int32_t mainNext = kNoHop;          // the main route's next hop
    bool mainViaCL = false;             // true: toCL; false: toCell[mainCell]
    Hex mainCell;
    uint32_t hopsToCH = kNoRoute;
    double metresToCH = 0;
};

struct Gateway {
    int32_t a = kNoHop, b = kNoHop;     // a in the first cell, b in the second
    double metres = 0;
    bool bridge = false;                // longer than range: added to connect
};

struct Bridge {
    int32_t a, b;
    double metres;
    bool gateway;                       // false: joins components inside one cell
};

struct Routing {
    std::vector<std::vector<int32_t>> links;   // neighbours of each node (bridges included)
    std::vector<Bridge> bridges;
    std::map<std::pair<Hex, Hex>, Gateway> gateway;   // (A, B) -> link; (B, A) mirrored
    std::vector<RouteTable> table;
};

Routing BuildRouting(const std::vector<SensorNode>& nodes, size_t ch, double range);

// Hops from every node to `to` over all links, ignoring cells (a lower bound).
std::vector<uint32_t> FreeHops(const Routing& r, size_t to);

}  // namespace ns3::uavcoop

#endif
