#include "scenario0-3-config.h"
#include "scenario0-3-energy.h"

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"
#include "ns3/spectrum-module.h"
#include "ns3/lr-wpan-module.h"
#include "ns3/energy-module.h"

#include <iostream>
#include <iomanip>
#include <map>

using namespace ns3;

namespace ns3::wsn::uav {

static uint32_t g_packetsReceived = 0;
static uint32_t g_packetsSent = 0;
static std::map<uint32_t, DeviceEnergyModel*> g_energyModels;
static std::map<uint32_t, SimpleBattery*> g_energySources;

static void OnPacketReceived(const std::string& nodeName, Ptr<const Packet> pkt) {
    g_packetsReceived++;
    std::cout << "  [" << std::fixed << std::setprecision(3) << Simulator::Now().GetSeconds()
              << "s] " << nodeName << " RX packet (size=" << pkt->GetSize() << " bytes)\n";

    // Transition to RX state if not already
    // (In real scenario, this would be automatic from PHY layer)
}

void UavBroadcast(Ptr<NetDevice> uavDev, uint32_t uavNodeId, uint32_t count,
                  uint32_t maxCount) {
    if (!uavDev || g_energyModels.find(uavNodeId) == g_energyModels.end()) {
        return;
    }

    auto energy = g_energyModels[uavNodeId];

    // Transition to TX
    energy->TransitionToTx();

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

    // Transition back to Idle after brief TX window
    Simulator::Schedule(Seconds(0.01), [energy]() { energy->TransitionToIdle(); });

    // Schedule next broadcast
    if (count < maxCount) {
        Simulator::Schedule(Seconds(1.0), &UavBroadcast, uavDev, uavNodeId, count + 1,
                           maxCount);
    }
}

void PrintEnergyReport(uint32_t nodeId, const std::string& nodeName,
                       SimpleBattery* energySource,
                       DeviceEnergyModel* energyModel) {
    if (!energySource || !energyModel) {
        return;
    }

    std::cout << "\n" << nodeName << " Energy Report:\n";
    std::cout << "  Battery remaining: " << std::fixed << std::setprecision(2)
              << energySource->GetRemainingEnergy() << " J ("
              << (energySource->GetEnergyFraction() * 100.0) << "%)\n";
    std::cout << "  Total consumed: " << energySource->GetTotalEnergyConsumed()
              << " J\n";

    // State-wise breakdown
    std::cout << "  Energy by state:\n";
    std::cout << "    TX:    " << energyModel->GetEnergyConsumedInState(EnergyState::TX)
              << " J (" << std::setprecision(1) << energyModel->GetTimeInState(EnergyState::TX)
              << " s)\n";
    std::cout << "    RX:    " << std::setprecision(2)
              << energyModel->GetEnergyConsumedInState(EnergyState::RX) << " J ("
              << std::setprecision(1) << energyModel->GetTimeInState(EnergyState::RX)
              << " s)\n";
    std::cout << "    IDLE:  " << std::setprecision(2)
              << energyModel->GetEnergyConsumedInState(EnergyState::IDLE) << " J ("
              << std::setprecision(1) << energyModel->GetTimeInState(EnergyState::IDLE)
              << " s)\n";
    std::cout << "    SLEEP: " << std::setprecision(2)
              << energyModel->GetEnergyConsumedInState(EnergyState::SLEEP) << " J ("
              << std::setprecision(1) << energyModel->GetTimeInState(EnergyState::SLEEP)
              << " s)\n";
}

Scenario03Results Scenario03Config::Run() {
    // Reset globals
    g_packetsReceived = 0;
    g_packetsSent = 0;
    g_energyModels.clear();
    g_energySources.clear();

    // Print header
    std::cout << "\n" << std::string(70, '=') << "\n";
    std::cout << "Scenario 0.3: Energy-Aware LR-WPAN Simulation (3 nodes)\n";
    std::cout << std::string(70, '=') << "\n\n";

    // Create nodes
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

    // Radio Installation
    std::cout << "Radio Stack (LR-WPAN):\n";
    LrWpanHelper lrWpan;

    auto channel = CreateObject<SingleModelSpectrumChannel>();
    Ptr<LogDistancePropagationLossModel> loss =
        CreateObject<LogDistancePropagationLossModel>();
    loss->SetAttribute("Exponent", ns3::DoubleValue(pathLossExponent));
    loss->SetAttribute("ReferenceDistance", ns3::DoubleValue(referenceDistance));
    loss->SetAttribute("ReferenceLoss", ns3::DoubleValue(referenceLoss));
    channel->AddPropagationLossModel(loss);

    Ptr<ConstantSpeedPropagationDelayModel> delay =
        CreateObject<ConstantSpeedPropagationDelayModel>();
    channel->SetPropagationDelayModel(delay);

    lrWpan.SetChannel(channel);

    NetDeviceContainer groundDevices = lrWpan.Install(groundNodes);
    NetDeviceContainer uavDevices = lrWpan.Install(uavNodes);

    std::cout << "  PHY: LrWpanPhy (IEEE 802.15.4)\n";
    std::cout << "  MAC: LrWpanMac (standard IEEE 802.15.4)\n";
    std::cout << "  Ground devices: " << groundDevices.GetN() << "\n";
    std::cout << "  UAV devices: " << uavDevices.GetN() << "\n";
    std::cout << "  Status: ✓ Shared channel\n\n";

    // Setup energy sources and models
    std::cout << "Energy Model Setup:\n";
    std::cout << "  Type: Custom SimpleEnergySource + DeviceEnergyModel\n";
    std::cout << "  Battery capacity: " << batteryCapacityJ << " J ("
              << (batteryCapacityJ / 3600.0) << " Wh)\n";
    std::cout << "  TX power: " << txPowerMw << " mW\n";
    std::cout << "  RX power: " << rxPowerMw << " mW\n";
    std::cout << "  Idle power: " << idlePowerMw << " mW\n";
    std::cout << "  Sleep power: " << sleepPowerMw << " mW\n\n";

    std::cout << "Installing Energy Models:\n";

    // Create energy sources for all nodes
    for (uint32_t i = 0; i < groundNodes.GetN(); i++) {
        uint32_t nodeId = groundNodes.Get(i)->GetId();
        auto energySource = new SimpleBattery();
        energySource->SetInitialEnergy(batteryCapacityJ);
        g_energySources[nodeId] = energySource;

        auto energyModel = new DeviceEnergyModel();
        energyModel->SetEnergySource(energySource);
        energyModel->SetTxPower(txPowerMw);
        energyModel->SetRxPower(rxPowerMw);
        energyModel->SetIdlePower(idlePowerMw);
        energyModel->SetSleepPower(sleepPowerMw);

        g_energyModels[nodeId] = energyModel;

        // Set initial state to IDLE
        energyModel->TransitionToIdle();

        std::cout << "  Ground Node " << i << " (ID=" << nodeId << ") energy ready\n";
    }

    uint32_t uavNodeId = uavNodes.Get(0)->GetId();
    auto uavEnergySource = new SimpleBattery();
    uavEnergySource->SetInitialEnergy(batteryCapacityJ);
    g_energySources[uavNodeId] = uavEnergySource;

    auto uavEnergyModel = new DeviceEnergyModel();
    uavEnergyModel->SetEnergySource(uavEnergySource);
    uavEnergyModel->SetTxPower(txPowerMw);
    uavEnergyModel->SetRxPower(rxPowerMw);
    uavEnergyModel->SetIdlePower(idlePowerMw);
    uavEnergyModel->SetSleepPower(sleepPowerMw);

    g_energyModels[uavNodeId] = uavEnergyModel;
    uavEnergyModel->TransitionToIdle();

    std::cout << "  UAV Node 0 (ID=" << uavNodeId << ") energy ready\n";
    std::cout << "\n";

    // RX Callbacks (simple, no network layer)
    std::cout << "Wiring RX Callbacks:\n";
    for (uint32_t i = 0; i < groundDevices.GetN(); i++) {
        Ptr<NetDevice> dev = groundDevices.Get(i);
        uint32_t nodeId = groundNodes.Get(i)->GetId();

        dev->SetReceiveCallback(
            [nodeId, i](Ptr<NetDevice> dev, Ptr<const Packet> pkt, uint16_t proto,
                       const Address& from) {
                OnPacketReceived("Ground" + std::to_string(i), pkt);

                // Transition RX state
                if (g_energyModels.find(nodeId) != g_energyModels.end()) {
                    g_energyModels[nodeId]->TransitionToRx();
                }

                return true;
            }
        );
        std::cout << "  Ground" << i << " RX enabled\n";
    }

    Ptr<NetDevice> uavDev = uavDevices.Get(0);
    uavDev->SetReceiveCallback([uavNodeId](Ptr<NetDevice> dev, Ptr<const Packet> pkt,
                                           uint16_t proto, const Address& from) {
        OnPacketReceived("UAV", pkt);

        if (g_energyModels.find(uavNodeId) != g_energyModels.end()) {
            g_energyModels[uavNodeId]->TransitionToRx();
        }

        return true;
    });
    std::cout << "  UAV RX enabled\n";
    std::cout << "\n";

    // Simulation schedule
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
    std::cout << "Packets sent: " << g_packetsSent << "\n";
    std::cout << "Packets received: " << g_packetsReceived << "\n";

    Scenario03Results results;
    results.packetsSent = g_packetsSent;
    results.packetsReceived = g_packetsReceived;

    if (g_packetsSent > 0) {
        results.deliveryRate = (double)g_packetsReceived / (g_packetsSent * 2) * 100.0;
        std::cout << "Delivery rate: " << std::fixed << std::setprecision(1)
                  << results.deliveryRate << "%\n";
    }

    std::cout << "\n";

    // Energy reports
    if (g_energySources.find(uavNodeId) != g_energySources.end()) {
        PrintEnergyReport(uavNodeId, "UAV", g_energySources[uavNodeId], g_energyModels[uavNodeId]);
    }

    for (uint32_t i = 0; i < groundNodes.GetN(); i++) {
        uint32_t nodeId = groundNodes.Get(i)->GetId();
        if (g_energySources.find(nodeId) != g_energySources.end()) {
            PrintEnergyReport(nodeId, "Ground" + std::to_string(i), g_energySources[nodeId],
                             g_energyModels[nodeId]);
        }
    }

    std::cout << "\n";

    if (g_packetsReceived > 0) {
        results.passed = true;
        results.message = "Energy-aware LR-WPAN simulation successful";
        std::cout << "✓ PASS: " << results.message << "\n";
        std::cout << "        Packets delivered, energy consumption tracked\n";
    } else {
        results.passed = false;
        results.message = "No packets received";
        std::cout << "✗ FAIL: " << results.message << "\n";
    }

    std::cout << "\n";

    return results;
}

}  // namespace ns3::wsn::uav
