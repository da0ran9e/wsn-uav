#include "statistics-collector.h"
#include "ns3/type-id.h"

namespace ns3 {
namespace wsn {
namespace uav {

NS_OBJECT_ENSURE_REGISTERED(StatisticsCollector);

TypeId StatisticsCollector::GetTypeId() {
    static TypeId tid = TypeId("ns3::wsn::uav::StatisticsCollector")
        .SetParent<Object>()
        .SetGroupName("WsnUav")
        .AddConstructor<StatisticsCollector>();
    return tid;
}

StatisticsCollector::StatisticsCollector() {}

StatisticsCollector::~StatisticsCollector() {}

void StatisticsCollector::RecordDetection(uint32_t nodeId, double timeSeconds) {
    if (m_detectionTime < 0.0) {
        m_detectionTime = timeSeconds;
        m_detectionNodeId = nodeId;
    }
}

void StatisticsCollector::RecordUavPosition(double timeSeconds, const Vector& pos) {
    m_uavPositions.push_back({timeSeconds, pos.x, pos.y, pos.z});
}

void StatisticsCollector::RecordPacketSent(uint32_t srcId, uint32_t dstId, uint32_t fragId, const Vector& srcPos) {
    // Record sent packet with failure status initially
    // Will be updated to success if received within timeout window
    auto record = PacketRecord();
    record.timeSeconds = Simulator::Now().GetSeconds();
    record.srcNodeId = srcId;
    record.dstNodeId = dstId;
    record.fragmentId = fragId;
    record.success = false;
    record.rssiDbm = 0.0;
    record.srcX = srcPos.x;
    record.srcY = srcPos.y;
    record.srcZ = srcPos.z;
    m_packetRecords.push_back(record);
}

void StatisticsCollector::RecordPacketReceived(uint32_t srcId, uint32_t dstId, uint32_t fragId,
                                                bool success, double rssiDbm) {
    double now = Simulator::Now().GetSeconds();

    // Try to find matching sent packet and mark as success
    for (auto& rec : m_packetRecords) {
        // Match broadcast: same src, fragment, dest is 0xFFFFFFFF (broadcast), and within 1.0s window
        // Extended to 1.0s to catch received packets that match sent broadcasts
        // (accounting for propagation delays and processing latency)
        if (rec.srcNodeId == srcId && rec.fragmentId == fragId &&
            rec.dstNodeId == 0xFFFFFFFF &&  // was broadcast
            now - rec.timeSeconds < 1.0) {
            // Only mark as success if not already marked (first receiver counts)
            if (!rec.success) {
                rec.success = true;
                rec.rssiDbm = rssiDbm;
            }
            // Create a new entry for this specific receiver, copying source position from sent packet
            auto receivedRec = PacketRecord();
            receivedRec.timeSeconds = now;
            receivedRec.srcNodeId = srcId;
            receivedRec.dstNodeId = dstId;
            receivedRec.fragmentId = fragId;
            receivedRec.success = true;
            receivedRec.rssiDbm = rssiDbm;
            receivedRec.srcX = rec.srcX;  // Copy source position from sent packet
            receivedRec.srcY = rec.srcY;
            receivedRec.srcZ = rec.srcZ;
            m_packetRecords.push_back(receivedRec);

            // Track fragment reception at destination node (for coloring)
            m_nodeFragments[dstId].insert(fragId);

            return;
        }
    }

    // If no matching sent packet found, still create the record but with zero position
    // This shouldn't happen for UAV broadcasts, but just in case
    auto orphanRec = PacketRecord();
    orphanRec.timeSeconds = now;
    orphanRec.srcNodeId = srcId;
    orphanRec.dstNodeId = dstId;
    orphanRec.fragmentId = fragId;
    orphanRec.success = true;
    orphanRec.rssiDbm = rssiDbm;
    orphanRec.srcX = 0.0;
    orphanRec.srcY = 0.0;
    orphanRec.srcZ = 0.0;
    m_packetRecords.push_back(orphanRec);

    // Still track fragment reception at destination node
    m_nodeFragments[dstId].insert(fragId);
}

void StatisticsCollector::RecordPacketDropped(uint32_t srcId, uint32_t dstId, uint32_t fragId,
                                              const Vector& srcPos) {
    double now = Simulator::Now().GetSeconds();

    // Record dropped packet (success=false)
    auto dropRec = PacketRecord();
    dropRec.timeSeconds = now;
    dropRec.srcNodeId = srcId;
    dropRec.dstNodeId = dstId;
    dropRec.fragmentId = fragId;
    dropRec.success = false;
    dropRec.rssiDbm = 0.0;
    dropRec.srcX = srcPos.x;
    dropRec.srcY = srcPos.y;
    dropRec.srcZ = srcPos.z;
    m_packetRecords.push_back(dropRec);
}

void StatisticsCollector::RecordCooperation(uint32_t srcId, uint32_t dstId, uint32_t fragId) {
    m_cooperationRecords.push_back({Simulator::Now().GetSeconds(), srcId, dstId, fragId});
}

double StatisticsCollector::GetUavPathLength() const {
    if (m_uavPositions.size() < 2) return 0.0;
    
    double length = 0.0;
    for (size_t i = 1; i < m_uavPositions.size(); i++) {
        const auto& prev = m_uavPositions[i-1];
        const auto& curr = m_uavPositions[i];
        
        double dx = curr.x - prev.x;
        double dy = curr.y - prev.y;
        double dz = curr.z - prev.z;
        
        length += std::sqrt(dx*dx + dy*dy + dz*dz);
    }
    return length;
}

void StatisticsCollector::FinalizePacketRecords(double timeoutSeconds) {
    // MAC layer now tracks contact window drops directly via RecordPacketDropped
    // This method is kept for compatibility but no longer needs to infer drops
    // from timeout logic - all drops are already recorded explicitly
    (void)timeoutSeconds;  // Unused parameter
}

void StatisticsCollector::Clear() {
    m_detectionTime = -1.0;
    m_detectionNodeId = 0;
    m_uavPositions.clear();
    m_packetRecords.clear();
    m_cooperationRecords.clear();
}

}  // namespace uav
}  // namespace wsn
}  // namespace ns3
