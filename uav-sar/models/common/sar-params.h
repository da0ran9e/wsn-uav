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
inline constexpr double kShadowingSigmaDb= 8.7;     // [Lit/Assume] woodland (G2G)
inline constexpr double kNakagamiM       = 1.5;     // [Assume] partial-LoS forest

// ---- Elevation-angle LoS + foliage model (A2G realism v3) ------------------
// P_LoS(theta) = 1 / (1 + a*exp(-b*(theta - a)))   [Al-Hourani 2014]
// Suburban class as the nearest published proxy for sparse forest; the pair's
// LoS state uses a frozen per-pair quantile so it flips exactly once as the
// UAV's elevation angle rises (spatially consistent, no per-packet lottery).
inline constexpr double kLosA            = 4.88;    // [Lit?] Al-Hourani suburban
inline constexpr double kLosB            = 0.43;    // [Lit?]
inline constexpr double kEtaLosDb        = 0.1;     // [Lit?] LoS excess loss
// NLoS excess = foliage crossing per ITU-R P.833 capped exponential:
//   A = Amax * (1 - exp(-d_veg * gamma / Amax)),  d_veg = canopy/sin(theta)
inline constexpr double kVegGammaDbPerM  = 0.5;     // [Lit] ITU-R P.833 0.3-0.8 @2GHz
inline constexpr double kVegAmaxDb       = 35.0;    // [Lit] ITU-R P.833 10-40
// Residual A2G shadowing once LoS/foliage is explicit (avoid double counting
// the 8.7 dB woodland sigma, which folds vegetation variability in).
inline constexpr double kShadowSigmaA2gDb = 4.0;    // [Assume] residual

// ---- Topology / PECEE substrate -------------------------------------------
inline constexpr double kGridSpacingM    = 20.0;    // [Design] sensor spacing
inline constexpr double kHexCellRadiusM  = 80.0;    // [Lit?/Design] PECEE cell
// Ground neighbor range is DERIVED from the G2G link budget (see
// DeriveG2gRangeM below) so the substrate never assumes links the PHY cannot
// sustain. (Was a fixed 80 m — inconsistent with the ~37 m real G2G range.)
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
inline constexpr double kAlertThreshold  = 0.75;    // [Design] detect (region seed)
inline constexpr double kCoopThreshold   = 0.30;    // [Design] report / region join
inline constexpr double kRegionWindowS   = 1.0;     // [Design] cross-cell merge wait
inline constexpr uint32_t kBeaconQuota   = 60;      // [Design] persistent low-rate
inline constexpr double kBeaconIntervalS = 1.0;     // [Design]
inline constexpr double kCoopSuccIntra   = 0.92;    // [Assume] node->CL report success
inline constexpr double kCoopSuccInter   = 0.82;    // [Assume] CL<->CL share success
inline constexpr double kHopDelayS       = 0.02;    // [Assume] per ground hop latency

// Packet-level control plane: the clue report (RPT, up the cell tree) and the
// cross-cell share (SHARE, flooded) now cross the REAL radio, so their loss and
// latency come from the channel, not from kCoopSucc*/kHopDelayS above (which now
// serve only as a fallback for the legacy event-level path).
inline constexpr uint32_t kRptTtl        = 12;      // [Design] max up-tree hops
inline constexpr uint32_t kShareTtl      = 4;       // [Design] SHARE flood radius (hops)
inline constexpr double kFwdStaggerMaxS  = 0.03;    // [Design] random per-hop forward
                                                    // jitter, desync the shared MAC

// Reliability of the closing handshake (F2): the CONFIRM broadcast and the
// final REPORT are retransmitted a bounded number of times.
inline constexpr uint32_t kConfirmRetries = 5;      // [Design]
inline constexpr double  kConfirmRetryS   = 0.5;    // [Design]
inline constexpr uint32_t kReportRetries  = 10;     // [Design]
inline constexpr double  kReportRetryS    = 1.0;    // [Design]

// Baseline blind dwell: with no ground feedback a sweeping UAV cannot know when
// a dump landed, so it cycles chunks at each waypoint for a fixed time.
inline constexpr double kBaselineDwellS  = 25.0;    // [Design] see RESULTS.md

// ---- Timing (sim mechanics) ------------------------------------------------
inline constexpr double kControlTickS    = 0.1;     // flight state machine
inline constexpr double kDisseminateStaggerS = 0.2; // FAST cue broadcast
inline constexpr double kDeliverStaggerS = 0.02;    // point-blank bulk delivery
inline constexpr double kTrajLogS        = 1.0;

// ---- Derived helpers --------------------------------------------------------
// Max ground-to-ground link range from the log-distance budget.
inline double DeriveG2gRangeM() {
    // d = d0 * 10^((Tx - Sens - refLoss) / (10 n))
    double e = (kTxPowerDbm - kRxSensitivityDbm - kRefLossDb) / (10.0 * kG2GExponent);
    return kRefDistanceM * __builtin_pow(10.0, e);
}

// Rotary-wing propulsion power P(V) [W] (Zeng-Xu-Zhang 2019):
//   P0 (1 + 3V^2/Utip^2) + Pi (sqrt(1 + V^4/(4 v0^4)) - V^2/(2 v0^2))^{1/2}
//   + 1/2 d0 rho s A V^3
inline double EnergyPowerW(double v) {
    double blade = kEnergyP0W * (1.0 + 3.0 * v * v / (kEnergyUtipMps * kEnergyUtipMps));
    double t = __builtin_sqrt(1.0 + v * v * v * v / (4.0 * kEnergyV0Mps * kEnergyV0Mps *
                                                     kEnergyV0Mps * kEnergyV0Mps)) -
               v * v / (2.0 * kEnergyV0Mps * kEnergyV0Mps);
    double induced = kEnergyPiW * __builtin_sqrt(t > 0 ? t : 0);
    double parasite = 0.5 * kEnergyD0 * kEnergyRho * kEnergyS * kEnergyA * v * v * v;
    return blade + induced + parasite;
}

}  // namespace ns3::uavsar::params

#endif  // UAV_SAR_PARAMS_H
