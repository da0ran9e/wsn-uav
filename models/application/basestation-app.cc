#include "basestation-app.h"
#include "../common/log.h"

#include "ns3/core-module.h"
#include "ns3/network-module.h"

using namespace ns3;

namespace ns3::wsn::uav {

NS_OBJECT_ENSURE_REGISTERED(BaseStationApp);

TypeId BaseStationApp::GetTypeId() {
    static TypeId tid =
        TypeId("ns3::wsn::uav::BaseStationApp")
            .SetParent<Application>()
            .SetGroupName("wsn-uav")
            .AddConstructor<BaseStationApp>();
    return tid;
}

BaseStationApp::BaseStationApp() : m_nodeId(0) {
}

BaseStationApp::~BaseStationApp() {
}

void BaseStationApp::SetNodeId(uint32_t id) {
    m_nodeId = id;
}

void BaseStationApp::SetNetDevice(Ptr<NetDevice> dev) {
    m_device = dev;
}

void BaseStationApp::StartApplication() {
    LogN(GetNode()) << "BaseStation #" << m_nodeId << " started";
}

void BaseStationApp::StopApplication() {
    LogN(GetNode()) << "BaseStation #" << m_nodeId << " stopped";
}

}  // namespace ns3::wsn::uav
