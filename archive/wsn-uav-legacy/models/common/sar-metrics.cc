#include "sar-metrics.h"

#include <filesystem>
#include <fstream>
#include <iomanip>
#include <sstream>

namespace ns3::wsn::uav {

void SarMetrics::SetMeta(uint32_t seed, uint32_t gridSize, uint32_t numUav,
                         uint32_t numFrag, const std::string& scheme,
                         uint32_t targetNodeId) {
    m_seed = seed;
    m_gridSize = gridSize;
    m_numUav = numUav;
    m_numFrag = numFrag;
    m_scheme = scheme;
    m_targetNodeId = targetNodeId;
}

void SarMetrics::Event(double t, uint32_t nodeId, const std::string& role,
                       const std::string& event, const std::string& detail,
                       double x, double y, double z) {
    m_events.push_back({t, nodeId, role, event, detail, x, y, z});
}

void SarMetrics::Trajectory(double t, uint32_t uavId, const std::string& role,
                            double x, double y, double z) {
    m_traj.push_back({t, uavId, role, x, y, z});
}

void SarMetrics::MarkFirstBeacon(double t) {
    if (m_tFirstBeacon < 0) m_tFirstBeacon = t;
}
void SarMetrics::MarkConfirm(double t) {
    if (m_tConfirm < 0) m_tConfirm = t;
}
void SarMetrics::MarkCompleteData(double t) {
    if (m_tComplete < 0) m_tComplete = t;
}

namespace {
std::string Csv(const std::string& s) {
    // Quote if it contains comma/quote/newline.
    bool needs = s.find_first_of(",\"\n") != std::string::npos;
    if (!needs) return s;
    std::string out = "\"";
    for (char c : s) { if (c == '"') out += '"'; out += c; }
    out += '"';
    return out;
}
}  // namespace

void SarMetrics::Finalize(const std::string& outDir) {
    std::filesystem::create_directories(outDir);

    double pdr = (m_pktSent > 0) ? static_cast<double>(m_pktRecv) / m_pktSent : 0.0;
    double fragPct = (m_fragTotal > 0)
                         ? 100.0 * static_cast<double>(m_fragGot) / m_fragTotal
                         : 0.0;

    // metrics.csv — single aggregate row (with header).
    {
        std::ofstream f(outDir + "/metrics.csv");
        f << "seed,gridSize,numUav,numFrag,scheme,targetNodeId,"
             "timeToCompleteData_s,timeToFirstBeacon_s,timeToConfirm_s,"
             "fragDeliveredPct,pdr,beaconCount,custodyHandoffs,"
             "pktSent,pktRecv,uavEnergyJ,routeDeviation_m\n";
        f << std::fixed << std::setprecision(4)
          << m_seed << "," << m_gridSize << "," << m_numUav << "," << m_numFrag << ","
          << m_scheme << "," << m_targetNodeId << ","
          << m_tComplete << "," << m_tFirstBeacon << "," << m_tConfirm << ","
          << fragPct << "," << pdr << "," << m_beaconCount << "," << m_custodyHandoffs << ","
          << m_pktSent << "," << m_pktRecv << "," << m_uavEnergyJ << ","
          << m_routeDeviationM << "\n";
    }

    // events.csv
    {
        std::ofstream f(outDir + "/events.csv");
        f << "t,nodeId,role,event,detail,x,y,z\n";
        f << std::fixed << std::setprecision(4);
        for (const auto& e : m_events) {
            f << e.t << "," << e.nodeId << "," << Csv(e.role) << ","
              << Csv(e.event) << "," << Csv(e.detail) << ","
              << e.x << "," << e.y << "," << e.z << "\n";
        }
    }

    // trajectories.csv
    {
        std::ofstream f(outDir + "/trajectories.csv");
        f << "t,uavId,role,x,y,z\n";
        f << std::fixed << std::setprecision(4);
        for (const auto& r : m_traj) {
            f << r.t << "," << r.uavId << "," << Csv(r.role) << ","
              << r.x << "," << r.y << "," << r.z << "\n";
        }
    }

    // config.txt
    {
        std::ofstream f(outDir + "/config.txt");
        f << "seed=" << m_seed << "\n"
          << "gridSize=" << m_gridSize << "\n"
          << "numUav=" << m_numUav << "\n"
          << "numFrag=" << m_numFrag << "\n"
          << "scheme=" << m_scheme << "\n"
          << "targetNodeId=" << m_targetNodeId << "\n";
    }
}

}  // namespace ns3::wsn::uav
