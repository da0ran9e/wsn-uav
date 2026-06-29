#ifndef WSN_UAV_SAR_METRICS_H
#define WSN_UAV_SAR_METRICS_H

// Metrics collector for the SAR scenario. Apps push events here with explicit
// simulation timestamps (kept ns-3-free). On Finalize() it writes:
//   <outdir>/metrics.csv       one aggregate row for the run
//   <outdir>/events.csv        per-event timeline (for the HTML visualizer)
//   <outdir>/trajectories.csv  UAV paths (for the HTML visualizer)
//   <outdir>/config.txt        run parameters
//
// Primary metric: timeToCompleteData_s = time until the target node holds the
// COMPLETE dataset (all fragments) after confirmation. -1 if never achieved.

#include <cstdint>
#include <string>
#include <vector>

namespace ns3::wsn::uav {

struct EventRow {
    double t;
    uint32_t nodeId;
    std::string role;
    std::string event;
    std::string detail;
    double x, y, z;
};

struct TrajRow {
    double t;
    uint32_t uavId;
    std::string role;
    double x, y, z;
};

class SarMetrics {
public:
    // --- run metadata ---
    void SetMeta(uint32_t seed, uint32_t gridSize, uint32_t numUav,
                 uint32_t numFrag, const std::string& scheme,
                 uint32_t targetNodeId);

    // --- timeline pushes (called from apps) ---
    void Event(double t, uint32_t nodeId, const std::string& role,
               const std::string& event, const std::string& detail,
               double x = 0, double y = 0, double z = 0);
    void Trajectory(double t, uint32_t uavId, const std::string& role,
                    double x, double y, double z);

    // --- milestone markers ---
    void MarkFirstBeacon(double t);
    void MarkConfirm(double t);
    void MarkCompleteData(double t);          // PRIMARY metric stamp
    void AddBeacon()        { m_beaconCount++; }
    void AddCustodyHandoff(){ m_custodyHandoffs++; }
    void AddPacketSent()    { m_pktSent++; }
    void AddPacketRecv()    { m_pktRecv++; }
    void SetFragDelivered(uint32_t got, uint32_t total) { m_fragGot = got; m_fragTotal = total; }
    void AddUavEnergy(double j) { m_uavEnergyJ += j; }
    void AddRouteDeviation(double m) { m_routeDeviationM += m; }

    // --- output ---
    void Finalize(const std::string& outDir);

    double TimeToCompleteData() const { return m_tComplete; }

private:
    // meta
    uint32_t m_seed = 0, m_gridSize = 0, m_numUav = 0, m_numFrag = 0, m_targetNodeId = 0;
    std::string m_scheme = "proposed";
    // milestones
    double m_tFirstBeacon = -1, m_tConfirm = -1, m_tComplete = -1;
    // counters
    uint32_t m_beaconCount = 0, m_custodyHandoffs = 0;
    uint32_t m_pktSent = 0, m_pktRecv = 0;
    uint32_t m_fragGot = 0, m_fragTotal = 0;
    double m_uavEnergyJ = 0, m_routeDeviationM = 0;
    // timelines
    std::vector<EventRow> m_events;
    std::vector<TrajRow> m_traj;
};

}  // namespace ns3::wsn::uav

#endif  // WSN_UAV_SAR_METRICS_H
