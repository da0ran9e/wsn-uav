// Steps 1-2: hex lattice (corner radius R) -> random contiguous region, concavities
// filled up to a target convexity -> random nodes with three capabilities -> CH and
// CLs -> a Dubins flight path through the strongest nodes.
//
// Writes, for the figures:
//   PREFIX-lattice.csv    cells near the region: selected? grown or filled? order? hole?
//   PREFIX-growth.csv     the order cells grew in, and the frontier at each step
//   PREFIX-region.csv     convexity before and after filling
//   PREFIX-nodes-sS.csv   per spacing S: position, capabilities, roles
//   PREFIX-tour-sS.csv    per spacing: the flight path, sampled every 2 m
//   PREFIX-tourwp-sS.csv  per spacing: the points it flies through, and its legs
// and checks the geometry, the region, the deployment and the path before writing.
//
//   uav-coop-deploy --radius=100 --cells=60 --convexity=1 --spacings=20,35,50 --rho=255 --out=deploy

#include "../models/common/coop-params.h"
#include "../models/common/coop-rng.h"
#include "../models/common/deploy.h"
#include "../models/common/hex-grid.h"
#include "../models/common/region.h"
#include "../models/common/tour.h"

#include "ns3/core-module.h"

#include <algorithm>
#include <array>
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

void CheckRegion(const HexGrid& g, const Region& reg, uint32_t n, const Hex& seed, double kappa) {
    CHECK(reg.nGrown == n && reg.cells.size() >= n);
    CHECK(reg.cells.front() == seed);
    CHECK(IsConnected(reg.cells));
    std::set<Hex> seen;
    for (const Hex& h : reg.cells) CHECK(seen.insert(h).second);   // no cell twice
    // The grown part: each cell next to an earlier one.
    for (size_t i = 1; i < n; ++i) {
        bool touches = false;
        for (size_t j = 0; j < i && !touches; ++j)
            touches = HexGrid::Distance(reg.cells[i], reg.cells[j]) == 1;
        CHECK(touches);
    }
    // The filled part: only concavities of the grown region, and no further than asked.
    const std::vector<Hex> grown(reg.cells.begin(), reg.cells.begin() + n);
    const std::vector<Hex> hull = HullCells(g, grown);
    const std::set<Hex> hs(hull.begin(), hull.end());
    for (const Hex& h : reg.cells) CHECK(hs.count(h));
    CHECK(std::fabs(reg.rawConvexity - Convexity(g, grown)) < 1e-12);
    CHECK(std::fabs(reg.convexity - Convexity(g, reg.cells)) < 1e-12);   // the hull did not move
    if (kappa <= reg.rawConvexity) CHECK(reg.cells.size() == n);         // nothing to do
    else CHECK(reg.convexity >= kappa - 1e-12 &&
               reg.cells.size() == (size_t)std::ceil(kappa * hull.size() - 1e-9));
    if (kappa >= 1.0) {
        CHECK(reg.convexity == 1.0);
        CHECK(Holes(reg).empty());
    }
}

// Every one of the six words, not just the shortest, must land on the goal pose.
void CheckDubins() {
    CoopRng rng(777, 99);
    for (int i = 0; i < 20000; ++i) {
        const double rho = rng.Uniform(20, 400);
        const Pose a{rng.Uniform(-2000, 2000), rng.Uniform(-2000, 2000), rng.Uniform(0, 2 * M_PI)};
        const Pose b{rng.Uniform(-2000, 2000), rng.Uniform(-2000, 2000), rng.Uniform(0, 2 * M_PI)};
        std::array<DubinsPath, 6> all;
        const DubinsPath best = DubinsShortest(a, b, rho, &all);
        CHECK(best.Valid());
        CHECK(best.Length() >= std::hypot(b.x - a.x, b.y - a.y) - 1e-6);
        for (const DubinsPath& p : all) {
            if (!p.Valid()) continue;
            const Pose e = DubinsAt(a, p, p.Length());
            CHECK(std::hypot(e.x - b.x, e.y - b.y) < 1e-6 * rho);
            CHECK(std::fabs(std::remainder(e.th - b.th, 2 * M_PI)) < 1e-9);
            CHECK(best.Length() <= p.Length() + 1e-12);
        }
    }
    // Straight ahead is a straight line.
    const DubinsPath s = DubinsShortest({0, 0, 0}, {1000, 0, 0}, 100);
    CHECK(std::fabs(s.Length() - 1000) < 1e-9);
}

