#ifndef UAV_SAR_GMC_H
#define UAV_SAR_GMC_H

// Greedy Maximum Coverage waypoint planner: pick sensor positions (lifted to
// cruise altitude) that greedily cover all sensors within a broadcast radius,
// biased toward nearby picks. Header-only so UAV apps share one implementation.

#include "ns3/vector.h"

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

}  // namespace ns3::uavsar

#endif  // UAV_SAR_GMC_H
