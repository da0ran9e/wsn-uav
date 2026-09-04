#ifndef UAV_SAR_TIER1_DETECT_H
#define UAV_SAR_TIER1_DETECT_H

// Phase 1, Tier 1: local detection, before anything flies.
//
// Each cell asks "is something anomalous here?" using only its own data. It
// needs no reference and so it costs no aircraft time. What it produces is the
// input the whole flight plan is built on: the suspect set D and a prior w_n
// over it.
//
// The point about the prior is worth stating where the code is: every paper
// that allocates search effort has to assume a prior from somewhere. Here the
// network MEASURES it. That is a property of the architecture, not a modelling
// convenience.
//
// WHAT THIS TIER CANNOT DO, deliberately:
// A victim and a confuser produce the SAME score distribution. A node with no
// discriminating information is bounded by Fano at P(correct) <= 1/(M+1) over
// M confusers plus the target -- 50 % at M=1, 33 % at M=2, 20 % at M=4. That
// ceiling is informational, not a sensor limit: observing longer or harder does
// not move it. Breaking it requires information from outside, which is what
// Phase 1 flies out to deliver. If this model is ever "improved" so that the
// two distributions differ, it stops modelling the problem the system solves.
//
// The ceiling binds the FIRST AIM only, not the mission -- see STATUS.md 4.6,
// where a stronger reading of it was measured, found wrong, and retracted.
//
// The detector itself is a PLACEHOLDER (see phase1-params.h). Its ROC is not
// claimed. What is load-bearing is (a) it misses sometimes, (b) it false-alarms
// sometimes, (c) it cannot tell victim from confuser.

#include "cell-class.h"
#include "cell-grid.h"
#include "node-capability.h"

#include <cstdint>
#include <map>
#include <vector>

namespace ns3::uavsar {

// A thing on the ground that a detector can respond to. Tier 1 sees no
// difference between the two kinds; only the scoring of a run does.
struct Tier1Object {
    double x = 0, y = 0;
    bool   real = false;   // ground truth, for scoring ONLY -- never read by the detector
};

struct Tier1Cell {
    int32_t  cellId = -1;
    double   score = 0.0;      // a_n in [0,1]
    double   weight = 0.0;     // w_n, normalised over the suspect set
    bool     suspect = false;  // a_n > alert threshold
    bool     holdsObject = false;   // ground truth, for scoring only
    bool     holdsReal = false;     // ground truth, for scoring only
    uint32_t responder = 0;    // node whose response set the score
};

struct Tier1Result {
    std::map<int32_t, Tier1Cell> cells;
    std::vector<int32_t> suspects;      // D, ordered by descending score
    // Scoring of this realisation, against ground truth. Reported, never used.
    uint32_t objectCells = 0, detected = 0;   // recall over cells that hold one
    uint32_t emptyCells = 0, falseAlarms = 0; // false alarm rate over empty cells
};

// Run the tier over every class-A and class-B cell. Class C never reports.
// `seed` selects the detector's own noise stream.
Tier1Result RunTier1(const CellGridPlan& grid,
                     const CellRolePlan& roles,
                     const std::map<uint32_t, NodeCapability>& caps,
                     const std::vector<Tier1Object>& objects,
                     uint32_t seed);

// Bytes a Tier-1 report costs on the narrowband uplink: cell id, score, class.
// The asymmetry against the reference payload is the reason the architecture
// closes -- a few KB up against hundreds of KB down.
inline constexpr uint32_t kTier1ReportBytes = 6;

}  // namespace ns3::uavsar

#endif  // UAV_SAR_TIER1_DETECT_H
