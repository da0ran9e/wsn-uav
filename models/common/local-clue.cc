#include "local-clue.h"

#include "ns3/mobility-model.h"
#include "ns3/node.h"

#include <algorithm>
#include <cmath>
#include <limits>
#include <random>

namespace ns3::wsn::uav {

namespace {

double Distance2d(const Vector& a, const Vector& b) {
    double dx = a.x - b.x;
    double dy = a.y - b.y;
    return std::sqrt(dx * dx + dy * dy);
}

double Clamp01(double v) {
    return std::max(0.0, std::min(1.0, v));
}

std::set<uint32_t> PickSemanticTypes(uint32_t typeCount,
                                     double overlap,
                                     std::mt19937& rng) {
    std::set<uint32_t> types;
    if (typeCount == 0 || overlap <= 0.0) return types;

    std::vector<uint32_t> pool;
    pool.reserve(typeCount);
    for (uint32_t i = 0; i < typeCount; i++) {
        pool.push_back(i);
    }
    std::shuffle(pool.begin(), pool.end(), rng);

    uint32_t selected = static_cast<uint32_t>(
        std::ceil(Clamp01(overlap) * static_cast<double>(typeCount)));
    selected = std::max(1u, std::min(typeCount, selected));
    for (uint32_t i = 0; i < selected; i++) {
        types.insert(pool[i]);
    }
    return types;
}

uint32_t ChooseTargetNode(const std::map<uint32_t, Vector>& positions,
                          const LocalClueConfig& cfg) {
    if (positions.empty()) return 0;
    if (cfg.targetNodeId >= 0) {
        uint32_t requested = static_cast<uint32_t>(cfg.targetNodeId);
        if (positions.find(requested) != positions.end()) {
            return requested;
        }
    }

    double minX = std::numeric_limits<double>::max();
    double minY = std::numeric_limits<double>::max();
    double maxX = std::numeric_limits<double>::lowest();
    double maxY = std::numeric_limits<double>::lowest();
    for (const auto& [_, pos] : positions) {
        minX = std::min(minX, pos.x);
        minY = std::min(minY, pos.y);
        maxX = std::max(maxX, pos.x);
        maxY = std::max(maxY, pos.y);
    }

    Vector center((minX + maxX) * 0.5, (minY + maxY) * 0.5, 0.0);
    uint32_t bestNode = positions.begin()->first;
    double bestDist = std::numeric_limits<double>::max();
    for (const auto& [nodeId, pos] : positions) {
        double d = Distance2d(pos, center);
        if (d < bestDist || (d == bestDist && nodeId < bestNode)) {
            bestDist = d;
            bestNode = nodeId;
        }
    }
    return bestNode;
}

}  // namespace

LocalCluePlan BuildLocalCluePlan(const NodeContainer& groundNodes,
                                 const LocalClueConfig& config) {
    LocalCluePlan plan;
    plan.config = config;

    std::map<uint32_t, Vector> positions;
    for (uint32_t i = 0; i < groundNodes.GetN(); i++) {
        Ptr<Node> node = groundNodes.Get(i);
        Ptr<MobilityModel> mob = node ? node->GetObject<MobilityModel>() : nullptr;
        if (!node || !mob) continue;
        positions[node->GetId()] = mob->GetPosition();
    }
    if (positions.empty()) return plan;

    plan.targetNodeId = ChooseTargetNode(positions, config);
    plan.targetPosition = positions[plan.targetNodeId];

    std::mt19937 rng(config.randomSeed);
    std::uniform_real_distribution<double> jitter(0.75, 1.15);
    std::uniform_real_distribution<double> overlapNoise(0.65, 1.0);
    std::uniform_real_distribution<double> unit(0.0, 1.0);
    std::uniform_real_distribution<double> falseRisk(0.50, 0.90);
    std::uniform_real_distribution<double> noiseQuality(0.03, config.maxNoiseQuality);

    for (const auto& [nodeId, pos] : positions) {
        LocalClueInfo info;
        info.nodeId = nodeId;
        info.targetNodeId = plan.targetNodeId;
        info.position = pos;
        info.distanceToTargetMeters = Distance2d(pos, plan.targetPosition);
        info.isTrueTargetNode = (nodeId == plan.targetNodeId);

        if (info.isTrueTargetNode) {
            info.spatialDecay = 1.0;
            info.clueQuality = 1.0;
            info.semanticOverlap = 1.0;
            info.falsePositiveRisk = 0.0;
            for (uint32_t t = 0; t < config.semanticTypeCount; t++) {
                info.matchedSemanticTypes.insert(t);
            }
        } else {
            info.spatialDecay = std::exp(-info.distanceToTargetMeters /
                                         std::max(1.0, config.decayMeters));
            bool nearTarget = (info.distanceToTargetMeters <= config.weakRadiusMeters);
            bool falsePositive = (!nearTarget && unit(rng) < config.backgroundFalsePositiveRate);

            if (nearTarget) {
                double proximityBoost =
                    (info.distanceToTargetMeters <= config.strongRadiusMeters) ? 1.15 : 1.0;
                info.clueQuality = Clamp01(config.maxBlurredQuality *
                                           info.spatialDecay * proximityBoost * jitter(rng));
                info.semanticOverlap = Clamp01(info.clueQuality * overlapNoise(rng));
                info.falsePositiveRisk = Clamp01(0.05 + 0.35 * (1.0 - info.spatialDecay));
            } else if (falsePositive) {
                info.isFalsePositive = true;
                info.clueQuality = Clamp01(noiseQuality(rng));
                info.semanticOverlap = Clamp01(info.clueQuality * unit(rng));
                info.falsePositiveRisk = falseRisk(rng);
            }

            info.matchedSemanticTypes =
                PickSemanticTypes(config.semanticTypeCount, info.semanticOverlap, rng);
        }

        plan.nodes.emplace(nodeId, std::move(info));
    }

    return plan;
}

}  // namespace ns3::wsn::uav
