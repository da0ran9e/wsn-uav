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
inline constexpr double kNlosExcessDb    = 10.0;   // [Assume] NLoS diffraction excess on
                                                   // top of foliage (LoS/NLoS both cross
                                                   // the canopy to reach a ground sensor)
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
// FAIRNESS (audit F1): every scheme flies ONE cruise speed by default. The
// former two-tier fleet (FAST 25 / DATA 15) gave the proposed scheme's
// critical path a 1.67x speed advantage over every baseline UAV with nothing in
// the model implementing it (EnergyPowerW has no mass term; "payload" is bytes
// in a vector). The identical 5-byte REPORT was flown home at 25 m/s by one
// scheme and 15 m/s by the other. Two-tier speeds remain reachable via
// --fastSpeed/--dataSpeed so they can be studied as a declared variable.
inline constexpr double kCruiseSpeedMps  = 20.0;    // [Design] all schemes
inline constexpr double kFastSpeedMps    = kCruiseSpeedMps;   // override: --fastSpeed
inline constexpr double kDataSpeedMps    = kCruiseSpeedMps;   // override: --dataSpeed
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
inline constexpr double kRptRepeatS      = 2.0;     // [Design] re-send my RPT while my
inline constexpr uint32_t kRptRepeatMax  = 30;      // evidence >= coop and no SUMMON
                                                    // heard — single-shot reports die on
                                                    // deep trees / large areas (measured:
                                                    // 40x40 intra-deliveries 4/1600 nodes).
inline constexpr uint32_t kShareTtl      = 4;       // [Design] SHARE flood radius (hops)
inline constexpr double kFwdStaggerMaxS  = 0.03;    // [Design] random per-hop forward
                                                    // jitter, desync the shared MAC
inline constexpr double kClaimBackoffS    = 0.15;   // [Design] UAV role claim: broadcast a
                                                    // CLAIM after U(0,this); first wins, the
                                                    // rest yield (replaces shared-mem token).
// audit W4: closed-loop non-cooperative baseline. A node that crosses the coop
// threshold answers the sky directly, repeating at a low rate while a UAV might
// still be in range. Bounded so the arm cannot win on sheer chatter.
inline constexpr double kEchoRepeatS     = 2.0;     // [Design]
inline constexpr uint32_t kEchoRepeatMax = 8;       // [Design]

// ---- when to stop observing and summon (audit A10) -------------------------
// A wall-clock observation window (--minObserve) is the WRONG parameterization
// and it fails hard: it must be long enough for the cue sweep to have sampled
// the evidence field, but shorter than the sweep itself, because once the FAST
// UAVs finish and fly home there is nobody airborne to relay the SUMMON. That
// upper bound scales with area, so one constant cannot serve two grid sizes --
// measured, 45 s is optimal at 16x16 and produces ZERO localizations at 8x8.
//
// The adaptive rule is local and needs no knowledge of the sweep: a leader
// fires once its own cell evidence has STOPPED GROWING, which is exactly the
// condition the wall-clock window was a proxy for. Every significant growth
// pushes the decision later; a quiet interval releases it. Cells whose evidence
// saturates at different times therefore also desynchronize naturally, which
// addresses the A11 race that a hard window edge created.
inline constexpr double kEvidenceStableS = 8.0;     // [Design] quiet interval that
                                                    // means "the field is sampled"
inline constexpr double kEvidenceGrowEps = 0.02;    // [Design] growth below this is
                                                    // not a reason to keep waiting
// audit A10: a FAST UAV that has finished sweeping is the only relay a SUMMON
// has. It holds station this long before flying home — bounded, so it cannot
// regress to the old hover-forever trap, but long enough that the region can
// still form after a short sweep finishes.
inline constexpr double kRelayGraceS     = 30.0;    // [Design] post-sweep relay hold

// Delivery fallback: the scheme's central weakness was that a wrong region was
// unrecoverable — blind coverage serves the victim ~99% of the time, directed
// delivery ~88%, and the gap did not close with scale. If no CONFIRM arrives
// within this long after the summon, the elected leader re-aims at the NEXT
// strongest candidate it has heard from and keeps beaconing. Bounded, because
// an unbounded retarget loop would just be a slow blind sweep.
// The trigger is set from the MEASURED summon->confirm distribution, not from
// the delivery dwell. Over 107 successful deliveries at 16x16 that interval is
// median 25.8 s, p90 53.8 s, p95 61.6 s, max 68.9 s -- so the first attempt at
// 26 s fired before 49% of SUCCESSFUL deliveries had finished, retargeted 41% of
// runs when only 11% ever fail, and degraded the fix from 14.6 m to 22.8 m by
// replacing a good first guess with a worse second one. A fallback must not be
// eager: it has to sit past the tail of normal completion.
inline constexpr double kRetargetAfterS  = 60.0;    // [Measured] ~p95 of summon->confirm
inline constexpr uint32_t kMaxRetargets  = 2;       // [Design]
inline constexpr double kElectDeadlineS  = 90.0;    // [Design] hard ceiling after
                                                    // ALERT, so a cell whose evidence
                                                    // never settles cannot starve
inline constexpr double kElectBackoffS   = 0.6;     // [Design] distributed region-leader
                                                    // election: a cell that crosses ALERT
                                                    // waits kElectBackoffS·(1−evidence)
                                                    // before summoning; stronger fires
                                                    // first, others suppress on its SUMMON.

// Reliability of the closing handshake (F2): the CONFIRM broadcast and the
// final REPORT are retransmitted a bounded number of times.
inline constexpr uint32_t kConfirmRetries = 5;      // [Design]
inline constexpr double  kConfirmRetryS   = 0.5;    // [Design]
inline constexpr uint32_t kReportRetries  = 10;     // [Design]
inline constexpr double  kReportRetryS    = 1.0;    // [Design]

// Baseline blind dwell: with no ground feedback a sweeping UAV cannot know when
// a dump landed, so it cycles chunks at each waypoint for a fixed time.
inline constexpr double kBaselineDwellS  = 25.0;    // [Design] see RESULTS.md
// tsp-mc (Zeng'18) redundancy: coded multicast sends MORE than the file so GTs
// recover despite erasures — the per-VBS connection time is sized to R x the
// dataset airtime (their recovery-probability margin, made explicit).
inline constexpr double kMcRedundancy    = 3.0;     // [Design<-Lit] overhead factor
// Proposed coverage dwell: after the first CONFIRM the DATA UAV keeps delivering
// for at least this long so the whole localized footprint — not just the node
// nearest the drop — reconstructs the data (raises victim-served rate).
// [Measured] 20 s was the reliability bottleneck, and the diagnosis matters:
// CONFIRM is broadcast by ANY node that reconstructs the dataset, so a bystander
// sitting under the drop point closes the loop while the actual victim -- 20-44 m
// out, where the per-packet success is lower -- never finishes. Of 12 failures at
// 16x16, nine were exactly this (delivery happened, closest drop 19.7-43.6 m from
// the victim); the other three never got a SUMMON to the DATA team at all.
// Re-aiming does NOT fix this (measured: no change), because the aim was not
// wrong -- the delivery was too short at range. 40 s takes victim-served from
// 90.0% to 96.7% at N=120, for +10% mission time, +8% energy, +30% packets.
inline constexpr double kMinDeliverDwellS = 20.0;    // [Measured] default; --deliverDwell

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
