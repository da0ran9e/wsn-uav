/*
 * Statistics collection for simulation metrics
 */

#ifndef WSN_UAV_STATISTICS_COLLECTOR_H
#define WSN_UAV_STATISTICS_COLLECTOR_H

#include "ns3/object.h"
#include "ns3/vector.h"
#include "ns3/simulator.h"
#include <cstdint>
#include <map>
#include <vector>
#include <string>

namespace ns3 {
namespace wsn {
namespace uav {

// ============================================================================
// Event Records (for CSV export)
// ============================================================================

struct UavPositionRecord {
    double timeSeconds = 0.0;
    double x = 0.0, y = 0.0, z = 0.0;
};

struct PacketRecord {
    double timeSeconds = 0.0;
    uint32_t srcNodeId = 0;
    uint32_t dstNodeId = 0;
    uint32_t fragmentId = 0;
    bool success = false;
    double rssiDbm = 0.0;
    // Source position (for UAV, changes over time)
    double srcX = 0.0, srcY = 0.0, srcZ = 0.0;
};

struct CooperationRecord {
    double timeSeconds = 0.0;
    uint32_t srcNodeId = 0;
    uint32_t dstNodeId = 0;
    uint32_t fragmentId = 0;
};

// ============================================================================
// StatisticsCollector Class
// ============================================================================

class StatisticsCollector : public Object {
public:
    static TypeId GetTypeId();
    
    explicit StatisticsCollector();
    virtual ~StatisticsCollector();
    
    // Recording events
    void RecordDetection(uint32_t nodeId, double timeSeconds);
    void RecordUavPosition(double timeSeconds, const Vector& pos);
    void RecordPacketSent(uint32_t srcId, uint32_t dstId, uint32_t fragId, const Vector& srcPos);
    void RecordPacketReceived(uint32_t srcId, uint32_t dstId, uint32_t fragId,
                              bool success, double rssiDbm = 0.0);
    void RecordPacketDropped(uint32_t srcId, uint32_t dstId, uint32_t fragId, const Vector& srcPos);
    void RecordCooperation(uint32_t srcId, uint32_t dstId, uint32_t fragId);
    
    // Query results
    bool IsDetected() const { return m_detectionTime >= 0.0; }
    double GetDetectionTime() const { return m_detectionTime; }
    uint32_t GetDetectionNodeId() const { return m_detectionNodeId; }
    
    double GetUavPathLength() const;
    uint32_t GetTotalPacketsReceived() const { return m_packetRecords.size(); }
    uint32_t GetCooperationCount() const { return m_cooperationRecords.size(); }
    
    // Access records for export
    const std::vector<UavPositionRecord>& GetUavPositions() const { return m_uavPositions; }
    const std::vector<PacketRecord>& GetPacketRecords() const { return m_packetRecords; }
    const std::vector<CooperationRecord>& GetCooperationRecords() const { return m_cooperationRecords; }

    // Get fragment distribution per node
    const std::map<uint32_t, std::set<uint32_t>>& GetNodeFragments() const { return m_nodeFragments; }

    // Finalize: process dropped packets (unmatched broadcasts)
    void FinalizePacketRecords(double timeoutSeconds = 0.5);

    // Reset
    void Clear();
    
private:
    double m_detectionTime = -1.0;  // -1 = not detected
    uint32_t m_detectionNodeId = 0;

    std::vector<UavPositionRecord> m_uavPositions;
    std::vector<PacketRecord> m_packetRecords;
    std::vector<CooperationRecord> m_cooperationRecords;

    // Track which fragments each node has received (successful receptions only)
    std::map<uint32_t, std::set<uint32_t>> m_nodeFragments;  // nodeId -> set of fragmentIds
};

}  // namespace uav
}  // namespace wsn
}  // namespace ns3

#endif  // WSN_UAV_STATISTICS_COLLECTOR_H
