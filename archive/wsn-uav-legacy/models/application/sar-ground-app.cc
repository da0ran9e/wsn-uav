#include "sar-ground-app.h"
#include "../common/log.h"
#include "../common/sar-metrics.h"

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"
#include "ns3/mac16-address.h"

#include <cstring>
#include <vector>

using namespace ns3;

namespace ns3::wsn::uav {

using sar::MsgType;
using sar::FragClass;
using sar::Scheme;

NS_OBJECT_ENSURE_REGISTERED(SarGroundApp);

TypeId SarGroundApp::GetTypeId() {
    static TypeId tid = TypeId("ns3::wsn::uav::SarGroundApp")
                            .SetParent<Application>()
                            .SetGroupName("wsn-uav")
                            .AddConstructor<SarGroundApp>();
    return tid;
}

SarGroundApp::SarGroundApp() = default;
SarGroundApp::~SarGroundApp() = default;

static std::string GLabel(uint32_t id, bool target) {
    return std::string(target ? "sar-target[" : "sar-node[") + std::to_string(id) + "]";
}

void SarGroundApp::StartApplication() {
    LogT(GLabel(m_nodeId, m_isTarget)) << "start expectFrags=" << m_expectedFrags
                                       << " scheme=" << (int)m_scheme;
}

void SarGroundApp::StopApplication() {
    Simulator::Cancel(m_confirmTimer);
    Simulator::Cancel(m_beaconEvent);
}

void SarGroundApp::Detect() {
    if (m_detected) return;
    m_detected = true;
    Vector p = GetNode()->GetObject<MobilityModel>()->GetPosition();
    if (m_metrics)
        m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "target",
                         "detect", "clue found", p.x, p.y, p.z);
    LogT(GLabel(m_nodeId, true)) << "DETECT clue, requesting confirmation";
    RequestConfirmation();
}

void SarGroundApp::RequestConfirmation() {
    if (m_confirmNeighbors == 0) { Confirmed(); return; }
    if (m_device) {
        std::vector<uint8_t> buf(sar::CONFIRM_HDR);
        uint8_t* p = buf.data();
        *p++ = (uint8_t)MsgType::CONFIRM_REQ;
        *p++ = sar::BROADCAST_ID;
        std::memcpy(p, &m_evtId, 2); p += 2;
        *p++ = (uint8_t)(m_nodeId & 0xFF);
        Ptr<Packet> pkt = Create<Packet>(buf.data(), buf.size());
        m_device->Send(pkt, Mac16Address("ff:ff"), 0x00);
        if (m_metrics) m_metrics->AddPacketSent();
    }
    m_confirmTimer = Simulator::Schedule(Seconds(m_confirmTimeout),
                                         &SarGroundApp::ConfirmTimeout, this);
}

void SarGroundApp::ConfirmTimeout() {
    if (!m_confirmed) {
        LogT(GLabel(m_nodeId, true)) << "confirm timeout (acks=" << m_confirmAcks
                                     << "), sending anyway";
        Confirmed();
    }
}

void SarGroundApp::Confirmed() {
    if (m_confirmed) return;
    m_confirmed = true;
    Simulator::Cancel(m_confirmTimer);
    if (m_metrics) {
        m_metrics->MarkConfirm(Simulator::Now().GetSeconds());
        Vector p = GetNode()->GetObject<MobilityModel>()->GetPosition();
        m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "target",
                         "confirm", "corroborated", p.x, p.y, p.z);
    }
    BeaconLoop();
}

void SarGroundApp::BeaconLoop() {
    if (m_completed) return;
    if (m_beaconsSent >= m_beaconQuota) {
        LogT(GLabel(m_nodeId, true)) << "beacon quota exhausted (" << m_beaconsSent << ")";
        return;
    }
    Vector p = GetNode()->GetObject<MobilityModel>()->GetPosition();
    if (m_device) {
        std::vector<uint8_t> buf(sar::BEACON_LEN);
        uint8_t* q = buf.data();
        *q++ = (uint8_t)MsgType::EMERGENCY_BEACON;
        *q++ = sar::BROADCAST_ID;
        std::memcpy(q, &m_evtId, 2); q += 2;
        *q++ = (uint8_t)(m_nodeId & 0xFF);
        int16_t xdm = (int16_t)(p.x * 10), ydm = (int16_t)(p.y * 10);
        std::memcpy(q, &xdm, 2); q += 2;
        std::memcpy(q, &ydm, 2); q += 2;
        uint16_t aoiMs = 0; std::memcpy(q, &aoiMs, 2); q += 2;
        *q++ = 0;  // prio
        Ptr<Packet> pkt = Create<Packet>(buf.data(), buf.size());
        m_device->Send(pkt, Mac16Address("ff:ff"), 0x00);
        if (m_metrics) m_metrics->AddPacketSent();
    }
    m_beaconsSent++;
    if (m_metrics) {
        m_metrics->AddBeacon();
        m_metrics->MarkFirstBeacon(Simulator::Now().GetSeconds());
        m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "target",
                         "beacon", "summon DATA UAV", p.x, p.y, p.z);
    }
    LogT(GLabel(m_nodeId, true)) << "TX emergency beacon #" << m_beaconsSent;
    m_beaconEvent = Simulator::Schedule(Seconds(1.0), &SarGroundApp::BeaconLoop, this);
}

