// Steps 1-2: hex lattice (corner radius R) -> random contiguous region, concavities
// filled up to a target convexity -> random nodes with three capabilities -> CH and
// CLs -> a Dubins flight path crossing the cluster: in at a random boundary point,
// over the CH, out at another random boundary point -> pre-built routes over the
// cells (PECEE elastic clustering): to the CL, to each adjacent cell, main to the CH.
//
// Writes, for the figures:
//   PREFIX-lattice.csv    cells near the region: selected? grown or filled? order? hole?
//   PREFIX-growth.csv     the order cells grew in, and the frontier at each step
//   PREFIX-region.csv     convexity before and after filling
//   PREFIX-nodes-sS.csv   per spacing S: position, capabilities, roles
//   PREFIX-path-sS.csv    per spacing: the flight path, sampled every 2 m
//   PREFIX-pathwp-sS.csv  per spacing: entry, CH, exit, and the legs between
//   PREFIX-routes-sS.csv  per spacing: each node's route table (to its CL, to each
//                         adjacent cell, main route to the CH)
// and checks the geometry, the region, the deployment and the path before writing.
//
//   uav-coop-deploy --radius=100 --cells=60 --convexity=1 --spacings=20,35,50 --rho=255 --pick=0 --out=deploy

#include "../models/common/coop-params.h"
#include "../models/common/coop-rng.h"
#include "../models/common/deploy.h"
#include "../models/common/hex-grid.h"
#include "../models/common/region.h"
#include "../models/common/path.h"
#include "../models/common/routing.h"

#include "ns3/core-module.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <deque>
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
// entry/exit points: stream kStreamCross + pick, so --pick redraws them alone
constexpr uint64_t kStreamCross = 16;

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

// The straight line flown before the entry (sign -1) or after the exit (+1), lead m
// long, stays outside the cluster.
bool LeadOutside(const HexGrid& g, const std::unordered_set<Hex, HexHash>& inside, const Point& p,
                 double th, double sign, double lead) {
    for (double t = 1; t <= lead; t += 2)
        if (inside.count(g.CellAt({p.x + sign * t * std::cos(th), p.y + sign * t * std::sin(th)})))
            return false;
    return true;
}

