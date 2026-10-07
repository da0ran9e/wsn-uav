// Step 1: hex lattice from the origin -> random contiguous region -> random nodes.
//
// Writes, for the figures:
//   PREFIX-lattice.csv   every cell within 2 of the region: selected? growth order? hole?
//   PREFIX-growth.csv    the order cells were added, and the frontier at each step
//   PREFIX-nodes-sS.csv  one file per spacing S
// and checks the geometry, the region and the deployment before writing anything.
//
//   uav-coop-deploy --cells=60 --spacings=20,35,50 --seed=1 --out=deploy

#include "../models/common/coop-params.h"
#include "../models/common/coop-rng.h"
#include "../models/common/deploy.h"
#include "../models/common/hex-grid.h"
#include "../models/common/region.h"

#include "ns3/core-module.h"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <set>
#include <sstream>
#include <string>
#include <unordered_set>
#include <vector>

using namespace ns3;
using namespace ns3::uavcoop;

static uint32_t g_checks = 0;
#define CHECK(cond)                                                            \
    do {                                                                       \
        ++g_checks;                                                            \
        if (!(cond)) {                                                         \
            std::fprintf(stderr, "CHECK FAILED %s:%d: %s\n", __FILE__,         \
                         __LINE__, #cond);                                     \
            std::exit(1);                                                      \
        }                                                                      \
    } while (0)

namespace {

constexpr uint64_t kStreamRegion = 1, kStreamNodes = 2, kStreamTest = 3;

void CheckGeometry(const HexGrid& g) {
    for (int32_t q = -4; q <= 4; ++q)
        for (int32_t r = -4; r <= 4; ++r) {
            const Hex h{q, r};
            const Point c = g.Centre(h);
            CHECK(g.CellAt(c) == h);
            for (const Point& v : g.Corners(h))
                CHECK(std::fabs(std::hypot(v.x - c.x, v.y - c.y) - g.Radius()) < 1e-9);
            for (const Hex& n : HexGrid::Neighbours(h)) {
                const Point cn = g.Centre(n);
                CHECK(std::fabs(std::hypot(cn.x - c.x, cn.y - c.y) - g.Width()) < 1e-9);
                CHECK(HexGrid::Distance(h, n) == 1);
            }
        }
    // A hexagonal lattice's cells are its Voronoi cells: the cell holding a point
    // is the one with the nearest centre.
    CoopRng rng(12345, kStreamTest);
    const double span = 6 * g.Width();
    for (int i = 0; i < 200000; ++i) {
        const Point p{rng.Uniform(-span, span), rng.Uniform(-span, span)};
        const Hex h = g.CellAt(p);
        const Point c = g.Centre(h);
        const double d = std::hypot(p.x - c.x, p.y - c.y);
        for (const Hex& n : HexGrid::Neighbours(h)) {
            const Point cn = g.Centre(n);
            CHECK(d <= std::hypot(p.x - cn.x, p.y - cn.y) + 1e-9);
        }
    }
    // Area: hexagon / bounding box (width x 2R) = 3/4.
    int inside = 0, total = 400000;
    const Hex o{0, 0};
    for (int i = 0; i < total; ++i)
        inside += g.Contains(o, {rng.Uniform(-g.Width() / 2, g.Width() / 2),
                                 rng.Uniform(-g.Radius(), g.Radius())});
    CHECK(std::fabs((double)inside / total - 0.75) < 0.005);
}

void CheckRegion(const Region& reg, uint32_t n, const Hex& seed) {
    CHECK(reg.cells.size() == n);
    CHECK(reg.cells.front() == seed);
    std::set<Hex> seen;
    for (size_t i = 0; i < reg.cells.size(); ++i) {
        CHECK(seen.insert(reg.cells[i]).second);           // no cell twice
        if (i == 0) continue;
        bool touches = false;                              // grown from what was there
        for (size_t j = 0; j < i && !touches; ++j)
            touches = HexGrid::Distance(reg.cells[i], reg.cells[j]) == 1;
        CHECK(touches);
    }
    CHECK(IsConnected(reg.cells));
}

std::vector<double> NearestNeighbour(const std::vector<SensorNode>& v) {
    std::vector<double> nn(v.size(), 1e18);
    for (size_t i = 0; i < v.size(); ++i)
        for (size_t j = i + 1; j < v.size(); ++j) {
            const double d = std::hypot(v[i].pos.x - v[j].pos.x, v[i].pos.y - v[j].pos.y);
            nn[i] = std::min(nn[i], d);
            nn[j] = std::min(nn[j], d);
        }
    return nn;
}

}  // namespace

int main(int argc, char* argv[]) {
    double width = params::kCellWidthM;
    uint32_t cells = params::kRegionCells;
    std::string spacings = "20,35,50";
    uint32_t seed = 1;
    std::string out = "deploy";
    CommandLine cmd(__FILE__);
    cmd.AddValue("width", "cell width (flat to flat = centre spacing), m", width);
    cmd.AddValue("cells", "cells in the random region", cells);
    cmd.AddValue("spacings", "node spacing(s), m, comma-separated: one node per s^2", spacings);
    cmd.AddValue("seed", "random seed", seed);
    cmd.AddValue("out", "output prefix", out);
    cmd.Parse(argc, argv);
    CHECK(width > 0 && cells >= 1);

    // ---- step 1: the lattice ----------------------------------------------
    const HexGrid g(width);
    CheckGeometry(g);
    std::printf("lattice: pointy-top hexagons, width %.1f m (flat to flat = centre spacing), "
                "corner radius %.2f m, cell area %.1f m^2\n", g.Width(), g.Radius(), g.CellArea());

    // ---- step 2: a random contiguous region, grown from the origin's cell ---
    CoopRng rr(seed, kStreamRegion);
    const Hex origin{0, 0};
    const Region reg = GrowRegion(cells, origin, rr);
    CheckRegion(reg, cells, origin);
    const std::vector<Hex> holes = Holes(reg);
    double xmin = 1e18, xmax = -1e18, ymin = 1e18, ymax = -1e18;
    int32_t reach = 0;
    for (const Hex& h : reg.cells) {
        for (const Point& v : g.Corners(h)) {
            xmin = std::min(xmin, v.x); xmax = std::max(xmax, v.x);
            ymin = std::min(ymin, v.y); ymax = std::max(ymax, v.y);
        }
        reach = std::max(reach, HexGrid::Distance(origin, h));
    }
    const double area = cells * g.CellArea();
    std::printf("region: %u cells grown from (0,0), %.3f km^2, extent %.0f x %.0f m, "
                "farthest cell %d rings out, %zu enclosed hole(s)\n",
                cells, area / 1e6, xmax - xmin, ymax - ymin, reach, holes.size());

    // ---- outputs: lattice + growth ------------------------------------------
    std::unordered_set<Hex, HexHash> sel(reg.cells.begin(), reg.cells.end()),
        hole(holes.begin(), holes.end());
    std::vector<int> order;
    {
        FILE* f = std::fopen((out + "-lattice.csv").c_str(), "w");
        std::fprintf(f, "q,r,cx,cy,selected,order,hole\n");
        std::set<Hex> shown;
        for (const Hex& h : reg.cells)
            for (int32_t dq = -2; dq <= 2; ++dq)
                for (int32_t dr = -2; dr <= 2; ++dr) {
                    const Hex n{h.q + dq, h.r + dr};
                    if (HexGrid::Distance(h, n) <= 2) shown.insert(n);
                }
        for (const Hex& h : shown) {
            int ord = -1;
            for (size_t i = 0; i < reg.cells.size(); ++i)
                if (reg.cells[i] == h) ord = (int)i;
            const Point c = g.Centre(h);
            std::fprintf(f, "%d,%d,%.3f,%.3f,%d,%d,%d\n", h.q, h.r, c.x, c.y,
                         sel.count(h) ? 1 : 0, ord, hole.count(h) ? 1 : 0);
        }
        std::fclose(f);
        FILE* fg = std::fopen((out + "-growth.csv").c_str(), "w");
        std::fprintf(fg, "order,q,r,frontier\n");
        for (size_t i = 0; i < reg.cells.size(); ++i)
            std::fprintf(fg, "%zu,%d,%d,%u\n", i, reg.cells[i].q, reg.cells[i].r,
                         reg.frontierSize[i]);
        std::fclose(fg);
    }

    // ---- step 3: random nodes, one per spacing^2 ------------------------------
    std::stringstream ss(spacings);
    std::string tok;
    std::printf("\n%8s %7s %11s %13s %14s %16s %10s\n", "spacing", "nodes", "per cell",
                "per-cell sd", "chi2 / dof", "NN dist mean", "NN min");
    while (std::getline(ss, tok, ',')) {
        const double s = std::stod(tok);
        CHECK(s > 0);
        CoopRng rn(seed, kStreamNodes);   // same stream for every spacing: comparable
        const std::vector<SensorNode> nodes = DeployNodes(g, reg, s, rn);
        CHECK(nodes.size() == NodeCount(g, reg, s));
        std::vector<uint32_t> perCell(cells, 0);
        for (const SensorNode& nd : nodes) {
            CHECK(sel.count(nd.cell));                     // inside the region
            CHECK(g.CellAt(nd.pos) == nd.cell);            // inside its own hexagon
            for (size_t i = 0; i < reg.cells.size(); ++i)
                if (reg.cells[i] == nd.cell) perCell[i]++;
        }
        // Uniform over equal-area cells: counts ~ multinomial(n, 1/cells). chi^2 with
        // cells-1 dof must be within 5 standard deviations of its mean.
        const double mean = (double)nodes.size() / cells;
        double chi2 = 0, var = 0;
        for (uint32_t c : perCell) {
            chi2 += (c - mean) * (c - mean) / mean;
            var += (c - mean) * (c - mean);
        }
        const double dof = cells - 1.0;
        if (cells > 1) CHECK(std::fabs(chi2 - dof) < 5 * std::sqrt(2 * dof));
        const std::vector<double> nn = NearestNeighbour(nodes);
        double nnMean = 0, nnMin = 1e18;
        for (double d : nn) { nnMean += d; nnMin = std::min(nnMin, d); }
        nnMean /= nn.size();
        CHECK(nnMin > 0);
        std::printf("%6.0f m %7zu %11.2f %13.2f %8.1f / %3.0f %9.1f m (%.2f s) %7.2f m\n", s,
                    nodes.size(), mean, std::sqrt(var / cells), chi2, dof, nnMean, nnMean / s,
                    nnMin);
        FILE* f = std::fopen((out + "-nodes-s" + tok + ".csv").c_str(), "w");
        std::fprintf(f, "id,x,y,q,r,nnM\n");
        for (size_t i = 0; i < nodes.size(); ++i)
            std::fprintf(f, "%u,%.3f,%.3f,%d,%d,%.3f\n", nodes[i].id, nodes[i].pos.x,
                         nodes[i].pos.y, nodes[i].cell.q, nodes[i].cell.r, nn[i]);
        std::fclose(f);
    }
    std::printf("  NN mean for a uniform (Poisson) field of the same density is 0.50 s; edges "
                "push it up.\n");
    std::printf("\n%u CHECKS PASSED\n", g_checks);
    return 0;
}
