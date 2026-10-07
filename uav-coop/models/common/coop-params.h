// The parameter set this project starts from.
//
// Every value below was used -- and most were measured or checked -- in uav-sar's
// urban experiments (uav-sar/docs/A2G-RUN-vi.md, A2G-SWEEP-vi.md, G2G-CHAIN-vi.md).
// URBAN BRANCH: not the forest SAR model.
//
// Step 1 (deployment) uses only the geometry block. The radio blocks are carried
// over now so the later steps take them from one place.

#ifndef UAVCOOP_COOP_PARAMS_H
#define UAVCOOP_COOP_PARAMS_H

#include <cstdint>

namespace ns3::uavcoop::params {

// ---- deployment (step 1) ----------------------------------------------------
// Cells are sized by the corner radius R of a pointy-top hexagon: flat-to-flat width
// = R sqrt(3) = the distance between neighbouring centres, area = (3 sqrt(3) / 2) R^2.
inline constexpr double   kCellRadiusM  = 100.0;   // R = 100 m: width 173.2 m, 25 981 m^2
inline constexpr uint32_t kRegionCells  = 60;      // [design] cells grown at random
inline constexpr double   kSpacingM     = 30.0;    // [design] 20-50 m: one node per spacing^2
// Target convexity: grow at random, then fill the concavities (cells in the region's
// convex hull that are not in it) until convexity >= this. 1: convex. Values at or
// below the grown region's own convexity (~0.55-0.82) change nothing.
inline constexpr double   kConvexity    = 1.0;

// ---- flight path (step 2) ---------------------------------------------------
// Minimum turn radius v^2 / (g tan(bank)): 50 m/s, 45 deg -> 254.9 m (the same fixed-wing
// turn as uav-sar's lawnmower sweep).
inline constexpr double   kMinTurnRadiusM = 50.0 * 50.0 / 9.80665;

// ---- UAV --------------------------------------------------------------------
inline constexpr double kUavAltM    = 100.0;
inline constexpr double kUavSpeedMps = 50.0;

// ---- radio, both links (IEEE 802.15.4, 2.4 GHz, 250 kbps) ----------------------
inline constexpr double   kTxPowerDbm   = 10.0;    // UAV and nodes alike
inline constexpr double   kRxSensDbm    = -100.0;  // ns-3 semantics: PER 1 % @ 20 B PSDU;
                                                   // PER 50 % @ 127 B is -101.0 dBm (measured)
inline constexpr uint32_t kPsduBytes    = 127;     // airtime 4.256 ms incl. SHR+PHR
inline constexpr double   kSlotS        = 0.010;   // packet period / TDMA slot
inline constexpr double   kFspl1mDb     = 40.05;   // 20 log10(4 pi / lambda)

// ---- air-to-ground (A2G-RUN, A2G-SWEEP) ----------------------------------------
inline constexpr double kA2gAlpha    = 3.0;        // beyond the free-space segment
                                                   // (2.6 / 3.35 for sensitivity)
// free space up to d_ref = flight altitude (the spec's anchor)
inline constexpr double kA2gRicianK  = 2.0;        // redrawn every packet

// ---- ground-to-ground (G2G-CHAIN) ----------------------------------------------
inline constexpr double kG2gExponent  = 3.5;       // from 1 m
inline constexpr double kG2gShadowDb  = 7.8;       // static per node pair, reciprocal
inline constexpr double kG2gRicianK   = 0.0;       // Rayleigh
inline constexpr double kG2gCoherenceS = 0.1;      // fading block
inline constexpr uint32_t kTdmaReuse  = 3;         // node i sends in slots = i mod M

}  // namespace ns3::uavcoop::params

#endif
