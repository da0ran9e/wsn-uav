#include "sar-bs-app.h"
#include "../common/sar-metrics.h"
#include "../common/sar-types.h"

#include "ns3/core-module.h"
#include "ns3/packet.h"

#include <cstring>
#include <string>
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

bool SarBsApp::OnReceive(Ptr<NetDevice>, Ptr<const Packet> pkt, uint16_t, const Address& from) {
    if (pkt->GetSize() < 1) return true;
    uint8_t type = 0; pkt->CopyData(&type, 1);
    if (type == (uint8_t)Msg::REPORT && !m_reported) {
        double t = Simulator::Now().GetSeconds();
        bool firstFromThisUav = m_reporters.insert(from).second;
        if (m_metrics && firstFromThisUav) {
            m_metrics->AddRecv();
            m_metrics->Event(t, m_nodeId, "BS", "report_rx",
                             "reporter " + std::to_string(m_reporters.size()) + "/" +
                                 std::to_string(m_expected));
        }
        // audit B3: decode the victim fix, if this UAV carried one. The BS knows
        // a position ONLY because these bytes arrived; a blind-coverage baseline
        // reports mission-done with the flag clear and no position is recorded.
        // One fix per UAV: SendReport retries, and the decode used to run on
        // every copy, so fixesAtBS counted retransmissions rather than answers.
        if (m_metrics && firstFromThisUav && pkt->GetSize() >= kReportLen) {
            std::vector<uint8_t> b(kReportLen);
            pkt->CopyData(b.data(), kReportLen);
            if (b[1] & kFlagHasFix) {
                int16_t fx, fy;
                std::memcpy(&fx, &b[5], 2);
                std::memcpy(&fy, &b[7], 2);
                m_metrics->MarkVictimFix(t, fx / 10.0, fy / 10.0);
                m_metrics->Event(t, m_nodeId, "BS", "fix_rx", "victim fix decoded",
                                 fx / 10.0, fy / 10.0, 0.0);
            }
        }
        // mission complete only when every expected UAV has reported.
        if (m_reporters.size() >= m_expected) {
            m_reported = true;
            if (m_metrics) {
                m_metrics->MarkReportAtBS(t);
                m_metrics->Event(t, m_nodeId, "BS", "report_rx", "mission complete");
            }
            Simulator::Stop(Seconds(0.5));  // wind down shortly after closure
        }
    }
    return true;
}

}  // namespace ns3::uavsar
