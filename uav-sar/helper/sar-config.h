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
