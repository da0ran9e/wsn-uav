// A random contiguous set of cells.
//
// Eden growth from a seed cell: at every step one cell is drawn uniformly from the
// frontier (unselected cells touching the region) and added. The region is
// connected by construction, compact on average, ragged at the edge.

#ifndef UAVCOOP_REGION_H
#define UAVCOOP_REGION_H

#include "coop-rng.h"
#include "hex-grid.h"

#include <cstdint>
#include <unordered_set>
#include <vector>

namespace ns3::uavcoop {

struct Region {
    std::vector<Hex> cells;        // in the order they were added; cells[0] = seed
    std::vector<uint32_t> frontierSize;   // frontier size just before each addition
    // The convex envelope the region was grown inside; empty when growth was free.
    std::vector<Hex> envelope;
    double aspect = 0.0, thetaRad = 0.0;   // the envelope ellipse
};

// Free Eden growth; with `allowed`, only cells in it can join.
Region GrowRegion(uint32_t nCells, const Hex& seed, CoopRng& rng,
                  const std::unordered_set<Hex, HexHash>* allowed = nullptr);

// A region of nCells cells around the origin with the given convexity in [0, 1]:
//   convexity > 0   envelope = the round(nCells / convexity) cells whose centres are
//                   nearest the origin in a random ellipse metric (aspect U[1, maxAspect],
//                   orientation U[0, pi)) -- the lattice cut by a convex set, so convex.
//                   The region grows from the origin inside it; at 1 it fills it.
//   convexity = 0   free growth, no envelope.
Region MakeRegion(const HexGrid& g, uint32_t nCells, double convexity, double maxAspect,
                  CoopRng& rng);

// cells / (lattice cells whose centre lies in the convex hull of the cells' centres).
// 1 exactly for a convex region.
double Convexity(const HexGrid& g, const std::vector<Hex>& cells);

// Unselected cells that cannot reach the outside without crossing the region.
std::vector<Hex> Holes(const Region& reg);

// True if every cell can reach every other through shared edges.
bool IsConnected(const std::vector<Hex>& cells);

}  // namespace ns3::uavcoop

#endif
