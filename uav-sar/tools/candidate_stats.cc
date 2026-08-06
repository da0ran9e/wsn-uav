// Đo TẬP ỨNG VIÊN do ROC của bộ phát hiện sinh ra: có bao nhiêu điểm yêu cầu
// tách biệt về không gian, và mỗi điểm cách nạn nhân thật bao xa.
//
// Dùng chính ClueField + CellGrid của dự án (cả hai đều độc lập ns-3), nên số
// liệu là số liệu mà bộ mô phỏng sẽ nhìn thấy — không phải mô hình xấp xỉ viết
// lại. Vị trí nạn nhân được sinh bằng đúng chuỗi RNG của `SarScenario::Build`.
//
// Build:
//   g++ -O2 -std=c++17 -o candidate_stats tools/candidate_stats.cc \
//       models/common/clue-field.cc models/common/cell-grid.cc
// Run:
//   ./candidate_stats <grid> <senseSigma> <seeds> [maxNoiseQuality] [bgFpRate]
//
// "Ứng viên" = một thành phần liên thông (single-linkage ở tầm liên kết mặt đất
// ~37 m) của các nút vượt ngưỡng ALERT. Đó chính là mức mà một lãnh đạo ô có thể
// được bầu và phát SUMMON, nên đếm thành phần chứ không đếm nút là đúng đơn vị.
// "Mồi nhử" (decoy) = ứng viên cách nạn nhân thật > 60 m.

#include "../models/common/cell-grid.h"
#include "../models/common/clue-field.h"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <map>
#include <random>
#include <set>
#include <string>
#include <vector>

using namespace ns3::uavsar;

struct Comp { double px, py, peakQ; int n; double distVictim; };

