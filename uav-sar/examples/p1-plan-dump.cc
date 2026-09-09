// Run PHA 0 -> T0 -> T1 once and write the CSVs the visualiser reads.
// Pure logic; no ns-3 simulation.
//
//   p1-plan-dump OUTDIR [gridSize] [cellRadius] [vehicles] [seed] [tiltDeg]

#include "../models/p1/p1-cells.h"
#include "../models/p1/p1-demand.h"
#include "../models/p1/p1-field.h"
#include "../models/p1/p1-params.h"
#include "../models/p1/p1-partition.h"
#include "../models/p1/p1-sensing.h"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <map>
#include <string>
#include <vector>

using namespace ns3::uavsar::p1;

int main(int argc, char* argv[]) {
    const std::string dir = argc > 1 ? argv[1] : "p1-out";
    const uint32_t grid = argc > 2 ? (uint32_t)std::atoi(argv[2]) : 40;
    const double rc = argc > 3 ? std::atof(argv[3]) : 84.0;
    const uint32_t M = argc > 4 ? (uint32_t)std::atoi(argv[4]) : 3;
    const uint32_t seed = argc > 5 ? (uint32_t)std::atoi(argv[5]) : 1;
    const double tiltDeg = argc > 6 ? std::atof(argv[6]) : 20.0;
    const double spacing = 20.0;
    std::filesystem::create_directories(dir);

    const double side = (grid - 1) * spacing;
    const double tilt = tiltDeg * M_PI / 180.0;
    const double W = side, H = side * 0.62;
    auto rot = [&](double u, double v, double& x, double& y) {
        x = u * std::cos(tilt) - v * std::sin(tilt);
        y = u * std::sin(tilt) + v * std::cos(tilt);
    };
    std::vector<Point> boundary;
    for (auto [u, v] : {std::pair<double, double>{0, 0}, {W, 0}, {W, H}, {0, H}}) {
        double x, y; rot(u, v, x, y);
        boundary.push_back({x, y});
    }
    Field field = BuildField(boundary, kBoundaryTolM);

    std::vector<std::pair<double, double>> xy;
    for (uint32_t i = 0; i < grid; i++)
        for (uint32_t j = 0; j < grid; j++) {
            double x, y;
            rot(j * spacing, i * spacing * (H / side), x, y);
            xy.push_back({x, y});
        }
    std::vector<Node> nodes = BuildNodes(xy, seed);
    const double rho = TurnRadiusM(kCruiseMps);
    CellPlan plan = BuildCells(nodes, field, rc, kGroundRangeM, rho);
    DoseModel dose;
    auto demands = BuildDemands(plan, nodes);
    for (auto& [cid, d] : demands) ServiceCost(d, dose, plan.cellPitchM, rho);
    auto work = BuildRows(plan, demands);
    const Depot depot{0.0, 0.0};

    std::map<uint32_t, const Node*> byId;
    for (const Node& n : nodes) byId[n.id] = &n;
    auto open = [&](const char* n) { return std::fopen((dir + "/" + n).c_str(), "w"); };

    FILE* f = open("config.csv");
    std::fprintf(f, "key,value\ngrid,%u\nspacing,%.1f\nside,%.1f\ntiltDeg,%.1f\n"
                    "cellRadius,%.2f\ncellPitch,%.2f\nrowPitch,%.2f\nmaxOffset,%.2f\n"
                    "psiDeg,%.3f\nminWidth,%.2f\narea,%.0f\nturnRadius,%.2f\n"
                    "cruise,%.1f\nvmin,%.1f\nvmax,%.1f\nvehicles,%u\nseed,%u\n"
                    "served,%u\nbarren,%u\ninfeasible,%u\nrows,%zu\n"
                    "Pe,%.4f\nJ,%u\nfanoFloor,%.4f\nfileCount,%u\nfileBytes,%u\n",
                 grid, spacing, side, tiltDeg, rc, plan.cellPitchM, plan.rowPitchM,
                 plan.maxOffsetM, field.psiRad * 180 / M_PI, field.minWidthM,
                 field.areaM2, rho, kCruiseMps, kMinMps, kMaxMps, M, seed,
                 plan.nServed, plan.nBarren, plan.nInfeasible, plan.cellsByRow.size(),
                 kTargetPe, kConfusers, FanoFloor(), kFileCount, kFileBytes);
    std::fclose(f);

    f = open("hull.csv");
    std::fprintf(f, "x,y\n");
    for (const Point& p : field.hull) std::fprintf(f, "%.2f,%.2f\n", p.x, p.y);
    std::fclose(f);

    // Row lines, as world-frame segments spanning the hull.
    f = open("rows.csv");
    std::fprintf(f, "row,w,x0,y0,x1,y1,lengthM,serviceS,heads\n");
    for (const auto& [row, w] : work) {
        double lo = 1e18, hi = -1e18;
        for (const Point& p : field.hull) {
            double u, ww;
            field.ToRowFrame(p.x, p.y, u, ww);
            lo = std::min(lo, u); hi = std::max(hi, u);
        }
        double x0, y0, x1, y1;
        field.FromRowFrame(lo, plan.RowLineW(row), x0, y0);
        field.FromRowFrame(hi, plan.RowLineW(row), x1, y1);
        std::fprintf(f, "%d,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%u\n", row,
                     plan.RowLineW(row), x0, y0, x1, y1, w.lengthM, w.serviceS, w.heads);
    }
    std::fclose(f);

    f = open("nodes.csv");
    std::fprintf(f, "id,x,y,camera,obs,cpu,offset,eligible,row,isHead\n");
    for (const auto& [cid, c] : plan.cells)
        for (const CellMember& m : c.members) {
            const Node& n = *byId[m.id];
            std::fprintf(f, "%u,%.2f,%.2f,%d,%.3f,%.3f,%.2f,%d,%d,%d\n", n.id, n.x, n.y,
                         n.HasCamera(), n.obs, n.cpu, m.offsetM, m.eligible, c.row,
                         c.hasHead && c.head == n.id);
        }
    std::fclose(f);

    f = open("cells.csv");
    std::fprintf(f, "id,row,cx,cy,class,head,headX,headY,headOffset,headSignedOffset,"
                    "headScoreS,cameras,eligible,files,theta,weaveS,doseS,orbits\n");
    for (const auto& [cid, c] : plan.cells) {
        const Demand& d = demands.at(cid);
        double hx = c.cx, hy = c.cy, sgn = 0;
        if (c.hasHead) {
            hx = byId[c.head]->x; hy = byId[c.head]->y;
            double u, w;
            field.ToRowFrame(hx, hy, u, w);
            sgn = w - plan.RowLineW(c.row);
        }
        std::fprintf(f, "%d,%d,%.2f,%.2f,%s,%u,%.2f,%.2f,%.2f,%.2f,%.3f,%u,%u,"
                        "%u,%.0f,%.3f,%.3f,%u\n",
                     cid, c.row, c.cx, c.cy, CellClassName(c.cls), c.head, hx, hy,
                     c.headOffsetM, sgn, c.headScoreS, c.cameras, c.eligible,
                     d.files, d.theta, d.weaveS, d.doseS, d.orbits);
    }
    std::fclose(f);

    f = open("partition.csv");
    std::fprintf(f, "method,M,vehicle,row\n");
    auto emit = [&](const char* nm, const Partition& p) {
        for (size_t v = 0; v < p.vehicles.size(); ++v)
            for (int32_t r : p.vehicles[v].rows)
                std::fprintf(f, "%s,%u,%zu,%d\n", nm, M, v, r);
    };
    emit("credit-free", PartitionCredit(work, plan, depot, M, rho, false));
    emit("credit-contig", PartitionCredit(work, plan, depot, M, rho, true));
    emit("split", PartitionSplit(work, plan, depot, M, rho));
    std::fclose(f);

    f = open("partsummary.csv");
    std::fprintf(f, "method,M,makespanS,imbalancePct,changeS,depotS\n");
    for (uint32_t m = 2; m <= 5; ++m) {
        struct { const char* n; Partition p; } arr[3] = {
            {"credit-free",   PartitionCredit(work, plan, depot, m, rho, false)},
            {"credit-contig", PartitionCredit(work, plan, depot, m, rho, true)},
            {"split",         PartitionSplit(work, plan, depot, m, rho)}};
        for (auto& e : arr) {
            double ch = 0, dp = 0;
            for (const Block& b : e.p.vehicles) { ch += b.changeS; dp += b.depotS; }
            std::fprintf(f, "%s,%u,%.2f,%.2f,%.2f,%.2f\n", e.n, m, e.p.makespanS,
                         e.p.imbalancePct, ch, dp);
        }
    }
    std::fclose(f);

    // Does the weave model's assumption hold? pi^2 d^2 / (4a) comes from a
    // sinusoid of WAVELENGTH 2a, which is one full period per TWO cells -- that
    // is, consecutive heads on OPPOSITE sides of the row line. Count how often
    // they actually are.
    uint32_t pairs = 0, alternating = 0;
    for (const auto& [row, cells] : plan.cellsByRow) {
        std::vector<std::pair<double, double>> seq;   // (u, signed offset)
        for (int32_t cid : cells) {
            const Cell& c = plan.cells.at(cid);
            if (!c.hasHead) continue;
            double u, w;
            field.ToRowFrame(byId[c.head]->x, byId[c.head]->y, u, w);
            seq.push_back({u, w - plan.RowLineW(row)});
        }
        std::sort(seq.begin(), seq.end());
        for (size_t i = 0; i + 1 < seq.size(); ++i) {
            pairs++;
            if (seq[i].second * seq[i + 1].second < 0) alternating++;
        }
    }
    f = open("weavecheck.csv");
    std::fprintf(f, "pairs,alternating\n%u,%u\n", pairs, alternating);
    std::fclose(f);

    std::printf("%s: %zu cells over %zu rows, served=%u barren=%u (F1 fail %u), "
                "%u vehicles; consecutive heads alternate sides %u/%u\n",
                dir.c_str(), plan.cells.size(), plan.cellsByRow.size(), plan.nServed,
                plan.nBarren, plan.nInfeasible, M, alternating, pairs);
    return 0;
}
