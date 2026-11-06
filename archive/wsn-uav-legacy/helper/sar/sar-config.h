#ifndef WSN_UAV_SAR_CONFIG_H
#define WSN_UAV_SAR_CONFIG_H

// Orchestrator for the SAR experiment. Three-step workflow Build/Schedule/Run.
// Builds the multi-UAV network, splits the search dataset into fragments,
// assigns them to UAVs by role, picks the victim's target node, wires RX
// callbacks, runs the sim, and exports metrics + replay CSVs.

#include "../../models/network/sar-network.h"
#include "../../models/application/sar-uav-app.h"
#include "../../models/application/sar-ground-app.h"
#include "../../models/common/sar-metrics.h"
#include "../../models/common/sar-types.h"

#include "ns3/lr-wpan-helper.h"

#include <cstdint>
#include <memory>
#include <string>
#include <vector>

namespace ns3::wsn::uav {

class SarConfig {
public:
    // --- knobs (set before Build) ---
    uint32_t gridSize = 8;
    double gridSpacing = 20.0;
    uint32_t numUav = 4;
    uint32_t numFrag = 12;
    uint32_t maxFragBytes = 4000;   // round-1 tractable scale; model supports 20000
    uint32_t seed = 1;
    double simTime = 120.0;
    sar::Scheme scheme = sar::Scheme::PROPOSED;

    uint32_t confirmNeighbors = 1;
    double confirmTimeout = 0.5;
    uint32_t beaconQuota = 60;   // low-rate (1/s) persistent summon until a DATA UAV arrives

    double fastSpeed = 25.0;
    double dataSpeed = 15.0;
    double cruiseAlt = 20.0;

    std::string outputDir = "data/results/scenario-sar/run-001";
    std::string scenarioName = "scenario-sar";

    void Build();
    void Schedule();
    void Run();

private:
    std::unique_ptr<ns3::LrWpanHelper> m_lrWpan;
    SarNetworkSetup m_setup;
    SarMetrics m_metrics;
    std::vector<ns3::Ptr<SarUavApp>> m_uavApps;
    std::vector<ns3::Ptr<SarGroundApp>> m_groundApps;
    uint32_t m_targetNodeId = 0;
};

}  // namespace ns3::wsn::uav

#endif  // WSN_UAV_SAR_CONFIG_H
