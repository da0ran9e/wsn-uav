/*
 * Result writer: export simulation metrics to CSV
 */

#ifndef WSN_UAV_RESULT_WRITER_H
#define WSN_UAV_RESULT_WRITER_H

#include "ns3/ptr.h"
#include "ns3/node-container.h"
#include "../models/common/statistics-collector.h"
#include <string>
#include <cstdint>
#include <set>

namespace ns3 {
namespace wsn {
namespace uav {

// Forward declarations
struct SimulationConfig;
struct SimulationResults;

// ============================================================================
// ResultWriter Class
// ============================================================================

class ResultWriter {
public:
    explicit ResultWriter(const std::string& outputDir);
    
    // Initialize output directory (create if not exists)
    bool Initialize() const;
    
    // Write outputs
    void WriteMetrics(const SimulationResults& results, const SimulationConfig& config) const;
    void WriteTrajectories(Ptr<StatisticsCollector> collector) const;
    void WritePackets(Ptr<StatisticsCollector> collector, const NodeContainer& groundNodes) const;
    void WriteConfig(const SimulationConfig& config) const;

    // Write visualization data as standalone .js file
    void WriteVisualizationData(const SimulationResults& results,
                                const SimulationConfig& config,
                                const NodeContainer& groundNodes,
                                Ptr<StatisticsCollector> collector,
                                const std::set<uint32_t>& candidateNodes) const;

private:
    std::string m_outputDir;
    
    // Helper: get full path
    std::string GetPath(const std::string& filename) const;
};

}  // namespace uav
}  // namespace wsn
}  // namespace ns3

#endif  // WSN_UAV_RESULT_WRITER_H
