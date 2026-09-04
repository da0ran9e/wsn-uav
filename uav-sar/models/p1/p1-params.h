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

// The detector reads a NOISY observation of the field, and the noise is drawn
// ONCE PER NODE PER RUN -- it is one observation of that node's own footage, not
// a per-packet event. Getting that wrong turns a fixed sensing limitation into
// something that averages away over time.
inline constexpr double kQualityMax = 0.95;   // TODO(param): peak match score
inline constexpr double kDecayM     = 60.0;   // TODO(param): falloff scale
inline constexpr double kSenseSigma = 0.10;   // TODO(param): per node, per run

// How much of a confuser's resemblance the COMPLETE reference removes.
//
// This is the physical heart of the two tiers, and it is why they are two TIERS
// and not two detectors. The SAME node, with the SAME noise draw, reads one
// value from cue-level information and another once it holds the reference: a
// jacket of the same colour matches at tier 1 and stops matching at tier 2.
// Ambiguity is therefore not a fixed property of the world but a function of how
// much reference has been delivered -- which is what makes DELIVERING an act of
// disambiguation rather than an act of transport.
// 1.0 = the full reference settles it outright; 0 = ambiguity survives delivery.
inline constexpr double kClutterResolve = 1.0;   // TODO(param)

// The two decision bars, and the ORDERING THEY MUST SATISFY.
//
//        noise floor  <  kAlertScore  <  kConfirmScore  <  R_victim
//
// where R_victim is what the node NEAREST a real victim reads once it holds the
// reference -- the best reading the deployment can ever produce for a true
// positive. Each inequality is load-bearing and each has been violated before:
//
//   noise < alert        a bar inside the noise makes every empty cell a
//                        suspect and the flight plan meaningless.
//   alert < confirm      sharing one bar between raising a candidate and
//                        settling one was measured on the old system: nodes
//                        with no signal confirmed on noise alone, and the fault
//                        stayed invisible while only one candidate existed.
//   confirm < R_victim   a bar above the best true positive confirms NOTHING.
//                        The first placeholders here had kConfirmScore = 0.70
//                        while the weakest sensor at the worst lattice distance
//                        reads 0.564 -- so every real victim was rejected. The
//                        harness now computes R_victim from the deployment and
//                        fails if the chain breaks.
//
// This is a CONSTRAINT, not a tuning knob. Changing kQualityMax, kDecayM,
// kObsMin or the node spacing moves R_victim and can break it silently.
inline constexpr double kAlertScore   = 0.35;   // [design] ~3.5 sigma over noise
inline constexpr double kConfirmScore = 0.50;   // [design]

// Bytes one Tier-1 report costs on the narrowband uplink: cell id, score, class.
// The asymmetry against the reference payload going the other way is what makes
// the architecture close.  [design]
inline constexpr uint32_t kReportBytes = 6;

// ===========================================================================
// T0 -- information demand
// ===========================================================================

// Reference bytes a class-A cell needs to settle an identity.
//
// EVERY class-A cell asks for this, scaled by its own sensor quality. There is
// no "flagged" and "unflagged" tier, because at planning time NOTHING HAS BEEN
// DETECTED YET: the aircraft has not flown, so no node has the reference, so no
// node can say anything about what is there. The suspect set is an OUTPUT of
// Phase 1, not an input to it.
//
// theta ~ 1 / I_n is therefore the ONLY source of heterogeneity in demand, and
// it is a real one: a better sensor settles the same question on less reference.
// That is still what separates this from a plain weighted min-max mTSP -- the
// weights are DERIVED from the deployment rather than given -- but the claim is
// narrower than a prior measured by the network, and must be written that way.
// TODO(param): derive from the Chernoff exponent, theta ~ 1 / I_n(s).
inline constexpr double kThetaFullBytes = 120000.0;

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
