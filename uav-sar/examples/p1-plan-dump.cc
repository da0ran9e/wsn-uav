// Run the Phase-1 planner once and write the CSVs the visualiser reads.
// Pure logic; no ns-3 simulation.
//
//   p1-plan-dump OUTDIR [gridSize] [cellRadius] [vehicles] [seed] [thetaScale]

#include "../models/p1/p1-cells.h"
#include "../models/p1/p1-demand.h"
#include "../models/p1/p1-dubins.h"
#include "../models/p1/p1-refine.h"
#include "../models/p1/p1-route.h"
#include "../models/p1/p1-sensing.h"
#include "../models/p1/p1-speed.h"
#include "../models/p1/p1-tier1.h"

#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <random>
#include <string>
#include <vector>

using namespace ns3::uavsar::p1;

int main(int argc, char* argv[]) {
    const std::string dir = argc > 1 ? argv[1] : "p1-out";
    const uint32_t grid = argc > 2 ? (uint32_t)std::atoi(argv[2]) : 40;
    const double rc = argc > 3 ? std::atof(argv[3]) : 140.0;
    const uint32_t M = argc > 4 ? (uint32_t)std::atoi(argv[4]) : 3;
    const uint32_t seed = argc > 5 ? (uint32_t)std::atoi(argv[5]) : 1;
    const double tscale = argc > 6 ? std::atof(argv[6]) : 0.35;
    const double spacing = 20.0;
    std::filesystem::create_directories(dir);

    std::vector<std::pair<double, double>> xy;
    for (uint32_t i = 0; i < grid; i++)
        for (uint32_t j = 0; j < grid; j++) xy.push_back({j * spacing, i * spacing});
    const double side = (grid - 1) * spacing;

    std::vector<Node> nodes = BuildNodes(xy, seed);
    CellPlan plan = BuildCells(nodes, rc, kGroundRangeM);

    std::mt19937 orng(seed ^ 0xABCDu);
    std::uniform_real_distribution<double> ux(0.08 * side, 0.92 * side);
    std::vector<Object> objects;
    objects.push_back({ux(orng), ux(orng), true, 1.0});
    for (int k = 0; k < 3; k++) objects.push_back({ux(orng), ux(orng), false, 1.0});

    Tier1Result t1 = RunTier1(nodes, plan, objects, seed);
    DoseModel dose;
    auto demands = BuildDemands(plan, nodes, t1);
    for (auto& [cid, d] : demands) d.theta *= tscale;
    const double rho = TurnRadiusM(kCruiseMps);
    const Config depot{0.0, 0.0, 0.0};
    Plan pl = Refine(demands, plan, dose, depot, M, rho);

    // A run that found no valid plan still has a demand set worth dumping; the
    // feasible flag in config.csv is what says the plan is empty.
    if (pl.bestDemands.empty()) pl.bestDemands = demands;

    auto open = [&](const char* n) {
        return std::fopen((dir + "/" + n).c_str(), "w");
    };

    FILE* f = open("config.csv");
    std::fprintf(f, "key,value\ngrid,%u\nspacing,%.1f\nside,%.1f\ncellRadius,%.1f\n"
                    "rowPitch,%.2f\nvehicles,%u\nseed,%u\nthetaScale,%.3f\n"
                    "turnRadius,%.2f\ncruise,%.1f\nvmin,%.1f\nvmax,%.1f\n"
                    "alertScore,%.3f\nconfirmScore,%.3f\nprxD50,%.1f\n"
                    "makespan,%.2f\nfeasible,%d\nbestIter,%u\nconsistent,%u\n",
                 grid, spacing, side, rc, plan.RowPitchM(), M, seed, tscale,
                 rho, kCruiseMps, kMinMps, kMaxMps, kAlertScore, kConfirmScore,
                 kPrxD50M, pl.makespanS, pl.feasible ? 1 : 0, pl.bestIteration,
                 pl.consistentIterates);
    std::fclose(f);

    f = open("nodes.csv");
    std::fprintf(f, "id,x,y,modality,obs,cpu,rxBps,canMatch\n");
    for (const Node& n : nodes)
        std::fprintf(f, "%u,%.2f,%.2f,%s,%.3f,%.3f,%.0f,%d\n", n.id, n.x, n.y,
                     ModalityName(n.modality), n.obs, n.cpu, n.rxBps, n.CanMatch());
    std::fclose(f);

    f = open("cells.csv");
    std::fprintf(f, "id,q,r,cx,cy,class,leader,members,imagers,matchers,tLocal,"
                    "score,suspect,weight,holdsObject,holdsReal,theta,penaltyS,orbits\n");
    for (const auto& [cid, c] : plan.cells) {
        const CellReading* t = t1.cells.count(cid) ? &t1.cells.at(cid) : nullptr;
        const Demand& d = pl.bestDemands.at(cid);
        std::fprintf(f, "%d,%d,%d,%.2f,%.2f,%s,%u,%zu,%u,%u,%.2f,%.4f,%d,%.4f,%d,%d,%.0f,%.2f,%u\n",
                     cid, c.q, c.r, c.cx, c.cy, CellClassName(c.cls), c.leader,
                     c.members.size(), c.imagers, c.matchers, c.tLocalS,
                     t ? t->score : 0.0, t ? t->suspect : 0, t ? t->weight : 0.0,
                     t ? t->holdsObject : 0, t ? t->holdsReal : 0,
                     demands.at(cid).theta, d.penaltyS, d.orbits);
    }
    std::fclose(f);

    f = open("objects.csv");
    std::fprintf(f, "x,y,real,similarity\n");
    for (const Object& o : objects)
        std::fprintf(f, "%.2f,%.2f,%d,%.2f\n", o.x, o.y, o.real, o.similarity);
    std::fclose(f);

    f = open("tours.csv");
    std::fprintf(f, "vehicle,seq,cellId,x,y,hdgDeg,fromPrevM\n");
    for (size_t v = 0; v < pl.tours.size(); ++v)
        for (size_t k = 0; k < pl.tours[v].legs.size(); ++k) {
            const Leg& l = pl.tours[v].legs[k];
            std::fprintf(f, "%zu,%zu,%d,%.2f,%.2f,%.1f,%.2f\n", v, k, l.cellId,
                         l.cfg.x, l.cfg.y, l.cfg.hdg * 180.0 / M_PI, l.fromPrevM);
        }
    std::fclose(f);

    // The flown path, segment by segment, with the speed the LP chose. This is
    // the file the animation plays.
    f = open("path.csv");
    std::fprintf(f, "vehicle,seq,x,y,lengthM,speedMps,turning,tStartS\n");
    for (size_t v = 0; v < pl.speeds.size(); ++v) {
        double t = 0;
        for (size_t k = 0; k < pl.speeds[v].segments.size(); ++k) {
            const SpeedSegment& s = pl.speeds[v].segments[k];
            std::fprintf(f, "%zu,%zu,%.2f,%.2f,%.3f,%.3f,%d,%.3f\n", v, k, s.x, s.y,
                         s.lengthM, s.speedMps, s.turning, t);
            t += s.speedMps > 0 ? s.lengthM / s.speedMps : 0.0;
        }
    }
    std::fclose(f);

    // --- stage-by-stage state, for the step-through visualiser -------------
    // Each stage writes what it DECIDED, so the viewer shows the plan being
    // built rather than a finished plan with labels on it.
    f = open("stage_partition.csv");
    std::fprintf(f, "cellId,vehicle\n");
    for (size_t v = 0; v < pl.partition.vehicles.size(); ++v)
        for (int32_t c : pl.partition.vehicles[v].cells)
            std::fprintf(f, "%d,%zu\n", c, v);
    std::fclose(f);

    // Both tours, sampled as polylines: what nearest neighbour produced and what
    // the local search made of it. Sampling here rather than in the viewer keeps
    // ONE Dubins implementation in the system.
    auto emitTour = [&](FILE* fp, size_t v, const char* variant, const Tour& t) {
        Config prev = t.depot;
        uint32_t seq = 0;
        auto arc = [&](const Config& a, const Config& b) {
            const DubinsPath dp = Dubins(a, b, rho);
            if (!dp.valid) return;
            const int n = std::max(2, (int)std::ceil(dp.length / 12.0));
            for (int k = 0; k <= n; ++k) {
                const Config c = Integrate(a, dp, rho, (double)k / n);
                std::fprintf(fp, "%zu,%s,%u,%.2f,%.2f\n", v, variant, seq++, c.x, c.y);
            }
        };
        for (const Leg& l : t.legs) { arc(prev, l.cfg); prev = l.cfg; }
        arc(prev, t.depot);
    };
    f = open("stage_tours.csv");
    std::fprintf(f, "vehicle,variant,seq,x,y\n");
    for (size_t v = 0; v < pl.partition.vehicles.size(); ++v) {
        const auto& cells2 = pl.partition.vehicles[v].cells;
        emitTour(f, v, "nn", SeedTour(cells2, pl.bestDemands, depot, rho));
        emitTour(f, v, "opt", pl.tours[v]);
    }
    std::fclose(f);

    // The heading grid each cell was discretised into, and which one T2 chose.
    f = open("stage_headings.csv");
    std::fprintf(f, "vehicle,cellId,k,hdgDeg,chosen\n");
    for (size_t v = 0; v < pl.tours.size(); ++v)
        for (const Leg& l : pl.tours[v].legs) {
            const double chosen = l.cfg.hdg * 180.0 / M_PI;
            for (uint32_t k = 0; k < kHeadingSamples; ++k) {
                const double hd = 360.0 * k / kHeadingSamples;
                double diff = std::fabs(hd - chosen);
                if (diff > 180) diff = 360 - diff;
                std::fprintf(f, "%zu,%d,%u,%.1f,%d\n", v, l.cellId, k, hd, diff < 1.0);
            }
        }
    std::fclose(f);

    // Tour lengths per stage, so the viewer can state what each step bought.
    f = open("stage_cost.csv");
    std::fprintf(f, "vehicle,nnM,optM,serviceS,speedTimeS,feasible\n");
    for (size_t v = 0; v < pl.tours.size(); ++v) {
        const Tour nn = SeedTour(pl.partition.vehicles[v].cells, pl.bestDemands, depot, rho);
        std::fprintf(f, "%zu,%.2f,%.2f,%.2f,%.2f,%d\n", v, nn.flightM,
                     pl.tours[v].flightM, pl.tours[v].serviceS,
                     pl.speeds[v].solved ? pl.speeds[v].totalTimeS : 0.0,
                     pl.speeds[v].solved);
    }
    std::fclose(f);

    f = open("history.csv");
    std::fprintf(f, "iteration,makespanS,flightM,planCells,serving,retired,infeasible,uncovered,valid\n");
    for (const RefineStep& st : pl.history)
        std::fprintf(f, "%u,%.2f,%.2f,%u,%u,%u,%u,%u,%d\n", st.iteration, st.makespanS,
                     st.flightM, st.planCells, st.servedCells, st.droppedBySurplus,
                     st.infeasibleVehicles, st.uncovered, st.selfConsistent);
    std::fclose(f);

    std::printf("%s: %zu cells (A=%u B=%u C=%u), |D|=%zu, %u vehicles, "
                "makespan %.0fs, %s\n", dir.c_str(), plan.cells.size(), plan.nA,
                plan.nB, plan.nC, t1.suspects.size(), M, pl.makespanS,
                pl.feasible ? "valid plan" : "NO VALID PLAN");
    return 0;
}
