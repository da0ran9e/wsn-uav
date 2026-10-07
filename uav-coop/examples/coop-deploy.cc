// Step 1: hex lattice from the origin -> random contiguous region of a given
// convexity -> random nodes with three random capabilities -> CH and CLs.
//
// Writes, for the figures:
//   PREFIX-lattice.csv   cells near the region: selected? growth order? hole? envelope?
//   PREFIX-growth.csv    the order cells were added, and the frontier at each step
//   PREFIX-region.csv    the envelope ellipse and the measured convexity
//   PREFIX-nodes-sS.csv  one file per spacing S: position, capabilities, roles
// and checks the geometry, the region and the deployment before writing anything.
//
//   uav-coop-deploy --cells=60 --convexity=1 --spacings=20,35,50 --seed=1 --out=deploy

#include "../models/common/coop-params.h"
#include "../models/common/coop-rng.h"
#include "../models/common/deploy.h"
#include "../models/common/hex-grid.h"
#include "../models/common/region.h"

#include "ns3/core-module.h"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <map>
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

constexpr uint64_t kStreamRegion = 1, kStreamNodes = 2, kStreamTest = 3, kStreamCaps = 4;

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

void CheckRegion(const HexGrid& g, const Region& reg, uint32_t n, const Hex& seed,
                 double convexity) {
    CHECK(reg.cells.size() == n);
    CHECK(reg.cells.front() == seed);
    CHECK(IsConnected(reg.cells));
    std::set<Hex> seen;
    for (const Hex& h : reg.cells) CHECK(seen.insert(h).second);   // no cell twice
    if (convexity > 0) {
        // Inside its envelope, and the envelope is the size the convexity asks for.
        std::set<Hex> env(reg.envelope.begin(), reg.envelope.end());
        CHECK(env.size() == reg.envelope.size());
        CHECK(reg.envelope.size() == (size_t)std::lround(n / std::min(1.0, convexity)));
        CHECK(IsConnected(reg.envelope));
        CHECK(Convexity(g, reg.envelope) == 1.0);          // the envelope is convex
        for (const Hex& h : reg.cells) CHECK(env.count(h));
    }
    if (convexity >= 1.0) {
        CHECK(Convexity(g, reg.cells) == 1.0);             // fully convex region
        CHECK(Holes(reg).empty());
        return;                                            // listed by distance, not grown
    }
    for (size_t i = 1; i < reg.cells.size(); ++i) {
        bool touches = false;                              // grown from what was there
        for (size_t j = 0; j < i && !touches; ++j)
            touches = HexGrid::Distance(reg.cells[i], reg.cells[j]) == 1;
        CHECK(touches);
    }
}

