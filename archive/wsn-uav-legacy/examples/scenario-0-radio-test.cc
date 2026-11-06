/*
 * Scenario 0: Minimal Radio Communication Test
 *
 * Purpose: Verify CC2420 radio works correctly between UAV and ground nodes
 * Setup: 3 nodes (1 UAV, 2 ground), 100m range, basic packet exchange
 *
 * Expected Behavior:
 * - CORRECT (shared channel): UAV sends → both ground nodes receive
 * - BROKEN (isolated channels): UAV sends → ground nodes receive NOTHING
 *
 * Usage:
 *   ./ns3 run scenario-0-radio-test
 */

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"
#include "ns3/spectrum-module.h"
#include "ns3/cc2420-helper.h"

#include <iostream>
#include <iomanip>
#include <vector>

using namespace ns3;

NS_LOG_COMPONENT_DEFINE("Scenario0RadioTest");

static uint32_t g_packetsReceived = 0;
static uint32_t g_packetsSent = 0;

// ============================================================================
// Packet RX Callback
// ============================================================================

void OnPacketReceived(std::string nodeName, Ptr<const Packet> pkt) {
    g_packetsReceived++;
    std::cout << "  [" << std::fixed << std::setprecision(3) << Simulator::Now().GetSeconds()
              << "s] " << nodeName << " RX packet (size=" << pkt->GetSize() << " bytes)\n";
}

// ============================================================================
// UAV Transmit Function
// ============================================================================

void UavBroadcast(Ptr<NetDevice> uavDev, uint32_t count) {
    if (!uavDev) return;

    // Create and send a test packet
    Ptr<Packet> pkt = Create<Packet>(64);  // 64-byte test packet
    Mac16Address broadcast("ff:ff");

    bool success = uavDev->Send(pkt, broadcast, 0x00);

    std::cout << "  [" << std::fixed << std::setprecision(3) << Simulator::Now().GetSeconds()
              << "s] UAV TX packet #" << count;

    if (success) {
        std::cout << " [OK]\n";
        g_packetsSent++;
    } else {
        std::cout << " [FAILED]\n";
    }

    // Schedule next broadcast
    if (count < 5) {
        Simulator::Schedule(Seconds(1.0), &UavBroadcast, uavDev, count + 1);
    }
}

// ============================================================================
// Main
// ============================================================================