int main(int argc, char** argv) {
    uint32_t grid   = (argc > 1) ? std::stoul(argv[1]) : 16;
    double sigma    = (argc > 2) ? std::stod(argv[2])  : 0.10;
    uint32_t nSeeds = (argc > 3) ? std::stoul(argv[3]) : 120;
    const double spacing = 20.0;
    const double alert = 0.75, coop = 0.30;
    const double linkRange = 37.0;   // ~params::DeriveG2gRangeM()
    const double decoyRadius = 60.0;

    std::vector<CluePos> nodes;
    std::vector<NodePos> npos;
    uint32_t id = 2;                 // BS=0, UAV=1 theo quy ước node id
    for (uint32_t i = 0; i < grid; ++i)
        for (uint32_t j = 0; j < grid; ++j) {
            double x = i * spacing, y = j * spacing;
            nodes.push_back({id, x, y});
            npos.push_back({id, x, y});
            id++;
        }
    CellGridConfig cg;
    cg.cellRadius = 80.0;
    cg.neighborRange = linkRange;
    auto plan = BuildCellGrid(npos, cg);

    std::vector<int> kAlertNodes, kComps, kCoopNodes, kAlertCells, kDecoyComps;
    std::vector<double> nearestDecoyD, peakErr, farthestCompD;
    int seedsNoAlert = 0;

    for (uint32_t s = 1; s <= nSeeds; ++s) {
        // đúng chuỗi RNG của SarScenario::Build (victimOnNode=0)
        std::mt19937 trng(s);
        uint32_t tIdx = trng() % nodes.size();
        double vx = nodes[tIdx].x, vy = nodes[tIdx].y;
        std::uniform_real_distribution<double> off(-0.5 * spacing, 0.5 * spacing);
        vx += off(trng);
        vy += off(trng);
        uint32_t targetId = nodes[tIdx].id;
        double best = 1e18;
        for (auto& n : nodes) {
            double d = std::hypot(n.x - vx, n.y - vy);
            if (d < best) { best = d; targetId = n.id; }
        }

        ClueFieldConfig cc;
        cc.targetNodeId = targetId;
        cc.seed = s;
        cc.victimX = vx;
        cc.victimY = vy;
        cc.senseSigma = sigma;
        if (argc > 4) cc.maxNoiseQuality = std::stod(argv[4]);
        if (argc > 5) cc.bgFalsePositiveRate = std::stod(argv[5]);
        auto field = BuildClueField(nodes, cc);

        std::vector<ClueInfo> hot;
        int nCoop = 0;
        for (auto& kv : field) {
            if (kv.second.clueQuality >= coop) nCoop++;
            if (kv.second.clueQuality >= alert) hot.push_back(kv.second);
        }
        kAlertNodes.push_back((int)hot.size());
        kCoopNodes.push_back(nCoop);

        std::set<int> cells;
        for (auto& h : hot) {
            auto it = plan.nodes.find(h.id);
            if (it != plan.nodes.end()) cells.insert((int)it->second.cellId);
        }
        kAlertCells.push_back((int)cells.size());

        std::vector<int> lab(hot.size(), -1);
        int nc = 0;
        for (size_t i = 0; i < hot.size(); ++i) {
            if (lab[i] >= 0) continue;
            std::vector<size_t> stack{i};
            lab[i] = nc;
            while (!stack.empty()) {
                size_t u = stack.back();
                stack.pop_back();
                for (size_t v = 0; v < hot.size(); ++v)
                    if (lab[v] < 0 &&
                        std::hypot(hot[u].x - hot[v].x, hot[u].y - hot[v].y) <= linkRange) {
                        lab[v] = nc;
                        stack.push_back(v);
                    }
            }
            nc++;
        }
        kComps.push_back(nc);
        if (nc == 0) { seedsNoAlert++; continue; }

        std::vector<Comp> comps(nc, {0, 0, -1, 0, 0});
        for (size_t i = 0; i < hot.size(); ++i) {
            Comp& c = comps[lab[i]];
            c.n++;
            if (hot[i].clueQuality > c.peakQ) {
                c.peakQ = hot[i].clueQuality;
                c.px = hot[i].x;
                c.py = hot[i].y;
            }
        }
        int decoys = 0;
        double nd = 1e18, fd = 0, truePeakErr = 1e18;
        for (auto& c : comps) {
            c.distVictim = std::hypot(c.px - vx, c.py - vy);
            fd = std::max(fd, c.distVictim);
            if (c.distVictim > decoyRadius) { decoys++; nd = std::min(nd, c.distVictim); }
            else truePeakErr = std::min(truePeakErr, c.distVictim);
        }
        kDecoyComps.push_back(decoys);
        if (decoys) nearestDecoyD.push_back(nd);
        if (truePeakErr < 1e17) peakErr.push_back(truePeakErr);
        farthestCompD.push_back(fd);
    }

    auto med  = [](std::vector<double> v) { if (v.empty()) return -1.0; std::sort(v.begin(), v.end()); return v[v.size()/2]; };
    auto medi = [](std::vector<int> v)    { if (v.empty()) return -1.0; std::sort(v.begin(), v.end()); return (double)v[v.size()/2]; };
    auto mean = [](std::vector<int>& v)   { double t=0; for (int x : v) t += x; return v.empty() ? 0.0 : t/v.size(); };
    auto frac = [](std::vector<int>& v, int t) { int c=0; for (int x : v) if (x >= t) c++; return v.empty() ? 0.0 : 100.0*c/v.size(); };
    auto p90  = [](std::vector<int> v) { if (v.empty()) return -1.0; std::sort(v.begin(), v.end());
                                          size_t i = (size_t)std::ceil(0.9*v.size()); return (double)v[std::min(i, v.size())-1]; };

    printf("grid=%u sigma=%.2f seeds=%u maxNoiseQ=%s\n", grid, sigma, nSeeds, argc > 4 ? argv[4] : "0.18(default)");
    printf("  nut ALERT     : mean %.2f  median %.0f  p90 %.0f\n", mean(kAlertNodes), medi(kAlertNodes), p90(kAlertNodes));
    printf("  nut COOP      : mean %.2f  median %.0f  p90 %.0f\n", mean(kCoopNodes), medi(kCoopNodes), p90(kCoopNodes));
    printf("  ung vien K    : mean %.2f  median %.0f  p90 %.0f  max %d\n", mean(kComps), medi(kComps), p90(kComps),
           kComps.empty() ? 0 : *std::max_element(kComps.begin(), kComps.end()));
    printf("  K>=2: %.1f%%   K>=3: %.1f%%   K==0: %.1f%%\n", frac(kComps, 2), frac(kComps, 3), 100.0*seedsNoAlert/nSeeds);
    printf("  o ALERT       : mean %.2f  p90 %.0f\n", mean(kAlertCells), p90(kAlertCells));
    printf("  moi nhu       : mean %.2f  p90 %.0f  (run co >=1 moi nhu: %.1f%%)\n",
           mean(kDecoyComps), p90(kDecoyComps), frac(kDecoyComps, 1));
    printf("  k/c moi nhu gan nhat : median %.1f m (n=%zu)\n", med(nearestDecoyD), nearestDecoyD.size());
    printf("  k/c ung vien xa nhat : median %.1f m\n", med(farthestCompD));
    printf("  sai so dinh cum that : median %.1f m (n=%zu)\n", med(peakErr), peakErr.size());
    return 0;
}
