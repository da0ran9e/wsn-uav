// Two measurements against cell radius, and the correlation between them.
//
//   1  TIME TO FLY PAST EVERY CLUSTER HEAD
//      One aircraft flies the PA1 row pattern: every row end to end, weaving out
//      to each head, turning between rows at L(h, rho). No dose, no service --
//      this is the traversal, not the delivery.
//
//   2  TIME FOR A PACKET TO FLOOD ONE CELL
//      From the head out to every member over the intra-cell tree.
//
// They pull opposite ways. A bigger cell means fewer cells, fewer rows and a
// shorter flight -- and a wider cell, a deeper tree and a slower flood. The
// point of the sweep is to see where they cross and how tightly they are tied.
//
//   p1-scaling-test [gridSize] [seed] [out.csv]

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

struct FloodResult {
    uint32_t depth = 0;         // hops from the head to the furthest member
    uint32_t forwarders = 0;    // members that must transmit at all
    uint32_t slots = 0;         // slots a spatial-reuse schedule actually needs
    uint32_t unreached = 0;
};

// Flood the cell from its head and count the slots it takes.
//
// Three models, because the truth is bracketed rather than known:
//   depth       perfect spatial reuse -- every node at the same depth fires at
//               once. A lower bound.
//   forwarders  no reuse at all -- one transmission per slot, cell-wide. An
//               upper bound.
//   slots       greedy colouring: a forwarder takes the earliest slot after its
//               parent's in which nothing within kReuseRangeM is transmitting.
//               This is the one to quote; the other two say how wide the
//               uncertainty is.
FloodResult FloodCell(const Cell& c, const std::map<uint32_t, const Node*>& byId) {
    FloodResult f;
    if (!c.hasHead) { f.unreached = (uint32_t)c.members.size(); return f; }

    std::map<uint32_t, const CellMember*> mem;
    for (const CellMember& m : c.members) mem[m.id] = &m;

    // Who must transmit: the head, and any member that has a child.
    std::map<uint32_t, bool> sends;
    sends[c.head] = true;
    for (const CellMember& m : c.members) {
        if (m.hops == 0xFFFFFFFFu) { f.unreached++; continue; }
        f.depth = std::max(f.depth, m.hops);
        if (m.parent >= 0) sends[(uint32_t)m.parent] = true;
    }
    f.forwarders = (uint32_t)sends.size();

    // Greedy slot colouring, in hop order so a parent always precedes its child.
    std::vector<const CellMember*> order;
    for (const CellMember& m : c.members)
        if (m.hops != 0xFFFFFFFFu && sends.count(m.id)) order.push_back(&m);
    std::sort(order.begin(), order.end(),
              [](const CellMember* a, const CellMember* b) { return a->hops < b->hops; });

    std::map<uint32_t, uint32_t> slotOf;                 // node -> slot
    std::map<uint32_t, std::vector<uint32_t>> inSlot;    // slot -> nodes
    for (const CellMember* m : order) {
        uint32_t earliest = 0;
        if (m->parent >= 0 && slotOf.count((uint32_t)m->parent))
            earliest = slotOf[(uint32_t)m->parent] + 1;
        const Node& me = *byId.at(m->id);
        uint32_t s = earliest;
        while (true) {
            bool clash = false;
            for (uint32_t other : inSlot[s]) {
                const Node& o = *byId.at(other);
                if (std::hypot(me.x - o.x, me.y - o.y) < kReuseRangeM) { clash = true; break; }
            }
            if (!clash) break;
            ++s;
        }
        slotOf[m->id] = s;
        inSlot[s].push_back(m->id);
        f.slots = std::max(f.slots, s + 1);
    }
    return f;
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

    std::printf("field %.0f x %.0f m (tilted %.0f deg), %zu nodes @%.0fm, "
                "ground range %.0fm, rho %.1fm\n", W, H, tilt * 180 / M_PI,
                nodes.size(), spacing, kGroundRangeM, rho);
    std::printf("flood: %u B at %.0f kbps = %.1f ms airtime, MAC slot %.0f ms"
                "  -> the SLOT is what binds, by %.0fx\n",
                kFloodPacketBytes, kPhyBps / 1000.0,
                1000.0 * kFloodPacketBytes * 8 / kPhyBps, 1000 * kMacSlotS,
                kMacSlotS / (kFloodPacketBytes * 8 / kPhyBps));

    std::printf("\n%6s %5s %5s %7s %9s %9s %9s | %6s %6s %7s %9s %9s\n",
                "R_c", "cells", "rows", "n/cell", "fly(s)", "turn(s)", "weave(s)",
                "depth", "fwd", "slots", "flood(s)", "flood_max");

    FILE* f = out.empty() ? nullptr : std::fopen(out.c_str(), "w");
    if (f) std::fprintf(f, "Rc,cells,rows,nodesPerCell,flyS,turnS,weaveS,rowLenM,"
                           "depthMean,depthMax,fwdMean,slotsMean,slotsMax,"
                           "floodMeanS,floodMaxS,floodDepthS,floodSerialS\n");

    std::vector<double> vRc, vFly, vFlood;
    for (double rc = 40; rc <= 280.001; rc += 10.0) {
        CellPlan plan = BuildCells(nodes, field, rc, kGroundRangeM, rho);

        // --- 1. time to fly past every head --------------------------------
        double rowLen = 0, weaveM = 0;
        for (const auto& [row, cells] : plan.cellsByRow) {
            double lo = 1e18, hi = -1e18;
            for (int32_t cid : cells) {
                const Cell& c = plan.cells.at(cid);
                double u, w;
                field.ToRowFrame(c.cx, c.cy, u, w);
                lo = std::min(lo, u); hi = std::max(hi, u);
                if (c.hasHead) weaveM += WeaveExtraM(c.headOffsetM, plan.cellPitchM);
            }
            rowLen += (hi - lo) + plan.cellPitchM;
        }
        const uint32_t rows = (uint32_t)plan.cellsByRow.size();
        const double turnM = rows > 1 ? (rows - 1) * RowChangeM(plan.rowPitchM, rho) : 0.0;
        const double flyS = (rowLen + turnM + weaveM) / kCruiseMps;

        // --- 2. time to flood one cell -------------------------------------
        double dSum = 0, fSum = 0, sSum = 0, nSum = 0;
        uint32_t dMax = 0, sMax = 0, served = 0;
        for (const auto& [cid, c] : plan.cells) {
            if (!c.hasHead) continue;
            const FloodResult fr = FloodCell(c, byId);
            CHECK(fr.slots >= fr.depth);            // reuse can never beat depth
            CHECK(fr.slots <= fr.forwarders);       // nor be worse than serial
            dSum += fr.depth; dMax = std::max(dMax, fr.depth);
            fSum += fr.forwarders;
            sSum += fr.slots; sMax = std::max(sMax, fr.slots);
            nSum += c.members.size();
            served++;
        }
        if (!served) continue;
        const double floodMean = sSum / served * kMacSlotS;
        const double floodMax = sMax * kMacSlotS;

        std::printf("%6.0f %5zu %5u %7.1f %9.1f %9.1f %9.2f | %6.1f %6.1f %7.1f "
                    "%9.1f %9.1f\n", rc, plan.cells.size(), rows, nSum / served,
                    flyS, turnM / kCruiseMps, weaveM / kCruiseMps,
                    dSum / served, fSum / served, sSum / served,
                    floodMean, floodMax);
        if (f)
            std::fprintf(f, "%.0f,%zu,%u,%.2f,%.3f,%.3f,%.3f,%.1f,%.3f,%u,%.3f,"
                            "%.3f,%u,%.3f,%.3f,%.3f,%.3f\n",
                         rc, plan.cells.size(), rows, nSum / served, flyS,
                         turnM / kCruiseMps, weaveM / kCruiseMps, rowLen,
                         dSum / served, dMax, fSum / served, sSum / served, sMax,
                         floodMean, floodMax,
                         dSum / served * kMacSlotS, fSum / served * kMacSlotS);
        vRc.push_back(rc); vFly.push_back(flyS); vFlood.push_back(floodMean);
    }
    if (f) std::fclose(f);

    // --- the correlation the sweep was run for -----------------------------
    auto corr = [](const std::vector<double>& a, const std::vector<double>& b) {
        const size_t n = a.size();
        double ma = 0, mb = 0;
        for (size_t i = 0; i < n; ++i) { ma += a[i]; mb += b[i]; }
        ma /= n; mb /= n;
        double sab = 0, sa = 0, sb = 0;
        for (size_t i = 0; i < n; ++i) {
            sab += (a[i] - ma) * (b[i] - mb);
            sa += (a[i] - ma) * (a[i] - ma);
            sb += (b[i] - mb) * (b[i] - mb);
        }
        return sab / std::sqrt(sa * sb);
    };
    std::printf("\ncorrelation over %zu radii:  fly vs R_c = %+.3f   "
                "flood vs R_c = %+.3f   fly vs flood = %+.3f\n",
                vRc.size(), corr(vRc, vFly), corr(vRc, vFlood), corr(vFly, vFlood));

    // Where the two meet, and where their sum is least.
    size_t best = 0;
    for (size_t i = 1; i < vRc.size(); ++i)
        if (vFly[i] + vFlood[i] < vFly[best] + vFlood[best]) best = i;
    std::printf("least total (fly + flood): R_c = %.0f m   fly %.0f s + flood %.1f s"
                " = %.0f s\n", vRc[best], vFly[best], vFlood[best],
                vFly[best] + vFlood[best]);
    std::printf("  NOTE the sum is only meaningful if the flood must FINISH after"
                " the pass. If it overlaps the flight, the mission cost is the"
                " flight alone and the flood only has to beat it.\n");
    for (size_t i = 0; i < vRc.size(); ++i)
        if (vFlood[i] > vFly[i]) {
            std::printf("  flood first exceeds flight at R_c = %.0f m"
                        " (%.1f s vs %.0f s)\n", vRc[i], vFlood[i], vFly[i]);
            break;
        }

    // --- what N3 is worth, in seconds --------------------------------------
    // Revision 1 of the spec had the head disseminate the REFERENCE SET inside
    // its cell (T_local). N3 removed that: the head matches its own observation
    // and nothing moves in-cell. This says what that decision saved, using the
    // same flood model and the same measured MAC slot.
    {
        const uint32_t pkts = (uint32_t)std::ceil(DoseBytes(FilesNeeded(1.0)) /
                                                  (double)kFloodPacketBytes);
        std::printf("\nWHAT N3 SAVED. One reference set for a unit-capability head"
                    " is %.0f B = %u packets of %u B.\n",
                    DoseBytes(FilesNeeded(1.0)), pkts, kFloodPacketBytes);
        std::printf("%6s %11s %12s %12s\n", "R_c", "flight(s)", "1 pkt (s)",
                    "whole ref (s)");
        for (size_t i = 0; i < vRc.size(); i += 4) {
            const double whole = vFlood[i] * pkts;
            std::printf("%6.0f %11.0f %12.1f %12.0f   (%.0f x the flight)\n",
                        vRc[i], vFly[i], vFlood[i], whole, whole / vFly[i]);
        }
        std::printf("  Flooding the reference inside a cell costs ORDERS more than"
                    " flying the whole field. N3 is not a simplification -- it is"
                    " the only version of this that closes.\n");
    }

    std::printf("\n%u CHECKS PASSED\n", g_checks);
    return 0;
}
