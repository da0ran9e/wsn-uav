#ifndef UAV_SAR_LANE_PLAN_H
#define UAV_SAR_LANE_PLAN_H

// Phase 1 sweep planning for the fixed-wing (FAST) team.
//
// Two things this fixes about the previous arrangement, in which each FAST UAV
// was handed a slice of the SENSOR LIST and independently built a boustrophedon
// over the bounding box of that slice:
//
//  1. NOBODY OWNED A LANE. Two UAVs sizing their own lane grids from their own
//     bounding boxes put lanes within a broadcast radius of each other on both
//     sides of the seam, so the strip between them was swept twice. Measured at
//     24x24 with two FAST UAVs: 143 of 576 nodes (24.8 %) were covered by BOTH,
//     and the split was lopsided (69.4 % / 55.2 % of the field). Cueing a node
//     that already holds those chunks buys nothing -- it is airtime and flight
//     time spent on work already done.
//
//     Now there is ONE lane set over the whole field, and each lane belongs to
//     exactly one UAV. Overlap is reduced to what the swaths physically force
//     at the single seam, and the work splits evenly by construction.
//
//  2. LANES WERE FLOWN IN INDEX ORDER. With R(25 m/s) = 64 m against a 50 m lane
//     spacing, consecutive lanes are closer than the aircraft can turn in, so
//     every reversal had to be flown outside the search area. Ordering the lanes
//     is an asymmetric TSP over (lane, direction) under the Dubins metric; at
//     five or six lanes per UAV it is solved EXACTLY here by Held-Karp, so the
//     result is the true optimum rather than a heuristic's.

#include "ns3/vector.h"

#include <cstdint>
#include <vector>

namespace ns3::uavsar {

struct Lane {
    ns3::Vector a, b;      // the two ends; either may be the entry
};

// One lane set covering every sensor, lanes along the longer axis of the field,
// stacked `spacing` apart across it. Identical to what BuildMission() produced
// for the whole field, so coverage behaviour per lane is unchanged.
std::vector<Lane> BuildFieldLanes(const std::vector<ns3::Vector>& sensors,
                                  double spacing, double alt);

// Contiguous block of lanes owned by UAV `idx` of `count`. Contiguous rather
// than interleaved on purpose: interleaving would give each UAV wider gaps
// between its own lanes (cheaper turns) but would put every one of its lanes
// next to a peer's, which is the double-coverage this is meant to remove.
std::vector<Lane> LanesFor(const std::vector<Lane>& all, uint32_t idx, uint32_t count);

// Exact Dubins ordering of `lanes` from `start`, returned as a waypoint list
// (entry, exit, entry, exit, ...). Falls back to index order above
// kExactLaneLimit lanes, where Held-Karp stops being cheap.
std::vector<ns3::Vector> OrderLanes(const std::vector<Lane>& lanes,
                                    double turnRadiusM, ns3::Vector start);

// Shortest Dubins path length between two configurations (x, y, heading rad).
// Exposed for the unit check in tools/, which compares it against the
// independently written Python implementation.
double DubinsLength(double x0, double y0, double h0,
                    double x1, double y1, double h1, double R);

inline constexpr uint32_t kExactLaneLimit = 14;

}  // namespace ns3::uavsar

#endif  // UAV_SAR_LANE_PLAN_H
