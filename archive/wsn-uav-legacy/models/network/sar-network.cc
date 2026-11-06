#include "sar-network.h"
#include "../common/log.h"

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"
#include "ns3/spectrum-module.h"
#include "ns3/lr-wpan-module.h"

using namespace ns3;

namespace ns3::wsn::uav {

SarNetwork::SarNetwork(const SarNetworkConfig& cfg) : m_cfg(cfg) {}

SarNetworkSetup SarNetwork::Build(LrWpanHelper& lrWpan) {
    SarNetworkSetup s;
    CreateNodes(s);
    SetupMobility(s);
    InstallRadio(s, lrWpan);
    return s;
}

void SarNetwork::CreateNodes(SarNetworkSetup& s) {
    // Fixed order: BS (ID=0), then M UAVs, then N×N sensors.
    s.baseStationNode.Create(1);
    s.uavNodes.Create(m_cfg.numUav);
    s.sensorNodes.Create(m_cfg.gridSize * m_cfg.gridSize);

    s.bsNodeId = s.baseStationNode.Get(0)->GetId();
    s.firstUavNodeId = s.uavNodes.Get(0)->GetId();
    s.firstSensorNodeId = s.sensorNodes.Get(0)->GetId();

    LogM("SarNetwork") << "Nodes: BS=" << s.bsNodeId
                       << " UAVs=" << s.firstUavNodeId << ".."
                       << s.uavNodes.Get(m_cfg.numUav - 1)->GetId()
                       << " Sensors=" << s.firstSensorNodeId << ".."
                       << s.sensorNodes.Get(m_cfg.gridSize * m_cfg.gridSize - 1)->GetId()
                       << " (grid " << m_cfg.gridSize << "x" << m_cfg.gridSize << ")\n";
}

void SarNetwork::SetupMobility(SarNetworkSetup& s) {
    MobilityHelper staticMob;
    staticMob.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    staticMob.Install(s.sensorNodes);
    staticMob.Install(s.baseStationNode);

    MobilityHelper uavMob;
    uavMob.SetMobilityModel("ns3::ConstantVelocityMobilityModel");
    uavMob.Install(s.uavNodes);

    s.baseStationNode.Get(0)->GetObject<MobilityModel>()->SetPosition(
        Vector(m_cfg.baseStationPos.x, m_cfg.baseStationPos.y, m_cfg.baseStationPos.z));

    for (uint32_t i = 0; i < m_cfg.gridSize; i++) {
        for (uint32_t j = 0; j < m_cfg.gridSize; j++) {
            uint32_t idx = i * m_cfg.gridSize + j;
            s.sensorNodes.Get(idx)->GetObject<MobilityModel>()->SetPosition(
                Vector(j * m_cfg.gridSpacing, i * m_cfg.gridSpacing, 0.0));
        }
    }

    // All UAVs start clustered near the BS edge (small fan-out to avoid exact
    // coincidence). They climb to cruise altitude from the app layer.
    for (uint32_t u = 0; u < m_cfg.numUav; u++) {
        s.uavNodes.Get(u)->GetObject<MobilityModel>()->SetPosition(
            Vector(m_cfg.uavStartPos.x + u * 2.0, m_cfg.uavStartPos.y,
                   m_cfg.uavStartPos.z));
    }

    LogM("SarNetwork") << "Mobility: BS@(" << m_cfg.baseStationPos.x << ","
                       << m_cfg.baseStationPos.y << ") grid span "
                       << m_cfg.gridSize * m_cfg.gridSpacing << "m, "
                       << m_cfg.numUav << " UAVs @start\n";
}

void SarNetwork::InstallRadio(SarNetworkSetup& s, LrWpanHelper& lrWpan) {
    auto channel = CreateObject<SingleModelSpectrumChannel>();
    Ptr<LogDistancePropagationLossModel> loss = CreateObject<LogDistancePropagationLossModel>();
    loss->SetAttribute("Exponent", DoubleValue(m_cfg.pathLossExponent));
    loss->SetAttribute("ReferenceDistance", DoubleValue(m_cfg.referenceDistance));
    loss->SetAttribute("ReferenceLoss", DoubleValue(m_cfg.referenceLoss));
    channel->AddPropagationLossModel(loss);
    channel->SetPropagationDelayModel(CreateObject<ConstantSpeedPropagationDelayModel>());

    lrWpan.SetChannel(channel);

    // Single helper, single channel: sensors + BS + all UAVs.
    s.sensorDevices = lrWpan.Install(s.sensorNodes);
    s.baseStationDevice = lrWpan.Install(s.baseStationNode);
    s.uavDevices = lrWpan.Install(s.uavNodes);

    constexpr uint32_t lrwpanChannel = 11;
    lrwpan::LrWpanSpectrumValueHelper svh;
    Ptr<SpectrumValue> txPsd = svh.CreateTxPowerSpectralDensity(m_cfg.txPowerDbm, lrwpanChannel);
    const double rxSens = m_cfg.rxSensitivityDbm;
    auto applyPhy = [&txPsd, rxSens](Ptr<NetDevice> dev) {
        Ptr<lrwpan::LrWpanNetDevice> lrDev = DynamicCast<lrwpan::LrWpanNetDevice>(dev);
        if (lrDev) {
            lrDev->GetPhy()->SetTxPowerSpectralDensity(txPsd);
            lrDev->GetPhy()->SetRxSensitivity(rxSens);
        }
    };
    for (uint32_t i = 0; i < s.sensorDevices.GetN(); ++i) applyPhy(s.sensorDevices.Get(i));
    applyPhy(s.baseStationDevice.Get(0));
    for (uint32_t u = 0; u < s.uavDevices.GetN(); ++u) applyPhy(s.uavDevices.Get(u));

    LogM("SarNetwork") << "Radio: " << s.sensorDevices.GetN() << " sensors, "
                       << s.uavDevices.GetN() << " UAVs, shared 802.15.4 ch"
                       << lrwpanChannel << ", TxP=" << m_cfg.txPowerDbm
                       << "dBm RxS=" << rxSens << "dBm, LogDistance n="
                       << m_cfg.pathLossExponent << "\n";
}

}  // namespace ns3::wsn::uav
