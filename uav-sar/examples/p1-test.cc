// Verification harness for PA1: PHA 0 (P0.0-P0.6) -> T0 -> T1. Pure logic.
//
//   p1-test [gridSize] [cellRadius] [seed]
//
// Scope stops after the partition, on purpose: T2 onward is not implemented, so
// nothing here may depend on it.

#include "../models/common/cell-grid.h"   // ONLY to cross-check the hex duplicate
#include "../models/p1/p1-cells.h"
#include "../models/p1/p1-demand.h"
#include "../models/p1/p1-dubins.h"
#include "../models/p1/p1-field.h"
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
    const double rho = TurnRadiusM(kCruiseMps);

    // === hex duplicate is a VERIFIED duplicate ==============================
    {
        uint32_t n = 0;
        for (double x = -500; x <= 500; x += 9.1)
            for (double y = -500; y <= 500; y += 9.1) {
                int32_t q1, r1, q2, r2;
                hex::WorldToAxial(x, y, rc, q1, r1);
                ns3::uavsar::hex::WorldToAxial(x, y, rc, q2, r2);
                CHECK(q1 == q2 && r1 == r2);
                n++;
            }
        std::printf("hex duplicate verified against cell-grid over %u points\n", n);
    }

    // === P0.0 / P0.1: domain and sweep direction ===========================
    // The field is a rectangle rotated 20 degrees, so psi has a right answer
    // that is NOT the axis -- an axis-aligned bug would pass on a square.
    const double side = (gridSize - 1) * spacing;
    const double tilt = 20.0 * M_PI / 180.0;
    const double W = side, H = side * 0.62;      // deliberately not square
    std::vector<Point> boundary;
    for (auto [u, v] : {std::pair<double, double>{0, 0}, {W, 0}, {W, H}, {0, H}})
        boundary.push_back({u * std::cos(tilt) - v * std::sin(tilt),
                            u * std::sin(tilt) + v * std::cos(tilt)});
    Field field = BuildField(boundary, kBoundaryTolM);

    std::printf("\n=== P0.0/P0.1  hull %zu pts, area %.0f m^2, min width %.1f m,"
                " psi = %.2f deg\n", field.hull.size(), field.areaM2,
                field.minWidthM, field.psiRad * 180 / M_PI);
    // Rotating calipers is exact; a brute-force angular scan must not beat it.
    {
        double bestScan = 1e18;
        for (int a = 0; a < 3600; ++a) {
            const double th = a * M_PI / 1800.0;
            double lo = 1e18, hi = -1e18;
            for (const Point& p : field.hull) {
                const double w = -std::sin(th) * p.x + std::cos(th) * p.y;
                lo = std::min(lo, w); hi = std::max(hi, w);
            }
            bestScan = std::min(bestScan, hi - lo);
        }
        std::printf("  calipers %.3f m vs 0.1-degree brute scan %.3f m\n",
                    field.minWidthM, bestScan);
        CHECK(field.minWidthM <= bestScan + 1e-6);
        // For a rectangle the answer is the short side, and psi runs along the long one.
        CHECK(std::fabs(field.minWidthM - H) < 1e-6);
        double dpsi = std::fmod(std::fabs(field.psiRad - tilt), M_PI);
        if (dpsi > M_PI / 2) dpsi = M_PI - dpsi;
        CHECK(dpsi < 1e-6);
    }
    // The row frame must be a rigid motion: round-tripping is the identity.
    {
        double u, w, x2, y2;
        for (double x = -300; x <= 300; x += 37)
            for (double y = -300; y <= 300; y += 41) {
                field.ToRowFrame(x, y, u, w);
                field.FromRowFrame(u, w, x2, y2);
                CHECK(std::fabs(x - x2) < 1e-9 && std::fabs(y - y2) < 1e-9);
            }
    }

    // === P0.2 - P0.5: cells, rows, offsets, heads ==========================
    std::vector<std::pair<double, double>> xy;
    for (uint32_t i = 0; i < gridSize; i++)
        for (uint32_t j = 0; j < gridSize; j++) {
            const double u = j * spacing * (W / side), v = i * spacing * (H / side);
            xy.push_back({u * std::cos(tilt) - v * std::sin(tilt),
                          u * std::sin(tilt) + v * std::cos(tilt)});
        }
    std::vector<Node> nodes = BuildNodes(xy, seed);
    CellPlan plan = BuildCells(nodes, field, rc, kGroundRangeM, rho);

    std::printf("\n=== PHASE 0   %ux%u nodes, R_c=%.0fm, rho=%.1fm (%.2f rho)\n",
                gridSize, gridSize, rc, rho, rc / rho);
    std::printf("cells=%zu over %zu rows   served=%u barren=%u"
                "  (F1 failures: %u cells had cameras but none reachable)\n",
                plan.cells.size(), plan.cellsByRow.size(), plan.nServed,
                plan.nBarren, plan.nInfeasible);
    std::printf("a=%.1fm  h=%.1fm  delta_max=%.1fm = %.3f R_c"
                "   (4/pi^2 = 0.405 exactly at R_c = 4rho/3)\n",
                plan.cellPitchM, plan.rowPitchM, plan.maxOffsetM,
                plan.maxOffsetM / rc);
    std::printf("  adjacent-row scan optimal: SUFFICIENT R_c>=%.1fm"
                " | true(cited)>=%.1fm | true(Dubins)>=%.1fm\n",
                kAdjacentSufficient * rho, kAdjacentTrueCited * rho,
                kAdjacentTrueDubins * rho);

    std::map<uint32_t, const Node*> byId;
    for (const Node& n : nodes) byId[n.id] = &n;

    // I1: row centres are equally spaced by h in the row frame.
    for (const auto& [cid, c] : plan.cells) {
        double u, w;
        field.ToRowFrame(c.cx, c.cy, u, w);
        CHECK(std::fabs(w - plan.RowLineW(c.row)) < 1e-6);
    }
    // Every node in exactly one cell, and its offset is what P0.4 says.
    {
        std::map<uint32_t, uint32_t> seen;
        for (const auto& [cid, c] : plan.cells)
            for (const CellMember& m : c.members) {
                seen[m.id]++;
                CHECK(plan.cellOfNode.at(m.id) == cid);
                double u, w;
                field.ToRowFrame(byId[m.id]->x, byId[m.id]->y, u, w);
                CHECK(std::fabs(m.offsetM - std::fabs(w - plan.RowLineW(c.row))) < 1e-9);
                CHECK(m.eligible == (byId[m.id]->HasCamera() &&
                                     m.offsetM <= plan.maxOffsetM));
            }
        CHECK(seen.size() == nodes.size());
        for (const auto& [id, k] : seen) CHECK(k == 1);
    }
    // I2: the elected head is ALWAYS within delta_max. This is the invariant the
    // whole weave model rests on, so it is checked and not assumed.
    for (const auto& [cid, c] : plan.cells) {
        CHECK(c.cls == (c.hasHead ? CellClass::SERVED : CellClass::BARREN));
        if (!c.hasHead) continue;
        CHECK(c.headOffsetM <= plan.maxOffsetM + 1e-9);
        CHECK(byId[c.head]->HasCamera());
        // and it must be the BEST eligible node under P0.5, not merely one
        double best = 1e18;
        for (const CellMember& m : c.members) {
            if (!m.eligible) continue;
            const double s =
                DoseBytes(FilesNeeded(byId[m.id]->Information())) / kRefTxBytesPerS +
                WeaveExtraM(m.offsetM, plan.cellPitchM) / kCruiseMps;
            best = std::min(best, s);
        }
        CHECK(std::fabs(c.headScoreS - best) < 1e-9);
    }
    // The weave the head demands must be flyable: curvature within rho.
    for (const auto& [cid, c] : plan.cells) {
        if (!c.hasHead) continue;
        const double a = plan.cellPitchM;
        const double minRadius = a * a / (M_PI * M_PI * std::max(1e-9, c.headOffsetM));
        CHECK(minRadius >= rho - 1e-6);
    }

    // --- F1 as a function of how many candidates a cell has ----------------
    {
        std::map<uint32_t, std::pair<uint32_t, uint32_t>> byCand;   // cameras -> (cells, failed)
        for (const auto& [cid, c] : plan.cells) {
            if (c.cameras == 0) continue;
            auto& e = byCand[std::min(c.cameras, 12u)];
            e.first++;
            if (!c.hasHead) e.second++;
        }
        std::printf("F1 -- cells with cameras but no reachable head, by candidate count:\n ");
        for (const auto& [k, e] : byCand)
            std::printf("  n_c=%u: %u/%u", k, e.second, e.first);
        std::printf("\n");
    }

    // === P0.6 + T0 ==========================================================
    DoseModel dose;
    auto demands = BuildDemands(plan, nodes);
    std::printf("\n=== P0.6/T0   Pe*=%.3f  J=%u  Fano floor=%.3f  K=%u files x %u B\n",
                kTargetPe, kConfusers, FanoFloor(), kFileCount, kFileBytes);
    // F2: below the Fano floor the flight is pointless -- a reference-free node
    // is already bounded there, so asking for less is asking the impossible.
    CHECK(kTargetPe < FanoFloor());
    std::printf("  F2 %s: target error %.3f < 1/(J+1) = %.3f\n",
                kTargetPe < FanoFloor() ? "holds" : "VIOLATED", kTargetPe, FanoFloor());

    // k_n must fall as capability rises, and theta must rise with k.
    {
        uint32_t kLo = FilesNeeded(1.0), kHi = FilesNeeded(0.1);
        CHECK(kLo <= kHi);
        CHECK(DoseBytes(kLo) <= DoseBytes(kHi));
        std::printf("  I=1.00 -> k=%u files, theta=%.0f B     "
                    "I=0.10 -> k=%u files, theta=%.0f B\n",
                    kLo, DoseBytes(kLo), kHi, DoseBytes(kHi));
    }

    uint32_t served = 0, orbiting = 0, infeasible = 0;
    double totalC = 0, weaveTot = 0;
    for (auto& [cid, d] : demands) {
        const double c = ServiceCost(d, dose, plan.cellPitchM, rho);
        if (d.cls != CellClass::SERVED) { CHECK(d.theta == 0.0); CHECK(c == 0.0); continue; }
        CHECK(d.theta > 0.0);
        CHECK(d.files >= 1);
        served++;
        totalC += c;
        weaveTot += d.weaveS;
        if (d.orbits) orbiting++;
        if (!d.feasible) infeasible++;
    }
    std::printf("  %u heads: %u need orbits, %u fail F3;  service %.0f s"
                " of which weave %.0f s (%.0f%%)\n",
                served, orbiting, infeasible, totalC, weaveTot,
                totalC > 0 ? 100 * weaveTot / totalC : 0.0);
    std::printf("  ONE pass delivers %.0f B at cruise, %.0f B at stall\n",
                kRefTxBytesPerS * dose.G(0.0) / kCruiseMps,
                kRefTxBytesPerS * dose.G(0.0) / kMinMps);

    // T0.2: no iteration. The offset used is the one P0.5 fixed, so running the
    // cost twice must give the same answer -- there is nothing to converge to.
    for (auto& [cid, d] : demands) {
        Demand again = d;
        const double c1 = ServiceCost(again, dose, plan.cellPitchM, rho);
        const double c2 = ServiceCost(again, dose, plan.cellPitchM, rho);
        CHECK(c1 == c2);
        CHECK(std::fabs(again.offsetM - plan.cells.at(cid).headOffsetM) < 1e-12);
    }

    // === Dubins (geometry only; used to MEASURE, never to steer) ============
    {
        std::mt19937 dr(4242);
        std::uniform_real_distribution<double> ux2(-600, 600), uh(0, 2 * M_PI);
        double worst = 0;
        for (int k = 0; k < 3000; ++k) {
            Config a{ux2(dr), ux2(dr), uh(dr)}, b{ux2(dr), ux2(dr), uh(dr)};
            const DubinsPath pth = Dubins(a, b, rho);
            CHECK(pth.valid);
            const Config e = Integrate(a, pth, rho);
            worst = std::max(worst, std::hypot(e.x - b.x, e.y - b.y));
        }
        std::printf("\n=== DUBINS  worst endpoint error over 3000 pairs: %.2e m\n", worst);
        CHECK(worst < 1e-9);
    }
    // The row-change cost must agree with a real Dubins turn where the model
    // says it should -- above 2 rho, where the closed form is the true optimum.
    {
        double worstRel = 0;
        for (double d = 2.05 * rho; d < 8 * rho; d += 0.37 * rho) {
            const double closed = RowChangeM(d, rho);
            const double real = DubinsLength({0, 0, 0}, {0, d, M_PI}, rho);
            worstRel = std::max(worstRel, std::fabs(closed - real) / real);
        }
        std::printf("  row-change closed form vs true Dubins, d > 2rho:"
                    " worst %.2e relative\n", worstRel);
        CHECK(worstRel < 1e-9);
        // ... and it must be an OVERESTIMATE below 2 rho, where the true optimum
        // is a CCC path the cited family does not contain.
        double worstOver = 0;
        for (double d = 0.3 * rho; d < 1.95 * rho; d += 0.1 * rho) {
            const double closed = RowChangeM(d, rho);
            const double real = DubinsLength({0, 0, 0}, {0, d, M_PI}, rho);
            CHECK(closed >= real - 1e-9);
            worstOver = std::max(worstOver, (closed - real) / real);
        }
        std::printf("  below 2rho the cited form OVERSTATES the turn by up to %.1f%%"
                    " (true optimum is CCC)\n", 100 * worstOver);
    }

    // === T1: partition the ROWS ============================================
    auto work = BuildRows(plan, demands);
    const Depot depot{0.0, 0.0};
    std::printf("\n=== T1  %zu rows, %u heads, depot at the origin\n",
                work.size(), served);
    std::printf("%-22s %2s %10s %8s %9s %9s\n",
                "method", "M", "makespan", "spread", "turns", "depot");
    for (uint32_t M2 : {2u, 3u, 4u}) {
        Partition ps[3] = {
            PartitionCredit(work, plan, depot, M2, rho, false),
            PartitionCredit(work, plan, depot, M2, rho, true),
            PartitionSplit(work, plan, depot, M2, rho),
        };
        for (const Partition& q : ps) {
            std::set<int32_t> once;
            uint32_t n = 0;
            double turns = 0, dep = 0;
            for (const Block& b : q.vehicles) {
                for (int32_t r : b.rows) { n++; once.insert(r); }
                turns += b.changeS;
                dep += b.depotS;
            }
            CHECK(n == work.size());          // every row flown, exactly once
            CHECK(once.size() == work.size());
            CHECK(q.vehicles.size() == M2);
            CHECK(q.makespanS > 0);
            CHECK(q.imbalancePct >= 0 && q.imbalancePct <= 100.0);
            char name[48];
            std::snprintf(name, sizeof name, "%s%s", q.method,
                          std::string(q.method) == "credit"
                              ? (q.contiguous ? " (contiguous)" : " (free)") : "");
            std::printf("%-22s %2u %9.0fs %7.1f%% %8.0fs %8.0fs\n", name, M2,
                        q.makespanS, q.imbalancePct, turns, dep);
        }
    }

    std::printf("\n%u CHECKS PASSED\n", g_checks);
    return 0;
}
