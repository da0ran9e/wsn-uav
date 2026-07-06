#ifndef UAV_SAR_REGION_COORDINATOR_H
#define UAV_SAR_REGION_COORDINATOR_H

// Event-level control plane over the PECEE substrate, now with COST: a node's
// clue report travels its intra-cell tree to the Cell Leader with a per-hop
// delay and a success probability; when a cell first crosses the alert
// threshold a REGION WINDOW opens so neighbouring clue-cells can corroborate;
// at window close the cross-cell shares themselves succeed only with the
// inter-cell probability (via the gateways), the region leader (strongest
// aggregate) is elected, and ONE summon is fired. This makes the cross-cell
// cooperation neither free nor instantaneous (review finding F4).

#include "../common/cell-grid.h"
#include "../common/inter-cell-routing.h"

#include <cstdint>
#include <functional>
#include <map>
#include <random>
#include <set>
#include <utility>
#include <vector>

namespace ns3::uavsar {

class SarMetrics;

class RegionCoordinator {
public:
    // onSummon(regionLeaderNodes, verifierNodeId, regionId).
    // ALL Cell Leaders of the formed region beacon the SAME ticket — under
    // realistic A2G footprints a single beaconing CL is a needle for the
    // sweeping FAST team; the region's CLs together form a bigger acoustic
    // surface while staying bounded (|region| x quota, still no node storm).
    // The verifier is the strongest-evidence node in the region — the node
    // whose clue raised the alarm; it alone confirms the delivery (its footage
    // is what the full data must be checked against).
    using SummonCb =
        std::function<void(const std::vector<uint32_t>&, uint32_t, uint16_t)>;

    void Init(const CellGridPlan* plan, const InterCellRouting* routing,
              SarMetrics* metrics, double alertThreshold, double coopThreshold,
              uint32_t seed, SummonCb cb);

    // Node-side entry: evidence submitted at time tNow; transport to the CL is
    // simulated (per-hop delay + intra-cell success probability).
    void ReportClue(uint32_t nodeId, double evidence, double tNow);

    // A cross-cell SHARE flood physically reached toCell's leader from fromCell
    // over the real radio — record the edge so region growth uses only links the
    // channel actually carried (replaces the kCoopSuccInter probability proxy).
    void RecordShare(int32_t fromCell, int32_t toCell);

    bool Summoned() const { return m_summoned; }

private:
    void EvidenceArrive(uint32_t nodeId, double evidence);  // at the CL
    void CloseWindow();                                     // region formation

    const CellGridPlan* m_plan = nullptr;
    const InterCellRouting* m_routing = nullptr;
    SarMetrics* m_metrics = nullptr;
    double m_alert = 0.75;
    double m_coop = 0.30;
    SummonCb m_onSummon;
    std::mt19937 m_rng{1};
    std::uniform_real_distribution<double> m_u01{0.0, 1.0};

    std::map<uint32_t, double> m_nodeEvidence;  // nodeId -> strongest evidence at CL
    std::set<std::pair<int32_t, int32_t>> m_shareEdges;  // cross-cell links via real SHARE
    bool m_windowOpen = false;
    bool m_summoned = false;
};

}  // namespace ns3::uavsar

#endif  // UAV_SAR_REGION_COORDINATOR_H
