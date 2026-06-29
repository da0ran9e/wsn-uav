#include "sar-config.h"
#include "../../models/common/log.h"
#include "../../models/common/sar-fragment.h"

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"

#include <algorithm>
#include <random>

using namespace ns3;

namespace ns3::wsn::uav {

using sar::Scheme;
using sar::UavRole;
using sar::FragClass;
using sar::Fragment;

void SarConfig::Build() {
    LogReset(scenarioName);
    SeedManager::SetSeed(1);
    SeedManager::SetRun(seed);

    LogM("SarConfig") << "SAR scenario: grid=" << gridSize << "x" << gridSize
                      << " UAVs=" << numUav << " frags=" << numFrag
                      << " scheme=" << (int)scheme << " seed=" << seed << "\n";

    // SINGLE forces one UAV.
    if (scheme == Scheme::SINGLE) numUav = 1;

    SarNetworkConfig netCfg;
    netCfg.gridSize = gridSize;
    netCfg.gridSpacing = gridSpacing;
    netCfg.numUav = numUav;
    netCfg.uavStartPos.z = cruiseAlt;

    m_lrWpan = std::make_unique<LrWpanHelper>();
    SarNetwork network(netCfg);
    m_setup = network.Build(*m_lrWpan);

    // Sensor positions (for UAV GMC briefing) + pick the victim's target node.
    std::vector<Vector> sensorPos;
    sensorPos.reserve(m_setup.sensorNodes.GetN());
    for (uint32_t i = 0; i < m_setup.sensorNodes.GetN(); i++) {
        sensorPos.push_back(
            m_setup.sensorNodes.Get(i)->GetObject<MobilityModel>()->GetPosition());
    }
    // Pick the victim's cell deterministically from the seed so the SAME target
    // position is used across schemes (fair comparison), independent of how many
    // ns-3 RNG substreams each scheme's node/device creation consumed.
    std::mt19937 trng(seed);
    uint32_t targetIdx = trng() % m_setup.sensorNodes.GetN();
    m_targetNodeId = m_setup.sensorNodes.Get(targetIdx)->GetId();

    // Fragment set + role/fragment assignment.
    std::vector<Fragment> frags = sar::FragmentSet::Generate(numFrag, 100, maxFragBytes);
    std::vector<Fragment> recog, data;
    for (const auto& f : frags)
        (f.cls == FragClass::RECOGNITION ? recog : data).push_back(f);

    // Decide roles per UAV.
    uint32_t fastCount;
    if (scheme == Scheme::PROPOSED && numUav >= 2)
        fastCount = std::max<uint32_t>(1, numUav / 2);
    else
        fastCount = numUav;  // SINGLE / NOCOOP: all sweep-broadcast everything
    uint32_t dataCount = numUav - fastCount;

    m_metrics.SetMeta(seed, gridSize, numUav, numFrag,
                      scheme == Scheme::PROPOSED ? "proposed"
                          : scheme == Scheme::SINGLE ? "single" : "nocoop",
                      m_targetNodeId);

    LogM("SarConfig") << "roles: FAST=" << fastCount << " DATA=" << dataCount
                      << " | frags recog=" << recog.size() << " data=" << data.size()
                      << " | target node=" << m_targetNodeId << "\n";

    // Fleet-shared rescue claim token so exactly one DATA UAV responds.
    auto claimToken = std::make_shared<int32_t>(-1);

    // Install UAV apps.
    for (uint32_t u = 0; u < numUav; u++) {
        auto app = CreateObject<SarUavApp>();
        uint32_t nodeId = m_setup.uavNodes.Get(u)->GetId();
        app->SetNodeId(nodeId);
        app->SetNetDevice(m_setup.uavDevices.Get(u));
        app->SetScheme(scheme);
        app->SetMetrics(&m_metrics);
        app->SetSensorPositions(sensorPos);
        app->SetClaimToken(claimToken);

        bool isFast = (u < fastCount);
        app->SetRole(isFast ? UavRole::FAST : UavRole::DATA);
        app->SetCruise(cruiseAlt, isFast ? fastSpeed : dataSpeed);

        if (scheme == Scheme::PROPOSED && numUav >= 2) {
            if (isFast) {
                // FAST UAVs broadcast recognition fragments (round-robin split).
                std::vector<Fragment> mine;
                for (size_t i = u; i < recog.size(); i += fastCount) mine.push_back(recog[i]);
                if (mine.empty() && !recog.empty()) mine.push_back(recog[u % recog.size()]);
                app->SetCarriedFragments(mine);
            } else {
                // DATA UAVs hold data frags (suppressed) + full set for delivery.
                uint32_t d = u - fastCount;
                std::vector<Fragment> mine;
                for (size_t i = d; i < data.size(); i += std::max<uint32_t>(1, dataCount))
                    mine.push_back(data[i]);
                app->SetCarriedFragments(mine);
                app->SetFullDataset(frags);  // can deliver the complete dataset
            }
        } else {
            // SINGLE / NOCOOP: no smart summon, so every UAV dwell-and-dumps the
            // full dataset at each cell it visits.
            app->SetCarriedFragments(frags);
            app->SetFullDataset(frags);
        }

        m_setup.uavNodes.Get(u)->AddApplication(app);
        app->SetStartTime(Seconds(0.0));
        app->SetStopTime(Seconds(simTime));
        m_uavApps.push_back(app);

        m_setup.uavDevices.Get(u)->SetReceiveCallback(
            [app](Ptr<NetDevice> dev, Ptr<const Packet> pkt, uint16_t proto,
                  const Address& from) { return app->OnReceive(dev, pkt, proto, from); });
    }

    // Install ground apps.
    for (uint32_t i = 0; i < m_setup.sensorNodes.GetN(); i++) {
        auto app = CreateObject<SarGroundApp>();
        uint32_t nodeId = m_setup.sensorNodes.Get(i)->GetId();
        app->SetNodeId(nodeId);
        app->SetNetDevice(m_setup.sensorDevices.Get(i));
        app->SetIsTarget(nodeId == m_targetNodeId);
        app->SetExpectedFragments(numFrag);
        app->SetScheme(scheme);
        app->SetMetrics(&m_metrics);
        app->SetConfirmPolicy(confirmNeighbors, confirmTimeout, beaconQuota);
        m_setup.sensorNodes.Get(i)->AddApplication(app);
        app->SetStartTime(Seconds(0.0));
        app->SetStopTime(Seconds(simTime));
        m_groundApps.push_back(app);

        m_setup.sensorDevices.Get(i)->SetReceiveCallback(
            [app](Ptr<NetDevice> dev, Ptr<const Packet> pkt, uint16_t proto,
                  const Address& from) { return app->OnReceive(dev, pkt, proto, from); });
    }

    LogFlush();
}

void SarConfig::Schedule() {
    LogM("SarConfig") << "schedule: simTime=" << simTime << "s\n";
    LogFlush();
}

void SarConfig::Run() {
    Simulator::Stop(Seconds(simTime));
    Simulator::Run();
    Simulator::Destroy();

    m_metrics.Finalize(outputDir);
    double t = m_metrics.TimeToCompleteData();
    LogM("SarConfig") << "DONE. timeToCompleteData="
                      << (t < 0 ? -1.0 : t) << "s -> " << outputDir << "/metrics.csv\n";
    LogFlush();
}

}  // namespace ns3::wsn::uav
