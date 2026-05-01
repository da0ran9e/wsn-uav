/*
 * WSN-UAV Packet Header Definitions
 * Unified packet format for scenario 1 protocol
 */

#ifndef WSN_UAV_PACKET_HEADER_H
#define WSN_UAV_PACKET_HEADER_H

#include "ns3/header.h"
#include <vector>

namespace ns3 {
namespace wsn {
namespace uav {

/**
 * Packet types for wsn-uav protocol.
 */
enum PacketType {
    PACKET_TYPE_STARTUP     = 1,  ///< Startup phase discovery
    PACKET_TYPE_FRAGMENT    = 2,  ///< Fragment data from UAV or peer
    PACKET_TYPE_COOPERATION = 3   ///< Cell cooperation manifest
};

/**
 * Base packet header with type field.
 */
class PacketHeader : public Header {
public:
    PacketHeader();
    virtual ~PacketHeader();

    void SetType(PacketType type);
    PacketType GetType() const;

    static TypeId GetTypeId();
    TypeId GetInstanceTypeId() const override;
    void Print(std::ostream& os) const override;
    uint32_t GetSerializedSize() const override;
    void Serialize(Buffer::Iterator start) const override;
    uint32_t Deserialize(Buffer::Iterator start) override;

private:
    uint8_t m_type;
};

/**
 * Fragment data packet.
 * Contains file fragment metadata (id, confidence, source).
 */
class FragmentPacket : public Header {
public:
    FragmentPacket();
    virtual ~FragmentPacket();

    void SetFragmentId(uint32_t fragmentId);
    uint32_t GetFragmentId() const;

    void SetConfidence(double confidence);
    double GetConfidence() const;

    void SetSourceId(uint32_t sourceId);
    uint32_t GetSourceId() const;

    static TypeId GetTypeId();
    TypeId GetInstanceTypeId() const override;
    void Print(std::ostream& os) const override;
    uint32_t GetSerializedSize() const override;
    void Serialize(Buffer::Iterator start) const override;
    uint32_t Deserialize(Buffer::Iterator start) override;

private:
    uint32_t m_fragmentId;
    double m_confidence;
    uint32_t m_sourceId;
};

/**
 * Cell cooperation manifest packet.
 * Lists fragments available at requesting node for peer sharing.
 */
class CooperationPacket : public Header {
public:
    CooperationPacket();
    virtual ~CooperationPacket();

    void SetRequesterId(uint32_t requesterId);
    uint32_t GetRequesterId() const;

    void SetCellId(int32_t cellId);
    int32_t GetCellId() const;

    void SetAvailableFragments(const std::vector<uint32_t>& fragmentIds);
    const std::vector<uint32_t>& GetAvailableFragments() const;

    static TypeId GetTypeId();
    TypeId GetInstanceTypeId() const override;
    void Print(std::ostream& os) const override;
    uint32_t GetSerializedSize() const override;
    void Serialize(Buffer::Iterator start) const override;
    uint32_t Deserialize(Buffer::Iterator start) override;

private:
    uint32_t m_requesterId;
    int32_t m_cellId;
    std::vector<uint32_t> m_availableFragments;
};

}  // namespace uav
}  // namespace wsn
}  // namespace ns3

#endif  // WSN_UAV_PACKET_HEADER_H
