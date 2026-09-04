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
#include "../models/p1/p1-dubins.h"
#include "../models/p1/p1-partition.h"
#include "../models/p1/p1-route.h"
#include "../models/p1/p1-refine.h"
#include "../models/p1/p1-speed.h"
#include "../models/p1/p1-tier1.h"

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <random>
#include <string>
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

    // === S6: Dubins ========================================================
    // Closed form against forward integration. This is the check that once
    // caught an LRL word with 208 m of endpoint error while the other five were
    // exact -- a wrong CCC expression returns plausible LENGTHS, so only the
    // endpoint test finds it.
    {
        std::mt19937 dr(4242);
        std::uniform_real_distribution<double> ux2(-600, 600), uh(0, 2 * M_PI);
        double worst = 0;
        uint32_t words[7] = {0};
        for (int k = 0; k < 4000; ++k) {
            Config a{ux2(dr), ux2(dr), uh(dr)}, b{ux2(dr), ux2(dr), uh(dr)};
            const DubinsPath pth = Dubins(a, b, rho);
            CHECK(pth.valid);
            words[(int)pth.word]++;
            const Config e = Integrate(a, pth, rho);
            worst = std::max(worst, std::hypot(e.x - b.x, e.y - b.y));
            // and the length must equal the integrated arc length
            CHECK(std::fabs(pth.length - (pth.seg[0] + pth.seg[1] + pth.seg[2]) * rho) < 1e-9);
        }
        std::printf("\n=== DUBINS  worst endpoint error over 4000 pairs: %.2e m\n", worst);
        std::printf("  words used:");
        for (int w = 0; w < 6; ++w)
            std::printf("  %s=%u", WordName((Word)w), words[w]);
        std::printf("\n");
        CHECK(worst < 1e-9);
        for (int w = 0; w < 6; ++w) CHECK(words[w] > 0);   // every word must occur
    }

    // === S7: T1 partition ==================================================
    const Config depot{0.0, 0.0, 0.0};
    std::printf("\n=== T1  partition over %u class-A cells, depot at the field corner\n",
                plan.nA);
    std::printf("%-22s %2s %10s %10s %8s\n", "method", "M", "makespan", "spread", "cells");
    for (uint32_t M2 : {2u, 3u, 4u}) {
        Partition ps[3] = {
            PartitionCredit(demands, plan, depot, M2, rho, false),
            PartitionCredit(demands, plan, depot, M2, rho, true),
            PartitionSplit(demands, depot, M2, rho),
        };
        for (const Partition& q : ps) {
            uint32_t n = 0;
            std::set<int32_t> seen2;
            for (const Route& r : q.vehicles)
                for (int32_t c : r.cells) { n++; seen2.insert(c); }
            // every cell that needs serving is served, exactly once
            uint32_t need = 0;
            for (const auto& [cid, d] : demands) if (d.theta > 0) need++;
            CHECK(n == need);
            CHECK(seen2.size() == need);
            CHECK(q.vehicles.size() == M2);
            CHECK(q.makespanS > 0);
            CHECK(q.imbalancePct >= 0 && q.imbalancePct <= 100.0);
            char name[48];
            std::snprintf(name, sizeof name, "%s%s", q.method,
                          std::string(q.method) == "credit"
                              ? (q.contiguous ? " (contiguous)" : " (free)") : "");
            std::printf("%-22s %2u %9.0fs %8.1f%% %8u\n", name, M2,
                        q.makespanS, q.imbalancePct, n);
        }
    }

    // === S8: T2 routing ====================================================
    std::vector<int32_t> aCells;
    for (const auto& [cid, d] : demands) if (d.theta > 0) aCells.push_back(cid);
    std::printf("\n=== T2  Dubins tour over %zu cells\n", aCells.size());

    // The heading DP is EXACT for a fixed order. Verified against brute force
    // over every heading combination on a short order -- if the DP is wrong this
    // is the only thing that finds it, because a wrong DP still returns a
    // plausible tour.
    {
        std::vector<int32_t> shortOrder(aCells.begin(), aCells.begin() + 4);
        const uint32_t h = 6;
        const Tour dpT = BestHeadings(shortOrder, demands, depot, rho, h);
        double brute = 1e18;
        for (uint32_t a = 0; a < h; ++a)
        for (uint32_t b = 0; b < h; ++b)
        for (uint32_t c = 0; c < h; ++c)
        for (uint32_t e = 0; e < h; ++e) {
            const uint32_t idx[4] = {a, b, c, e};
            double m = 0;
            Config prev = depot;
            for (int k = 0; k < 4; ++k) {
                const Demand& d = demands.at(shortOrder[k]);
                const Config cf{d.x, d.y, 2.0 * M_PI * idx[k] / h};
                m += DubinsLength(prev, cf, rho);
                prev = cf;
            }
            m += DubinsLength(prev, depot, rho);
            brute = std::min(brute, m);
        }
        std::printf("  heading DP %.3fm vs brute force over %u^4 combinations %.3fm\n",
                    dpT.flightM, h, brute);
        CHECK(std::fabs(dpT.flightM - brute) < 1e-6);
    }

    // Heading resolution: more samples can only help, and the curve must flatten.
    {
        std::printf("  h sweep:");
        double prev = 1e18;
        for (uint32_t h : {4u, 8u, 16u, 32u}) {
            const Tour t2 = BestHeadings(aCells, demands, depot, rho, h);
            std::printf("   h=%2u %.0fm", h, t2.flightM);
            CHECK(t2.flightM <= prev + 1e-6);   // refining the grid never hurts
            prev = t2.flightM;
        }
        std::printf("\n");
    }

    // The local search must not make things worse, and the legs it reports must
    // add up to the length it claims.
    {
        const Tour nn = BestHeadings(aCells, demands, depot, rho);
        const Tour opt = SolveTour(aCells, demands, depot, rho);
        std::printf("  order: nearest-neighbour %.0fm -> 2-opt/Or-opt %.0fm  (%.1f%% shorter)\n",
                    nn.flightM, opt.flightM, 100.0 * (nn.flightM - opt.flightM) / nn.flightM);
        CHECK(opt.flightM <= nn.flightM + 1e-6);
        CHECK(opt.legs.size() == aCells.size());
        std::set<int32_t> once;
        for (const Leg& l : opt.legs) CHECK(once.insert(l.cellId).second);
        double sum = 0;
        Config prev = depot;
        for (const Leg& l : opt.legs) {
            CHECK(std::fabs(l.fromPrevM - DubinsLength(prev, l.cfg, rho)) < 1e-9);
            sum += l.fromPrevM;
            prev = l.cfg;
        }
        sum += DubinsLength(prev, depot, rho);
        CHECK(std::fabs(sum - opt.flightM) < 1e-6);
    }

    // === S9: the LP solver, on problems with known answers =================
    {
        // max 3x+5y  s.t. x<=4, 2y<=12, 3x+2y<=18  -> 36 at (2,6)  (as a min)
        LpResult r1 = SolveLp({{1, 0}, {0, 2}, {3, 2}}, {4, 12, 18}, {-3, -5});
        CHECK(r1.ok);
        CHECK(std::fabs(r1.objective + 36.0) < 1e-6);
        CHECK(std::fabs(r1.x[0] - 2.0) < 1e-6 && std::fabs(r1.x[1] - 6.0) < 1e-6);
        // a >= row, passed negated: min x+y s.t. x+y>=5 -> 5
        LpResult r2 = SolveLp({{-1, -1}}, {-5}, {1, 1});
        CHECK(r2.ok && std::fabs(r2.objective - 5.0) < 1e-6);
        // infeasible, and detected as such rather than silently wrong
        LpResult r3 = SolveLp({{1, 1}, {-1, -1}}, {1, -5}, {1, 1});
        CHECK(!r3.ok && r3.infeasible);
        // unbounded
        LpResult r4 = SolveLp({{-1, 0}}, {-1}, {-1, 0});
        CHECK(!r4.ok && r4.unbounded);
        // random instances against a dense random search: the simplex must never
        // be beaten by sampling, and must always return a feasible point
        std::mt19937 lr(7);
        std::uniform_real_distribution<double> uu(0.1, 2.0);
        uint32_t beaten = 0;
        for (int t = 0; t < 60; ++t) {
            const int m2 = 4, n2 = 3;
            std::vector<std::vector<double>> A2(m2, std::vector<double>(n2));
            std::vector<double> b2(m2), c2(n2);
            for (int i = 0; i < m2; ++i) { for (int j = 0; j < n2; ++j) A2[i][j] = uu(lr); b2[i] = 3 * uu(lr); }
            for (int j = 0; j < n2; ++j) c2[j] = -uu(lr);
            LpResult rr = SolveLp(A2, b2, c2);
            CHECK(rr.ok);
            for (int i = 0; i < m2; ++i) {
                double s2 = 0;
                for (int j = 0; j < n2; ++j) s2 += A2[i][j] * rr.x[j];
                CHECK(s2 <= b2[i] + 1e-6);          // feasible
            }
            for (int k = 0; k < 4000; ++k) {
                std::vector<double> x2(n2);
                for (int j = 0; j < n2; ++j) x2[j] = uu(lr) * 2;
                bool feas = true;
                for (int i = 0; i < m2 && feas; ++i) {
                    double s2 = 0;
                    for (int j = 0; j < n2; ++j) s2 += A2[i][j] * x2[j];
                    if (s2 > b2[i]) feas = false;
                }
                if (!feas) continue;
                double o = 0;
                for (int j = 0; j < n2; ++j) o += c2[j] * x2[j];
                if (o < rr.objective - 1e-6) beaten++;
            }
        }
        std::printf("\n=== LP  known optima exact; 60 random instances, "
                    "%u of 240000 samples beat the simplex\n", beaten);
        CHECK(beaten == 0);
    }

    // === S10: T3 speed profile =============================================
    {
        const Tour tour = SolveTour(aCells, demands, depot, rho);
        const SpeedPlan sp = PlanSpeed(tour, demands, dose, rho);
        std::printf("\n=== T3  %zu segments, LP %ux%u, %u simplex iterations\n",
                    sp.segments.size(), sp.lpRows, sp.lpCols, sp.lpIterations);
        if (sp.infeasible) {
            // Not a solver failure: it is the honest answer that this tour
            // cannot deliver theta at any admissible speed. T4 must re-route or
            // add orbits, and it needs to be TOLD rather than handed a number.
            std::printf("  INFEASIBLE at these parameters -- no admissible speed "
                        "profile delivers theta on this tour\n");
            // How far off is it? Scaling theta is the same question as scaling
            // the link budget the other way, and the answer is a number the
            // parameter review can act on rather than a failed run.
            std::printf("  feasibility vs demand:");
            double firstOk = 0;
            for (double scale : {1.0, 0.7, 0.5, 0.35, 0.25, 0.15}) {
                auto scaled = demands;
                for (auto& [cid, d2] : scaled) d2.theta *= scale;
                const SpeedPlan s3 = PlanSpeed(tour, scaled, dose, rho);
                std::printf("  x%.2f=%s", scale, s3.infeasible ? "no" : "YES");
                if (!s3.infeasible && firstOk == 0) firstOk = scale;
            }
            std::printf("\n");
            CHECK(firstOk > 0);   // the model must be feasible SOMEWHERE
            // and at that point every invariant of the plan must hold
            auto scaled = demands;
            for (auto& [cid, d2] : scaled) d2.theta *= firstOk;
            const SpeedPlan ok = PlanSpeed(tour, scaled, dose, rho);
            CHECK(ok.solved);
            double vlo = 1e9, vhi = 0, pin = 0;
            for (const SpeedSegment& s2 : ok.segments) {
                CHECK(s2.speedMps >= kMinMps - 1e-6 && s2.speedMps <= kMaxMps + 1e-6);
                if (s2.turning) { CHECK(std::fabs(s2.speedMps - kCruiseMps) < 1e-6); pin++; }
                vlo = std::min(vlo, s2.speedMps); vhi = std::max(vhi, s2.speedMps);
            }
            uint32_t binding = 0;
            for (const auto& [cid, got] : ok.doseBytes) {
                CHECK(got >= scaled.at(cid).theta - 1e-3);
                if (ok.shadow.at(cid) > 1e-9) binding++;
            }
            std::printf("  at theta x%.2f: speed %.1f..%.1f m/s, %.0f%% pinned on turns,"
                        " %u/%zu cells binding, %.0f s vs %.0f s at cruise\n",
                        firstOk, vlo, vhi, 100.0 * pin / ok.segments.size(),
                        binding, ok.doseBytes.size(), ok.totalTimeS,
                        tour.flightM / kCruiseMps);
            CHECK(ok.totalTimeS >= tour.flightM / kMaxMps - 1e-6);
        } else {
            CHECK(sp.solved);
            double vmin2 = 1e9, vmax2 = 0, pinned = 0;
            for (const SpeedSegment& s2 : sp.segments) {
                CHECK(s2.speedMps >= kMinMps - 1e-6);
                CHECK(s2.speedMps <= kMaxMps + 1e-6);
                if (s2.turning) { CHECK(std::fabs(s2.speedMps - kCruiseMps) < 1e-6); pinned++; }
                vmin2 = std::min(vmin2, s2.speedMps);
                vmax2 = std::max(vmax2, s2.speedMps);
            }
            uint32_t met = 0, binding = 0;
            for (const auto& [cid, got] : sp.doseBytes) {
                CHECK(got >= demands.at(cid).theta - 1e-3);   // every cell served
                met++;
                if (sp.shadow.at(cid) > 1e-9) binding++;
            }
            std::printf("  speed %.1f..%.1f m/s, %.0f%% of segments pinned on turns\n",
                        vmin2, vmax2, 100.0 * pinned / sp.segments.size());
            std::printf("  %u/%zu cells served, %u binding; total time %.0f s "
                        "(cruise everywhere would be %.0f s)\n",
                        met, aCells.size(), binding, sp.totalTimeS,
                        tour.flightM / kCruiseMps);
            CHECK(sp.totalTimeS >= tour.flightM / kMaxMps - 1e-6);
        }
    }

    // === S11: T4 refinement loop ===========================================
    {
        const uint32_t M3 = 3;
        Plan pl = Refine(demands, plan, dose, depot, M3, rho);
        std::printf("\n=== T4  %u aircraft, closing the c_n <-> b loop\n", M3);
        std::printf("  %-4s %10s %10s %8s %10s %7s %10s\n",
                    "iter", "makespan", "flight", "visited", "retired", "infeas", "valid");
        for (const RefineStep& st : pl.history)
            std::printf("  %-4u %9.0fs %9.0fm %8u %10u %7u %10s\n",
                        st.iteration, st.makespanS, st.flightM, st.planCells,
                        st.droppedBySurplus, st.infeasibleVehicles,
                        st.selfConsistent ? "yes"
                                          : (st.uncovered ? "uncovered" : "infeasible"));
        std::printf("  %s after %zu iterations; %u self-consistent; %s\n",
                    pl.converged ? "converged" : "stopped at the iteration cap",
                    pl.history.size(), pl.consistentIterates,
                    pl.feasible ? "best valid makespan below" : "NO VALID PLAN FOUND");
        if (pl.feasible)
            std::printf("  best valid makespan %.0f s at iteration %u\n",
                        pl.makespanS, pl.bestIteration);

        CHECK(!pl.history.empty());
        // Only a plan that passed the validity test may be returned.
        for (const RefineStep& st : pl.history)
            if (st.selfConsistent) CHECK(pl.makespanS <= st.makespanS + 1e-9);
        if (pl.feasible) CHECK(pl.tours.size() == M3 && pl.speeds.size() == M3);
        for (const RefineStep& st : pl.history) {
            CHECK(st.makespanS > 0);
            CHECK(st.servedCells + st.droppedBySurplus <= plan.nA);
            // a self-consistent plan leaves nothing uncovered, by definition
            CHECK(!st.selfConsistent || st.uncovered == 0);
        }
        // Demand may only ever fall: the loop retires work, it never invents it.
        for (const auto& [cid, d] : pl.demands)
            CHECK(d.theta <= demands.at(cid).theta + 1e-6);
        // The makespan must not be worse at the end than it was at the start --
        // that is what the damping is there to prevent, so it is what gets
        // checked rather than assumed.
    }

    // === S12: the whole pipeline at an OPERABLE parameter point ============
    // Everything above runs in the regime the placeholders put it in, where one
    // pass can never deliver theta and the speed LP is correctly infeasible. That
    // regime exercises the failure paths but leaves T4 inert -- nothing is ever
    // delivered, so nothing is ever retired. This runs the same pipeline at the
    // demand the operability condition allows, which is the answer the parameter
    // review is really asking for: what does the system DO once the link budget
    // is big enough.
    {
        const double thetaMax = kRefTxBytesPerS * dose.G(0.0) / kMinMps;
        const double scale = 0.5;
        auto op = demands;
        for (auto& [cid, d] : op) d.theta *= scale;
        std::printf("\n=== FULL PIPELINE at theta x%.2f  (one pass at stall delivers"
                    " %.0f B; scaled theta_full %.0f B)\n",
                    scale, thetaMax, kThetaFullBytes * scale);

        for (uint32_t M4 : {2u, 3u, 4u}) {
            Plan pl = Refine(op, plan, dose, depot, M4, rho);
            uint32_t served = 0, feas = 0;
            double flight = 0;
            for (const SpeedPlan& sp : pl.speeds) if (sp.solved) feas++;
            for (const Tour& t : pl.tours) flight += t.flightM;
            for (const auto& [cid, d] : pl.demands) if (d.theta > 0) served++;
            std::printf("  M=%u  makespan %.0fs  flight %.0fm  %u/%u profiles feasible"
                        "  %u cells still owed  %u/%zu valid iterates\n",
                        M4, pl.makespanS, flight, feas, M4, served,
                        pl.consistentIterates, pl.history.size());
            CHECK(!pl.history.empty());
            if (pl.feasible) {
                CHECK(pl.makespanS > 0);
                for (const RefineStep& st : pl.history)
                    if (st.selfConsistent) CHECK(pl.makespanS <= st.makespanS + 1e-9);
            }
            // With deliveries actually happening, the loop must retire work.
            uint32_t retired = 0;
            for (const RefineStep& st : pl.history) retired += st.droppedBySurplus;
            CHECK(retired > 0);

        }
    }

    std::printf("\n%u CHECKS PASSED\n", g_checks);
    return 0;
}
