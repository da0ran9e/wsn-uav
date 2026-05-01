/*
 * Fragment model implementation
 */

#include "fragment-model.h"
#include <cmath>
#include <algorithm>

namespace ns3 {
namespace wsn {
namespace uav {

// ============================================================================
// FragmentCollection::Generate() - Pixel-Stride Interleaving Algorithm
// ============================================================================
// 
// Distributes a 416x416 pixel RGB image across K fragments.
// Each fragment gets an equal (or nearly equal) number of pixels.
// Fragment confidence is proportional to pixel count.
//
// The union probability C = 1 - ∏(1-p_i) recovers exactly the 
// masterConfidence value when all K fragments are received.

FragmentCollection FragmentCollection::Generate(uint32_t count, double masterConfidence) {
    FragmentCollection fc;
    
    // Image dimensions (YOLOv4 input)
    const uint32_t width = 416;
    const uint32_t height = 416;
    const uint32_t bytesPerPixel = 3;  // RGB
    
    uint32_t totalPixels = width * height;  // 173056
    
    // Distribute pixels evenly across K fragments
    uint32_t basePixelsPerFragment = totalPixels / count;
    uint32_t extraPixels = totalPixels % count;  // fragments 0..extraPixels-1 get +1
    
    for (uint32_t i = 0; i < count; i++) {
        Fragment frag;
        frag.id = i;
        
        // Pixel count for this fragment
        uint32_t pixelCount = basePixelsPerFragment + (i < extraPixels ? 1 : 0);
        
        // Evidence: how much confidence this fragment contributes
        // Formula: p_i = 1 - (1 - C_master)^(pixels_i / total_pixels)
        frag.evidence = EvidenceFromPixelCount(pixelCount, totalPixels, masterConfidence);
        
        // Payload: pixelCount * 3 bytes (RGB), filled with pattern
        uint32_t dataBytes = pixelCount * bytesPerPixel;
        frag.data.resize(dataBytes);
        for (uint32_t j = 0; j < dataBytes; j++) {
            frag.data[j] = static_cast<uint8_t>(i % 256);  // pattern for debugging
        }
        
        fc.Add(frag);
    }
    
    return fc;
}

// ============================================================================
// FragmentCollection::EvidenceFromPixelCount()
// ============================================================================

double FragmentCollection::EvidenceFromPixelCount(uint32_t pixelCount, uint32_t totalPixels,
                                                   double masterConfidence) {
    // Solve: C_master = 1 - (1 - p)^(pixels / totalPixels)
    // Let k = pixels / totalPixels
    // C = 1 - (1-p)^k
    // (1-p)^k = 1 - C
    // 1-p = (1-C)^(1/k)
    // p = 1 - (1-C)^(1/k)
    
    if (pixelCount == 0) return 0.0;
    
    double fraction = static_cast<double>(pixelCount) / static_cast<double>(totalPixels);
    double evidence = 1.0 - std::pow(1.0 - masterConfidence, 1.0 / fraction);
    
    // Clamp to valid range
    return std::max(0.001, std::min(0.999, evidence));
}

// ============================================================================
// FragmentCollection::Add()
// ============================================================================

bool FragmentCollection::Add(const Fragment& frag) {
    if (m_fragments.count(frag.id)) {
        return false;  // already have this fragment
    }
    m_fragments[frag.id] = frag;
    UpdateConfidence();
    return true;
}

// ============================================================================
// FragmentCollection::Has()
// ============================================================================

bool FragmentCollection::Has(uint32_t id) const {
    return m_fragments.count(id) > 0;
}

// ============================================================================
// FragmentCollection::Get()
// ============================================================================

const Fragment* FragmentCollection::Get(uint32_t id) const {
    auto it = m_fragments.find(id);
    if (it == m_fragments.end()) return nullptr;
    return &it->second;
}

// ============================================================================
// FragmentCollection::GetTotalConfidence()
// ============================================================================

double FragmentCollection::GetTotalConfidence() const {
    return m_totalConfidence;
}

// ============================================================================
// FragmentCollection::UpdateConfidence()
// ============================================================================
// 
// Union probability: C = 1 - ∏(1 - evidence_i)

void FragmentCollection::UpdateConfidence() {
    if (m_fragments.empty()) {
        m_totalConfidence = 0.0;
        return;
    }
    
    double product = 1.0;
    for (const auto& [id, frag] : m_fragments) {
        product *= (1.0 - frag.evidence);
    }
    
    m_totalConfidence = 1.0 - product;
}

// ============================================================================
// FragmentCollection::GetIds()
// ============================================================================

std::vector<uint32_t> FragmentCollection::GetIds() const {
    std::vector<uint32_t> ids;
    for (const auto& [id, frag] : m_fragments) {
        ids.push_back(id);
    }
    std::sort(ids.begin(), ids.end());
    return ids;
}

// ============================================================================
// FragmentCollection::GetPresenceMask()
// ============================================================================

std::vector<bool> FragmentCollection::GetPresenceMask() const {
    uint32_t maxId = 0;
    for (const auto& [id, frag] : m_fragments) {
        maxId = std::max(maxId, id);
    }
    
    std::vector<bool> mask(maxId + 1, false);
    for (const auto& [id, frag] : m_fragments) {
        mask[id] = true;
    }
    return mask;
}

}  // namespace uav
}  // namespace wsn
}  // namespace ns3
