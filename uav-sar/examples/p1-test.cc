// Verification harness for Phase 0 -> T0 -> T1. Pure logic, no ns-3 simulation.
// Built and run after every step, not at the end.
//
//   p1-test [gridSize] [cellRadius] [seed]
//
// Scope stops after the partition, on purpose: T2 onward is not implemented, so
// nothing here may depend on it.

#include "../models/common/cell-grid.h"   // ONLY to cross-check the hex duplicate
#include "../models/p1/p1-cells.h"
#include "../models/p1/p1-demand.h"
#include "../models/p1/p1-dubins.h"
#include "../models/p1/p1-hex.h"
#include "../models/p1/p1-params.h"
#include "../models/p1/p1-partition.h"
#include "../models/p1/p1-sensing.h"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <map>
#include <random>
#include <set>
#include <string>
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
    uint32_t gridSize = 40;
    double spacing = 20.0;
    double rc = kCellRadiusM;
    uint32_t seed = 1;
    if (argc > 1) gridSize = (uint32_t)std::atoi(argv[1]);
    if (argc > 2) rc = std::atof(argv[2]);
    if (argc > 3) seed = (uint32_t)std::atoi(argv[3]);

    // === S1: the hex duplicate is a VERIFIED duplicate =====================
    // p1-hex.h deliberately re-states the maths in cell-grid.cc rather than
    // depending on it (see the header for why). That is only safe if the two are
    // checked to agree, which is what this does.
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

    // === S2: PHASE 0 -- cells and heads ====================================
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
    std::printf("cells=%zu   served=%u barren=%u   head-score CV=%.3f\n",
                plan.cells.size(), plan.nServed, plan.nBarren, LeaderScoreCv(plan));
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
    CHECK(plan.nServed + plan.nBarren == plan.cells.size());
    CHECK(plan.cellOfNode.size() == nodes.size());
    {
        std::map<uint32_t, uint32_t> seen;
        for (const auto& [cid, c] : plan.cells)
            for (const CellMember& m : c.members) {
                seen[m.id]++;
                CHECK(plan.cellOfNode.at(m.id) == cid);
            }
        CHECK(seen.size() == nodes.size());
        for (const auto& [id, k] : seen) CHECK(k == 1);   // exactly one cell each
    }

    std::map<uint32_t, const Node*> byId;
    for (const Node& n : nodes) byId[n.id] = &n;

    // --- election: camera is a HARD filter, then priority ---
    for (const auto& [cid, c] : plan.cells) {
        uint32_t cameras = 0;
        for (const CellMember& m : c.members)
            if (byId[m.id]->HasCamera()) cameras++;
        CHECK(cameras == c.cameras);
        // The class is decided by ONE thing: does a camera exist here.
        CHECK(c.cls == (cameras > 0 ? CellClass::SERVED : CellClass::BARREN));
        if (c.cls == CellClass::SERVED) {
            CHECK(c.hasLeader);
            // N3: the head is the matching subject, so it must have a camera...
            CHECK(byId[c.leader]->HasCamera());
            // ...and it must be the BEST such node, not merely one of them.
            double best = -1;
            for (const CellMember& m : c.members)
                if (byId[m.id]->HasCamera())
                    best = std::max(best, byId[m.id]->ElectScore());
            CHECK(std::fabs(c.leaderScore - best) < 1e-12);
        }
        double cx, cy;
        hex::AxialToCentre(c.q, c.r, rc, cx, cy);
        CHECK(std::fabs(cx - c.cx) < 1e-9 && std::fabs(cy - c.cy) < 1e-9);
    }

    // --- tree invariants: rooted at the ELECTED head, acyclic ---
    {
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
                const CellMember* pa = mem.at((uint32_t)m.parent);
                CHECK(pa->hops == m.hops - 1);          // strictly closer: no cycles
                CHECK(std::hypot(byId[m.id]->x - byId[pa->id]->x,
                                 byId[m.id]->y - byId[pa->id]->y) <= kGroundRangeM + 1e-9);
            }
        }
        std::printf("intra-cell trees rooted at the elected head; %u members "
                    "unreachable in-cell\n", unreachable);
        std::printf("  (no payload travels down them: N3 makes the head the "
                    "matching subject)\n");
    }

    // Every node identical and fully capable: every cell servable, identical
    // scores. If not, the class rule is reading something other than capability.
    {
        CellPlan uni = BuildCells(BuildUniformNodes(xy), rc, kGroundRangeM);
        CHECK(uni.nBarren == 0);
        CHECK(uni.nServed == uni.cells.size());
        CHECK(LeaderScoreCv(uni) == 0.0);
        std::printf("uniform world: %u/%zu cells servable, head CV %.3f\n",
                    uni.nServed, uni.cells.size(), LeaderScoreCv(uni));
    }

    // --- 0.2.1: what the capability weighting actually buys ----------------
    // The spec asks for this number and marks it unmeasured. It is the whole
    // justification for changing PECEE's election rule, so it must be a
    // measurement -- and it must be measured over MANY WORLDS, because on one
    // seed it reads 1.91x and on another 0.82x. A single seed here would have
    // produced a confident claim in the wrong direction.
    //
    // What matters is not the mean capability -- it is the WEAKEST head, since
    // that cell carries the largest theta and therefore the hardest service cost
    // in the whole problem.
    {
        const int kSeeds = 12;
        double capW[kSeeds], cenW[kSeeds], rndW[kSeeds];
        for (int t = 0; t < kSeeds; ++t) {
            std::vector<Node> nn = BuildNodes(xy, 100 + t);
            std::map<uint32_t, const Node*> id2;
            for (const Node& n : nn) id2[n.id] = &n;
            double* dst[3] = {&capW[t], &cenW[t], &rndW[t]};
            for (int r = 0; r < 3; ++r) {
                CellPlan pr = BuildCells(nn, rc, kGroundRangeM, (Election)r, 100 + t);
                double lo = 1e18;
                uint32_t n = 0;
                for (const auto& [cid, c] : pr.cells) {
                    if (c.cls != CellClass::SERVED) continue;
                    lo = std::min(lo, id2[c.leader]->Information());
                    n++;
                }
                CHECK(n > 0);
                *dst[r] = lo;
            }
        }
        auto stat = [&](double* v, double& lo, double& med, double& hi2) {
            std::vector<double> a(v, v + kSeeds);
            std::sort(a.begin(), a.end());
            lo = a.front(); med = a[kSeeds / 2]; hi2 = a.back();
        };
        double a1, a2, a3, b1, b2, b3, c1, c2, c3;
        stat(capW, a1, a2, a3); stat(cenW, b1, b2, b3); stat(rndW, c1, c2, c3);
        std::printf("\n0.2.1 -- weakest head's I_n over %d worlds  (min / median / max)\n",
                    kSeeds);
        std::printf("  capability (design) %.3f / %.3f / %.3f\n", a1, a2, a3);
        std::printf("  centroid   (PECEE)  %.3f / %.3f / %.3f\n", b1, b2, b3);
        std::printf("  random     (null)   %.3f / %.3f / %.3f\n", c1, c2, c3);
        double rc1 = 1e18, rc2 = 0, rr1 = 1e18, rr2 = 0;
        uint32_t capWins = 0;
        for (int t = 0; t < kSeeds; ++t) {
            rc1 = std::min(rc1, capW[t] / cenW[t]);
            rc2 = std::max(rc2, capW[t] / cenW[t]);
            rr1 = std::min(rr1, capW[t] / rndW[t]);
            rr2 = std::max(rr2, capW[t] / rndW[t]);
            if (capW[t] > cenW[t]) capWins++;
        }
        // The verdict is DERIVED, not written in: a claim that survives one
        // parameter set and not another must change when the numbers change.
        std::printf("  capability / centroid: %.2fx .. %.2fx, better on %u of %d worlds"
                    "  -> %s\n", rc1, rc2, capWins, kSeeds,
                    (rc1 > 1.0 && capWins == kSeeds) ? "established"
                                                     : "NOT established");
        std::printf("  capability / random  : %.2fx .. %.2fx  -> %s\n", rr1, rr2,
                    rr1 > 1.0 ? "established" : "NOT established");
        // Where a node SITS says nothing about what it can DO, so the centroid
        // rule should land near the null. It does, and that is the cleanest way
        // to state what the election is worth: it is not that proximity is a bad
        // proxy for capability, it is that it is not a proxy at all.
        std::printf("  centroid vs random: median %.3f vs %.3f -- proximity to the"
                    " centre carries %s capability information\n", b2, c2,
                    std::fabs(b2 - c2) / c2 < 0.25 ? "essentially NO" : "some");
        // The null must lose. If it does not, the election is doing nothing.
        for (int t = 0; t < kSeeds; ++t) CHECK(capW[t] >= rndW[t]);
    }

    // === S3: T0 -- demand and service cost =================================
    DoseModel dose;
    auto demands = BuildDemands(plan, nodes);
    std::printf("\n=== T0   lambda_tx=%.0f B/s   theta(unit capability)=%.0f B"
                "   s=%.2f\n", kRefTxBytesPerS, ThetaFullBytes(), kConfuserSimilarity);
    std::printf("G(b):");
    for (double b : {0.0, 50.0, 100.0, 150.0, 200.0, 300.0})
        std::printf("  G(%.0f)=%.0fm", b, dose.G(b));
    std::printf("\n");

    // G must be positive, strictly decreasing, and match an independent integral.
    {
        double prev = 1e18;
        for (double b = 0; b <= kGmaxOffsetM; b += 5.0) {
            const double g = dose.G(b);
            CHECK(g >= 0.0);
            CHECK(g < prev + 1e-9);
            prev = g;
        }
        double ref = 0.0;
        const double hh = 0.5;
        for (double x = -1600.0; x <= 1600.0; x += hh) ref += dose.Prx(std::fabs(x)) * hh;
        CHECK(std::fabs(ref - dose.G(0.0)) / ref < 0.01);
        std::printf("  G(0) by Simpson %.2fm vs independent rectangle sum %.2fm\n",
                    dose.G(0.0), ref);
    }

    // Only a cell with a head ever costs the aircraft anything, at any offset.
    for (auto& [cid, d] : demands) {
        if (d.cls != CellClass::SERVED) {
            CHECK(d.theta == 0.0);
            CHECK(ServiceCost(d, 0.0, dose) == 0.0);
        } else {
            CHECK(d.theta > 0.0);
        }
    }
    // Serving is monotone in offset: further away is never cheaper.
    for (auto& [cid, d] : demands) {
        if (d.theta <= 0.0) continue;
        Demand a = d, b = d;
        CHECK(ServiceCost(b, 120.0, dose) >= ServiceCost(a, 0.0, dose) - 1e-9);
    }

    // theta spread: both feature quality and matcher strength enter (0.3.1), so
    // the spread is the product of their ranges. Reported because it sets how
    // hard the weakest cell makes the whole problem.
    {
        double lo = 1e18, hi2 = 0;
        uint32_t slowed = 0, orbited = 0;
        double total = 0;
        for (auto& [cid, d] : demands) {
            if (d.theta <= 0) continue;
            lo = std::min(lo, d.theta);
            hi2 = std::max(hi2, d.theta);
            total += ServiceCost(d, 0.0, dose);
            if (d.orbits) orbited++; else slowed++;
            CHECK((d.orbits > 0) == (d.serveMps == 0.0));
        }
        std::printf("theta over served cells: %.0f..%.0f B (spread %.1fx)\n",
                    lo, hi2, hi2 / lo);
        std::printf("cells to serve: %u   one pass slowed %u, must orbit %u   "
                    "total service %.0f s\n", slowed + orbited, slowed, orbited, total);
        const double thetaMax = kRefTxBytesPerS * dose.G(0.0) / kMinMps;
        const double thetaMin = kRefTxBytesPerS * dose.G(0.0) / kCruiseMps;
        std::printf("  one pass delivers %.0f B at cruise, %.0f B at stall\n",
                    thetaMin, thetaMax);
        std::printf("  -> theta below %.0f B needs no slow-down at all (T0 inert);"
                    " above %.0f B one pass can never be enough\n",
                    thetaMin, thetaMax);
    }

    // === S4: Dubins (geometry only -- used to MEASURE T1, never to steer it) ==
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
            CHECK(std::fabs(pth.length - (pth.seg[0] + pth.seg[1] + pth.seg[2]) * rho) < 1e-9);
        }
        std::printf("\n=== DUBINS  worst endpoint error over 4000 pairs: %.2e m\n", worst);
        std::printf("  words used:");
        for (int w = 0; w < 6; ++w) std::printf("  %s=%u", WordName((Word)w), words[w]);
        std::printf("\n");
        CHECK(worst < 1e-9);
        for (int w = 0; w < 6; ++w) CHECK(words[w] > 0);
    }

    // === S5: T1 partition ==================================================
    const Depot depot{0.0, 0.0};
    uint32_t need = 0;
    for (const auto& [cid, d] : demands) if (d.theta > 0) need++;
    std::printf("\n=== T1  partition over %u cluster heads, depot at the field corner\n",
                need);
    std::printf("%-22s %2s %10s %8s %12s %8s\n",
                "method", "M", "makespan", "spread", "Dubins real", "gap");
    for (uint32_t M2 : {2u, 3u, 4u}) {
        Partition ps[3] = {
            PartitionCredit(demands, plan, depot, M2, false),
            PartitionCredit(demands, plan, depot, M2, true),
            PartitionSplit(demands, depot, M2),
        };
        for (const Partition& q : ps) {
            uint32_t n = 0;
            std::set<int32_t> once;
            for (const Block& b : q.vehicles)
                for (int32_t c : b.cells) { n++; once.insert(c); }
            // every head that needs serving is served, exactly once
            CHECK(n == need);
            CHECK(once.size() == need);
            CHECK(q.vehicles.size() == M2);
            CHECK(q.makespanS > 0);
            CHECK(q.imbalancePct >= 0 && q.imbalancePct <= 100.0);

            // What the SAME partition costs when flown rather than estimated.
            // T1 optimises the Euclidean number by design (T2's job is the
            // kinematics); this says how far that yardstick is from the truth.
            double realMax = 0;
            for (const Block& b : q.vehicles)
                realMax = std::max(realMax, DubinsTravelS(b, demands, depot, rho) + b.serviceS);
            CHECK(realMax >= q.makespanS - 1e-6);   // turning is never cheaper

            char name[48];
            std::snprintf(name, sizeof name, "%s%s", q.method,
                          std::string(q.method) == "credit"
                              ? (q.contiguous ? " (contiguous)" : " (free)") : "");
            std::printf("%-22s %2u %9.0fs %7.1f%% %11.0fs %7.1f%%\n", name, M2,
                        q.makespanS, q.imbalancePct, realMax,
                        100.0 * (realMax - q.makespanS) / q.makespanS);
        }
    }

    std::printf("\n%u CHECKS PASSED\n", g_checks);
    return 0;
}
