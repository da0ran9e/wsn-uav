#include "sar-config.h"
#include "../models/common/target-profile.h"
#include "../models/common/clue-field.h"
#include "../models/common/sar-params.h"

#include "ns3/core-module.h"
#include "ns3/mobility-module.h"

#include <random>
#include <vector>

using namespace ns3;

namespace ns3::uavsar {

void SarScenario::Run(const SarScenarioConfig& cfg) {
    RngSeedManager::SetSeed(1);
    RngSeedManager::SetRun(cfg.seed);

    // 1) network
    SarNetworkConfig net;
    net.gridSize = cfg.gridSize;
    net.gridSpacing = cfg.gridSpacing;
    net.numUav = cfg.numUav;
    m_lr = std::make_unique<LrWpanHelper>();
    SarNetwork network(net);
    SarNetworkSetup s = network.Build(*m_lr);

    // 2) substrate over the actual sensor node ids
    std::vector<NodePos> nodePos;
    std::vector<CluePos> cluePos;
    for (uint32_t i = 0; i < s.sensors.GetN(); i++) {
        uint32_t id = s.sensors.Get(i)->GetId();
        Vector p = s.sensorPositions[i];
        nodePos.push_back({id, p.x, p.y});
        cluePos.push_back({id, p.x, p.y});
    }
    CellGridConfig cg;
    cg.cellRadius = params::kHexCellRadiusM;
    cg.neighborRange = params::kNeighborRangeM;
    m_plan = BuildCellGrid(nodePos, cg);
    m_routing = BuildInterCellRouting(m_plan);

    // 3) victim node (deterministic from seed) + clue field
    std::mt19937 trng(cfg.seed);
    uint32_t tIdx = trng() % s.sensors.GetN();
    uint32_t targetId = s.sensors.Get(tIdx)->GetId();
    ClueFieldConfig cc;
    cc.targetNodeId = targetId;
    cc.seed = cfg.seed;
    auto field = BuildClueField(cluePos, cc);

    // 4) target profile
    TargetProfile tp = TargetProfile::Generate();
    std::vector<Fragment> cues = tp.OfLayer(Layer::L0_IDENTITY);
    for (auto& f : tp.OfLayer(Layer::L1_DESCRIPTOR)) cues.push_back(f);
    std::vector<Fragment> full = tp.All();

    m_metrics.SetMeta(cfg.seed, cfg.gridSize, cfg.numUav, cfg.scheme, targetId);

    // 5) region coordinator (control-plane, event-level)
    m_coord.Init(&m_plan, &m_routing, &m_metrics,
                 params::kAlertThreshold, params::kCoopThreshold,
                 [this](uint32_t leaderNode, uint16_t rid, double x, double y) {
                     auto it = m_groundById.find(leaderNode);
                     if (it != m_groundById.end()) it->second->StartSummon(rid, x, y);
                 });

    // 6) BS app
    Ptr<SarBsApp> bs = CreateObject<SarBsApp>();
    bs->SetNodeId(s.bsId);
    bs->SetMetrics(&m_metrics);
    s.bs.Get(0)->AddApplication(bs);
    bs->SetStartTime(Seconds(0));
    bs->SetStopTime(Seconds(cfg.simTime));
    s.bsDev.Get(0)->SetReceiveCallback(
        [bs](Ptr<NetDevice> d, Ptr<const Packet> p, uint16_t pr, const Address& f) {
            return bs->OnReceive(d, p, pr, f);
        });
    Vector bsPos = s.bs.Get(0)->GetObject<MobilityModel>()->GetPosition();
    Address bsAddr = s.bsDev.Get(0)->GetAddress();

    // loiter/staging point = area centre
    double cx = 0, cy = 0;
    for (auto& p : s.sensorPositions) { cx += p.x; cy += p.y; }
    cx /= s.sensorPositions.size(); cy /= s.sensorPositions.size();

    // 7) UAV apps
    uint32_t fastCount = std::max<uint32_t>(1, (uint32_t)(cfg.numUav * cfg.fastRatio));
    auto claim = std::make_shared<int32_t>(-1);
    for (uint32_t u = 0; u < cfg.numUav; u++) {
        bool isFast = (u < fastCount);
        if (isFast) {
            Ptr<SarFastUavApp> app = CreateObject<SarFastUavApp>();
            app->SetNodeId(s.uavs.Get(u)->GetId());
            app->SetDevice(s.uavDevs.Get(u));
            app->SetMetrics(&m_metrics);
            app->SetSensorPositions(s.sensorPositions);
            app->SetCues(cues);
            app->SetCruise(params::kCruiseAltitudeM, params::kFastSpeedMps);
            s.uavs.Get(u)->AddApplication(app);
            app->SetStartTime(Seconds(0));
            app->SetStopTime(Seconds(cfg.simTime));
            s.uavDevs.Get(u)->SetReceiveCallback(
                [app](Ptr<NetDevice> d, Ptr<const Packet> p, uint16_t pr, const Address& f) {
                    return app->OnReceive(d, p, pr, f);
                });
        } else {
            Ptr<SarDataUavApp> app = CreateObject<SarDataUavApp>();
            app->SetNodeId(s.uavs.Get(u)->GetId());
            app->SetDevice(s.uavDevs.Get(u));
            app->SetMetrics(&m_metrics);
            app->SetFullDataset(full);
            app->SetCruise(params::kCruiseAltitudeM, params::kDataSpeedMps);
            app->SetLoiter(Vector(cx, cy, params::kCruiseAltitudeM));
            app->SetClaimToken(claim);
            app->SetBs(bsPos, bsAddr);
            s.uavs.Get(u)->AddApplication(app);
            app->SetStartTime(Seconds(0));
            app->SetStopTime(Seconds(cfg.simTime));
            s.uavDevs.Get(u)->SetReceiveCallback(
                [app](Ptr<NetDevice> d, Ptr<const Packet> p, uint16_t pr, const Address& f) {
                    return app->OnReceive(d, p, pr, f);
                });
        }
    }

    // 8) ground apps
    for (uint32_t i = 0; i < s.sensors.GetN(); i++) {
        uint32_t id = s.sensors.Get(i)->GetId();
        Ptr<SarGroundApp> app = CreateObject<SarGroundApp>();
        app->SetNodeId(id);
        app->SetDevice(s.sensorDevs.Get(i));
        app->SetMetrics(&m_metrics);
        app->SetCoordinator(&m_coord);
        app->SetProfile(full);
        app->SetClueQuality(field.at(id).clueQuality);
        app->SetThresholds(params::kCoopThreshold, params::kConfirmThreshold);
        s.sensors.Get(i)->AddApplication(app);
        app->SetStartTime(Seconds(0));
        app->SetStopTime(Seconds(cfg.simTime));
        m_groundById[id] = app;
        s.sensorDevs.Get(i)->SetReceiveCallback(
            [app](Ptr<NetDevice> d, Ptr<const Packet> p, uint16_t pr, const Address& f) {
                return app->OnReceive(d, p, pr, f);
            });
    }

    // 9) run
    Simulator::Stop(Seconds(cfg.simTime));
    Simulator::Run();
    Simulator::Destroy();
    m_metrics.Finalize(cfg.outputDir);
}

}  // namespace ns3::uavsar
