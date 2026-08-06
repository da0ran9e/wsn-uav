#include "sar-metrics.h"

#include <cmath>
#include <filesystem>
#include <sys/stat.h>
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
             "pktSent,pktRecv,bytesSent,bytesRecv,uavEnergyJ,routeDeviation_m,"
             // audit B3: the fix as DECODED AT THE BS (-1 / empty = the BS never
             // learned a position, which is the honest outcome for every
             // blind-coverage baseline).
             "timeToFixAtBS_s,reportedX,reportedY,reportErr_m,"
             // World-level ambiguity. fixOnVictim = the delivered position is
             // closer to the victim than to any confusable object; -1 = no fix.
             // Without this split, "closed the loop on the wrong person" and
             // "estimated the right person imprecisely" are the same number.
             "clutterCount,fixOnVictim,fixToNearestClutter_m";
        for (auto& [k, v] : m_extra) f << "," << k;
        f << "\n";
        const double fixErr =
            m_hasFix ? std::hypot(m_fixX - m_vx, m_fixY - m_vy) : -1.0;
        double clutterD = -1.0;
        int fixOnVictim = -1;
        if (m_hasFix) {
            for (const auto& c : m_clutter) {
                double d = std::hypot(m_fixX - c.x, m_fixY - c.y);
                if (clutterD < 0 || d < clutterD) clutterD = d;
            }
            fixOnVictim = (clutterD < 0 || fixErr <= clutterD) ? 1 : 0;
        }
        f << std::fixed << std::setprecision(4)
          << m_seed << "," << m_grid << "," << m_spacing << "," << m_numUav << ","
          << m_scheme << "," << m_target << "," << m_vx << "," << m_vy << "," << m_tReport << "," << m_tLocalize << "," << m_tComplete << ","
          << m_regionCells << "," << m_intraShares << "," << m_interShares << ","
          << m_beacons << "," << m_custody << "," << m_sent << "," << m_recv << ","
          << m_sentBytes << "," << m_recvBytes << ","
          << m_energyJ << "," << m_devM << ","
          << m_tFix << "," << (m_hasFix ? m_fixX : -1.0) << ","
          << (m_hasFix ? m_fixY : -1.0) << "," << fixErr << ","
          << m_clutter.size() << "," << fixOnVictim << "," << clutterD;
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
        // Audit meta-finding: a rebuild during two in-flight campaigns silently
        // mixed binaries within one campaign, and it was caught only because the
        // timing happened to be noticed. Stamping the build identity into every
        // run lets the analysis scripts REFUSE to aggregate across builds
        // instead of relying on someone remembering.
        f << "build=" << __DATE__ << " " << __TIME__ << "\n";
        // STATUS.md open problem 5: the line above is compiled into THIS
        // translation unit, so it only moves when this file recompiles -- a
        // rebuild that changed any other source leaves it identical and the
        // guard passes on a genuinely mixed campaign. That is not hypothetical:
        // flipping a default in sar-config.h changes behaviour and leaves this
        // stamp untouched. Stat the running executable instead, which moves on
        // every relink.
        {
            struct stat st;
            if (::stat("/proc/self/exe", &st) == 0)
                f << "binary=" << (long long)st.st_mtime << "," << (long long)st.st_size << "\n";
        }
        // The ambiguity regime, for the same reason as build=: clutterCount = 0
        // is the uniqueness assumption the baseline comparisons are measured
        // under, and pooling it with clutterCount > 0 runs is meaningless but
        // invisible. campaign_common.assert_one_clutter refuses to aggregate
        // across regimes on the strength of this line.
        double sMin = 0, sMax = 0;
        for (size_t i = 0; i < m_clutter.size(); ++i) {
            if (i == 0 || m_clutter[i].similarity < sMin) sMin = m_clutter[i].similarity;
            if (i == 0 || m_clutter[i].similarity > sMax) sMax = m_clutter[i].similarity;
        }
        f << "clutter=" << m_clutter.size() << "," << sMin << "," << sMax << "\n";
    }
}

}  // namespace ns3::uavsar
