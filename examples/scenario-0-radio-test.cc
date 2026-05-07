/*
 * Scenario 0: Radio Transmission Test - With Actual Packet Flow
 *
 * 3 nodes test: 1 UAV + 2 ground nodes
 * Goal: Verify actual packet transmission and reception via CC2420 radio
 *
 * Key Questions:
 * 1. Does UAV transmit packets successfully?
 * 2. Do ground nodes receive UAV packets?
 * 3. Are packets actually propagating through the shared/broken channel?
 *
 * Usage:
 *   ./ns3 run scenario-0-radio-test -- --testMode=shared
 *   ./ns3 run scenario-0-radio-test -- --testMode=broken
 */

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"
#include "ns3/spectrum-module.h"
#include "ns3/cc2420-helper.h"
#include "ns3/cc2420-net-device.h"
#include "ns3/cc2420-mac.h"

#include <iostream>
#include <iomanip>
#include <map>

using namespace ns3;

NS_LOG_COMPONENT_DEFINE("Scenario0Radio");

// Global packet tracking
struct PacketStats {
    uint32_t txCount = 0;
    uint32_t rxCount = 0;
    std::map<uint32_t, uint32_t> rxPerNode;  // node -> rx count
};

PacketStats g_stats;

// ============================================================================
// Callbacks
// ============================================================================

void OnPhyTxBegin(std::string context, Ptr<const Packet> pkt) {
    g_stats.txCount++;
    size_t pos = context.find("/NodeList/");
    size_t nodeIdStart = pos + 10;
    size_t nodeIdEnd = context.find("/", nodeIdStart);
    uint32_t nodeId = std::stoi(context.substr(nodeIdStart, nodeIdEnd - nodeIdStart));

    std::cout << "[" << std::fixed << std::setprecision(3)
              << Simulator::Now().GetSeconds() << "s] TX: Node " << nodeId
              << " sending " << pkt->GetSize() << " bytes\n";
}

void OnPhyRxBegin(std::string context, Ptr<const Packet> pkt) {
    g_stats.rxCount++;
    size_t pos = context.find("/NodeList/");
    size_t nodeIdStart = pos + 10;
    size_t nodeIdEnd = context.find("/", nodeIdStart);
    uint32_t nodeId = std::stoi(context.substr(nodeIdStart, nodeIdEnd - nodeIdStart));

    g_stats.rxPerNode[nodeId]++;

    std::cout << "[" << std::fixed << std::setprecision(3)
              << Simulator::Now().GetSeconds() << "s] RX: Node " << nodeId
              << " received " << pkt->GetSize() << " bytes\n";
}

void SendPacketFromUav(Ptr<NetDevice> uavDev) {
    if (!uavDev) return;

    g_stats.txCount++;

    Ptr<Packet> pkt = Create<Packet>(32);  // 32 bytes test packet
    // Use broadcast address appropriate for CC2420 (Mac16Address)
    bool sendOk = uavDev->Send(pkt, Mac16Address("ff:ff"), 0);

    std::cout << "[" << std::fixed << std::setprecision(3)
              << Simulator::Now().GetSeconds() << "s] TX: UAV sent broadcast packet (status="
              << (sendOk ? "OK" : "FAIL") << ")\n";

    // Schedule next packet
    Simulator::Schedule(Seconds(1.0), &SendPacketFromUav, uavDev);
}

// ============================================================================
// Main
// ============================================================================

