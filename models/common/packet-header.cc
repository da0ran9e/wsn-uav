#include "packet-header.h"
#include "ns3/buffer.h"
#include "ns3/log.h"

NS_LOG_COMPONENT_DEFINE("WsnUavPacketHeader");

namespace ns3 {
namespace wsn {
namespace uav {

// ============================================================================
// PacketHeader
// ============================================================================

PacketHeader::PacketHeader() : m_type(PACKET_TYPE_FRAGMENT) {}

PacketHeader::~PacketHeader() {}

void PacketHeader::SetType(PacketType type) {
    m_type = static_cast<uint8_t>(type);
}

PacketType PacketHeader::GetType() const {
    return static_cast<PacketType>(m_type);
}

TypeId PacketHeader::GetTypeId() {
    static TypeId tid = TypeId("ns3::wsn::uav::PacketHeader")
        .SetParent<Header>()
        .SetGroupName("WsnUav")
        .AddConstructor<PacketHeader>();
    return tid;
}

TypeId PacketHeader::GetInstanceTypeId() const {
    return GetTypeId();
}

void PacketHeader::Print(std::ostream& os) const {
    os << "PacketHeader(type=" << static_cast<uint32_t>(m_type) << ")";
}

uint32_t PacketHeader::GetSerializedSize() const {
    return 1;  // 1 byte for type
}

void PacketHeader::Serialize(Buffer::Iterator start) const {
    start.WriteU8(m_type);
}

uint32_t PacketHeader::Deserialize(Buffer::Iterator start) {
    m_type = start.ReadU8();
    return 1;
}

// ============================================================================
// FragmentPacket
// ============================================================================

FragmentPacket::FragmentPacket()
    : m_fragmentId(0), m_confidence(0.0), m_sourceId(0) {}

FragmentPacket::~FragmentPacket() {}

void FragmentPacket::SetFragmentId(uint32_t fragmentId) {
    m_fragmentId = fragmentId;
}

uint32_t FragmentPacket::GetFragmentId() const {
    return m_fragmentId;
}

void FragmentPacket::SetConfidence(double confidence) {
    m_confidence = confidence;
}

double FragmentPacket::GetConfidence() const {
    return m_confidence;
}

void FragmentPacket::SetSourceId(uint32_t sourceId) {
    m_sourceId = sourceId;
}

uint32_t FragmentPacket::GetSourceId() const {
    return m_sourceId;
}

TypeId FragmentPacket::GetTypeId() {
    static TypeId tid = TypeId("ns3::wsn::uav::FragmentPacket")
        .SetParent<Header>()
        .SetGroupName("WsnUav")
        .AddConstructor<FragmentPacket>();
    return tid;
}

TypeId FragmentPacket::GetInstanceTypeId() const {
    return GetTypeId();
}

void FragmentPacket::Print(std::ostream& os) const {
    os << "FragmentPacket(id=" << m_fragmentId
       << ", conf=" << m_confidence
       << ", src=" << m_sourceId << ")";
}

uint32_t FragmentPacket::GetSerializedSize() const {
    return 4 + 4 + 4;  // fragId(4) + confidence(4 as float) + sourceId(4) = 12 bytes
}

void FragmentPacket::Serialize(Buffer::Iterator start) const {
    start.WriteU32(m_fragmentId);
    // Store confidence as fixed-point: multiply by 10000, store as uint32_t
    uint32_t confFixed = static_cast<uint32_t>(m_confidence * 10000.0);
    start.WriteU32(confFixed);
    start.WriteU32(m_sourceId);
}

uint32_t FragmentPacket::Deserialize(Buffer::Iterator start) {
    m_fragmentId = start.ReadU32();
    uint32_t confFixed = start.ReadU32();
    m_confidence = confFixed / 10000.0;
    m_sourceId = start.ReadU32();
    return 12;
}

// ============================================================================
// CooperationPacket
// ============================================================================

CooperationPacket::CooperationPacket()
    : m_requesterId(0), m_cellId(-1) {}

CooperationPacket::~CooperationPacket() {}

void CooperationPacket::SetRequesterId(uint32_t requesterId) {
    m_requesterId = requesterId;
}

uint32_t CooperationPacket::GetRequesterId() const {
    return m_requesterId;
}

void CooperationPacket::SetCellId(int32_t cellId) {
    m_cellId = cellId;
}

int32_t CooperationPacket::GetCellId() const {
    return m_cellId;
}

void CooperationPacket::SetAvailableFragments(const std::vector<uint32_t>& fragmentIds) {
    m_availableFragments = fragmentIds;
}

const std::vector<uint32_t>& CooperationPacket::GetAvailableFragments() const {
    return m_availableFragments;
}

TypeId CooperationPacket::GetTypeId() {
    static TypeId tid = TypeId("ns3::wsn::uav::CooperationPacket")
        .SetParent<Header>()
        .SetGroupName("WsnUav")
        .AddConstructor<CooperationPacket>();
    return tid;
}

TypeId CooperationPacket::GetInstanceTypeId() const {
    return GetTypeId();
}

void CooperationPacket::Print(std::ostream& os) const {
    os << "CooperationPacket(requester=" << m_requesterId
       << ", cell=" << m_cellId
       << ", frags=" << m_availableFragments.size() << ")";
}

uint32_t CooperationPacket::GetSerializedSize() const {
    return 4 + 4 + 4 + (m_availableFragments.size() * 4);  // requester(4) + cellId(4) + count(4) + fragIds
}

void CooperationPacket::Serialize(Buffer::Iterator start) const {
    start.WriteU32(m_requesterId);
    start.WriteU32(static_cast<uint32_t>(m_cellId));
    start.WriteU32(static_cast<uint32_t>(m_availableFragments.size()));
    for (uint32_t fragId : m_availableFragments) {
        start.WriteU32(fragId);
    }
}

uint32_t CooperationPacket::Deserialize(Buffer::Iterator start) {
    m_requesterId = start.ReadU32();
    m_cellId = static_cast<int32_t>(start.ReadU32());
    uint32_t count = start.ReadU32();
    m_availableFragments.clear();
    for (uint32_t i = 0; i < count; i++) {
        m_availableFragments.push_back(start.ReadU32());
    }
    return 4 + 4 + 4 + (count * 4);
}

}  // namespace uav
}  // namespace wsn
}  // namespace ns3
