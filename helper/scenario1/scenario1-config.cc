#include "scenario1-config.h"
#include "../../models/common/cell-layer.h"
#include "../../models/common/log.h"

#include "ns3/core-module.h"
#include "ns3/random-variable-stream.h"
#include "ns3/lr-wpan-net-device.h"
#include "ns3/lr-wpan-phy.h"
#include "ns3/lr-wpan-mac.h"

#include <iomanip>
#include <limits>
#include <algorithm>
#include <cmath>
#include <map>
#include <string>

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
    m_bsApp->SetSensorNodes(m_setup.sensorNodes);
    m_bsApp->SetUavNode(m_setup.uavNode);
    m_setup.baseStationNode.Get(0)->AddApplication(m_bsApp);
    m_bsApp->SetStartTime(Seconds(0.0));
    m_bsApp->SetStopTime(Seconds(simulationDurationSec));
    LogM("Scenario1Config") << "  BaseStation (ID=" << m_setup.bsNodeId << ") app installed\n";

    m_uavApp = CreateObject<UavApp>();
    m_uavApp->SetNodeId(m_setup.uavNodeId);
    m_uavApp->SetNetDevice(m_setup.uavDevice.Get(0));
    m_uavApp->SetFlightPathModel(flightPathModel);
    m_uavApp->SetBroadcastModel(broadcastModel);
    m_uavApp->SetRandomWaypointBudget(randomWaypointBudget);
    std::vector<uint32_t> groundNodeIds;
    std::vector<Address> groundAddresses;
    groundNodeIds.reserve(m_setup.sensorNodes.GetN());
    groundAddresses.reserve(m_setup.sensorDevices.GetN());
    for (uint32_t i = 0; i < m_setup.sensorDevices.GetN(); ++i) {
        groundNodeIds.push_back(m_setup.sensorNodes.Get(i)->GetId());
        groundAddresses.push_back(m_setup.sensorDevices.Get(i)->GetAddress());
    }
    m_uavApp->SetGroundNodeDestinations(groundNodeIds, groundAddresses);

    // Flight area / altitude / speed are derived inside the UAV app from
    // the topology packet sent by the BS. The UAV decides when to take off.

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

    BuildAndInstallCellLayer();
    BuildAndInstallLocalClues();

    // Setup NetDevice RX callbacks
    LogM("Scenario1Config") << "Setting up RX callbacks:\n";

    for (uint32_t i = 0; i < m_setup.sensorDevices.GetN(); i++) {
        Ptr<NetDevice> dev = m_setup.sensorDevices.Get(i);
        Ptr<GroundNodeApp> app = m_groundApps[i];
        dev->SetReceiveCallback(
            [app](Ptr<NetDevice> d, Ptr<const Packet> pkt, uint16_t proto,
                  const Address& from) {
                return app->OnReceive(d, pkt, proto, from);
            }
        );
    }
    LogM("Scenario1Config") << "RX callbacks enabled on " << m_setup.sensorDevices.GetN() << " ground nodes";

    m_setup.baseStationDevice.Get(0)->SetReceiveCallback(
        [this](Ptr<NetDevice> dev, Ptr<const Packet> pkt, uint16_t proto, const Address& from) {
            return m_bsApp->OnMessageReceived(dev, pkt, proto, from);
        }
    );
    LogM("Scenario1Config") << "RX callback hooked to BaseStation application";

    m_setup.uavDevice.Get(0)->SetReceiveCallback(
        [this](Ptr<NetDevice> dev, Ptr<const Packet> pkt, uint16_t proto, const Address& from) {
            return m_uavApp->OnMessageReceived(dev, pkt, proto, from);
        }
    );
    LogM("Scenario1Config") << "RX callback hooked to UAV application";

    // Phase 4: wire aggregate PHY/MAC counters on every LrWpanNetDevice.
    ConnectPhyMacCounters();

    LogFlush();  // checkpoint: build complete
}

void Scenario1Config::BuildAndInstallCellLayer() {
    CellLayerConfig cfg;
    cfg.cellSizeMeters = cellSizeMeters;
    cfg.neighborRangeMeters = cellNeighborRangeMeters;
    cfg.colorCount = cellColorCount;

    CellLayerPlan plan = BuildCellLayerPlan(m_setup.sensorNodes, cfg);
    uint32_t leaders = 0;
    uint32_t isolated = 0;
    uint32_t unreachable = 0;
    uint32_t maxHop = 0;
    uint64_t neighborSum = 0;

    for (const auto& app : m_groundApps) {
        auto it = plan.nodes.find(app->GetNodeId());
        if (it == plan.nodes.end()) continue;
        app->SetCellRoutingInfo(it->second);
        if (it->second.isCellLeader) leaders++;
        if (it->second.isIsolated) isolated++;
        if (it->second.hopToLeader == std::numeric_limits<uint32_t>::max()) {
            unreachable++;
        } else {
            maxHop = std::max(maxHop, it->second.hopToLeader);
        }
        neighborSum += it->second.neighbors.size();
    }

    double meanNeighbors = m_groundApps.empty()
                               ? 0.0
                               : static_cast<double>(neighborSum) / m_groundApps.size();
    LogM("Scenario1Config") << "Cell layer installed by BS direct bootstrap:\n";
    LogM("Scenario1Config") << "  cellSize=" << cfg.cellSizeMeters
                            << "m neighborRange=" << cfg.neighborRangeMeters
                            << "m colors=" << cfg.colorCount << "\n";
    LogM("Scenario1Config") << "  cells=" << plan.nodesByCell.size()
                            << " leaders=" << leaders
                            << " isolated=" << isolated
                            << " unreachableToLeader=" << unreachable
                            << " maxHopToLeader=" << maxHop
                            << " meanNeighbors=" << std::fixed << std::setprecision(1)
                            << meanNeighbors << "\n";
    LogM("Scenario1Config") << "  sample node cell info:";
    uint32_t sampleCount = 0;
    for (const auto& app : m_groundApps) {
        if (sampleCount >= 8) break;
        auto it = plan.nodes.find(app->GetNodeId());
        if (it == plan.nodes.end()) continue;
        const CellRoutingInfo& info = it->second;
        LogM("Scenario1Config") << " node " << info.nodeId
                                << "[cell=" << info.cellId
                                << ",color=" << info.cellColor
                                << ",leader=" << info.cellLeaderId
                                << ",parent=" << info.parentId
                                << ",peers=" << info.cellPeers.size()
                                << ",neighbors=" << info.neighbors.size()
                                << "]";
        sampleCount++;
    }
    LogM("Scenario1Config") << "\n";
}

