/*
 * Packet Tracing Helper: Unified packet diagnostics
 *
 * Provides MAC-layer packet tracing for all scenarios
 * Tracks TX/RX packets, RSSI, source addresses, statistics
 */

#ifndef WSN_UAV_PACKET_TRACING_HELPER_H
#define WSN_UAV_PACKET_TRACING_HELPER_H

#include "ns3/net-device-container.h"
#include "ns3/ptr.h"
#include "ns3/mac16-address.h"
#include "ns3/packet.h"
#include <map>
#include <cstdint>
#include <iostream>

namespace ns3 {
namespace wsn {
namespace uav {

// ============================================================================
// Packet Tracing Statistics
// ============================================================================

struct PacketTracingStats {
    uint32_t totalTxPackets = 0;
    uint32_t totalRxPackets = 0;
    std::map<uint32_t, uint32_t> txPerNode;      // nodeId -> tx count
    std::map<uint32_t, uint32_t> rxPerNode;      // nodeId -> rx count
    std::map<uint32_t, double> avgRssiPerNode;   // nodeId -> avg RSSI
    std::map<uint32_t, uint32_t> rssiCountPerNode; // for averaging
};

// ============================================================================
// Packet Tracing Helper
// ============================================================================

class PacketTracingHelper {
public:
    explicit PacketTracingHelper();
    virtual ~PacketTracingHelper();

    // Enable packet tracing on TX side
    // Call this BEFORE simulation starts if you want to track transmissions
    void InstallTxTracing(ns3::NetDeviceContainer txDevices, uint32_t startNodeId = 0);

    // Enable packet tracing on RX side (MAC-layer callbacks)
    void InstallRxTracing(ns3::NetDeviceContainer rxDevices, uint32_t startNodeId = 0);

    // Enable tracing on both TX and RX
    void InstallFullTracing(ns3::NetDeviceContainer groundDevices,
                           ns3::NetDeviceContainer uavDevices);

    // Get statistics
    const PacketTracingStats& GetStats() const { return m_stats; }

    // Print results in formatted output
    void PrintResults(std::ostream& os = std::cout) const;

    // Reset statistics
    void Reset() { m_stats = PacketTracingStats(); }

    // Public callback for reporting TX packets (for use in applications)
    void ReportTx(uint32_t nodeId, Ptr<const Packet> pkt) { OnPacketTx(nodeId, pkt); }

    // Public callback for reporting RX packets (for use in applications)
    void ReportRx(uint32_t nodeId, Ptr<Packet> pkt, Mac16Address src, double rssi) {
        OnPacketRx(nodeId, pkt, src, rssi);
    }

private:
    PacketTracingStats m_stats;

    // Callback handlers
    void OnPacketTx(uint32_t nodeId, Ptr<const Packet> pkt);
    void OnPacketRx(uint32_t nodeId, Ptr<Packet> pkt, Mac16Address src, double rssi);
};

}  // namespace uav
}  // namespace wsn
}  // namespace ns3

#endif  // WSN_UAV_PACKET_TRACING_HELPER_H
