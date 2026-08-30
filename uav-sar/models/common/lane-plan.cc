#include "lane-plan.h"

#include <algorithm>
#include <cmath>
#include <limits>

namespace ns3::uavsar {

using ns3::Vector;

namespace {

constexpr double kTwoPi = 2.0 * M_PI;

double Mod2Pi(double t) { return t - kTwoPi * std::floor(t / kTwoPi); }

struct Word { double t, p, q; bool ok; };

Word Lsl(double a, double b, double d) {
    double tmp = std::atan2(std::cos(b) - std::cos(a), d + std::sin(a) - std::sin(b));
    double ps = 2 + d * d - 2 * std::cos(a - b) + 2 * d * (std::sin(a) - std::sin(b));
    if (ps < 0) return {0, 0, 0, false};
    return {Mod2Pi(tmp - a), std::sqrt(ps), Mod2Pi(b - tmp), true};
}
Word Rsr(double a, double b, double d) {
    double tmp = std::atan2(std::cos(a) - std::cos(b), d - std::sin(a) + std::sin(b));
    double ps = 2 + d * d - 2 * std::cos(a - b) + 2 * d * (std::sin(b) - std::sin(a));
    if (ps < 0) return {0, 0, 0, false};
    return {Mod2Pi(a - tmp), std::sqrt(ps), Mod2Pi(tmp - b), true};
}
Word Lsr(double a, double b, double d) {
    double ps = -2 + d * d + 2 * std::cos(a - b) + 2 * d * (std::sin(a) + std::sin(b));
    if (ps < 0) return {0, 0, 0, false};
    double p = std::sqrt(ps);
    double tmp = std::atan2(-std::cos(a) - std::cos(b), d + std::sin(a) + std::sin(b)) -
                 std::atan2(-2.0, p);
    return {Mod2Pi(tmp - a), p, Mod2Pi(tmp - Mod2Pi(b)), true};
}
Word Rsl(double a, double b, double d) {
    double ps = -2 + d * d + 2 * std::cos(a - b) - 2 * d * (std::sin(a) + std::sin(b));
    if (ps < 0) return {0, 0, 0, false};
    double p = std::sqrt(ps);
    double tmp = std::atan2(std::cos(a) + std::cos(b), d - std::sin(a) - std::sin(b)) -
                 std::atan2(2.0, p);
    return {Mod2Pi(a - tmp), p, Mod2Pi(Mod2Pi(b) - tmp), true};
}

// CCC is built geometrically, not from a remembered closed form: the textbook
// LRL/RLR expressions are easy to transcribe with one sign wrong, and a wrong
// one still returns plausible LENGTHS. The Python twin of this file had exactly
// that bug (208 m endpoint error on LRL while the other five words were exact),
// caught only by integrating the control word back to its endpoint.
Word Ccc(double a, double b, double d, bool leftOuter) {
    const double s = leftOuter ? 1.0 : -1.0;
    const double p1x = 0.0, p1y = 0.0, p2x = d, p2y = 0.0;
    const double c1x = p1x - s * std::sin(a), c1y = p1y + s * std::cos(a);
    const double c3x = p2x - s * std::sin(b), c3y = p2y + s * std::cos(b);
    const double vx = c3x - c1x, vy = c3y - c1y;
    const double D = std::hypot(vx, vy);
    if (D > 4.0 || D < 1e-12) return {0, 0, 0, false};
    const double theta = std::atan2(vy, vx), phi = std::acos(D / 4.0);
    Word best{0, 0, 0, false};
    double bestLen = std::numeric_limits<double>::infinity();
    for (double sign : {1.0, -1.0}) {
        const double ang = theta + sign * phi;
        const double c2x = c1x + 2 * std::cos(ang), c2y = c1y + 2 * std::sin(ang);
        const double t = Mod2Pi(s * (std::atan2(c2y - c1y, c2x - c1x) -
                                     std::atan2(p1y - c1y, p1x - c1x)));
        const double p = Mod2Pi(-s * (std::atan2(c3y - c2y, c3x - c2x) -
                                      std::atan2(c1y - c2y, c1x - c2x)));
        const double q = Mod2Pi(s * (std::atan2(p2y - c3y, p2x - c3x) -
                                     std::atan2(c2y - c3y, c2x - c3x)));
        if (t + p + q < bestLen) { bestLen = t + p + q; best = {t, p, q, true}; }
    }
    return best;
}

}  // namespace

double DubinsLength(double x0, double y0, double h0,
                    double x1, double y1, double h1, double R) {
    const double dx = x1 - x0, dy = y1 - y0;
    const double D = std::hypot(dx, dy);
    const double d = D / R;
    const double th = D > 1e-12 ? Mod2Pi(std::atan2(dy, dx)) : 0.0;
    const double a = Mod2Pi(h0 - th), b = Mod2Pi(h1 - th);
    double best = std::numeric_limits<double>::infinity();
    const Word ws[6] = {Lsl(a, b, d), Rsr(a, b, d), Lsr(a, b, d),
                        Rsl(a, b, d), Ccc(a, b, d, false), Ccc(a, b, d, true)};
    for (const Word& w : ws)
        if (w.ok) best = std::min(best, w.t + w.p + w.q);
    return best * R;
}

std::vector<Lane> BuildFieldLanes(const std::vector<Vector>& sensors,
                                  double spacing, double alt) {
    std::vector<Lane> lanes;
    if (sensors.empty() || spacing <= 0) return lanes;
    double x0 = sensors[0].x, x1 = x0, y0 = sensors[0].y, y1 = y0;
    for (const Vector& s : sensors) {
        x0 = std::min(x0, s.x); x1 = std::max(x1, s.x);
        y0 = std::min(y0, s.y); y1 = std::max(y1, s.y);
    }
    const bool alongX = (x1 - x0) >= (y1 - y0);
    const double across0 = alongX ? y0 : x0, across1 = alongX ? y1 : x1;
    const double along0 = alongX ? x0 : y0, along1 = alongX ? x1 : y1;
    const int n = std::max(1, (int)std::ceil((across1 - across0) / spacing) + 1);
    for (int i = 0; i < n; ++i) {
        const double a = std::min(across0 + i * spacing, across1);
        lanes.push_back(alongX ? Lane{Vector(along0, a, alt), Vector(along1, a, alt)}
                               : Lane{Vector(a, along0, alt), Vector(a, along1, alt)});
    }
    return lanes;
}

std::vector<Lane> LanesFor(const std::vector<Lane>& all, uint32_t idx, uint32_t count) {
    if (count == 0) return {};
    const size_t n = all.size();
    const size_t lo = n * idx / count, hi = n * (idx + 1) / count;
    return std::vector<Lane>(all.begin() + lo, all.begin() + hi);
}

std::vector<Vector> OrderLanes(const std::vector<Lane>& lanes,
                               double R, Vector start) {
    const uint32_t n = (uint32_t)lanes.size();
    std::vector<Vector> out;
    if (n == 0) return out;

    auto heading = [](const Vector& from, const Vector& to) {
        return std::atan2(to.y - from.y, to.x - from.x);
    };
    // Each lane has two modes: fly a->b or b->a.
    auto entry = [&](uint32_t i, int d) { return d == 0 ? lanes[i].a : lanes[i].b; };
    auto exit_ = [&](uint32_t i, int d) { return d == 0 ? lanes[i].b : lanes[i].a; };
    auto entryH = [&](uint32_t i, int d) {
        return d == 0 ? heading(lanes[i].a, lanes[i].b) : heading(lanes[i].b, lanes[i].a);
    };

    auto emit = [&](const std::vector<std::pair<uint32_t, int>>& order) {
        for (auto [i, d] : order) { out.push_back(entry(i, d)); out.push_back(exit_(i, d)); }
    };

    if (n > kExactLaneLimit) {                       // fall back to index order
        std::vector<std::pair<uint32_t, int>> order;
        for (uint32_t i = 0; i < n; ++i) order.push_back({i, (int)(i % 2)});
        emit(order);
        return out;
    }

    auto laneLen = [&](uint32_t i) {
        return std::hypot(lanes[i].b.x - lanes[i].a.x, lanes[i].b.y - lanes[i].a.y);
    };
    auto hop = [&](uint32_t i, int di, uint32_t j, int dj) {
        const Vector e = exit_(i, di);
        return DubinsLength(e.x, e.y, entryH(i, di),
                            entry(j, dj).x, entry(j, dj).y, entryH(j, dj), R);
    };

    const uint32_t full = 1u << n;
    const double INF = std::numeric_limits<double>::infinity();
    std::vector<double> dp((size_t)full * n * 2, INF);
    std::vector<int> par((size_t)full * n * 2, -1);
    auto at = [&](uint32_t mask, uint32_t i, int d) { return ((size_t)mask * n + i) * 2 + d; };

    const double sh = heading(start, lanes[0].a);    // heading into the field
    for (uint32_t i = 0; i < n; ++i)
        for (int d = 0; d < 2; ++d)
            dp[at(1u << i, i, d)] =
                DubinsLength(start.x, start.y, sh, entry(i, d).x, entry(i, d).y,
                             entryH(i, d), R) + laneLen(i);

    for (uint32_t mask = 1; mask < full; ++mask)
        for (uint32_t i = 0; i < n; ++i) {
            if (!(mask & (1u << i))) continue;
            for (int di = 0; di < 2; ++di) {
                const double cur = dp[at(mask, i, di)];
                if (cur == INF) continue;
                for (uint32_t j = 0; j < n; ++j) {
                    if (mask & (1u << j)) continue;
                    const uint32_t nm = mask | (1u << j);
                    for (int dj = 0; dj < 2; ++dj) {
                        const double cand = cur + hop(i, di, j, dj) + laneLen(j);
                        if (cand < dp[at(nm, j, dj)] - 1e-9) {
                            dp[at(nm, j, dj)] = cand;
                            par[at(nm, j, dj)] = (int)(i * 2 + di);
                        }
                    }
                }
            }
        }

    double best = INF; uint32_t bi = 0; int bd = 0;
    for (uint32_t i = 0; i < n; ++i)
        for (int d = 0; d < 2; ++d)
            if (dp[at(full - 1, i, d)] < best) { best = dp[at(full - 1, i, d)]; bi = i; bd = d; }

    std::vector<std::pair<uint32_t, int>> order;
    uint32_t mask = full - 1, i = bi; int d = bd;
    while (true) {
        order.push_back({i, d});
        const int pr = par[at(mask, i, d)];
        if (pr < 0) break;
        mask &= ~(1u << i);
        i = (uint32_t)(pr / 2); d = pr % 2;
    }
    std::reverse(order.begin(), order.end());
    emit(order);
    return out;
}

}  // namespace ns3::uavsar
