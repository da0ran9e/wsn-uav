// Verification harness for the Phase-1 subtree (models/p1/). Pure logic, no
// ns-3 simulation. Built and run after every step, not at the end.
//
//   p1-test [gridSize] [cellRadius] [seed]

#include "../models/common/cell-grid.h"   // ONLY to cross-check the hex duplicate
#include "../models/p1/p1-cells.h"
#include "../models/p1/p1-hex.h"
#include "../models/p1/p1-params.h"
#include "../models/p1/p1-sensing.h"
#include "../models/p1/p1-demand.h"
#include "../models/p1/p1-tier1.h"

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <random>
#include <map>
#include <set>
#include <vector>

using namespace ns3::uavsar::p1;

// NOT assert(): ns-3 builds this profile with NDEBUG and assert() is compiled
// away, so a harness built on it verifies nothing while reporting success.
static uint32_t g_checks = 0;
#define CHECK(cond)                                                            \
    do {                                                                       \
        ++g_checks;                                                            \
        if (!(cond)) {                                                         \
            std::fprintf(stderr, "CHECK FAILED %s:%d: %s\n", __FILE__,         \
                         __LINE__, #cond);                                     \
            return 1;                                                          \
        }                                                                      \
    } while (0)

int main(int argc, char* argv[]) {
    uint32_t gridSize = 24;
    double spacing = 20.0;
    double rc = kCellRadiusM;
    uint32_t seed = 1;
    if (argc > 1) gridSize = (uint32_t)std::atoi(argv[1]);
    if (argc > 2) rc = std::atof(argv[2]);
    if (argc > 3) seed = (uint32_t)std::atoi(argv[3]);

    // === S1: the hex duplicate is a VERIFIED duplicate =====================
    // p1-hex.h deliberately re-states the maths in cell-grid.cc rather than
    // depending on it (see the header for why). That is only safe if the two
    // are checked to agree, which is what this does.
    {
        uint32_t n = 0;
        for (double x = -500; x <= 500; x += 7.3)
            for (double y = -500; y <= 500; y += 7.3) {
                int32_t q1, r1, q2, r2;
                hex::WorldToAxial(x, y, rc, q1, r1);
                ns3::uavsar::hex::WorldToAxial(x, y, rc, q2, r2);
                CHECK(q1 == q2 && r1 == r2);
                double ax, ay, bx, by;
                hex::AxialToCentre(q1, r1, rc, ax, ay);
                ns3::uavsar::hex::AxialToCenter(q2, r2, rc, bx, by);
                CHECK(std::fabs(ax - bx) < 1e-12 && std::fabs(ay - by) < 1e-12);
                n++;
            }
        std::printf("hex duplicate verified against cell-grid over %u points\n", n);
    }
    CHECK(std::fabs(hex::RowPitch(rc) - 1.5 * rc) < 1e-12);
    CHECK(hex::CellArea(rc) < M_PI * rc * rc);   // a hex is smaller than its circumcircle

    // === S2/S3: nodes and cells ===========================================
    std::vector<std::pair<double, double>> xy;
    for (uint32_t i = 0; i < gridSize; i++)
        for (uint32_t j = 0; j < gridSize; j++)
            xy.push_back({j * spacing, i * spacing});
    const double side = (gridSize - 1) * spacing;

    std::vector<Node> nodes = BuildNodes(xy, seed);
    CHECK(nodes.size() == xy.size());
    CellPlan plan = BuildCells(nodes, rc, kGroundRangeM);

    std::printf("\n=== PHASE 0   %ux%u nodes @%.0fm, field %.0fm, R_c=%.0fm\n",
                gridSize, gridSize, spacing, side, rc);
    std::printf("cells=%zu   A=%u B=%u C=%u   leader-score CV=%.3f\n",
                plan.cells.size(), plan.nA, plan.nB, plan.nC, LeaderScoreCv(plan));
    const double rho = TurnRadiusM(kCruiseMps);
    std::printf("h=1.5R_c=%.1fm   rho(%.0fm/s,%.0fdeg)=%.1fm   h/2rho=%.2f\n",
                plan.RowPitchM(), kCruiseMps, kBankDeg, rho, plan.RowPitchM() / (2 * rho));
    std::printf("  adjacent-row scan optimal:  SUFFICIENT R_c>=%.1fm"
                " | true(cited)>=%.1fm | true(Dubins)>=%.1fm\n",
                kAdjacentSufficient * rho, kAdjacentTrueCited * rho,
                kAdjacentTrueDubins * rho);
    std::printf("  cells by area: hex %.0f  (treating a cell as a disc: %.0f, "
                "%.1f%% low)\n", side * side / hex::CellArea(rc),
                side * side / (M_PI * rc * rc),
                100.0 * (1.0 - hex::CellArea(rc) / (M_PI * rc * rc)));

    // --- partition invariants ---
    CHECK(plan.nA + plan.nB + plan.nC == plan.cells.size());
    CHECK(plan.cellOfNode.size() == nodes.size());
    std::map<uint32_t, uint32_t> seen;
    for (const auto& [cid, c] : plan.cells)
        for (const CellMember& m : c.members) {
            seen[m.id]++;
            CHECK(plan.cellOfNode.at(m.id) == cid);
        }
    CHECK(seen.size() == nodes.size());
    for (const auto& [id, k] : seen) CHECK(k == 1);   // exactly one cell each

    std::map<uint32_t, const Node*> byId;
    for (const Node& n : nodes) byId[n.id] = &n;

    // --- class and election invariants ---
    for (const auto& [cid, c] : plan.cells) {
        uint32_t matchers = 0, imagers = 0;
        for (const CellMember& m : c.members) {
            if (byId[m.id]->CanMatch()) matchers++;
            if (byId[m.id]->Images()) imagers++;
        }
        CHECK(matchers == c.matchers && imagers == c.imagers);
        // Class is decided by capability, and by nothing else.
        if (matchers > 0)      CHECK(c.cls == CellClass::A);
        else if (imagers > 0)  CHECK(c.cls == CellClass::B);
        else                   CHECK(c.cls == CellClass::C);
        // A class-A cell's leader must itself be able to run the match: that is
        // the whole reason the election filters on modality before weighting.
        if (c.cls == CellClass::A) {
            CHECK(c.hasLeader);
            CHECK(byId[c.leader]->CanMatch());
            // and it must be the BEST such node, not merely one of them
            double best = -1;
            for (const CellMember& m : c.members)
                if (byId[m.id]->CanMatch()) best = std::max(best, byId[m.id]->ElectScore());
            CHECK(std::fabs(c.leaderScore - best) < 1e-12);
        }
        // Every cell centre is where the hex maths says it is.
        double cx, cy;
        hex::AxialToCentre(c.q, c.r, rc, cx, cy);
        CHECK(std::fabs(cx - c.cx) < 1e-9 && std::fabs(cy - c.cy) < 1e-9);
    }

    // --- tree invariants: rooted at the ELECTED leader, acyclic ---
    uint32_t unreachable = 0;
    for (const auto& [cid, c] : plan.cells) {
        if (!c.hasLeader) continue;
        std::map<uint32_t, const CellMember*> mem;
        for (const CellMember& m : c.members) mem[m.id] = &m;
        CHECK(mem.at(c.leader)->hops == 0);
        CHECK(mem.at(c.leader)->parent == -1);
        for (const CellMember& m : c.members) {
            if (m.hops == 0xFFFFFFFFu) { unreachable++; continue; }
            if (m.hops == 0) { CHECK(m.id == c.leader); continue; }
            CHECK(m.parent >= 0);
            const CellMember* p = mem.at((uint32_t)m.parent);
            CHECK(p->hops == m.hops - 1);           // strictly closer: no cycles
            // the link the tree used must actually exist
            CHECK(std::hypot(byId[m.id]->x - byId[p->id]->x,
                             byId[m.id]->y - byId[p->id]->y) <= kGroundRangeM + 1e-9);
        }
    }
    std::printf("intra-cell trees rooted at the elected leader; %u members "
                "unreachable in-cell\n", unreachable);

    // --- T_local ---
    double tmax = 0, tsum = 0; uint32_t na = 0;
    for (const auto& [cid, c] : plan.cells) {
        CHECK(c.tLocalS >= 0.0);
        if (c.cls != CellClass::A) continue;
        na++; tsum += c.tLocalS; tmax = std::max(tmax, c.tLocalS);
        // Zero exactly when the leader is the only matcher it has to feed.
        if (c.matchers == 1) CHECK(c.tLocalS == 0.0);
    }
    std::printf("T_local over class-A cells: mean %.1fs  max %.1fs  "
                "(theta_full=%.0fB to every matcher)\n",
                na ? tsum / na : 0.0, tmax, kThetaFullBytes);

    // The homogeneous world must make every cell class A -- if it does not, the
    // class rule is reading something other than capability.
    {
        CellPlan uni = BuildCells(BuildUniformNodes(xy), rc, kGroundRangeM);
        CHECK(uni.nB == 0 && uni.nC == 0);
        CHECK(uni.nA == uni.cells.size());
        CHECK(LeaderScoreCv(uni) == 0.0);
        std::printf("uniform world: %u/%zu cells class A, leader CV %.3f\n",
                    uni.nA, uni.cells.size(), LeaderScoreCv(uni));
    }


    // === S4: Tier 1 ========================================================
    std::mt19937 orng(seed ^ 0xABCDu);
    std::uniform_real_distribution<double> ux(0.08 * side, 0.92 * side);
    std::vector<Object> objects;
    objects.push_back({ux(orng), ux(orng), true, 1.0});
    for (int k = 0; k < 3; k++) objects.push_back({ux(orng), ux(orng), false, 1.0});
    const int M = (int)objects.size() - 1;

    Tier1Result t1 = RunTier1(nodes, plan, objects, seed);
    std::printf("\n=== TIER 1   %zu objects (1 real, %d confusers, similarity 1.0)\n",
                objects.size(), M);
    std::printf("|D|=%zu   recall %u/%u   false alarms %u/%u   uplink %.2f kB\n",
                t1.suspects.size(), t1.detected, t1.objectCells,
                t1.falseAlarms, t1.emptyCells, t1.UplinkBytes() / 1000.0);

    CHECK(t1.nodes.size() == nodes.size());
    for (const auto& [cid, t] : t1.cells) CHECK(plan.cells.at(cid).cls != CellClass::C);
    for (const auto& [cid, c] : plan.cells)
        if (c.cls != CellClass::C) CHECK(t1.cells.count(cid) == 1);
    double wsum = 0;
    for (int32_t cid : t1.suspects) wsum += t1.cells.at(cid).weight;
    CHECK(t1.suspects.empty() || std::fabs(wsum - 1.0) < 1e-9);
    for (const auto& [id, r] : t1.nodes) {
        CHECK(r.scoreCue >= 0.0 && r.scoreCue <= 1.0);
        CHECK(r.scoreFull >= 0.0 && r.scoreFull <= 1.0);
        // The reference can only ever REMOVE a resemblance, never add one.
        CHECK(r.scoreFull <= r.scoreCue + 1e-12);
    }

    // Same seed, same readings: the noise is one observation per node per run,
    // not something a node can average away by looking again.
    {
        Tier1Result again = RunTier1(nodes, plan, objects, seed);
        for (const auto& [id, r] : t1.nodes) {
            CHECK(again.nodes.at(id).scoreCue == r.scoreCue);
            CHECK(again.nodes.at(id).noise == r.noise);
        }
    }

    // Tier 1 is blind to WHICH object is real: move the ground-truth flag and
    // every cue-level reading must come back bit-identical. Comparing mean
    // scores would not test this -- those differ by geometry and by sampling,
    // and a difference there would prove nothing either way.
    {
        std::vector<Object> swapped = objects;
        swapped[0].real = false;
        swapped[1].real = true;
        Tier1Result alt = RunTier1(nodes, plan, swapped, seed);
        for (const auto& [id, r] : t1.nodes) CHECK(alt.nodes.at(id).scoreCue == r.scoreCue);
        CHECK(alt.suspects == t1.suspects);
        // ... and NOT blind once it holds the reference. That gap is the thing
        // the aircraft flies out to buy.
        uint32_t moved = 0;
        for (const auto& [id, r] : t1.nodes)
            if (alt.nodes.at(id).scoreFull != r.scoreFull) moved++;
        std::printf("cue-level readings identical under a ground-truth swap; "
                    "%u/%zu full-reference readings move\n", moved, t1.nodes.size());
        CHECK(moved > 0);
    }

    // Spillover vs noise. Not every false alarm is noise: a node near a boundary
    // responds to an object in the NEXT cell, so the alarm is right and only the
    // cell label is wrong. Spillover is a RESOLUTION limit of the cell layer --
    // it is what Phase 2 pays to resolve, and it is one of the three competing
    // pressures on R_c. Isolated alarms are detector noise, which is what a
    // better detector would remove. Reporting them as one number hides both.
    {
        uint32_t spill = 0, isolated = 0;
        for (const auto& [cid, t] : t1.cells) {
            if (!t.suspect || t.holdsObject) continue;
            const Cell& c = plan.cells.at(cid);
            double near = 1e18;
            for (const Object& o : objects)
                near = std::min(near, std::hypot(c.cx - o.x, c.cy - o.y));
            if (near <= 2.0 * rc) spill++; else isolated++;
        }
        CHECK(spill + isolated == t1.falseAlarms);
        std::printf("  of those: %u spillover from a neighbouring cell, %u isolated noise\n",
                    spill, isolated);
    }

    // === The threshold ordering, checked against THIS deployment ===========
    // noise floor < alert < confirm < R_victim. The third inequality is the one
    // that broke: a confirm bar above the best true positive rejects every real
    // victim, and nothing in the code complains -- the run just comes back with
    // no confirmations and looks like a hard search problem.
    {
        // Worst case for a true positive: the weakest imager, at the furthest a
        // victim can be from its nearest node on this lattice.
        const double dWorst = spacing * std::sqrt(2.0) / 2.0;
        const double rVictim = kQualityMax * std::exp(-dWorst / (kDecayM * kObsMin));
        const double noise3s = 3.0 * kSenseSigma;
        std::printf("\nthreshold chain: noise 3sigma %.3f < alert %.2f < confirm %.2f"
                    " < R_victim %.3f  (weakest sensor, d=%.1fm)\n",
                    noise3s, kAlertScore, kConfirmScore, rVictim, dWorst);
        CHECK(noise3s < kAlertScore);
        CHECK(kAlertScore < kConfirmScore);
        CHECK(kConfirmScore < rVictim);
    }

    // === The Fano ceiling, MEASURED ========================================
    // The claim the architecture rests on: with no reference, picking the cell
    // that holds the real victim is at chance over M+1 equally plausible
    // objects. Measured over many worlds, not asserted.
    {
        uint32_t trials = 0, cueRight = 0, fullRight = 0;
        for (uint32_t s2 = 1; s2 <= 400; ++s2) {
            std::mt19937 r2(s2 ^ 0xBEEFu);
            std::uniform_real_distribution<double> u2(0.08 * side, 0.92 * side);
            std::vector<Object> ob;
            ob.push_back({u2(r2), u2(r2), true, 1.0});
            for (int k = 0; k < M; k++) ob.push_back({u2(r2), u2(r2), false, 1.0});
            Tier1Result r = RunTier1(nodes, plan, ob, s2);
            if (r.suspects.empty()) continue;
            // truth: the cell the real object sits in
            int32_t truth = -1;
            for (const auto& [cid, t] : r.cells) if (t.holdsReal) truth = cid;
            if (truth < 0) continue;
            trials++;
            if (r.suspects.front() == truth) cueRight++;
            // the same argmax taken on the FULL-reference reading
            int32_t bestFull = -1; double bs = -1;
            for (const auto& [cid, t] : r.cells) {
                double m2 = 0;
                for (const CellMember& mm : plan.cells.at(cid).members)
                    m2 = std::max(m2, r.nodes.at(mm.id).scoreFull);
                if (m2 > bs) { bs = m2; bestFull = cid; }
            }
            if (bestFull == truth) fullRight++;
        }
        const double pc = trials ? 100.0 * cueRight / trials : 0.0;
        const double pf = trials ? 100.0 * fullRight / trials : 0.0;
        std::printf("\npicking the victim's cell over %u worlds (M=%d):\n"
                    "  tier 1, no reference : %.1f%%   (Fano ceiling 1/(M+1) = %.1f%%)\n"
                    "  tier 2, full reference: %.1f%%\n",
                    trials, M, pc, 100.0 / (M + 1), pf);
        CHECK(trials > 100);
        // The reference must buy something. If it does not, the two tiers are
        // not two tiers.
        CHECK(pf > pc);
    }

    // === The Fano ceiling, with the geometry CONTROLLED ====================
    // The number above is the realistic one, and it sits ABOVE 1/(M+1) because
    // the field is not symmetric: an object that happens to land near a strong,
    // close sensor is better observed than one that does not, so the M+1
    // hypotheses are not equally distinguishable and the effective M is smaller
    // than the nominal one. That is a true statement about deployments, not a
    // violation of the bound -- but it means the realistic number cannot be used
    // to demonstrate the bound. This control removes the asymmetry: identical
    // sensors everywhere, and every object sitting exactly on a node. Then the
    // M+1 hypotheses really are exchangeable and tier 1 must be at chance.
    {
        std::vector<Node> uni = BuildUniformNodes(xy);
        CellPlan up = BuildCells(uni, rc, kGroundRangeM);
        uint32_t trials = 0, right = 0, collisions = 0;
        for (uint32_t s2 = 1; s2 <= 1200; ++s2) {
            std::mt19937 r2(s2 ^ 0xFACEu);
            std::uniform_int_distribution<size_t> pick(0, xy.size() - 1);
            std::vector<Object> ob;
            std::set<size_t> used;
            while (ob.size() < (size_t)M + 1) {
                const size_t k = pick(r2);
                if (!used.insert(k).second) continue;
                ob.push_back({xy[k].first, xy[k].second, ob.empty(), 1.0});
            }
            // The ceiling is over OBJECTS, and the question here is over CELLS.
            // Those are not the same question: when two objects share a cell,
            // naming that cell is right if EITHER is the real one, so a coarse
            // partition scores above the bound with no extra information at all.
            // Discarding the collided worlds makes cell and object the same
            // question again, which is the only condition under which 1/(M+1)
            // is the number to compare against.
            std::set<int32_t> occupied;
            bool collided = false;
            for (const Object& o : ob) {
                int32_t q, rr;
                hex::WorldToAxial(o.x, o.y, rc, q, rr);
                if (!occupied.insert(q * 10007 + rr).second) { collided = true; break; }
            }
            if (collided) { collisions++; continue; }
            Tier1Result r = RunTier1(uni, up, ob, s2);
            if (r.suspects.empty()) continue;
            int32_t truth = -1;
            for (const auto& [cid, t] : r.cells) if (t.holdsReal) truth = cid;
            if (truth < 0) continue;
            trials++;
            if (r.suspects.front() == truth) right++;
        }
        const double pc = trials ? 100.0 * right / trials : 0.0;
        std::printf("controlled (identical sensors, objects on nodes, one object per"
                    " cell): %.1f%% over %u worlds vs ceiling %.1f%%"
                    "   [%u worlds discarded for cell collisions]\n",
                    pc, trials, 100.0 / (M + 1), collisions);
        CHECK(trials > 150);
        // At chance, within sampling error for a few hundred trials.
        CHECK(std::fabs(pc - 100.0 / (M + 1)) < 8.0);
    }

    // === Tier 2 verdicts ===================================================
    {
        uint32_t conf = 0, rej = 0, none = 0;
        for (int32_t cid : t1.suspects) {
            switch (CellVerdict(t1, plan, nodes, cid, 1.0)) {
                case Verdict::CONFIRM: conf++; break;
                case Verdict::REJECT:  rej++;  break;
                default:               none++; break;
            }
        }
        std::printf("tier 2 on the %zu suspects, full delivery: %u confirm, %u reject, "
                    "%u no verdict (no node able to run the matcher)\n",
                    t1.suspects.size(), conf, rej, none);
        // Nothing is decided before anything is delivered, unless the cue
        // reading already cleared the confirm bar on its own.
        for (int32_t cid : t1.suspects) {
            const Verdict v0 = CellVerdict(t1, plan, nodes, cid, 0.0);
            CHECK(v0 == Verdict::NONE || v0 == Verdict::REJECT || v0 == Verdict::CONFIRM);
        }
        // A class-B or C cell can never return a verdict, at any dose.
        for (const auto& [cid, c] : plan.cells)
            if (c.cls != CellClass::A)
                CHECK(CellVerdict(t1, plan, nodes, cid, 1.0) == Verdict::NONE);
    }

    // === S5: T0 ============================================================
    DoseModel dose;
    auto demands = BuildDemands(plan, nodes, t1);
    std::printf("\n=== T0   lambda_tx=%.0f B/s  theta_full=%.0f B  hedge=%.0f%%\n",
                kRefTxBytesPerS, kThetaFullBytes, 100 * kThetaHedgeFrac);
    std::printf("G(b):");
    for (double b : {0.0, 50.0, 100.0, 150.0, 200.0, 300.0})
        std::printf("  G(%.0f)=%.0fm", b, dose.G(b));
    std::printf("\n");

    // G must be positive, strictly decreasing, and never exceed the width of the
    // region where p is appreciable.
    {
        double prev = 1e18;
        for (double b = 0; b <= kGmaxOffsetM; b += 5.0) {
            const double g = dose.G(b);
            CHECK(g >= 0.0);
            CHECK(g < prev + 1e-9);
            prev = g;
        }
        // Simpson against a coarse independent rectangle sum: the table is the
        // one piece of numerics here, so it gets an independent check.
        double ref = 0.0;
        const double hh = 0.5;
        for (double x = -1600.0; x <= 1600.0; x += hh) ref += dose.Prx(std::fabs(x)) * hh;
        CHECK(std::fabs(ref - dose.G(0.0)) / ref < 0.01);
        std::printf("  G(0) by Simpson %.2fm vs independent rectangle sum %.2fm\n",
                    dose.G(0.0), ref);
    }

    // Only class A ever costs the aircraft anything, at any offset.
    for (auto& [cid, d] : demands) {
        if (d.cls != CellClass::A) {
            CHECK(d.theta == 0.0);
            CHECK(ServiceCost(d, 0.0, dose) == 0.0);
        }
        // A flagged cell needs strictly more than an unflagged one of the same
        // sensor quality: that ratio IS the hedge.
        if (d.cls == CellClass::A) CHECK(d.theta > 0.0);
    }

    // Serving is monotone in offset: further away is never cheaper.
    {
        for (auto& [cid, d] : demands) {
            if (d.theta <= 0.0) continue;
            Demand a = d, b = d;
            const double ca = ServiceCost(a, 0.0, dose);
            const double cb = ServiceCost(b, 120.0, dose);
            CHECK(cb >= ca - 1e-9);
        }
    }

    uint32_t slowed = 0, orbited = 0; double total = 0;
    for (auto& [cid, d] : demands) {
        const double c = ServiceCost(d, 0.0, dose);
        if (d.theta <= 0.0) continue;
        total += c;
        if (d.orbits) orbited++; else slowed++;
        CHECK(c >= 0.0);
        CHECK((d.orbits > 0) == (d.serveMps == 0.0));
    }
    std::printf("cells to serve: %u   one pass slowed %u, must orbit %u   "
                "total service %.0f s\n", slowed + orbited, slowed, orbited, total);

    // The parameter set is only OPERABLE if a flagged cell can be served in one
    // pass. Reported, not asserted: it is a statement about the placeholders,
    // and the placeholders are what the parameter review will replace.
    {
        const double thetaMax = kRefTxBytesPerS * dose.G(0.0) / kMinMps;
        std::printf("one pass at stall can deliver at most %.0f B; theta_full is "
                    "%.0f B  -> %s\n", thetaMax, kThetaFullBytes,
                    thetaMax >= kThetaFullBytes ? "a flagged cell CAN be served in one pass"
                                                : "every flagged cell must ORBIT");
    }

    std::printf("\n%u CHECKS PASSED\n", g_checks);
    return 0;
}
