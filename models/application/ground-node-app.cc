#include "ground-node-app.h"
#include "../common/semantic-fragment.h"
#include "../common/log.h"

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mac16-address.h"

#include <algorithm>
#include <cmath>
#include <cstring>
#include <iomanip>

using namespace ns3;

namespace ns3::wsn::uav {

NS_OBJECT_ENSURE_REGISTERED(GroundNodeApp);

TypeId GroundNodeApp::GetTypeId() {
    static TypeId tid = TypeId("ns3::wsn::uav::GroundNodeApp")
                            .SetParent<Application>()
                            .SetGroupName("wsn-uav")
                            .AddConstructor<GroundNodeApp>();
    return tid;
}

GroundNodeApp::GroundNodeApp() : m_nodeId(0) {
}

GroundNodeApp::~GroundNodeApp() {
}

void GroundNodeApp::SetNodeId(uint32_t id) {
    m_nodeId = id;
}

void GroundNodeApp::SetNetDevice(Ptr<NetDevice> dev) {
    m_device = dev;
}

void GroundNodeApp::SetCellRoutingInfo(const CellRoutingInfo& info) {
    m_cellInfo = info;
    m_hasCellInfo = true;
}

void GroundNodeApp::SetLocalClueInfo(const LocalClueInfo& info) {
    m_clueInfo = info;
    m_hasClueInfo = true;
}

static std::string GroundLabel(uint32_t id) {
    return "ground-node[" + std::to_string(id) + "]";
}

void GroundNodeApp::StartApplication() {
    LogT(GroundLabel(m_nodeId)) << "started";
    // Ground-ground beacon temporarily disabled - current focus is UAV flight.
    // SendBeacon() is kept intact below; re-enable by uncommenting this call.
    // SendBeacon();
}

void GroundNodeApp::StopApplication() {
    LogT(GroundLabel(m_nodeId)) << "stopped";
}

void GroundNodeApp::SendBeacon() {
    uint32_t beaconPayload = m_nodeId;
    Ptr<Packet> pkt = Create<Packet>((const uint8_t*)&beaconPayload, sizeof(uint32_t));

    Mac16Address broadcast("ff:ff");
    bool success = m_device->Send(pkt, broadcast, 0x00);

    LogT(GroundLabel(m_nodeId)) << "TX beacon (size=" << pkt->GetSize() << "B) "
                                 << (success ? "[OK]" : "[FAIL]");
}

uint32_t GroundNodeApp::MergeCoopFragments(const std::set<uint16_t>& fragments) {
    uint32_t gained = 0;
    for (uint16_t fragId : fragments) {
        auto [_, inserted] = m_distinctFragments.insert(fragId);
        if (inserted) {
            gained++;
        }
    }
    if (gained > 0) {
        m_coopFragmentsGained += gained;
        m_coopMergeRounds++;
    }
    return gained;
}

bool GroundNodeApp::OnReceive(Ptr<NetDevice> dev,
                              Ptr<const Packet> pkt,
                              uint16_t proto,
                              const Address& from) {
    // Layer-0 packets emitted by the UAV:
    //   msgType 5 = L0_DATA broadcast
    //   msgType 6 = L0_SEMANTIC broadcast
    //   msgType 7 = FULL_UNICAST baseline data chunk
    //   semantic (100B): [msgType=6][fragId:u16][semanticType:u8][filler]
    //   data sub-pkt  : [msgType=5/7][fragId:u16][subIdx:u8][subTotal:u8][filler]
    // A fragment is counted as received only when every data sub-packet of
    // that fragId arrives. The semantic preamble is counted separately.
    (void)dev;
    (void)proto;
    (void)from;
    uint32_t sz = pkt->GetSize();
    if (sz < 4) return true;

    uint8_t hdr[7];
    uint32_t hdrLen = std::min<uint32_t>(sz, sizeof(hdr));
    pkt->CopyData(hdr, hdrLen);
    uint8_t msgType = hdr[0];
    if (msgType != 5 && msgType != 6 && msgType != 7) return true;  // not search data

    uint16_t fragId = 0;
    uint8_t subIdx = 0;
    uint8_t subTotal = 0;
    if (msgType == 7) {
        if (hdrLen < 7) return true;
        uint16_t destNodeId = 0;
        std::memcpy(&destNodeId, hdr + 1, 2);
        if (destNodeId != m_nodeId) return true;  // app-level unicast filter
        std::memcpy(&fragId, hdr + 3, 2);
        subIdx = hdr[5];
        subTotal = hdr[6];
    } else {
        if (hdrLen < 4) return true;
        std::memcpy(&fragId, hdr + 1, 2);
    }
    m_l0RxTotal++;

    if (msgType == 6) {
        // L0 semantic preamble — counted only.
        m_l0SemanticRx++;
        return true;
    }

    // msgType == 5/7: L0 data sub-packet or full-clip unicast sub-packet.
    if (msgType == 5) {
        if (hdrLen < 5) return true;
        subIdx = hdr[3];
        subTotal = hdr[4];
    }
    if (subTotal == 0 || subTotal > 32 || subIdx >= subTotal) return true;
    m_l0DataSubRx++;

    // Already fully received directly from UAV — drop further sub-packets.
    // A fragment learned through cooperation still remains eligible for direct
    // RX accounting if all UAV sub-packets later arrive.
    if (m_directFragments.find(fragId) != m_directFragments.end()) return true;

    auto& mask = m_fragMask[fragId];
    mask |= (1u << subIdx);
    m_fragSubTotal[fragId] = subTotal;

    // Fragment complete once every sub-packet bit is set.
    if (static_cast<uint8_t>(__builtin_popcount(mask)) >= subTotal) {
        m_directFragments.insert(fragId);
        m_distinctFragments.insert(fragId);
        m_fragMask.erase(fragId);
        m_fragSubTotal.erase(fragId);
    }
    return true;
}

}  // namespace ns3::wsn::uav
