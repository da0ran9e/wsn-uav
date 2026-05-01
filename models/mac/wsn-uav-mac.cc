#include "wsn-uav-mac.h"
#include "ns3/type-id.h"
#include "ns3/log.h"
#include "ns3/boolean.h"
#include "../../../wsn/model/radio/cc2420/cc2420-mac.h"
#include "../../../wsn/model/radio/cc2420/cc2420-phy.h"
#include "../../../wsn/model/radio/cc2420/cc2420-net-device.h"
#include "../../../wsn/model/radio/cc2420/cc2420-contact-window-model.h"
#include "ns3/node.h"
#include "ns3/mobility-model.h"

NS_LOG_COMPONENT_DEFINE("WsnUavMac");

namespace ns3 {
namespace wsn {
namespace uav {

NS_OBJECT_ENSURE_REGISTERED(WsnUavMac);

TypeId WsnUavMac::GetTypeId() {
    static TypeId tid = TypeId("ns3::wsn::uav::WsnUavMac")
        .SetParent<Object>()
        .SetGroupName("WsnUav")
        .AddConstructor<WsnUavMac>();
    return tid;
}

WsnUavMac::WsnUavMac()
    : m_contactWindowEnabled(true) {
    NS_LOG_FUNCTION(this);
}

WsnUavMac::~WsnUavMac() {
    NS_LOG_FUNCTION(this);
}

void WsnUavMac::Initialize(Ptr<Cc2420NetDevice> device) {
    NS_LOG_FUNCTION(this << device);

    if (!device) {
        NS_LOG_ERROR("Device is null");
        return;
    }

    m_device = device;
    m_mac = device->GetMac();
    m_phy = device->GetPhy();

    if (!m_mac || !m_phy) {
        NS_LOG_ERROR("MAC or PHY is null");
        return;
    }

    NS_LOG_INFO("WsnUavMac initialized with device");
}

bool WsnUavMac::Send(Ptr<Packet> packet, Mac16Address dest) {
    NS_LOG_FUNCTION(this << packet->GetSize() << dest);

    if (!m_mac) {
        NS_LOG_WARN("MAC not initialized");
        return false;
    }

    // Check contact window if enabled
    if (m_contactWindowEnabled && !HasContactWindow(packet)) {
        NS_LOG_DEBUG("Contact window not available, packet would be dropped");
        // Packet will be dropped at MAC layer due to contact window check
        // We still try to send it, but it will be rejected by MAC
    }

    // Delegate to Cc2420Mac
    return m_mac->McpsDataRequest(packet, dest, false);
}

bool WsnUavMac::HasContactWindow(Ptr<Packet> packet) const {
    if (!m_mac || !m_phy) {
        return true;  // Assume contact if not initialized
    }

    auto cwModel = m_mac->GetContactWindowModel();
    if (!cwModel || !cwModel->IsEnabled()) {
        return true;  // Contact window disabled
    }

    // Check if contact window is available for this packet
    // This mirrors the check in Cc2420Mac::AttemptTransmission()
    // We need TX and RX PHYs - but we only have one side here
    // The full check happens in MAC layer, so return true
    return true;
}

void WsnUavMac::SetPacketDroppedCallback(PacketDroppedCallback cb) {
    NS_LOG_FUNCTION(this);
    m_droppedCb = cb;
}

void WsnUavMac::SetContactWindowEnabled(bool enabled) {
    NS_LOG_FUNCTION(this << enabled);
    m_contactWindowEnabled = enabled;

    if (!m_mac) {
        return;
    }

    auto cwModel = m_mac->GetContactWindowModel();
    if (cwModel) {
        cwModel->SetAttribute("Enabled", BooleanValue(enabled));
        NS_LOG_INFO("Contact window " << (enabled ? "enabled" : "disabled"));
    }
}

Ptr<Cc2420Mac> WsnUavMac::GetMac() const {
    return m_mac;
}

}  // namespace uav
}  // namespace wsn
}  // namespace ns3
