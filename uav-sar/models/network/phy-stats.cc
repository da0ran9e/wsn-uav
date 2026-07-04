#include "phy-stats.h"

#include "ns3/lr-wpan-mac-header.h"
#include "ns3/lr-wpan-phy.h"

#include <cstring>

namespace ns3::uavsar {

using namespace ns3;
using lrwpan::LrWpanMacHeader;
using lrwpan::LrWpanNetDevice;
using lrwpan::PhyEnumeration;

void PhyStats::Attach(const NetDeviceContainer& devs, char role) {
    for (uint32_t i = 0; i < devs.GetN(); i++) {
        Ptr<LrWpanNetDevice> dev = DynamicCast<LrWpanNetDevice>(devs.Get(i));
        if (!dev) continue;
        auto probe = std::make_unique<Probe>();
        Probe* pr = probe.get();
        pr->self = this;
        pr->role = role;
        pr->state = lrwpan::IEEE_802_15_4_PHY_TRX_OFF;

        Ptr<lrwpan::LrWpanPhy> phy = dev->GetPhy();
        phy->TraceConnectWithoutContext(
            "TrxState", MakeCallback(&PhyStats::OnState, this).Bind(pr));
        phy->TraceConnectWithoutContext(
            "PhyRxEnd", MakeCallback(&PhyStats::OnRxEnd, this).Bind(pr));
        phy->TraceConnectWithoutContext(
            "PhyRxDrop", MakeCallback(&PhyStats::OnRxDrop, this).Bind(pr));
        phy->TraceConnectWithoutContext(
            "PhyTxEnd", MakeCallback(&PhyStats::OnTxEnd, this).Bind(pr));

        m_probes.push_back(std::move(probe));
        m_devs.push_back(dev);
    }
}

void PhyStats::BuildAddressMap() {
    for (size_t i = 0; i < m_devs.size(); i++) {
        m_roleByAddr[m_devs[i]->GetMac()->GetShortAddress()] = m_probes[i]->role;
    }
}

const std::map<std::string, uint64_t>& PhyStats::Counters() {
    for (auto& pr : m_probes) FlushPending(pr.get());
    return m_c;
}

void PhyStats::OnState(Probe* pr, Time, PhyEnumeration, PhyEnumeration newS) {
    pr->state = newS;
}

char PhyStats::SrcRole(Ptr<const Packet> p) const {
    LrWpanMacHeader h;
    if (!p || p->PeekHeader(h) == 0) return '?';
    if (!h.IsData()) return '?';
    auto it = m_roleByAddr.find(h.GetShortSrcAddr());
    return it == m_roleByAddr.end() ? '?' : it->second;
}

std::string PhyStats::LinkClass(char src, char dst) const {
    if (src == 'b' || dst == 'b') return "bs";
    if (src == 'u' && dst == 'u') return "a2a";
    if (src == 'g' && dst == 'g') return "g2g";
    if (src == '?' || dst == '?') return "ctl";
    return "a2g";  // u<->g either direction
}

void PhyStats::FlushPending(Probe* pr) {
    if (!pr->pending) return;
    Bump(std::string("phyOk_") + pr->pendingClass);
    pr->pending = nullptr;
}

void PhyStats::OnRxEnd(Probe* pr, Ptr<const Packet> p, double /*sinr*/) {
    // A completed reception; verdict (ok vs corrupted) shows up as an
    // immediately-following PhyRxDrop for the same packet.
    FlushPending(pr);
    pr->pending = p;
    std::string cls = LinkClass(SrcRole(p), pr->role);
    std::strncpy(pr->pendingClass, cls.c_str(), sizeof(pr->pendingClass) - 1);
}

void PhyStats::OnRxDrop(Probe* pr, Ptr<const Packet> p) {
    if (pr->pending && pr->pending == p) {
        // completed but corrupted by the SINR error model
        Bump(std::string("phyPer_") + pr->pendingClass);
        pr->pending = nullptr;
        return;
    }
    FlushPending(pr);
    std::string cls = LinkClass(SrcRole(p), pr->role);
    switch (pr->state) {
        case lrwpan::IEEE_802_15_4_PHY_RX_ON:
            Bump("phyWeak_" + cls);       // sync fail: SINR <= -5 dB at start
            break;
        case lrwpan::IEEE_802_15_4_PHY_BUSY_RX:
            Bump("phyCol_" + cls);        // arrived mid-reception
            break;
        default:
            Bump("phyNotInRx");           // transceiver TX / off
            break;
    }
}

void PhyStats::OnTxEnd(Probe* pr, Ptr<const Packet>) {
    Bump(std::string("phyTx_") + pr->role);
}

}  // namespace ns3::uavsar
