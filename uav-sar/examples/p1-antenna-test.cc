// Would several UAV antennas change either scaling result?
//
// The question: the aircraft can transmit different packets to different nodes
// at the same time, while a node still listens to one antenna only. Does that
// move the numbers in p1-scaling-test?
//
// Two things have to be measured before that can be answered, because both are
// about how many ground nodes sit under the aircraft AT ONCE:
//
//   A  HOW MANY HEADS ARE IN RANGE AT THE SAME INSTANT, along the flown path.
//      One omnidirectional broadcast already serves every head inside p(d)
//      simultaneously. Extra beams can only help if the heads need DIFFERENT
//      content; under I4 (uniform round-robin, no acknowledgement) they do not.
//      So this count is what a second antenna would have to beat.
//
//   B  HOW MUCH OF A CELL ONE PASS SEEDS FOR FREE. Every member -- not just the
//      head -- that falls inside p(d) while the aircraft goes by has the packet
//      without anyone relaying it. The intra-cell flood then starts from that
//      whole set rather than from the head alone. If a single broadcast already
//      seeds most of the cell, a per-node beam has nothing left to seed.
//
// Altitude is not a p1 parameter, so p(d) is evaluated on horizontal separation
// and the sweep is repeated at a few slant heights to show how much that
// assumption is worth.
//
//   p1-antenna-test [gridSize] [seed] [out.csv]

#include "../models/p1/p1-cells.h"
#include "../models/p1/p1-field.h"
#include "../models/p1/p1-params.h"
#include "../models/p1/p1-sensing.h"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <map>
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

namespace {

// Reception probability, the logistic of p1-params.
double Prx(double d) { return 1.0 / (1.0 + std::exp((d - kPrxD50M) / kPrxWidth)); }

struct Flood {
    uint32_t depth = 0;
    uint32_t slots = 0;
    uint32_t unreached = 0;
};

// Flood a cell from a SET of roots and count the slots a spatial-reuse schedule
// needs. Same model as p1-scaling-test: greedy colouring, a forwarder takes the
// earliest slot after its parent's in which nothing within kReuseRangeM speaks.
// With one root this reduces exactly to the single-source case.
Flood FloodFrom(const Cell& c, const std::map<uint32_t, const Node*>& byId,
                const std::set<uint32_t>& roots) {
    Flood f;
    std::vector<uint32_t> ids;
    for (const CellMember& m : c.members) ids.push_back(m.id);

    std::map<uint32_t, uint32_t> hop;
    std::map<uint32_t, int32_t> par;
    std::vector<uint32_t> frontier;
    for (uint32_t r : roots)
        if (std::find(ids.begin(), ids.end(), r) != ids.end()) {
            hop[r] = 0; par[r] = -1; frontier.push_back(r);
        }

    uint32_t d = 0;
    while (!frontier.empty()) {
        std::vector<uint32_t> next;
        for (uint32_t cur : frontier) {
            const Node& a = *byId.at(cur);
            for (uint32_t other : ids) {
                if (hop.count(other)) continue;
                const Node& b = *byId.at(other);
                if (std::hypot(a.x - b.x, a.y - b.y) > kGroundRangeM) continue;
                hop[other] = d + 1; par[other] = (int32_t)cur;
                next.push_back(other);
            }
        }
        frontier.swap(next);
        if (!frontier.empty()) ++d;
    }
    f.depth = d;
    for (uint32_t id : ids) if (!hop.count(id)) f.unreached++;

    // Who must speak: anyone with a child.
    std::set<uint32_t> sends;
    for (uint32_t id : ids)
        if (par.count(id) && par[id] >= 0) sends.insert((uint32_t)par[id]);
    if (sends.empty()) return f;   // one broadcast covered the whole cell

    std::vector<uint32_t> order(sends.begin(), sends.end());
    std::sort(order.begin(), order.end(),
              [&](uint32_t a, uint32_t b) { return hop[a] < hop[b]; });

    std::map<uint32_t, uint32_t> slotOf;
    std::map<uint32_t, std::vector<uint32_t>> inSlot;
    for (uint32_t id : order) {
        uint32_t earliest = 0;
        if (par[id] >= 0 && slotOf.count((uint32_t)par[id]))
            earliest = slotOf[(uint32_t)par[id]] + 1;
        const Node& me = *byId.at(id);
        uint32_t s = earliest;
        while (true) {
            bool clash = false;
            for (uint32_t o : inSlot[s])
                if (std::hypot(me.x - byId.at(o)->x, me.y - byId.at(o)->y) < kReuseRangeM) {
                    clash = true; break;
                }
            if (!clash) break;
            ++s;
        }
        slotOf[id] = s;
        inSlot[s].push_back(id);
        f.slots = std::max(f.slots, s + 1);
    }
    return f;
}

// The PA1 flight path of one row, in the row frame: straight down the row line,
// weaving out to each head by its offset over that head's cell interval.
std::vector<std::pair<double, double>>
RowPath(const CellPlan& plan, const std::vector<int32_t>& cells,
        const std::map<uint32_t, const Node*>& byId, double stepM) {
    const double a = plan.cellPitchM;
    struct Seg { double u, w, delta; };   // delta is SIGNED, toward the head
    std::vector<Seg> segs;
    double lo = 1e18, hi = -1e18, wRow = 0;
    for (int32_t cid : cells) {
        const Cell& c = plan.cells.at(cid);
        double u, w;
        plan.field.ToRowFrame(c.cx, c.cy, u, w);
        lo = std::min(lo, u); hi = std::max(hi, u);
        wRow = w;
        double delta = 0.0;
        if (c.hasHead) {
            const Node& h = *byId.at(c.head);
            double hu, hw;
            plan.field.ToRowFrame(h.x, h.y, hu, hw);
            delta = (hw >= w ? 1.0 : -1.0) * c.headOffsetM;
        }
        segs.push_back({u, w, delta});
    }
    std::sort(segs.begin(), segs.end(),
              [](const Seg& p, const Seg& q) { return p.u < q.u; });

    std::vector<std::pair<double, double>> path;
    for (double u = lo - a / 2; u <= hi + a / 2; u += stepM) {
        double w = wRow;
        for (const Seg& s : segs) {
            if (u < s.u - a / 2 || u > s.u + a / 2) continue;
            const double t = (u - (s.u - a / 2)) / a;
            w = s.w + s.delta * std::sin(M_PI * t);
            break;
        }
        path.push_back({u, w});
    }
    return path;
}

}  // namespace

