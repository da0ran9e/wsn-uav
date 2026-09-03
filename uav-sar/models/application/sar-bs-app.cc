#include "sar-bs-app.h"
#include "../common/sar-params.h"
#include "ns3/mac16-address.h"
#include "../common/sar-metrics.h"
#include "../common/sar-types.h"

#include "ns3/core-module.h"
#include "ns3/packet.h"

#include <algorithm>
#include <cmath>
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

void SarBsApp::OnLoraFlag(uint16_t rid, double x, double y) {
    m_loraFlags++;
    if (m_metrics)
        m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "BS", "lora_rx",
                         "candidate flagged", x, y, 0.0);
    if (m_launched || !m_dev) return;
    m_launched = true;
    // CLAIM role 5: launch Phase 2. Repeated, because a single unacknowledged
    // broadcast is not a protocol -- the same lesson the sweep-done announcement
    // cost earlier, where one seed in five opened no gate at all.
    for (uint32_t k = 0; k < params::kConfirmRetries; ++k) {
        Simulator::Schedule(Seconds(k * params::kConfirmRetryS), [this]() {
            std::vector<uint8_t> b(kClaimLen);
            uint8_t* q = b.data();
            *q++ = (uint8_t)Msg::CLAIM;
            uint16_t none = 0xFFFF; std::memcpy(q, &none, 2); q += 2;
            *q++ = 5;
            uint16_t id = (uint16_t)m_nodeId; std::memcpy(q, &id, 2);
            m_dev->Send(Create<Packet>(b.data(), b.size()), Mac16Address("ff:ff"), 0);
            if (m_metrics) { m_metrics->AddSent(); m_metrics->AddSentBytes(b.size()); }
        });
        // ...and WHERE to go. Releasing the gate alone was measured and it is not
        // enough: the team took off on time and then never claimed anything,
        // because the summon still had to reach it across the field over the
        // mesh and did not. The flag already carried the coordinates to the
        // base, so the base advertises them as an ordinary A2A job advert --
        // the same message a FAST relay would have sent, from a transmitter the
        // grounded team is standing next to.
        //
        // Offset by 250 ms from the CLAIM: back-to-back Send() calls overflow
        // the MAC queue, and 200 ms is the documented floor.
        Simulator::Schedule(Seconds(k * params::kConfirmRetryS + 0.25),
                            [this, rid, x, y]() {
            std::vector<uint8_t> b(kA2ALen, 0);
            uint8_t* q = b.data();
            *q++ = (uint8_t)Msg::A2A; *q++ = kBroadcast;
            uint16_t r = rid; std::memcpy(q, &r, 2); q += 2;
            int16_t ix = (int16_t)std::lround(x * 10), iy = (int16_t)std::lround(y * 10);
            std::memcpy(q, &ix, 2); q += 2; std::memcpy(q, &iy, 2);
            m_dev->Send(Create<Packet>(b.data(), b.size()), Mac16Address("ff:ff"), 0);
            if (m_metrics) { m_metrics->AddSent(); m_metrics->AddSentBytes(b.size()); }
        });
    }
    if (m_metrics) {
        Vector p(0, 0, 0);
        m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "BS", "launch_order",
                         "phase 2 released on first candidate", p.x, p.y, p.z);
    }
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
                // D37: a report may carry several confirmed positions.
                const uint32_t n = std::min<uint32_t>(b[2], kMaxFixes);
                for (uint32_t i = 0; i < n; ++i) {
                    int16_t fx, fy;
                    std::memcpy(&fx, &b[kReportHdr + i * 4], 2);
                    std::memcpy(&fy, &b[kReportHdr + i * 4 + 2], 2);
                    m_metrics->MarkVictimFix(t, fx / 10.0, fy / 10.0);
                    m_metrics->Event(t, m_nodeId, "BS", "fix_rx", "victim fix decoded",
                                     fx / 10.0, fy / 10.0, 0.0);
                }
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