void CheckRoles(const std::vector<SensorNode>& v, size_t ch) {
    size_t nCH = 0;
    std::map<Hex, std::vector<size_t>> byCell;
    for (size_t i = 0; i < v.size(); ++i) {
        CHECK(v[i].obs >= 0 && v[i].obs < 1 && v[i].cpu >= 0 && v[i].cpu < 1);
        CHECK(v[i].comm > 0 && v[i].comm <= 1);
        CHECK(v[i].Score() <= v[ch].Score());              // nobody beats the CH
        nCH += v[i].isCH;
        byCell[v[i].cell].push_back(i);
    }
    CHECK(nCH == 1 && v[ch].isCH && v[ch].isCL);           // the CH leads its own cell too
    for (const auto& [cell, idx] : byCell) {
        size_t nCL = 0, cl = 0;
        for (size_t i : idx) if (v[i].isCL) { nCL++; cl = i; }
        CHECK(nCL == 1);                                   // exactly one CL per occupied cell
        for (size_t i : idx) CHECK(v[i].Score() <= v[cl].Score());
    }
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
    double convexity = params::kConvexity;
    double maxAspect = params::kMaxAspect;
    std::string spacings = "20,35,50";
    uint32_t seed = 1;
    std::string out = "deploy";
    CommandLine cmd(__FILE__);
    cmd.AddValue("width", "cell width (flat to flat = centre spacing), m", width);
    cmd.AddValue("cells", "cells in the random region", cells);
    cmd.AddValue("convexity", "share of a random convex envelope the region fills: 1 convex, "
                 "0 free growth", convexity);
    cmd.AddValue("maxAspect", "envelope ellipse aspect ~ U[1, maxAspect]", maxAspect);
    cmd.AddValue("spacings", "node spacing(s), m, comma-separated: one node per s^2", spacings);
    cmd.AddValue("seed", "random seed", seed);
    cmd.AddValue("out", "output prefix", out);
    cmd.Parse(argc, argv);
    CHECK(width > 0 && cells >= 1 && convexity >= 0 && convexity <= 1 && maxAspect >= 1);

    // ---- step 1: the lattice ----------------------------------------------
    const HexGrid g(width);
    CheckGeometry(g);
    std::printf("lattice: pointy-top hexagons, width %.1f m (flat to flat = centre spacing), "
                "corner radius %.2f m, cell area %.1f m^2\n", g.Width(), g.Radius(), g.CellArea());

    // ---- step 2: a random contiguous region around the origin's cell ---------
    CoopRng rr(seed, kStreamRegion);
    const Hex origin{0, 0};
    const Region reg = MakeRegion(g, cells, convexity, maxAspect, rr);
    CheckRegion(g, reg, cells, origin, convexity);
    const double measured = Convexity(g, reg.cells);
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
    std::printf("region: %u cells around (0,0), %.3f km^2, extent %.0f x %.0f m, "
                "farthest cell %d rings out, %zu enclosed hole(s)\n",
                cells, area / 1e6, xmax - xmin, ymax - ymin, reach, holes.size());
    if (convexity > 0)
        std::printf("  convexity %.2f asked: envelope %zu cells (ellipse aspect %.2f, %.0f deg); "
                    "measured convexity %.3f\n", convexity, reg.envelope.size(), reg.aspect,
                    reg.thetaRad * 180 / M_PI, measured);
    else
        std::printf("  convexity 0: free growth, no envelope; measured convexity %.3f\n", measured);

    // ---- outputs: lattice + growth ------------------------------------------
    std::unordered_set<Hex, HexHash> sel(reg.cells.begin(), reg.cells.end()),
        hole(holes.begin(), holes.end()), env(reg.envelope.begin(), reg.envelope.end());
    std::vector<int> order;
    {
        FILE* f = std::fopen((out + "-lattice.csv").c_str(), "w");
        std::fprintf(f, "q,r,cx,cy,selected,order,hole,envelope\n");
        std::set<Hex> shown;
        std::vector<Hex> around(reg.cells);
        around.insert(around.end(), reg.envelope.begin(), reg.envelope.end());
        for (const Hex& h : around)
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
            std::fprintf(f, "%d,%d,%.3f,%.3f,%d,%d,%d,%d\n", h.q, h.r, c.x, c.y,
                         sel.count(h) ? 1 : 0, ord, hole.count(h) ? 1 : 0, env.count(h) ? 1 : 0);
        }
        std::fclose(f);
        FILE* fg = std::fopen((out + "-growth.csv").c_str(), "w");
        std::fprintf(fg, "order,q,r,frontier\n");
        for (size_t i = 0; i < reg.cells.size(); ++i)
            std::fprintf(fg, "%zu,%d,%d,%u\n", i, reg.cells[i].q, reg.cells[i].r,
                         reg.frontierSize[i]);
        std::fclose(fg);
        FILE* fm = std::fopen((out + "-region.csv").c_str(), "w");
        std::fprintf(fm, "convexityAsked,cells,envelopeCells,aspect,thetaDeg,convexityMeasured,holes\n");
        std::fprintf(fm, "%.4f,%u,%zu,%.4f,%.3f,%.4f,%zu\n", convexity, cells, reg.envelope.size(),
                     reg.aspect, reg.thetaRad * 180 / M_PI, measured, holes.size());
        std::fclose(fm);
    }

    // ---- step 3: random nodes, one per spacing^2 ------------------------------
    std::stringstream ss(spacings);
    std::string tok;
    struct Roles { double s; std::vector<SensorNode> nodes; size_t ch; };
    std::vector<Roles> roles;
    std::printf("\n%8s %7s %11s %13s %14s %16s %10s\n", "spacing", "nodes", "per cell",
                "per-cell sd", "chi2 / dof", "NN dist mean", "NN min");
    while (std::getline(ss, tok, ',')) {
        const double s = std::stod(tok);
        CHECK(s > 0);
        CoopRng rn(seed, kStreamNodes);   // same stream for every spacing: comparable
        std::vector<SensorNode> nodes = DeployNodes(g, reg, s, rn);
        CoopRng rc(seed, kStreamCaps);    // own stream: positions do not depend on it
        AssignCapabilities(nodes, rc);
        const size_t ch = AssignRoles(nodes);
        CheckRoles(nodes, ch);
        roles.push_back({s, nodes, ch});
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
        std::fprintf(f, "id,x,y,q,r,nnM,obs,cpu,comm,score,isCH,isCL\n");
        for (size_t i = 0; i < nodes.size(); ++i)
            std::fprintf(f, "%u,%.3f,%.3f,%d,%d,%.3f,%.6f,%.6f,%.6f,%.6f,%d,%d\n", nodes[i].id,
                         nodes[i].pos.x, nodes[i].pos.y, nodes[i].cell.q, nodes[i].cell.r, nn[i],
                         nodes[i].obs, nodes[i].cpu, nodes[i].comm, nodes[i].Score(),
                         nodes[i].isCH ? 1 : 0, nodes[i].isCL ? 1 : 0);
        std::fclose(f);
    }
    std::printf("  NN mean for a uniform (Poisson) field of the same density is 0.50 s; edges "
                "push it up.\n");

    // ---- step 4: capabilities and roles -------------------------------------
    std::printf("\ncapabilities: obs ~ U[0,1), cpu ~ U[0,1), comm ~ U(0,1]; strength = obs x cpu x comm\n");
    std::printf("%8s | %-44s | %9s %13s %12s\n", "spacing", "CH: id, cell, obs / cpu / comm = strength",
                "CLs", "empty cells", "CL strength");
    for (const Roles& R : roles) {
        const SensorNode& c = R.nodes[R.ch];
        std::set<Hex> occupied;
        double clSum = 0;
        uint32_t nCL = 0;
        bool topAll = true;
        for (const SensorNode& nd : R.nodes) {
            occupied.insert(nd.cell);
            if (nd.isCL) { clSum += nd.Score(); nCL++; }
            topAll = topAll && nd.obs <= c.obs && nd.cpu <= c.cpu && nd.comm <= c.comm;
        }
        CHECK(nCL == occupied.size());
        char chs[96];
        std::snprintf(chs, sizeof chs, "#%u (%d,%d)  %.2f / %.2f / %.2f = %.3f", c.id, c.cell.q,
                      c.cell.r, c.obs, c.cpu, c.comm, c.Score());
        std::printf("%6.0f m | %-44s | %9u %13zu %12.3f\n", R.s, chs, nCL,
                    (size_t)cells - occupied.size(), clSum / nCL);
        std::printf("         |   the CH is %s the best in all three at once\n", topAll ? "ALSO" : "NOT");
    }
    std::printf("\n%u CHECKS PASSED\n", g_checks);
    return 0;
}