int main(int argc, char* argv[]) {
    LogComponentEnable("Scenario0RadioTest", LOG_LEVEL_INFO);

    // Create nodes: 2 ground + 1 UAV
    std::cout << "\n" << std::string(60, '=') << "\n";
    std::cout << "Scenario 0: Radio Communication Test (3 nodes)\n";
    std::cout << std::string(60, '=') << "\n\n";

    NodeContainer groundNodes;
    groundNodes.Create(2);

    NodeContainer uavNodes;
    uavNodes.Create(1);

    std::cout << "Node Setup:\n";
    std::cout << "  Ground Node 0 (ID=" << groundNodes.Get(0)->GetId() << ")\n";
    std::cout << "  Ground Node 1 (ID=" << groundNodes.Get(1)->GetId() << ")\n";
    std::cout << "  UAV Node 0    (ID=" << uavNodes.Get(0)->GetId() << ")\n\n";

    // ========================================================================
    // Mobility Setup
    // ========================================================================

    std::cout << "Mobility Setup:\n";
    MobilityHelper mobility;
    mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    mobility.Install(groundNodes);
    mobility.Install(uavNodes);

    // Position: UAV at (0,0,20), ground nodes at (10,0,0) and (50,0,0)
    groundNodes.Get(0)->GetObject<MobilityModel>()->SetPosition(Vector(10, 0, 0));
    groundNodes.Get(1)->GetObject<MobilityModel>()->SetPosition(Vector(50, 0, 0));
    uavNodes.Get(0)->GetObject<MobilityModel>()->SetPosition(Vector(0, 0, 20));

    std::cout << "  Ground 0: (10, 0, 0)\n";
    std::cout << "  Ground 1: (50, 0, 0)\n";
    std::cout << "  UAV 0:    (0, 0, 20)\n";
    std::cout << "  All within RF range\n\n";

    // ========================================================================
    // Radio Installation (SINGLE SHARED CHANNEL - CORRECT)
    // ========================================================================

    std::cout << "Radio Setup:\n";
    std::cout << "  Using SINGLE Cc2420Helper instance (shared channel)\n";

    ns3::wsn::Cc2420Helper cc2420;
    auto channel = cc2420.CreateChannel();

    cc2420.SetPhyAttribute("TxPower", DoubleValue(0.0));           // 0 dBm
    cc2420.SetPhyAttribute("RxSensitivity", DoubleValue(-95.0));   // -95 dBm

    // Install on ALL nodes using same helper + channel
    NetDeviceContainer groundDevices = cc2420.Install(groundNodes);
    NetDeviceContainer uavDevices = cc2420.Install(uavNodes);

    std::cout << "  Channel pointer: " << channel << "\n";
    std::cout << "  Ground devices installed: " << groundDevices.GetN() << "\n";
    std::cout << "  UAV devices installed: " << uavDevices.GetN() << "\n";
    std::cout << "  Status: ✓ SHARED channel for all nodes\n\n";

    // ========================================================================
    // RX Callback Setup for Ground Nodes
    // ========================================================================

    std::cout << "Enabling RX Callbacks:\n";
    for (uint32_t i = 0; i < groundDevices.GetN(); i++) {
        Ptr<NetDevice> dev = groundDevices.Get(i);
        std::ostringstream oss;
        oss << "Ground" << i;

        // Connect to RX callback (device-dependent, using lambda)
        dev->SetReceiveCallback(
            [i](Ptr<NetDevice> dev, Ptr<const Packet> pkt, uint16_t proto,
                const Address& from) {
                OnPacketReceived("Ground" + std::to_string(i), pkt);
                return true;
            }
        );
        std::cout << "  " << oss.str() << " RX callback enabled\n";
    }
    std::cout << "\n";

    // ========================================================================
    // Simulation Schedule
    // ========================================================================

    std::cout << "Simulation Schedule:\n";
    std::cout << "  t=2.0s  : Start UAV broadcasts\n";
    std::cout << "  t=2.0-7.0s : 5 packets sent (1s apart)\n";
    std::cout << "  t=10.0s : Stop simulation\n\n";

    Simulator::Schedule(Seconds(2.0), &UavBroadcast, uavDevices.Get(0), 1);

    // ========================================================================
    // Run Simulation
    // ========================================================================

    std::cout << std::string(60, '=') << "\n";
    std::cout << "PACKET FLOW TRACE\n";
    std::cout << std::string(60, '=') << "\n";

    Simulator::Stop(Seconds(10.0));
    Simulator::Run();
    Simulator::Destroy();

    // ========================================================================
    // Results
    // ========================================================================

    std::cout << "\n" << std::string(60, '=') << "\n";
    std::cout << "TEST RESULTS\n";
    std::cout << std::string(60, '=') << "\n";
    std::cout << "Packets sent (UAV):     " << g_packetsSent << "\n";
    std::cout << "Packets received (GND): " << g_packetsReceived << "\n";

    if (g_packetsSent > 0) {
        double deliveryRate = (double)g_packetsReceived / (g_packetsSent * 2) * 100.0;
        std::cout << "Delivery rate:          " << std::fixed << std::setprecision(1)
                  << deliveryRate << "%\n";
    }

    std::cout << "\n";

    if (g_packetsReceived > 0) {
        std::cout << "✓ PASS: Radio communication works (shared channel correct)\n";
        std::cout << "        Ground nodes received UAV broadcasts\n";
        return 0;
    } else {
        std::cout << "✗ FAIL: Radio communication broken (isolated channels)\n";
        std::cout << "        Ground nodes did NOT receive UAV broadcasts\n";
        std::cout << "        Likely cause: separate Cc2420Helper instances\n";
        return 1;
    }
}
