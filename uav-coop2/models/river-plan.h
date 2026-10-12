// The River plan written by tools/river_export.py (L3-vi.md, Algorithms 1-4), read back
// for the ns-3 trial. Cells are uav-coop Hex (axial q, r).

#ifndef UAVCOOP2_RIVER_PLAN_H
#define UAVCOOP2_RIVER_PLAN_H

#include "ns3/hex-grid.h"

#include <cstdint>
#include <string>
#include <vector>

namespace ns3::uavcoop2 {

using uavcoop::Hex;

struct PlanAxe {
    Hex a;
    uint32_t first = 0, last = 0;       // Seg(a) = [first, last]
};
struct PlanBank {
    Hex a, b;
    int side = 0;
    std::vector<Hex> path;              // a -> b
};
struct PlanCirc {
    Hex k, m, a, b;                     // member m of k fetches Seg(a) from Bank b
    std::vector<Hex> path;              // b -> m
};
struct PlanDirect {
    Hex k, a;
    std::vector<Hex> path;              // k -> a
};
struct Plan {
    uint32_t packets = 0;
    std::vector<PlanAxe> axe;
    std::vector<PlanBank> banks;
    std::vector<Hex> crit;
    std::vector<PlanCirc> circ;
    std::vector<PlanDirect> direct;
};

// Reads the plan file; aborts with a message on a malformed line.
Plan ReadPlan(const std::string& file);

}  // namespace ns3::uavcoop2

#endif
