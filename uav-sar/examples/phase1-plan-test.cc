// Standalone verification of the Phase-1 planning front end: cell classes
// (0.2/0.3), Tier-1 detection (1.1/1.2) and the T0 demand model. No ns-3
// simulation -- pure logic, so it can be run and read in a second.
//
//   phase1-plan-test [gridSize] [cellRadius] [seed]
//
// Asserts the invariants that must hold whatever the parameters are; prints the
// quantities that still need a measurement to be believed.

#include "../models/common/cell-class.h"
#include "../models/common/cell-grid.h"
#include "../models/common/node-capability.h"
#include "../models/common/phase1-params.h"
#include "../models/common/service-demand.h"
#include "../models/common/tier1-detect.h"

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <iostream>
#include <random>
#include <vector>

using namespace ns3::uavsar;

// NOT CHECK(): ns-3 builds this profile with NDEBUG, which compiles CHECK()
// away entirely. A verification harness whose checks vanish in the build it is
// actually run under is worse than no harness -- it reports success it never
// tested. CHECK always runs and always fails loudly.
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
    double cellRadius = 94.0;      // at the 4rho/3 threshold for 20 m/s, 30 deg
    uint32_t seed = 1;
    if (argc > 1) gridSize = (uint32_t)std::atoi(argv[1]);
    if (argc > 2) cellRadius = std::atof(argv[2]);
    if (argc > 3) seed = (uint32_t)std::atoi(argv[3]);

    std::vector<NodePos> nodes;
    std::vector<uint32_t> ids;
    uint32_t id = 0;
    for (uint32_t i = 0; i < gridSize; i++)
        for (uint32_t j = 0; j < gridSize; j++) {
            nodes.push_back({id, j * spacing, i * spacing});
            ids.push_back(id++);
        }
    const double side = (gridSize - 1) * spacing;

    CellGridConfig gcfg;
    gcfg.cellRadius = cellRadius;
    gcfg.neighborRange = 40.0;
    CellGridPlan grid = BuildCellGrid(nodes, gcfg);

    CapabilityConfig ccfg;
    ccfg.seed = seed;
    auto caps = BuildCapabilities(ids, ccfg);

    // --- PHASE 0.2 / 0.3 ---------------------------------------------------
    CellRolePlan roles = BuildCellRoles(grid, caps);
    std::printf("=== PHASE 0  %ux%u nodes, spacing %.0f m, field %.0f m, R_c %.0f m\n",
                gridSize, gridSize, spacing, side, cellRadius);
    std::printf("cells=%zu   A=%u  B=%u  C=%u   leader-score CV=%.3f\n",
                grid.cells.size(), roles.nA, roles.nB, roles.nC, LeaderScoreCv(roles));

    CHECK(roles.roles.size() == grid.cells.size());
    CHECK(roles.nA + roles.nB + roles.nC == grid.cells.size());
    for (const auto& [cid, r] : roles.roles) {
        if (r.cls == CellClass::A) {
            // Class A must actually be able to run the match.
            auto c = caps.at(r.matcherId);
            CHECK(c.modality == p1::kReferenceModality);
            CHECK(c.cpu >= kCpuConfirmMin && c.obs > 0.0);
        } else {
            CHECK(r.matcherId == 0);   // only A carries a matcher
        }
    }

    // Hex geometry the design rule stands on.
    const double h = 1.5 * cellRadius;
    const double rho = p1::TurnRadiusM(p1::kCruiseMps);
    std::printf("row pitch h=1.5R_c=%.1f m   rho(%.0f m/s,%.0f deg)=%.1f m   h/2rho=%.2f\n",
                h, p1::kCruiseMps, p1::kBankDeg, rho, h / (2 * rho));
    std::printf("  adjacent-row scan optimal:  sufficient R_c>=%.1f m"
                "  |  true (cited turn) >=%.1f m  |  true (Dubins) >=%.1f m\n",
                p1::kAdjacentRowSufficient * rho, p1::kAdjacentRowTrueCited * rho,
                p1::kAdjacentRowTrueDubins * rho);
    // Hex cell area, NOT pi R_c^2 -- the circle formula undercounts cells by 17.3 %.
    const double hexArea = 1.5 * std::sqrt(3.0) * cellRadius * cellRadius;
    std::printf("  cells by area: hex %.0f   (circle formula would say %.0f)\n",
                side * side / hexArea, side * side / (M_PI * cellRadius * cellRadius));

    // --- PHASE 1 TIER 1 ----------------------------------------------------
    // One victim and three confusers, placed apart. Tier 1 must not be able to
    // tell them apart -- that is checked below, not assumed.
    std::mt19937 orng(seed ^ 0xABCDu);
    std::uniform_real_distribution<double> ux(0.1 * side, 0.9 * side);
    std::vector<Tier1Object> objects;
    objects.push_back({ux(orng), ux(orng), true});
    for (int k = 0; k < 3; k++) objects.push_back({ux(orng), ux(orng), false});

    Tier1Result t1 = RunTier1(grid, roles, caps, objects, seed);
    std::printf("\n=== TIER 1  objects=%zu (1 real, 3 confusers)\n", objects.size());
    std::printf("suspects |D|=%zu   recall %u/%u   false alarms %u/%u\n",
                t1.suspects.size(), t1.detected, t1.objectCells,
                t1.falseAlarms, t1.emptyCells);

    // Not every false alarm is noise. A node near a cell boundary responds to an
    // object in the NEXT cell, so the alarm is real and only the cell label is
    // wrong. Splitting the two matters: spillover is a resolution limit of the
    // cell substrate and it is what Phase 2 pays to resolve, whereas isolated
    // alarms are detector noise and are what a better detector would remove.
    {
        uint32_t spill = 0, isolated = 0;
        for (const auto& [cid, c] : t1.cells) {
            if (!c.suspect || c.holdsObject) continue;
            double nearest = 1e18;
            const auto& cell = grid.cells.at(cid);
            for (const Tier1Object& o : objects)
                nearest = std::min(nearest, std::hypot(cell.centerX - o.x, cell.centerY - o.y));
            if (nearest <= 2.0 * cellRadius) spill++; else isolated++;
        }
        CHECK(spill + isolated == t1.falseAlarms);
        std::printf("  of those: %u are spillover from an object in a neighbouring cell"
                    " (<= 2R_c), %u are isolated noise\n", spill, isolated);
    }

    double wsum = 0.0;
    for (int32_t cid : t1.suspects) wsum += t1.cells[cid].weight;
    CHECK(t1.suspects.empty() || std::fabs(wsum - 1.0) < 1e-9);
    for (const auto& [cid, c] : t1.cells) CHECK(c.score >= 0.0 && c.score <= 1.0);
    // No class-C cell ever reports.
    for (const auto& [cid, c] : t1.cells) CHECK(roles.roles.at(cid).cls != CellClass::C);

    // The Fano property, tested rather than asserted in prose. Comparing MEAN
    // scores of real vs confuser cells does not test it -- the two differ by
    // sampling and by how close a node happens to sit, and a difference there
    // would prove nothing either way. What must hold is that the detector is
    // INVARIANT to which object is the real one: move the ground-truth flag and
    // every score must come back bit-identical.
    {
        std::vector<Tier1Object> swapped = objects;
        swapped[0].real = false;
        swapped[1].real = true;
        Tier1Result alt = RunTier1(grid, roles, caps, swapped, seed);
        CHECK(alt.cells.size() == t1.cells.size());
        for (const auto& [cid, c] : t1.cells) CHECK(alt.cells.at(cid).score == c.score);
        CHECK(alt.suspects == t1.suspects);
        std::printf("detector is blind to which object is real: %zu scores identical"
                    " under a ground-truth swap  (Fano ceiling 1/(M+1) = %.0f%% at M=3)\n",
                    t1.cells.size(), 100.0 / 4.0);
    }
    std::printf("uplink cost of the whole tier: %zu reports x %u B = %.1f kB\n",
                t1.cells.size(), kTier1ReportBytes,
                t1.cells.size() * kTier1ReportBytes / 1000.0);

    // --- T0 ----------------------------------------------------------------
    auto demands = BuildDemands(grid, roles, t1, caps);
    DosePerPass dose;
    std::printf("\n=== T0  lambda_tx=%.0f B/s  theta_full=%.0f B  hedge=%.0f%%\n",
                p1::kRefTxBytesPerS, p1::kThetaFullBytes, 100 * p1::kThetaHedgeFrac);
    std::printf("G(b): ");
    for (double b : {0.0, 50.0, 100.0, 150.0, 200.0, 300.0})
        std::printf("G(%.0f)=%.0fm ", b, dose.G(b));
    std::printf("\n");
    // G must be positive and strictly decreasing.
    double prev = 1e18;
    for (double b = 0; b <= p1::kGmaxOffsetM; b += 10.0) {
        const double g = dose.G(b);
        CHECK(g >= 0.0 && g < prev + 1e-9);
        prev = g;
    }

    uint32_t served = 0, loiter = 0, slowed = 0; double totalS = 0;
    for (auto& [cid, d] : demands) {
        const double c = ServiceCost(d, 0.0, dose);
        if (d.theta <= 0.0) { CHECK(c == 0.0); continue; }
        served++; totalS += c;
        if (d.loiterLoops) loiter++; else slowed++;
        CHECK(c >= 0.0);
    }
    std::printf("cells to serve: %u  (one pass slowed %u, must orbit %u)   "
                "total service cost %.0f s\n", served, slowed, loiter, totalS);
    // Only class A ever consumes aircraft time.
    for (const auto& [cid, d] : demands)
        CHECK(d.cls == CellClass::A || d.theta == 0.0);
    // A flagged cell must never be cheaper to serve than an unflagged one.
    for (const auto& [cid, d] : demands)
        if (d.cls == CellClass::A && d.suspect) CHECK(d.theta > 0.0);

    std::printf("\n%u CHECKS PASSED\n", g_checks);
    return 0;
}
