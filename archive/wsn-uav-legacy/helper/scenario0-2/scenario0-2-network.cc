#include "scenario0-2-network.h"

#include "ns3/log.h"
#include "ns3/type-id.h"
#include "ns3/simulator.h"

#include <cstring>

NS_LOG_COMPONENT_DEFINE("Scenario0_2_Network");

namespace ns3::wsn::uav {

ns3::TypeId
Scenario02Network::GetTypeId()
{
    static ns3::TypeId tid = ns3::TypeId("ns3::wsn::uav::Scenario02Network")
                                .SetParent<ns3::Object>()
                                .SetGroupName("WsnUav")
                                .AddConstructor<Scenario02Network>();
    return tid;
}

bool Scenario02Network::Send(Ptr<ns3::NetDevice> device,
                             Ptr<ns3::Packet> payload,
                             uint32_t dstId,
                             uint8_t payloadType)
{
    if (!device) {
        return false;
    }

    // Build network header
    Scenario02NetHeader hdr;
    hdr.version = 1;
    hdr.headerSize = sizeof(Scenario02NetHeader);
    hdr.hopLimit = 15;
    hdr.payloadType = payloadType;
    hdr.sequenceNumber = GetNextSequenceNumber();
    hdr.sourceId = m_nodeId;
    hdr.destinationId = dstId;

    uint16_t payloadSize = payload ? payload->GetSize() : 0;
    hdr.totalLength = hdr.headerSize + payloadSize;

    // Create packet with header
    auto pkt = PrependHeader(hdr, payload);

    // Send via MAC layer (broadcast address)
    ns3::Mac16Address broadcast("ff:ff");
    return device->Send(pkt, broadcast, 0x00);
}

void Scenario02Network::OnMacReceive(Ptr<ns3::NetDevice> device,
                                     Ptr<const ns3::Packet> macPkt,
                                     uint16_t protocol,
                                     const ns3::Address& from)
{
    if (!macPkt) {
        return;
    }

    auto pktCopy = macPkt->Copy();

    Scenario02NetHeader hdr;
    Ptr<ns3::Packet> payload;

    // Extract and validate header
    if (!ExtractHeader(pktCopy, hdr, payload)) {
        NS_LOG_DEBUG("Node " << m_nodeId << " : Invalid network header");
        return;
    }

    NS_LOG_DEBUG("Node " << m_nodeId << " RX from " << hdr.sourceId << " seq="
                         << hdr.sequenceNumber << " type=" << (int)hdr.payloadType);

    // Update neighbor table
    UpdateNeighbor(hdr.sourceId, -90);  // Default RSSI (should be from PHY layer)

    // Check if packet is for us or broadcast
    if (hdr.destinationId != 0xffffffff && hdr.destinationId != m_nodeId) {
        NS_LOG_DEBUG("Node " << m_nodeId << " : Packet not for us, dropping");
        return;
    }

    // Call receive callback if registered
    if (m_rxCallback) {
        m_rxCallback(hdr.sourceId, hdr.destinationId, payload, -90);
    }
}

void Scenario02Network::UpdateNeighbor(uint32_t nodeId, int8_t rssi)
{
    auto it = m_neighbors.find(nodeId);
    if (it != m_neighbors.end()) {
        it->second.rssi = rssi;
        it->second.lastSeenTime = ns3::Simulator::Now().GetMicroSeconds();
    } else {
        NeighborEntry entry;
        entry.nodeId = nodeId;
        entry.rssi = rssi;
        entry.lastSeenTime = ns3::Simulator::Now().GetMicroSeconds();
        entry.hopCount = 1;
        m_neighbors[nodeId] = entry;
    }
}

bool Scenario02Network::ExtractHeader(Ptr<const ns3::Packet> pkt,
                                      Scenario02NetHeader& hdr,
                                      Ptr<ns3::Packet>& payload) const
{
    if (pkt->GetSize() < sizeof(Scenario02NetHeader)) {
        return false;
    }

    // Extract header bytes
    uint8_t buffer[sizeof(Scenario02NetHeader)];
    pkt->CopyData(buffer, sizeof(Scenario02NetHeader));

    // Deserialize header
    hdr.version = buffer[0];
    hdr.headerSize = buffer[1];
    std::memcpy(&hdr.totalLength, buffer + 2, sizeof(uint16_t));
    hdr.hopLimit = buffer[4];
    hdr.payloadType = buffer[5];
    std::memcpy(&hdr.sequenceNumber, buffer + 6, sizeof(uint16_t));
    std::memcpy(&hdr.sourceId, buffer + 8, sizeof(uint32_t));
    std::memcpy(&hdr.destinationId, buffer + 12, sizeof(uint32_t));

    // Validate header
    if (hdr.version != 1 || hdr.headerSize != sizeof(Scenario02NetHeader)) {
        return false;
    }

    // Extract payload
    if (pkt->GetSize() > hdr.headerSize) {
        payload = pkt->CreateFragment(hdr.headerSize,
                                      pkt->GetSize() - hdr.headerSize);
    } else {
        payload = ns3::Create<ns3::Packet>(0);
    }

    return true;
}

Ptr<ns3::Packet> Scenario02Network::PrependHeader(const Scenario02NetHeader& hdr,
                                                  Ptr<ns3::Packet> payload) const
{
    // Serialize header to buffer
    uint8_t buffer[sizeof(Scenario02NetHeader)];
    buffer[0] = hdr.version;
    buffer[1] = hdr.headerSize;
    std::memcpy(buffer + 2, &hdr.totalLength, sizeof(uint16_t));
    buffer[4] = hdr.hopLimit;
    buffer[5] = hdr.payloadType;
    std::memcpy(buffer + 6, &hdr.sequenceNumber, sizeof(uint16_t));
    std::memcpy(buffer + 8, &hdr.sourceId, sizeof(uint32_t));
    std::memcpy(buffer + 12, &hdr.destinationId, sizeof(uint32_t));

    // Create packet with header
    auto pkt = ns3::Create<ns3::Packet>(buffer, sizeof(Scenario02NetHeader));

    // Append payload if provided
    if (payload && payload->GetSize() > 0) {
        pkt->AddAtEnd(payload);
    }

    return pkt;
}

}  // namespace ns3::wsn::uav
