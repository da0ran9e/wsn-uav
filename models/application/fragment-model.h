/*
 * WSN-UAV Module: Fragment Data Structures
 * 
 * Port from src/wsn/model/routing/scenario4/fragment.h
 */

#ifndef WSN_UAV_FRAGMENT_MODEL_H
#define WSN_UAV_FRAGMENT_MODEL_H

#include <cstdint>
#include <vector>
#include <map>
#include <cmath>

namespace ns3 {
namespace wsn {
namespace uav {

// ============================================================================
// Fragment Struct
// ============================================================================

struct Fragment {
    uint32_t id = 0;  // fragment index [0, K)
    double evidence = 0.0;  // p_i ∈ (0, 1) - individual confidence
    std::vector<uint8_t> data;  // payload bytes
};

// ============================================================================
// FragmentCollection Class
// ============================================================================

class FragmentCollection {
public:
    // Generate K fragments with pixel-stride interleaving
    // Algorithm: stride over 416x416x3 pixel image, distribute evidence 
    //           proportional to pixel count per fragment
    static FragmentCollection Generate(uint32_t count, double masterConfidence = 0.90);
    
    // Add/check fragments
    bool Add(const Fragment& frag);
    bool Has(uint32_t id) const;
    const Fragment* Get(uint32_t id) const;
    
    // Aggregate confidence using union probability
    // C = 1 - ∏(1 - evidence_i) for all received fragments
    double GetTotalConfidence() const;
    
    // Query
    uint32_t Size() const { return m_fragments.size(); }
    const std::map<uint32_t, Fragment>& All() const { return m_fragments; }
    std::vector<uint32_t> GetIds() const;
    
    // For cooperation: manifest = set of known fragment IDs
    std::vector<bool> GetPresenceMask() const;  // bit vector: has frag i
    
private:
    std::map<uint32_t, Fragment> m_fragments;  // id → Fragment
    double m_totalConfidence = 0.0;  // union probability
    
    void UpdateConfidence();  // recompute from fragments
    
    // Helper: evidence from pixel count
    static double EvidenceFromPixelCount(uint32_t pixelCount, uint32_t totalPixels, 
                                         double masterConfidence);
};

}  // namespace uav
}  // namespace wsn
}  // namespace ns3

#endif  // WSN_UAV_FRAGMENT_MODEL_H