void SarGroundApp::CheckComplete() {
    if (!m_isTarget || m_completed) return;
    if (m_completeFrags.size() >= m_expectedFrags && m_expectedFrags > 0) {
        m_completed = true;
        Simulator::Cancel(m_beaconEvent);
        Vector p = GetNode()->GetObject<MobilityModel>()->GetPosition();
        if (m_metrics) {
            m_metrics->MarkCompleteData(Simulator::Now().GetSeconds());
            m_metrics->SetFragDelivered(m_completeFrags.size(), m_expectedFrags);
            m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "target",
                             "complete", "full dataset received", p.x, p.y, p.z);
        }
        LogT(GLabel(m_nodeId, true)) << "COMPLETE dataset ("
                                     << m_completeFrags.size() << "/" << m_expectedFrags
                                     << ") at t=" << Simulator::Now().GetSeconds();
        // Primary metric reached: wind the sim down shortly after (bounds batch
        // runtime). Baselines that never complete run to the configured cap.
        Simulator::Stop(Seconds(1.0));
    }
}

bool SarGroundApp::OnReceive(Ptr<NetDevice>, Ptr<const Packet> pkt, uint16_t,
                             const Address& from) {
    uint32_t sz = pkt->GetSize();
    if (sz < 2) return true;
    std::vector<uint8_t> buf(sz);
    pkt->CopyData(buf.data(), sz);
    uint8_t type = buf[0];

    switch (type) {
        case (uint8_t)MsgType::SAR_DATA_FRAG:
        case (uint8_t)MsgType::FULLDATA_FRAG: {
            if (sz < sar::DATA_FRAG_HDR) return true;
            uint16_t fragId, seq, total;
            std::memcpy(&fragId, &buf[2], 2);
            std::memcpy(&seq, &buf[4], 2);
            std::memcpy(&total, &buf[6], 2);
            uint8_t cls = buf[8];
            m_chunks[fragId].insert(seq);
            m_fragTotal[fragId] = total;
            if (m_chunks[fragId].size() >= total) m_completeFrags.insert(fragId);
            if (m_metrics) m_metrics->AddPacketRecv();
            if (m_isTarget && !m_detected && m_scheme == Scheme::PROPOSED &&
                cls == (uint8_t)FragClass::RECOGNITION) {
                Detect();
            }
            CheckComplete();
            break;
        }
        case (uint8_t)MsgType::CONFIRM_REQ: {
            // A neighbour (not the originator) corroborates.
            if (m_isTarget) break;
            if (m_device) {
                std::vector<uint8_t> ack(sar::CONFIRM_HDR);
                uint8_t* p = ack.data();
                *p++ = (uint8_t)MsgType::CONFIRM_ACK;
                *p++ = sar::BROADCAST_ID;
                std::memcpy(p, &buf[2], 2); p += 2;        // echo evtId
                *p++ = (uint8_t)(m_nodeId & 0xFF);
                Ptr<Packet> rp = Create<Packet>(ack.data(), ack.size());
                m_device->Send(rp, from, 0x00);            // unicast back
                if (m_metrics) m_metrics->AddPacketSent();
            }
            break;
        }
        case (uint8_t)MsgType::CONFIRM_ACK: {
            if (m_isTarget && m_detected && !m_confirmed) {
                m_confirmAcks++;
                if (m_metrics) m_metrics->AddPacketRecv();
                if (m_confirmAcks >= m_confirmNeighbors) Confirmed();
            }
            break;
        }
        default:
            break;
    }
    return true;
}

}  // namespace ns3::wsn::uav
