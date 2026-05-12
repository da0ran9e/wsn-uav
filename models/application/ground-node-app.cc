#include "ground-node-app.h"
#include "../common/log.h"

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mac16-address.h"

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

void GroundNodeApp::StartApplication() {
    LogN(GetNode()) << "Ground Node #" << m_nodeId << " started";
    // Send a single beacon upon startup.
    // The random startup delay naturally staggers TX times across nodes.
    SendBeacon();
}

void GroundNodeApp::StopApplication() {
    LogN(GetNode()) << "Ground Node #" << m_nodeId << " stopped";
}

void GroundNodeApp::SendBeacon() {
    // Create beacon packet (node ID as payload)
    uint32_t beaconPayload = m_nodeId;
    Ptr<Packet> pkt = Create<Packet>((const uint8_t*)&beaconPayload, sizeof(uint32_t));

    // Broadcast to all neighbors
    Mac16Address broadcast("ff:ff");
    bool success = m_device->Send(pkt, broadcast, 0x00);

    LogN(GetNode()) << "Ground Node #" << m_nodeId << " TX beacon (size="
                    << pkt->GetSize() << " bytes) " << (success ? "[OK]" : "[FAIL]");
}

bool GroundNodeApp::OnReceive(Ptr<NetDevice> dev,
                              Ptr<const Packet> pkt,
                              uint16_t proto,
                              const Address& from) {
    LogN(GetNode()) << "Ground Node #" << m_nodeId << " RX packet (size="
                    << pkt->GetSize() << " bytes, from=" << from << ")";
    return true;
}

}  // namespace ns3::wsn::uav
