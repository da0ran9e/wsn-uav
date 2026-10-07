#include "tour.h"

#include <algorithm>
#include <cmath>
#include <limits>

namespace ns3::uavcoop {

namespace {

constexpr int kGrid = 360;   // 1 degree

double Leg(const Point& a, double ta, const Point& b, double tb, double rho) {
    return DubinsShortest({a.x, a.y, ta}, {b.x, b.y, tb}, rho).Length();
}

double Cost(const std::vector<Point>& p, const std::vector<double>& th, double rho, bool closed) {
    double c = 0;
    const size_t n = p.size();
    for (size_t i = 0; i + 1 < n; ++i) c += Leg(p[i], th[i], p[i + 1], th[i + 1], rho);
    if (closed && n > 1) c += Leg(p[n - 1], th[n - 1], p[0], th[0], rho);
    return c;
}

// Best headings for one visiting order: exhaustive on the grid, then refine.
std::pair<std::vector<double>, double> BestHeadings(const std::vector<Point>& p, double rho,
                                                    bool closed, double& gridBest) {
    const size_t n = p.size();
    const double step = 2 * M_PI / kGrid;
    // leg[i][a][b]: point i at heading a -> point i+1 (mod n) at heading b
    const size_t legs = closed ? n : n - 1;
    std::vector<std::vector<double>> leg(legs, std::vector<double>(kGrid * kGrid));
    for (size_t i = 0; i < legs; ++i)
        for (int a = 0; a < kGrid; ++a)
            for (int b = 0; b < kGrid; ++b)
                leg[i][a * kGrid + b] = Leg(p[i], a * step, p[(i + 1) % n], b * step, rho);
    // Dynamic programme over the chain; for a loop, once per start heading.
    std::vector<int> best(n, 0);
    double bestC = std::numeric_limits<double>::infinity();
    const int starts = closed ? kGrid : 1;
    for (int h0 = 0; h0 < starts; ++h0) {
        std::vector<std::vector<double>> D(n, std::vector<double>(kGrid, std::numeric_limits<double>::infinity()));
        std::vector<std::vector<int>> arg(n, std::vector<int>(kGrid, -1));
        for (int a = 0; a < kGrid; ++a)
            if (!closed || a == h0) D[0][a] = 0;
        for (size_t i = 1; i < n; ++i)
            for (int b = 0; b < kGrid; ++b)
                for (int a = 0; a < kGrid; ++a) {
                    const double c = D[i - 1][a] + leg[i - 1][a * kGrid + b];
                    if (c < D[i][b]) { D[i][b] = c; arg[i][b] = a; }
                }
        for (int b = 0; b < kGrid; ++b) {
            const double c = D[n - 1][b] + (closed ? leg[n - 1][b * kGrid + h0] : 0.0);
            if (c < bestC) {
                bestC = c;
                std::vector<int> h(n);
                h[n - 1] = b;
                for (size_t i = n - 1; i > 0; --i) h[i - 1] = arg[i][h[i]];
                best = h;
            }
        }
    }
    gridBest = bestC;
    std::vector<double> th(n);
    for (size_t i = 0; i < n; ++i) th[i] = best[i] * step;
    // Coordinate descent: step from 1 degree down to 0.01 degree.
    double c = Cost(p, th, rho, closed);
    for (double d = step; d > step / 100; d /= 2)
        for (bool moved = true; moved;) {
            moved = false;
            for (size_t i = 0; i < n; ++i)
                for (double s : {d, -d}) {
                    std::vector<double> t2 = th;
                    t2[i] = Mod2Pi(t2[i] + s);
                    const double c2 = Cost(p, t2, rho, closed);
                    if (c2 < c - 1e-9) { c = c2; th = t2; moved = true; }
                }
        }
    return {th, c};
}

}  // namespace

Tour PlanTour(const std::vector<Point>& pts, double rho, bool closed) {
    Tour best;
    best.closed = closed;
    best.length = std::numeric_limits<double>::infinity();
    std::vector<int> ord(pts.size());
    for (size_t i = 0; i < ord.size(); ++i) ord[i] = (int)i;
    do {
        // A loop is the same from any starting point: fix point 0 first.
        if (closed && ord[0] != 0) continue;
        std::vector<Point> p;
        for (int i : ord) p.push_back(pts[i]);
        double grid = 0;
        auto [th, c] = BestHeadings(p, rho, closed, grid);
        if (c < best.length) {
            best.length = c;
            best.gridLength = grid;
            best.order = ord;
            best.poses.clear();
            for (size_t i = 0; i < p.size(); ++i) best.poses.push_back({p[i].x, p[i].y, th[i]});
        }
    } while (std::next_permutation(ord.begin(), ord.end()));
    best.legs.clear();
    const size_t n = best.poses.size();
    for (size_t i = 0; i + 1 < n; ++i) best.legs.push_back(DubinsShortest(best.poses[i], best.poses[i + 1], rho));
    if (closed && n > 1) best.legs.push_back(DubinsShortest(best.poses[n - 1], best.poses[0], rho));
    return best;
}

}  // namespace ns3::uavcoop
