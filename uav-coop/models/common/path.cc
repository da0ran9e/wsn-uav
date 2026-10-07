#include "path.h"

#include <cmath>
#include <limits>

namespace ns3::uavcoop {

namespace {

constexpr int kGrid = 360;   // 1 degree

double Cost(const std::vector<Point>& p, const std::vector<double>& th, double rho) {
    double c = 0;
    for (size_t i = 0; i + 1 < p.size(); ++i)
        c += DubinsShortest({p[i].x, p[i].y, th[i]}, {p[i + 1].x, p[i + 1].y, th[i + 1]}, rho).Length();
    return c;
}

}  // namespace

Path PlanPath(const std::vector<Point>& p, double rho, const std::vector<HeadingOk>& ok) {
    const size_t n = p.size();
    const double step = 2 * M_PI / kGrid;
    const double inf = std::numeric_limits<double>::infinity();
    auto allowed = [&](size_t i, double th) { return !ok[i] || ok[i](th); };
    std::vector<std::vector<bool>> on(n, std::vector<bool>(kGrid));
    for (size_t i = 0; i < n; ++i)
        for (int a = 0; a < kGrid; ++a) on[i][a] = allowed(i, a * step);
    // Dynamic programme along the chain over the allowed grid headings.
    std::vector<std::vector<double>> D(n, std::vector<double>(kGrid, inf));
    std::vector<std::vector<int>> arg(n, std::vector<int>(kGrid, -1));
    for (int a = 0; a < kGrid; ++a)
        if (on[0][a]) D[0][a] = 0;
    for (size_t i = 1; i < n; ++i)
        for (int b = 0; b < kGrid; ++b) {
            if (!on[i][b]) continue;
            for (int a = 0; a < kGrid; ++a) {
                if (D[i - 1][a] == inf) continue;
                const double c = D[i - 1][a] + DubinsShortest({p[i - 1].x, p[i - 1].y, a * step},
                                                              {p[i].x, p[i].y, b * step}, rho).Length();
                if (c < D[i][b]) { D[i][b] = c; arg[i][b] = a; }
            }
        }
    int last = -1;
    for (int b = 0; b < kGrid; ++b)
        if (D[n - 1][b] < inf && (last < 0 || D[n - 1][b] < D[n - 1][last])) last = b;
    Path out;
    if (last < 0) return out;
    out.gridLength = D[n - 1][last];
    std::vector<double> th(n);
    for (size_t i = n, h = last; i-- > 0;) {
        th[i] = h * step;
        if (i > 0) h = arg[i][h];
    }
    // Coordinate descent: step from 1 degree down to 0.01 degree.
    double c = Cost(p, th, rho);
    for (double d = step; d > step / 100; d /= 2)
        for (bool moved = true; moved;) {
            moved = false;
            for (size_t i = 0; i < n; ++i)
                for (double s : {d, -d}) {
                    std::vector<double> t2 = th;
                    t2[i] = Mod2Pi(t2[i] + s);
                    if (!allowed(i, t2[i])) continue;
                    const double c2 = Cost(p, t2, rho);
                    if (c2 < c - 1e-9) { c = c2; th = t2; moved = true; }
                }
        }
    out.length = c;
    for (size_t i = 0; i < n; ++i) out.poses.push_back({p[i].x, p[i].y, th[i]});
    for (size_t i = 0; i + 1 < n; ++i) out.legs.push_back(DubinsShortest(out.poses[i], out.poses[i + 1], rho));
    return out;
}

}  // namespace ns3::uavcoop
