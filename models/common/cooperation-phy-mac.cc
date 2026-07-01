#include "cooperation-phy-mac.h"

#include <algorithm>
#include <cmath>

namespace ns3::wsn::uav {

CooperationPhyMacModel::CooperationPhyMacModel()
    : m_rng(ns3::CreateObject<ns3::UniformRandomVariable>()) {
    m_rng->SetAttribute("Min", ns3::DoubleValue(0.0));
    m_rng->SetAttribute("Max", ns3::DoubleValue(1.0));
}

void CooperationPhyMacModel::Configure(const CooperationPhyMacConfig& config) {
    m_config = config;
    if (m_config.packetsPerFragment == 0) {
        m_config.packetsPerFragment = 1;
    }
    m_config.intraCellFragmentSuccessProb =
        std::clamp(m_config.intraCellFragmentSuccessProb, 0.0, 1.0);
    m_config.interCellFragmentSuccessProb =
        std::clamp(m_config.interCellFragmentSuccessProb, 0.0, 1.0);
    m_config.intraCellManifestSuccessProb =
        std::clamp(m_config.intraCellManifestSuccessProb, 0.0, 1.0);
    m_config.interCellManifestSuccessProb =
        std::clamp(m_config.interCellManifestSuccessProb, 0.0, 1.0);
}

void CooperationPhyMacModel::ResetCounters() {
    m_counters = CooperationPhyMacCounters{};
}

uint32_t CooperationPhyMacModel::PacketBudget(CooperationLinkType linkType) const {
    return (linkType == CooperationLinkType::INTRA_CELL)
               ? m_config.intraCellPacketBudget
               : m_config.interCellPacketBudget;
}

double CooperationPhyMacModel::ManifestSuccessProbability(CooperationLinkType linkType) const {
    return (linkType == CooperationLinkType::INTRA_CELL)
               ? m_config.intraCellManifestSuccessProb
               : m_config.interCellManifestSuccessProb;
}

double CooperationPhyMacModel::FragmentSuccessProbability(CooperationLinkType linkType) const {
    return (linkType == CooperationLinkType::INTRA_CELL)
               ? m_config.intraCellFragmentSuccessProb
               : m_config.interCellFragmentSuccessProb;
}

double CooperationPhyMacModel::DataPacketSuccessProbability(CooperationLinkType linkType) const {
    double fragmentSuccess = FragmentSuccessProbability(linkType);
    uint32_t packetsPerFragment = std::max(1u, m_config.packetsPerFragment);
    if (fragmentSuccess <= 0.0) return 0.0;
    if (fragmentSuccess >= 1.0) return 1.0;
    return std::pow(fragmentSuccess, 1.0 / static_cast<double>(packetsPerFragment));
}

CooperationTransferResult CooperationPhyMacModel::TransferMissingFragments(
    CooperationLinkType linkType,
    const std::set<uint16_t>& offeredFragments,
    const std::set<uint16_t>& alreadyHave) {
    CooperationTransferResult result;
    m_counters.manifestPacketsAttempted++;
    if (linkType == CooperationLinkType::INTRA_CELL) {
        m_counters.intraCellTransferCalls++;
    } else {
        m_counters.interCellTransferCalls++;
    }

    if (m_rng->GetValue() > ManifestSuccessProbability(linkType)) {
        m_counters.manifestPacketsDropped++;
        return result;
    }
    result.manifestDelivered = true;
    m_counters.manifestPacketsDelivered++;

    uint32_t remainingPackets = PacketBudget(linkType);
    uint32_t packetsPerFragment = std::max(1u, m_config.packetsPerFragment);
    double packetSuccessProbability = DataPacketSuccessProbability(linkType);

    for (uint16_t fragId : offeredFragments) {
        if (remainingPackets < packetsPerFragment) break;
        if (alreadyHave.find(fragId) != alreadyHave.end()) continue;

        remainingPackets -= packetsPerFragment;
        result.fragmentTransfersAttempted++;
        m_counters.fragmentTransfersAttempted++;
        result.dataPacketsAttempted += packetsPerFragment;
        m_counters.dataPacketsAttempted += packetsPerFragment;

        uint32_t deliveredPacketsForFragment = 0;
        for (uint32_t i = 0; i < packetsPerFragment; i++) {
            if (m_rng->GetValue() <= packetSuccessProbability) {
                deliveredPacketsForFragment++;
            }
        }

        result.dataPacketsDelivered += deliveredPacketsForFragment;
        m_counters.dataPacketsDelivered += deliveredPacketsForFragment;
        uint32_t droppedPacketsForFragment = packetsPerFragment - deliveredPacketsForFragment;
        result.dataPacketsDropped += droppedPacketsForFragment;
        m_counters.dataPacketsDropped += droppedPacketsForFragment;

        if (deliveredPacketsForFragment == packetsPerFragment) {
            result.deliveredFragments.insert(fragId);
            result.fragmentTransfersCompleted++;
            m_counters.fragmentTransfersCompleted++;
            if (linkType == CooperationLinkType::INTRA_CELL) {
                m_counters.intraCellFragmentsDelivered++;
            } else {
                m_counters.interCellFragmentsDelivered++;
            }
        } else {
            result.fragmentTransfersIncomplete++;
            m_counters.fragmentTransfersIncomplete++;
        }
    }

    return result;
}

}  // namespace ns3::wsn::uav
