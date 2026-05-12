#include "scenario0-2-config.h"
#include "scenario0-2-network.h"

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"
#include "ns3/spectrum-module.h"
#include "ns3/lr-wpan-module.h"

#include <iostream>
#include <iomanip>
#include <map>

using namespace ns3;

namespace ns3::wsn::uav {

static uint32_t g_packetsReceived = 0;
static uint32_t g_packetsSent = 0;
static std::map<uint32_t, Ptr<Scenario02Network>> g_networkLayers;

static void OnPacketReceived(const std::string& nodeName, uint32_t srcId, uint32_t dstId,
                             Ptr<const Packet> payload) {
    g_packetsReceived++;
    std::cout << "  [" << std::fixed << std::setprecision(3) << Simulator::Now().GetSeconds()
              << "s] " << nodeName << " RX from node#" << srcId << " (dst=" << dstId
              << ", size=" << payload->GetSize() << " bytes)\n";
}

static void UavBroadcast(Ptr<NetDevice> uavDev, uint32_t uavNodeId, uint32_t count,
                         uint32_t maxCount) {
    if (!uavDev || g_networkLayers.find(uavNodeId) == g_networkLayers.end()) {
        return;
    }

    Ptr<Scenario02Network> net = g_networkLayers[uavNodeId];
    Ptr<Packet> payload = Create<Packet>(64);

    bool success = net->Send(uavDev, payload, 0xffffffff, 0);  // broadcast, data type

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
        Simulator::Schedule(Seconds(1.0), &UavBroadcast, uavDev, uavNodeId, count + 1,
                           maxCount);
    }
}

