// Standalone verification of the PECEE substrate (cell-grid + inter-cell
// routing). No ns-3 simulation needed: builds a grid of positions, prints the
// cell structure, and asserts the design invariants.

#include "../models/common/cell-grid.h"
#include "../models/common/inter-cell-routing.h"

#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <vector>

using namespace ns3::uavsar;

int main(int argc, char* argv[]) {
    uint32_t gridSize = 8;
    double spacing = 20.0;
    double cellRadius = 40.0;
    double neighborRange = 30.0;
    if (argc > 1) gridSize = (uint32_t)std::atoi(argv[1]);
    if (argc > 2) cellRadius = std::atof(argv[2]);

    // Build N×N grid of ground node positions (ids 0..N-1).
    std::vector<NodePos> nodes;
    uint32_t id = 0;
    for (uint32_t i = 0; i < gridSize; i++)
        for (uint32_t j = 0; j < gridSize; j++)
            nodes.push_back({id++, j * spacing, i * spacing});

    CellGridConfig cfg;
    cfg.cellRadius = cellRadius;
    cfg.neighborRange = neighborRange;

    CellGridPlan plan = BuildCellGrid(nodes, cfg);
    InterCellRouting routing = BuildInterCellRouting(plan);

    std::cout << "=== SUBSTRATE: " << gridSize << "x" << gridSize
              << " grid, spacing=" << spacing << "m, cellRadius=" << cellRadius
              << "m, neighborRange=" << neighborRange << "m ===\n";
    std::cout << "nodes=" << plan.nodes.size() << " cells=" << plan.cells.size()
              << " colors=" << plan.colorCount << "\n\n";

    for (const auto& [cid, cell] : plan.cells) {
        std::cout << "cell " << cid << " (q=" << cell.q << ",r=" << cell.r
                  << ") center=(" << cell.centerX << "," << cell.centerY << ")"
                  << " leader=" << cell.leaderId << " color=" << cell.color
                  << " members=" << cell.members.size() << " adj={";
        for (int32_t a : cell.adjacentCells) std::cout << a << " ";
        std::cout << "}\n";
    }

    int checks = 0, fails = 0;
    auto CHECK = [&](bool ok, const std::string& msg) {
        checks++;
        if (!ok) { fails++; std::cout << "  FAIL: " << msg << "\n"; }
    };

    // Inv 1: every node assigned to a cell, has a leader in the same cell.
    for (const auto& [nid, ni] : plan.nodes) {
        CHECK(ni.cellId >= 0, "node has no cell");
        CHECK(plan.nodes.at(ni.leaderId).cellId == ni.cellId, "leader in different cell");
    }

    // Inv 2: exactly one leader per cell, and it is closest to the centroid.
    for (const auto& [cid, cell] : plan.cells) {
        uint32_t leaders = 0;
        for (uint32_t m : cell.members) if (plan.nodes.at(m).isLeader) leaders++;
        CHECK(leaders == 1, "cell must have exactly one leader");

        double sx = 0, sy = 0;
        for (uint32_t m : cell.members) { sx += plan.nodes.at(m).x; sy += plan.nodes.at(m).y; }
        double gx = sx / cell.members.size(), gy = sy / cell.members.size();
        double dLeader = std::hypot(plan.nodes.at(cell.leaderId).x - gx,
                                    plan.nodes.at(cell.leaderId).y - gy);
        for (uint32_t m : cell.members) {
            double d = std::hypot(plan.nodes.at(m).x - gx, plan.nodes.at(m).y - gy);
            CHECK(d >= dLeader - 1e-6, "leader not closest to centroid");
        }
    }

    // Inv 3: adjacent cells have different colors.
    for (const auto& [cid, cell] : plan.cells)
        for (int32_t adj : cell.adjacentCells)
            CHECK(plan.cells.at(adj).color != cell.color, "adjacent cells share color");

    // Inv 4: every adjacency has a gateway (both directions).
    for (const auto& [cid, cell] : plan.cells)
        for (int32_t adj : cell.adjacentCells) {
            bool has = routing.gateway.count(cid) && routing.gateway.at(cid).count(adj);
            CHECK(has, "missing gateway for adjacency");
        }

    // Inv 5: intra-cell tree — every non-isolated member reaches its leader.
    for (const auto& [cid, cell] : plan.cells)
        for (uint32_t m : cell.members) {
            const auto& ni = plan.nodes.at(m);
            if (ni.isLeader) continue;
            // reachable iff hopToLeader finite; isolated members (no in-cell link) allowed
            bool hasInCellNeighbor = false;
            for (uint32_t nb : ni.neighbors)
                if (plan.nodes.at(nb).cellId == cid) { hasInCellNeighbor = true; break; }
            if (hasInCellNeighbor)
                CHECK(ni.hopToLeader != 0xFFFFFFFF, "connected member cannot reach leader");
        }

    // Demonstrate routing between two cells (first vs last).
    if (plan.cells.size() >= 2) {
        int32_t a = plan.cells.begin()->first;
        int32_t b = plan.cells.rbegin()->first;
        std::vector<int32_t> cr = CellRoute(plan, a, b);
        std::cout << "\nCellRoute " << a << "->" << b << ": ";
        for (int32_t c : cr) std::cout << c << " ";
        std::cout << "\n";
        std::vector<uint32_t> lp = LeaderPath(plan, routing, a, b);
        std::cout << "LeaderPath (node ids): ";
        for (uint32_t n : lp) std::cout << n << " ";
        std::cout << "\n";
        if (!cr.empty()) {
            CHECK(cr.front() == a && cr.back() == b, "cell route endpoints wrong");
            CHECK(!lp.empty() && lp.front() == plan.cells.at(a).leaderId &&
                      lp.back() == plan.cells.at(b).leaderId,
                  "leader path endpoints wrong");
        }
    }

    std::cout << "\n=== CHECKS: " << (checks - fails) << "/" << checks
              << " passed ===\n";
    return fails == 0 ? 0 : 1;
}