int main(int argc, char* argv[]) {
    const uint32_t grid = argc > 1 ? (uint32_t)std::atoi(argv[1]) : 40;
    const uint32_t seed = argc > 2 ? (uint32_t)std::atoi(argv[2]) : 1;
    const std::string out = argc > 3 ? argv[3] : "";
    const double spacing = 20.0;
    const double side = (grid - 1) * spacing;
    const double tilt = 20.0 * M_PI / 180.0;
    const double W = side, H = side * 0.62;
    const double rho = TurnRadiusM(kCruiseMps);
    const double stepM = 2.0;

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
    std::map<uint32_t, const Node*> byId;
    for (const Node& n : nodes) byId[n.id] = &n;

    std::printf("field %.0f x %.0f m, %zu nodes @%.0fm.  p(d): d50 %.0f m, "
                "width %.0f m  (p=0.5 at %.0f m, p=0.9 at %.0f m)\n",
                W, H, nodes.size(), spacing, kPrxD50M, kPrxWidth, kPrxD50M,
                kPrxD50M - kPrxWidth * std::log(9.0));
    std::printf("ground link range %.0f m, reuse guard %.0f m, MAC slot %.0f ms\n",
                kGroundRangeM, kReuseRangeM, 1000 * kMacSlotS);

    // ==================================================================== A
    std::printf("\nA.  HEADS INSIDE p(d) AT THE SAME INSTANT, along the path\n");
    std::printf("    (a broadcast already reaches all of them; this is what an\n"
                "     extra beam would have to beat)\n");
    std::printf("\n%6s %6s %10s %10s %9s %9s %9s\n", "R_c", "heads",
                "mean>=0.5", "max>=0.5", "E[heads]", "frac>=2", "frac==1");

    FILE* f = out.empty() ? nullptr : std::fopen(out.c_str(), "w");
    if (f) std::fprintf(f, "Rc,heads,meanInRange,maxInRange,expected,frac2,frac1,"
                           "seedPass,seedSnap,slotsHead,slotsPass,slotsSnap,"
                           "floodHeadS,floodPassS,floodSnapS,wholePass,wholeSnap\n");

    struct Row { double rc, mean, frac2, seedPass, seedSnap, sHead, sPass,
                        sSnap, wholePass, wholeSnap; };
    std::vector<Row> rows;

    for (double rc = 40; rc <= 280.001; rc += 20.0) {
        CellPlan plan = BuildCells(nodes, field, rc, kGroundRangeM, rho);

        std::vector<const Cell*> served;
        for (const auto& [cid, c] : plan.cells) if (c.hasHead) served.push_back(&c);
        if (served.empty()) continue;

        // The whole flight path, row by row.
        std::vector<std::pair<double, double>> path;
        for (const auto& [row, cells] : plan.cellsByRow) {
            auto p = RowPath(plan, cells, byId, stepM);
            path.insert(path.end(), p.begin(), p.end());
        }
        CHECK(!path.empty());

        // Heads in the row frame, once.
        std::vector<std::pair<double, double>> headUW;
        for (const Cell* c : served) {
            const Node& h = *byId.at(c->head);
            double u, w; field.ToRowFrame(h.x, h.y, u, w);
            headUW.push_back({u, w});
        }

        double sumIn = 0, sumExp = 0, n2 = 0, n1 = 0;
        uint32_t maxIn = 0;
        for (const auto& [pu, pw] : path) {
            uint32_t in = 0; double e = 0;
            for (const auto& [hu, hw] : headUW) {
                const double d = std::hypot(pu - hu, pw - hw);
                if (d > 3 * kPrxD50M) continue;
                const double p = Prx(d);
                e += p;
                if (p >= 0.5) in++;
            }
            sumIn += in; sumExp += e; maxIn = std::max(maxIn, in);
            if (in >= 2) n2++;
            if (in == 1) n1++;
        }
        const double S = (double)path.size();

        // ================================================================ B
        // What one pass seeds for free, and what that does to the flood.
        // Two seed sets, and the difference between them is the whole point.
        //   pass   every member in range at SOME instant of the flight. That is
        //          the right set for a STREAM of packets sent throughout the
        //          pass, which is what T0 actually does.
        //   snap   every member in range at ONE instant -- the single best
        //          sample. That is the right set for ONE packet. Never quote
        //          the pass figure for a single packet.
        double seedPass = 0, seedSnap = 0, sHead = 0, sPass = 0, sSnap = 0;
        double wholePass = 0, wholeSnap = 0;
        uint32_t nc = 0;
        for (const Cell* c : served) {
            std::vector<std::pair<double, double>> uw;
            for (const CellMember& m : c->members) {
                const Node& nd = *byId.at(m.id);
                double u, w; field.ToRowFrame(nd.x, nd.y, u, w);
                uw.push_back({u, w});
            }
            std::set<uint32_t> pass, snap;
            for (size_t i = 0; i < c->members.size(); ++i)
                for (const auto& [pu, pw] : path)
                    if (Prx(std::hypot(pu - uw[i].first, pw - uw[i].second)) >= 0.5) {
                        pass.insert(c->members[i].id); break;
                    }
            for (const auto& [pu, pw] : path) {     // best single instant
                std::set<uint32_t> here;
                for (size_t i = 0; i < c->members.size(); ++i)
                    if (Prx(std::hypot(pu - uw[i].first, pw - uw[i].second)) >= 0.5)
                        here.insert(c->members[i].id);
                if (here.size() > snap.size()) snap.swap(here);
            }
            CHECK(snap.size() <= pass.size());      // one instant cannot beat all

            auto orHead = [&](const std::set<uint32_t>& r) {
                return r.empty() ? std::set<uint32_t>{c->head} : r;
            };
            const Flood fh = FloodFrom(*c, byId, {c->head});
            const Flood fp = FloodFrom(*c, byId, orHead(pass));
            const Flood fs = FloodFrom(*c, byId, orHead(snap));
            CHECK(fp.slots <= fh.slots);            // more roots cannot be slower
            CHECK(fp.slots <= fs.slots);
            const double n = (double)c->members.size();
            seedPass += pass.size() / n; seedSnap += snap.size() / n;
            sHead += fh.slots; sPass += fp.slots; sSnap += fs.slots;
            if (fp.slots == 0) wholePass++;
            if (fs.slots == 0) wholeSnap++;
            nc++;
        }
        seedPass /= nc; seedSnap /= nc; wholePass /= nc; wholeSnap /= nc;
        sHead /= nc; sPass /= nc; sSnap /= nc;

        std::printf("%6.0f %6zu %10.2f %10u %9.2f %9.1f%% %8.1f%%\n", rc,
                    served.size(), sumIn / S, maxIn, sumExp / S,
                    100 * n2 / S, 100 * n1 / S);
        if (f)
            std::fprintf(f, "%.0f,%zu,%.4f,%u,%.4f,%.4f,%.4f,%.4f,%.4f,%.3f,"
                            "%.3f,%.3f,%.4f,%.4f,%.4f,%.4f,%.4f\n",
                         rc, served.size(), sumIn / S, maxIn, sumExp / S,
                         n2 / S, n1 / S, seedPass, seedSnap, sHead, sPass, sSnap,
                         sHead * kMacSlotS, sPass * kMacSlotS, sSnap * kMacSlotS,
                         wholePass, wholeSnap);
        rows.push_back({rc, sumIn / S, n2 / S, seedPass, seedSnap, sHead, sPass,
                        sSnap, wholePass, wholeSnap});
    }
    if (f) std::fclose(f);

    // ==================================================================== B
    std::printf("\nB.  WHAT ONE BROADCAST SEEDS FOR FREE, and the flood that is left\n");
    std::printf("    pass = in range at SOME instant of the flight (a stream of\n"
                "           packets).  snap = in range at ONE instant (one packet).\n");
    std::printf("\n%6s | %8s %10s %10s %10s | %8s %10s %10s %10s\n", "R_c",
                "seed", "slots", "flood(s)", "done", "seed", "slots", "flood(s)", "done");
    std::printf("%6s | %8s %10s %10s %10s | %8s %10s %10s %10s   [head-only: slots]\n",
                "", "pass", "pass", "pass", "pass", "snap", "snap", "snap", "snap");
    for (const Row& r : rows)
        std::printf("%6.0f | %7.0f%% %10.2f %10.2f %9.0f%% | %7.0f%% %10.2f %10.2f "
                    "%9.0f%%   [%.2f]\n", r.rc,
                    100 * r.seedPass, r.sPass, r.sPass * kMacSlotS, 100 * r.wholePass,
                    100 * r.seedSnap, r.sSnap, r.sSnap * kMacSlotS, 100 * r.wholeSnap,
                    r.sHead);

    // ==================================================================== C
    // Altitude sensitivity for A, since z is not a p1 parameter.
    std::printf("\nC.  SENSITIVITY TO ALTITUDE (p(d) on slant range).  R_c = %.0f m\n",
                kCellRadiusM);
    {
        CellPlan plan = BuildCells(nodes, field, kCellRadiusM, kGroundRangeM, rho);
        std::vector<std::pair<double, double>> path;
        for (const auto& [row, cells] : plan.cellsByRow) {
            auto p = RowPath(plan, cells, byId, stepM);
            path.insert(path.end(), p.begin(), p.end());
        }
        std::vector<std::pair<double, double>> headUW;
        for (const auto& [cid, c] : plan.cells) {
            if (!c.hasHead) continue;
            const Node& h = *byId.at(c.head);
            double u, w; field.ToRowFrame(h.x, h.y, u, w);
            headUW.push_back({u, w});
        }
        FILE* fz = out.empty() ? nullptr : std::fopen((out + ".alt.csv").c_str(), "w");
        if (fz) std::fprintf(fz, "z,meanInRange,maxInRange\n");
        std::printf("%8s %12s %10s\n", "z (m)", "mean heads", "max");
        for (double z : {0.0, 25.0, 50.0, 75.0, 100.0, 125.0, 150.0, 175.0, 200.0}) {
            double sumIn = 0; uint32_t maxIn = 0;
            for (const auto& [pu, pw] : path) {
                uint32_t in = 0;
                for (const auto& [hu, hw] : headUW) {
                    const double dh = std::hypot(pu - hu, pw - hw);
                    if (Prx(std::hypot(dh, z)) >= 0.5) in++;
                }
                sumIn += in; maxIn = std::max(maxIn, in);
            }
            std::printf("%8.0f %12.2f %10u\n", z, sumIn / path.size(), maxIn);
            if (fz) std::fprintf(fz, "%.0f,%.4f,%u\n", z, sumIn / path.size(), maxIn);
        }
        if (fz) std::fclose(fz);
    }

    std::printf("\n%u CHECKS PASSED\n", g_checks);
    return 0;
}
