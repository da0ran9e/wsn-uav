#ifndef WSN_UAV_LOG_H
#define WSN_UAV_LOG_H

#include "ns3/ptr.h"

#include <sstream>
#include <string>

namespace ns3 { class Node; }

namespace ns3::wsn::uav {

// One structured event row in the simulation event log.
// Captures content via operator<<; emits a markdown table row on destruction.
// Columns: simtime | module | content
class LogRow {
public:
    LogRow();                                                       // -, -, content
    explicit LogRow(double simtime);                                // t, -, content
    explicit LogRow(std::string module);                            // -, module, content
    LogRow(double simtime, std::string module);                     // t, module, content
    ~LogRow();

    LogRow(const LogRow&) = delete;
    LogRow& operator=(const LogRow&) = delete;
    LogRow(LogRow&& other) noexcept;

    template <typename T>
    LogRow& operator<<(const T& x) { m_content << x; return *this; }

private:
    bool m_hasTime;
    bool m_alive;                  // false after move-out (single emit)
    double m_time;
    std::string m_module;          // empty == "-"
    std::ostringstream m_content;
};

// ---------------------------------------------------------------------------
// Builders.
// Module-naming convention (ns-3 style path):
//   Node[<id>].Application   — application layer of a specific node
//   Node[<id>].Phy           — PHY layer
//   Node[<id>].Mac           — MAC layer
//   Node[<id>].Mobility      — mobility model / actuator
//   Scenario1Config          — orchestrator
//   Scenario1Network         — network builder
// Use LogN() from inside node-bound code; it fills in Node[<id>].<submodule>
// and the current simulation time automatically.
// ---------------------------------------------------------------------------
LogRow Log();                                                       // info (no time, no module)
LogRow Log(double t);                                               // event w/o module
LogRow Log(double t, std::string module);                           // event with explicit module
LogRow LogM(std::string module);                                    // info from a named module
LogRow LogN(ns3::Ptr<ns3::Node> node,
            std::string submodule = "Application");                 // auto: t=Now(), module=Node[<id>].<submodule>
LogRow LogT(std::string module);                                    // auto: t=Now(), with explicit module name

// File: src/wsn-uav/docs/visualize/result/<scenarioName>/<dd-MM-yy>/<hh-mm-ss>.md
// cwd-relative; ns3 is run from the ns-3 root.
void LogReset(const std::string& scenarioName = "scenario1");
void LogFlush();

}  // namespace ns3::wsn::uav

#endif  // WSN_UAV_LOG_H