void Scenario1Config::BuildAndInstallLocalClues() {
    LocalClueConfig cfg;
    cfg.targetNodeId = clueTargetNodeId;
    cfg.randomSeed = clueSeed;
    cfg.strongRadiusMeters = clueStrongRadiusMeters;
    cfg.weakRadiusMeters = clueWeakRadiusMeters;
    cfg.decayMeters = clueDecayMeters;
    cfg.maxBlurredQuality = clueMaxBlurredQuality;
    cfg.backgroundFalsePositiveRate = clueFalsePositiveRate;

    m_cluePlan = BuildLocalCluePlan(m_setup.sensorNodes, cfg);

    uint32_t trueNodes = 0;
    uint32_t blurredNodes = 0;
    uint32_t falsePositiveNodes = 0;
    uint32_t zeroClueNodes = 0;
    uint32_t strongRadiusNodes = 0;
    uint32_t weakRadiusNodes = 0;
    double qualitySum = 0.0;

    for (const auto& app : m_groundApps) {
        auto it = m_cluePlan.nodes.find(app->GetNodeId());
        if (it == m_cluePlan.nodes.end()) continue;
        app->SetLocalClueInfo(it->second);

        const LocalClueInfo& info = it->second;
        if (info.isTrueTargetNode) trueNodes++;
        else if (info.isFalsePositive) falsePositiveNodes++;
        else if (info.clueQuality > 0.0) blurredNodes++;
        else zeroClueNodes++;

        if (info.distanceToTargetMeters <= cfg.strongRadiusMeters) strongRadiusNodes++;
        if (info.distanceToTargetMeters <= cfg.weakRadiusMeters) weakRadiusNodes++;
        qualitySum += info.clueQuality;
    }

    double meanQuality = m_groundApps.empty()
                             ? 0.0
                             : qualitySum / static_cast<double>(m_groundApps.size());
    LogM("Scenario1Config") << "Local clue model installed by BS direct bootstrap:\n";
    LogM("Scenario1Config") << "  targetNode=" << m_cluePlan.targetNodeId
                            << " pos=(" << m_cluePlan.targetPosition.x
                            << "," << m_cluePlan.targetPosition.y << ")"
                            << " seed=" << cfg.randomSeed << "\n";
    LogM("Scenario1Config") << "  strongRadius=" << cfg.strongRadiusMeters
                            << "m weakRadius=" << cfg.weakRadiusMeters
                            << "m decay=" << cfg.decayMeters
                            << "m maxBlurredQuality=" << cfg.maxBlurredQuality
                            << " falsePositiveRate=" << cfg.backgroundFalsePositiveRate
                            << "\n";
    LogM("Scenario1Config") << "  true=" << trueNodes
                            << " blurred=" << blurredNodes
                            << " falsePositive=" << falsePositiveNodes
                            << " zero=" << zeroClueNodes
                            << " withinStrong=" << strongRadiusNodes
                            << " withinWeak=" << weakRadiusNodes
                            << " meanQuality=" << std::fixed << std::setprecision(3)
                            << meanQuality << "\n";

    std::vector<LocalClueInfo> topClues;
    topClues.reserve(m_cluePlan.nodes.size());
    for (const auto& [_, info] : m_cluePlan.nodes) {
        if (info.clueQuality > 0.0 || info.isTrueTargetNode) {
            topClues.push_back(info);
        }
    }
    std::sort(topClues.begin(), topClues.end(),
              [](const LocalClueInfo& a, const LocalClueInfo& b) {
                  if (a.clueQuality != b.clueQuality) return a.clueQuality > b.clueQuality;
                  return a.nodeId < b.nodeId;
              });

    LogM("Scenario1Config") << "  sample top clue nodes:";
    uint32_t sampleCount = 0;
    for (const LocalClueInfo& info : topClues) {
        if (sampleCount >= 8) break;
        LogM("Scenario1Config") << " node " << info.nodeId
                                << "[q=" << std::fixed << std::setprecision(2)
                                << info.clueQuality
                                << ",overlap=" << info.semanticOverlap
                                << ",d=" << std::setprecision(1)
                                << info.distanceToTargetMeters
                                << ",types=" << info.matchedSemanticTypes.size()
                                << (info.isTrueTargetNode ? ",true" : "")
                                << (info.isFalsePositive ? ",fp" : "")
                                << "]";
        sampleCount++;
    }
    LogM("Scenario1Config") << "\n";
}

