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
    
    uint32_t fragId = m_nextFragmentIndex % m_expectedFragmentCount;
    SendFragment(fragId);
    
    m_nextFragmentIndex++;
    
    m_broadcastEvent = Simulator::Schedule(
        Seconds(params::FRAGMENT_BROADCAST_INTERVAL),
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
    
    // Check detection condition
    if (m_nodeId == m_detectionNodeId && m_confidenceModel.Above(m_alertThreshold)) {
        m_detected = true;
        NS_LOG_INFO("Node " << m_nodeId << ": DETECTION TRIGGERED at t=" 
                    << Simulator::Now().GetSeconds() << "s");
        
        if (!m_detectionCb.IsNull()) {
            m_detectionCb(m_nodeId, Simulator::Now().GetSeconds());
        }
        
        if (m_stats) {
            m_stats->RecordDetection(m_nodeId, Simulator::Now().GetSeconds());
        }
        
        Simulator::Stop(Seconds(1.0));
        return;
    }
    
    // Schedule cooperation if first fragment and not complete
    if (!m_coopScheduled && m_role == Role::GROUND_NODE) {
        m_coopScheduled = true;
        ScheduleCooperation(CoopTrigger::CONFIDENCE_REACHED);
    }
}

void FragmentDisseminationApp::ScheduleCooperation(CoopTrigger trigger) {
    if (m_confidenceModel.IsComplete()) {
        return;  // Already have all fragments
    }
    
    // Cooperation delay: K * broadcastInterval + 0.5s + bfsLevel * stagger + jitter
    Time baseDelay = Seconds(m_expectedFragmentCount * params::FRAGMENT_BROADCAST_INTERVAL + 0.5);
    Time bfsDelay = Seconds(m_bfsLevel * params::COOPERATION_STAGGER_STEP);
    
    Ptr<UniformRandomVariable> rng = CreateObject<UniformRandomVariable>();
    Time jitterDelay = Seconds(rng->GetValue(0, params::COOPERATION_JITTER_MAX));
    
    Time totalDelay = baseDelay + bfsDelay + jitterDelay;
    
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
    
    // Reschedule if still incomplete
    if (!m_confidenceModel.IsComplete()) {
        ScheduleCooperation(CoopTrigger::CONTACT_ENDED);
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

void FragmentDisseminationApp::ProcessIncomingManifest(uint32_t srcNodeId,
                                                       const std::set<uint32_t>& theirFragments) {
    // They have fragments theirFragments - send them what they're missing
    auto ourMissing = m_confidenceModel.GetMissingIds();
    
    std::set<uint32_t> toSend;
    for (uint32_t fragId : ourMissing) {
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
