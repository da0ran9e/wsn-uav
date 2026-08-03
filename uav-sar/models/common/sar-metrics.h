#ifndef UAV_SAR_METRICS_H
#define UAV_SAR_METRICS_H

// Full-loop metrics collector. Apps push events with explicit sim timestamps.
// Primary metric: timeToReportAtBS_s (start -> small report reaches BS).
// Writes metrics.csv (1 row), events.csv, trajectories.csv, config.txt.

#include <cstdint>
#include <map>
#include <string>
#include <vector>

namespace ns3::uavsar {

struct MEvent { double t; uint32_t nodeId; std::string role, event, detail; double x, y, z; };
struct MTraj  { double t; uint32_t uavId; std::string role; double x, y, z; };

class SarMetrics {
public:
    void SetMeta(uint32_t seed, uint32_t gridSize, uint32_t numUav,
                 const std::string& scheme, uint32_t targetNodeId);
    // audit S9/W8: emit ground truth and the swept parameters, so analysis scripts
    // stop reconstructing the victim position from a hard-coded 20 m spacing
    // (which was ~11x wrong at any other spacing) and a run dir is self-describing.
    void SetGroundTruth(double vx, double vy, double spacing) {
        m_vx = vx; m_vy = vy; m_spacing = spacing;
    }

    void Event(double t, uint32_t id, const std::string& role,
               const std::string& ev, const std::string& detail,
               double x = 0, double y = 0, double z = 0);
    void Traj(double t, uint32_t uav, const std::string& role, double x, double y, double z);

    void MarkLocalize(double t)     { if (m_tLocalize < 0) m_tLocalize = t; }
    void MarkCompleteData(double t) { if (m_tComplete < 0) m_tComplete = t; }
    void MarkReportAtBS(double t)   { if (m_tReport < 0) m_tReport = t; }

    void AddIntraShare()   { m_intraShares++; }
    void AddInterShare()   { m_interShares++; }
    void SetRegionCells(uint32_t n) { m_regionCells = n; }
    void AddBeacon()       { m_beacons++; }
    void AddCustody()      { m_custody++; }
    void AddSent()         { m_sent++; }
    void AddRecv()         { m_recv++; }
    void AddSentBytes(uint64_t b) { m_sentBytes += b; }
    void AddRecvBytes(uint64_t b) { m_recvBytes += b; }
    void AddEnergy(double j){ m_energyJ += j; }
    void AddDeviation(double m){ m_devM += m; }

    // Extra name->value columns appended to metrics.csv (e.g. PHY error stats).
    void SetExtra(const std::map<std::string, uint64_t>& e) { m_extra = e; }

    double ReportTime() const { return m_tReport; }
    void Finalize(const std::string& outDir);

private:
    uint32_t m_seed=0, m_grid=0, m_numUav=0, m_target=0;
    double m_vx=0, m_vy=0, m_spacing=0;
    std::string m_scheme="proposed";
    double m_tLocalize=-1, m_tComplete=-1, m_tReport=-1;
    uint32_t m_intraShares=0, m_interShares=0, m_regionCells=0, m_beacons=0, m_custody=0;
    uint32_t m_sent=0, m_recv=0;
    uint64_t m_sentBytes=0, m_recvBytes=0;
    double m_energyJ=0, m_devM=0;
    std::map<std::string, uint64_t> m_extra;
    std::vector<MEvent> m_events;
    std::vector<MTraj> m_traj;
};

}  // namespace ns3::uavsar

#endif  // UAV_SAR_METRICS_H
