#include "sar-config.h"
#include "../models/common/target-profile.h"
#include "../models/common/clue-field.h"
#include "../models/common/sar-params.h"

#include "ns3/core-module.h"
#include "ns3/mobility-module.h"

#include <algorithm>
#include <random>
#include <vector>

using namespace ns3;

namespace ns3::uavsar {

void SarScenario::Run(const SarScenarioConfig& cfg) {
    RngSeedManager::SetSeed(1);
    RngSeedManager::SetRun(cfg.seed);

    const bool proposed = (cfg.scheme == "proposed");
    uint32_t numUav = cfg.numUav;
    if (cfg.scheme == "pure-uav") numUav = 1;   // single UAV, no WSN cooperation

    // 1) network
    SarNetworkConfig net;
    net.gridSize = cfg.gridSize;
    net.gridSpacing = cfg.gridSpacing;
    net.numUav = numUav;
    m_lr = std::make_unique<LrWpanHelper>();
    SarNetwork network(net);
    SarNetworkSetup s = network.Build(*m_lr);

    // Packet-level PHY error accounting on every device (instrumentation only).
    m_phyStats.Attach(s.sensorDevs, 'g');
    m_phyStats.Attach(s.bsDev, 'b');
    m_phyStats.Attach(s.uavDevs, 'u');
    m_phyStats.BuildAddressMap();

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
    // Ground link range derived from the G2G budget so the substrate never
    // assumes links the PHY cannot sustain (review finding F6). ~37 m here.
    cg.neighborRange = params::DeriveG2gRangeM();
    m_plan = BuildCellGrid(nodePos, cg);
    m_routing = BuildInterCellRouting(m_plan);

    // 3) victim node (deterministic from seed) + clue field
    std::mt19937 trng(cfg.seed);
    uint32_t tIdx = trng() % s.sensors.GetN();
    uint32_t targetId = s.sensors.Get(tIdx)->GetId();
    ClueFieldConfig cc;
    cc.targetNodeId = targetId;
    cc.seed = cfg.seed;
    cc.decay = cfg.clueDecayM;          // sensing range knob (localization-resolution study)
    auto field = BuildClueField(cluePos, cc);

    // 4) target profile
    TargetProfile tp = TargetProfile::Generate();
    std::vector<Fragment> cues = tp.OfLayer(Layer::L0_IDENTITY);
    for (auto& f : tp.OfLayer(Layer::L1_DESCRIPTOR)) cues.push_back(f);
    std::vector<Fragment> full = tp.All();

    m_metrics.SetMeta(cfg.seed, cfg.gridSize, numUav, cfg.scheme, targetId);

    // 5) Control plane is now FULLY DISTRIBUTED in the ground apps: each Cell
    // Leader aggregates its cell from RPTs, floods SHARE across boundaries, and
    // runs an evidence-weighted-backoff + SUMMON-suppression election on radio.
    // No central RegionCoordinator (removed the global-view / pointer bypass).

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

    // Partition the sensor set into k contiguous x-bands so sweeping UAVs
    // divide the area instead of flying identical GMC paths in convoy
    // (review finding F5). Band i of k gets a contiguous slice sorted by x.
    auto partition = [&](uint32_t i, uint32_t k) {
        std::vector<Vector> sorted = s.sensorPositions;
        std::sort(sorted.begin(), sorted.end(), [](const Vector& a, const Vector& b) {
            return a.x != b.x ? a.x < b.x : a.y < b.y;
        });
        size_t n = sorted.size();
        size_t lo = n * i / k, hi = n * (i + 1) / k;
        return std::vector<Vector>(sorted.begin() + lo, sorted.begin() + hi);
    };

    // 7) UAV apps
    uint32_t fastCount = proposed ? std::max<uint32_t>(1, (uint32_t)(numUav * cfg.fastRatio)) : 0;
    // UAV role coordination (who diverts, who couriers) is now a radio CLAIM with
    // suppression — no shared-memory tokens.
    for (uint32_t u = 0; u < numUav; u++) {
        if (!proposed) {
            // baseline: every UAV sweeps ITS band and dwell-dumps the dataset.
            Ptr<SarDataUavApp> app = CreateObject<SarDataUavApp>();
            app->SetNodeId(s.uavs.Get(u)->GetId());
            app->SetDevice(s.uavDevs.Get(u));
            app->SetMetrics(&m_metrics);
            app->SetFullDataset(full);
            app->SetMode(SarDataUavApp::Mode::SWEEP_DUMP);
            app->SetSensorPositions(partition(u, numUav));
            app->SetCruise(params::kCruiseAltitudeM, params::kDataSpeedMps);
            app->SetBs(bsPos, bsAddr);
            s.uavs.Get(u)->AddApplication(app);
            app->SetStartTime(Seconds(0));
            app->SetStopTime(Seconds(cfg.simTime));
            s.uavDevs.Get(u)->SetReceiveCallback(
                [app](Ptr<NetDevice> d, Ptr<const Packet> p, uint16_t pr, const Address& f) {
                    return app->OnReceive(d, p, pr, f);
                });
            continue;
        }
        bool isFast = (u < fastCount);
        if (isFast) {
            Ptr<SarFastUavApp> app = CreateObject<SarFastUavApp>();
            app->SetNodeId(s.uavs.Get(u)->GetId());
            app->SetDevice(s.uavDevs.Get(u));
            app->SetMetrics(&m_metrics);
            app->SetSensorPositions(partition(u, fastCount));
            app->SetCues(cues);
            app->SetCruise(params::kCruiseAltitudeM, params::kFastSpeedMps);
            app->SetBs(bsPos, bsAddr);
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
        app->SetCooperative(proposed);
        app->SetMinObserve(cfg.minObserveS);
        app->SetProfile(full);
        app->SetClueQuality(field.at(id).clueQuality);
        app->SetCoopThreshold(params::kCoopThreshold);
        // Intra-cell tree so clue reports (RPT) climb to the CL over real radio;
        // cell id + center so a CL can flood its SHARE across the boundary.
        app->SetTreeParent(m_plan.nodes.at(id).parentId);
        app->SetCellLeader(m_plan.nodes.at(id).isLeader);
        int32_t cid = m_plan.nodes.at(id).cellId;
        app->SetCellId(cid);
        app->SetCellCenter(m_plan.cells.at(cid).centerX, m_plan.cells.at(cid).centerY);
        app->SetIsTarget(id == targetId);
        app->SetStopOnComplete(!proposed);
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
    m_metrics.SetExtra(m_phyStats.Counters());
    m_metrics.Finalize(cfg.outputDir);
}

}  // namespace ns3::uavsar