void Scenario1Config::ConnectPhyMacCounters() {
    // Reset (Build() may be called fresh per scenario instance, but guard anyway).
    m_phyTxBegin = m_phyRxBegin = m_phyRxDrop = 0;
    m_macTx = m_macTxOk = m_macTxEnqueue = m_macTxDequeue = 0;
    m_macSentPkt = m_macTxDrop = 0;
    m_macTraceConnectFail = 0;
    m_macRetries = m_macBackoffs = 0;

    // Captureless lambdas decay to function pointers via the leading +, so
    // they can be wrapped by MakeBoundCallback(fn*, this).
    auto onPhyTxBegin = +[](Scenario1Config* self, Ptr<const Packet>) {
        ++self->m_phyTxBegin;
    };
    auto onPhyRxBegin = +[](Scenario1Config* self, Ptr<const Packet>) {
        ++self->m_phyRxBegin;
    };
    auto onPhyRxDrop  = +[](Scenario1Config* self, Ptr<const Packet>) {
        ++self->m_phyRxDrop;
    };
    auto onMacSent    = +[](Scenario1Config* self,
                            Ptr<const Packet>, uint8_t retries, uint8_t backoffs) {
        ++self->m_macSentPkt;
        self->m_macRetries  += retries;
        self->m_macBackoffs += backoffs;
    };
    auto onMacTx      = +[](Scenario1Config* self, Ptr<const Packet>) {
        ++self->m_macTx;
    };
    auto onMacTxOk    = +[](Scenario1Config* self, Ptr<const Packet>) {
        ++self->m_macTxOk;
    };
    auto onMacTxEnqueue = +[](Scenario1Config* self, Ptr<const Packet>) {
        ++self->m_macTxEnqueue;
    };
    auto onMacTxDequeue = +[](Scenario1Config* self, Ptr<const Packet>) {
        ++self->m_macTxDequeue;
    };
    auto onMacTxDrop  = +[](Scenario1Config* self, Ptr<const Packet>) {
        ++self->m_macTxDrop;
    };

    auto wirePhyMac = [&, this](Ptr<NetDevice> dev) {
        Ptr<lrwpan::LrWpanNetDevice> lrDev =
            DynamicCast<lrwpan::LrWpanNetDevice>(dev);
        if (!lrDev) return;

        Ptr<lrwpan::LrWpanPhy> phy = lrDev->GetPhy();
        Ptr<lrwpan::LrWpanMac> mac = lrDev->GetMac();
        auto mustConnect = [this](bool ok) {
            if (!ok) {
                ++m_macTraceConnectFail;
            }
        };

        // PHY: Ptr<const Packet> only — no drop-reason argument exposed.
        mustConnect(phy->TraceConnectWithoutContext("PhyTxBegin",
            MakeBoundCallback(onPhyTxBegin, this)));
        mustConnect(phy->TraceConnectWithoutContext("PhyRxBegin",
            MakeBoundCallback(onPhyRxBegin, this)));
        mustConnect(phy->TraceConnectWithoutContext("PhyRxDrop",
            MakeBoundCallback(onPhyRxDrop, this)));

        // MAC: use both generic TX lifecycle traces and MacSentPkt. In
        // ns-3.46 lr-wpan, MacSentPkt fires only from a narrow queue-removal
        // path, so MacTxOk is the more reliable successful-TX counter.
        mustConnect(mac->TraceConnectWithoutContext("MacTx",
            MakeBoundCallback(onMacTx, this)));
        mustConnect(mac->TraceConnectWithoutContext("MacTxOk",
            MakeBoundCallback(onMacTxOk, this)));
        mustConnect(mac->TraceConnectWithoutContext("MacTxEnqueue",
            MakeBoundCallback(onMacTxEnqueue, this)));
        mustConnect(mac->TraceConnectWithoutContext("MacTxDequeue",
            MakeBoundCallback(onMacTxDequeue, this)));
        mustConnect(mac->TraceConnectWithoutContext("MacSentPkt",
            MakeBoundCallback(onMacSent, this)));
        // MacTxDrop: Ptr<const Packet> only — no drop-reason argument exposed.
        mustConnect(mac->TraceConnectWithoutContext("MacTxDrop",
            MakeBoundCallback(onMacTxDrop, this)));
    };

    wirePhyMac(m_setup.baseStationDevice.Get(0));
    wirePhyMac(m_setup.uavDevice.Get(0));
    for (uint32_t i = 0; i < m_setup.sensorDevices.GetN(); i++) {
        wirePhyMac(m_setup.sensorDevices.Get(i));
    }
    LogM("Scenario1Config") << "PHY/MAC counter traces wired on "
                            << (2 + m_setup.sensorDevices.GetN())
                            << " devices (connect failures=" << m_macTraceConnectFail << ")";
}

