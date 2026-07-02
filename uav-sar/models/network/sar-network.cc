#include "sar-network.h"
#include "air-ground-loss.h"
#include "pair-shadowing-loss.h"
#include "../common/sar-params.h"

#include "ns3/core-module.h"
#include "ns3/mobility-module.h"
#include "ns3/single-model-spectrum-channel.h"
#include "ns3/propagation-loss-model.h"
#include "ns3/propagation-delay-model.h"
#include "ns3/lr-wpan-module.h"

namespace ns3::uavsar {

using namespace ns3;

Ptr<SpectrumChannel> BuildSarChannel() {
    Ptr<SingleModelSpectrumChannel> channel = CreateObject<SingleModelSpectrumChannel>();

    // 1) deterministic A2G/G2G large-scale path loss
    Ptr<AirGroundLossModel> pl = CreateObject<AirGroundLossModel>();
    channel->AddPropagationLossModel(pl);

    // 2) small-scale multipath fading (Nakagami-m)
    Ptr<NakagamiPropagationLossModel> nak = CreateObject<NakagamiPropagationLossModel>();
    nak->SetAttribute("m0", DoubleValue(params::kNakagamiM));
    nak->SetAttribute("m1", DoubleValue(params::kNakagamiM));
    nak->SetAttribute("m2", DoubleValue(params::kNakagamiM));
    channel->AddPropagationLossModel(nak);

    // 3) log-normal shadowing, spatially persistent: ONE draw per node pair for
    // the whole run (ns-3's RandomPropagationLossModel redraws per packet,
    // which acts like extra fast fading — see review finding F3).
    Ptr<PairShadowingLossModel> shad = CreateObject<PairShadowingLossModel>();
    channel->AddPropagationLossModel(shad);

    channel->SetPropagationDelayModel(CreateObject<ConstantSpeedPropagationDelayModel>());
    return channel;
}

SarNetworkSetup SarNetwork::Build(LrWpanHelper& lrWpan) {
    SarNetworkSetup s;

    // Fixed creation order: BS, UAVs, sensors.
    s.bs.Create(1);
    s.uavs.Create(m_cfg.numUav);
    s.sensors.Create(m_cfg.gridSize * m_cfg.gridSize);
    s.bsId = s.bs.Get(0)->GetId();
    s.firstUavId = s.uavs.Get(0)->GetId();
    s.firstSensorId = s.sensors.Get(0)->GetId();

    // Mobility: BS + sensors static; UAVs on ConstantVelocity (app drives them).
    MobilityHelper stat;
    stat.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    stat.Install(s.bs);
    stat.Install(s.sensors);
    MobilityHelper mob;
    mob.SetMobilityModel("ns3::ConstantVelocityMobilityModel");
    mob.Install(s.uavs);

    s.bs.Get(0)->GetObject<MobilityModel>()->SetPosition(m_cfg.bsPos);
    for (uint32_t i = 0; i < m_cfg.gridSize; i++)
        for (uint32_t j = 0; j < m_cfg.gridSize; j++) {
            uint32_t idx = i * m_cfg.gridSize + j;
            Vector p(j * m_cfg.gridSpacing, i * m_cfg.gridSpacing, 0.0);
            s.sensors.Get(idx)->GetObject<MobilityModel>()->SetPosition(p);
            s.sensorPositions.push_back(p);
        }
    for (uint32_t u = 0; u < m_cfg.numUav; u++)
        s.uavs.Get(u)->GetObject<MobilityModel>()->SetPosition(
            Vector(m_cfg.bsPos.x + u * 2.0, m_cfg.bsPos.y, m_cfg.uavStartAltitude));

    // Radio: single helper + single shared channel.
    lrWpan.SetChannel(BuildSarChannel());
    s.sensorDevs = lrWpan.Install(s.sensors);
    s.bsDev = lrWpan.Install(s.bs);
    s.uavDevs = lrWpan.Install(s.uavs);

    lrwpan::LrWpanSpectrumValueHelper svh;
    Ptr<SpectrumValue> txPsd =
        svh.CreateTxPowerSpectralDensity(params::kTxPowerDbm, params::kLrwpanChannel);
    auto applyPhy = [&txPsd](Ptr<NetDevice> dev) {
        Ptr<lrwpan::LrWpanNetDevice> d = DynamicCast<lrwpan::LrWpanNetDevice>(dev);
        if (d) {
            d->GetPhy()->SetTxPowerSpectralDensity(txPsd);
            d->GetPhy()->SetRxSensitivity(params::kRxSensitivityDbm);
        }
    };
    for (uint32_t i = 0; i < s.sensorDevs.GetN(); i++) applyPhy(s.sensorDevs.Get(i));
    applyPhy(s.bsDev.Get(0));
    for (uint32_t u = 0; u < s.uavDevs.GetN(); u++) applyPhy(s.uavDevs.Get(u));

    return s;
}

}  // namespace ns3::uavsar
