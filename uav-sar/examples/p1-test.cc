// Verification harness for the Phase-1 subtree (models/p1/). Pure logic, no
// ns-3 simulation. Built and run after every step, not at the end.
//
//   p1-test [gridSize] [cellRadius] [seed]

#include "../models/common/cell-grid.h"   // ONLY to cross-check the hex duplicate
#include "../models/p1/p1-cells.h"
#include "../models/p1/p1-hex.h"
#include "../models/p1/p1-params.h"
#include "../models/p1/p1-sensing.h"

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
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

    std::printf("\n%u CHECKS PASSED\n", g_checks);
    return 0;
}
