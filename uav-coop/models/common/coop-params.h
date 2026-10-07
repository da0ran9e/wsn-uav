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
// "Cell width" = flat-to-flat width of a pointy-top hexagon = the distance between
// the centres of two neighbouring cells. Corner radius R = width / sqrt(3).
inline constexpr double   kCellWidthM   = 100.0;
inline constexpr uint32_t kRegionCells  = 60;      // [design] size of the random region
inline constexpr double   kSpacingM     = 30.0;    // [design] 20-50 m: one node per spacing^2
// Convexity = the share of a random convex envelope the region fills. 1: the region
// IS the envelope (convex). Lower: a random contiguous subset of it. 0: no envelope
// at all, free growth (step 1's original behaviour).
inline constexpr double   kConvexity    = 1.0;
inline constexpr double   kMaxAspect    = 2.0;     // [design] envelope: ellipse, aspect U[1, this]

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
