#ifndef UAV_SAR_REGION_COORDINATOR_H
#define UAV_SAR_REGION_COORDINATOR_H

// Event-level control plane (the design keeps control-plane event-level, only
// summon/data/report cross the radio). Ground nodes report clue evidence to
// their Cell Leader; the coordinator aggregates soft evidence per cell, links
// adjacent clue-cells into ONE region via inter-cell routing (cross-cell
// cooperation), elects the region leader (clue-cell CL with the strongest
// aggregate), and fires a single summon through it — preventing a call storm
// while merging cameras spread across several cells.

#include "../common/cell-grid.h"
#include "../common/inter-cell-routing.h"

#include <cstdint>
#include <functional>
#include <map>
#include <set>

namespace ns3::uavsar {

class SarMetrics;

class RegionCoordinator {
public:
    // onSummon(leaderNodeId, regionId, centroidX, centroidY): start the summon
    // at the region-leader ground node (packet-level).
    using SummonCb = std::function<void(uint32_t, uint16_t, double, double)>;

    void Init(const CellGridPlan* plan, const InterCellRouting* routing,
              SarMetrics* metrics, double alertThreshold, double coopThreshold,
              SummonCb cb);

    // A node's local soft evidence (cueConfidence * clueQuality) at time t.
    void ReportClue(uint32_t nodeId, double evidence, double tNow);

    bool Summoned() const { return m_summoned; }

private:
    void MaybeFormRegion(double tNow);

    const CellGridPlan* m_plan = nullptr;
    const InterCellRouting* m_routing = nullptr;
    SarMetrics* m_metrics = nullptr;
    double m_alert = 0.75;
    double m_coop = 0.30;
    SummonCb m_onSummon;

    std::map<uint32_t, double> m_nodeEvidence;  // nodeId -> strongest evidence
    bool m_summoned = false;
};

}  // namespace ns3::uavsar

#endif  // UAV_SAR_REGION_COORDINATOR_H
