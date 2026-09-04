#ifndef UAV_SAR_P1_TIER1_H
#define UAV_SAR_P1_TIER1_H

// Phase 1, Tier 1: detection, before anything flies.
//
// Each cell asks "is something anomalous here?" using only its own footage. It
// needs no reference, so it costs no aircraft time. What it produces is the
// input the entire flight plan is built on: the suspect set D and a prior w_n
// over it.
//
// The prior is worth a sentence where the code is. Every method that allocates
// search effort has to assume a prior from somewhere. Here the network MEASURES
// it. That is a property of the architecture, not a modelling convenience.
//
// ---------------------------------------------------------------------------
// THE ONE THING THIS FILE MUST GET RIGHT
// ---------------------------------------------------------------------------
// A tier is not a detector. The SAME node, with the SAME noise draw, produces
// TWO readings:
//
//   scoreCue    what it reads from cue-level information alone -- no reference.
//               A confuser resembling the target is indistinguishable here.
//   scoreFull   what THAT SAME node, with THAT SAME noise, would read holding
//               the complete reference. The confuser stops matching; a real
//               victim does not.
//
// Both come out of one observation, because they are one observation. Drawing
// them separately would make tier 2 an unrelated second coin flip, and the
// claim the whole architecture rests on -- that DELIVERING IS AN ACT OF
// DISAMBIGUATION, not an act of transport -- would quietly stop being modelled.
//
// The gap between the two readings is exactly what the aircraft flies out to
// buy. With no reference a node is bounded by Fano at P(correct) <= 1/(M+1)
// over M confusers plus the target: 50 % at M=1, 33 % at M=2, 20 % at M=4. That
// ceiling is informational, not a sensor limit -- observing longer or harder
// does not move it, and only information from outside does. It binds the FIRST
// AIM, not the mission: once the reference has been delivered the ceiling no
// longer applies, which is why the mission can succeed where a single look
// cannot.
//
// Noise is drawn ONCE PER NODE PER RUN. It is one observation of that node's own
// footage, not a per-packet event. Drawing it per read would let a node average
// its own limitation away, turning a fixed constraint into a soft one.

#include "p1-cells.h"
#include "p1-params.h"
#include "p1-sensing.h"
#include "p1-types.h"

#include <cstdint>
#include <map>
#include <vector>

namespace ns3::uavsar::p1 {

// Something on the ground a detector responds to. Tier 1 sees no difference
// between the two kinds; only the scoring of a run does.
struct Object {
    double x = 0, y = 0;
    bool   real = false;        // ground truth -- NEVER read by the detector
    // How much this object resembles the target to a cue-level detector.
    // 1.0 = indistinguishable without the reference. Ignored when real.
    double similarity = 1.0;
};

struct NodeReading {
    uint32_t id = 0;
    double scoreCue = 0.0;      // tier 1: no reference
    double scoreFull = 0.0;     // tier 2: same node, same noise, full reference
    double noise = 0.0;         // the one draw, kept so both tiers share it
};

struct CellReading {
    int32_t  cellId = -1;
    double   score = 0.0;       // a_n: best cue-level reading in the cell
    double   weight = 0.0;      // w_n, normalised over D
    bool     suspect = false;
    uint32_t responder = 0;     // the node whose reading set the score
    // Ground truth, for scoring a run only. An object is IN a cell or it is not;
    // labelling by whether some member responded makes nearly every cell "hold"
    // one as soon as sensing range approaches the cell pitch, and then recall
    // and false-alarm rate both stop meaning anything.
    bool holdsObject = false;
    bool holdsReal = false;
};

struct Tier1Result {
    std::map<uint32_t, NodeReading> nodes;
    std::map<int32_t, CellReading> cells;
    std::vector<int32_t> suspects;          // D, best score first
    uint32_t objectCells = 0, detected = 0;
    uint32_t emptyCells = 0, falseAlarms = 0;
    double UplinkBytes() const { return cells.size() * (double)kReportBytes; }
};

Tier1Result RunTier1(const std::vector<Node>& nodes, const CellPlan& plan,
                     const std::vector<Object>& objects, uint32_t seed);

// Tier 2, step E.3: what a cell concludes once it holds the reference. Uses the
// SAME reading realisation, which is the point.
enum class Verdict : uint8_t { NONE = 0, CONFIRM = 1, REJECT = 2 };

// `held` is the fraction of theta the cell actually received, in [0,1]. The
// reading moves from the cue value to the full value as the reference arrives:
// a partial delivery buys partial disambiguation, which is what makes the dose
// model in T0 mean anything.
Verdict CellVerdict(const Tier1Result& t1, const CellPlan& plan,
                    const std::vector<Node>& nodes, int32_t cellId, double held);

}  // namespace ns3::uavsar::p1

#endif  // UAV_SAR_P1_TIER1_H
