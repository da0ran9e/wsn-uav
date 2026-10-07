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
#include <vector>

namespace ns3::uavcoop {

struct Region {
    std::vector<Hex> cells;        // in the order they were added; cells[0] = seed
    std::vector<uint32_t> frontierSize;   // frontier size just before each addition
};

Region GrowRegion(uint32_t nCells, const Hex& seed, CoopRng& rng);

// Unselected cells that cannot reach the outside without crossing the region.
std::vector<Hex> Holes(const Region& reg);

// True if every cell can reach every other through shared edges.
bool IsConnected(const std::vector<Hex>& cells);

}  // namespace ns3::uavcoop

#endif
