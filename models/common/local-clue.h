#ifndef WSN_UAV_LOCAL_CLUE_H
#define WSN_UAV_LOCAL_CLUE_H

#include "ns3/node-container.h"
#include "ns3/vector.h"

#include <cstdint>
#include <map>
#include <set>
#include <vector>

namespace ns3::wsn::uav {

struct LocalClueConfig {
    // -1 selects the node closest to the deployment center. This keeps default
    // runs deterministic while still allowing explicit target placement.
    int32_t targetNodeId = -1;
    uint32_t randomSeed = 20260525;
    double strongRadiusMeters = 40.0;
    double weakRadiusMeters = 120.0;
    double decayMeters = 60.0;
    double maxBlurredQuality = 0.65;
    double backgroundFalsePositiveRate = 0.03;
    double maxNoiseQuality = 0.18;
    uint32_t semanticTypeCount = 7;
};

struct LocalClueInfo {
    uint32_t nodeId = 0;
    uint32_t targetNodeId = 0;
    bool isTrueTargetNode = false;
    bool isFalsePositive = false;
    double distanceToTargetMeters = 0.0;
    double spatialDecay = 0.0;
    double clueQuality = 0.0;      // 0..1, local evidence clarity.
    double semanticOverlap = 0.0;  // 0..1, overlap with BS/UAV semantic target data.
    double falsePositiveRisk = 0.0;
    ns3::Vector position;
    std::set<uint32_t> matchedSemanticTypes;
};

struct LocalCluePlan {
    LocalClueConfig config;
    uint32_t targetNodeId = 0;
    ns3::Vector targetPosition;
    std::map<uint32_t, LocalClueInfo> nodes;
};

LocalCluePlan BuildLocalCluePlan(const ns3::NodeContainer& groundNodes,
                                 const LocalClueConfig& config);

}  // namespace ns3::wsn::uav

#endif  // WSN_UAV_LOCAL_CLUE_H
