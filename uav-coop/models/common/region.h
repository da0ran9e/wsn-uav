// A random contiguous set of cells, made more convex on demand.
//
// 1  Eden growth from the origin's cell: at every step one cell is drawn uniformly
//    from the frontier (unselected cells touching the region) and added. Truly
//    random; ragged; may enclose holes.
// 2  Concavity filling to a target convexity kappa. The cells whose centres lie in
//    the convex hull of the region's centres but are not in the region are its
//    concavities (inlets and holes). They are filled one at a time -- always the
//    one with the most region neighbours, ties drawn at random, so holes and narrow
//    inlets go first -- until convexity >= kappa. kappa = 1 fills them all and the
//    region becomes convex; kappa at or below the raw convexity changes nothing.
//
// Convexity = cells / (lattice cells whose centre lies in the convex hull of the
// cells' centres). Filling never moves the hull, so it rises linearly to 1.

#ifndef UAVCOOP_REGION_H
#define UAVCOOP_REGION_H

#include "coop-rng.h"
#include "hex-grid.h"

#include <cstdint>
#include <unordered_set>
#include <vector>

namespace ns3::uavcoop {

struct Region {
    std::vector<Hex> cells;        // the grown cells in growth order, then the filled ones
    std::vector<uint32_t> frontierSize;   // frontier size just before each growth step
    uint32_t nGrown = 0;           // cells[0 .. nGrown) grew; the rest were filled in
    double rawConvexity = 1.0, convexity = 1.0;
};

// Eden growth from `seed`.
Region GrowRegion(uint32_t nCells, const Hex& seed, CoopRng& rng);

// Grow nCells from the origin, then fill concavities up to convexity kappa in [0, 1].
Region MakeRegion(const HexGrid& g, uint32_t nCells, double kappa, CoopRng& rng);

// The lattice cells inside the convex hull of the cells' centres (the cells included).
std::vector<Hex> HullCells(const HexGrid& g, const std::vector<Hex>& cells);
double Convexity(const HexGrid& g, const std::vector<Hex>& cells);

// Unselected cells that cannot reach the outside without crossing the region.
std::vector<Hex> Holes(const Region& reg);

// True if every cell can reach every other through shared edges.
bool IsConnected(const std::vector<Hex>& cells);

// A side of the cluster's outer edge: shared by a cluster cell and a cell outside
// (hole sides excluded -- a hole is inside the cluster).
struct Edge {
    Point a, b;
    Point in;   // unit normal pointing into the cluster
};
std::vector<Edge> OuterEdges(const HexGrid& g, const Region& reg);

// Distance from p to the nearest of the edges.
double EdgeDistance(const Point& p, const std::vector<Edge>& edges);

}  // namespace ns3::uavcoop

#endif
