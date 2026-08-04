#include "clue-field.h"

#include <cmath>
#include <random>

namespace ns3::uavsar {

std::map<uint32_t, ClueInfo> BuildClueField(const std::vector<CluePos>& nodes,
                                            const ClueFieldConfig& cfg) {
    std::map<uint32_t, ClueInfo> out;

    // audit W7: distances are to the victim's CONTINUOUS position, not to the
    // node that happens to be nearest it.
    const double tx = cfg.victimX, ty = cfg.victimY;

    std::mt19937 rng(cfg.seed);
    std::uniform_real_distribution<double> u01(0.0, 1.0);
    std::normal_distribution<double> gauss(0.0, 1.0);

    for (const auto& n : nodes) {
        ClueInfo c;
        c.id = n.id;
        c.x = n.x;
        c.y = n.y;
        c.distToTarget = std::hypot(n.x - tx, n.y - ty);
        c.isTarget = (n.id == cfg.targetNodeId);

        double qTrue;
        if (c.distToTarget <= cfg.weakRadius) {
            // spatial decay from the victim; strongest closest to it
            qTrue = cfg.maxQuality * std::exp(-c.distToTarget / cfg.decay);
            if (c.distToTarget > cfg.strongRadius) qTrue *= 0.6;  // weaker halo
        } else {
            // background: rare spurious matches
            if (u01(rng) < cfg.bgFalsePositiveRate) {
                c.isFalsePositive = true;
                qTrue = cfg.maxNoiseQuality * u01(rng);
            } else {
                qTrue = 0.0;
            }
        }

        // audit M9/W3: the node reports what its detector measured, not the
        // field. One draw per node per run. This is what makes a false positive
        // possible near the victim and a miss possible on it -- i.e. it is the
        // detector's ROC, emergent from the noise rather than hand-set.
        if (cfg.senseSigma > 0.0) {
            double qMeas = qTrue + cfg.senseSigma * gauss(rng);
            c.clueQuality = std::min(1.0, std::max(0.0, qMeas));
            if (qTrue <= 0.0 && c.clueQuality > 0.0) c.isFalsePositive = true;
        } else {
            c.clueQuality = qTrue;
        }
        out.emplace(n.id, c);
    }
    return out;
}

}  // namespace ns3::uavsar
