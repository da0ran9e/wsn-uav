#include "p1-sensing-model.h"

#include <algorithm>
#include <cmath>
#include <random>

namespace ns3::uavsar::p1 {

namespace {

// Response of one node to an object at distance d.
//
// obs scales RANGE, not gain. That distinction was measured on the old system
// and getting it wrong collapsed detection entirely: as a gain multiplier a weak
// sensor standing on top of the target still reported nothing. A weak sensor
// sees the same thing -- it just has to be closer to see it.
double Response(double d, double obs) {
    if (obs <= 0.0) return 0.0;
    return kQualityMax * std::exp(-d / (kDecayM * obs));
}

}  // namespace

SensingResult RunSensing(const std::vector<Node>& nodes, const CellPlan& plan,
                     const std::vector<Object>& objects, uint32_t seed) {
    SensingResult out;
    std::mt19937 rng(seed ^ 0x9E3779B9u);
    std::normal_distribution<double> gauss(0.0, kSenseSigma);

    // --- per node: ONE observation, read two ways -------------------------
    for (const Node& n : nodes) {
        NodeReading r;
        r.id = n.id;
        if (!n.HasCamera()) { out.nodes[n.id] = r; continue; }
        r.noise = gauss(rng);                 // once per node per run
        double bestCue = 0.0, bestFull = 0.0;
        for (const Object& o : objects) {
            const double base = Response(std::hypot(n.x - o.x, n.y - o.y), n.obs);
            // Without the reference a confuser is as good a match as it looks.
            const double simCue = o.real ? 1.0 : o.similarity;
            // With it, the confuser's resemblance is stripped by kClutterResolve.
            const double simFull = o.real ? 1.0 : o.similarity * (1.0 - kClutterResolve);
            bestCue = std::max(bestCue, base * simCue);
            bestFull = std::max(bestFull, base * simFull);
        }
        r.scoreCue = std::clamp(bestCue + r.noise, 0.0, 1.0);
        r.scoreFull = std::clamp(bestFull + r.noise, 0.0, 1.0);
        out.nodes[n.id] = r;
    }

    // --- per cell: the leader aggregates ----------------------------------
    for (const auto& [cid, c] : plan.cells) {
        if (c.cls != CellClass::SERVED) continue;   // no head, so no verdict
        CellReading t;
        t.cellId = cid;
        for (const CellMember& m : c.members) {
            const auto it = out.nodes.find(m.id);
            if (it == out.nodes.end()) continue;
            if (it->second.scoreCue > t.score) {
                t.score = it->second.scoreCue;
                t.responder = m.id;
            }
        }
        t.suspect = t.score > kAlertScore;
        out.cells[cid] = t;
    }

    // --- ground truth by geometry, never by response ----------------------
    for (const Object& o : objects) {
        int32_t q, r;
        hex::WorldToAxial(o.x, o.y, plan.cellRadiusM, q, r);
        for (auto& [cid, t] : out.cells) {
            const Cell& c = plan.cells.at(cid);
            if (c.q != q || c.r != r) continue;
            t.holdsObject = true;
            if (o.real) t.holdsReal = true;
        }
    }
    for (const auto& [cid, t] : out.cells) {
        if (t.holdsObject) { out.objectCells++; if (t.suspect) out.detected++; }
        else               { out.emptyCells++;  if (t.suspect) out.falseAlarms++; }
    }

    // What the network would have guessed on cue-level information alone. This
    // is the BASELINE, kept so the flight can be measured against it -- it is
    // not, and must not become, an input to the planner.
    double total = 0.0;
    for (const auto& [cid, t] : out.cells)
        if (t.suspect) { out.cueGuess.push_back(cid); total += t.score; }
    if (total > 0.0)
        for (int32_t cid : out.cueGuess) out.cells[cid].weight = out.cells[cid].score / total;
    std::sort(out.cueGuess.begin(), out.cueGuess.end(),
              [&](int32_t a, int32_t b) { return out.cells[a].score > out.cells[b].score; });
    return out;
}

Verdict CellVerdict(const SensingResult& sr, const CellPlan& plan,
                    const std::vector<Node>& nodes, int32_t cellId, double held) {
    const auto ci = plan.cells.find(cellId);
    if (ci == plan.cells.end() || ci->second.cls != CellClass::SERVED) return Verdict::NONE;

    std::map<uint32_t, const Node*> byId;
    for (const Node& n : nodes) byId[n.id] = &n;

    held = std::clamp(held, 0.0, 1.0);
    bool anyVoter = false;
    for (const CellMember& m : ci->second.members) {
        // Only a node that can actually RUN the matcher may return a verdict. A
        // node holding the reference it cannot run is not a quiet REJECT -- it
        // is no answer at all, and counting it as a rejection would retire a
        // live candidate for the wrong reason.
        const auto bi = byId.find(m.id);
        if (bi == byId.end() || m.id != ci->second.leader) continue;   // N3: only the head matches
        const auto ni = sr.nodes.find(m.id);
        if (ni == sr.nodes.end()) continue;
        anyVoter = true;
        // Partial delivery buys partial disambiguation: the reading slides from
        // the cue value to the full value as the reference arrives. Without this
        // the dose model in T0 would have nothing to be a dose OF.
        const double s = ni->second.scoreCue +
                         held * (ni->second.scoreFull - ni->second.scoreCue);
        if (s >= kConfirmScore) return Verdict::CONFIRM;
    }
    return anyVoter ? Verdict::REJECT : Verdict::NONE;
}

}  // namespace ns3::uavsar::p1
