#include "scenario1-network.h"
#include "../common/log.h"

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"
#include "ns3/spectrum-module.h"
#include "ns3/lr-wpan-module.h"

#include <iomanip>

using namespace ns3;

namespace ns3::wsn::uav {

Scenario1Network::Scenario1Network(const NetworkConfig& cfg) : m_cfg(cfg) {}

NetworkSetup Scenario1Network::Build(LrWpanHelper& lrWpan) {
    NetworkSetup setup;

    CreateNodes(setup);
    SetupMobility(setup);
    InstallRadio(setup, lrWpan);

    return setup;
}

void Scenario1Network::CreateNodes(NetworkSetup& setup) {
    // Sensor nodes (N×N grid)
    setup.sensorNodes.Create(m_cfg.gridSize * m_cfg.gridSize);

    // BaseStation node
    setup.baseStationNode.Create(1);

    // UAV node
    setup.uavNode.Create(1);

    setup.bsNodeId = setup.baseStationNode.Get(0)->GetId();
    setup.uavNodeId = setup.uavNode.Get(0)->GetId();

    LogM("Scenario1Network") << "Node Creation:\n";
    LogM("Scenario1Network") << "  BaseStation ID=" << setup.bsNodeId << "\n";
    LogM("Scenario1Network") << "  Sensors: " << m_cfg.gridSize << "×" << m_cfg.gridSize << " (IDs="
              << setup.sensorNodes.Get(0)->GetId() << "-"
              << setup.sensorNodes.Get(m_cfg.gridSize * m_cfg.gridSize - 1)->GetId()
              << ")\n";
    LogM("Scenario1Network") << "  UAV ID=" << setup.uavNodeId << "\n";
}

void Scenario1Network::SetupMobility(NetworkSetup& setup) {
    // Static nodes use ConstantPosition; UAV uses WaypointMobilityModel so the
    // application layer can issue movement commands (AddWaypoint) at runtime.
    MobilityHelper staticMobility;
    staticMobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    staticMobility.Install(setup.sensorNodes);
    staticMobility.Install(setup.baseStationNode);

    MobilityHelper uavMobility;
    uavMobility.SetMobilityModel("ns3::WaypointMobilityModel");
    uavMobility.Install(setup.uavNode);

    // BaseStation position
    setup.baseStationNode.Get(0)->GetObject<MobilityModel>()->SetPosition(
        Vector(m_cfg.baseStationPos.x, m_cfg.baseStationPos.y, m_cfg.baseStationPos.z));

    // Sensor nodes in grid
    for (uint32_t i = 0; i < m_cfg.gridSize; i++) {
        for (uint32_t j = 0; j < m_cfg.gridSize; j++) {
            uint32_t idx = i * m_cfg.gridSize + j;
            double x = j * m_cfg.gridSpacing;
            double y = i * m_cfg.gridSpacing;
            double z = 0.0;
            setup.sensorNodes.Get(idx)->GetObject<MobilityModel>()->SetPosition(
                Vector(x, y, z));
        }
    }

    // UAV position
    setup.uavNode.Get(0)->GetObject<MobilityModel>()->SetPosition(
        Vector(m_cfg.uavStartPos.x, m_cfg.uavStartPos.y, m_cfg.uavStartPos.z));

    LogM("Scenario1Network") << "Mobility Setup:\n";
    LogM("Scenario1Network") << "  BaseStation: (" << m_cfg.baseStationPos.x << ", "
              << m_cfg.baseStationPos.y << ", " << m_cfg.baseStationPos.z << ")\n";
    LogM("Scenario1Network") << "  Sensors: grid [0," << m_cfg.gridSize * m_cfg.gridSpacing << "] × [0,"
              << m_cfg.gridSize * m_cfg.gridSpacing << "] spacing=" << m_cfg.gridSpacing
              << "m\n";
    LogM("Scenario1Network") << "  UAV: (" << m_cfg.uavStartPos.x << ", " << m_cfg.uavStartPos.y << ", "
              << m_cfg.uavStartPos.z << ")\n";
}

void Scenario1Network::InstallRadio(NetworkSetup& setup, LrWpanHelper& lrWpan) {
    auto channel = CreateObject<SingleModelSpectrumChannel>();
    Ptr<LogDistancePropagationLossModel> loss = CreateObject<LogDistancePropagationLossModel>();
    loss->SetAttribute("Exponent", DoubleValue(m_cfg.pathLossExponent));
    loss->SetAttribute("ReferenceDistance", DoubleValue(m_cfg.referenceDistance));
    loss->SetAttribute("ReferenceLoss", DoubleValue(m_cfg.referenceLoss));
    channel->AddPropagationLossModel(loss);

    Ptr<ConstantSpeedPropagationDelayModel> delay =
        CreateObject<ConstantSpeedPropagationDelayModel>();
    channel->SetPropagationDelayModel(delay);

    lrWpan.SetChannel(channel);

    setup.sensorDevices = lrWpan.Install(setup.sensorNodes);
    setup.baseStationDevice = lrWpan.Install(setup.baseStationNode);
    setup.uavDevice = lrWpan.Install(setup.uavNode);

    LogM("Scenario1Network") << "Radio Stack (LR-WPAN):\n";
    LogM("Scenario1Network") << "  Sensor devices: " << setup.sensorDevices.GetN() << "\n";
    LogM("Scenario1Network") << "  BaseStation devices: " << setup.baseStationDevice.GetN() << "\n";
    LogM("Scenario1Network") << "  UAV devices: " << setup.uavDevice.GetN() << "\n";
    LogM("Scenario1Network") << "  Channel: shared (IEEE 802.15.4)\n";
}

}  // namespace ns3::wsn::uav
