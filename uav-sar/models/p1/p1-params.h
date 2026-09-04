#ifndef UAV_SAR_P1_PARAMS_H
#define UAV_SAR_P1_PARAMS_H

// EVERY parameter of the Phase-1 system lives here and nowhere else.
//
// The system is being built before its parameters are known. That is workable
// only if the unknowns sit in ONE place and each says what it is waiting for.
// A plausible number written into a .cc file is indistinguishable from a
// measured one three weeks later, and that is how a placeholder becomes an
// unexamined assumption in a paper.
//
// Markers:
//   TODO(param)  MUST be replaced by a measurement or a decision before any
//                result resting on it is reported. The value here is chosen to
//                make the pipeline run. It is not a claim.
//   [derived]    computed from others; never set independently.
//   [design]     a decision, not a measurement. Changing it changes the system,
//                not the accuracy of the model.
//
// NOTE ON NAMES. The old system has its own kAlertThreshold on a different
// quantity and a different scale. Nothing here is shared with it -- see
// tools/check_p1_isolation.py, which fails the build path if this subtree ever
// reaches into the old one.

#include "p1-types.h"

#include <cstdint>

namespace ns3::uavsar::p1 {

// ===========================================================================
// PHASE 0 -- cells, leaders, classes
// ===========================================================================

// Cell circumradius. Not a free parameter: it is the variable the paper's design
// rule is about, so it is swept, not set.  [design]
inline constexpr double kCellRadiusM = 94.0;

// Ground link range between nodes, for the intra-cell tree.  TODO(param):
// should come from the measured G2G range, not assumed.
inline constexpr double kGroundRangeM = 40.0;

// The modality the reference dataset is recorded in.  [design]
inline constexpr Modality kReferenceModality = Modality::VISUAL;

// A node needs this much of the matcher to run it at all. Below it, the node can
// raise an anomaly but can never confirm or deny one -- so it cannot make its
// cell class A.  TODO(param): from the matcher's actual compute cost.
inline constexpr double kCpuMatchMin = 0.50;

// Weights of the capability-weighted leader election. Modality is NOT among
// them: it is a hard filter applied first, because a leader of the wrong
// modality cannot run the match and no amount of compute compensates.
// Residual energy -- PECEE's original criterion -- carries weight 0 because
// this simulator has no per-node energy model. Weighting a constant would look
// like a criterion without being one.
// TODO(param): give energy weight only once ground-node energy is modelled.
inline constexpr double kElectWCompute = 0.55;   // [design]
inline constexpr double kElectWRadio   = 0.45;   // [design]
inline constexpr double kElectWEnergy  = 0.00;

// ===========================================================================
// Node population
// ===========================================================================
// TODO(param): the whole block is a deployment description, not physics.
inline constexpr double kImagingFraction  = 0.65;   // nodes with any imager
inline constexpr double kVisualFraction   = 0.55;   // of imagers, share VISUAL
inline constexpr double kThermalFraction  = 0.30;   // ... THERMAL; rest ACOUSTIC
inline constexpr double kObsMin = 0.45,  kObsMax = 1.00;
inline constexpr double kCpuMin = 0.20,  kCpuMax = 1.00;
inline constexpr double kRxBpsMin = 20000.0, kRxBpsMax = 250000.0;

// ===========================================================================
// PHASE 1 TIER 1 -- detection, no reference needed
// ===========================================================================
//
// A PLACEHOLDER standing in for a real anomaly detector. Exactly two properties
// are load-bearing and must survive any replacement:
//   (a) it misses, and it false-alarms;
//   (b) it CANNOT tell a victim from a confuser.
// (b) is the whole content of the Fano ceiling and the reason Phase 1 exists.
// A "better" detector that separates the two stops modelling the problem.

inline constexpr double kDetectMeanSignal = 0.72;   // TODO(param): from a real ROC
inline constexpr double kDetectMeanNoise  = 0.18;   // TODO(param)
inline constexpr double kDetectSigma      = 0.12;   // TODO(param)
// Distance at which an obs = 1.0 node's response has halved.  TODO(param)
inline constexpr double kDetectHalfRangeM = 55.0;

// A cell enters the suspect set D above this. Deliberately low: Tier 1 is biased
// to sensitivity and Tier 2 pays for the false alarms. It must stay well below
// the bar used to CONFIRM -- sharing one threshold between alerting and
// confirming is a measured, expensive bug in the old system.  [design]
inline constexpr double kAlertScore = 0.45;

// Bytes one Tier-1 report costs on the narrowband uplink: cell id, score, class.
// The asymmetry against the reference payload going the other way is what makes
// the architecture close.  [design]
inline constexpr uint32_t kReportBytes = 6;

// ===========================================================================
// T0 -- information demand
// ===========================================================================

// Reference bytes a class-A cell needs to settle an identity it flagged.
// TODO(param): derive from the Chernoff exponent, theta ~ 1 / I_n(s).
inline constexpr double kThetaFullBytes = 120000.0;

// Demand for a class-A cell that did NOT flag: the hedge against a Tier-1 miss.
// A fraction, because the RATIO is what the planner is sensitive to.
// TODO(param): must follow from the measured Tier-1 miss rate. 0 disables it.
inline constexpr double kThetaHedgeFrac = 0.15;

// Reference broadcast rate from the aircraft.
// TODO(param): from the airborne link budget.
inline constexpr double kRefTxBytesPerS = 4000.0;   // ~32 kbps

// Reception probability p(d), used only through G(b): a logistic in distance,
// d50 being where a packet is caught half the time.
// TODO(param): MEASURABLE TODAY from the existing forest A2G channel model.
// This is the first placeholder that should be replaced by a measurement.
inline constexpr double kPrxD50M  = 190.0;
inline constexpr double kPrxWidth =  35.0;

inline constexpr double   kGmaxOffsetM = 400.0;   // [design] G table cutoff
inline constexpr uint32_t kGTableBins  = 81;

// ===========================================================================
// The Phase-1 aircraft (fixed wing)
// ===========================================================================
inline constexpr double kCruiseMps = 25.0;
inline constexpr double kMinMps    = 18.0;   // TODO(param): stall margin
inline constexpr double kMaxMps    = 30.0;   // TODO(param)
inline constexpr double kBankDeg   = 45.0;   // [design]
inline constexpr double kGravity   = 9.81;

double TurnRadiusM(double speedMps);          // [derived]

// The paper's design rule, as a SUFFICIENT condition:
//   h = 1.5 R_c >= 2 rho   =>   R_c >= 4 rho / 3   =>   adjacent-row scan optimal
//
// It is NOT necessary, and it must not be written as an iff. Verified
// numerically: with the cited turn family adjacent rows still win down to
// 1.218 rho, and with full Dubins turns (RLR admitted) down to 1.156 rho.
// The cited closed form also OVERSTATES the tight turn by up to 14 % because
// the true optimum there is a CCC path, not a fly-out-and-loop-back.
inline constexpr double kAdjacentSufficient = 4.0 / 3.0;
inline constexpr double kAdjacentTrueCited  = 1.2178;   // [derived]
inline constexpr double kAdjacentTrueDubins = 1.1559;   // [derived]

}  // namespace ns3::uavsar::p1

#endif  // UAV_SAR_P1_PARAMS_H
