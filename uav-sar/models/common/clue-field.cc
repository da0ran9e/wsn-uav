#include "clue-field.h"

#include <algorithm>
#include <cmath>
#include <random>

namespace ns3::uavsar {

namespace {
// The spatial response of the detector to ONE object at distance d. Victim and
// confusable objects share it deliberately: if the two used different shapes the
// aggregation layer could tell them apart from shape alone, which is exactly the
// discriminating power the "same jacket" case says we do not have.
double Kernel(double d, const ClueFieldConfig& cfg) {
    if (d > cfg.weakRadius) return 0.0;
    double q = cfg.maxQuality * std::exp(-d / cfg.decay);
    if (d > cfg.strongRadius) q *= 0.6;   // weaker halo
    return q;
}
}  // namespace

std::vector<ClutterSource> BuildClutter(const std::vector<CluePos>& nodes,
                                        const ClueFieldConfig& cfg) {
    std::vector<ClutterSource> out;
    if (cfg.clutterCount == 0 || nodes.empty()) return out;

    double x0 = nodes[0].x, x1 = nodes[0].x, y0 = nodes[0].y, y1 = nodes[0].y;
    for (const auto& n : nodes) {
        x0 = std::min(x0, n.x); x1 = std::max(x1, n.x);
        y0 = std::min(y0, n.y); y1 = std::max(y1, n.y);
    }
    if (cfg.areaW > 0) { x1 = x0 + cfg.areaW; }
    if (cfg.areaH > 0) { y1 = y0 + cfg.areaH; }

    // Separate stream (see header): clutterCount = 0 must be a no-op on the main
    // sequence so historical results stay reproducible.
    std::mt19937 crng(cfg.seed ^ 0x9E3779B9u);
    std::uniform_real_distribution<double> ux(x0, x1), uy(y0, y1);
    std::uniform_real_distribution<double> us(cfg.clutterSimMin, cfg.clutterSimMax);

    for (uint32_t m = 0; m < cfg.clutterCount; ++m) {
        ClutterSource c;
        // Rejection sampling keeps sources apart, so K really is M+1 candidates
        // rather than one merged blob. Bounded: a saturated box just yields
        // whatever fits, it must not hang.
        for (int attempt = 0; attempt < 200; ++attempt) {
            c.x = ux(crng); c.y = uy(crng);
            bool ok = std::hypot(c.x - cfg.victimX, c.y - cfg.victimY) >= cfg.clutterMinSepM;
            for (const auto& p : out)
                if (std::hypot(c.x - p.x, c.y - p.y) < cfg.clutterMinSepM) ok = false;
            if (ok) break;
        }
        c.similarity = us(crng);
        out.push_back(c);
    }
    return out;
}

std::map<uint32_t, ClueInfo> BuildClueField(const std::vector<CluePos>& nodes,
                                            const ClueFieldConfig& cfg) {
    std::map<uint32_t, ClueInfo> out;

    // audit W7: distances are to the victim's CONTINUOUS position, not to the
    // node that happens to be nearest it.
    std::vector<std::pair<double, double>> victims = cfg.victims;
    if (victims.empty()) victims.push_back({cfg.victimX, cfg.victimY});
    const double tx = cfg.victimX, ty = cfg.victimY;
    const auto clutter = BuildClutter(nodes, cfg);

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

        // The detector reports the BEST match it can find, whichever object
        // produced it. It has no way to know which one that was.
        //
        // Two versions of that number are produced from the SAME geometry: what
        // the node measures on cue fragments alone, and what it would measure
        // holding the complete reference. They differ only in how much of a
        // confusable object's similarity survives (clutterResolve). The node
        // itself never sees both -- the application interpolates by how much of
        // the dataset it actually holds -- so this is not an oracle, it is the
        // detector getting better as it is given more to compare against.
        // The best match over ALL real victims. Both readings get it: extra
        // reference data sharpens the test, it does not make a real victim stop
        // matching.
        double victimQ = 0;
        for (const auto& [vx, vy] : victims)
            victimQ = std::max(victimQ, Kernel(std::hypot(n.x - vx, n.y - vy), cfg));
        double qTrue = victimQ, qFull = victimQ;
        if (qTrue > 0) c.sourceId = -1;
        const double keep = 1.0 - std::min(1.0, std::max(0.0, cfg.clutterResolve));
        for (size_t m = 0; m < clutter.size(); ++m) {
            double k = Kernel(std::hypot(n.x - clutter[m].x, n.y - clutter[m].y), cfg);
            double q = clutter[m].similarity * k;
            if (q > qTrue) { qTrue = q; c.sourceId = (int32_t)m; }
            qFull = std::max(qFull, clutter[m].similarity * keep * k);
        }

        if (qTrue <= 0.0) {
            // background: rare spurious matches
            if (u01(rng) < cfg.bgFalsePositiveRate) {
                c.isFalsePositive = true;
                qTrue = cfg.maxNoiseQuality * u01(rng);
            } else {
                qTrue = 0.0;
            }
            // Background clutter is spurious, not a real object, so the complete
            // reference resolves it away on exactly the same terms.
            qFull = qTrue * keep;
        }

        // audit M9/W3: the node reports what its detector measured, not the
        // field. One draw per node per run. This is what makes a false positive
        // possible near the victim and a miss possible on it -- i.e. it is the
        // detector's ROC, emergent from the noise rather than hand-set.
        if (cfg.senseSigma > 0.0) {
            // ONE draw, applied to both readings: it is one detector, one piece
            // of footage. Drawing twice would let the full-data reading average
            // the noise away for free and overstate what delivery buys.
            double eps = cfg.senseSigma * gauss(rng);
            c.clueQuality = std::min(1.0, std::max(0.0, qTrue + eps));
            c.clueQualityFull = std::min(1.0, std::max(0.0, qFull + eps));
            if (qTrue <= 0.0 && c.clueQuality > 0.0) c.isFalsePositive = true;
        } else {
            c.clueQuality = qTrue;
            c.clueQualityFull = qFull;
        }
        out.emplace(n.id, c);
    }
    return out;
}

}  // namespace ns3::uavsar