int main(int argc, char* argv[]) {
    std::string testMode = "shared";

    CommandLine cmd(__FILE__);
    cmd.AddValue("testMode", "Test mode: 'shared' or 'broken'", testMode);
    cmd.Parse(argc, argv);

    std::cout << "\n========================================\n";
    std::cout << "Scenario 0: Radio Packet Flow Test\n";
    std::cout << "Test Mode: " << testMode << "\n";
    std::cout << "========================================\n\n";

    // Create nodes: 2 ground + 1 UAV
    NodeContainer groundNodes;
    groundNodes.Create(2);
    NodeContainer uavNodes;
    uavNodes.Create(1);

    std::cout << "Nodes:\n";
    std::cout << "  Ground 0: ID=" << groundNodes.Get(0)->GetId() << "\n";
    std::cout << "  Ground 1: ID=" << groundNodes.Get(1)->GetId() << "\n";
    std::cout << "  UAV 0:    ID=" << uavNodes.Get(0)->GetId() << "\n\n";

    // Install mobility
    MobilityHelper mobility;
    mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    mobility.Install(groundNodes);
    mobility.Install(uavNodes);

    groundNodes.Get(0)->GetObject<MobilityModel>()->SetPosition(Vector(0, 0, 0));
    groundNodes.Get(1)->GetObject<MobilityModel>()->SetPosition(Vector(100, 0, 0));
    uavNodes.Get(0)->GetObject<MobilityModel>()->SetPosition(Vector(50, 0, 20));

    std::cout << "Positions set (all within 100m RF range)\n\n";

    // Install radios
    NetDeviceContainer groundDevices, uavDevices;

    if (testMode == "shared") {
        std::cout << "Radio Setup: SHARED CHANNEL (correct)\n";
        std::cout << "  - Single Cc2420Helper instance\n";
        std::cout << "  - Both ground and UAV on same channel\n\n";

        ns3::wsn::Cc2420Helper cc2420;
        auto channel = cc2420.CreateChannel();
        cc2420.SetChannel(channel);
        cc2420.SetPhyAttribute("TxPower", DoubleValue(-10));
        cc2420.SetPhyAttribute("RxSensitivity", DoubleValue(-95));

        groundDevices = cc2420.Install(groundNodes);
        uavDevices = cc2420.Install(uavNodes);

        std::cout << "Channel ptr: " << channel << "\n";
        std::cout << "Ground devices: " << groundDevices.GetN() << "\n";
        std::cout << "UAV devices: " << uavDevices.GetN() << "\n";
        std::cout << "Status: ✓ SAME channel for all\n\n";

    } else if (testMode == "broken") {
        std::cout << "Radio Setup: BROKEN (separate channels for demo)\n";
        std::cout << "  - Ground: separate Cc2420Helper + channel\n";
        std::cout << "  - UAV: different Cc2420Helper + channel\n\n";

        ns3::wsn::Cc2420Helper cc2420_ground;
        auto channelA = cc2420_ground.CreateChannel();
        cc2420_ground.SetChannel(channelA);
        cc2420_ground.SetPhyAttribute("TxPower", DoubleValue(-10));
        cc2420_ground.SetPhyAttribute("RxSensitivity", DoubleValue(-95));
        groundDevices = cc2420_ground.Install(groundNodes);

        ns3::wsn::Cc2420Helper cc2420_uav;
        auto channelB = cc2420_uav.CreateChannel();
        cc2420_uav.SetChannel(channelB);
        cc2420_uav.SetPhyAttribute("TxPower", DoubleValue(-10));
        cc2420_uav.SetPhyAttribute("RxSensitivity", DoubleValue(-95));
        uavDevices = cc2420_uav.Install(uavNodes);

        std::cout << "Ground channel ptr: " << channelA << "\n";
        std::cout << "UAV channel ptr:    " << channelB << "\n";
        std::cout << "Status: ✗ DIFFERENT channels (isolation bug)\n\n";
    }

    // Setup MAC-layer packet sniffer for ground nodes
    std::cout << "Connecting MAC-layer packet sniffer...\n";

    for (uint32_t i = 0; i < groundDevices.GetN(); i++) {
        auto groundDev = DynamicCast<ns3::wsn::Cc2420NetDevice>(groundDevices.Get(i));
        if (groundDev) {
            auto groundMac = groundDev->GetMac();
            if (groundMac) {
                // Bind MAC callback to record received packets
                groundMac->SetMcpsDataIndicationCallback(
                    [i](Ptr<Packet> pkt, Mac16Address src, double rssi) {
                        g_stats.rxCount++;
                        g_stats.rxPerNode[i]++;
                        std::cout << "[" << std::fixed << std::setprecision(3)
                                  << Simulator::Now().GetSeconds() << "s] RX: Ground node " << i
                                  << " received " << pkt->GetSize() << " bytes from "
                                  << src << " (RSSI=" << rssi << " dBm)\n";
                    });
                std::cout << "  Ground node " << i << ": MAC callback wired\n";
            }
        }
    }

    // Schedule UAV to send packets
    std::cout << "Scheduling UAV broadcasts starting at t=5s...\n\n";
    Simulator::Schedule(Seconds(5.0), &SendPacketFromUav, uavDevices.Get(0));

    // Run simulation
    std::cout << "========================================\n";
    std::cout << "PACKET FLOW TRACE (5s - 10s)\n";
    std::cout << "========================================\n";
    Simulator::Stop(Seconds(10.0));
    Simulator::Run();
    Simulator::Destroy();

    // Results
    std::cout << "\n========================================\n";
    std::cout << "RESULTS\n";
    std::cout << "========================================\n";
    std::cout << "Total TX packets: " << g_stats.txCount << "\n";
    std::cout << "Total RX packets: " << g_stats.rxCount << "\n";

    if (!g_stats.rxPerNode.empty()) {
        std::cout << "RX per node:\n";
        for (auto& p : g_stats.rxPerNode) {
            std::cout << "  Node " << p.first << ": " << p.second << " packets\n";
        }
    }

    std::cout << "\nAnalysis:\n";
    if (testMode == "shared") {
        if (g_stats.rxCount > 0) {
            std::cout << "✓ PASS: Ground nodes received UAV packets\n";
            std::cout << "  Shared channel is working correctly!\n";
        } else {
            std::cout << "✗ FAIL: No packets received despite shared channel\n";
            std::cout << "  Issue may be in application layer or packet format\n";
        }
    } else {
        if (g_stats.rxCount == 0) {
            std::cout << "✓ VERIFIED: No cross-channel communication (as expected)\n";
            std::cout << "  Broken channel isolation confirmed\n";
        } else {
            std::cout << "✗ UNEXPECTED: Received packets on separate channels\n";
        }
    }

    std::cout << "\n========================================\n\n";

    return 0;
}