void CheckPath(const HexGrid& g, const std::unordered_set<Hex, HexHash>& inside, const Path& t,
               const std::vector<Point>& pts, const std::vector<HeadingOk>& ok, const Edge& in,
               const Edge& outE, double rho, double lead) {
    const size_t n = pts.size();
    CHECK(t.poses.size() == n && t.legs.size() == n - 1);
    double sum = 0, poly = 0;
    for (size_t i = 0; i < n; ++i) {
        CHECK(std::hypot(t.poses[i].x - pts[i].x, t.poses[i].y - pts[i].y) < 1e-9);   // through the points, in order
        CHECK(ok[i] == nullptr || ok[i](t.poses[i].th));                          // headings allowed
    }
    for (size_t i = 0; i + 1 < n; ++i) {
        const Pose& a = t.poses[i];
        const Pose& b = t.poses[i + 1];
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
    // Entry and exit lie on the cluster's edge: just inside is in, just outside is out.
    for (const auto& [E, P] : {std::pair<const Edge&, const Point&>{in, pts.front()}, {outE, pts.back()}}) {
        const double ex = E.b.x - E.a.x, ey = E.b.y - E.a.y;
        CHECK(std::fabs(ex * (P.y - E.a.y) - ey * (P.x - E.a.x)) < 1e-6 * g.Radius());
        CHECK(inside.count(g.CellAt({P.x + 1e-3 * E.in.x, P.y + 1e-3 * E.in.y})) == 1);
        CHECK(inside.count(g.CellAt({P.x - 1e-3 * E.in.x, P.y - 1e-3 * E.in.y})) == 0);
    }
    // Comes from outside and leaves to the outside along straight lines.
    CHECK(LeadOutside(g, inside, pts.front(), t.poses.front().th, -1, lead));
    CHECK(LeadOutside(g, inside, pts.back(), t.poses.back().th, +1, lead));
    // No random choice of allowed headings beats it.
    CoopRng rng(4242, 98);
    for (int k = 0, tried = 0; k < 2000 && tried < 200000; ++tried) {
        std::vector<Pose> ps;
        bool good = true;
        for (size_t i = 0; i < n; ++i) {
            ps.push_back({pts[i].x, pts[i].y, rng.Uniform(0, 2 * M_PI)});
            good = good && (ok[i] == nullptr || ok[i](ps.back().th));
        }
        if (!good) continue;
        ++k;
        double c = 0;
        for (size_t i = 0; i + 1 < n; ++i) c += DubinsShortest(ps[i], ps[i + 1], rho).Length();
        CHECK(c >= t.length - 1e-6);
    }
}

// Hops from every node to the nearest of `to`, over links between nodes in `in`.
std::vector<uint32_t> Bfs(const Routing& R, const std::vector<int32_t>& to, const std::vector<char>& in) {
    std::vector<uint32_t> h(R.links.size(), kNoRoute);
    std::deque<int32_t> q;
    for (int32_t t : to) { h[t] = 0; q.push_back(t); }
    while (!q.empty()) {
        const int32_t u = q.front();
        q.pop_front();
        for (int32_t v : R.links[u])
            if (in[v] && h[v] == kNoRoute) { h[v] = h[u] + 1; q.push_back(v); }
    }
    return h;
}

void CheckRouting(const std::vector<SensorNode>& v, size_t ch, const Routing& R, double range) {
    const size_t n = v.size();
    // Links: exactly the pairs within range, both ways.
    size_t nl = 0;
    for (size_t i = 0; i < n; ++i)
        for (size_t j = i + 1; j < n; ++j) {
            const bool near = std::hypot(v[i].pos.x - v[j].pos.x, v[i].pos.y - v[j].pos.y) <= range;
            const bool ij = std::binary_search(R.links[i].begin(), R.links[i].end(), (int32_t)j);
            const bool ji = std::binary_search(R.links[j].begin(), R.links[j].end(), (int32_t)i);
            CHECK(near == ij && ij == ji);
            nl += near;
        }
    size_t deg = 0;
    for (const auto& l : R.links) deg += l.size();
    CHECK(deg == 2 * nl);
    auto linked = [&](int32_t a, int32_t b) {
        return std::binary_search(R.links[a].begin(), R.links[a].end(), b);
    };
    std::map<Hex, std::vector<int32_t>> members;
    for (size_t i = 0; i < n; ++i) members[v[i].cell].push_back((int32_t)i);
    for (const auto& [A, mem] : members) {
        std::vector<char> inA(n, 0);
        for (int32_t i : mem) inA[i] = 1;
        int32_t cl = -1;
        for (int32_t i : mem) if (v[i].isCL) cl = i;
        CHECK(cl >= 0);
        // toCL: in-cell hops, walked hop by hop.
        const std::vector<uint32_t> hc = Bfs(R, {cl}, inA);
        for (int32_t i : mem) {
            const CellHop& t = R.table[i].toCL;
            CHECK(t.hops == hc[i]);
            if (t.hops == kNoRoute) { CHECK(t.next == kNoHop); continue; }
            int32_t cur = i;
            for (uint32_t k = 0; k < t.hops; ++k) {
                const int32_t nx = R.table[cur].toCL.next;
                CHECK(linked(cur, nx) && inA[nx]);
                CHECK(R.table[nx].toCL.hops == R.table[cur].toCL.hops - 1);
                cur = nx;
            }
            CHECK(cur == cl && t.entry == cl);
        }
        // toCell[B]: hops within A and B, walked: stays in A, the last hop lands in B.
        for (const Hex& B : HexGrid::Neighbours(A)) {
            auto it = members.find(B);
            if (it == members.end()) {
                for (int32_t i : mem) CHECK(R.table[i].toCell.count(B) == 0);
                continue;
            }
            std::vector<char> inAB = inA;
            for (int32_t j : it->second) inAB[j] = 1;
            const std::vector<uint32_t> hb = Bfs(R, it->second, inAB);
            for (int32_t i : mem) {
                const CellHop& t = R.table[i].toCell.at(B);
                CHECK(t.hops == hb[i]);
                if (t.hops == kNoRoute) continue;
                int32_t cur = i;
                for (uint32_t k = 0; k < t.hops; ++k) {
                    const int32_t nx = R.table[cur].toCell.at(B).next;
                    CHECK(linked(cur, nx));
                    CHECK(k + 1 < t.hops ? v[nx].cell == A : v[nx].cell == B);
                    cur = nx;
                    if (k + 1 < t.hops) CHECK(R.table[cur].toCell.at(B).hops == t.hops - k - 1);
                }
                CHECK(cur == t.entry);
            }
        }
    }
    // Main route: walked from every node, every hop lowers the remaining count by one
    // and is a link inside the cell or into an adjacent cell; ends at the CH.
    const std::vector<uint32_t> fh = FreeHops(R, ch);
    for (size_t i = 0; i < n; ++i) {
        const RouteTable& t = R.table[i];
        if (t.hopsToCH == kNoRoute) { CHECK(t.mainNext == kNoHop); continue; }
        CHECK(t.hopsToCH >= fh[i]);                   // never shorter than ignoring cells
        int32_t cur = (int32_t)i;
        for (uint32_t k = 0; k < t.hopsToCH; ++k) {
            const int32_t nx = R.table[cur].mainNext;
            CHECK(linked(cur, nx));
            CHECK(v[nx].cell == v[cur].cell || HexGrid::Distance(v[nx].cell, v[cur].cell) == 1);
            CHECK(R.table[nx].hopsToCH == R.table[cur].hopsToCH - 1);
            cur = nx;
        }
        CHECK(cur == (int32_t)ch);
        // and it is the best of its own stored next hops (Bellman equation)
        if (i == ch) continue;
        uint32_t best = kNoRoute;
        auto opt = [&](const CellHop& h) {
            if (h.next != kNoHop && R.table[h.next].hopsToCH != kNoRoute)
                best = std::min(best, R.table[h.next].hopsToCH + 1);
        };
        opt(t.toCL);
        for (const auto& [B, h] : t.toCell) opt(h);
        CHECK(t.hopsToCH == best);
        CHECK(t.mainNext == (t.mainViaCL ? t.toCL.next : t.toCell.at(t.mainCell).next));
    }
}

void CheckRoles(const std::vector<SensorNode>& v, size_t ch, const std::vector<double>& ed,
                double margin) {
    size_t nCH = 0;
    std::map<Hex, std::vector<size_t>> byCell;
    CHECK(ch < v.size() && ed[ch] >= margin);              // the CH is far enough in
    for (size_t i = 0; i < v.size(); ++i) {
        CHECK(v[i].obs >= 0 && v[i].obs < 1 && v[i].cpu >= 0 && v[i].cpu < 1);
        CHECK(v[i].comm > 0 && v[i].comm <= 1);
        if (ed[i] >= margin) CHECK(v[i].Score() <= v[ch].Score());   // no eligible node beats it
        nCH += v[i].isCH;
        byCell[v[i].cell].push_back(i);
    }
    CHECK(nCH == 1 && v[ch].isCH && v[ch].isCL);           // the CH leads its own cell too
    for (const auto& [cell, idx] : byCell) {
        size_t nCL = 0, cl = 0;
        for (size_t i : idx) if (v[i].isCL) { nCL++; cl = i; }
        CHECK(nCL == 1);                                   // exactly one CL per occupied cell
        if (cell == v[ch].cell) continue;                  // the CH's cell: the CH, see above
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
    uint32_t pick = 0;
    double chMargin = params::kChMarginM;
    double linkRange = params::kLinkRangeM;
    std::string spacings = "20,35,50";
    uint32_t seed = 1;
    std::string out = "deploy";
    CommandLine cmd(__FILE__);
    cmd.AddValue("radius", "cell corner radius R, m", radius);
    cmd.AddValue("cells", "cells in the random region", cells);
    cmd.AddValue("convexity", "target convexity: fill concavities until reached; 1 = convex",
                 convexity);
    cmd.AddValue("rho", "minimum turn radius of the flight path, m", rho);
    cmd.AddValue("chMargin", "the CH is at least this far from the cluster's edge, m", chMargin);
    cmd.AddValue("linkRange", "G2G link: nodes at most this far apart, m", linkRange);
    cmd.AddValue("pick", "which random entry/exit pair (same region and nodes)", pick);
    cmd.AddValue("spacings", "node spacing(s), m, comma-separated: one node per s^2", spacings);
    cmd.AddValue("seed", "random seed", seed);
    cmd.AddValue("out", "output prefix", out);
    cmd.Parse(argc, argv);
    CHECK(radius > 0 && cells >= 1 && convexity >= 0 && convexity <= 1 && rho > 0 && chMargin >= 0);

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

    // The cluster's outer edge: for the CH margin and for the entry/exit points.
    const std::vector<Edge> edges = OuterEdges(g, reg);
    CHECK(!edges.empty());
    double perim = 0;
    for (const Edge& e : edges) {
        perim += std::hypot(e.b.x - e.a.x, e.b.y - e.a.y);
        // the normal points into the cluster: just inside is in, just outside is out
        const Point m{(e.a.x + e.b.x) / 2, (e.a.y + e.b.y) / 2};
        CHECK(sel.count(g.CellAt({m.x + 1e-3 * e.in.x, m.y + 1e-3 * e.in.y})) == 1);
        CHECK(sel.count(g.CellAt({m.x - 1e-3 * e.in.x, m.y - 1e-3 * e.in.y})) == 0);
    }

    // ---- step 3: random nodes, one per spacing^2 ------------------------------
    std::stringstream ss(spacings);
    std::string tok;
    struct Roles { double s; std::vector<SensorNode> nodes; size_t ch, free; std::vector<double> ed; };
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
        std::vector<double> ed(nodes.size());
        for (size_t i = 0; i < nodes.size(); ++i) ed[i] = EdgeDistance(nodes[i].pos, edges);
        // Without the margin, for comparison: only the CH and its cell's CL may differ.
        std::vector<SensorNode> freeRoles = nodes;
        const size_t free = AssignRoles(freeRoles, ed, 0.0);
        CheckRoles(freeRoles, free, ed, 0.0);
        const size_t ch = AssignRoles(nodes, ed, chMargin);
        if (ch == nodes.size()) {
            std::fprintf(stderr, "no node is %.0f m from the edge: lower --chMargin\n", chMargin);
            return 1;
        }
        CheckRoles(nodes, ch, ed, chMargin);
        for (size_t i = 0; i < nodes.size(); ++i) {
            CHECK(nodes[i].pos.x == freeRoles[i].pos.x && nodes[i].pos.y == freeRoles[i].pos.y);
            CHECK(nodes[i].Score() == freeRoles[i].Score());
            if (nodes[i].isCL != freeRoles[i].isCL)
                CHECK(nodes[i].cell == nodes[ch].cell || nodes[i].cell == nodes[free].cell);
        }
        roles.push_back({s, nodes, ch, free, ed});
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
        std::fprintf(f, "id,x,y,q,r,nnM,edgeM,obs,cpu,comm,score,isCH,isCL\n");
        for (size_t i = 0; i < nodes.size(); ++i)
            std::fprintf(f, "%u,%.3f,%.3f,%d,%d,%.3f,%.3f,%.6f,%.6f,%.6f,%.6f,%d,%d\n", nodes[i].id,
                         nodes[i].pos.x, nodes[i].pos.y, nodes[i].cell.q, nodes[i].cell.r, nn[i], ed[i],
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
        const SensorNode& f = R.nodes[R.free];
        std::printf("         |   %.0f m from the edge (margin %.0f m); strongest anywhere: #%u, "
                    "strength %.3f, %.0f m from the edge%s\n", R.ed[R.ch], chMargin, f.id,
                    f.Score(), R.ed[R.free], R.free == R.ch ? " (the same node)" : "");
    }

    // ---- step 5: a Dubins flight path across the cluster, over the CH ----------
    std::unordered_set<Hex, HexHash> inside(sel);
    inside.insert(holes.begin(), holes.end());
    // Two points drawn uniformly along that edge (by length).
    CoopRng rx(seed, kStreamCross + pick);
    auto onEdge = [&](size_t& which) {
        double u = rx.Uniform() * perim;
        for (which = 0; which + 1 < edges.size(); ++which) {
            const double L = std::hypot(edges[which].b.x - edges[which].a.x, edges[which].b.y - edges[which].a.y);
            if (u < L) break;
            u -= L;
        }
        const Edge& e = edges[which];
        const double L = std::hypot(e.b.x - e.a.x, e.b.y - e.a.y);
        const double f = std::min(u / L, 1.0);
        return Point{e.a.x + f * (e.b.x - e.a.x), e.a.y + f * (e.b.y - e.a.y)};
    };
    size_t eIn = 0, eOut = 0;
    const Point entry = onEdge(eIn), exitP = onEdge(eOut);
    // Flying in from, and out to, the outside: a straight lead of one turn radius
    // before the entry and after the exit must stay outside the cluster.
    const double lead = rho;
    std::printf("\nflight path across the cluster (perimeter %.0f m, %zu edges): entry -> CH -> exit, "
                "random entry/exit (pick %u), open Dubins, min turn radius %.1f m, straight "
                "lead-in/out %.0f m outside\n", perim, edges.size(), pick, rho, lead);
    std::printf("  entry (%.0f, %.0f), exit (%.0f, %.0f): %.0f m apart\n", entry.x, entry.y, exitP.x,
                exitP.y, std::hypot(exitP.x - entry.x, exitP.y - entry.y));
    // Strictly across the edge (not along it), and the lead clear of the cluster.
    const Edge& EI = edges[eIn];
    const Edge& EO = edges[eOut];
    const std::vector<HeadingOk> ok = {
        [&](double th) {
            return std::cos(th) * EI.in.x + std::sin(th) * EI.in.y > 1e-6 &&
                   LeadOutside(g, inside, entry, th, -1, lead);
        },
        nullptr,
        [&](double th) {
            return std::cos(th) * EO.in.x + std::sin(th) * EO.in.y < -1e-6 &&
                   LeadOutside(g, inside, exitP, th, +1, lead);
        }};
    for (const Roles& R : roles) {
        const SensorNode& chN = R.nodes[R.ch];
        const std::vector<Point> pts = {entry, chN.pos, exitP};
        const Path t = PlanPath(pts, rho, ok);
        CHECK(!t.poses.empty());
        CheckPath(g, inside, t, pts, ok, edges[eIn], edges[eOut], rho, lead);
        const double poly = std::hypot(chN.pos.x - entry.x, chN.pos.y - entry.y) +
                            std::hypot(exitP.x - chN.pos.x, exitP.y - chN.pos.y);
        std::printf("  %4.0f m: CH #%u | entry -> CH -> exit %.0f m (straight lines %.0f m, +%.0f%%) "
                    "= %.1f s at %.0f m/s; with leads %.0f m\n", R.s, chN.id, t.length, poly,
                    100 * (t.length / poly - 1), t.length / params::kUavSpeedMps,
                    params::kUavSpeedMps, t.length + 2 * lead);
        for (size_t i = 0; i < t.legs.size(); ++i)
            std::printf("         leg %zu: %s %.0f m (%.0f / %.0f / %.0f)\n", i + 1,
                        t.legs[i].Word().c_str(), t.legs[i].Length(), t.legs[i].seg[0] * rho,
                        t.legs[i].seg[1] * rho, t.legs[i].seg[2] * rho);
        char sfx[32];
        std::snprintf(sfx, sizeof sfx, "-s%.0f.csv", R.s);
        // part 0: lead-in, 1: entry -> CH, 2: CH -> exit, 3: lead-out; seg -1 = a lead
        FILE* fp = std::fopen((out + "-path" + sfx).c_str(), "w");
        std::fprintf(fp, "part,seg,x,y,thDeg\n");
        auto leadLine = [&](int part, const Pose& p, double sign) {
            for (double d = 0; d <= lead + 1e-9; d += 2) {
                const double tt = sign < 0 ? d - lead : d;
                std::fprintf(fp, "%d,-1,%.3f,%.3f,%.4f\n", part, p.x + tt * std::cos(p.th),
                             p.y + tt * std::sin(p.th), p.th * 180 / M_PI);
            }
        };
        leadLine(0, t.poses.front(), -1);
        for (size_t i = 0; i < t.legs.size(); ++i) {
            std::vector<int> sg;
            const std::vector<Pose> sm = DubinsSample(t.poses[i], t.legs[i], 2.0, &sg);
            for (size_t k = 0; k < sm.size(); ++k)
                std::fprintf(fp, "%zu,%d,%.3f,%.3f,%.4f\n", i + 1, sg[k], sm[k].x, sm[k].y,
                             sm[k].th * 180 / M_PI);
        }
        leadLine(3, t.poses.back(), +1);
        std::fclose(fp);
        FILE* fw = std::fopen((out + "-pathwp" + sfx).c_str(), "w");
        std::fprintf(fw, "point,id,x,y,thDeg,legWord,legM,rho,leadM,lengthM,pick\n");
        const char* name[3] = {"entry", "CH", "exit"};
        for (size_t i = 0; i < 3; ++i) {
            const bool hasLeg = i < t.legs.size();
            std::fprintf(fw, "%s,%d,%.3f,%.3f,%.4f,%s,%.3f,%.3f,%.3f,%.3f,%u\n", name[i],
                         i == 1 ? (int)chN.id : -1, t.poses[i].x, t.poses[i].y,
                         t.poses[i].th * 180 / M_PI, hasLeg ? t.legs[i].Word().c_str() : "-",
                         hasLeg ? t.legs[i].Length() : 0.0, rho, lead, t.length, pick);
        }
        std::fclose(fw);
    }

    // ---- step 6: pre-built routes over the cells (PECEE elastic clustering) ----
    std::printf("\nroutes: G2G link = nodes at most %.0f m apart; per node: next hop to its CL, to "
                "each adjacent cell, main route to the CH\n", linkRange);
    std::printf("%8s %8s %7s %9s %11s %11s %12s %14s %13s\n", "spacing", "links", "degree",
                "isolated", "no route CL", "no main", "hops to CH", "free (no cells)", "stretch max");
    for (const Roles& R : roles) {
        const Routing rt = BuildRouting(R.nodes, R.ch, linkRange);
        CheckRouting(R.nodes, R.ch, rt, linkRange);
        const std::vector<uint32_t> fh = FreeHops(rt, R.ch);
        size_t links = 0, iso = 0, noCL = 0, noMain = 0, freeOnly = 0;
        double hm = 0, fm = 0, smax = 0;
        uint32_t hmax = 0;
        size_t nr = 0;
        for (size_t i = 0; i < R.nodes.size(); ++i) {
            links += rt.links[i].size();
            iso += rt.links[i].empty();
            noCL += rt.table[i].toCL.hops == kNoRoute;
            const uint32_t h = rt.table[i].hopsToCH;
            if (h == kNoRoute) { noMain++; freeOnly += fh[i] != kNoRoute; continue; }
            nr++;
            hm += h;
            fm += fh[i];
            hmax = std::max(hmax, h);
            if (fh[i] > 0) smax = std::max(smax, (double)h / fh[i]);
        }
        std::printf("%6.0f m %8zu %7.2f %9zu %11zu %11zu %7.1f (max %u) %9.1f %13.2f\n", R.s,
                    links / 2, (double)links / R.nodes.size(), iso, noCL, noMain, hm / nr, hmax,
                    fm / nr, smax);
        std::printf("         | %zu node(s) without a main route could reach the CH ignoring cells\n",
                    freeOnly);
        char sfx[32];
        std::snprintf(sfx, sizeof sfx, "-s%.0f.csv", R.s);
        FILE* f = std::fopen((out + "-routes" + sfx).c_str(), "w");
        std::fprintf(f, "id,degree,toCL,hopsCL,mainNext,mainVia,hopsCH,metresCH,freeHopsCH,toCells\n");
        auto id = [&](int32_t k) { return k == kNoHop ? -1 : (int64_t)R.nodes[k].id; };
        for (size_t i = 0; i < R.nodes.size(); ++i) {
            const RouteTable& t = rt.table[i];
            char via[32] = "-";
            if (t.hopsToCH != kNoRoute)
                std::snprintf(via, sizeof via, t.mainViaCL ? "CL" : "%d:%d", t.mainCell.q, t.mainCell.r);
            std::fprintf(f, "%u,%zu,%lld,%d,%lld,%s,%d,%.1f,%d,", R.nodes[i].id, rt.links[i].size(),
                         (long long)id(t.toCL.next), t.toCL.hops == kNoRoute ? -1 : (int)t.toCL.hops,
                         (long long)id(t.mainNext), via, t.hopsToCH == kNoRoute ? -1 : (int)t.hopsToCH,
                         t.metresToCH, fh[i] == kNoRoute ? -1 : (int)fh[i]);
            bool first = true;
            for (const auto& [B, h] : t.toCell) {
                std::fprintf(f, "%s%d:%d>%lld/%d", first ? "" : "|", B.q, B.r, (long long)id(h.next),
                             h.hops == kNoRoute ? -1 : (int)h.hops);
                first = false;
            }
            std::fprintf(f, "\n");
        }
        std::fclose(f);
    }
    std::printf("\n%u CHECKS PASSED\n", g_checks);
    return 0;
}
