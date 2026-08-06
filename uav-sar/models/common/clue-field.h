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

// A CONFUSABLE OBJECT: something in the search area that genuinely resembles the
// reference dataset (another hiker in the same jacket, the search party itself,
// a discarded garment). This is NOT detector noise. A node reporting high
// evidence next to one of these is reporting CORRECTLY -- the world is ambiguous,
// not the sensor. The distinction matters because sensor noise is reducible by
// observing longer or averaging, and this is not reducible at all by the same
// modality: with similarity 1.0 no algorithm reading this scalar can beat
// 1/(M+1) at picking the victim. Modelling ambiguity as large senseSigma would
// therefore overstate what better sensing can fix.
struct ClutterSource {
    double x = 0, y = 0;
    double similarity = 1.0;   // peak evidence relative to the victim's, in [0,1]
};

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
    // --- world-level ambiguity (confusable objects) -------------------------
    // Placed from a SEPARATE rng stream so that clutterCount = 0 reproduces every
    // previously measured result byte-for-byte; adding draws to the main stream
    // would silently shift every background false-positive decision.
    uint32_t clutterCount = 0;        // M
    double clutterSimMin = 0.60;      // similarity drawn U[min,max]; 1.0 = identical
    double clutterSimMax = 1.00;      // outfit, indistinguishable by this sensor
    double clutterMinSepM = 150.0;    // keep sources from merging into one cluster
    double areaW = 0, areaH = 0;      // placement box; 0 = bounding box of nodes
};

struct ClueInfo {
    uint32_t id = 0;
    double x = 0, y = 0;
    double distToTarget = 0;
    double clueQuality = 0;         // [0,1]
    bool isTarget = false;
    bool isFalsePositive = false;
    // Which object drove this node's evidence: -1 victim, >= 0 clutter index,
    // -2 background. Analysis only -- no application may read it (it is an
    // oracle; audit B1 removed the last one of those).
    int32_t sourceId = -2;
};

std::map<uint32_t, ClueInfo> BuildClueField(const std::vector<CluePos>& nodes,
                                            const ClueFieldConfig& cfg);

// The confusable objects the config asks for, placed deterministically from the
// seed. Exposed so metrics can score a delivery against them: without this, a
// dataset delivered to the wrong person is indistinguishable in metrics.csv from
// a large estimation error, and the two mean completely different things.
std::vector<ClutterSource> BuildClutter(const std::vector<CluePos>& nodes,
                                        const ClueFieldConfig& cfg);

}  // namespace ns3::uavsar

#endif  // UAV_SAR_CLUE_FIELD_H
