#ifndef SEMANTIC_FRAGMENT_H
#define SEMANTIC_FRAGMENT_H

#include <array>
#include <cstdint>
#include <vector>

namespace ns3::wsn::uav {

// Coarse-to-fine semantic layers of the target identity package. Layer 0
// carries the smallest, highest-utility identity cues; layer 3 is the full
// reference payload reserved for final verification (Stage D in the story).
enum class SemanticLayer : uint8_t {
    IDENTITY_CUE        = 0,
    SEMANTIC_DESCRIPTOR = 1,
    LOCAL_DETAIL        = 2,
    FULL_REFERENCE      = 3,
};

constexpr uint32_t kNumSemanticLayers = 4;

// Layer-0 semantic atom types — the elementary coarse identity cues (story
// v1.2). Layers 1-3 carry no atom type and use NONE.
enum class SemanticType : uint8_t {
    NONE       = 0,
    COLOR      = 1,
    SILHOUETTE = 2,
    BODY_RATIO = 3,
    EMBEDDING  = 4,
    LAYOUT     = 5,
    POSE       = 6,
    GAIT       = 7,
};

constexpr uint32_t kNumSemanticTypes = 7;  // COLOR..GAIT

// One semantic fragment. Abstract (metadata only): no real payload bytes are
// stored — `sizeBytes` exists purely to model radio transmission cost.
struct Fragment {
    uint32_t      id;
    SemanticLayer layer;
    SemanticType  semanticType;  // identity-cue type (L0); NONE for L1-L3
    double        utility;       // p_i in (0,1): recognition/search value
    uint32_t      sizeBytes;     // payload size for radio cost modelling
};

// A multi-layer semantic target profile — the BS-owned evidence package the
// UAV disseminates. Fragments have unequal importance; a partial set is still
// useful; confidence grows progressively as more fragments are received.
class TargetProfile {
public:
    // Builds `totalFragments` fragments distributed across the 4 layers by
    // the relative weights in `layerSplit` (largest-remainder rounding). The
    // default {120,16,32,8} with totalFragments=176 yields the experiment
    // profile: L0 120x500B (=60KB master), L1 16x256B, L2 32x512B, L3 8x4096B.
    // Capped at 255 fragments so fragment ids fit in one byte on the wire.
    //
    // fullPayloadBytes > 0 overrides layer 3: a single fragment of that size
    // replaces the multiple layer-3 fragments (Stage D full-image delivery).
    static TargetProfile Generate(
        uint32_t totalFragments = 216,
        std::array<uint32_t, kNumSemanticLayers> layerSplit = {180, 8, 24, 4},
        uint32_t fullPayloadBytes = 0);

    const std::vector<Fragment>& All() const { return m_fragments; }
    std::vector<Fragment>        Layer(SemanticLayer l) const;
    uint32_t                     Size() const { return m_fragments.size(); }
    uint32_t                     LayerCount(SemanticLayer l) const;
    uint32_t                     TotalBytes() const;

    // Noisy-OR confidence from a received subset: C = 1 - prod(1 - p_i).
    // Monotone, diminishing returns — models progressive recognition.
    static double Confidence(const std::vector<Fragment>& received);

private:
    std::vector<Fragment> m_fragments;
};

}  // namespace ns3::wsn::uav

#endif  // SEMANTIC_FRAGMENT_H
