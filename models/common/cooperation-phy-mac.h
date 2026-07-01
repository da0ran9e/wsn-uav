#ifndef WSN_UAV_COOPERATION_PHY_MAC_H
#define WSN_UAV_COOPERATION_PHY_MAC_H

#include "ns3/ptr.h"
#include "ns3/random-variable-stream.h"
#include "ns3/double.h"

#include <cstdint>
#include <set>

namespace ns3::wsn::uav {

enum class CooperationLinkType : uint8_t {
    INTRA_CELL = 0,
    INTER_CELL = 1,
};

struct CooperationPhyMacConfig {
    uint32_t packetsPerFragment = 1;
    uint32_t intraCellPacketBudget = 64;
    uint32_t interCellPacketBudget = 160;
    double intraCellManifestSuccessProb = 0.98;
    double interCellManifestSuccessProb = 0.95;
    // Target probability that a complete fragment transfer succeeds. The model
    // converts this to per-data-packet probability using packetsPerFragment.
    double intraCellFragmentSuccessProb = 0.92;
    double interCellFragmentSuccessProb = 0.82;
};

struct CooperationPhyMacCounters {
    uint64_t manifestPacketsAttempted = 0;
    uint64_t manifestPacketsDelivered = 0;
    uint64_t manifestPacketsDropped = 0;
    uint64_t dataPacketsAttempted = 0;
    uint64_t dataPacketsDelivered = 0;
    uint64_t dataPacketsDropped = 0;
    uint64_t fragmentTransfersAttempted = 0;
    uint64_t fragmentTransfersCompleted = 0;
    uint64_t fragmentTransfersIncomplete = 0;
    uint64_t intraCellFragmentsDelivered = 0;
    uint64_t interCellFragmentsDelivered = 0;
    uint64_t intraCellTransferCalls = 0;
    uint64_t interCellTransferCalls = 0;
};

struct CooperationTransferResult {
    std::set<uint16_t> deliveredFragments;
    uint32_t dataPacketsAttempted = 0;
    uint32_t dataPacketsDelivered = 0;
    uint32_t dataPacketsDropped = 0;
    uint32_t fragmentTransfersAttempted = 0;
    uint32_t fragmentTransfersCompleted = 0;
    uint32_t fragmentTransfersIncomplete = 0;
    bool manifestDelivered = false;
};

class CooperationPhyMacModel {
public:
    CooperationPhyMacModel();

    void Configure(const CooperationPhyMacConfig& config);
    void ResetCounters();

    CooperationTransferResult TransferMissingFragments(
        CooperationLinkType linkType,
        const std::set<uint16_t>& offeredFragments,
        const std::set<uint16_t>& alreadyHave);

    const CooperationPhyMacConfig& Config() const { return m_config; }
    const CooperationPhyMacCounters& Counters() const { return m_counters; }

private:
    uint32_t PacketBudget(CooperationLinkType linkType) const;
    double ManifestSuccessProbability(CooperationLinkType linkType) const;
    double FragmentSuccessProbability(CooperationLinkType linkType) const;
    double DataPacketSuccessProbability(CooperationLinkType linkType) const;

    CooperationPhyMacConfig m_config;
    CooperationPhyMacCounters m_counters;
    ns3::Ptr<ns3::UniformRandomVariable> m_rng;
};

}  // namespace ns3::wsn::uav

#endif  // WSN_UAV_COOPERATION_PHY_MAC_H
