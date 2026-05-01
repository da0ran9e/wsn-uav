/*
 * Per-node confidence tracking with fragment reception history
 */

#ifndef WSN_UAV_CONFIDENCE_MODEL_H
#define WSN_UAV_CONFIDENCE_MODEL_H

#include "fragment-model.h"
#include <cstdint>
#include <set>

namespace ns3 {
namespace wsn {
namespace uav {

class ConfidenceModel {
public:
    explicit ConfidenceModel(uint32_t nodeId, uint32_t expectedCount);
    
    // Process incoming fragment: returns true if state changed
    bool OnFragment(const Fragment& frag, bool fromUav);
    
    // Query
    double GetConfidence() const;
    bool Has(uint32_t fragmentId) const;
    bool Above(double threshold) const;
    bool IsComplete() const;
    
    // Missing fragments (for cooperation manifest)
    std::set<uint32_t> GetMissingIds() const;
    
    // Statistics
    uint32_t GetCountFromUav() const { return m_fromUav; }
    uint32_t GetCountFromCoop() const { return m_fromCoop; }
    uint32_t GetReceivedCount() const { return m_received.Size(); }
    
    const FragmentCollection& GetFragments() const { return m_received; }
    
private:
    uint32_t m_nodeId;
    uint32_t m_expectedCount;
    FragmentCollection m_received;
    uint32_t m_fromUav = 0;
    uint32_t m_fromCoop = 0;
};

}  // namespace uav
}  // namespace wsn
}  // namespace ns3

#endif  // WSN_UAV_CONFIDENCE_MODEL_H
