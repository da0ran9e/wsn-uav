#include "fragment-dissemination-app.h"
#include "ns3/simulator.h"
#include "ns3/log.h"
#include "ns3/node.h"
#include "ns3/mobility-model.h"
#include "ns3/random-variable-stream.h"
#include "../common/parameters.h"

NS_LOG_COMPONENT_DEFINE("FragmentDisseminationApp");

namespace ns3 {
namespace wsn {
namespace uav {

NS_OBJECT_ENSURE_REGISTERED(FragmentDisseminationApp);

TypeId FragmentDisseminationApp::GetTypeId() {
    static TypeId tid = TypeId("ns3::wsn::uav::FragmentDisseminationApp")
        .SetParent<Application>()
        .SetGroupName("WsnUav")
        .AddConstructor<FragmentDisseminationApp>();
    return tid;
}

FragmentDisseminationApp::FragmentDisseminationApp()
    : m_confidenceModel(0, 10) {}

FragmentDisseminationApp::~FragmentDisseminationApp() {}

void FragmentDisseminationApp::SetRole(Role role) {
    m_role = role;
}

void FragmentDisseminationApp::SetNodeId(uint32_t id) {
    m_nodeId = id;
    m_confidenceModel = ConfidenceModel(id, m_expectedFragmentCount);
}

void FragmentDisseminationApp::SetFragments(const FragmentCollection& frags) {
    m_allFragments = frags;
}

void FragmentDisseminationApp::SetExpectedFragmentCount(uint32_t count) {
    m_expectedFragmentCount = count;
    m_confidenceModel = ConfidenceModel(m_nodeId, count);
}

void FragmentDisseminationApp::SetDetectionNodeId(uint32_t id) {
    m_detectionNodeId = id;
}

void FragmentDisseminationApp::SetThresholds(double cooperationThreshold, double alertThreshold) {
    m_cooperationThreshold = cooperationThreshold;
    m_alertThreshold = alertThreshold;
}

void FragmentDisseminationApp::SetBfsLevel(uint32_t level) {
    m_bfsLevel = level;
}

void FragmentDisseminationApp::SetGroundNodeCount(uint32_t count) {
    m_groundNodeCount = count;
}

void FragmentDisseminationApp::SetAssignedUavRegion(uint32_t uavId) {
    m_assignedUavRegion = uavId;
}

void FragmentDisseminationApp::SetStatisticsCollector(Ptr<StatisticsCollector> stats) {
    m_stats = stats;
}

void FragmentDisseminationApp::SetDetectionCallback(DetectionCallback cb) {
    m_detectionCb = cb;
}

void FragmentDisseminationApp::SetPacketDroppedCallback(PacketDroppedCallback cb) {
    m_droppedCb = cb;
}

void FragmentDisseminationApp::SetNetDevice(Ptr<NetDevice> device) {
    m_device = device;
}

double FragmentDisseminationApp::GetConfidence() const {
    return m_confidenceModel.GetConfidence();
}

bool FragmentDisseminationApp::IsDetected() const {
    return m_detected;
}

const ConfidenceModel& FragmentDisseminationApp::GetConfidenceModel() const {
    return m_confidenceModel;
}

void FragmentDisseminationApp::StartApplication() {
    if (m_role == Role::UAV_BROADCASTER) {
        NS_LOG_INFO("Node " << m_nodeId << ": UAV starting broadcast");
        m_broadcastEvent = Simulator::Schedule(
            Seconds(params::FRAGMENT_BROADCAST_INTERVAL),
            &FragmentDisseminationApp::DoBroadcast, this);
    } else {
        NS_LOG_INFO("Node " << m_nodeId << ": Ground node started");
    }
}

void FragmentDisseminationApp::StopApplication() {
    Simulator::Cancel(m_broadcastEvent);
    Simulator::Cancel(m_cooperationEvent);
}

void FragmentDisseminationApp::DoBroadcast() {
    if (m_detected) {
        return;  // Mission complete
    }

    // Use actual fragment IDs from this node's fragment collection
    auto ids = m_allFragments.GetIds();
    if (ids.empty()) {
        return;  // No fragments to broadcast
    }

    uint32_t fragId = ids[m_nextFragmentIndex % ids.size()];
    SendFragment(fragId);
    m_nextFragmentIndex++;

    // Compute transmission time based on fragment size
    double txTime = params::FRAGMENT_BROADCAST_INTERVAL;  // fallback
    const Fragment* frag = m_allFragments.Get(fragId);
    if (frag && frag->sizeBytes > 0) {
        // txTime = (sizeBytes * 8 bits) / DATA_RATE_BPS
        txTime = (frag->sizeBytes * 8.0) / params::DATA_RATE_BPS;
    }

    m_broadcastEvent = Simulator::Schedule(
        Seconds(txTime),
        &FragmentDisseminationApp::DoBroadcast, this);
}

void FragmentDisseminationApp::SendFragment(uint32_t fragmentId) {
    const Fragment* frag = m_allFragments.Get(fragmentId);
    if (!frag) {
        NS_LOG_WARN("Node " << m_nodeId << ": fragment " << fragmentId << " not found");
        return;
    }

    // Build packet with headers
    Ptr<Packet> p = Create<Packet>();

    FragmentPacket fragHeader;
    fragHeader.SetFragmentId(fragmentId);
    fragHeader.SetConfidence(frag->evidence);
    fragHeader.SetSourceId(m_nodeId);

    PacketHeader baseHeader;
    baseHeader.SetType(PACKET_TYPE_FRAGMENT);

    p->AddHeader(fragHeader);
    p->AddHeader(baseHeader);

    // Record sent packet with broadcast destination marker (0xFFFFFFFF)
    // Needed to capture source position for reception records
    // Will be filtered out during visualization export
    if (m_stats) {
        // Get current node position
        Vector nodePos(0, 0, 0);
        auto node = GetNode();
        if (node) {
            auto mob = node->GetObject<MobilityModel>();
            if (mob) {
                nodePos = mob->GetPosition();
            }
        }
        m_stats->RecordPacketSent(m_nodeId, 0xFFFFFFFF, fragmentId, nodePos);
    }

    // Send via NetDevice (MAC layer handles propagation + delivery)
    if (m_device) {
        m_device->Send(p, Mac16Address("FF:FF"), 0);  // Broadcast to all
        NS_LOG_DEBUG("Node " << m_nodeId << ": sent via device frag=" << fragmentId);
    } else {
        NS_LOG_WARN("Node " << m_nodeId << ": device is null!");
    }

    NS_LOG_INFO("Node " << m_nodeId << ": broadcast fragment " << fragmentId << " (conf=" << frag->evidence << ")");
}

void FragmentDisseminationApp::OnPacketReceived(Ptr<const Packet> pkt, double rssiDbm) {
    if (!pkt) return;

    Ptr<Packet> copy = pkt->Copy();

    // Extract base header to determine packet type
    PacketHeader baseHeader;
    if (copy->RemoveHeader(baseHeader) == 0) {
        NS_LOG_WARN("Node " << m_nodeId << ": malformed packet (no base header)");
        return;
    }

    if (baseHeader.GetType() == PACKET_TYPE_FRAGMENT) {
        // Extract fragment header
        FragmentPacket fragHeader;
        if (copy->RemoveHeader(fragHeader) == 0) {
            NS_LOG_WARN("Node " << m_nodeId << ": malformed fragment packet");
            return;
        }

        // Determine if from UAV (source node ID >= groundNodeCount)
        uint32_t srcNodeId = fragHeader.GetSourceId();
        bool fromUav = (srcNodeId >= m_groundNodeCount);

        // DISABLED: Spatial filtering removed - all nodes accept fragments from all UAVs
        // This allows cooperative multi-UAV dissemination where:
        // - All UAVs broadcast all fragments
        // - UAVs with lighter fragments (smaller tx time) fly faster
        // - UAVs with heavier fragments (larger tx time) fly slower
        // - All work together to cover the entire network efficiently
        //
        // if (fromUav && m_assignedUavRegion < UINT32_MAX) {
        //     uint32_t srcUavId = srcNodeId - m_groundNodeCount;
        //     if (srcUavId != m_assignedUavRegion) {
        //         return;  // Reject packet from non-assigned UAV
        //     }
        // }

        // Reconstruct fragment object
        Fragment frag;
        frag.id = fragHeader.GetFragmentId();
        frag.evidence = fragHeader.GetConfidence();
        // frag.data can be extracted from payload if needed

        // Record successful packet reception (match broadcast sent record)
        if (m_stats) {
            // Try to match with a sent broadcast packet
            // If this is from UAV broadcast (srcNodeId >= 1000), match with 0xFFFFFFFF dest
            m_stats->RecordPacketReceived(srcNodeId, m_nodeId, frag.id, true, rssiDbm);
        }

        ProcessFragment(frag, fromUav);
    }
    else if (baseHeader.GetType() == PACKET_TYPE_COOPERATION) {
        // Extract cooperation header (manifest)
        CooperationPacket coop;
        if (copy->RemoveHeader(coop) == 0) {
            NS_LOG_WARN("Node " << m_nodeId << ": malformed cooperation packet");
            return;
        }

        uint32_t srcNodeId = coop.GetRequesterId();
        const auto& theirFragments = coop.GetAvailableFragments();

        NS_LOG_DEBUG("Node " << m_nodeId << ": received manifest from node " << srcNodeId
                     << " with " << theirFragments.size() << " fragments");

        // Convert to set for ProcessIncomingManifest
        std::set<uint32_t> theirFragSet(theirFragments.begin(), theirFragments.end());
        ProcessIncomingManifest(srcNodeId, theirFragSet);
    }
    else {
        NS_LOG_DEBUG("Node " << m_nodeId << ": ignoring unknown packet type " << baseHeader.GetType());
    }
}

void FragmentDisseminationApp::ProcessFragment(const Fragment& frag, bool fromUav) {
    // Update confidence
    bool changed = m_confidenceModel.OnFragment(frag, fromUav);
    
    if (!changed) return;  // Already had this fragment
    
    NS_LOG_INFO("Node " << m_nodeId << ": received fragment " << frag.id 
                << " (confidence=" << m_confidenceModel.GetConfidence() << ")");
    
    // Check detection condition (allow multiple nodes to trigger detection for statistics)
    if (!m_detected && m_confidenceModel.Above(m_alertThreshold)) {
        m_detected = true;
        NS_LOG_INFO("Node " << m_nodeId << ": DETECTION TRIGGERED at t=" 
                    << Simulator::Now().GetSeconds() << "s");
        
        if (!m_detectionCb.IsNull()) {
            m_detectionCb(m_nodeId, Simulator::Now().GetSeconds());
        }
        
        if (m_stats) {
            m_stats->RecordDetection(m_nodeId, Simulator::Now().GetSeconds());
        }
        
        // Do NOT stop the simulator here. Let it run to simTime to collect cooperation statistics.
    }

    // Phase 1: Enable cooperation for ground nodes
    // When confidence reaches threshold, nodes start sharing fragments with neighbors
    // This allows nodes from different clusters to combine fragments and achieve detection
    if (!m_coopScheduled && m_role == Role::GROUND_NODE) {
        m_coopScheduled = true;
        ScheduleCooperation(CoopTrigger::CONFIDENCE_REACHED);
    }
}

void FragmentDisseminationApp::ScheduleCooperation(CoopTrigger trigger) {
    if (m_confidenceModel.IsComplete()) {
        return;  // Already have all fragments
    }

    // Improved cooperation: much shorter delay, periodic execution
    // Earlier delay: 2-3x broadcastInterval instead of K*broadcastInterval
    Time baseDelay = Seconds(params::FRAGMENT_BROADCAST_INTERVAL * (2 + m_bfsLevel * 0.3));

    Ptr<UniformRandomVariable> rng = CreateObject<UniformRandomVariable>();
    Time jitterDelay = Seconds(rng->GetValue(0, 0.05));  // Reduced jitter

    Time totalDelay = baseDelay + jitterDelay;

    if (m_cooperationEvent.IsPending()) {
        Simulator::Cancel(m_cooperationEvent);
    }

    m_cooperationEvent = Simulator::Schedule(totalDelay,
                                             &FragmentDisseminationApp::DoCooperation, this);
}

void FragmentDisseminationApp::DoCooperation() {
    if (m_confidenceModel.IsComplete() || m_detected) {
        return;
    }

    NS_LOG_DEBUG("Node " << m_nodeId << ": initiating cooperation");
    SendManifest();

    // Reschedule more frequently (every 2-3 seconds instead of once)
    if (!m_confidenceModel.IsComplete()) {
        Ptr<UniformRandomVariable> rng = CreateObject<UniformRandomVariable>();
        Time nextDelay = Seconds(2.0 + rng->GetValue(0, 1.0));
        m_cooperationEvent = Simulator::Schedule(nextDelay,
                                                  &FragmentDisseminationApp::DoCooperation, this);
    }
}

void FragmentDisseminationApp::SendManifest() {
    // Send list of fragments we have to all neighbors (broadcast to cell)
    if (!m_device) {
        NS_LOG_WARN("Node " << m_nodeId << ": device is null, cannot send manifest");
        return;
    }

    // Get list of fragments we have
    const auto& frags = m_confidenceModel.GetFragments().All();
    std::vector<uint32_t> fragmentIds;
    for (const auto& pair : frags) {
        fragmentIds.push_back(pair.first);  // fragment ID
    }

    // Create manifest packet
    Ptr<Packet> p = Create<Packet>();

    CooperationPacket coop;
    coop.SetRequesterId(m_nodeId);
    coop.SetCellId(-1);  // Broadcast to all in range
    coop.SetAvailableFragments(fragmentIds);

    PacketHeader baseHeader;
    baseHeader.SetType(PACKET_TYPE_COOPERATION);

    p->AddHeader(coop);
    p->AddHeader(baseHeader);

    // Send via broadcast
    m_device->Send(p, Mac16Address("FF:FF"), 0);
    NS_LOG_DEBUG("Node " << m_nodeId << ": sent manifest with "
                 << fragmentIds.size() << " fragments");
}

void FragmentDisseminationApp::SendCooperationRequest(uint32_t dstNodeId,
                                                       const std::set<uint32_t>& requestedFrags) {
    // Send request for specific fragments to a neighbor
    if (!m_device) {
        NS_LOG_WARN("Node " << m_nodeId << ": device is null, cannot send request");
        return;
    }

    std::vector<uint32_t> fragIds(requestedFrags.begin(), requestedFrags.end());

    Ptr<Packet> p = Create<Packet>();

    CooperationPacket coop;
    coop.SetRequesterId(m_nodeId);
    coop.SetCellId(-1);
    coop.SetAvailableFragments(fragIds);  // Reuse field for requested fragments

    PacketHeader baseHeader;
    baseHeader.SetType(PACKET_TYPE_COOPERATION);

    p->AddHeader(coop);
    p->AddHeader(baseHeader);

    Mac16Address dstAddr((uint16_t)dstNodeId);
    m_device->Send(p, dstAddr, 0);
    NS_LOG_DEBUG("Node " << m_nodeId << ": sent cooperation request to node " << dstNodeId
                 << " for " << requestedFrags.size() << " fragments");
}

void FragmentDisseminationApp::ProcessIncomingManifest(uint32_t srcNodeId,
                                                       const std::set<uint32_t>& theirFragments) {
    // They have fragments theirFragments - send them what we have that they're missing
    const auto& ourFragments = m_confidenceModel.GetFragments().All();

    std::set<uint32_t> toSend;
    for (const auto& pair : ourFragments) {
        uint32_t fragId = pair.first;
        if (!theirFragments.count(fragId)) {
            toSend.insert(fragId);
        }
    }

    for (uint32_t fragId : toSend) {
        SendMissingFragmentTo(srcNodeId, fragId);
    }
}

void FragmentDisseminationApp::SendMissingFragmentTo(uint32_t dstNodeId, uint32_t fragmentId) {
    // Send fragment to specific node during cooperation
    if (!m_device) {
        NS_LOG_WARN("Node " << m_nodeId << ": device is null, cannot send fragment");
        return;
    }

    const Fragment* frag = m_allFragments.Get(fragmentId);
    if (!frag) {
        NS_LOG_WARN("Node " << m_nodeId << ": fragment " << fragmentId << " not found");
        return;
    }

    // Create packet with fragment header
    Ptr<Packet> p = Create<Packet>();

    FragmentPacket fragHeader;
    fragHeader.SetFragmentId(fragmentId);
    fragHeader.SetConfidence(frag->evidence);
    fragHeader.SetSourceId(m_nodeId);

    PacketHeader baseHeader;
    baseHeader.SetType(PACKET_TYPE_FRAGMENT);

    p->AddHeader(fragHeader);
    p->AddHeader(baseHeader);

    // Convert dstNodeId to MAC address (simple mapping: node 0 -> 0x0000, etc.)
    Mac16Address dstAddr((uint16_t)dstNodeId);

    // Record sent packet for statistics
    if (m_stats) {
        Vector nodePos(0, 0, 0);
        auto node = GetNode();
        if (node) {
            auto mob = node->GetObject<MobilityModel>();
            if (mob) {
                nodePos = mob->GetPosition();
            }
        }
        m_stats->RecordPacketSent(m_nodeId, dstNodeId, fragmentId, nodePos);
    }

    // Send via NetDevice
    if (m_device) {
        m_device->Send(p, dstAddr, 0);
        NS_LOG_DEBUG("Node " << m_nodeId << ": sent fragment " << fragmentId
                     << " to node " << dstNodeId);
    }
}


}  // namespace uav
}  // namespace wsn
}  // namespace ns3
