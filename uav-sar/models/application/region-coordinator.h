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

namespace ns3::uavsar {

class SarMetrics;

class RegionCoordinator {
public:
    // onSummon(leaderNodeId, regionId, centroidX, centroidY)
    using SummonCb = std::function<void(uint32_t, uint16_t, double, double)>;

    void Init(const CellGridPlan* plan, const InterCellRouting* routing,
              SarMetrics* metrics, double alertThreshold, double coopThreshold,
              uint32_t seed, SummonCb cb);

    // Node-side entry: evidence submitted at time tNow; transport to the CL is
    // simulated (per-hop delay + intra-cell success probability).
    void ReportClue(uint32_t nodeId, double evidence, double tNow);

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
    bool m_windowOpen = false;
    bool m_summoned = false;
};

}  // namespace ns3::uavsar

#endif  // UAV_SAR_REGION_COORDINATOR_H
