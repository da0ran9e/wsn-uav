#ifndef UAV_SAR_PHY_STATS_H
#define UAV_SAR_PHY_STATS_H

// Packet-level PHY error accounting (đánh giá lỗi mức gói).
//
// ns-3.46 lr-wpan already decides packet fate from SINR: LrWpanErrorModel
// (IEEE 802.15.4 O-QPSK BER curve) is attached by every LrWpanNetDevice, the
// noise floor is derived from the configured RX sensitivity
// (LrWpanPhy::SetRxSensitivity -> noiseFactor), and concurrent signals add
// interference / collide (BUSY_RX). This class does NOT change behaviour — it
// instruments every device's PHY traces and classifies each reception:
//
//   ok        completed reception, error model passed
//   perFail   completed reception, corrupted by SINR (chunk PER draw)
//   weak      sync failure at reception start (SINR <= -5 dB: too far/noisy)
//   collision arrived while the transceiver was mid-reception (BUSY_RX)
//   notInRx   arrived while the transceiver was transmitting / not listening
//
// Each classified event is also bucketed by LINK CLASS, derived from the MAC
// source address (parsed from the frame) and the receiver's role:
//   a2g  UAV <-> ground sensor        a2a  UAV <-> UAV
//   g2g  ground <-> ground            bs   any link touching the BS
//
// Counters are exported as name->count for metrics.csv extra columns.

#include "ns3/net-device-container.h"
#include "ns3/lr-wpan-net-device.h"
#include "ns3/mac16-address.h"
#include "ns3/packet.h"
#include "ns3/nstime.h"

#include <cstdint>
#include <map>
#include <memory>
#include <string>
#include <vector>

namespace ns3::uavsar {

class PhyStats {
public:
    // role: 'g' ground sensor, 'u' UAV, 'b' base station.
    void Attach(const ns3::NetDeviceContainer& devs, char role);
    // Call once after all Attach() calls: builds the src-address -> role map.
    void BuildAddressMap();
    // Flush pending receptions and return all counters (call at sim end).
    const std::map<std::string, uint64_t>& Counters();

private:
    struct Probe {
        PhyStats* self = nullptr;
        char role = '?';
        ns3::lrwpan::PhyEnumeration state{};
        ns3::Ptr<const ns3::Packet> pending;  // completed rx awaiting verdict
        char pendingClass[8] = {0};
    };

    void OnState(Probe* pr, ns3::Time t, ns3::lrwpan::PhyEnumeration oldS,
                 ns3::lrwpan::PhyEnumeration newS);
    void OnRxEnd(Probe* pr, ns3::Ptr<const ns3::Packet> p, double sinr);
    void OnRxDrop(Probe* pr, ns3::Ptr<const ns3::Packet> p);
    void OnTxEnd(Probe* pr, ns3::Ptr<const ns3::Packet> p);
    void FlushPending(Probe* pr);  // pending survived -> ok

    char SrcRole(ns3::Ptr<const ns3::Packet> p) const;
    std::string LinkClass(char src, char dst) const;
    void Bump(const std::string& key) { m_c[key]++; }

    std::vector<std::unique_ptr<Probe>> m_probes;
    std::vector<ns3::Ptr<ns3::lrwpan::LrWpanNetDevice>> m_devs;
    std::map<ns3::Mac16Address, char> m_roleByAddr;
    std::map<std::string, uint64_t> m_c;
};

}  // namespace ns3::uavsar

#endif  // UAV_SAR_PHY_STATS_H
