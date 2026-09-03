// End-to-end SAR scenario entry point.
#include "ns3/core-module.h"
#include "../helper/sar-config.h"

#include <iostream>
#include <string>

using namespace ns3;
using namespace ns3::uavsar;

int main(int argc, char* argv[]) {
    SarScenarioConfig cfg;
    std::string outputDir;
    CommandLine cmd;
    cmd.AddValue("gridSize", "N x N sensor grid", cfg.gridSize);
    cmd.AddValue("gridSpacing", "sensor spacing (m)", cfg.gridSpacing);
    cmd.AddValue("numUav", "number of UAVs", cfg.numUav);
    cmd.AddValue("fastRatio", "fraction of UAVs on the FAST team", cfg.fastRatio);
    cmd.AddValue("seed", "RNG run seed", cfg.seed);
    cmd.AddValue("simTime", "sim duration (s)", cfg.simTime);
    cmd.AddValue("minObserve", "proposed: hold first summon until this time (s)", cfg.minObserveS);
    cmd.AddValue("clueDecay", "clue-field decay / on-node sensing range (m)", cfg.clueDecayM);
    cmd.AddValue("mcRedundancy", "tsp-mc: coded-multicast overhead factor", cfg.mcRedundancy);
    cmd.AddValue("mcRadius", "tsp-mc: VBS coverage radius m (0=design default)", cfg.mcRadiusM);
    cmd.AddValue("fastSpeed", "FAST UAV cruise m/s (0 = common speed)", cfg.fastSpeedMps);
    cmd.AddValue("dataSpeed", "DATA UAV cruise m/s (0 = common speed)", cfg.dataSpeedMps);
    cmd.AddValue("allHome", "mission completes only when EVERY UAV reported", cfg.allHome);
    cmd.AddValue("codedMulticast", "tsp-mc: rateless recovery (Zeng'18 semantics)", cfg.codedMulticast);
    cmd.AddValue("aimArgmax", "aim at strongest reporter (default; 0 = centroid ablation)", cfg.aimArgmax);
    cmd.AddValue("electSuppress", "flood the election stand-down (0 = ablation)", cfg.electSuppress);
    cmd.AddValue("electScope", "stand down only for claims within this many m (0 = field-wide)", cfg.electScopeM);
    cmd.AddValue("aimScope", "leader may aim only this far from its own cell (0 = unbounded)", cfg.aimScopeM);
    cmd.AddValue("stayAvailable", "a DATA UAV that loses a CLAIM waits for another region", cfg.stayAvailable);
    cmd.AddValue("fixOnConfirm", "report a position only for a CONFIRMED delivery", cfg.fixOnConfirm);
    cmd.AddValue("confirmThreshold", "evidence bar for CONFIRM (identity claim)", cfg.confirmThreshold);
    cmd.AddValue("adaptiveWindow", "summon when evidence settles (0 = fixed --minObserve)", cfg.adaptiveWindow);
    cmd.AddValue("dataPatrol", "DATA UAVs patrol+cue while waiting (0 = park)", cfg.dataPatrol);
    cmd.AddValue("dataCueEnroute", "DATA UAVs cue on legs already flown (1 = default)", cfg.dataCueEnroute);
    cmd.AddValue("deliverDwell", "min delivery dwell s (0 = design default)", cfg.deliverDwellS);
    cmd.AddValue("senseSigma", "detector noise sigma on clue quality (0 = ideal)", cfg.senseSigma);
    cmd.AddValue("gpsSigma", "per-node GPS error sigma in m (0 = exact)", cfg.gpsSigmaM);
    cmd.AddValue("lanePlan", "one field-wide lane set, each lane owned by one FAST UAV", cfg.lanePlan);
    cmd.AddValue("cellCoverTarget", "seed this fraction of each cell's capability (0 = cover nodes)", cfg.cellCoverTarget);
    cmd.AddValue("laneCandidateSpacing", "candidate lane pitch for the cell selector (m)", cfg.laneCandidateSpacing);
    cmd.AddValue("balanceAlpha", "1 = balance flight effort only, 0 = capability only", cfg.balanceAlpha);
    cmd.AddValue("capPriorityExp", "planner's exponent on node capability (0 = blind, >1 = chase the best)", cfg.capPriorityExp);
    cmd.AddValue("noFly", "no-fly zones as cx,cy,r;cx,cy,r", cfg.noFly);
    cmd.AddValue("uniformNodes", "all nodes fully capable (1) or heterogeneous (0)", cfg.uniformNodes);
    cmd.AddValue("cameraFraction", "share of nodes carrying a camera", cfg.cameraFraction);
    cmd.AddValue("phaseGate", "rotary team waits for the fixed-wing sweep to finish", cfg.phaseGate);
    cmd.AddValue("phaseGateDeadline", "fail-open bound on the phase gate (s)", cfg.phaseGateDeadlineS);
    cmd.AddValue("phaseGateGround", "rotary team waits on the ground, not airborne", cfg.phaseGateGround);
    cmd.AddValue("phaseGateMode", "what Phase 2 waits for: sweep | home | flag", cfg.phaseGateMode);
    cmd.AddValue("victimOnNode", "victim sits exactly on a sensor (0 = continuous)", cfg.victimOnNode);
    cmd.AddValue("fixFirst", "a UAV holding a confirmed fix flies it home before taking another candidate", cfg.fixFirst);
    cmd.AddValue("victimCount", "number of REAL victims (1 = the classic setting)", cfg.victimCount);
    cmd.AddValue("victimMinSep", "minimum separation between real victims (m)", cfg.victimMinSepM);
    cmd.AddValue("clutterCount", "confusable objects matching the reference data (0 = uniqueness)", cfg.clutterCount);
    cmd.AddValue("clutterSimMin", "min similarity of a confusable object", cfg.clutterSimMin);
    cmd.AddValue("clutterSimMax", "max similarity (1.0 = indistinguishable)", cfg.clutterSimMax);
    cmd.AddValue("clutterResolve", "how much the FULL dataset resolves a confusable object", cfg.clutterResolve);
    cmd.AddValue("scheme", "proposed | closed-loop | nocoop | pure-uav | tsp-mc", cfg.scheme);
    cmd.AddValue("outputDir", "results dir", outputDir);
    cmd.Parse(argc, argv);

    if (cfg.scheme != "proposed" && cfg.scheme != "nocoop" && cfg.scheme != "pure-uav" &&
        cfg.scheme != "tsp-mc" && cfg.scheme != "closed-loop") {
        std::cerr << "unknown --scheme=" << cfg.scheme
                  << " (expected proposed | closed-loop | nocoop | pure-uav | tsp-mc)\n";
        return 1;
    }

    if (outputDir.empty())
        outputDir = "data/results/uav-sar/" + cfg.scheme + "/run-" + std::to_string(cfg.seed);
    cfg.outputDir = outputDir;

    SarScenario sc;
    sc.Run(cfg);
    return 0;
}
