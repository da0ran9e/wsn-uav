#include "p1-field.h"

#include <algorithm>
#include <cmath>
#include <limits>

namespace ns3::uavsar::p1 {

namespace {

double Cross(const Point& o, const Point& a, const Point& b) {
    return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x);
}

}  // namespace

std::vector<Point> ConvexHull(std::vector<Point> p) {
    if (p.size() < 3) return p;
    std::sort(p.begin(), p.end(), [](const Point& a, const Point& b) {
        return a.x < b.x || (a.x == b.x && a.y < b.y);
    });
    p.erase(std::unique(p.begin(), p.end(), [](const Point& a, const Point& b) {
                return a.x == b.x && a.y == b.y;
            }), p.end());
    if (p.size() < 3) return p;
    std::vector<Point> h(2 * p.size());
    size_t k = 0;
    for (size_t i = 0; i < p.size(); ++i) {
        while (k >= 2 && Cross(h[k - 2], h[k - 1], p[i]) <= 0) k--;
        h[k++] = p[i];
    }
    for (size_t i = p.size() - 1, t = k + 1; i > 0; --i) {
        while (k >= t && Cross(h[k - 2], h[k - 1], p[i - 1]) <= 0) k--;
        h[k++] = p[i - 1];
    }
    h.resize(k - 1);
    return h;
}

// Douglas-Peucker on a closed polygon: run it on the open chain and keep the
// endpoints. Used before the hull, not after -- simplifying a hull would only
// shrink it, and losing area is losing cells.
std::vector<Point> Simplify(const std::vector<Point>& poly, double tolM) {
    if (poly.size() < 3 || tolM <= 0) return poly;
    std::vector<char> keep(poly.size(), 0);
    keep.front() = keep.back() = 1;
    std::vector<std::pair<size_t, size_t>> stack{{0, poly.size() - 1}};
    while (!stack.empty()) {
        auto [i, j] = stack.back();
        stack.pop_back();
        if (j <= i + 1) continue;
        const Point& a = poly[i];
        const Point& b = poly[j];
        const double dx = b.x - a.x, dy = b.y - a.y;
        const double len = std::hypot(dx, dy);
        size_t worst = i;
        double wd = 0;
        for (size_t k = i + 1; k < j; ++k) {
            const double d = len > 1e-12
                ? std::fabs(dy * (poly[k].x - a.x) - dx * (poly[k].y - a.y)) / len
                : std::hypot(poly[k].x - a.x, poly[k].y - a.y);
            if (d > wd) { wd = d; worst = k; }
        }
        if (wd > tolM) {
            keep[worst] = 1;
            stack.push_back({i, worst});
            stack.push_back({worst, j});
        }
    }
    std::vector<Point> out;
    for (size_t i = 0; i < poly.size(); ++i) if (keep[i]) out.push_back(poly[i]);
    return out;
}

double MinWidth(const std::vector<Point>& hull, double& bestPsi) {
    bestPsi = 0.0;
    const size_t n = hull.size();
    if (n < 3) return 0.0;
    double best = std::numeric_limits<double>::infinity();
    // Rotating calipers: the minimum width of a convex polygon is always
    // achieved with one support line flush against an EDGE, so testing the n
    // edges is exact -- no angular sampling and no resolution to argue about.
    for (size_t i = 0; i < n; ++i) {
        const Point& a = hull[i];
        const Point& b = hull[(i + 1) % n];
        const double ex = b.x - a.x, ey = b.y - a.y;
        const double len = std::hypot(ex, ey);
        if (len < 1e-12) continue;
        double far = 0;
        for (const Point& p : hull)
            far = std::max(far, std::fabs(ey * (p.x - a.x) - ex * (p.y - a.y)) / len);
        if (far < best) {
            best = far;
            // Rows run ALONG the supporting edge: that is the direction across
            // which the extent is smallest, so it is the direction that needs
            // the fewest rows.
            bestPsi = std::atan2(ey, ex);
        }
    }
    return best;
}

void Field::ToRowFrame(double x, double y, double& u, double& w) const {
    const double c = std::cos(psiRad), s = std::sin(psiRad);
    u =  c * x + s * y;
    w = -s * x + c * y;
}

void Field::FromRowFrame(double u, double w, double& x, double& y) const {
    const double c = std::cos(psiRad), s = std::sin(psiRad);
    x = c * u - s * w;
    y = s * u + c * w;
}

Field BuildField(const std::vector<Point>& boundary, double tolM) {
    Field f;
    f.hull = ConvexHull(Simplify(boundary, tolM));
    f.minWidthM = MinWidth(f.hull, f.psiRad);
    double a2 = 0;
    for (size_t i = 0; i < f.hull.size(); ++i) {
        const Point& p = f.hull[i];
        const Point& q = f.hull[(i + 1) % f.hull.size()];
        a2 += p.x * q.y - q.x * p.y;
    }
    f.areaM2 = std::fabs(a2) * 0.5;
    return f;
}

Field BuildFieldFromBox(double x0, double y0, double x1, double y1) {
    return BuildField({{x0, y0}, {x1, y0}, {x1, y1}, {x0, y1}}, 0.0);
}

}  // namespace ns3::uavsar::p1
