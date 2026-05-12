#include "scenario0-1-mac.h"

#include "ns3/log.h"
#include "ns3/type-id.h"
#include <cstring>

NS_LOG_COMPONENT_DEFINE("Scenario0_1_Mac");

namespace ns3::wsn::uav {

ns3::TypeId
Scenario01Mac::GetTypeId()
{
    static ns3::TypeId tid =
        ns3::TypeId("ns3::wsn::uav::Scenario01Mac")
            .SetParent<ns3::Object>()
            .SetGroupName("WsnUav")
            .AddConstructor<Scenario01Mac>();
    return tid;
}

Scenario01Mac::Scenario01Mac(uint32_t nodeId)
    : m_nodeId(nodeId)
{
}

void Scenario01Mac::SetReceiveCallback(const Scenario01RxCallback& cb)
{
    m_rxCallback = cb;
}

bool Scenario01Mac::Send(Ptr<ns3::NetDevice> device,
                         Ptr<ns3::Packet> payload,
                         uint8_t packetType,
                         uint32_t dstId)
{
    if (!device) {
        return false;
    }

    // Build header
    Scenario01PacketHeader hdr;
    hdr.packetType = packetType;
    hdr.sourceId = m_nodeId;
    hdr.destinationId = dstId;
    hdr.sequenceNumber = GetSequenceNumber();

    // Create packet with header
    auto pkt = PrependHeader(hdr, payload);

    // Send via device (broadcast address)
    ns3::Mac16Address broadcast("ff:ff");
    return device->Send(pkt, broadcast, 0x00);
}

void Scenario01Mac::OnReceive(Ptr<ns3::NetDevice> device,
                              Ptr<const ns3::Packet> pkt,
                              uint16_t protocol,
                              const ns3::Address& from,
                              bool isFromUav)
{
    if (!pkt) {
        return;
    }

    // Copy packet to avoid modifying original
    auto pktCopy = pkt->Copy();

    Scenario01PacketHeader hdr;
    Ptr<ns3::Packet> payload;

    // Try to extract header
    if (!ExtractHeader(pktCopy, hdr, payload)) {
        NS_LOG_DEBUG("Failed to extract header from packet");
        return;
    }

    NS_LOG_DEBUG("Node " << m_nodeId << " received packet from " << hdr.sourceId
                         << " (type=" << static_cast<int>(hdr.packetType) << ")");

    // Call receive callback if registered
    if (m_rxCallback) {
        m_rxCallback(hdr.sourceId, hdr.destinationId, payload, isFromUav);
    }
}

bool Scenario01Mac::ExtractHeader(Ptr<const ns3::Packet> pkt,
                                  Scenario01PacketHeader& hdr,
                                  Ptr<ns3::Packet>& payload) const
{
    if (pkt->GetSize() < sizeof(Scenario01PacketHeader)) {
        return false;
    }

    // Extract header bytes
    uint8_t buffer[sizeof(Scenario01PacketHeader)];
    pkt->CopyData(buffer, sizeof(Scenario01PacketHeader));

    // Deserialize header
    hdr.packetType = buffer[0];
    std::memcpy(&hdr.sourceId, buffer + 1, sizeof(uint32_t));
    std::memcpy(&hdr.destinationId, buffer + 5, sizeof(uint32_t));
    std::memcpy(&hdr.sequenceNumber, buffer + 9, sizeof(uint32_t));

    // Create payload (remove header)
    payload = pkt->CreateFragment(sizeof(Scenario01PacketHeader),
                                  pkt->GetSize() - sizeof(Scenario01PacketHeader));

    return true;
}

Ptr<ns3::Packet> Scenario01Mac::PrependHeader(const Scenario01PacketHeader& hdr,
                                              Ptr<ns3::Packet> payload) const
{
    // Serialize header to buffer
    uint8_t buffer[sizeof(Scenario01PacketHeader)];
    buffer[0] = hdr.packetType;
    std::memcpy(buffer + 1, &hdr.sourceId, sizeof(uint32_t));
    std::memcpy(buffer + 5, &hdr.destinationId, sizeof(uint32_t));
    std::memcpy(buffer + 9, &hdr.sequenceNumber, sizeof(uint32_t));

    // Create packet with header
    auto pkt = ns3::Create<ns3::Packet>(buffer, sizeof(Scenario01PacketHeader));

    // Append payload if provided
    if (payload && payload->GetSize() > 0) {
        pkt->AddAtEnd(payload);
    }

    return pkt;
}

}  // namespace ns3::wsn::uav
