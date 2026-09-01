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

// ---------------------------------------------------------------------------
// Cell-based coverage, and a split that balances CAPABILITY as well as EFFORT.
// ---------------------------------------------------------------------------
//
// Covering every NODE is the wrong target once the ground can relay and once
// nodes differ. What the screening layer actually needs is that every CELL ends
// up with a seed set that is (a) big enough to spread from and (b) capable
// enough to produce evidence. A node with no camera is not worth flying over.
//
// So a lane is scored by the SCREENING CAPABILITY it seeds, not by the node
// count it passes, and lanes are selected until every cell's capability target
// is met rather than until every node is within range.

struct LaneScore {
    double effort = 0;      // metres of flight this lane costs
    double capability = 0;  // sum of Screening() over nodes it would seed
};

struct CapNode {
    double x = 0, y = 0;
    double screening = 1.0;   // obs * cpu
    int32_t cellId = -1;
};

// Score every candidate lane by the capability within `radius` of it.
std::vector<LaneScore> ScoreLanes(const std::vector<Lane>& lanes,
                                  const std::vector<CapNode>& nodes, double radius);

// Choose the smallest set of lanes such that every cell reaches `cellTarget` of
// its own total screening capability. Greedy on marginal capability per metre --
// the natural heuristic for a coverage problem that is a weighted set cover, and
// the one whose guarantee is understood.
std::vector<Lane> SelectLanesForCells(const std::vector<Lane>& candidates,
                                      const std::vector<CapNode>& nodes,
                                      double radius, double cellTarget);

// A circular no-fly zone: the aircraft may not enter, and nodes inside it can
// never be seeded directly by an overflight. Circles rather than polygons on
// purpose -- the clip below is then exact and closed-form, and a polygon buys
// nothing the argument needs.
struct NoFlyZone { double x = 0, y = 0, r = 0; };

// Cut every lane at the zones it crosses, keeping only the pieces OUTSIDE them.
// A lane that runs straight through a zone becomes two lanes; one buried
// entirely inside disappears. This is what stops the plan from AIMING into a
// zone -- it does not by itself stop the aircraft from cutting a corner while
// turning between two pieces, which is measured separately.
std::vector<Lane> ClipLanes(const std::vector<Lane>& lanes,
                            const std::vector<NoFlyZone>& zones);

// Insert bypass waypoints so no straight leg between consecutive waypoints
// passes through a zone.
//
// Clipping the lanes is only half the job and the measurement says so: with
// clipped lanes alone the aircraft still spent 4.6-7.1 % of its track inside a
// zone, up to 94 m deep, because the leg BETWEEN two clipped pieces runs
// straight across the hole between them. Worse, that violation quietly repaired
// the coverage numbers -- node-based coverage scored 100 % on shadowed nodes it
// was only reaching by flying somewhere it was not allowed to be.
//
// Each offending leg gets a waypoint pushed radially out past the zone edge, so
// the guidance is steered around instead of through. Applied repeatedly up to a
// bound, because pushing clear of one zone can push into another.
std::vector<ns3::Vector> RouteAroundZones(const std::vector<ns3::Vector>& wps,
                                          const std::vector<NoFlyZone>& zones,
                                          double marginM);

// Cut lanes lengthwise until there are at least `minPieces` of them.
//
// Cell-based selection leaves very few lanes -- five cover the whole field at
// the nominal cue radius -- and a balanced split cannot be finer than the pieces
// it is given. With five lanes and four UAVs the best possible split is 2/1/1/1,
// which is a 100 % effort imbalance no objective function can talk its way out
// of. Cutting a lane in half costs one extra turn and buys the granularity.
std::vector<Lane> SubdivideLanes(const std::vector<Lane>& lanes, uint32_t minPieces);

// Split `lanes` (in across-field order) into `count` CONTIGUOUS blocks that
// balance effort and capability at once, exactly, by dynamic programming over
// the split points. alpha weights effort against capability; 0.5 treats a point
// of effort imbalance as costing the same as a point of capability imbalance.
std::vector<std::vector<Lane>> BalancedSplit(const std::vector<Lane>& lanes,
                                             const std::vector<CapNode>& nodes,
                                             double radius, uint32_t count,
                                             double alpha, ns3::Vector start,
                                             double turnRadiusM);

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
// A clipped sliver shorter than this is not worth a turn to reach.
inline constexpr double kMinLanePieceM = 40.0;

}  // namespace ns3::uavsar

#endif  // UAV_SAR_LANE_PLAN_H
