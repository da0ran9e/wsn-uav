#ifndef UAV_SAR_GMC_H
#define UAV_SAR_GMC_H

// Greedy Maximum Coverage waypoint planner: pick sensor positions (lifted to
// cruise altitude) that greedily cover all sensors within a broadcast radius,
// biased toward nearby picks. Header-only so UAV apps share one implementation.

#include "ns3/vector.h"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <vector>

namespace ns3::uavsar {

inline std::vector<ns3::Vector> BuildGmc(const std::vector<ns3::Vector>& sensors,
                                         double radius, ns3::Vector start,
                                         double alt, double speed) {
    std::vector<ns3::Vector> targets;
    const size_t N = sensors.size();
    if (N == 0 || radius <= 0) return targets;
    const double r2 = radius * radius;
    std::vector<std::vector<uint32_t>> cov(N);
    for (size_t i = 0; i < N; i++)
        for (size_t j = 0; j < N; j++) {
            double dx = sensors[i].x - sensors[j].x, dy = sensors[i].y - sensors[j].y;
            if (dx * dx + dy * dy <= r2) cov[i].push_back((uint32_t)j);
        }
    std::vector<bool> covered(N, false), used(N, false);
    size_t cc = 0;
    ns3::Vector last = start;
    while (cc < N) {
        double bs = -1; int bi = -1;
        for (size_t i = 0; i < N; i++) {
            if (used[i]) continue;
            uint32_t g = 0; for (uint32_t s : cov[i]) if (!covered[s]) g++;
            if (!g) continue;
            double d = std::hypot(sensors[i].x - last.x, sensors[i].y - last.y);
            double sc = g / (1.0 + d / speed);
            if (sc > bs) { bs = sc; bi = (int)i; }
        }
        if (bi < 0) break;
        ns3::Vector wp(sensors[bi].x, sensors[bi].y, alt);
        targets.push_back(wp); used[bi] = true;
        for (uint32_t s : cov[bi]) if (!covered[s]) { covered[s] = true; cc++; }
        last = wp;
    }
    return targets;
}

// Zeng-Xu-Zhang (TWC 2018) style multicast trajectory: (1) VBS placement —
// cover ALL ground terminals with a minimum set of disks of the coverage
// radius (greedy set-cover over candidate centres at the GT positions),
// (2) order the VBSs as a TSP tour from the start point (nearest-neighbour +
// 2-opt), to be flown fly-hover with a per-VBS connection-time dwell. Used by
// the "tsp-mc" baseline (their scheme adapted to our mission: the UAV must
// still return to the BS and report to complete).
inline std::vector<ns3::Vector> BuildVbsTour(const std::vector<ns3::Vector>& gts,
                                             double radius, ns3::Vector start,
                                             double alt) {
    std::vector<ns3::Vector> vbs;
    const size_t N = gts.size();
    if (N == 0 || radius <= 0) return vbs;
    const double r2 = radius * radius;
    // 1) greedy disk cover: repeatedly pick the candidate centre covering the
    //    most uncovered GTs (tie -> lowest index).
    std::vector<bool> covered(N, false);
    size_t cc = 0;
    while (cc < N) {
        int best = -1; uint32_t bestGain = 0;
        for (size_t i = 0; i < N; i++) {
            uint32_t g = 0;
            for (size_t j = 0; j < N; j++) {
                if (covered[j]) continue;
                double dx = gts[i].x - gts[j].x, dy = gts[i].y - gts[j].y;
                if (dx * dx + dy * dy <= r2) g++;
            }
            if (g > bestGain) { bestGain = g; best = (int)i; }
        }
        if (best < 0) break;
        vbs.push_back(ns3::Vector(gts[best].x, gts[best].y, alt));
        for (size_t j = 0; j < N; j++) {
            double dx = gts[best].x - gts[j].x, dy = gts[best].y - gts[j].y;
            if (dx * dx + dy * dy <= r2) { if (!covered[j]) { covered[j] = true; cc++; } }
        }
    }
    // 2) TSP order from the start: nearest-neighbour construction...
    const size_t G = vbs.size();
    std::vector<ns3::Vector> tour;
    std::vector<bool> used(G, false);
    ns3::Vector cur = start;
    for (size_t k = 0; k < G; k++) {
        int bi = -1; double bd = 0;
        for (size_t i = 0; i < G; i++) {
            if (used[i]) continue;
            double d = std::hypot(vbs[i].x - cur.x, vbs[i].y - cur.y);
            if (bi < 0 || d < bd) { bd = d; bi = (int)i; }
        }
        used[bi] = true; tour.push_back(vbs[bi]); cur = vbs[bi];
    }
    // ...then 2-opt improvement (open path start -> ... -> last).
    auto dist = [](const ns3::Vector& a, const ns3::Vector& b) {
        return std::hypot(a.x - b.x, a.y - b.y);
    };
    bool improved = true;
    while (improved && G >= 3) {
        improved = false;
        for (size_t i = 0; i + 1 < G; i++) {
            for (size_t j = i + 1; j < G; j++) {
                const ns3::Vector& A = i == 0 ? start : tour[i - 1];
                double before = dist(A, tour[i]) + (j + 1 < G ? dist(tour[j], tour[j + 1]) : 0);
                double after  = dist(A, tour[j]) + (j + 1 < G ? dist(tour[i], tour[j + 1]) : 0);
                if (after + 1e-9 < before) {
                    std::reverse(tour.begin() + i, tour.begin() + j + 1);
                    improved = true;
                }
            }
        }
    }
    return tour;
}

}  // namespace ns3::uavsar

#endif  // UAV_SAR_GMC_H
