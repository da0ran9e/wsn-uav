#ifndef UAV_SAR_PHASE1_PARAMS_H
#define UAV_SAR_PHASE1_PARAMS_H

// EVERY parameter of the two-tier sensing / Phase-1 planning system lives here,
// and nowhere else.
//
// The system is being built before its parameters are known. That is fine as
// long as the unknowns are IN ONE PLACE and each one says what it is waiting
// for -- otherwise a placeholder drawn out of the air in some .cc file becomes
// an unexamined assumption that survives into the paper.
//
// Read the markers:
//   TODO(param)   a number that MUST be replaced by a measurement or a decision
//                 before any result built on it may be reported. The value here
//                 is a placeholder chosen to be plausible and to make the
//                 pipeline run -- it is NOT a claim.
//   [derived]     computed from others; do not set independently.
//   [design]      a decision, not a measurement. Changing it changes the system,
//                 not the accuracy of the model.

#include "node-capability.h"

#include <cstdint>

namespace ns3::uavsar::p1 {

// ---------------------------------------------------------------------------
// PHASE 0 -- cells and classes
// ---------------------------------------------------------------------------

// The modality the reference dataset is recorded in. A cell can only ever
// DISCRIMINATE if it holds a node of this modality.  [design]
inline constexpr Modality kReferenceModality = Modality::VISUAL;

// Weights for the capability-weighted leader election (Phase 0.2). Modality is
// not in this list: it is a hard filter applied before the weights, because a
// leader of the wrong modality cannot run the match at all and no amount of
// compute compensates.  [design]
inline constexpr double kElectWCompute = 0.55;
inline constexpr double kElectWRadio   = 0.45;
// PECEE's original criterion, demoted to fourth. Weight is 0 because THERE IS NO
// per-node residual-energy model in this simulator -- ground nodes are not
// energy-limited, only aircraft are. Carrying a non-zero weight against a
// constant would be decoration that looks like a criterion.
// TODO(param): give it weight only if and when ground-node energy is modelled.
inline constexpr double kElectWEnergy  = 0.0;

// ---------------------------------------------------------------------------
// PHASE 1 TIER 1 -- detection (no reference needed)
// ---------------------------------------------------------------------------
//
// The detector model is a PLACEHOLDER standing in for a real anomaly detector.
// What it must reproduce to be useful for planning is exactly two things:
//   (a) it fires on something being there, with a miss rate,
//   (b) it CANNOT tell a victim from a confuser -- that is the whole content of
//       the 1/(M+1) ceiling, and it is what Phase 1 exists to break.
// Everything else about it is decoration and must not be leaned on.

// Mean detector score when the cell holds an object (victim OR confuser -- the
// same distribution, deliberately).            TODO(param): from a real detector ROC
inline constexpr double kDetectMeanSignal = 0.72;
// Mean score with nothing there.               TODO(param)
inline constexpr double kDetectMeanNoise  = 0.18;
// Score spread, both cases.                    TODO(param)
inline constexpr double kDetectSigma      = 0.12;
// Distance at which an obs = 1.0 node's response has fallen to half.  TODO(param)
inline constexpr double kDetectHalfRangeM = 55.0;

// A cell enters the suspect set D above this score. Deliberately LOW: Tier 1 is
// biased to sensitivity, and Tier 2 pays for the false alarms.
// NOTE this must stay well below the CONFIRM threshold -- sharing one threshold
// between alerting and confirming is a measured, expensive bug (STATUS.md 3.1b).
inline constexpr double kAlertThreshold = 0.45;   // [design]

// ---------------------------------------------------------------------------
// T0 -- information demand
// ---------------------------------------------------------------------------

// Reference bytes a class-A cell needs to settle an identity it has flagged.
// TODO(param): derive from the Chernoff exponent, theta ~ 1/I_n(s).
inline constexpr double kThetaFullBytes = 120000.0;

// Demand for a class-A cell that did NOT flag -- the hedge against a Tier-1
// miss. Expressed as a FRACTION of the full demand, because the ratio is what
// the planner is actually sensitive to.
// TODO(param): must follow from the Tier-1 miss rate. 0 disables hedging.
inline constexpr double kThetaHedgeFrac = 0.15;

// Broadcast rate of the reference stream from the aircraft (bytes/s).
// TODO(param): from the airborne link budget, not guessed.
inline constexpr double kRefTxBytesPerS = 4000.0;   // ~32 kbps

// Reception probability model p(d), used only through G(b). A logistic in
// distance; d50 is where a packet is caught half the time.
// TODO(param): MEASURABLE TODAY from the existing forest A2G channel model --
// this is the first thing that should replace a placeholder here.
inline constexpr double kPrxD50M  = 190.0;   // half-reception distance
inline constexpr double kPrxWidth =  35.0;   // logistic width; smaller = sharper

// Cutoff for the G(b) table: beyond this offset a pass delivers nothing worth
// counting.  [design]
inline constexpr double kGmaxOffsetM = 400.0;
inline constexpr uint32_t kGTableBins = 81;   // 0..kGmaxOffsetM inclusive

// ---------------------------------------------------------------------------
// Vehicle (fixed-wing) -- the Phase-1 aircraft
// ---------------------------------------------------------------------------
inline constexpr double kCruiseMps  = 25.0;
inline constexpr double kMinMps     = 18.0;   // stall margin  TODO(param)
inline constexpr double kMaxMps     = 30.0;   //               TODO(param)
inline constexpr double kBankDeg    = 45.0;
inline constexpr double kGravity    = 9.81;

// Turn radius at a given speed and the configured bank.  [derived]
double TurnRadiusM(double speedMps);

// The design rule of the paper, as a SUFFICIENT condition:
//   h = 1.5 R_c >= 2 rho   =>   R_c >= 4 rho / 3   =>  adjacent-row scan optimal.
// It is not necessary: with the cited turn family adjacent rows still win down
// to R_c = 1.218 rho, and with full Dubins turns (RLR admitted) down to
// R_c = 1.156 rho. Both verified numerically. Do not state it as iff.
inline constexpr double kAdjacentRowSufficient = 4.0 / 3.0;
inline constexpr double kAdjacentRowTrueCited  = 1.2178;   // [derived]
inline constexpr double kAdjacentRowTrueDubins = 1.1559;   // [derived]

}  // namespace ns3::uavsar::p1

#endif  // UAV_SAR_PHASE1_PARAMS_H
