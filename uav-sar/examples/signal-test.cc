// Phase 3 verification: semantic fragments (confidence) + clue field (region).
// No ns-3 sim. Checks: confidence grows L0 < FAST(L0+L1) < full and full >=
// confirm threshold; clue quality peaks at the victim node and fades with
// distance; combining FAST cue-confidence with local clue quality lights up a
// small region around the victim and stays quiet far away (no false storm).

#include "../models/common/target-profile.h"
#include "../models/common/clue-field.h"
#include "../models/common/sar-params.h"

#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <vector>

using namespace ns3::uavsar;

int main() {
    // --- fragments ---
    TargetProfile tp = TargetProfile::Generate();
    auto L0 = tp.OfLayer(Layer::L0_IDENTITY);
    auto L1 = tp.OfLayer(Layer::L1_DESCRIPTOR);
    std::vector<Fragment> fast = L0;
    fast.insert(fast.end(), L1.begin(), L1.end());
    double cL0 = TargetProfile::Confidence(L0);
    double cFast = TargetProfile::Confidence(fast);
    double cFull = TargetProfile::Confidence(tp.All());

    std::cout << "=== FRAGMENTS ===\n";
    std::cout << "total=" << tp.Size() << " frags, " << tp.TotalBytes() << " bytes\n";
    std::cout << "Confidence: L0only=" << cL0 << "  FAST(L0+L1)=" << cFast
              << "  FULL=" << cFull << "\n";
    std::cout << "thresholds: alert=" << params::kAlertThreshold
              << " coop=" << params::kCoopThreshold
              << " (confirm = possession of the ENTIRE dataset)\n\n";

    // --- clue field on an 8x8 grid, victim near centre ---
    const uint32_t G = 8;
    const double sp = 20.0;
    std::vector<CluePos> nodes;
    uint32_t id = 0, target = 0;
    double bestd = 1e18, cx = (G - 1) * sp / 2, cy = (G - 1) * sp / 2;
    for (uint32_t i = 0; i < G; i++)
        for (uint32_t j = 0; j < G; j++) {
            nodes.push_back({id, j * sp, i * sp});
            double d = std::hypot(j * sp - cx, i * sp - cy);
            if (d < bestd) { bestd = d; target = id; }
            id++;
        }
    ClueFieldConfig cc;
    cc.targetNodeId = target;
    cc.seed = 7;
    auto field = BuildClueField(nodes, cc);

    std::cout << "=== CLUE FIELD (victim node=" << target << ") ===\n";
    uint32_t regionNodes = 0, falseAlarms = 0;
    for (const auto& n : nodes) {
        const ClueInfo& ci = field.at(n.id);
        double eff = cFast * ci.clueQuality;   // FAST cues corroborated by local footage
        bool detect = eff >= params::kAlertThreshold;
        if (detect) {
            regionNodes++;
            if (ci.distToTarget > cc.weakRadius) falseAlarms++;
        }
    }
    // print a few representative nodes
    for (uint32_t nid : {target}) {
        const ClueInfo& ci = field.at(nid);
        std::cout << "  victim node " << nid << ": q=" << ci.clueQuality
                  << " eff=" << cFast * ci.clueQuality << "\n";
    }
    std::cout << "  detecting region size=" << regionNodes
              << " (nodes with eff>=alert), far false-alarms=" << falseAlarms << "\n\n";

    int checks = 0, fails = 0;
    auto CHECK = [&](bool ok, const std::string& m) {
        checks++; if (!ok) { fails++; std::cout << "  FAIL: " << m << "\n"; }
    };
    CHECK(cL0 < cFast && cFast < cFull, "confidence must grow L0<FAST<FULL");
    CHECK(cFull >= 0.99, "full-dataset confidence should be near certain");
    CHECK(field.at(target).clueQuality >= 0.5, "victim node clue quality should be high");
    // monotonic-ish: a node far away should have ~0 quality (unless FP)
    uint32_t farId = 0;  // corner (0,0) far from centre
    CHECK(field.at(farId).clueQuality < 0.2, "far node clue quality should be low");
    CHECK(regionNodes >= 1, "at least the victim node should detect");
    CHECK(falseAlarms == 0, "no far false alarms from clue+cue combination");

    std::cout << "=== CHECKS: " << (checks - fails) << "/" << checks << " passed ===\n";
    return fails == 0 ? 0 : 1;
}
