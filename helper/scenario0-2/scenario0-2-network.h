#ifndef SCENARIO0_2_NETWORK_H
#define SCENARIO0_2_NETWORK_H

#include "ns3/object.h"
#include "ns3/node.h"
#include "ns3/net-device.h"
#include "ns3/packet.h"
#include "ns3/mac16-address.h"
#include "ns3/callback.h"

#include <cstdint>
#include <map>
#include <set>
#include <functional>

namespace ns3::wsn::uav {

// Network layer packet header
struct Scenario02NetHeader {
    uint8_t  version = 1;           // protocol version
    uint8_t  headerSize = 16;       // header size in bytes
    uint16_t totalLength = 0;       // total packet length
    uint8_t  hopLimit = 15;         // TTL/hop limit
    uint8_t  payloadType = 0;       // 0=data, 1=beacon, 2=ack, 3=route
    uint16_t sequenceNumber = 0;
    uint32_t sourceId = 0;          // network layer source
    uint32_t destinationId = 0;     // network layer destination (0xffffffff = broadcast)
};

// Neighbor entry in routing table
struct NeighborEntry {
    uint32_t nodeId;
    int8_t   rssi;              // signal strength
    uint32_t lastSeenTime;      // last seen timestamp (simTime in microseconds)
    uint8_t   hopCount = 255;   // distance to this node
};

// Callback: void(srcId, dstId, Ptr<Packet> payload, rssi_dbm)
using Scenario02RxCallback = std::function<
    void(uint32_t, uint32_t, Ptr<ns3::Packet>, int8_t)
>;

// Custom Network Layer
class Scenario02Network : public ns3::Object {
public:
    static ns3::TypeId GetTypeId();

    Scenario02Network() : m_nodeId(0), m_seqNum(0) {}
    explicit Scenario02Network(uint32_t nodeId) : m_nodeId(nodeId), m_seqNum(0) {}

    // Send packet via network layer
    bool Send(Ptr<ns3::NetDevice> device,
              Ptr<ns3::Packet> payload,
              uint32_t dstId,
              uint8_t payloadType = 0);

    // Process received packet from MAC layer
    void OnMacReceive(Ptr<ns3::NetDevice> device,
                      Ptr<const ns3::Packet> macPkt,
                      uint16_t protocol,
                      const ns3::Address& from);

    // Register receive callback
    void SetReceiveCallback(const Scenario02RxCallback& cb) { m_rxCallback = cb; }

    // Neighbor management
    void UpdateNeighbor(uint32_t nodeId, int8_t rssi);
    const std::map<uint32_t, NeighborEntry>& GetNeighbors() const { return m_neighbors; }

    // Getters
    uint32_t GetNodeId() const { return m_nodeId; }
    uint16_t GetNextSequenceNumber() { return ++m_seqNum; }
    uint32_t GetNeighborCount() const { return m_neighbors.size(); }

private:
    uint32_t m_nodeId;
    uint16_t m_seqNum;
    Scenario02RxCallback m_rxCallback;
    std::map<uint32_t, NeighborEntry> m_neighbors;  // neighbor table

    // Helper methods
    bool ExtractHeader(Ptr<const ns3::Packet> pkt,
                      Scenario02NetHeader& hdr,
                      Ptr<ns3::Packet>& payload) const;

    Ptr<ns3::Packet> PrependHeader(const Scenario02NetHeader& hdr,
                                   Ptr<ns3::Packet> payload) const;
};

}  // namespace ns3::wsn::uav

#endif  // SCENARIO0_2_NETWORK_H