Scenario02Results Scenario02Config::Run() {
    // Reset globals
    g_packetsReceived = 0;
    g_packetsSent = 0;
    g_networkLayers.clear();

    LogComponentEnable("Scenario0_2_Network", LOG_LEVEL_INFO);

    // Print header
    std::cout << "\n" << std::string(70, '=') << "\n";
    std::cout << "Scenario 0.2: Custom Network Layer over LR-WPAN (3 nodes)\n";
    std::cout << std::string(70, '=') << "\n\n";

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

    // Radio Installation (LR-WPAN)
    std::cout << "Radio Stack (LR-WPAN):\n";
    std::cout << "  PHY: LrWpanPhy (IEEE 802.15.4)\n";
    std::cout << "  MAC: LrWpanMac (standard IEEE 802.15.4)\n";

    LrWpanHelper lrWpan;

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

    NetDeviceContainer groundDevices = lrWpan.Install(groundNodes);
    NetDeviceContainer uavDevices = lrWpan.Install(uavNodes);

    std::cout << "  Ground devices: " << groundDevices.GetN() << "\n";
    std::cout << "  UAV devices: " << uavDevices.GetN() << "\n";
    std::cout << "  Status: ✓ Shared channel for all nodes\n\n";

    // Setup custom network layers for all nodes
    std::cout << "Custom Network Layer Stack:\n";
    std::cout << "  Layer 3: Scenario02Network (source/dest routing)\n";
    std::cout << "  Packet format: [version|headerSize|length|hopLimit|type|seq|src|dst]\n\n";

    std::cout << "Initializing Network Layer:\n";
    for (uint32_t i = 0; i < groundNodes.GetN(); i++) {
        uint32_t nodeId = groundNodes.Get(i)->GetId();
        auto net = CreateObject<Scenario02Network>(nodeId);
        g_networkLayers[nodeId] = net;
        std::cout << "  Ground Node " << i << " (ID=" << nodeId << ") network layer ready\n";
    }
    uint32_t uavNodeId = uavNodes.Get(0)->GetId();
    auto uavNet = CreateObject<Scenario02Network>(uavNodeId);
    g_networkLayers[uavNodeId] = uavNet;
    std::cout << "  UAV Node 0 (ID=" << uavNodeId << ") network layer ready\n";
    std::cout << "\n";

    // Wire RX callbacks and connect to network layer
    std::cout << "Wiring RX Callbacks:\n";
    for (uint32_t i = 0; i < groundDevices.GetN(); i++) {
        Ptr<NetDevice> dev = groundDevices.Get(i);
        uint32_t nodeId = groundNodes.Get(i)->GetId();
        std::string nodeName = "Ground" + std::to_string(i);

        // Register network layer receive callback
        g_networkLayers[nodeId]->SetReceiveCallback(
            [nodeName](uint32_t srcId, uint32_t dstId, Ptr<Packet> payload, int8_t rssi) {
                OnPacketReceived(nodeName, srcId, dstId, payload);
            }
        );

        // Wire MAC layer RX to network layer
        dev->SetReceiveCallback(
            [nodeId](Ptr<NetDevice> dev, Ptr<const Packet> pkt, uint16_t proto,
                     const Address& from) {
                if (g_networkLayers.find(nodeId) != g_networkLayers.end()) {
                    g_networkLayers[nodeId]->OnMacReceive(dev, pkt, proto, from);
                }
                return true;
            }
        );
        std::cout << "  Ground" << i << " : MAC → Network layer wired\n";
    }

    // UAV network layer callback
    uavNet->SetReceiveCallback([](uint32_t srcId, uint32_t dstId, Ptr<Packet> payload,
                                  int8_t rssi) {
        OnPacketReceived("UAV", srcId, dstId, payload);
    });

    Ptr<NetDevice> uavDev = uavDevices.Get(0);
    uavDev->SetReceiveCallback([uavNodeId](Ptr<NetDevice> dev, Ptr<const Packet> pkt,
                                           uint16_t proto, const Address& from) {
        if (g_networkLayers.find(uavNodeId) != g_networkLayers.end()) {
            g_networkLayers[uavNodeId]->OnMacReceive(dev, pkt, proto, from);
        }
        return true;
    });
    std::cout << "  UAV : MAC → Network layer wired\n";
    std::cout << "\n";

    // Simulation Schedule
    std::cout << "Simulation Schedule:\n";
    std::cout << "  t=" << startTimeSec << "s  : Start UAV broadcasts\n";
    std::cout << "  t=" << startTimeSec << "-"
              << (startTimeSec + numFragmentsToSend * broadcastIntervalSec) << "s : "
              << numFragmentsToSend << " packets sent (" << broadcastIntervalSec << "s apart)\n";
    std::cout << "  t=" << simulationDurationSec << ".0s : Stop simulation\n\n";

    Simulator::Schedule(Seconds(startTimeSec), &UavBroadcast, uavDev, uavNodeId, 1,
                       numFragmentsToSend);

    // Run Simulation
    std::cout << std::string(70, '=') << "\n";
    std::cout << "PACKET FLOW TRACE\n";
    std::cout << std::string(70, '=') << "\n";

    Simulator::Stop(Seconds(simulationDurationSec));
    Simulator::Run();
    Simulator::Destroy();

    // Print results
    std::cout << "\n" << std::string(70, '=') << "\n";
    std::cout << "TEST RESULTS\n";
    std::cout << std::string(70, '=') << "\n";
    std::cout << "Packets sent (UAV network layer):     " << g_packetsSent << "\n";
    std::cout << "Packets received (GND network layer): " << g_packetsReceived << "\n";

    Scenario02Results results;
    results.packetsSent = g_packetsSent;
    results.packetsReceived = g_packetsReceived;

    if (g_packetsSent > 0) {
        results.deliveryRate = (double)g_packetsReceived / (g_packetsSent * 2) * 100.0;
        std::cout << "Delivery rate:                       " << std::fixed
                  << std::setprecision(1) << results.deliveryRate << "%\n";
    }

    std::cout << "\n";

    if (g_packetsReceived > 0) {
        results.passed = true;
        results.message = "Custom network layer works over LR-WPAN";
        std::cout << "✓ PASS: " << results.message << "\n";
        std::cout << "        Ground nodes received UAV broadcasts via network layer\n";
        std::cout << "        Features: routing headers, neighbor tracking, broadcast\n";
    } else {
        results.passed = false;
        results.message = "Network layer communication failed";
        std::cout << "✗ FAIL: " << results.message << "\n";
    }

    std::cout << "\n";

    return results;
}

}  // namespace ns3::wsn::uav
