#ifndef UAV_SAR_P1_PARAMS_H
#define UAV_SAR_P1_PARAMS_H

// EVERY parameter of the Phase-1 system lives here and nowhere else.
//
// Markers:
//   TODO(param)  MUST be replaced by a measurement or a decision before any
//                result resting on it is reported. The value here is chosen to
//                make the pipeline run. It is not a claim.
//   [derived]    computed from others; never set independently.
//   [design]     a decision, not a measurement.

#include "p1-types.h"

#include <cstdint>

namespace ns3::uavsar::p1 {

// ===========================================================================
// PHASE 0 -- grid
// ===========================================================================

// Cell circumradius. Not a free parameter: it is what the design rule is about,
// so it is swept, not set.  [design]
inline constexpr double kCellRadiusM = 94.0;

// Douglas-Peucker tolerance for P0.0.  [design]
inline constexpr double kBoundaryTolM = 5.0;

// Ground link range, for the intra-cell tree.  TODO(param): from measured G2G.
inline constexpr double kGroundRangeM = 40.0;

// ===========================================================================
// Node population
// ===========================================================================
// TODO(param): a deployment description, not physics.
inline constexpr double kCameraFraction = 0.85;
inline constexpr double kObsMin = 0.45,  kObsMax = 1.00;
inline constexpr double kCpuMin = 0.20,  kCpuMax = 1.00;
inline constexpr double kRxBpsMin = 20000.0, kRxBpsMax = 250000.0;

// ===========================================================================
// P0.6 -- how many FILES, then how much DOSE
// ===========================================================================
//
//   k_n = ceil( ln(1/Pe*) / (I_n * S_eff) )     Chernoff: files to discriminate
//   theta_n = theta(k_n, K, C)                  coupon collector: dose to get them
//
// The two-stage shape is the point. Discrimination is a question about FILES --
// how many distinct pieces of reference the head needs to separate the target
// from J confusers. Delivery is a question about DOSE -- how much air time it
// takes to collect k distinct files out of K when they are broadcast blind, in
// round-robin, with no acknowledgement. Collapsing them into one number loses
// the coupon-collector term, which is where the broadcast schedule enters.

// Target probability of a wrong identification.  [design]
inline constexpr double kTargetPe = 0.05;

// Number of confusing objects the scene may hold. Enters through Fano: no
// target error below J/(J+1) is meaningful without reference (F2).
// TODO(param): a property of the scene.
inline constexpr uint32_t kConfusers = 3;

// Chernoff information a unit-capability head extracts per reference file.
// TODO(param): from the feature extractor and the matcher, not guessed.
inline constexpr double kInfoPerFile = 0.35;

// The broadcast file set.  [design]
inline constexpr uint32_t kFileCount = 24;      // K
inline constexpr uint32_t kFileBytes = 4096;    // TODO(param): feature vector size

// Confidence that a head has collected its k files by the time the dose is
// spent. Higher C costs more air time through the coupon-collector tail.
inline constexpr double kDeliveryConfidence = 0.95;   // [design]

// theta_n in bytes, for a head needing k of K files at confidence C.  [derived]
double DoseBytes(uint32_t filesNeeded);

// Files a head of information rate I needs.  [derived]
uint32_t FilesNeeded(double information);

// F2: below this target error the flight cannot help, because Fano already
// bounds a reference-free node at 1/(J+1).  [derived]
double FanoFloor();

// ===========================================================================
// The Phase-1 aircraft (fixed wing)
// ===========================================================================
inline constexpr double kCruiseMps = 25.0;
inline constexpr double kMinMps    = 18.0;   // TODO(param): stall margin
inline constexpr double kMaxMps    = 30.0;   // TODO(param)
inline constexpr double kBankDeg   = 45.0;   // [design]  phi_b
inline constexpr double kGravity   = 9.81;

double TurnRadiusM(double speedMps);          // [derived] rho = v^2/(g tan phi)

// Cost of moving between two row lines a distance d apart, three regimes.
// [derived]  L(d, rho)
double RowChangeM(double gapM, double turnRadiusM);

// P0.5 / T0.4 -- both come from ONE model: the aircraft weaves along the row on
// a sinusoid of amplitude delta and wavelength 2a, so that it passes over each
// head instead of standing off from it.
//
//   extra length over one cell pitch :  pi^2 delta^2 / (4a)
//   minimum radius of curvature      :  a^2 / (pi^2 delta)
//
// The second gives the HARD feasibility bound: a head further than delta_max
// from its row line cannot be followed, and reaching it would need a real Dubins
// detour instead of a weave.
//
//     delta_max = a^2 / (pi^2 rho) = 3 R_c^2 / (pi^2 rho)
//
// Note this is NOT a fixed fraction of R_c: delta_max / R_c = 3 R_c / (pi^2 rho)
// grows linearly with cell size. It equals 4/pi^2 = 0.405 exactly at the design
// point R_c = 4 rho / 3, which is where the "about 0.4 R_c" figure comes from --
// and it stops binding at all once R_c is past about 3.3 rho.  [derived]
double MaxOffsetM(double cellRadiusM, double turnRadiusM);
double WeaveExtraM(double offsetM, double cellPitchM);

// ===========================================================================
// T0 -- dose delivery
// ===========================================================================
inline constexpr double kRefTxBytesPerS = 4000.0;   // TODO(param): link budget

// Reception probability p(d): a logistic in distance.
// TODO(param): MEASURABLE from the existing forest A2G channel model.
inline constexpr double kPrxD50M  = 190.0;
inline constexpr double kPrxWidth =  35.0;

inline constexpr double   kGmaxOffsetM = 400.0;   // [design] G table cutoff
inline constexpr uint32_t kGTableBins  = 81;

// ===========================================================================
// Intra-cell flooding -- for the R_c scaling study, not for the planner
// ===========================================================================
//
// A packet leaving the head has to reach every member of its cell. How long
// that takes is the other half of the R_c trade-off: bigger cells mean fewer
// cells and a shorter flight, but a deeper tree and a longer flood.
//
// The numbers here are MEASURED on this project's own radio, not assumed:
//   * app payload ceiling is 100 B, not the 127 B PSDU -- 125 B made Send()
//     fail, 100 B did not.
//   * back-to-back Send() calls need >= 200 ms of stagger or the MAC queue
//     overflows and most packets are lost. 50 ms was verified insufficient.
//
// Note what that implies before reading any result: 100 B at 250 kbps is 3.2 ms
// of airtime against a 200 ms slot, so AIRTIME IS IRRELEVANT HERE. The flood is
// paced entirely by the MAC, and any conclusion about cell size that depends on
// packet length is a conclusion about the wrong variable.
inline constexpr uint32_t kFloodPacketBytes = 100;      // [measured ceiling]
inline constexpr double   kPhyBps           = 250000.0; // 802.15.4 O-QPSK
inline constexpr double   kMacSlotS         = 0.200;    // [measured]
// Two nodes closer than this cannot transmit in the same slot. A node's own
// range is kGroundRangeM; interference reaches further than reception does.
// TODO(param): measured capture ratio would pin this down.
inline constexpr double   kReuseRangeM      = 2.0 * kGroundRangeM;

// ===========================================================================
// The design rule
// ===========================================================================
// h = 1.5 R_c >= 2 rho  =>  R_c >= 4 rho / 3  =>  adjacent-row scan optimal.
//
// SUFFICIENT, not necessary, and it must not be written as an iff. Verified
// numerically: with the cited turn family adjacent rows still win down to
// 1.218 rho, and with full Dubins turns (RLR admitted) down to 1.156 rho. The
// cited closed form also OVERSTATES the tight turn by up to 14 %, because the
// true optimum there is a CCC path rather than a fly-out-and-loop-back.
inline constexpr double kAdjacentSufficient = 4.0 / 3.0;
inline constexpr double kAdjacentTrueCited  = 1.2178;   // [derived]
inline constexpr double kAdjacentTrueDubins = 1.1559;   // [derived]

}  // namespace ns3::uavsar::p1

#endif  // UAV_SAR_P1_PARAMS_H
