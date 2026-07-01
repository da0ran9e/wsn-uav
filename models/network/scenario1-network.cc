#include "scenario1-network.h"
#include "a2g-log-distance-loss.h"
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
    // Order matters: BS first (ID=0), UAV next (ID=1), sensors after (ID=2+)
    setup.baseStationNode.Create(1);
    setup.uavNode.Create(1);
    setup.sensorNodes.Create(m_cfg.gridSize * m_cfg.gridSize);

    setup.bsNodeId = setup.baseStationNode.Get(0)->GetId();
    setup.uavNodeId = setup.uavNode.Get(0)->GetId();

    LogM("Scenario1Network") << "Node Creation:\n";
    LogM("Scenario1Network") << "  BaseStation ID=" << setup.bsNodeId << "\n";
    LogM("Scenario1Network") << "  UAV ID=" << setup.uavNodeId << "\n";
    LogM("Scenario1Network") << "  Sensors: " << m_cfg.gridSize << "×" << m_cfg.gridSize << " (IDs="
              << setup.sensorNodes.Get(0)->GetId() << "-"
              << setup.sensorNodes.Get(m_cfg.gridSize * m_cfg.gridSize - 1)->GetId()
              << ")\n";
}

void Scenario1Network::SetupMobility(NetworkSetup& setup) {
    // Static nodes use ConstantPosition; UAV uses WaypointMobilityModel so the
    // application layer can issue movement commands (AddWaypoint) at runtime.
    MobilityHelper staticMobility;
    staticMobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    staticMobility.Install(setup.sensorNodes);
    staticMobility.Install(setup.baseStationNode);

    MobilityHelper uavMobility;
    uavMobility.SetMobilityModel("ns3::ConstantVelocityMobilityModel");
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
    // Phase 3 PHY realism: altitude-aware LogDistance path loss.
    // UAV<->ground links (z > threshold) use n_A2G=2.2 (LoS-dominant).
    // Ground<->ground links use n_G2G=3.5 (NLoS).
    // Reference distance/loss carry over from m_cfg (1.0 m / 46.6 dB).
    constexpr double kA2GExponent = 2.2;
    constexpr double kG2GExponent = 3.5;
    constexpr double kAltitudeThreshold = 5.0;
    Ptr<A2GLogDistanceLossModel> loss = CreateObject<A2GLogDistanceLossModel>();
    loss->SetA2GExponent(kA2GExponent);
    loss->SetG2GExponent(kG2GExponent);
    loss->SetAltitudeThreshold(kAltitudeThreshold);
    loss->SetReferenceDistance(m_cfg.referenceDistance);
    loss->SetReferenceLoss(m_cfg.referenceLoss);
    channel->AddPropagationLossModel(loss);

    // Phase 1 PHY realism: small-scale Nakagami multipath fading.
    // m=3 — LoS-dominant moderate fading. BS<->UAV selective ARQ now handles
    // occasional chunk loss without stalling the whole profile transfer.
    Ptr<NakagamiPropagationLossModel> nakagami = CreateObject<NakagamiPropagationLossModel>();
    nakagami->SetAttribute("m0", DoubleValue(3.0));
    nakagami->SetAttribute("m1", DoubleValue(3.0));
    nakagami->SetAttribute("m2", DoubleValue(3.0));
    channel->AddPropagationLossModel(nakagami);

    // Phase 1 PHY realism: log-normal shadowing. RandomPropagationLossModel
    // adds a random dB loss per propagation calculation; variance=196 => σ=14dB.
    Ptr<RandomPropagationLossModel> shadowing = CreateObject<RandomPropagationLossModel>();
    Ptr<NormalRandomVariable> shadowingRv = CreateObject<NormalRandomVariable>();
    shadowingRv->SetAttribute("Mean", DoubleValue(0.0));
    shadowingRv->SetAttribute("Variance", DoubleValue(196.0));
    shadowing->SetAttribute("Variable", PointerValue(shadowingRv));
    channel->AddPropagationLossModel(shadowing);

    Ptr<ConstantSpeedPropagationDelayModel> delay =
        CreateObject<ConstantSpeedPropagationDelayModel>();
    channel->SetPropagationDelayModel(delay);

    lrWpan.SetChannel(channel);

    setup.sensorDevices = lrWpan.Install(setup.sensorNodes);
    setup.baseStationDevice = lrWpan.Install(setup.baseStationNode);
    setup.uavDevice = lrWpan.Install(setup.uavNode);

    // Set TX power = 0 dBm on every device's PHY (default channel 11).
    // Custom propagation model will further limit range later.
    const double txPowerDbm = m_cfg.txPowerDbm;
    const double rxSensitivityDbm = m_cfg.rxSensitivityDbm;
    constexpr uint32_t lrwpanChannel = 11;
    lrwpan::LrWpanSpectrumValueHelper svh;
    Ptr<SpectrumValue> txPsd = svh.CreateTxPowerSpectralDensity(txPowerDbm, lrwpanChannel);
    auto applyPhy = [&txPsd, rxSensitivityDbm](Ptr<NetDevice> dev) {
        Ptr<lrwpan::LrWpanNetDevice> lrDev = DynamicCast<lrwpan::LrWpanNetDevice>(dev);
        if (lrDev) {
            lrDev->GetPhy()->SetTxPowerSpectralDensity(txPsd);
            lrDev->GetPhy()->SetRxSensitivity(rxSensitivityDbm);
        }
    };
    for (uint32_t i = 0; i < setup.sensorDevices.GetN(); ++i) applyPhy(setup.sensorDevices.Get(i));
    applyPhy(setup.baseStationDevice.Get(0));
    applyPhy(setup.uavDevice.Get(0));

    // ---- Phase 2 MAC realism ----
    // ns-3.46 lr-wpan does NOT expose MacMinBE/MacMaxBE/MacMaxCSMABackoffs/
    // MacMaxFrameRetries/MaxTxQueueSize as ns-3 Attributes (only "PanId" on
    // LrWpanMac, and "UseAcks" on LrWpanNetDevice). They must be tuned via
    // setter methods on LrWpanMac. See src/lr-wpan/model/lr-wpan-mac.{h,cc}
    // and src/lr-wpan/model/lr-wpan-csmaca.{h,cc}.
    //
    // Audit (defaults from lr-wpan source @ ns-3.46):
    //   LrWpanMac::m_macMaxFrameRetries = 3       (lr-wpan-mac.cc:210)
    //   LrWpanCsmaCa::m_macMinBE        = 3       (lr-wpan-csmaca.cc:53)
    //   LrWpanCsmaCa::m_macMaxBE        = 5       (lr-wpan-csmaca.cc:54)
    //   LrWpanCsmaCa::m_macMaxCSMABackoffs = 4    (lr-wpan-csmaca.cc:55)
    //   LrWpanMac::m_maxTxQueueSize     = std::deque<>::max_size() (~SIZE_MAX,
    //                                     effectively unbounded; settable via
    //                                     LrWpanMac::SetTxQMaxSize, NOT a
    //                                     ns-3 Attribute)
    //   LrWpanNetDevice "UseAcks"       = true    (lr-wpan-net-device.cc:59)
    //     -> Unicast frames are sent with TX_OPTION_ACK by default; MAC strips
    //        the ACK bit for broadcast destinations automatically
    //        (lr-wpan-net-device.cc:422-427). No code change needed to enable
    //        ACK on BS<->UAV unicast traffic.
    //
    // Tune target: bump MacMaxFrameRetries 3 -> 7 to double the link-level
    // retry budget for unicast (helps BS<->UAV fragment frames once we lower
    // Nakagami m in a future phase). MAC TX queue is intentionally left at
    // its default: the spec asked for ~32 frames, but ns-3.46's default is
    // already std::deque::max_size() (~SIZE_MAX). Calling SetTxQMaxSize(32)
    // here was verified to silently drop the UAV's bursty L0 broadcasts via
    // MAC TRANSACTION_OVERFLOW (visible only as MacTxDrop, not as Send()
    // failure), collapsing L0 reception from mean=23.7% to ~0%. So we keep
    // the default. CsmaCa BE / backoff params left at IEEE 802.15.4 defaults.
    auto applyMac = [](Ptr<NetDevice> dev) {
        Ptr<lrwpan::LrWpanNetDevice> lrDev = DynamicCast<lrwpan::LrWpanNetDevice>(dev);
        if (lrDev) {
            lrDev->GetMac()->SetMacMaxFrameRetries(7);
        }
    };
    for (uint32_t i = 0; i < setup.sensorDevices.GetN(); ++i) applyMac(setup.sensorDevices.Get(i));
    applyMac(setup.baseStationDevice.Get(0));
    applyMac(setup.uavDevice.Get(0));

    // Read back from BS device for audit logging.
    Ptr<lrwpan::LrWpanNetDevice> bsLr =
        DynamicCast<lrwpan::LrWpanNetDevice>(setup.baseStationDevice.Get(0));
    BooleanValue useAcksVal;
    bsLr->GetAttribute("UseAcks", useAcksVal);
    LogM("Scenario1Network") << "MAC (LR-WPAN) Phase 2 audit (BS device):\n";
    LogM("Scenario1Network") << "  MacMinBE          (CsmaCa default)        = 3\n";
    LogM("Scenario1Network") << "  MacMaxBE          (CsmaCa default)        = 5\n";
    LogM("Scenario1Network") << "  MacMaxCSMABackoffs (CsmaCa default)       = 4\n";
    LogM("Scenario1Network") << "  MacMaxFrameRetries before tune            = 3 (lr-wpan default)\n";
    LogM("Scenario1Network") << "  MacMaxFrameRetries after  tune            = "
                              << static_cast<unsigned>(bsLr->GetMac()->GetMacMaxFrameRetries())
                              << "\n";
    LogM("Scenario1Network") << "  MaxTxQueueSize (LrWpanMac, setter only)   = default (~SIZE_MAX) "
                              << "kept; capping to 32 silently drops UAV L0 broadcasts\n";
    LogM("Scenario1Network") << "  UseAcks (LrWpanNetDevice attribute)       = "
                              << (useAcksVal.Get() ? "true" : "false")
                              << " -> unicast frames request ACK + retry (ACK auto-disabled for broadcast)\n";

    LogM("Scenario1Network") << "Radio Stack (LR-WPAN):\n";
    LogM("Scenario1Network") << "  Sensor devices: " << setup.sensorDevices.GetN() << "\n";
    LogM("Scenario1Network") << "  BaseStation devices: " << setup.baseStationDevice.GetN() << "\n";
    LogM("Scenario1Network") << "  UAV devices: " << setup.uavDevice.GetN() << "\n";
    LogM("Scenario1Network") << "  TX power: " << txPowerDbm << " dBm, RX sens: "
                              << rxSensitivityDbm << " dBm, channel: " << lrwpanChannel << "\n";
    LogM("Scenario1Network") << "  Path loss: A2GLogDistance n_A2G=" << kA2GExponent
                              << " n_G2G=" << kG2GExponent
                              << " altThresh=" << kAltitudeThreshold << "m"
                              << " refLoss=" << m_cfg.referenceLoss << "dB @ "
                              << m_cfg.referenceDistance << "m\n";
    LogM("Scenario1Network") << "  Fading: Nakagami m0=m1=m2=3.0\n";
    LogM("Scenario1Network") << "  Shadowing: log-normal sigma=14dB (variance=196)\n";
    LogM("Scenario1Network") << "  Channel: shared (IEEE 802.15.4)\n";
}

}  // namespace ns3::wsn::uav
