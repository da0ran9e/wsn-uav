#include "p1-route.h"

#include <algorithm>
#include <cmath>
#include <limits>

namespace ns3::uavsar::p1 {

namespace {

constexpr double kInf = std::numeric_limits<double>::infinity();

double HeadingOf(uint32_t k, uint32_t h) { return 2.0 * M_PI * k / h; }

}  // namespace

Tour BestHeadings(const std::vector<int32_t>& order,
                  const std::map<int32_t, Demand>& demands,
                  const Config& depot, double R, uint32_t h) {
    Tour t;
    t.depot = depot;
    if (order.empty() || h == 0) return t;
    const size_t n = order.size();

    // dp[i][a] = least metres to arrive at cell i on heading a, having visited
    // i+1 cells in the given order. Exact: the order is fixed, so the only
    // remaining choice is the heading, and it decomposes.
    std::vector<std::vector<double>> dp(n, std::vector<double>(h, kInf));
    std::vector<std::vector<int32_t>> par(n, std::vector<int32_t>(h, -1));
    for (uint32_t a = 0; a < h; ++a) {
        const Demand& d = demands.at(order[0]);
        dp[0][a] = DubinsLength(depot, Config{d.x, d.y, HeadingOf(a, h)}, R);
    }
    for (size_t i = 1; i < n; ++i) {
        const Demand& prev = demands.at(order[i - 1]);
        const Demand& cur = demands.at(order[i]);
        for (uint32_t b = 0; b < h; ++b) {
            const Config to{cur.x, cur.y, HeadingOf(b, h)};
            for (uint32_t a = 0; a < h; ++a) {
                if (dp[i - 1][a] == kInf) continue;
                const double c = dp[i - 1][a] +
                    DubinsLength(Config{prev.x, prev.y, HeadingOf(a, h)}, to, R);
                if (c < dp[i][b]) { dp[i][b] = c; par[i][b] = (int32_t)a; }
            }
        }
    }
    // close the tour at the depot
    double best = kInf;
    int32_t bestA = 0;
    const Demand& last = demands.at(order[n - 1]);
    for (uint32_t a = 0; a < h; ++a) {
        if (dp[n - 1][a] == kInf) continue;
        const double c = dp[n - 1][a] +
            DubinsLength(Config{last.x, last.y, HeadingOf(a, h)}, depot, R);
        if (c < best) { best = c; bestA = (int32_t)a; }
    }
    if (best == kInf) return t;

    std::vector<uint32_t> pick(n, 0);
    int32_t a = bestA;
    for (size_t i = n; i-- > 0;) { pick[i] = (uint32_t)a; a = par[i][a]; if (a < 0) a = 0; }

    Config prevCfg = depot;
    for (size_t i = 0; i < n; ++i) {
        const Demand& d = demands.at(order[i]);
        Leg l;
        l.cellId = order[i];
        l.cfg = Config{d.x, d.y, HeadingOf(pick[i], h)};
        l.fromPrevM = DubinsLength(prevCfg, l.cfg, R);
        t.legs.push_back(l);
        t.serviceS += d.penaltyS;
        prevCfg = l.cfg;
    }
    t.flightM = best;
    return t;
}

namespace {
// nearest neighbour on Euclidean distance, only as a starting order
std::vector<int32_t> NnOrder(const std::vector<int32_t>& cells,
                             const std::map<int32_t, Demand>& demands,
                             const Config& depot) {
    std::vector<int32_t> order, left = cells;
    double cx = depot.x, cy = depot.y;
    while (!left.empty()) {
        size_t best = 0;
        double bd = kInf;
        for (size_t i = 0; i < left.size(); ++i) {
            const Demand& d = demands.at(left[i]);
            const double dd = std::hypot(d.x - cx, d.y - cy);
            if (dd < bd) { bd = dd; best = i; }
        }
        order.push_back(left[best]);
        cx = demands.at(left[best]).x;
        cy = demands.at(left[best]).y;
        left.erase(left.begin() + best);
    }
    return order;
}
}  // namespace

Tour SeedTour(const std::vector<int32_t>& cells,
              const std::map<int32_t, Demand>& demands,
              const Config& depot, double R, uint32_t h) {
    if (cells.empty()) { Tour t; t.depot = depot; return t; }
    return BestHeadings(NnOrder(cells, demands, depot), demands, depot, R, h);
}

Tour SolveTour(const std::vector<int32_t>& cells,
               const std::map<int32_t, Demand>& demands,
               const Config& depot, double R, uint32_t h) {
    if (cells.empty()) { Tour t; t.depot = depot; return t; }
    std::vector<int32_t> order = NnOrder(cells, demands, depot);

    // Every candidate order is scored by the SAME exact heading DP that will be
    // used for the answer. Scoring candidates on a cheaper proxy and the winner
    // on the real cost is how a planner ends up confidently choosing the worse
    // of two orders.
    auto score = [&](const std::vector<int32_t>& o) {
        return BestHeadings(o, demands, depot, R, h).flightM;
    };
    double cur = score(order);
    const size_t n = order.size();
    bool improved = true;
    int guard = 0;
    while (improved && guard++ < 50) {
        improved = false;
        for (size_t i = 0; i + 1 < n && !improved; ++i)
            for (size_t j = i + 1; j < n && !improved; ++j) {
                std::vector<int32_t> cand = order;
                std::reverse(cand.begin() + i, cand.begin() + j + 1);   // 2-opt
                const double s = score(cand);
                if (s < cur - 1e-9) { order = cand; cur = s; improved = true; }
            }
        for (size_t i = 0; i < n && !improved; ++i)
            for (size_t j = 0; j < n && !improved; ++j) {
                if (i == j) continue;
                std::vector<int32_t> cand = order;                       // Or-opt(1)
                const int32_t v = cand[i];
                cand.erase(cand.begin() + i);
                cand.insert(cand.begin() + (j > i ? j - 1 : j), v);
                const double s = score(cand);
                if (s < cur - 1e-9) { order = cand; cur = s; improved = true; }
            }
    }
    return BestHeadings(order, demands, depot, R, h);
}

}  // namespace ns3::uavsar::p1
