#ifndef UAV_SAR_TARGET_PROFILE_H
#define UAV_SAR_TARGET_PROFILE_H

// The missing person's search data, split into semantic fragments across four
// layers (clean reimplementation; ref: main's semantic-fragment):
//   L0 IDENTITY_CUE     — many, tiny, high-recognition (COLOR/SILHOUETTE/…) → FAST
//   L1 SEMANTIC_DESCRIPTOR — few, small                                     → FAST
//   L2 LOCAL_DETAIL     — medium/large                                      → DATA
//   L3 FULL_REFERENCE   — the full image/embedding                          → DATA
//
// Each fragment has a recognition utility p_i in (0,1). A node's confidence
// given a received subset is the union probability  C = 1 - ∏(1 - p_i).
// CV is NOT simulated; payloads are opaque byte counts for radio cost only.

#include <cstdint>
#include <vector>

namespace ns3::uavsar {

enum class Layer : uint8_t { L0_IDENTITY = 0, L1_DESCRIPTOR = 1, L2_DETAIL = 2, L3_FULL = 3 };
enum class CueType : uint8_t { COLOR, SILHOUETTE, BODY_RATIO, EMBEDDING, LAYOUT, POSE, GAIT };

struct Fragment {
    uint32_t id = 0;
    Layer layer = Layer::L0_IDENTITY;
    CueType cueType = CueType::COLOR;
    double utility = 0.0;     // p_i in (0,1)
    uint32_t sizeBytes = 0;
};

struct TargetProfileConfig {
    uint32_t l0Count = 8;
    uint32_t l1Count = 2;
    uint32_t l2Count = 4;
    uint32_t l3Count = 1;
    // per-layer per-fragment utility
    double l0Utility = 0.18;
    double l1Utility = 0.40;
    double l2Utility = 0.60;
    double l3Utility = 0.95;
    // per-layer fragment size (bytes)
    uint32_t l0Bytes = 150;
    uint32_t l1Bytes = 600;
    uint32_t l2Bytes = 4000;
    uint32_t l3Bytes = 16000;
};

class TargetProfile {
public:
    static TargetProfile Generate(const TargetProfileConfig& cfg = {});

    const std::vector<Fragment>& All() const { return m_frags; }
    std::vector<Fragment> OfLayer(Layer l) const;
    uint32_t Size() const { return (uint32_t)m_frags.size(); }
    uint32_t TotalBytes() const;

    // Union-probability confidence for a received subset of fragments.
    static double Confidence(const std::vector<Fragment>& received);

private:
    std::vector<Fragment> m_frags;
};

}  // namespace ns3::uavsar

#endif  // UAV_SAR_TARGET_PROFILE_H
