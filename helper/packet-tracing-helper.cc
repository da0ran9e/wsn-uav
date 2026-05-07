#include "packet-tracing-helper.h"
#include "ns3/cc2420-net-device.h"
#include "ns3/cc2420-mac.h"
#include "ns3/simulator.h"
#include <iomanip>
#include <cmath>

namespace ns3 {
namespace wsn {
namespace uav {

PacketTracingHelper::PacketTracingHelper() {}

PacketTracingHelper::~PacketTracingHelper() {}

// ============================================================================
// PacketTracingHelper::InstallTxTracing()
// ============================================================================

void PacketTracingHelper::InstallTxTracing(ns3::NetDeviceContainer txDevices,
                                          uint32_t startNodeId) {
    for (uint32_t i = 0; i < txDevices.GetN(); i++) {
        uint32_t nodeId = startNodeId + i;
        auto dev = txDevices.Get(i);

        // Wrap TX callback in lambda with captured nodeId
        auto txCallback = [this, nodeId](Ptr<const Packet> pkt) {
            this->OnPacketTx(nodeId, pkt);
        };

        // Try to set TX callback on Cc2420NetDevice if available
        // (Note: may not be available for all device types)
        // For now, we'll track via explicit Send() calls in application
    }
}

// ============================================================================
// PacketTracingHelper::InstallRxTracing()
// ============================================================================

void PacketTracingHelper::InstallRxTracing(ns3::NetDeviceContainer rxDevices,
                                          uint32_t startNodeId) {
    for (uint32_t i = 0; i < rxDevices.GetN(); i++) {
        uint32_t nodeId = startNodeId + i;
        auto dev = rxDevices.Get(i);

        auto cc2420Dev = DynamicCast<wsn::Cc2420NetDevice>(dev);
        if (cc2420Dev) {
            auto mac = cc2420Dev->GetMac();
            if (mac) {
                // Bind MAC callback with captured nodeId
                mac->SetMcpsDataIndicationCallback(
                    [this, nodeId](Ptr<Packet> pkt, Mac16Address src, double rssi) {
                        this->OnPacketRx(nodeId, pkt, src, rssi);
                    });
            }
        }
    }
}

// ============================================================================
// PacketTracingHelper::InstallFullTracing()
// ============================================================================

void PacketTracingHelper::InstallFullTracing(ns3::NetDeviceContainer groundDevices,
                                            ns3::NetDeviceContainer uavDevices) {
    // Install RX tracing on ground nodes
    InstallRxTracing(groundDevices, 0);

    // Install RX tracing on UAV nodes (optional - usually UAVs don't listen)
    InstallRxTracing(uavDevices, groundDevices.GetN());
}

// ============================================================================
// Callback: Packet Transmitted
// ============================================================================

void PacketTracingHelper::OnPacketTx(uint32_t nodeId, Ptr<const Packet> pkt) {
    m_stats.totalTxPackets++;
    m_stats.txPerNode[nodeId]++;

    std::cout << "[" << std::fixed << std::setprecision(3)
              << Simulator::Now().GetSeconds() << "s] TX: Node " << nodeId
              << " sent " << pkt->GetSize() << " bytes\n";
}

// ============================================================================
// Callback: Packet Received (MAC layer)
// ============================================================================

void PacketTracingHelper::OnPacketRx(uint32_t nodeId, Ptr<Packet> pkt, Mac16Address src,
                                     double rssi) {
    m_stats.totalRxPackets++;
    m_stats.rxPerNode[nodeId]++;

    // Track RSSI for averaging
    if (m_stats.rssiCountPerNode[nodeId] == 0) {
        m_stats.avgRssiPerNode[nodeId] = rssi;
    } else {
        // Running average
        double oldAvg = m_stats.avgRssiPerNode[nodeId];
        uint32_t count = m_stats.rssiCountPerNode[nodeId];
        m_stats.avgRssiPerNode[nodeId] = (oldAvg * count + rssi) / (count + 1);
    }
    m_stats.rssiCountPerNode[nodeId]++;

    std::cout << "[" << std::fixed << std::setprecision(3) << Simulator::Now().GetSeconds()
              << "s] RX: Node " << nodeId << " received " << pkt->GetSize() << " bytes from "
              << src << " (RSSI=" << std::fixed << std::setprecision(2) << rssi << " dBm)\n";
}

// ============================================================================
// PacketTracingHelper::PrintResults()
// ============================================================================

void PacketTracingHelper::PrintResults(std::ostream& os) const {
    os << "\n========================================\n";
    os << "PACKET TRACING RESULTS\n";
    os << "========================================\n";
    os << "Total TX packets: " << m_stats.totalTxPackets << "\n";
    os << "Total RX packets: " << m_stats.totalRxPackets << "\n";

    if (!m_stats.txPerNode.empty()) {
        os << "\nTX per node:\n";
        for (const auto& p : m_stats.txPerNode) {
            os << "  Node " << p.first << ": " << p.second << " packets\n";
        }
    }

    if (!m_stats.rxPerNode.empty()) {
        os << "\nRX per node:\n";
        for (const auto& p : m_stats.rxPerNode) {
            os << "  Node " << p.first << ": " << p.second << " packets";
            if (m_stats.avgRssiPerNode.count(p.first)) {
                os << " (avg RSSI=" << std::fixed << std::setprecision(2)
                   << m_stats.avgRssiPerNode.at(p.first) << " dBm)";
            }
            os << "\n";
        }
    }

    // Analysis
    os << "\nAnalysis:\n";
    if (m_stats.totalTxPackets > 0 && m_stats.totalRxPackets > 0) {
        double deliveryRate =
            (100.0 * m_stats.totalRxPackets) / (m_stats.totalTxPackets * 2);  // 2 RX nodes
        os << "✓ Packet delivery: " << std::fixed << std::setprecision(1) << deliveryRate
           << "%\n";
    } else if (m_stats.totalTxPackets > 0 && m_stats.totalRxPackets == 0) {
        os << "✗ No packets received despite TX (channel isolation?)\n";
    } else if (m_stats.totalTxPackets == 0 && m_stats.totalRxPackets == 0) {
        os << "⚠ No packet activity recorded\n";
    }

    os << "========================================\n\n";
}

}  // namespace uav
}  // namespace wsn
}  // namespace ns3
