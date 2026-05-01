#include "confidence-model.h"

namespace ns3 {
namespace wsn {
namespace uav {

ConfidenceModel::ConfidenceModel(uint32_t nodeId, uint32_t expectedCount)
    : m_nodeId(nodeId), m_expectedCount(expectedCount) {}

bool ConfidenceModel::OnFragment(const Fragment& frag, bool fromUav) {
    if (m_received.Has(frag.id)) {
        return false;  // already have it
    }
    
    bool ok = m_received.Add(frag);
    if (ok) {
        if (fromUav) {
            m_fromUav++;
        } else {
            m_fromCoop++;
        }
    }
    return ok;
}

double ConfidenceModel::GetConfidence() const {
    if (m_expectedCount == 0) return 0.0;
    return static_cast<double>(m_received.Size()) / static_cast<double>(m_expectedCount);
}

bool ConfidenceModel::Has(uint32_t fragmentId) const {
    return m_received.Has(fragmentId);
}

bool ConfidenceModel::Above(double threshold) const {
    return GetConfidence() >= threshold;
}

bool ConfidenceModel::IsComplete() const {
    return m_received.Size() >= m_expectedCount;
}

std::set<uint32_t> ConfidenceModel::GetMissingIds() const {
    std::set<uint32_t> missing;
    for (uint32_t i = 0; i < m_expectedCount; i++) {
        if (!m_received.Has(i)) {
            missing.insert(i);
        }
    }
    return missing;
}

}  // namespace uav
}  // namespace wsn
}  // namespace ns3
