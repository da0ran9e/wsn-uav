#ifndef GROUND_NODE_APP_H
#define GROUND_NODE_APP_H

#include "../common/cell-layer.h"
#include "../common/local-clue.h"

#include "ns3/application.h"
#include "ns3/net-device.h"
#include "ns3/ptr.h"
#include "ns3/event-id.h"

#include <cstdint>
#include <map>
#include <set>
#include <vector>

namespace ns3::wsn::uav {

class GroundNodeApp : public Application {
public:
    static TypeId GetTypeId();

    GroundNodeApp();
    virtual ~GroundNodeApp();

    // Configuration
    void SetNodeId(uint32_t id);
    void SetNetDevice(ns3::Ptr<ns3::NetDevice> dev);
    void SetCellRoutingInfo(const CellRoutingInfo& info);
    void SetLocalClueInfo(const LocalClueInfo& info);

    // Broadcast beacon
    void SendBeacon();

    // NetDevice RX callback — wired by the scenario config.
    bool OnReceive(ns3::Ptr<ns3::NetDevice> dev,
                   ns3::Ptr<const ns3::Packet> pkt,
                   uint16_t proto,
                   const ns3::Address& from);

    // Layer-0 systematic broadcast — per-node reception accessors.
    uint32_t GetNodeId() const { return m_nodeId; }
    uint32_t L0RxTotal() const { return m_l0RxTotal; }
    uint32_t L0DataSubRx() const { return m_l0DataSubRx; }
    uint32_t L0SemanticRx() const { return m_l0SemanticRx; }
    uint32_t DistinctFragmentCount() const {
        return static_cast<uint32_t>(m_distinctFragments.size());
    }
    uint32_t DirectUavFragmentCount() const {
        return static_cast<uint32_t>(m_directFragments.size());
    }
    const std::set<uint16_t>& DistinctFragments() const { return m_distinctFragments; }
    uint32_t MergeCoopFragments(const std::set<uint16_t>& fragments);
    uint32_t CoopFragmentsGained() const { return m_coopFragmentsGained; }
    uint32_t CoopMergeRounds() const { return m_coopMergeRounds; }
    const CellRoutingInfo& GetCellRoutingInfo() const { return m_cellInfo; }
    bool HasCellRoutingInfo() const { return m_hasCellInfo; }
    const LocalClueInfo& GetLocalClueInfo() const { return m_clueInfo; }
    bool HasLocalClueInfo() const { return m_hasClueInfo; }

private:
    void StartApplication() override;
    void StopApplication() override;

    uint32_t m_nodeId;
    ns3::Ptr<ns3::NetDevice> m_device;
    CellRoutingInfo m_cellInfo;
    bool m_hasCellInfo = false;
    LocalClueInfo m_clueInfo;
    bool m_hasClueInfo = false;

    // Layer-0 systematic reassembly state. Each fragment is "received" only
    // when every data sub-packet of that fragId arrives.
    std::map<uint16_t, uint32_t> m_fragMask;       // fragId -> sub-bitmask
    std::map<uint16_t, uint8_t>  m_fragSubTotal;   // fragId -> expected subTotal
    std::set<uint16_t>           m_directFragments;    // fully received from UAV PHY/MAC
    std::set<uint16_t>           m_distinctFragments;  // fully-received fragIds
    uint32_t m_l0RxTotal    = 0;  // every L0 packet (semantic + data)
    uint32_t m_l0DataSubRx  = 0;  // data sub-packets only
    uint32_t m_l0SemanticRx = 0;  // semantic preambles only
    uint32_t m_coopFragmentsGained = 0;
    uint32_t m_coopMergeRounds = 0;
};

}  // namespace ns3::wsn::uav

#endif  // GROUND_NODE_APP_H
