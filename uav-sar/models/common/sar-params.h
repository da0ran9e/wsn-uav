#ifndef UAV_SAR_PARAMS_H
#define UAV_SAR_PARAMS_H

// SINGLE SOURCE OF TRUTH for tunable parameters. Values are the current best
// estimates (see docs/PARAMETERS.md for citations + confidence). Swapping a
// literature value later = edit here only; nothing else hard-codes numbers.
//
// Tags in comments: [Lit] literature, [Lit?] needs PDF confirm, [Design] our
// choice, [Assume] assumption to validate.

#include <cstdint>

namespace ns3::uavsar::params {

// ---- Radio (IEEE 802.15.4 @ 2.4 GHz) --------------------------------------
inline constexpr double kFreqHz          = 2.4e9;   // [Lit]
inline constexpr double kTxPowerDbm      = 0.0;     // [Lit] CC2420 typical
inline constexpr double kRxSensitivityDbm= -95.0;   // [Lit] CC2420
inline constexpr double kRefDistanceM    = 1.0;     // d0
inline constexpr double kRefLossDb       = 40.05;   // [Lit] FSPL(1m,2.4GHz)
inline constexpr uint32_t kLrwpanChannel = 11;      // [Design]

// ---- Channel (A2G / G2G + fading + shadowing) -----------------------------
inline constexpr double kA2GExponent     = 2.2;     // [Lit] 3GPP 36.777 LoS
inline constexpr double kG2GExponent     = 3.5;     // [Lit] ground NLoS
inline constexpr double kAltThresholdM   = 15.0;    // [Assume] canopy top: A2G above
inline constexpr double kShadowingSigmaDb= 8.7;     // [Lit/Assume] woodland
inline constexpr double kNakagamiM       = 1.5;     // [Assume] partial-LoS forest

// ---- Topology / PECEE substrate -------------------------------------------
inline constexpr double kGridSpacingM    = 20.0;    // [Design] sensor spacing
inline constexpr double kHexCellRadiusM  = 80.0;    // [Lit?/Design] PECEE cell
inline constexpr double kNeighborRangeM  = 80.0;    // [Design] ground link range
inline constexpr double kUavBroadcastRadiusM = 50.0;// [Lit dẫn xuất] link budget

// ---- UAV flight ------------------------------------------------------------
inline constexpr double kCruiseAltitudeM = 20.0;    // [Design] single mode
inline constexpr double kFastSpeedMps    = 25.0;    // [Design]
inline constexpr double kDataSpeedMps    = 15.0;    // [Design]
inline constexpr double kClimbRateMps    = 5.0;     // [Design]

// ---- UAV energy (Zeng-Zhang 2019 rotary-wing) -----------------------------
inline constexpr double kEnergyP0W       = 79.86;   // [Lit?] blade profile
inline constexpr double kEnergyPiW       = 88.63;   // [Lit?] induced
inline constexpr double kEnergyUtipMps   = 120.0;   // [Lit?]
inline constexpr double kEnergyV0Mps     = 4.03;    // [Lit?] rotor induced vel
inline constexpr double kEnergyD0        = 0.6;     // [Lit?] fuselage drag ratio
inline constexpr double kEnergyRho       = 1.225;   // [Lit] air density
inline constexpr double kEnergyS         = 0.05;    // [Lit?] rotor solidity
inline constexpr double kEnergyA         = 0.503;   // [Lit?] rotor disc area

// ---- SAR application (mostly design) --------------------------------------
inline constexpr double kBaseCueProb     = 0.90;    // [Design] p0 per baseline
inline constexpr double kAlertThreshold  = 0.75;    // [Design] detect
inline constexpr double kConfirmThreshold= 0.95;    // [Design] full confirm
inline constexpr double kCoopThreshold   = 0.30;    // [Design]
inline constexpr double kRegionWindowS   = 1.0;     // [Design] cross-cell merge wait
inline constexpr uint32_t kBeaconQuota   = 60;      // [Design] persistent low-rate
inline constexpr double kBeaconIntervalS = 1.0;     // [Design]
inline constexpr double kCoopSuccIntra   = 0.92;    // [Assume]->derive from PDR
inline constexpr double kCoopSuccInter   = 0.82;    // [Assume]

// ---- Timing (sim mechanics) ------------------------------------------------
inline constexpr double kControlTickS    = 0.1;     // flight state machine
inline constexpr double kDisseminateStaggerS = 0.2; // FAST cue broadcast
inline constexpr double kDeliverStaggerS = 0.02;    // point-blank bulk delivery
inline constexpr double kTrajLogS        = 1.0;

}  // namespace ns3::uavsar::params

#endif  // UAV_SAR_PARAMS_H
