#include "log.h"

#include "ns3/node.h"
#include "ns3/simulator.h"

#include <chrono>
#include <ctime>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>

namespace ns3::wsn::uav {

static std::ofstream g_logFile;
static std::ostream* g_logStream = &std::cerr;

// ---------------------------------------------------------------------------
// Markdown row helpers
// ---------------------------------------------------------------------------

static std::string EscapeContent(std::string s) {
    while (!s.empty() && (s.back() == '\n' || s.back() == '\r' || s.back() == ' ')) {
        s.pop_back();
    }
    std::string out;
    out.reserve(s.size());
    for (char c : s) {
        if (c == '|') out += "\\|";
        else if (c == '\n') out += "<br>";
        else if (c == '\r') /* drop */;
        else out += c;
    }
    return out;
}

// ---------------------------------------------------------------------------
// LogRow
// ---------------------------------------------------------------------------

LogRow::LogRow() : m_hasTime(false), m_alive(true), m_time(0.0) {}

LogRow::LogRow(double simtime) : m_hasTime(true), m_alive(true), m_time(simtime) {}

LogRow::LogRow(std::string module)
    : m_hasTime(false), m_alive(true), m_time(0.0), m_module(std::move(module)) {}

LogRow::LogRow(double simtime, std::string module)
    : m_hasTime(true), m_alive(true), m_time(simtime), m_module(std::move(module)) {}

LogRow::LogRow(LogRow&& other) noexcept
    : m_hasTime(other.m_hasTime), m_alive(other.m_alive),
      m_time(other.m_time), m_module(std::move(other.m_module)),
      m_content(std::move(other.m_content)) {
    other.m_alive = false;
}

LogRow::~LogRow() {
    if (!m_alive) return;

    std::ostringstream out;
    out << "| ";
    if (m_hasTime) out << std::fixed << std::setprecision(6) << m_time;
    else           out << "-";

    out << " | ";
    if (!m_module.empty()) out << m_module;
    else                   out << "-";

    out << " | " << EscapeContent(m_content.str()) << " |\n";

    *g_logStream << out.str();
}

// ---------------------------------------------------------------------------
// Free helpers
// ---------------------------------------------------------------------------

LogRow Log() { return LogRow(); }
LogRow Log(double t) { return LogRow(t); }
LogRow Log(double t, std::string module) { return LogRow(t, std::move(module)); }

LogRow LogM(std::string module) { return LogRow(std::move(module)); }

LogRow LogN(ns3::Ptr<ns3::Node> node, std::string submodule) {
    double t = ns3::Simulator::Now().GetSeconds();
    if (!node) {
        return LogRow(t);
    }
    std::ostringstream m;
    m << "Node[" << node->GetId() << "]." << submodule;
    return LogRow(t, m.str());
}

LogRow LogT(std::string module) {
    double t = ns3::Simulator::Now().GetSeconds();
    return LogRow(t, std::move(module));
}

// ---------------------------------------------------------------------------
// File management
// ---------------------------------------------------------------------------

static std::string BuildLogPath(const std::string& scenarioName) {
    auto now = std::chrono::system_clock::now();
    std::time_t t = std::chrono::system_clock::to_time_t(now);
    std::tm tm = *std::localtime(&t);

    char dateBuf[16];
    char timeBuf[16];
    std::strftime(dateBuf, sizeof(dateBuf), "%d-%m-%y", &tm);
    std::strftime(timeBuf, sizeof(timeBuf), "%H-%M-%S", &tm);

    namespace fs = std::filesystem;
    fs::path dir = fs::path("src/wsn-uav/docs/visualize/result") /
                   scenarioName / dateBuf;
    std::error_code ec;
    fs::create_directories(dir, ec);
    if (ec) {
        std::cerr << "[wsn-uav log] mkdir '" << dir.string()
                  << "' failed: " << ec.message() << "\n";
    }
    return (dir / (std::string(timeBuf) + ".md")).string();
}

void LogReset(const std::string& scenarioName) {
    if (g_logFile.is_open()) g_logFile.close();

    std::string path = BuildLogPath(scenarioName);
    g_logFile.open(path, std::ios::out | std::ios::trunc);
    if (!g_logFile.is_open()) {
        g_logStream = &std::cerr;
        std::cerr << "[wsn-uav log] failed to open '" << path
                  << "', falling back to stderr\n";
        return;
    }
    g_logStream = &g_logFile;

    g_logFile << "# " << scenarioName << " event log\n\n";
    g_logFile << "Log file: `" << path << "`\n\n";
    g_logFile << "| simtime | module | content |\n";
    g_logFile << "|---------|--------|---------|\n";
}

void LogFlush() {
    if (g_logFile.is_open()) g_logFile.flush();
}

}  // namespace ns3::wsn::uav
