#include "uav-dissemination-model.h"

#include "ns3/core-module.h"
#include "ns3/mac16-address.h"

#include <algorithm>
#include <cstring>
#include <limits>

namespace ns3::wsn::uav {

namespace {
constexpr uint8_t MSG_L0_DATA      = 5;
constexpr uint8_t MSG_L0_SEMANTIC  = 6;
constexpr uint8_t MSG_FULL_UNICAST = 7;
constexpr uint32_t L0_DATA_BYTES = 92;
constexpr uint32_t L0_SEMANTIC_BYTES = 100;
}  // namespace

UavDisseminationModel::UavDisseminationModel()
    : m_rng(CreateObject<UniformRandomVariable>()) {
}

void UavDisseminationModel::Start(const UavDisseminationConfig& config) {
    m_model = config.model;
    m_fragments = config.fragments;
    m_dataSubPacketsPerFragment = config.dataSubPacketsPerFragment;
    m_sensorPositions = config.sensorPositions;
    m_groundNodeIds = config.groundNodeIds;
    m_groundNodeAddresses = config.groundNodeAddresses;
    m_radiusMeters = config.radiusMeters;

    m_curFragIdx = 0;
    m_curStep = 0;
    m_unicastFragIdxByNode.assign(m_sensorPositions.size(), 0);
    m_unicastSubIdxByNode.assign(m_sensorPositions.size(), 0);
    m_unicastNodeComplete.assign(m_sensorPositions.size(), false);
    m_unicastCursor = 0;
    m_unicastCompletedNodes = 0;
    m_pendingUnicast = false;
    m_pendingUnicastNode = 0;
    m_txSuccessCount = 0;
    m_txAttemptCount = 0;
    m_txFailCount = 0;
    m_active = !m_fragments.empty() && m_dataSubPacketsPerFragment > 0;
}

void UavDisseminationModel::Stop() {
    m_active = false;
    m_pendingUnicast = false;
}

const char* UavDisseminationModel::ModelName() const {
    switch (m_model) {
        case BroadcastModel::CYCLIC: return "cyclic";
        case BroadcastModel::RANDOM: return "random";
        case BroadcastModel::UNICAST_FULL: return "unicast-full";
        case BroadcastModel::UTILITY_WEIGHTED: return "utility-weighted";
    }
    return "unknown";
}

UavDisseminationPacket UavDisseminationModel::NextPacket(const Vector& uavPosition) {
    if (!m_active) return {};
    if (m_model == BroadcastModel::UNICAST_FULL) {
        return BuildUnicastFullPacket(uavPosition);
    }
    return BuildBroadcastPacket();
}

void UavDisseminationModel::NotifyTxResult(bool sent) {
    ++m_txAttemptCount;
    if (sent) {
        ++m_txSuccessCount;
        if (m_pendingUnicast) {
            AdvanceUnicastAfterSuccess();
        }
    } else {
        ++m_txFailCount;
    }
    m_pendingUnicast = false;
}

UavDisseminationPacket UavDisseminationModel::BuildBroadcastPacket() {
    if (m_fragments.empty()) return {};

    size_t selectedIdx = m_curFragIdx;
    if (m_model == BroadcastModel::UTILITY_WEIGHTED && m_curStep == 0 &&
        m_fragments.size() > 1) {
        selectedIdx = PickWeightedFragment();
        m_curFragIdx = selectedIdx;
    } else if (m_model == BroadcastModel::RANDOM && m_curStep == 0 && m_fragments.size() > 1) {
        selectedIdx = static_cast<size_t>(
            m_rng->GetInteger(0, static_cast<uint32_t>(m_fragments.size() - 1)));
        selectedIdx = std::min(selectedIdx, m_fragments.size() - 1);
        m_curFragIdx = selectedIdx;
    }

    const Fragment& f = m_fragments[selectedIdx];
    uint16_t fragId = static_cast<uint16_t>(f.id);
    bool isSemantic = (m_curStep == 0);
    uint32_t pktSize = isSemantic ? L0_SEMANTIC_BYTES : L0_DATA_BYTES;
    std::vector<uint8_t> buf(pktSize, 0);
    uint8_t* p = buf.data();

    if (isSemantic) {
        *p++ = MSG_L0_SEMANTIC;
        std::memcpy(p, &fragId, 2); p += 2;
        *p++ = static_cast<uint8_t>(f.semanticType);
    } else {
        uint8_t subIdx = static_cast<uint8_t>(m_curStep - 1);
        *p++ = MSG_L0_DATA;
        std::memcpy(p, &fragId, 2); p += 2;
        *p++ = subIdx;
        *p++ = static_cast<uint8_t>(m_dataSubPacketsPerFragment);
    }

    m_curStep++;
    if (m_curStep > m_dataSubPacketsPerFragment) {
        m_curStep = 0;
        if (m_model == BroadcastModel::CYCLIC) {
            m_curFragIdx = (m_curFragIdx + 1) % m_fragments.size();
        }
    }

    UavDisseminationPacket out;
    out.valid = true;
    out.payload = std::move(buf);
    out.destination = Mac16Address("ff:ff");
    return out;
}

UavDisseminationPacket UavDisseminationModel::BuildUnicastFullPacket(const Vector& uavPosition) {
    if (m_groundNodeAddresses.size() < m_sensorPositions.size() ||
        m_groundNodeIds.size() < m_sensorPositions.size() ||
        m_unicastNodeComplete.size() != m_sensorPositions.size()) {
        return {};
    }
    if (m_unicastCompletedNodes >= m_sensorPositions.size()) {
        m_active = false;
        return {};
    }

    size_t selected = m_sensorPositions.size();
    double bestDist2 = std::numeric_limits<double>::max();
    double r2 = m_radiusMeters * m_radiusMeters;
    for (size_t i = 0; i < m_sensorPositions.size(); ++i) {
        size_t idx = (m_unicastCursor + i) % m_sensorPositions.size();
        if (m_unicastNodeComplete[idx]) continue;
        const Vector& s = m_sensorPositions[idx];
        double dx = s.x - uavPosition.x;
        double dy = s.y - uavPosition.y;
        double d2 = dx * dx + dy * dy;
        if (d2 <= r2 && d2 < bestDist2) {
            bestDist2 = d2;
            selected = idx;
        }
    }
    if (selected >= m_sensorPositions.size()) return {};

    uint16_t fragOrdinal = m_unicastFragIdxByNode[selected];
    if (fragOrdinal >= m_fragments.size()) {
        m_unicastNodeComplete[selected] = true;
        ++m_unicastCompletedNodes;
        return {};
    }

    const Fragment& f = m_fragments[fragOrdinal];
    uint16_t destNodeId = static_cast<uint16_t>(
        std::min<uint32_t>(m_groundNodeIds[selected], std::numeric_limits<uint16_t>::max()));
    uint16_t fragId = static_cast<uint16_t>(f.id);
    uint8_t subIdx = m_unicastSubIdxByNode[selected];

    std::vector<uint8_t> buf(L0_DATA_BYTES, 0);
    uint8_t* p = buf.data();
    *p++ = MSG_FULL_UNICAST;
    std::memcpy(p, &destNodeId, 2); p += 2;
    std::memcpy(p, &fragId, 2); p += 2;
    *p++ = subIdx;
    *p++ = static_cast<uint8_t>(m_dataSubPacketsPerFragment);

    m_pendingUnicast = true;
    m_pendingUnicastNode = selected;

    UavDisseminationPacket out;
    out.valid = true;
    out.payload = std::move(buf);
    out.destination = m_groundNodeAddresses[selected];
    return out;
}

size_t UavDisseminationModel::PickWeightedFragment() const {
    double total = 0.0;
    for (const Fragment& f : m_fragments) {
        total += FragmentWeight(f);
    }
    if (total <= 0.0) return m_curFragIdx;

    double draw = m_rng->GetValue(0.0, total);
    double acc = 0.0;
    for (size_t i = 0; i < m_fragments.size(); ++i) {
        acc += FragmentWeight(m_fragments[i]);
        if (draw <= acc) return i;
    }
    return m_fragments.size() - 1;
}

double UavDisseminationModel::FragmentWeight(const Fragment& fragment) const {
    double semanticMultiplier = 1.0;
    switch (fragment.semanticType) {
        case SemanticType::COLOR:      semanticMultiplier = 2.00; break;
        case SemanticType::SILHOUETTE: semanticMultiplier = 1.70; break;
        case SemanticType::BODY_RATIO: semanticMultiplier = 1.45; break;
        case SemanticType::POSE:       semanticMultiplier = 1.20; break;
        case SemanticType::GAIT:       semanticMultiplier = 1.15; break;
        case SemanticType::LAYOUT:     semanticMultiplier = 1.05; break;
        case SemanticType::EMBEDDING:  semanticMultiplier = 1.00; break;
        case SemanticType::NONE:       semanticMultiplier = 1.00; break;
    }
    return std::max(0.001, fragment.utility * semanticMultiplier);
}

void UavDisseminationModel::AdvanceUnicastAfterSuccess() {
    if (m_pendingUnicastNode >= m_unicastFragIdxByNode.size()) return;
    size_t selected = m_pendingUnicastNode;
    uint8_t subIdx = m_unicastSubIdxByNode[selected] + 1;
    uint16_t fragOrdinal = m_unicastFragIdxByNode[selected];
    if (subIdx >= m_dataSubPacketsPerFragment) {
        subIdx = 0;
        ++fragOrdinal;
        if (fragOrdinal >= m_fragments.size() && !m_unicastNodeComplete[selected]) {
            m_unicastNodeComplete[selected] = true;
            ++m_unicastCompletedNodes;
            m_unicastCursor = (selected + 1) % m_sensorPositions.size();
        }
    }
    m_unicastSubIdxByNode[selected] = subIdx;
    m_unicastFragIdxByNode[selected] = fragOrdinal;
    if (!m_unicastNodeComplete[selected]) {
        m_unicastCursor = selected;
    }
}

}  // namespace ns3::wsn::uav