void CheckTour(const Tour& t, const std::vector<Point>& pts, double rho, bool closed) {
    const size_t n = pts.size();
    CHECK(t.poses.size() == n && t.legs.size() == (closed ? n : n - 1));
    double sum = 0, poly = 0;
    for (size_t i = 0; i < t.legs.size(); ++i) {
        const Pose& a = t.poses[i];
        const Pose& b = t.poses[(i + 1) % n];
        const Pose e = DubinsAt(a, t.legs[i], t.legs[i].Length());   // the leg lands on the next pose
        CHECK(std::hypot(e.x - b.x, e.y - b.y) < 1e-6 * rho);
        CHECK(std::fabs(std::remainder(e.th - b.th, 2 * M_PI)) < 1e-9);
        // Flown at the turn radius: consecutive 1 m samples are 1 m apart and turn by
        // at most 1/rho.
        const std::vector<Pose> sm = DubinsSample(a, t.legs[i], 1.0);
        for (size_t k = 1; k < sm.size(); ++k) {
            const double ds = std::hypot(sm[k].x - sm[k - 1].x, sm[k].y - sm[k - 1].y);
            const double step = t.legs[i].Length() / (sm.size() - 1);
            CHECK(ds <= step + 1e-6);
            CHECK(std::fabs(std::remainder(sm[k].th - sm[k - 1].th, 2 * M_PI)) <= step / rho + 1e-9);
        }
        sum += t.legs[i].Length();
        poly += std::hypot(b.x - a.x, b.y - a.y);
    }
    CHECK(std::fabs(sum - t.length) < 1e-6);
    CHECK(t.length >= poly - 1e-6);                 // never shorter than straight lines
    CHECK(t.length <= t.gridLength + 1e-9);         // refinement only improves
    for (size_t i = 0; i < n; ++i)                  // passes through every point
        CHECK(std::hypot(t.poses[i].x - pts[t.order[i]].x, t.poses[i].y - pts[t.order[i]].y) < 1e-9);
    // No random choice of headings, in any order, beats it.
    CoopRng rng(4242, 98);
    std::vector<int> ord(n);
    for (size_t i = 0; i < n; ++i) ord[i] = (int)i;
    do {
        for (int k = 0; k < 400; ++k) {
            std::vector<Pose> ps;
            for (int i : ord) ps.push_back({pts[i].x, pts[i].y, rng.Uniform(0, 2 * M_PI)});
            double c = 0;
            for (size_t i = 0; i + 1 < n; ++i) c += DubinsShortest(ps[i], ps[i + 1], rho).Length();
            if (closed) c += DubinsShortest(ps[n - 1], ps[0], rho).Length();
            CHECK(c >= t.length - 1e-6);
        }
    } while (std::next_permutation(ord.begin(), ord.end()));
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
    double radius = params::kCellRadiusM;
    uint32_t cells = params::kRegionCells;
    double convexity = params::kConvexity;
    double rho = params::kMinTurnRadiusM;
    bool open = false;
    std::string spacings = "20,35,50";
    uint32_t seed = 1;
    std::string out = "deploy";
    CommandLine cmd(__FILE__);
    cmd.AddValue("radius", "cell corner radius R, m", radius);
    cmd.AddValue("cells", "cells in the random region", cells);
    cmd.AddValue("convexity", "target convexity: fill concavities until reached; 1 = convex",
                 convexity);
    cmd.AddValue("rho", "minimum turn radius of the flight path, m", rho);
    cmd.AddValue("open", "open path instead of a closed loop", open);
    cmd.AddValue("spacings", "node spacing(s), m, comma-separated: one node per s^2", spacings);
    cmd.AddValue("seed", "random seed", seed);
    cmd.AddValue("out", "output prefix", out);
    cmd.Parse(argc, argv);
    CHECK(radius > 0 && cells >= 1 && convexity >= 0 && convexity <= 1 && rho > 0);

    // ---- step 1: the lattice ----------------------------------------------
    const HexGrid g = HexGrid::FromRadius(radius);
    CHECK(std::fabs(g.Radius() - radius) < 1e-9);
    CheckGeometry(g);
    CheckDubins();
    std::printf("lattice: pointy-top hexagons, corner radius R %.1f m, flat-to-flat width %.1f m "
                "(= centre spacing), cell area %.0f m^2\n", g.Radius(), g.Width(), g.CellArea());

    // ---- step 2: a random contiguous region around the origin's cell ---------
    CoopRng rr(seed, kStreamRegion);
    const Hex origin{0, 0};
    const Region reg = MakeRegion(g, cells, convexity, rr);
    CheckRegion(g, reg, cells, origin, convexity);
    Region grownOnly = reg;
    grownOnly.cells.resize(reg.nGrown);
    const size_t holesRaw = Holes(grownOnly).size();
    const uint32_t nFinal = (uint32_t)reg.cells.size();
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
    const double area = nFinal * g.CellArea();
    std::printf("region: %u cells grown at random from (0,0): convexity %.3f, %zu hole(s)\n",
                cells, reg.rawConvexity, holesRaw);
    std::printf("  target convexity %.2f: %u concave cells filled -> %u cells, convexity %.3f, "
                "%zu hole(s)\n", convexity, nFinal - cells, nFinal, reg.convexity, holes.size());
    std::printf("  %.3f km^2, extent %.0f x %.0f m, farthest cell %d rings out\n", area / 1e6,
                xmax - xmin, ymax - ymin, reach);

    // ---- outputs: lattice + growth ------------------------------------------
    std::unordered_set<Hex, HexHash> sel(reg.cells.begin(), reg.cells.end()),
        hole(holes.begin(), holes.end());
    std::vector<int> order;
    {
        FILE* f = std::fopen((out + "-lattice.csv").c_str(), "w");
        std::fprintf(f, "q,r,cx,cy,selected,order,hole,filled\n");
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
            std::fprintf(f, "%d,%d,%.3f,%.3f,%d,%d,%d,%d\n", h.q, h.r, c.x, c.y,
                         sel.count(h) ? 1 : 0, ord, hole.count(h) ? 1 : 0,
                         ord >= (int)reg.nGrown ? 1 : 0);
        }
        std::fclose(f);
        FILE* fg = std::fopen((out + "-growth.csv").c_str(), "w");
        std::fprintf(fg, "order,q,r,frontier\n");
        for (size_t i = 0; i < reg.nGrown; ++i)
            std::fprintf(fg, "%zu,%d,%d,%u\n", i, reg.cells[i].q, reg.cells[i].r,
                         reg.frontierSize[i]);
        std::fclose(fg);
        FILE* fm = std::fopen((out + "-region.csv").c_str(), "w");
        std::fprintf(fm, "convexityAsked,cellsGrown,cells,rawConvexity,convexityMeasured,holesRaw,holes,radius\n");
        std::fprintf(fm, "%.4f,%u,%u,%.4f,%.4f,%zu,%zu,%.3f\n", convexity, cells, nFinal,
                     reg.rawConvexity, reg.convexity, holesRaw, holes.size(), g.Radius());
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
        std::vector<uint32_t> perCell(nFinal, 0);
        for (const SensorNode& nd : nodes) {
            CHECK(sel.count(nd.cell));                     // inside the region
            CHECK(g.CellAt(nd.pos) == nd.cell);            // inside its own hexagon
            for (size_t i = 0; i < reg.cells.size(); ++i)
                if (reg.cells[i] == nd.cell) perCell[i]++;
        }
        // Uniform over equal-area cells: counts ~ multinomial(n, 1/cells). chi^2 with
        // cells-1 dof must be within 5 standard deviations of its mean.
        const double mean = (double)nodes.size() / nFinal;
        double chi2 = 0, var = 0;
        for (uint32_t c : perCell) {
            chi2 += (c - mean) * (c - mean) / mean;
            var += (c - mean) * (c - mean);
        }
        const double dof = nFinal - 1.0;
        if (nFinal > 1) CHECK(std::fabs(chi2 - dof) < 5 * std::sqrt(2 * dof));
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
                    (size_t)nFinal - occupied.size(), clSum / nCL);
        std::printf("         |   the CH is %s the best in all three at once\n", topAll ? "ALSO" : "NOT");
    }

    // ---- step 5: a Dubins flight path through the strongest nodes -------------
    std::printf("\nflight path through the %u strongest nodes (CH first): %s Dubins, min turn "
                "radius %.1f m\n", params::kTourNodes, open ? "open" : "closed", rho);
    for (const Roles& R : roles) {
        std::vector<size_t> idx(R.nodes.size());
        for (size_t i = 0; i < idx.size(); ++i) idx[i] = i;
        std::sort(idx.begin(), idx.end(), [&](size_t a, size_t b) {
            const double sa = R.nodes[a].Score(), sb = R.nodes[b].Score();
            return sa != sb ? sa > sb : R.nodes[a].id < R.nodes[b].id;
        });
        idx.resize(std::min<size_t>(params::kTourNodes, idx.size()));
        CHECK(idx.front() == R.ch);                       // the CH is among them, first
        std::vector<Point> pts;
        for (size_t i : idx) pts.push_back(R.nodes[i].pos);
        const Tour t = PlanTour(pts, rho, !open);
        CheckTour(t, pts, rho, !open);
        double poly = 0;
        for (size_t i = 0; i < t.legs.size(); ++i)
            poly += std::hypot(t.poses[(i + 1) % pts.size()].x - t.poses[i].x,
                               t.poses[(i + 1) % pts.size()].y - t.poses[i].y);
        std::printf("  %4.0f m: nodes", R.s);
        for (size_t i : idx) std::printf(" #%u", R.nodes[i].id);
        std::printf("  | fly order");
        for (int o : t.order) std::printf(" #%u", R.nodes[idx[o]].id);
        std::printf("  | %.0f m (straight lines %.0f m, +%.0f%%) = %.1f s at %.0f m/s\n", t.length,
                    poly, 100 * (t.length / poly - 1), t.length / params::kUavSpeedMps,
                    params::kUavSpeedMps);
        for (size_t i = 0; i < t.legs.size(); ++i)
            std::printf("         leg %zu: %s %.0f m (%.0f / %.0f / %.0f)\n", i + 1,
                        t.legs[i].Word().c_str(), t.legs[i].Length(), t.legs[i].seg[0] * rho,
                        t.legs[i].seg[1] * rho, t.legs[i].seg[2] * rho);
        char sfx[32];
        std::snprintf(sfx, sizeof sfx, "-s%.0f.csv", R.s);
        FILE* fp = std::fopen((out + "-tour" + sfx).c_str(), "w");
        std::fprintf(fp, "leg,seg,x,y,thDeg\n");
        for (size_t i = 0; i < t.legs.size(); ++i) {
            std::vector<int> sg;
            const std::vector<Pose> sm = DubinsSample(t.poses[i], t.legs[i], 2.0, &sg);
            for (size_t k = 0; k < sm.size(); ++k)
                std::fprintf(fp, "%zu,%d,%.3f,%.3f,%.4f\n", i, sg[k], sm[k].x, sm[k].y,
                             sm[k].th * 180 / M_PI);
        }
        std::fclose(fp);
        FILE* fw = std::fopen((out + "-tourwp" + sfx).c_str(), "w");
        std::fprintf(fw, "flyOrder,rank,id,x,y,score,thDeg,legWord,legM,closed,rho,lengthM\n");
        for (size_t i = 0; i < t.poses.size(); ++i) {
            const size_t rank = (size_t)t.order[i];
            const bool hasLeg = i < t.legs.size();
            std::fprintf(fw, "%zu,%zu,%u,%.3f,%.3f,%.6f,%.4f,%s,%.3f,%d,%.3f,%.3f\n", i, rank + 1,
                         R.nodes[idx[rank]].id, t.poses[i].x, t.poses[i].y,
                         R.nodes[idx[rank]].Score(), t.poses[i].th * 180 / M_PI,
                         hasLeg ? t.legs[i].Word().c_str() : "-", hasLeg ? t.legs[i].Length() : 0.0,
                         open ? 0 : 1, rho, t.length);
        }
        std::fclose(fw);
    }
    std::printf("\n%u CHECKS PASSED\n", g_checks);
    return 0;
}
