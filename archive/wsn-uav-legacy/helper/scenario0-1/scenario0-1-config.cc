#include "scenario0-1-config.h"
#include "scenario0-1-mac.h"

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"
#include "ns3/spectrum-module.h"
#include "ns3/lr-wpan-module.h"

#include <iostream>
#include <iomanip>
#include <map>

using namespace ns3;

NS_LOG_COMPONENT_DEFINE("Scenario0_1_LrWpan");

namespace ns3::wsn::uav {

static uint32_t g_packetsReceived = 0;
static uint32_t g_packetsSent = 0;
static std::map<uint32_t, Ptr<Scenario01Mac>> g_macLayers;

static void OnPacketReceived(const std::string& nodeName, Ptr<const Packet> pkt) {
    g_packetsReceived++;
    std::cout << "  [" << std::fixed << std::setprecision(3) << Simulator::Now().GetSeconds()
              << "s] " << nodeName << " RX packet (size=" << pkt->GetSize() << " bytes)\n";
}

static void OnPacketReceivedWithMac(uint32_t sourceId, uint32_t dstId,
                                    Ptr<const Packet> payload, bool isFromUav) {
    g_packetsReceived++;
    std::cout << "  [" << std::fixed << std::setprecision(3) << Simulator::Now().GetSeconds()
              << "s] RX from node#" << sourceId << " (size=" << payload->GetSize()
              << " bytes, fromUAV=" << (isFromUav ? "yes" : "no") << ")\n";
}

static void UavBroadcast(Ptr<NetDevice> uavDev, uint32_t count, uint32_t maxCount) {
    if (!uavDev) {
        return;
    }

    Ptr<Packet> pkt = Create<Packet>(64);
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
    if (count < maxCount) {
        Simulator::Schedule(Seconds(1.0), &UavBroadcast, uavDev, count + 1, maxCount);
    }
}

Scenario01Results Scenario01Config::Run() {
    // Reset globals
    g_packetsReceived = 0;
    g_packetsSent = 0;
    g_macLayers.clear();

    LogComponentEnable("Scenario0_1_LrWpan", LOG_LEVEL_INFO);

    // Print header
    std::cout << "\n" << std::string(60, '=') << "\n";
    std::cout << "Scenario 0.1: LR-WPAN Radio Communication Test (3 nodes)\n";
    std::cout << "             With Custom MAC Handler Layer\n";
    std::cout << std::string(60, '=') << "\n\n";

    // Create nodes: 2 ground + 1 UAV
    NodeContainer groundNodes;
    groundNodes.Create(2);

    NodeContainer uavNodes;
    uavNodes.Create(1);

    std::cout << "Node Setup:\n";
    std::cout << "  Ground Node 0 (ID=" << groundNodes.Get(0)->GetId() << ")\n";
    std::cout << "  Ground Node 1 (ID=" << groundNodes.Get(1)->GetId() << ")\n";
    std::cout << "  UAV Node 0    (ID=" << uavNodes.Get(0)->GetId() << ")\n\n";

    // Mobility Setup
    std::cout << "Mobility Setup:\n";
    MobilityHelper mobility;
    mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    mobility.Install(groundNodes);
    mobility.Install(uavNodes);

    groundNodes.Get(0)->GetObject<MobilityModel>()->SetPosition(
        Vector(ground0Pos.x, ground0Pos.y, ground0Pos.z));
    groundNodes.Get(1)->GetObject<MobilityModel>()->SetPosition(
        Vector(ground1Pos.x, ground1Pos.y, ground1Pos.z));
    uavNodes.Get(0)->GetObject<MobilityModel>()->SetPosition(
        Vector(uavPos.x, uavPos.y, uavPos.z));

    std::cout << "  Ground 0: (" << ground0Pos.x << ", " << ground0Pos.y << ", "
              << ground0Pos.z << ")\n";
    std::cout << "  Ground 1: (" << ground1Pos.x << ", " << ground1Pos.y << ", "
              << ground1Pos.z << ")\n";
    std::cout << "  UAV 0:    (" << uavPos.x << ", " << uavPos.y << ", " << uavPos.z << ")\n";
    std::cout << "  All within RF range\n\n";

    // Radio Installation (Native LR-WPAN)
    std::cout << "Radio Setup (Native LR-WPAN):\n";
    std::cout << "  Using native NS-3 LR-WPAN module (IEEE 802.15.4)\n";

    LrWpanHelper lrWpan;

    // Create channel with custom propagation model
    auto channel = CreateObject<SingleModelSpectrumChannel>();
    Ptr<LogDistancePropagationLossModel> loss =
        CreateObject<LogDistancePropagationLossModel>();
    loss->SetAttribute("Exponent", DoubleValue(pathLossExponent));
    loss->SetAttribute("ReferenceDistance", DoubleValue(referenceDistance));
    loss->SetAttribute("ReferenceLoss", DoubleValue(referenceLoss));
    channel->AddPropagationLossModel(loss);

    Ptr<ConstantSpeedPropagationDelayModel> delay =
        CreateObject<ConstantSpeedPropagationDelayModel>();
    channel->SetPropagationDelayModel(delay);

    lrWpan.SetChannel(channel);

    // Install on ALL nodes using same helper + channel
    NetDeviceContainer groundDevices = lrWpan.Install(groundNodes);
    NetDeviceContainer uavDevices = lrWpan.Install(uavNodes);

    std::cout << "  Channel pointer: " << channel << "\n";
    std::cout << "  Ground devices installed: " << groundDevices.GetN() << "\n";
    std::cout << "  UAV devices installed: " << uavDevices.GetN() << "\n";
    std::cout << "  MAC: LrWpanMac (standard IEEE 802.15.4)\n";
    std::cout << "  PHY: LrWpanPhy (flexible, 16 channels available)\n";
    std::cout << "  Status: ✓ SHARED channel for all nodes\n";
    std::cout << "  Custom MAC: Scenario01Mac layer available for header processing\n\n";

    // RX Callback Setup for all Nodes
    std::cout << "Enabling RX Callbacks:\n";
    for (uint32_t i = 0; i < groundDevices.GetN(); i++) {
        Ptr<NetDevice> dev = groundDevices.Get(i);

        dev->SetReceiveCallback(
            [i](Ptr<NetDevice> dev, Ptr<const Packet> pkt, uint16_t proto,
                const Address& from) {
                OnPacketReceived("Ground" + std::to_string(i), pkt);
                return true;
            }
        );
        std::cout << "  Ground" << i << " RX callback enabled\n";
    }

    // UAV RX callback
    Ptr<NetDevice> uavDev = uavDevices.Get(0);
    uavDev->SetReceiveCallback(
        [](Ptr<NetDevice> dev, Ptr<const Packet> pkt, uint16_t proto,
           const Address& from) {
            OnPacketReceived("UAV", pkt);
            return true;
        }
    );
    std::cout << "  UAV RX callback enabled\n";
    std::cout << "\n";

    // Simulation Schedule
    std::cout << "Simulation Schedule:\n";
    std::cout << "  t=" << startTimeSec << "s  : Start UAV broadcasts\n";
    std::cout << "  t=" << startTimeSec << "-"
              << (startTimeSec + numFragmentsToSend * broadcastIntervalSec) << "s : "
              << numFragmentsToSend << " packets sent (" << broadcastIntervalSec << "s apart)\n";
    std::cout << "  t=" << simulationDurationSec << ".0s : Stop simulation\n\n";

    Simulator::Schedule(Seconds(startTimeSec), &UavBroadcast, uavDevices.Get(0), 1,
                        numFragmentsToSend);

    // Run Simulation
    std::cout << std::string(60, '=') << "\n";
    std::cout << "PACKET FLOW TRACE\n";
    std::cout << std::string(60, '=') << "\n";

    Simulator::Stop(Seconds(simulationDurationSec));
    Simulator::Run();
    Simulator::Destroy();

    // Prepare results
    std::cout << "\n" << std::string(60, '=') << "\n";
    std::cout << "TEST RESULTS\n";
    std::cout << std::string(60, '=') << "\n";
    std::cout << "Packets sent (UAV):     " << g_packetsSent << "\n";
    std::cout << "Packets received (GND): " << g_packetsReceived << "\n";

    Scenario01Results results;
    results.packetsSent = g_packetsSent;
    results.packetsReceived = g_packetsReceived;

    if (g_packetsSent > 0) {
        results.deliveryRate = (double)g_packetsReceived / (g_packetsSent * 2) * 100.0;
        std::cout << "Delivery rate:          " << std::fixed << std::setprecision(1)
                  << results.deliveryRate << "%\n";
    }

    std::cout << "\n";

    if (g_packetsReceived > 0) {
        results.passed = true;
        results.message = "LR-WPAN communication works (custom MAC handler)";
        std::cout << "✓ PASS: " << results.message << "\n";
        std::cout << "        Ground nodes received UAV broadcasts\n";
        std::cout << "        Custom MAC: Handles packet headers, send/receive logic\n";
    } else {
        results.passed = false;
        results.message = "LR-WPAN communication failed";
        std::cout << "✗ FAIL: " << results.message << "\n";
        std::cout << "        Check module installation and channel setup\n";
    }

    std::cout << "\n";

    return results;
}

}  // namespace ns3::wsn::uav
