#ifndef UAV_SAR_CONFIG_H
#define UAV_SAR_CONFIG_H

// Scenario orchestrator: builds the network, PECEE substrate, clue field, target
// profile, wires the region coordinator + all apps, runs the sim, exports
// metrics. One end-to-end SAR run.

#include "../models/network/sar-network.h"
#include "../models/network/phy-stats.h"
#include "../models/common/cell-grid.h"
#include "../models/common/inter-cell-routing.h"
#include "../models/common/sar-metrics.h"
#include "../models/application/region-coordinator.h"
#include "../models/application/sar-ground-app.h"
#include "../models/application/sar-fast-uav-app.h"
#include "../models/application/sar-data-uav-app.h"
#include "../models/application/sar-bs-app.h"

#include "ns3/lr-wpan-helper.h"

#include <cstdint>
#include <map>
#include <memory>
#include <string>

namespace ns3::uavsar {

struct SarScenarioConfig {
    uint32_t gridSize = 8;
    double gridSpacing = 20.0;
    uint32_t numUav = 4;
    double fastRatio = 0.5;
    uint32_t seed = 1;
    double simTime = 200.0;
    double minObserveS = 20.0;   // proposed: hold the first summon this long (coverage)
    double clueDecayM = 60.0;    // clue-field decay (on-node detector sensing range)
    // audit F4: under RATELESS recovery the baseline meets its own goal (98.8% of
    // GTs, 100% of victims) at R=1.2; the old default of 3.0 was an artifact of
    // the uncoded-repetition implementation and inflated every hover ~2.5x.
    double mcRedundancy = 1.2;   // tsp-mc: coded-multicast overhead factor (dwell sizing)
    double mcRadiusM = 0.0;      // tsp-mc: VBS coverage radius (0 = kUavBroadcastRadiusM)
    double fastSpeedMps = 0.0;   // 0 = kFastSpeedMps (audit F1: equal by default)
    double dataSpeedMps = 0.0;   // 0 = kDataSpeedMps
    bool   allHome = true;       // audit F2: mission completes only when EVERY UAV
                                 // has returned to the BS and reported (all schemes)
    bool   codedMulticast = true;// audit F4: rateless semantics for tsp-mc GTs
    // audit W1: aim at the strongest reporter. This is the DEFAULT because the
    // noise sweep (tools/campaign_noise.py, both grids, N=20) found argmax
    // better or tied at every noisy operating point, and found the
    // evidence^2-weighted centroid collapsing at detector sigma 0.20 (64.6 m
    // median vs 24.1, Cliff delta +0.51) -- a distant false positive enters the
    // centroid with SQUARED weight. --aimArgmax=0 selects the centroid as the
    // ablation arm.
    bool   aimArgmax = true;
    bool   electSuppress = true; // audit B2: flood the stand-down (off = ablation:
                                 // every alerting cell summons independently)
    // audit M9/W3/W7: realism knobs for the sensing side. All default to the
    // idealized values the earlier results were measured under, so the noise-free
    // case stays reproducible and becomes the ABLATION rather than the claim.
    // audit A10: adaptive observation window is the default; --adaptiveWindow=0
    // restores the fixed wall-clock --minObserve as the ablation arm.
    bool   adaptiveWindow = true;
    // DATA UAVs patrol their band spreading cues while waiting to be summoned,
    // instead of parking at the field centre.
    //
    // Measured net-negative at 16x16 (+14% packets, -2.5 pp reliability) and
    // switched off -- but that was measured under the UNIQUENESS assumption,
    // where spreading data early buys nothing except coverage. It is no longer
    // the same experiment: with confusable objects present, cue coverage is what
    // lets the evidence field self-correct before a delivery is ever aimed, so
    // the arm has to be re-measured rather than inherited. Default back ON; the
    // old measurement is the ablation.
    //
    // The payload stays CUES, not the full dataset. Cues are 2400 B against
    // 18400 B for the full reference (7.7x), and a UAV blanketing the field with
    // the full dataset is the nocoop blind-coverage baseline -- which is the arm
    // this scheme exists to beat, not to become.
    bool   dataPatrol = true;
    // Distinct from dataPatrol: cue on the legs already being flown (climb,
    // transit, loiter) instead of only while patrolling. Costs no extra flight,
    // so unlike dataPatrol it has no airtime price -- only radio.
    bool   dataCueEnroute = true;
    // Reliability/cost knob. 20 s keeps the cost advantage at every density;
    // 40 s buys ~+6 pp victim-served but costs the 8x8 advantage outright.
    // Measured at N=120, both scales -- see RESULTS-honest.md.
    double deliverDwellS = 0.0;  // 0 = kMinDeliverDwellS
    double senseSigma = 0.0;     // detector noise, additive sigma on clueQuality
    double gpsSigmaM = 0.0;      // per-node frozen GPS offset, sigma in metres
    bool   victimOnNode = true;  // false = victim at a continuous position (W7)
    // World-level ambiguity: M objects in the area that genuinely match the
    // reference dataset (another hiker in the same jacket, the search party).
    // 0 = the uniqueness assumption every earlier result was measured under.
    // similarity 1.0 means indistinguishable by this sensing modality, which
    // caps ANY algorithm at 1/(M+1) for picking the victim -- so the sweep is
    // over an identifiability floor, not over a controller's competence.
    uint32_t clutterCount = 0;
    double clutterSimMin = 0.60;
    double clutterSimMax = 1.00;
    // How much of a confusable object's similarity the COMPLETE dataset removes.
    // 1.0 (default) says delivering the full reference settles the identity,
    // which is the scheme's actual premise: a node judging on cue fragments can
    // false-alarm, a node holding everything cannot. 0 restores the pessimistic
    // case where ambiguity survives delivery.
    double clutterResolve = 1.0;
    std::string scheme = "proposed";
    std::string outputDir = "data/results/uav-sar/run-1";
};

class SarScenario {
public:
    void Run(const SarScenarioConfig& cfg);

private:
    std::unique_ptr<ns3::LrWpanHelper> m_lr;
    SarMetrics m_metrics;
    PhyStats m_phyStats;
    CellGridPlan m_plan;
    InterCellRouting m_routing;
    RegionCoordinator m_coord;
    std::map<uint32_t, ns3::Ptr<SarGroundApp>> m_groundById;
};

}  // namespace ns3::uavsar

#endif  // UAV_SAR_CONFIG_H
