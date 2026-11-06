#include "basestation-app.h"
#include "../common/log.h"

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"

#include <algorithm>
#include <cstring>
#include <vector>

using namespace ns3;

namespace ns3::wsn::uav {

namespace {
constexpr uint8_t APP_MSG_TOPOLOGY_FRAGMENT = 0x01;
constexpr uint8_t APP_MSG_TOPOLOGY_ACK      = 0x02;
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

    // Broadcast topology info to UAV at startup
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

        Simulator::Schedule(Seconds(STAGGER_S * pktIdx),
                            &BaseStationApp::SendOneTopologyPacket,
                            this, std::move(buf), pktIdx, numPackets);
    }
    LogT("BS") << "topology dispatch scheduled: " << numPackets << " packets, "
               << totalCount << " nodes total";
}

void BaseStationApp::SendOneTopologyPacket(std::vector<uint8_t> buf,
                                           uint32_t pktIdx,
                                           uint32_t numPackets) {
    if (!m_device || m_uavNode.GetN() == 0) return;
    Ptr<NetDevice> uavDev = m_uavNode.Get(0)->GetDevice(0);
    Address uavAddr = uavDev->GetAddress();
    Ptr<Packet> pkt = Create<Packet>(buf.data(), buf.size());
    bool sent = m_device->Send(pkt, uavAddr, 0x00);
    LogT("BS") << "send topology[" << pktIdx + 1 << "/" << numPackets
               << "] size=" << buf.size() << "B sent=" << (sent ? "OK" : "FAIL");
}

bool BaseStationApp::OnMessageReceived(ns3::Ptr<ns3::NetDevice> dev,
                                       ns3::Ptr<const ns3::Packet> pkt,
                                       uint16_t proto,
                                       const ns3::Address& from) {
    (void)dev;
    (void)proto;
    (void)from;

    uint32_t pktSize = pkt->GetSize();
    constexpr uint32_t ACK_SIZE = 1 + 1 + 2 + 2 + 1;
    if (pktSize < 1) {
        LogT("BS") << "RX packet (size=0B, missing msgType)";
        return true;
    }

    std::vector<uint8_t> buf(pktSize);
    pkt->CopyData(buf.data(), pktSize);
    const uint8_t* p = buf.data();
    uint8_t msgType = *p++;

    if (msgType != APP_MSG_TOPOLOGY_ACK) {
        LogT("BS") << "RX packet (size=" << pktSize << "B, msgType="
                   << static_cast<uint32_t>(msgType) << ", unsupported)";
        return true;
    }

    if (pktSize != ACK_SIZE) {
        LogT("BS") << "RX topology ACK (size=" << pktSize
                   << "B, expected " << ACK_SIZE << "B)";
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

    LogT("BS") << "RX topology ACK receivedSensors=" << receivedSensors
               << " totalSensors=" << totalSensors
               << " complete=" << (complete ? "true" : "false");
    return true;
}

}  // namespace ns3::wsn::uav
