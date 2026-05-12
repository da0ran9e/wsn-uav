#ifndef SCENARIO0_1_MAC_H
#define SCENARIO0_1_MAC_H

#include "ns3/object.h"
#include "ns3/net-device.h"
#include "ns3/packet.h"
#include "ns3/mac16-address.h"
#include "ns3/callback.h"

#include <cstdint>
#include <functional>

namespace ns3::wsn::uav {

// Custom packet header for scenario-0.1
struct Scenario01PacketHeader {
    uint8_t  packetType = 0;  // 0=data, 1=manifest, 2=fragment
    uint32_t sourceId = 0;
    uint32_t destinationId = 0xFFFF;  // broadcast by default
    uint32_t sequenceNumber = 0;
};

// Callback signature: void(sourceId, destinationId, Ptr<Packet>, bool isFromUav)
using Scenario01RxCallback = std::function<
    void(uint32_t, uint32_t, Ptr<ns3::Packet>, bool)
>;

// Wrapper class for send/receive operations
class Scenario01Mac : public ns3::Object {
public:
    static ns3::TypeId GetTypeId();

    Scenario01Mac() : m_nodeId(0) {}
    explicit Scenario01Mac(uint32_t nodeId);

    // Send packet with custom header
    bool Send(Ptr<ns3::NetDevice> device,
              Ptr<ns3::Packet> payload,
              uint8_t packetType,
              uint32_t dstId = 0xFFFF);

    // Process received packet (called from NetDevice RX callback)
    void OnReceive(Ptr<ns3::NetDevice> device,
                   Ptr<const ns3::Packet> pkt,
                   uint16_t protocol,
                   const ns3::Address& from,
                   bool isFromUav = false);

    // Register receive callback
    void SetReceiveCallback(const Scenario01RxCallback& cb);

    uint32_t GetNodeId() const { return m_nodeId; }
    uint32_t GetSequenceNumber() { return ++m_seqNum; }

private:
    uint32_t m_nodeId;
    uint32_t m_seqNum = 0;
    Scenario01RxCallback m_rxCallback;

    // Helper: extract header from packet
    bool ExtractHeader(Ptr<const ns3::Packet> pkt,
                      Scenario01PacketHeader& hdr,
                      Ptr<ns3::Packet>& payload) const;

    // Helper: prepend header to packet
    Ptr<ns3::Packet> PrependHeader(const Scenario01PacketHeader& hdr,
                                   Ptr<ns3::Packet> payload) const;
};

}  // namespace ns3::wsn::uav

#endif  // SCENARIO0_1_MAC_H
