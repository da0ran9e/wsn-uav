#include "basestation-app.h"
#include "../common/log.h"

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"

#include <algorithm>
#include <cstring>
#include <limits>
#include <vector>

using namespace ns3;

namespace ns3::wsn::uav {

namespace {
constexpr uint8_t APP_MSG_TOPOLOGY_FRAGMENT = 0x01;
constexpr uint8_t APP_MSG_TOPOLOGY_ACK      = 0x02;
constexpr uint8_t APP_MSG_DATA_FRAGMENT     = 0x03;
constexpr uint8_t APP_MSG_DATA_ACK          = 0x04;
constexpr uint8_t APP_MSG_L0_DATA           = 0x05;
constexpr uint8_t APP_MSG_L0_SEMANTIC       = 0x06;
constexpr uint8_t APP_MSG_FULL_UNICAST      = 0x07;
}  // namespace

NS_OBJECT_ENSURE_REGISTERED(BaseStationApp);

TypeId BaseStationApp::GetTypeId() {
    static TypeId tid =
        TypeId("ns3::wsn::uav::BaseStationApp")
            .SetParent<Application>()
            .SetGroupName("wsn-uav")
            .AddConstructor<BaseStationApp>();
    return tid;
}

BaseStationApp::BaseStationApp() : m_nodeId(0) {
}

BaseStationApp::~BaseStationApp() {
}

void BaseStationApp::SetNodeId(uint32_t id) {
    m_nodeId = id;
}

void BaseStationApp::SetNetDevice(Ptr<NetDevice> dev) {
    m_device = dev;
}

void BaseStationApp::StartApplication() {
    LogT("BS") << "started";

    m_profile = TargetProfile::Generate();
    LogT("BS") << "target profile: " << m_profile.Size() << " fragments, "
               << m_profile.TotalBytes() << "B (L0="
               << m_profile.LayerCount(SemanticLayer::IDENTITY_CUE) << " L1="
               << m_profile.LayerCount(SemanticLayer::SEMANTIC_DESCRIPTOR) << " L2="
               << m_profile.LayerCount(SemanticLayer::LOCAL_DETAIL) << " L3="
               << m_profile.LayerCount(SemanticLayer::FULL_REFERENCE) << ")";

    // Phase 1: topology first, fragment data right after (chained inside
    // BroadcastTopology once the topology packet count is known).
    Simulator::Schedule(Seconds(0.1), &BaseStationApp::BroadcastTopology, this);
}

void BaseStationApp::StopApplication() {
    LogT("BS") << "stopped";
}

void BaseStationApp::BroadcastTopology() {
    // Topology is fragmented over multiple LR-WPAN packets to respect the
    // 127B MTU. Per-packet header (7B): [msgType:u8][destId:u8]
    // [totalNodeCount:u16][thisPacketCount:u8][startIdx:u16].
    // Entry (7B): [id:u8, x/y/z:i16_dm].
    if (m_uavNode.GetN() == 0 || !m_device) return;
    // LR-WPAN PSDU=127B includes MAC header (~13B) + FCS (2B) → app payload
    // effectively ~100B. Use 100B as the safe ceiling.
    constexpr uint32_t MAX_PAYLOAD = 100;
    constexpr uint32_t HDR         = 1 + 1 + 2 + 1 + 2;     // 7B
    constexpr uint32_t ENTRY       = 1 + 6;             // 7B
    constexpr uint32_t MAX_ENTRIES = (MAX_PAYLOAD - HDR) / ENTRY;  // 13

    uint8_t destId = static_cast<uint8_t>(m_uavNode.Get(0)->GetId());
    uint32_t totalCount = m_sensorNodes.GetN() + 2;     // BS + UAV + sensors

    // Build the full ordered list once (BS, UAV, sensors).
    struct Entry { uint32_t id; Vector pos; };
    std::vector<Entry> entries;
    entries.reserve(totalCount);

    Ptr<MobilityModel> bsMob = GetNode()->GetObject<MobilityModel>();
    entries.push_back({GetNode()->GetId(), bsMob ? bsMob->GetPosition() : Vector(0,0,0)});

    Ptr<Node> uavNode = m_uavNode.Get(0);
    Ptr<MobilityModel> uavMob = uavNode->GetObject<MobilityModel>();
    entries.push_back({uavNode->GetId(), uavMob ? uavMob->GetPosition() : Vector(0,0,0)});

    for (uint32_t i = 0; i < m_sensorNodes.GetN(); i++) {
        Ptr<Node> node = m_sensorNodes.Get(i);
        Ptr<MobilityModel> mob = node->GetObject<MobilityModel>();
        entries.push_back({node->GetId(), mob ? mob->GetPosition() : Vector(0,0,0)});
    }

    uint32_t numPackets = (totalCount + MAX_ENTRIES - 1) / MAX_ENTRIES;
    constexpr double STAGGER_S = 0.2;   // 200 ms between back-to-back packets

    m_topologyPackets.clear();
    m_topologyTransferComplete = false;
    m_topologyPackets.reserve(numPackets);
    for (uint32_t pktIdx = 0; pktIdx < numPackets; pktIdx++) {
        uint32_t startIdx = pktIdx * MAX_ENTRIES;
        uint32_t thisCount = std::min<uint32_t>(MAX_ENTRIES, totalCount - startIdx);
        uint32_t pktSize = HDR + thisCount * ENTRY;
        std::vector<uint8_t> buf(pktSize);
        uint8_t* p = buf.data();
        *p++ = APP_MSG_TOPOLOGY_FRAGMENT;
        *p++ = destId;
        uint16_t tc = static_cast<uint16_t>(totalCount);
        std::memcpy(p, &tc, 2); p += 2;
        *p++ = static_cast<uint8_t>(thisCount);
        uint16_t si = static_cast<uint16_t>(startIdx);
        std::memcpy(p, &si, 2); p += 2;

        for (uint32_t i = 0; i < thisCount; i++) {
            const Entry& e = entries[startIdx + i];
            *p++ = static_cast<uint8_t>(e.id);
            int16_t x = static_cast<int16_t>(e.pos.x * 10);
            int16_t y = static_cast<int16_t>(e.pos.y * 10);
            int16_t z = static_cast<int16_t>(e.pos.z * 10);
            std::memcpy(p, &x, 2); p += 2;
            std::memcpy(p, &y, 2); p += 2;
            std::memcpy(p, &z, 2); p += 2;
        }

        m_topologyPackets.push_back(std::move(buf));
        Simulator::Schedule(Seconds(STAGGER_S * pktIdx),
                            &BaseStationApp::SendOneTopologyPacket,
                            this, pktIdx, false);
    }
    Simulator::Schedule(Seconds(STAGGER_S * numPackets + 1.0),
                        &BaseStationApp::ScheduleTopologyRetransmissionPass, this);
    LogT("BS") << "topology dispatch scheduled: " << numPackets << " packets, "
               << totalCount << " nodes total";

    // Chain fragment-data dispatch right after the last topology packet.
    Simulator::Schedule(Seconds(STAGGER_S * numPackets + STAGGER_S),
                        &BaseStationApp::DispatchFragmentData, this);
}

void BaseStationApp::DispatchFragmentData() {
    if (!m_device || m_uavNode.GetN() == 0) return;

    // Data packet header (16B):
    // [msgType:u8][destId:u8][numFragments:u8][fragId:u8][fragLayer:u8]
    // [utilityMilli:u16][fragTotalBytes:u32][chunkOffset:u32][chunkLen:u8]
    constexpr uint32_t MAX_PAYLOAD = 100;
    constexpr uint32_t DHDR  = 1 + 1 + 1 + 1 + 1 + 2 + 4 + 4 + 1;  // 16B
    constexpr uint32_t CHUNK = MAX_PAYLOAD - DHDR;                 // 84B
    constexpr double   STAGGER_S = 0.2;

    uint8_t destId = static_cast<uint8_t>(m_uavNode.Get(0)->GetId());
    const std::vector<Fragment>& frags = m_profile.All();
    NS_ABORT_MSG_IF(
        frags.size() > std::numeric_limits<uint8_t>::max(),
        "BaseStationApp DATA_FRAGMENT wire format supports at most 255 fragments; "
        "update UAV/BS together before increasing the fragment count.");
    uint8_t numFragments = static_cast<uint8_t>(frags.size());

    // Every fragment's data volume is split into MTU-sized chunks. Fragment
    // metadata rides in each packet header, so any chunk self-identifies.
    m_dataPackets.clear();
    m_dataTransferComplete = false;
    for (const Fragment& f : frags) {
        NS_ABORT_MSG_IF(
            f.id > std::numeric_limits<uint8_t>::max(),
            "BaseStationApp DATA_FRAGMENT wire format supports fragId <= 255; "
            "update UAV/BS together before sending larger fragment ids.");
        uint32_t total = f.sizeBytes;
        uint32_t off = 0;
        do {
            uint32_t len = std::min<uint32_t>(CHUNK, total - off);
            DataPacketRecord rec;
            rec.fragId = static_cast<uint16_t>(f.id);
            rec.chunkOffset = off;
            rec.buf.assign(DHDR + len, 0);  // payload region = filler
            std::vector<uint8_t>& buf = rec.buf;
            uint8_t* p = buf.data();
            *p++ = APP_MSG_DATA_FRAGMENT;
            *p++ = destId;
            *p++ = numFragments;
            *p++ = static_cast<uint8_t>(f.id);
            *p++ = static_cast<uint8_t>(f.layer);
            uint16_t um = static_cast<uint16_t>(f.utility * 1000.0 + 0.5);
            std::memcpy(p, &um, 2);    p += 2;
            std::memcpy(p, &total, 4); p += 4;
            std::memcpy(p, &off, 4);   p += 4;
            *p++ = static_cast<uint8_t>(len);
            m_dataPackets.push_back(std::move(rec));
            off += len;
        } while (off < total);
    }

    uint32_t numPackets = m_dataPackets.size();
    for (uint32_t i = 0; i < numPackets; i++) {
        Simulator::Schedule(Seconds(STAGGER_S * i),
                            &BaseStationApp::SendOneDataPacket,
                            this, i, false);
    }
    Simulator::Schedule(Seconds(STAGGER_S * numPackets + 1.0),
                        &BaseStationApp::ScheduleDataRetransmissionPass, this);
    LogT("BS") << "fragment data dispatch scheduled: " << numPackets
               << " packets, " << static_cast<uint32_t>(numFragments)
               << " fragments, " << m_profile.TotalBytes() << "B total";
}

void BaseStationApp::SendOneDataPacket(uint32_t pktIdx, bool retransmission) {
    if (!m_device || m_uavNode.GetN() == 0) return;
    if (pktIdx >= m_dataPackets.size()) return;
    if (retransmission && m_dataPackets[pktIdx].acked) return;

    Ptr<NetDevice> uavDev = m_uavNode.Get(0)->GetDevice(0);
    Address uavAddr = uavDev->GetAddress();
    const std::vector<uint8_t>& buf = m_dataPackets[pktIdx].buf;
    Ptr<Packet> pkt = Create<Packet>(buf.data(), buf.size());
    bool sent = m_device->Send(pkt, uavAddr, 0x00);
    if (!sent) {
        LogT("BS") << "send data[" << pktIdx + 1 << "/" << m_dataPackets.size()
                   << "]" << (retransmission ? " retransmit" : "") << " FAILED";
    }
}

void BaseStationApp::ScheduleDataRetransmissionPass() {
    if (m_dataTransferComplete || m_dataPackets.empty()) return;

    constexpr double STAGGER_S = 0.2;
    uint32_t missing = 0;
    for (uint32_t i = 0; i < m_dataPackets.size(); i++) {
        if (m_dataPackets[i].acked) continue;
        Simulator::Schedule(Seconds(STAGGER_S * missing),
                            &BaseStationApp::SendOneDataPacket,
                            this, i, true);
        missing++;
    }
    if (missing > 0) {
        LogT("BS") << "data ARQ retransmission pass scheduled: "
                   << missing << " unacked chunks";
        Simulator::Schedule(Seconds(STAGGER_S * missing + 1.0),
                            &BaseStationApp::ScheduleDataRetransmissionPass, this);
    }
}

void BaseStationApp::SendOneTopologyPacket(uint32_t pktIdx, bool retransmission) {
    if (!m_device || m_uavNode.GetN() == 0) return;
    if (pktIdx >= m_topologyPackets.size()) return;
    if (retransmission && m_topologyTransferComplete) return;

    Ptr<NetDevice> uavDev = m_uavNode.Get(0)->GetDevice(0);
    Address uavAddr = uavDev->GetAddress();
    const std::vector<uint8_t>& buf = m_topologyPackets[pktIdx];
    Ptr<Packet> pkt = Create<Packet>(buf.data(), buf.size());
    bool sent = m_device->Send(pkt, uavAddr, 0x00);
    if (!sent) {
        LogT("BS") << "send topology[" << pktIdx + 1 << "/" << m_topologyPackets.size()
                   << "]" << (retransmission ? " retransmit" : "") << " FAILED";
    }
}

void BaseStationApp::ScheduleTopologyRetransmissionPass() {
    if (m_topologyTransferComplete || m_topologyPackets.empty()) return;

    constexpr double STAGGER_S = 0.2;
    for (uint32_t i = 0; i < m_topologyPackets.size(); i++) {
        Simulator::Schedule(Seconds(STAGGER_S * i),
                            &BaseStationApp::SendOneTopologyPacket,
                            this, i, true);
    }
    LogT("BS") << "topology ARQ retransmission pass scheduled: "
               << m_topologyPackets.size() << " packets";
    Simulator::Schedule(Seconds(STAGGER_S * m_topologyPackets.size() + 1.0),
                        &BaseStationApp::ScheduleTopologyRetransmissionPass, this);
}

bool BaseStationApp::OnMessageReceived(ns3::Ptr<ns3::NetDevice> dev,
                                       ns3::Ptr<const ns3::Packet> pkt,
                                       uint16_t proto,
                                       const ns3::Address& from) {
    (void)dev;
    (void)proto;
    (void)from;

    uint32_t pktSize = pkt->GetSize();
    constexpr uint32_t TOPO_ACK_SIZE = 1 + 1 + 2 + 2 + 1;
    constexpr uint32_t DATA_ACK_SIZE = 1 + 1 + 2 + 4 + 2 + 2 + 2 + 1;
    if (pktSize < 1) {
        LogT("BS") << "RX packet (size=0B, missing msgType)";
        return true;
    }

    std::vector<uint8_t> buf(pktSize);
    pkt->CopyData(buf.data(), pktSize);
    const uint8_t* p = buf.data();
    uint8_t msgType = *p++;

    if (msgType == APP_MSG_L0_DATA || msgType == APP_MSG_L0_SEMANTIC ||
        msgType == APP_MSG_FULL_UNICAST) {
        return true;  // UAV search dissemination — not addressed to the BS
    }

    if (msgType == APP_MSG_DATA_ACK) {
        if (pktSize != DATA_ACK_SIZE) {
            LogT("BS") << "RX data ACK (size=" << pktSize << "B, expected "
                       << DATA_ACK_SIZE << "B)";
            return true;
        }
        uint8_t destId = *p++;
        if (destId != m_nodeId) {
            LogT("BS") << "drop data ACK (destId=" << static_cast<uint32_t>(destId)
                       << " not me)";
            return true;
        }
        uint16_t fragId = 0;
        uint32_t chunkOffset = 0;
        uint16_t chunkLen = 0;
        uint16_t fragsComplete = 0;
        uint16_t fragsTotal = 0;
        std::memcpy(&fragId, p, 2);         p += 2;
        std::memcpy(&chunkOffset, p, 4);    p += 4;
        std::memcpy(&chunkLen, p, 2);       p += 2;
        std::memcpy(&fragsComplete, p, 2); p += 2;
        std::memcpy(&fragsTotal, p, 2);     p += 2;
        bool complete = (*p != 0);
        for (DataPacketRecord& rec : m_dataPackets) {
            if (rec.fragId == fragId && rec.chunkOffset == chunkOffset) {
                rec.acked = true;
                break;
            }
        }
        if (complete) {
            m_dataTransferComplete = true;
            LogT("BS") << "RX data ACK fragmentsComplete=" << fragsComplete
                       << "/" << fragsTotal << " complete=true";
        }
        (void)fragId; (void)chunkOffset; (void)chunkLen;
        return true;
    }

    if (msgType != APP_MSG_TOPOLOGY_ACK) {
        LogT("BS") << "RX packet (size=" << pktSize << "B, msgType="
                   << static_cast<uint32_t>(msgType) << ", unsupported)";
        return true;
    }

    if (pktSize != TOPO_ACK_SIZE) {
        LogT("BS") << "RX topology ACK (size=" << pktSize
                   << "B, expected " << TOPO_ACK_SIZE << "B)";
        return true;
    }

    uint8_t destId = *p++;
    if (destId != m_nodeId) {
        LogT("BS") << "drop topology ACK (destId=" << static_cast<uint32_t>(destId)
                   << " not me=" << m_nodeId << ")";
        return true;
    }

    uint16_t receivedSensors = 0;
    uint16_t totalSensors = 0;
    std::memcpy(&receivedSensors, p, 2); p += 2;
    std::memcpy(&totalSensors, p, 2); p += 2;
    bool complete = (*p != 0);

    if (complete) {
        m_topologyTransferComplete = true;
        LogT("BS") << "RX topology ACK receivedSensors=" << receivedSensors
                   << "/" << totalSensors << " complete=true";
    }
    return true;
}

}  // namespace ns3::wsn::uav
