#include "sar-metrics.h"

#include <filesystem>
#include <fstream>
#include <iomanip>

namespace ns3::uavsar {

void SarMetrics::SetMeta(uint32_t seed, uint32_t gridSize, uint32_t numUav,
                         const std::string& scheme, uint32_t targetNodeId) {
    m_seed = seed; m_grid = gridSize; m_numUav = numUav;
    m_scheme = scheme; m_target = targetNodeId;
}

void SarMetrics::Event(double t, uint32_t id, const std::string& role,
                       const std::string& ev, const std::string& detail,
                       double x, double y, double z) {
    m_events.push_back({t, id, role, ev, detail, x, y, z});
}
void SarMetrics::Traj(double t, uint32_t uav, const std::string& role,
                      double x, double y, double z) {
    m_traj.push_back({t, uav, role, x, y, z});
}

namespace {
std::string Csv(const std::string& s) {
    if (s.find_first_of(",\"\n") == std::string::npos) return s;
    std::string o = "\"";
    for (char c : s) { if (c == '"') o += '"'; o += c; }
    return o + "\"";
}
}  // namespace

void SarMetrics::Finalize(const std::string& outDir) {
    std::filesystem::create_directories(outDir);
    {
        std::ofstream f(outDir + "/metrics.csv");
        f << "seed,gridSize,gridSpacing,numUav,scheme,targetNodeId,victimX,victimY,"
             "timeToReportAtBS_s,timeToLocalize_s,timeToCompleteData_s,"
             "regionCells,intraShares,interShares,beaconCount,custodyHandoffs,"
             "pktSent,pktRecv,bytesSent,bytesRecv,uavEnergyJ,routeDeviation_m";
        for (auto& [k, v] : m_extra) f << "," << k;
        f << "\n";
        f << std::fixed << std::setprecision(4)
          << m_seed << "," << m_grid << "," << m_spacing << "," << m_numUav << ","
          << m_scheme << "," << m_target << "," << m_vx << "," << m_vy << "," << m_tReport << "," << m_tLocalize << "," << m_tComplete << ","
          << m_regionCells << "," << m_intraShares << "," << m_interShares << ","
          << m_beacons << "," << m_custody << "," << m_sent << "," << m_recv << ","
          << m_sentBytes << "," << m_recvBytes << ","
          << m_energyJ << "," << m_devM;
        for (auto& [k, v] : m_extra) f << "," << v;
        f << "\n";
    }
    {
        std::ofstream f(outDir + "/events.csv");
        f << "t,nodeId,role,event,detail,x,y,z\n" << std::fixed << std::setprecision(4);
        for (auto& e : m_events)
            f << e.t << "," << e.nodeId << "," << Csv(e.role) << "," << Csv(e.event) << ","
              << Csv(e.detail) << "," << e.x << "," << e.y << "," << e.z << "\n";
    }
    {
        std::ofstream f(outDir + "/trajectories.csv");
        f << "t,uavId,role,x,y,z\n" << std::fixed << std::setprecision(4);
        for (auto& r : m_traj)
            f << r.t << "," << r.uavId << "," << Csv(r.role) << ","
              << r.x << "," << r.y << "," << r.z << "\n";
    }
    {
        std::ofstream f(outDir + "/config.txt");
        f << "seed=" << m_seed << "\ngridSize=" << m_grid << "\nnumUav=" << m_numUav
          << "\nscheme=" << m_scheme << "\ntargetNodeId=" << m_target << "\n";
    }
}

}  // namespace ns3::uavsar
