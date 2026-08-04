#ifndef UAV_SAR_CLUE_FIELD_H
#define UAV_SAR_CLUE_FIELD_H

// Local-evidence (clue) field over the ground nodes (clean reimplementation;
// ref: main's local-clue). Each node has a clueQuality in [0,1] = how strongly
// its own footage matches the victim, driven by distance to the (hidden) victim:
//   - within strongRadius: high quality, decaying with distance
//   - within weakRadius: moderate
//   - beyond: only background false positives (rare, low quality)
// This is what lets small identity cues from FAST UAVs "narrow the region":
// several nodes around the victim (possibly across cells) light up.
//
// ns-3-independent: operates on (id,x,y). Deterministic given seed.

#include <cstdint>
#include <map>
#include <vector>

namespace ns3::uavsar {

struct CluePos { uint32_t id; double x, y; };

struct ClueFieldConfig {
    uint32_t targetNodeId = 0;      // the node nearest the victim (metrics only)
    uint32_t seed = 1;
    // audit W7: the victim is a CONTINUOUS position, not a node. When the victim
    // is co-located with a sensor, the strongest reporter IS the victim and any
    // estimator looks good for free; that coincidence is removed here.
    double victimX = 0, victimY = 0;
    double strongRadius = 40.0;     // m
    double weakRadius = 120.0;      // m
    double decay = 60.0;            // m, exponential falloff scale
    double maxQuality = 0.95;
    double bgFalsePositiveRate = 0.03;
    double maxNoiseQuality = 0.18;
    // audit M9/W3: a detector does not read the field, it reads a NOISY
    // observation of it. sigma is additive Gaussian on the quality, drawn ONCE
    // per node per run (it is one observation of that node's own footage, not a
    // per-packet event) and clipped to [0,1]. sigma = 0 reproduces the
    // idealized field exactly, so it is the ablation, not the default reality.
    double senseSigma = 0.0;
};

struct ClueInfo {
    uint32_t id = 0;
    double x = 0, y = 0;
    double distToTarget = 0;
    double clueQuality = 0;         // [0,1]
    bool isTarget = false;
    bool isFalsePositive = false;
};

std::map<uint32_t, ClueInfo> BuildClueField(const std::vector<CluePos>& nodes,
                                            const ClueFieldConfig& cfg);

}  // namespace ns3::uavsar

#endif  // UAV_SAR_CLUE_FIELD_H
