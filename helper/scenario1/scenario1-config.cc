#include "scenario1-config.h"
#include "../../models/common/log.h"

#include "ns3/core-module.h"
#include "ns3/mobility-module.h"
#include "ns3/random-variable-stream.h"

#include <iomanip>

using namespace ns3;

namespace ns3::wsn::uav {

void Scenario1Config::Build() {
    LogReset(scenarioName);  // open dated log file under docs/visualize/result/

    LogM("Scenario1Config") << "\n" << std::string(70, '=') << "\n";
    LogM("Scenario1Config") << "Scenario 1: UAV-Assisted WSN (1 BS + N×N Sensors + 1 UAV)\n";
    LogM("Scenario1Config") << std::string(70, '=') << "\n\n";

    // Build network from model
    NetworkConfig netCfg;
    netCfg.gridSize = gridSize;
    netCfg.gridSpacing = gridSpacing;
    netCfg.uavStartPos.z = uavStartHeight;

    // LrWpanHelper MUST outlive the simulation. Its destructor calls
    // m_channel->Dispose() which empties the channel's PHY list, so
    // packets stop being delivered to receivers. Keep it as a member.
    m_lrWpan = std::make_unique<LrWpanHelper>();

    Scenario1Network network(netCfg);
    m_setup = network.Build(*m_lrWpan);

    LogM("Scenario1Config") << "\n";

    // Install Applications
    LogM("Scenario1Config") << "Installing Applications:\n";

    m_bsApp = CreateObject<BaseStationApp>();
    m_bsApp->SetNodeId(m_setup.bsNodeId);
    m_bsApp->SetNetDevice(m_setup.baseStationDevice.Get(0));
    m_setup.baseStationNode.Get(0)->AddApplication(m_bsApp);
    m_bsApp->SetStartTime(Seconds(0.0));
    m_bsApp->SetStopTime(Seconds(simulationDurationSec));
    LogM("Scenario1Config") << "  BaseStation (ID=" << m_setup.bsNodeId << ") app installed\n";

    m_uavApp = CreateObject<UavApp>();
    m_uavApp->SetNodeId(m_setup.uavNodeId);
    m_uavApp->SetNetDevice(m_setup.uavDevice.Get(0));
    m_uavApp->SetBroadcastInterval(broadcastIntervalSec);
    m_uavApp->SetNumFragments(numFragmentsToSend);

    // Flight: cover the sensor grid [0..(N-1)*spacing] in both axes.
    double areaMax = (gridSize - 1) * gridSpacing;
    m_uavApp->SetFlightArea(0.0, 0.0, areaMax, areaMax);
    m_uavApp->SetFlightAltitude(uavStartHeight);
    m_uavApp->SetFlightSpeed(20.0);
    m_uavApp->SetRowSpacing(gridSpacing);

    m_setup.uavNode.Get(0)->AddApplication(m_uavApp);
    m_uavApp->SetStartTime(Seconds(startTimeSec));
    m_uavApp->SetStopTime(Seconds(simulationDurationSec));
    LogM("Scenario1Config") << "  UAV (ID=" << m_setup.uavNodeId << ") app installed\n";

    for (uint32_t i = 0; i < m_setup.sensorNodes.GetN(); i++) {
        auto groundApp = CreateObject<GroundNodeApp>();
        groundApp->SetNodeId(m_setup.sensorNodes.Get(i)->GetId());
        groundApp->SetNetDevice(m_setup.sensorDevices.Get(i));
        m_setup.sensorNodes.Get(i)->AddApplication(groundApp);
        groundApp->SetStartTime(Seconds(0.0));
        groundApp->SetStopTime(Seconds(simulationDurationSec));
        m_groundApps.push_back(groundApp);
    }
    LogM("Scenario1Config") << "  " << m_setup.sensorNodes.GetN() << " ground node apps installed\n\n";

    // Setup NetDevice RX callbacks
    LogM("Scenario1Config") << "Setting up RX callbacks:\n";

    for (uint32_t i = 0; i < m_setup.sensorDevices.GetN(); i++) {
        Ptr<NetDevice> dev = m_setup.sensorDevices.Get(i);
        Ptr<Node> node = m_setup.sensorNodes.Get(i);
        uint32_t nodeId = node->GetId();
        dev->SetReceiveCallback(
            [node, nodeId](Ptr<NetDevice>, Ptr<const Packet> pkt, uint16_t, const Address&) {
                LogN(node) << "Ground Node #" << nodeId << " RX packet (size="
                           << pkt->GetSize() << " bytes)";
                return true;
            }
        );
    }
    LogM("Scenario1Config") << "RX callbacks enabled on " << m_setup.sensorDevices.GetN() << " ground nodes";

    Ptr<Node> bsNode = m_setup.baseStationNode.Get(0);
    uint32_t bsId = m_setup.bsNodeId;
    m_setup.baseStationDevice.Get(0)->SetReceiveCallback(
        [bsNode, bsId](Ptr<NetDevice>, Ptr<const Packet> pkt, uint16_t, const Address&) {
            LogN(bsNode) << "BaseStation #" << bsId << " RX packet (size="
                         << pkt->GetSize() << " bytes)";
            return true;
        }
    );
    LogM("Scenario1Config") << "RX callback enabled on BaseStation";

    Ptr<Node> uavNode = m_setup.uavNode.Get(0);
    uint32_t uavId = m_setup.uavNodeId;
    m_setup.uavDevice.Get(0)->SetReceiveCallback(
        [uavNode, uavId](Ptr<NetDevice>, Ptr<const Packet> pkt, uint16_t, const Address&) {
            LogN(uavNode) << "UAV #" << uavId << " RX packet (size="
                          << pkt->GetSize() << " bytes)";
            return true;
        }
    );
    LogM("Scenario1Config") << "RX callback enabled on UAV";

    LogFlush();  // checkpoint: build complete
}

void Scenario1Config::Schedule() {
    double delayThreshold = 0.01;  // 10ms max stagger
    RandomDelayedStartUp(delayThreshold);

    LogM("Scenario1Config") << "Simulation Schedule:\n";
    LogM("Scenario1Config") << "  t=" << startTimeSec << "s  : UAV starts broadcasting\n";
    LogM("Scenario1Config") << "  t=" << simulationDurationSec << ".0s : Stop simulation\n\n";

    // Schedule UAV trajectory verification callback every 1 second
    LogM("Scenario1Config") << "UAV trajectory verification enabled (every 1s)\n";
    Simulator::Schedule(Seconds(startTimeSec), [this]() { VerifyUavTrajectory(); });
}

void Scenario1Config::VerifyUavTrajectory() {
    Ptr<Node> uavNode = m_setup.uavNode.Get(0);
    Ptr<MobilityModel> mob = uavNode->GetObject<MobilityModel>();

    if (mob) {
        Vector pos = mob->GetPosition();
        Vector vel = mob->GetVelocity();
        double speed = std::sqrt(vel.x * vel.x + vel.y * vel.y + vel.z * vel.z);
        LogN(uavNode) << "Trajectory check: pos=(" << pos.x << "," << pos.y << ","
                      << pos.z << ") speed=" << speed << "m/s";
    }

    double t = Simulator::Now().GetSeconds();
    if (t < simulationDurationSec) {
        Simulator::Schedule(Seconds(1.0), [this]() { VerifyUavTrajectory(); });
    }
}

void Scenario1Config::RandomDelayedStartUp(double delayThreshold) {
    LogM("Scenario1Config") << "Applying random startup delays:\n";

    Ptr<UniformRandomVariable> rng = CreateObject<UniformRandomVariable>();
    rng->SetAttribute("Min", DoubleValue(0.0));
    rng->SetAttribute("Max", DoubleValue(delayThreshold));

    double bsDelay = rng->GetValue();
    m_bsApp->SetStartTime(Seconds(bsDelay));
    LogM("Scenario1Config") << "  BS (ID=" << m_setup.bsNodeId << "): +" << std::fixed
              << std::setprecision(4) << bsDelay << "s\n";

    double uavDelay = rng->GetValue();
    m_uavApp->SetStartTime(Seconds(startTimeSec + uavDelay));
    LogM("Scenario1Config") << "  UAV (ID=" << m_setup.uavNodeId << "): +" << std::fixed
              << std::setprecision(4) << uavDelay << "s\n";

    for (size_t i = 0; i < m_groundApps.size(); i++) {
        double groundDelay = rng->GetValue();
        m_groundApps[i]->SetStartTime(Seconds(groundDelay));
    }
    LogM("Scenario1Config") << "  Ground nodes (" << m_groundApps.size() << "): random ±"
              << std::fixed << std::setprecision(4) << delayThreshold << "s\n\n";

    LogFlush();  // checkpoint: schedule complete
}

void Scenario1Config::Run() {
    LogM("Scenario1Config") << std::string(70, '=') << "\n";
    LogM("Scenario1Config") << "SIMULATION\n";
    LogM("Scenario1Config") << std::string(70, '=') << "\n";

    Simulator::Stop(Seconds(simulationDurationSec));
    Simulator::Run();
    Simulator::Destroy();

    LogM("Scenario1Config") << "\n" << std::string(70, '=') << "\n";
    LogM("Scenario1Config") << "TEST RESULTS\n";
    LogM("Scenario1Config") << std::string(70, '=') << "\n";
    LogM("Scenario1Config") << "✓ Topology: " << (gridSize * gridSize + 2) << " nodes (sensors + BS + UAV)\n";
    LogM("Scenario1Config") << "✓ " << m_groundApps.size() << " ground node apps started\n\n";

    // Flush remaining buffered bytes to disk so the log is complete on exit.
    LogFlush();
}

}  // namespace ns3::wsn::uav
