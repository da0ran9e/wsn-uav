#include "sar-bs-app.h"
#include "../common/sar-metrics.h"
#include "../common/sar-types.h"

#include "ns3/core-module.h"
#include "ns3/packet.h"

#include <vector>

using namespace ns3;

namespace ns3::uavsar {

NS_OBJECT_ENSURE_REGISTERED(SarBsApp);

TypeId SarBsApp::GetTypeId() {
    static TypeId tid = TypeId("ns3::uavsar::SarBsApp")
                            .SetParent<Application>().SetGroupName("uav-sar")
                            .AddConstructor<SarBsApp>();
    return tid;
}

bool SarBsApp::OnReceive(Ptr<NetDevice>, Ptr<const Packet> pkt, uint16_t, const Address&) {
    if (pkt->GetSize() < 1) return true;
    uint8_t type = 0; pkt->CopyData(&type, 1);
    if (type == (uint8_t)Msg::REPORT && !m_reported) {
        m_reported = true;
        if (m_metrics) {
            double t = Simulator::Now().GetSeconds();
            m_metrics->AddRecv();
            m_metrics->MarkReportAtBS(t);
            m_metrics->Event(t, m_nodeId, "BS", "report_rx", "mission complete");
        }
        Simulator::Stop(Seconds(0.5));  // wind down shortly after closure
    }
    return true;
}

}  // namespace ns3::uavsar
