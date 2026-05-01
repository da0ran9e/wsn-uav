/*
 * WSN-UAV MAC Layer Wrapper
 * Wraps Cc2420Mac with ContactWindowModel integration for time window tracking
 */

#ifndef WSN_UAV_MAC_H
#define WSN_UAV_MAC_H

#include "ns3/object.h"
#include "ns3/packet.h"
#include "ns3/mac16-address.h"
#include "ns3/callback.h"
#include "ns3/ptr.h"
#include "../../../wsn/model/radio/cc2420/cc2420-mac.h"
#include "../../../wsn/model/radio/cc2420/cc2420-phy.h"
#include "../../../wsn/model/radio/cc2420/cc2420-net-device.h"

namespace ns3 {
namespace wsn {
namespace uav {

/**
 * MAC layer wrapper for WSN-UAV scenario
 * Adds contact window tracking for dropped packet reporting
 */
class WsnUavMac : public Object {
public:
    static TypeId GetTypeId();

    WsnUavMac();
    ~WsnUavMac() override;

    /**
     * Callback when packet is dropped due to contact window timeout
     * Arguments: srcNodeId, dstNodeId, fragmentId
     */
    typedef Callback<void, uint32_t, uint32_t, uint32_t> PacketDroppedCallback;

    /**
     * Initialize MAC with Cc2420 device
     */
    void Initialize(Ptr<Cc2420NetDevice> device);

    /**
     * Send packet (delegates to underlying Cc2420Mac)
     */
    bool Send(Ptr<Packet> packet, Mac16Address dest);

    /**
     * Set callback for dropped packets
     */
    void SetPacketDroppedCallback(PacketDroppedCallback cb);

    /**
     * Enable/disable contact window checking
     */
    void SetContactWindowEnabled(bool enabled);

    /**
     * Get underlying Cc2420Mac
     */
    Ptr<Cc2420Mac> GetMac() const;

private:
    /**
     * Handle packet before transmission (check contact window)
     */
    void OnBeforeTransmit(Ptr<Packet> packet, Mac16Address dest);

    /**
     * Check if contact window is available for this packet
     */
    bool HasContactWindow(Ptr<Packet> packet) const;

    Ptr<Cc2420NetDevice> m_device;
    Ptr<Cc2420Mac> m_mac;
    Ptr<Cc2420Phy> m_phy;
    PacketDroppedCallback m_droppedCb;
    bool m_contactWindowEnabled;
};

}  // namespace uav
}  // namespace wsn
}  // namespace ns3

#endif  // WSN_UAV_MAC_H