void Scenario1Config::Schedule() {
    double delayThreshold = 0.01;  // 10ms max stagger
    RandomDelayedStartUp(delayThreshold);
    ScheduleInCellCooperation();

    LogM("Scenario1Config") << "Simulation Schedule:\n";
    LogM("Scenario1Config") << "  t=" << startTimeSec << "s  : UAV starts broadcasting\n";
    if (inCellCooperationEnabled) {
        LogM("Scenario1Config") << "  t=" << inCellCooperationStartSec
                                << "s  : in-cell cooperation starts every "
                                << inCellCooperationIntervalSec << "s\n";
    }
    LogM("Scenario1Config") << "  t=" << simulationDurationSec << ".0s : Stop simulation\n\n";
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

void Scenario1Config::ScheduleInCellCooperation() {
    m_inCellCoopRounds = 0;
    m_inCellCoopFragmentTransfers = 0;
    m_interCellCoopFragmentTransfers = 0;
    CooperationPhyMacConfig coopCfg;
    coopCfg.packetsPerFragment = m_uavApp ? m_uavApp->L0SubPacketsPerFragment() : 1;
    if (coopCfg.packetsPerFragment == 0) coopCfg.packetsPerFragment = 1;
    coopCfg.intraCellPacketBudget = coopInCellPacketBudgetPerNode;
    coopCfg.interCellPacketBudget = coopInterCellPacketBudgetPerNode;
    coopCfg.intraCellManifestSuccessProb = coopInCellManifestSuccessProb;
    coopCfg.interCellManifestSuccessProb = coopInterCellManifestSuccessProb;
    coopCfg.intraCellFragmentSuccessProb = coopInCellFragmentSuccessProb;
    coopCfg.interCellFragmentSuccessProb = coopInterCellFragmentSuccessProb;
    m_coopPhyMac.Configure(coopCfg);
    m_coopPhyMac.ResetCounters();
    m_detectionReached = false;
    m_detectionTimeSec = -1.0;
    m_detectionNodeId = 0;
    m_detectionConfidence = 0.0;
    if (!inCellCooperationEnabled || inCellCooperationIntervalSec <= 0.0) {
        LogM("Scenario1Config") << "In-cell cooperation disabled\n";
        return;
    }

    m_inCellCoopEvent = Simulator::Schedule(Seconds(inCellCooperationStartSec),
                                            &Scenario1Config::RunInCellCooperationRound,
                                            this);
    LogM("Scenario1Config") << "In-cell cooperation scheduled: interval="
                            << inCellCooperationIntervalSec
                            << "s stopRatio=" << inCellCooperationStopRatio
                            << " interCell=" << (interCellCooperationEnabled ? "enabled" : "disabled")
                            << " everyRounds=" << interCellCooperationEveryRounds
                            << " range=" << interCellCooperationRangeMeters
                            << "m alertRatio=" << cooperationAlertRatio
                            << " detectionThreshold=" << detectionAlertThreshold
                            << " inBudgetPkts=" << coopInCellPacketBudgetPerNode
                            << " interBudgetPkts=" << coopInterCellPacketBudgetPerNode
                            << " inManifestSucc=" << coopInCellManifestSuccessProb
                            << " interManifestSucc=" << coopInterCellManifestSuccessProb
                            << " inSucc=" << coopInCellFragmentSuccessProb
                            << " interSucc=" << coopInterCellFragmentSuccessProb << "\n";
}

uint32_t Scenario1Config::ApplyCoopTransfer(Ptr<GroundNodeApp> app,
                                            const std::set<uint16_t>& offeredFragments,
                                            CooperationLinkType linkType) {
    if (!app || offeredFragments.empty()) return 0;
    CooperationTransferResult tx = m_coopPhyMac.TransferMissingFragments(
        linkType,
        offeredFragments,
        app->DistinctFragments());
    return app->MergeCoopFragments(tx.deliveredFragments);
}

std::string Scenario1Config::DetectionModelName() const {
    switch (detectionModel) {
        case DetectionModel::FRAGMENT_RATIO: return "fragment-ratio";
        case DetectionModel::CLUE_WEIGHTED:  return "clue-weighted";
        case DetectionModel::NOISY_OR:       return "noisy-or";
    }
    return "unknown";
}

double Scenario1Config::ComputeNodeDetectionScore(Ptr<GroundNodeApp> app,
                                                  uint32_t fragTotal) const {
    if (!app || !app->HasLocalClueInfo()) return 0.0;
    const LocalClueInfo& clue = app->GetLocalClueInfo();
    double fragmentRatio = (fragTotal > 0)
                               ? static_cast<double>(app->DistinctFragmentCount()) /
                                     static_cast<double>(fragTotal)
                               : 0.0;
    switch (detectionModel) {
        case DetectionModel::FRAGMENT_RATIO:
            return std::max(0.0, std::min(1.0, fragmentRatio));
        case DetectionModel::CLUE_WEIGHTED: {
            double evidenceGate = 0.35 + 0.65 * fragmentRatio;
            return std::max(0.0, std::min(1.0,
                clue.clueQuality * clue.semanticOverlap * evidenceGate));
        }
        case DetectionModel::NOISY_OR: {
            // Placeholder until per-fragment p_i is carried in the received set.
            // Uses equal per-fragment utility calibrated so 180 fragments approach
            // high confidence without instant saturation.
            constexpr double p = 0.015;
            double product = std::pow(1.0 - p, app->DistinctFragmentCount());
            double fragmentConfidence = 1.0 - product;
            return std::max(0.0, std::min(1.0,
                fragmentConfidence * clue.clueQuality * clue.semanticOverlap));
        }
    }
    return 0.0;
}

double Scenario1Config::ComputeNodeFalseAlarm(Ptr<GroundNodeApp> app,
                                              uint32_t fragTotal) const {
    if (!app || !app->HasLocalClueInfo()) return 0.0;
    const LocalClueInfo& clue = app->GetLocalClueInfo();
    if (clue.isTrueTargetNode) return 0.0;

    double fragmentRatio = (fragTotal > 0)
                               ? static_cast<double>(app->DistinctFragmentCount()) /
                                     static_cast<double>(fragTotal)
                               : 0.0;
    return std::max(0.0, std::min(1.0,
        clue.falsePositiveRisk *
        (0.20 + 0.80 * fragmentRatio) *
        (0.25 + 0.75 * clue.clueQuality)));
}

void Scenario1Config::CheckDetection(uint32_t fragTotal, const char* source) {
    if (m_detectionReached || fragTotal == 0) return;
    for (const auto& app : m_groundApps) {
        if (!app->HasLocalClueInfo() || !app->GetLocalClueInfo().isTrueTargetNode) continue;
        double confidence = ComputeNodeDetectionScore(app, fragTotal);
        if (confidence >= detectionAlertThreshold) {
            m_detectionReached = true;
            m_detectionTimeSec = Simulator::Now().GetSeconds();
            m_detectionNodeId = app->GetNodeId();
            m_detectionConfidence = confidence;
            LogT("DETECT") << "target node " << m_detectionNodeId
                           << " confidence=" << confidence
                           << " threshold=" << detectionAlertThreshold
                           << " model=" << DetectionModelName()
                           << " source=" << source
                           << " fragments=" << app->DistinctFragmentCount()
                           << "/" << fragTotal;
            break;
        }
    }
}

void Scenario1Config::RunInCellCooperationRound() {
    if (!inCellCooperationEnabled) return;
    m_inCellCoopRounds++;

    uint32_t fragTotal = m_uavApp ? m_uavApp->L0FragmentCount() : 0;
    uint32_t currentPacketsPerFragment = m_uavApp ? m_uavApp->L0SubPacketsPerFragment() : 0;
    if (currentPacketsPerFragment > 0 &&
        currentPacketsPerFragment != m_coopPhyMac.Config().packetsPerFragment) {
        CooperationPhyMacConfig cfg = m_coopPhyMac.Config();
        cfg.packetsPerFragment = currentPacketsPerFragment;
        m_coopPhyMac.Configure(cfg);
        LogT("COOP") << "PHY/MAC packetsPerFragment updated to "
                     << currentPacketsPerFragment;
    }
    std::map<int32_t, std::set<uint16_t>> cellUnion;
    std::map<int32_t, uint32_t> cellMembers;
    std::map<int32_t, Vector> cellPositionSum;
    std::map<int32_t, uint64_t> cellDistinctSum;

    for (const auto& app : m_groundApps) {
        if (!app->HasCellRoutingInfo()) continue;
        int32_t cellId = app->GetCellRoutingInfo().cellId;
        cellMembers[cellId]++;
        const Vector& pos = app->GetCellRoutingInfo().position;
        cellPositionSum[cellId].x += pos.x;
        cellPositionSum[cellId].y += pos.y;
        cellPositionSum[cellId].z += pos.z;
        cellDistinctSum[cellId] += app->DistinctFragmentCount();
        const auto& fragments = app->DistinctFragments();
        cellUnion[cellId].insert(fragments.begin(), fragments.end());
    }

    uint64_t gainedThisRound = 0;
    for (const auto& app : m_groundApps) {
        if (!app->HasCellRoutingInfo()) continue;
        if (fragTotal > 0 && inCellCooperationStopRatio > 0.0) {
            double ratio = static_cast<double>(app->DistinctFragmentCount()) /
                           static_cast<double>(fragTotal);
            if (ratio >= inCellCooperationStopRatio) {
                continue;
            }
        }

        int32_t cellId = app->GetCellRoutingInfo().cellId;
        auto it = cellUnion.find(cellId);
        if (it == cellUnion.end() || it->second.empty()) continue;
        gainedThisRound += ApplyCoopTransfer(app,
                                             it->second,
                                             CooperationLinkType::INTRA_CELL);
    }
    m_inCellCoopFragmentTransfers += gainedThisRound;

    uint64_t interGainedThisRound = 0;
    if (interCellCooperationEnabled && interCellCooperationEveryRounds > 0 &&
        (m_inCellCoopRounds % interCellCooperationEveryRounds == 0)) {
        std::map<int32_t, Vector> centroids;
        for (const auto& [cellId, count] : cellMembers) {
            if (count == 0) continue;
            Vector c = cellPositionSum[cellId];
            c.x /= static_cast<double>(count);
            c.y /= static_cast<double>(count);
            c.z /= static_cast<double>(count);
            centroids[cellId] = c;
        }

        // Gateway-to-gateway abstraction from the paper: cells exchange compact
        // manifests with adjacent cells. A receiving cell pulls neighbor union
        // only while its mean fragment ratio is below the alert ratio.
        std::map<int32_t, std::set<uint16_t>> neighborManifest;
        for (const auto& [cellId, centroid] : centroids) {
            double cellMeanRatio = 0.0;
            auto cntIt = cellMembers.find(cellId);
            if (fragTotal > 0 && cntIt != cellMembers.end() && cntIt->second > 0) {
                cellMeanRatio = static_cast<double>(cellDistinctSum[cellId]) /
                                (static_cast<double>(cntIt->second) *
                                 static_cast<double>(fragTotal));
            }
            if (cellMeanRatio >= cooperationAlertRatio) {
                continue;
            }

            auto& manifest = neighborManifest[cellId];
            for (const auto& [otherCellId, otherCentroid] : centroids) {
                if (otherCellId == cellId) continue;
                double dx = centroid.x - otherCentroid.x;
                double dy = centroid.y - otherCentroid.y;
                double dist = std::sqrt(dx * dx + dy * dy);
                if (dist > interCellCooperationRangeMeters) continue;

                auto unionIt = cellUnion.find(otherCellId);
                if (unionIt == cellUnion.end()) continue;
                manifest.insert(unionIt->second.begin(), unionIt->second.end());
            }
        }

        for (const auto& app : m_groundApps) {
            if (!app->HasCellRoutingInfo()) continue;
            if (fragTotal > 0 && cooperationAlertRatio > 0.0) {
                double ratio = static_cast<double>(app->DistinctFragmentCount()) /
                               static_cast<double>(fragTotal);
                if (ratio >= cooperationAlertRatio) {
                    continue;
                }
            }
            int32_t cellId = app->GetCellRoutingInfo().cellId;
            auto it = neighborManifest.find(cellId);
            if (it == neighborManifest.end() || it->second.empty()) continue;
            interGainedThisRound += ApplyCoopTransfer(app,
                                                      it->second,
                                                      CooperationLinkType::INTER_CELL);
        }
        m_interCellCoopFragmentTransfers += interGainedThisRound;
    }

    if (gainedThisRound > 0 || interGainedThisRound > 0) {
        CheckDetection(fragTotal, interGainedThisRound > 0 ? "inter-cell-coop" : "in-cell-coop");
    }

    if (gainedThisRound > 0 || interGainedThisRound > 0 || (m_inCellCoopRounds <= 3)) {
        const CooperationPhyMacCounters& counters = m_coopPhyMac.Counters();
        LogT("COOP") << "in-cell round=" << m_inCellCoopRounds
                     << " cells=" << cellUnion.size()
                     << " gained=" << gainedThisRound
                     << " interGained=" << interGainedThisRound
                     << " totalIntra=" << m_inCellCoopFragmentTransfers
                     << " totalInter=" << m_interCellCoopFragmentTransfers
                     << " coopPkts=" << counters.dataPacketsDelivered
                     << "/" << counters.dataPacketsAttempted;
    }

    double next = Simulator::Now().GetSeconds() + inCellCooperationIntervalSec;
    if (next < simulationDurationSec) {
        m_inCellCoopEvent = Simulator::Schedule(Seconds(inCellCooperationIntervalSec),
                                                &Scenario1Config::RunInCellCooperationRound,
                                                this);
    }
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

    // Layer-0 systematic dissemination: how many DISTINCT fragments did each
    // ground node fully receive? (semantic preamble counted separately).
    uint32_t totalNodes = static_cast<uint32_t>(m_groundApps.size());
    uint32_t fragTotal = m_uavApp->L0FragmentCount();
    uint32_t nodesAll = 0, nodesPartial = 0, nodesZero = 0;
    uint32_t directNodesAll = 0, directNodesPartial = 0, directNodesZero = 0;
    std::vector<uint32_t> distincts;
    std::vector<uint32_t> directDistincts;
    distincts.reserve(totalNodes);
    directDistincts.reserve(totalNodes);
    for (const auto& app : m_groundApps) {
        uint32_t direct = app->DirectUavFragmentCount();
        uint32_t d = app->DistinctFragmentCount();
        directDistincts.push_back(direct);
        distincts.push_back(d);
        if (direct == 0) directNodesZero++;
        else if (fragTotal > 0 && direct >= fragTotal) directNodesAll++;
        else directNodesPartial++;
        if (d == 0) nodesZero++;
        else if (fragTotal > 0 && d >= fragTotal) nodesAll++;
        else nodesPartial++;
    }
    std::sort(directDistincts.begin(), directDistincts.end());
    std::sort(distincts.begin(), distincts.end());
    uint64_t directSum = 0;
    for (uint32_t d : directDistincts) directSum += d;
    uint64_t dsum = 0;
    for (uint32_t d : distincts) dsum += d;
    double directMean = totalNodes ? static_cast<double>(directSum) / totalNodes : 0.0;
    double dmean = totalNodes ? static_cast<double>(dsum) / totalNodes : 0.0;
    auto pctVec = [](const std::vector<uint32_t>& values, double q) -> uint32_t {
        if (values.empty()) return 0;
        size_t idx = static_cast<size_t>(q * (values.size() - 1));
        return values[idx];
    };
    auto pct = [&](double q) -> uint32_t { return pctVec(distincts, q); };
    auto directPct = [&](double q) -> uint32_t { return pctVec(directDistincts, q); };
    uint32_t directMin = directDistincts.empty() ? 0 : directDistincts.front();
    uint32_t directMax = directDistincts.empty() ? 0 : directDistincts.back();
    uint32_t dmin = distincts.empty() ? 0 : distincts.front();
    uint32_t dmax = distincts.empty() ? 0 : distincts.back();

    // Phase 4: aggregate PHY/MAC counters (lr-wpan trace sources). Drop traces
    // carry only Ptr<const Packet> in ns-3.46, so no reason buckets are exposed.
    LogM("Scenario1Config") << "PHY counters:\n";
    LogM("Scenario1Config") << "  PhyTxBegin : " << m_phyTxBegin << "\n";
    LogM("Scenario1Config") << "  PhyRxBegin : " << m_phyRxBegin << "\n";
    LogM("Scenario1Config") << "  PhyRxDrop  : " << m_phyRxDrop  << "\n";
    LogM("Scenario1Config") << "MAC counters:\n";
    LogM("Scenario1Config") << "  MacTx        : " << m_macTx << "\n";
    LogM("Scenario1Config") << "  MacTxOk      : " << m_macTxOk << "\n";
    LogM("Scenario1Config") << "  MacTxEnqueue : " << m_macTxEnqueue << "\n";
    LogM("Scenario1Config") << "  MacTxDequeue : " << m_macTxDequeue << "\n";
    LogM("Scenario1Config") << "  MacSentPkt : " << m_macSentPkt
                            << " (retries=" << m_macRetries
                            << ", csma_backoffs=" << m_macBackoffs << ")\n";
    LogM("Scenario1Config") << "  MacTxDrop  : " << m_macTxDrop << "\n";
    LogM("Scenario1Config") << "  Trace connect failures : "
                            << m_macTraceConnectFail << "\n\n";

    LogM("Scenario1Config") << "L0 dissemination result:\n";
    LogM("Scenario1Config") << "  UAV flight path model     : "
                            << m_uavApp->GetFlightPathModelName()
                            << " broadcastModel=" << m_uavApp->GetBroadcastModelName()
                            << "\n";
    LogM("Scenario1Config") << "  UAV flight cost           : waypoints="
                            << m_uavApp->WaypointCount()
                            << " plannedPath=" << std::fixed << std::setprecision(1)
                            << m_uavApp->PlannedPathLengthMeters()
                            << "m takeoff=" << std::setprecision(3)
                            << m_uavApp->TakeoffTimeSec()
                            << "s landing=" << m_uavApp->LandingTimeSec()
                            << "s duration=" << m_uavApp->FlightDurationSec()
                            << "s\n";
    LogM("Scenario1Config") << "  UAV search packets emitted: " << m_uavApp->L0BroadcastCount()
                            << " (attempts=" << m_uavApp->L0SendAttemptCount()
                            << " fail=" << m_uavApp->L0SendFailCount() << ")\n";
    LogM("Scenario1Config") << "  L0 fragments total        : " << fragTotal
                            << " (" << m_uavApp->L0SubPacketsPerFragment()
                            << " data sub-packets / fragment + 1 semantic)\n";
    LogM("Scenario1Config") << "  in-cell cooperation       : "
                            << (inCellCooperationEnabled ? "enabled" : "disabled")
                            << " rounds=" << m_inCellCoopRounds
                            << " gainedFragments=" << m_inCellCoopFragmentTransfers
                            << " interval=" << inCellCooperationIntervalSec << "s\n";
    LogM("Scenario1Config") << "  inter-cell cooperation    : "
                            << (interCellCooperationEnabled ? "enabled" : "disabled")
                            << " everyRounds=" << interCellCooperationEveryRounds
                            << " range=" << interCellCooperationRangeMeters
                            << "m alertRatio=" << cooperationAlertRatio
                            << " gainedFragments=" << m_interCellCoopFragmentTransfers
                            << "\n";
    const CooperationPhyMacCounters& coopCounters = m_coopPhyMac.Counters();
    const CooperationPhyMacConfig& coopCfg = m_coopPhyMac.Config();
    LogM("Scenario1Config") << "  cooperation PHY/MAC       : manifestPkts="
                            << coopCounters.manifestPacketsDelivered
                            << "/" << coopCounters.manifestPacketsAttempted
                            << " manifestDrop=" << coopCounters.manifestPacketsDropped
                            << " dataPktsAttempted=" << coopCounters.dataPacketsAttempted
                            << " delivered=" << coopCounters.dataPacketsDelivered
                            << " dropped=" << coopCounters.dataPacketsDropped
                            << " fragmentTx="
                            << coopCounters.fragmentTransfersCompleted
                            << "/" << coopCounters.fragmentTransfersAttempted
                            << " incomplete=" << coopCounters.fragmentTransfersIncomplete
                            << " packetsPerFragment=" << coopCfg.packetsPerFragment
                            << " inBudget=" << coopCfg.intraCellPacketBudget
                            << " interBudget=" << coopCfg.interCellPacketBudget
                            << " inManifestSucc=" << coopCfg.intraCellManifestSuccessProb
                            << " interManifestSucc=" << coopCfg.interCellManifestSuccessProb
                            << " targetFragSucc(in/inter)="
                            << coopCfg.intraCellFragmentSuccessProb
                            << "/" << coopCfg.interCellFragmentSuccessProb
                            << " transferCalls(in/inter)="
                            << coopCounters.intraCellTransferCalls
                            << "/" << coopCounters.interCellTransferCalls
                            << "\n";
    LogM("Scenario1Config") << "  detection model           : "
                            << DetectionModelName() << "\n";
    if (m_detectionReached) {
        LogM("Scenario1Config") << "  detection time            : "
                                << std::fixed << std::setprecision(3)
                                << m_detectionTimeSec << "s"
                                << " node=" << m_detectionNodeId
                                << " confidence=" << m_detectionConfidence
                                << " threshold=" << detectionAlertThreshold
                                << " model=" << DetectionModelName() << "\n";
    } else {
        LogM("Scenario1Config") << "  detection time            : not reached"
                                << " threshold=" << detectionAlertThreshold << "\n";
    }

    LogM("Scenario1Config") << "L0 direct UAV fragments per node:\n";
    LogM("Scenario1Config") << "  mean=" << std::fixed << std::setprecision(1) << directMean
                            << "   median=" << directPct(0.50)
                            << "   min=" << directMin << "   max=" << directMax << "\n";
    LogM("Scenario1Config") << "  q25=" << directPct(0.25)
                            << "   q75=" << directPct(0.75)
                            << "   p90=" << directPct(0.90) << "\n";
    LogM("Scenario1Config") << "  nodes all (" << fragTotal << "/" << fragTotal << ")   : "
                            << directNodesAll << "/" << totalNodes << "\n";
    LogM("Scenario1Config") << "  nodes partial         : " << directNodesPartial << "/" << totalNodes << "\n";
    LogM("Scenario1Config") << "  nodes zero            : " << directNodesZero << "/" << totalNodes << "\n\n";

    LogM("Scenario1Config") << "L0 distinct fragments per node after cooperation:\n";
    LogM("Scenario1Config") << "  mean=" << std::fixed << std::setprecision(1) << dmean
                            << "   median=" << pct(0.50)
                            << "   min=" << dmin << "   max=" << dmax << "\n";
    LogM("Scenario1Config") << "  q25=" << pct(0.25)
                            << "   q75=" << pct(0.75)
                            << "   p90=" << pct(0.90) << "\n";
    LogM("Scenario1Config") << "  nodes all (" << fragTotal << "/" << fragTotal << ")   : "
                            << nodesAll << "/" << totalNodes << "\n";
    LogM("Scenario1Config") << "  nodes partial         : " << nodesPartial << "/" << totalNodes << "\n";
    LogM("Scenario1Config") << "  nodes zero            : " << nodesZero << "/" << totalNodes << "\n\n";

    struct NodeSearchScore {
        uint32_t nodeId = 0;
        int32_t cellId = -1;
        double score = 0.0;
        double detectionScore = 0.0;
        double falseAlarmProbability = 0.0;
        double clueQuality = 0.0;
        double semanticOverlap = 0.0;
        double fragmentRatio = 0.0;
        bool isTarget = false;
        bool isFalsePositive = false;
    };
    std::vector<NodeSearchScore> nodeScores;
    nodeScores.reserve(m_groundApps.size());

    for (const auto& app : m_groundApps) {
        if (!app->HasLocalClueInfo()) continue;
        const LocalClueInfo& clue = app->GetLocalClueInfo();
        double fragmentRatio = (fragTotal > 0)
                                   ? static_cast<double>(app->DistinctFragmentCount()) /
                                         static_cast<double>(fragTotal)
                                   : 0.0;
        double detectionScore = ComputeNodeDetectionScore(app, fragTotal);
        double falseAlarmProbability = ComputeNodeFalseAlarm(app, fragTotal);
        double score = std::max(0.0, detectionScore - 0.20 * falseAlarmProbability);

        NodeSearchScore item;
        item.nodeId = app->GetNodeId();
        item.cellId = app->HasCellRoutingInfo() ? app->GetCellRoutingInfo().cellId : -1;
        item.score = score;
        item.detectionScore = detectionScore;
        item.falseAlarmProbability = falseAlarmProbability;
        item.clueQuality = clue.clueQuality;
        item.semanticOverlap = clue.semanticOverlap;
        item.fragmentRatio = fragmentRatio;
        item.isTarget = clue.isTrueTargetNode;
        item.isFalsePositive = clue.isFalsePositive;
        nodeScores.push_back(item);
    }

    std::sort(nodeScores.begin(), nodeScores.end(),
              [](const NodeSearchScore& a, const NodeSearchScore& b) {
                  if (a.score != b.score) return a.score > b.score;
                  return a.nodeId < b.nodeId;
              });

    uint32_t targetNodeRank = 0;
    int32_t targetCellId = -1;
    double targetNodeScore = 0.0;
    double targetDetectionScore = 0.0;
    for (uint32_t i = 0; i < nodeScores.size(); i++) {
        if (nodeScores[i].isTarget) {
            targetNodeRank = i + 1;
            targetCellId = nodeScores[i].cellId;
            targetNodeScore = nodeScores[i].score;
            targetDetectionScore = nodeScores[i].detectionScore;
            break;
        }
    }

    struct CellSearchScore {
        int32_t cellId = -1;
        double score = 0.0;
        double bestNodeScore = 0.0;
        double meanTopSupport = 0.0;
        double meanFragmentRatio = 0.0;
        uint32_t nodeCount = 0;
        bool hasTarget = false;
    };
    std::map<int32_t, std::vector<NodeSearchScore>> byCell;
    for (const auto& item : nodeScores) {
        byCell[item.cellId].push_back(item);
    }

    std::vector<CellSearchScore> cellScores;
    cellScores.reserve(byCell.size());
    for (auto& [cellId, members] : byCell) {
        std::sort(members.begin(), members.end(),
                  [](const NodeSearchScore& a, const NodeSearchScore& b) {
                      if (a.score != b.score) return a.score > b.score;
                      return a.nodeId < b.nodeId;
                  });

        double fragmentSum = 0.0;
        double supportSum = 0.0;
        uint32_t supportCount = 0;
        bool hasTarget = false;
        for (const auto& item : members) {
            fragmentSum += item.fragmentRatio;
            hasTarget = hasTarget || item.isTarget;
        }
        for (uint32_t i = 0; i < members.size() && i < 3; i++) {
            supportSum += members[i].score;
            supportCount++;
        }

        CellSearchScore cell;
        cell.cellId = cellId;
        cell.nodeCount = static_cast<uint32_t>(members.size());
        cell.bestNodeScore = members.empty() ? 0.0 : members.front().score;
        cell.meanTopSupport = supportCount ? supportSum / supportCount : 0.0;
        cell.meanFragmentRatio = members.empty() ? 0.0 : fragmentSum / members.size();
        cell.hasTarget = hasTarget;
        cell.score = cell.bestNodeScore +
                     0.25 * cell.meanTopSupport +
                     0.10 * cell.meanFragmentRatio;
        cellScores.push_back(cell);
    }

    std::sort(cellScores.begin(), cellScores.end(),
              [](const CellSearchScore& a, const CellSearchScore& b) {
                  if (a.score != b.score) return a.score > b.score;
                  return a.cellId < b.cellId;
              });

    uint32_t targetCellRank = 0;
    double targetCellScore = 0.0;
    for (uint32_t i = 0; i < cellScores.size(); i++) {
        if (cellScores[i].cellId == targetCellId) {
            targetCellRank = i + 1;
            targetCellScore = cellScores[i].score;
            break;
        }
    }

    double detectionSum = 0.0;
    double falseAlarmSum = 0.0;
    double nonTargetFalseAlarmSum = 0.0;
    uint32_t nonTargetCount = 0;
    uint32_t detectedNodes = 0;
    uint32_t falseAlarmNodes = 0;
    uint32_t randomFalseAlarmNodes = 0;
    std::vector<double> detectionValues;
    std::vector<double> falseAlarmValues;
    detectionValues.reserve(nodeScores.size());
    falseAlarmValues.reserve(nodeScores.size());
    for (const auto& item : nodeScores) {
        detectionSum += item.detectionScore;
        falseAlarmSum += item.falseAlarmProbability;
        detectionValues.push_back(item.detectionScore);
        falseAlarmValues.push_back(item.falseAlarmProbability);
        if (item.detectionScore >= detectionAlertThreshold) detectedNodes++;
        if (!item.isTarget) {
            nonTargetCount++;
            nonTargetFalseAlarmSum += item.falseAlarmProbability;
            if (item.falseAlarmProbability >= 0.15) falseAlarmNodes++;
            if (item.isFalsePositive && item.falseAlarmProbability >= 0.15) {
                randomFalseAlarmNodes++;
            }
        }
    }
    std::sort(detectionValues.begin(), detectionValues.end());
    std::sort(falseAlarmValues.begin(), falseAlarmValues.end());
    auto pctDouble = [](const std::vector<double>& values, double q) -> double {
        if (values.empty()) return 0.0;
        size_t idx = static_cast<size_t>(q * (values.size() - 1));
        return values[idx];
    };
    double meanDetection = nodeScores.empty()
                                 ? 0.0
                                 : detectionSum / static_cast<double>(nodeScores.size());
    double meanFalseAlarm = nodeScores.empty()
                                ? 0.0
                                : falseAlarmSum / static_cast<double>(nodeScores.size());
    double meanNonTargetFalseAlarm = nonTargetCount
                                         ? nonTargetFalseAlarmSum /
                                               static_cast<double>(nonTargetCount)
                                         : 0.0;

    LogM("Scenario1Config") << "Local clue search result:\n";
    LogM("Scenario1Config") << "  targetNode=" << m_cluePlan.targetNodeId
                            << " targetCell=" << targetCellId
                            << " nodeRank=" << targetNodeRank << "/" << nodeScores.size()
                            << " nodeScore=" << std::fixed << std::setprecision(3)
                            << targetNodeScore
                            << " detection=" << targetDetectionScore
                            << " cellRank=" << targetCellRank << "/" << cellScores.size()
                            << " cellScore=" << targetCellScore << "\n";
    LogM("Scenario1Config") << "  detection score (" << DetectionModelName()
                            << "): mean=" << meanDetection
                            << " median=" << pctDouble(detectionValues, 0.50)
                            << " p90=" << pctDouble(detectionValues, 0.90)
                            << " nodes>=threshold=" << detectedNodes << "/"
                            << nodeScores.size() << "\n";
    LogM("Scenario1Config") << "  false alarm probability: mean=" << meanFalseAlarm
                            << " nonTargetMean=" << meanNonTargetFalseAlarm
                            << " median=" << pctDouble(falseAlarmValues, 0.50)
                            << " p90=" << pctDouble(falseAlarmValues, 0.90)
                            << " nonTarget>=0.15=" << falseAlarmNodes << "/"
                            << nonTargetCount
                            << " randomFalsePositive>=0.15="
                            << randomFalseAlarmNodes << "\n";
    LogM("Scenario1Config") << "  top nodes:";
    for (uint32_t i = 0; i < nodeScores.size() && i < 8; i++) {
        const auto& item = nodeScores[i];
        LogM("Scenario1Config") << " node " << item.nodeId
                                << "[cell=" << item.cellId
                                << ",score=" << std::fixed << std::setprecision(3)
                                << item.score
                                << ",det=" << item.detectionScore
                                << ",false=" << item.falseAlarmProbability
                                << ",q=" << item.clueQuality
                                << ",frag=" << item.fragmentRatio
                                << (item.isTarget ? ",target" : "")
                                << (item.isFalsePositive ? ",fp" : "")
                                << "]";
    }
    LogM("Scenario1Config") << "\n";
    LogM("Scenario1Config") << "  top cells:";
    for (uint32_t i = 0; i < cellScores.size() && i < 6; i++) {
        const auto& cell = cellScores[i];
        LogM("Scenario1Config") << " cell " << cell.cellId
                                << "[score=" << std::fixed << std::setprecision(3)
                                << cell.score
                                << ",best=" << cell.bestNodeScore
                                << ",support=" << cell.meanTopSupport
                                << ",frag=" << cell.meanFragmentRatio
                                << ",nodes=" << cell.nodeCount
                                << (cell.hasTarget ? ",target" : "")
                                << "]";
    }
    LogM("Scenario1Config") << "\n\n";

    LogM("Scenario1Config") << "Per-ground-node L0 reception:\n";
    for (const auto& app : m_groundApps) {
        LogM("Scenario1Config") << "  node " << app->GetNodeId()
                                << ": direct=" << app->DirectUavFragmentCount()
                                << "/" << fragTotal
                                << " distinct=" << app->DistinctFragmentCount()
                                << "/" << fragTotal
                                << " coopGain=" << app->CoopFragmentsGained()
                                << "\n";
    }
    LogM("Scenario1Config") << "\n";

    // Flush remaining buffered bytes to disk so the log is complete on exit.
    LogFlush();
}

}  // namespace ns3::wsn::uav
