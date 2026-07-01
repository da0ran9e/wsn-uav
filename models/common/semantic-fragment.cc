#include "semantic-fragment.h"

#include <algorithm>
#include <numeric>
#include <stdexcept>

namespace ns3::wsn::uav {

namespace {

constexpr uint32_t kMaxTargetProfileFragments = 255;

// Per-fragment payload size in bytes, per layer.
constexpr uint32_t kLayerFragmentBytes[kNumSemanticLayers] = {2500, 256, 512, 4096};

// Per-fragment recognition utility, per layer. Placeholder values for the
// noisy-OR confidence model; tune as the recognition model firms up.
constexpr double kLayerUtility[kNumSemanticLayers] = {0.30, 0.12, 0.05, 0.40};

// Distributes `total` items across the layers proportional to `weights`,
// using the largest-remainder method so the counts sum exactly to `total`.
std::array<uint32_t, kNumSemanticLayers> DistributeCounts(
    uint32_t total, const std::array<uint32_t, kNumSemanticLayers>& weights) {
    std::array<uint32_t, kNumSemanticLayers> counts{0, 0, 0, 0};
    uint32_t weightSum = std::accumulate(weights.begin(), weights.end(), 0u);
    if (weightSum == 0) return counts;

    std::array<double, kNumSemanticLayers> remainder{};
    uint32_t assigned = 0;
    for (uint32_t i = 0; i < kNumSemanticLayers; i++) {
        double exact = static_cast<double>(total) * weights[i] / weightSum;
        counts[i] = static_cast<uint32_t>(exact);
        remainder[i] = exact - counts[i];
        assigned += counts[i];
    }
    // Hand the leftover units to the layers with the largest fractional part.
    while (assigned < total) {
        uint32_t best = 0;
        for (uint32_t i = 1; i < kNumSemanticLayers; i++) {
            if (remainder[i] > remainder[best]) best = i;
        }
        counts[best]++;
        remainder[best] = -1.0;  // don't pick this layer again
        assigned++;
    }
    return counts;
}

}  // namespace

TargetProfile TargetProfile::Generate(
    uint32_t totalFragments,
    std::array<uint32_t, kNumSemanticLayers> layerSplit,
    uint32_t fullPayloadBytes) {
    if (totalFragments > kMaxTargetProfileFragments) {
        throw std::invalid_argument("TargetProfile::Generate supports at most 255 fragments");
    }

    TargetProfile profile;

    auto counts = DistributeCounts(totalFragments, layerSplit);

    uint32_t nextId = 0;
    for (uint32_t l = 0; l < kNumSemanticLayers; l++) {
        SemanticLayer layer = static_cast<SemanticLayer>(l);

        // Full-payload mode: layer 3 collapses to a single large fragment.
        if (layer == SemanticLayer::FULL_REFERENCE && fullPayloadBytes > 0) {
            profile.m_fragments.push_back(
                {nextId++, layer, SemanticType::NONE, kLayerUtility[l],
                 fullPayloadBytes});
            continue;
        }

        for (uint32_t k = 0; k < counts[l]; k++) {
            // Layer-0 fragments carry a cycled semantic-atom type; deeper
            // layers have no atom type.
            SemanticType st = (layer == SemanticLayer::IDENTITY_CUE)
                ? static_cast<SemanticType>(1 + (k % kNumSemanticTypes))
                : SemanticType::NONE;
            profile.m_fragments.push_back(
                {nextId++, layer, st, kLayerUtility[l], kLayerFragmentBytes[l]});
        }
    }
    if (profile.m_fragments.size() > kMaxTargetProfileFragments) {
        throw std::invalid_argument("TargetProfile::Generate produced more than 255 fragments");
    }
    return profile;
}

std::vector<Fragment> TargetProfile::Layer(SemanticLayer l) const {
    std::vector<Fragment> out;
    for (const Fragment& f : m_fragments) {
        if (f.layer == l) out.push_back(f);
    }
    return out;
}

uint32_t TargetProfile::LayerCount(SemanticLayer l) const {
    uint32_t n = 0;
    for (const Fragment& f : m_fragments) {
        if (f.layer == l) n++;
    }
    return n;
}

uint32_t TargetProfile::TotalBytes() const {
    uint32_t total = 0;
    for (const Fragment& f : m_fragments) total += f.sizeBytes;
    return total;
}

double TargetProfile::Confidence(const std::vector<Fragment>& received) {
    double product = 1.0;
    for (const Fragment& f : received) {
        double p = std::clamp(f.utility, 0.0, 0.999999);
        product *= (1.0 - p);
    }
    return 1.0 - product;
}

}  // namespace ns3::wsn::uav
