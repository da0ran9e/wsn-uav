#include "tier1-detect.h"

#include "phase1-params.h"

#include <algorithm>
#include <cmath>
#include <random>

namespace ns3::uavsar {

namespace {

// Response of one node to an object at distance d.
//
// obs scales RANGE, not gain. That distinction was measured: applying obs as a
// multiplier on the reading collapsed detection entirely (0 of 2 victims found),
// because a weak sensor standing ON the target still reported nothing. A weak
// sensor sees the same thing, just from closer.
double Response(double d, double obs) {
    if (obs <= 0.0) return 0.0;
    const double half = p1::kDetectHalfRangeM * obs;
    return std::exp(-d * std::log(2.0) / half);
}

}  // namespace

Tier1Result RunTier1(const CellGridPlan& grid,
                     const CellRolePlan& roles,
                     const std::map<uint32_t, NodeCapability>& caps,
                     const std::vector<Tier1Object>& objects,
                     uint32_t seed) {
    Tier1Result out;
    std::mt19937 rng(seed ^ 0x9E3779B9u);
    std::normal_distribution<double> noise(0.0, p1::kDetectSigma);

    for (const auto& [cid, role] : roles.roles) {
        if (role.cls == CellClass::C) continue;
        auto ci = grid.cells.find(cid);
        if (ci == grid.cells.end()) continue;

        Tier1Cell t;
        t.cellId = cid;

        // Best response any imaging member of the cell can raise. The victim and
        // the confuser go through the SAME branch -- that is the model, not an
        // oversight.
        double best = 0.0;
        for (uint32_t nid : ci->second.members) {
            auto capIt = caps.find(nid);
            auto posIt = grid.nodes.find(nid);
            if (capIt == caps.end() || posIt == grid.nodes.end()) continue;
            if (!Images(capIt->second.modality)) continue;
            for (const Tier1Object& o : objects) {
                const double d = std::hypot(posIt->second.x - o.x, posIt->second.y - o.y);
                const double r = Response(d, capIt->second.obs);
                if (r > best) { best = r; t.responder = nid; }
            }
        }

        // Ground truth: does the object lie IN this cell? Answered by geometry,
        // not by whether some member happened to respond -- a response-based
        // label makes almost every cell "hold" an object once the sensing range
        // is a good fraction of the cell pitch, and then recall and false-alarm
        // rate both stop meaning anything.
        for (const Tier1Object& o : objects) {
            int32_t nearest = -1; double bd = 1e18;
            for (const auto& [ocid, ocell] : grid.cells) {
                const double d = std::hypot(ocell.centerX - o.x, ocell.centerY - o.y);
                if (d < bd) { bd = d; nearest = ocid; }
            }
            if (nearest == cid) { t.holdsObject = true; if (o.real) t.holdsReal = true; }
        }

        const double mean = p1::kDetectMeanNoise +
                            (p1::kDetectMeanSignal - p1::kDetectMeanNoise) * best;
        t.score = std::clamp(mean + noise(rng), 0.0, 1.0);
        t.suspect = t.score > p1::kAlertThreshold;

        if (t.holdsObject) { out.objectCells++; if (t.suspect) out.detected++; }
        else               { out.emptyCells++;  if (t.suspect) out.falseAlarms++; }

        out.cells[cid] = t;
    }

    // D, and the prior over it.
    double total = 0.0;
    for (auto& [cid, t] : out.cells)
        if (t.suspect) { out.suspects.push_back(cid); total += t.score; }
    if (total > 0.0)
        for (int32_t cid : out.suspects) out.cells[cid].weight = out.cells[cid].score / total;

    std::sort(out.suspects.begin(), out.suspects.end(),
              [&](int32_t a, int32_t b) { return out.cells[a].score > out.cells[b].score; });
    return out;
}

}  // namespace ns3::uavsar
