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

static std::string GroundLabel(uint32_t id) {
    return "ground-node[" + std::to_string(id) + "]";
}

void GroundNodeApp::StartApplication() {
    LogT(GroundLabel(m_nodeId)) << "started";
    SendBeacon();
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

bool GroundNodeApp::OnReceive(Ptr<NetDevice> dev,
                              Ptr<const Packet> pkt,
                              uint16_t proto,
                              const Address& from) {
    LogT(GroundLabel(m_nodeId)) << "RX packet (size=" << pkt->GetSize()
                                 << "B, from=" << from << ")";
    return true;
}

}  // namespace ns3::wsn::uav
