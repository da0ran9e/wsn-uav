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
#include "../helper/packet-tracing-helper.h"

#include <iostream>
#include <iomanip>

using namespace ns3;

NS_LOG_COMPONENT_DEFINE("Scenario0Radio");

void SendPacketFromUav(Ptr<NetDevice> uavDev, ns3::wsn::uav::PacketTracingHelper* tracer) {
    if (!uavDev) return;

    Ptr<Packet> pkt = Create<Packet>(32);  // 32 bytes test packet
    // Use broadcast address appropriate for CC2420 (Mac16Address)
    bool sendOk = uavDev->Send(pkt, Mac16Address("ff:ff"), 0);

    if (sendOk && tracer) {
        tracer->ReportTx(2, pkt);  // Node 2 is UAV
    }

    // Schedule next packet
    Simulator::Schedule(Seconds(1.0), &SendPacketFromUav, uavDev, tracer);
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

    } else {
        std::cerr << "Error: testMode must be 'shared'\n";
        return 1;
    }

    // Setup packet tracing helper
    std::cout << "Setting up packet tracing...\n";
    ns3::wsn::uav::PacketTracingHelper tracer;
    tracer.InstallRxTracing(groundDevices, 0);
    std::cout << "  Ground nodes: RX tracing enabled\n";

    // Schedule UAV to send packets
    std::cout << "Scheduling UAV broadcasts starting at t=5s...\n\n";
    Simulator::Schedule(Seconds(5.0), &SendPacketFromUav, uavDevices.Get(0), &tracer);

    // Run simulation
    std::cout << "========================================\n";
    std::cout << "PACKET FLOW TRACE (5s - 10s)\n";
    std::cout << "========================================\n";
    Simulator::Stop(Seconds(10.0));
    Simulator::Run();
    Simulator::Destroy();

    // Print results using tracer
    tracer.PrintResults();

    return 0;
}
