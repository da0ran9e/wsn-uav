#include "target-profile.h"

namespace ns3::uavsar {

TargetProfile TargetProfile::Generate(const TargetProfileConfig& cfg) {
    TargetProfile tp;
    uint32_t id = 0;
    auto add = [&](Layer layer, uint32_t count, double util, uint32_t bytes) {
        for (uint32_t i = 0; i < count; i++) {
            Fragment f;
            f.id = id++;
            f.layer = layer;
            f.cueType = static_cast<CueType>(i % 7);  // L0 cues cycle through types
            f.utility = util;
            f.sizeBytes = bytes;
            tp.m_frags.push_back(f);
        }
    };
    add(Layer::L0_IDENTITY, cfg.l0Count, cfg.l0Utility, cfg.l0Bytes);
    add(Layer::L1_DESCRIPTOR, cfg.l1Count, cfg.l1Utility, cfg.l1Bytes);
    add(Layer::L2_DETAIL, cfg.l2Count, cfg.l2Utility, cfg.l2Bytes);
    add(Layer::L3_FULL, cfg.l3Count, cfg.l3Utility, cfg.l3Bytes);
    return tp;
}

std::vector<Fragment> TargetProfile::OfLayer(Layer l) const {
    std::vector<Fragment> out;
    for (const auto& f : m_frags) if (f.layer == l) out.push_back(f);
    return out;
}

uint32_t TargetProfile::TotalBytes() const {
    uint32_t t = 0;
    for (const auto& f : m_frags) t += f.sizeBytes;
    return t;
}

double TargetProfile::Confidence(const std::vector<Fragment>& received) {
    double prodMiss = 1.0;
    for (const auto& f : received) prodMiss *= (1.0 - f.utility);
    return 1.0 - prodMiss;
}

}  // namespace ns3::uavsar
