#include "clue-field.h"

#include <cmath>
#include <random>

namespace ns3::uavsar {

std::map<uint32_t, ClueInfo> BuildClueField(const std::vector<CluePos>& nodes,
                                            const ClueFieldConfig& cfg) {
    std::map<uint32_t, ClueInfo> out;

    // Locate the victim's node position.
    double tx = 0, ty = 0;
    for (const auto& n : nodes)
        if (n.id == cfg.targetNodeId) { tx = n.x; ty = n.y; }

    std::mt19937 rng(cfg.seed);
    std::uniform_real_distribution<double> u01(0.0, 1.0);

    for (const auto& n : nodes) {
        ClueInfo c;
        c.id = n.id;
        c.x = n.x;
        c.y = n.y;
        c.distToTarget = std::hypot(n.x - tx, n.y - ty);
        c.isTarget = (n.id == cfg.targetNodeId);

        if (c.distToTarget <= cfg.weakRadius) {
            // spatial decay from the victim; strongest at the target node
            double q = cfg.maxQuality * std::exp(-c.distToTarget / cfg.decay);
            if (c.distToTarget > cfg.strongRadius) q *= 0.6;  // weaker halo
            c.clueQuality = q;
        } else {
            // background: rare spurious matches
            if (u01(rng) < cfg.bgFalsePositiveRate) {
                c.isFalsePositive = true;
                c.clueQuality = cfg.maxNoiseQuality * u01(rng);
            } else {
                c.clueQuality = 0.0;
            }
        }
        out.emplace(n.id, c);
    }
    return out;
}

}  // namespace ns3::uavsar
