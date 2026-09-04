#ifndef UAV_SAR_P1_ROUTE_H
#define UAV_SAR_P1_ROUTE_H

// T2: order one aircraft's cells, with the heading at each one as part of the
// decision.
//
// For a vehicle that cannot turn on the spot the distance between two places
// depends on the heading at BOTH ends, so this is not a metric TSP. The standard
// treatment samples the heading at each cell into h values, which turns each
// cell into a CLUSTER of h configurations and the problem into a generalised
// TSP: visit exactly one configuration per cluster.
//
// ---------------------------------------------------------------------------
// A MODELLING DECISION WORTH RECORDING, WITH A COUNTEREXAMPLE
// ---------------------------------------------------------------------------
// The alternative is to keep ONE node per cell and carry a sign variable for the
// direction of travel through it. Then "two consecutive passes must be in
// opposite directions" becomes a PRODUCT of two decision variables -- bilinear,
// non-convex -- and that is exactly why the work that took this route had to
// abandon exact solution and fall back on a heuristic. Duplicating nodes costs
// h times the variables and keeps the problem linear. That is the right trade.
//
// ---------------------------------------------------------------------------
// WHY NOT NOON-BEAN HERE
// ---------------------------------------------------------------------------
// The spec names the Noon-Bean transformation to an ordinary asymmetric TSP.
// Its value is that it lets a MATURE EXACT SOLVER be pointed at the result --
// and this environment has none (no OR-Tools, no LKH, no Concorde), so the ATSP
// would be attacked by a heuristic anyway. Noon-Bean would then buy nothing and
// still cost the n*h node blow-up plus a big-M constant that heuristics handle
// badly.
//
// What is done instead keeps the EXACT part exact: for a FIXED cell order the
// optimal headings are found by dynamic programming over h states, which is
// exact and costs O(n h^2). Only the cell ORDER is heuristic (nearest neighbour,
// then 2-opt and Or-opt, every candidate scored by that same DP). So the
// approximation is confined to one place and named, rather than spread across
// a transformation whose guarantee has already been lost.
//
// The relaxation guarantees quoted for rooted min-max cycle cover -- (6+1/3+eps)
// and (7+eps) -- assume a METRIC graph. Dubins costs are not metric. The
// algorithms are usable; the bounds are not, and must not be claimed.

#include "p1-demand.h"
#include "p1-dubins.h"
#include "p1-params.h"

#include <cstdint>
#include <map>
#include <vector>

namespace ns3::uavsar::p1 {

// Heading samples per cell. h = 8 is the working default; the harness sweeps it
// and shows where the curve flattens.
inline constexpr uint32_t kHeadingSamples = 8;

struct Leg {
    int32_t cellId = -1;
    Config  cfg;                    // where and on what heading
    double  fromPrevM = 0.0;        // Dubins metres from the previous config
};

struct Tour {
    std::vector<Leg> legs;          // depot is not a leg; it bounds the tour
    Config depot;
    double flightM = 0.0;
    double serviceS = 0.0;
    double TotalS() const { return flightM / kCruiseMps + serviceS; }
};

// Exact optimal headings for a FIXED cell order: DP over h states per cell.
Tour BestHeadings(const std::vector<int32_t>& order,
                  const std::map<int32_t, Demand>& demands,
                  const Config& depot, double turnRadiusM,
                  uint32_t headings = kHeadingSamples);

// The nearest-neighbour order alone, measured with the same exact heading DP.
// Exposed so the step-by-step visualiser can show what the local search started
// from -- and so that "38 % shorter" is a claim about two things this code
// actually produced, not about a remembered baseline.
Tour SeedTour(const std::vector<int32_t>& cells,
              const std::map<int32_t, Demand>& demands,
              const Config& depot, double turnRadiusM,
              uint32_t headings = kHeadingSamples);

// Cell order by nearest neighbour, improved by 2-opt and Or-opt, every candidate
// scored with BestHeadings so the order is never chosen on a yardstick the
// aircraft does not fly.
Tour SolveTour(const std::vector<int32_t>& cells,
               const std::map<int32_t, Demand>& demands,
               const Config& depot, double turnRadiusM,
               uint32_t headings = kHeadingSamples);

}  // namespace ns3::uavsar::p1

#endif  // UAV_SAR_P1_ROUTE_H
