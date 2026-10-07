#include "hex-grid.h"

#include <cmath>
#include <cstdlib>

namespace ns3::uavcoop {

HexGrid::HexGrid(double width) : m_w(width), m_R(width / std::sqrt(3.0)) {}

double HexGrid::CellArea() const { return std::sqrt(3.0) / 2.0 * m_w * m_w; }

Point HexGrid::Centre(const Hex& h) const {
    return {m_w * (h.q + h.r / 2.0), 1.5 * m_R * h.r};
}

std::array<Point, 6> HexGrid::Corners(const Hex& h) const {
    const Point c = Centre(h);
    std::array<Point, 6> v;
    for (int k = 0; k < 6; ++k) {
        const double a = (30.0 + 60.0 * k) * M_PI / 180.0;   // pointy-top: 90 deg is a corner
        v[k] = {c.x + m_R * std::cos(a), c.y + m_R * std::sin(a)};
    }
    return v;
}

Hex HexGrid::CellAt(const Point& p) const {
    // Fractional axial coordinates, then cube rounding.
    const double r = p.y / (1.5 * m_R);
    const double q = p.x / m_w - r / 2.0;
    const double x = q, z = r, y = -x - z;
    double rx = std::round(x), ry = std::round(y), rz = std::round(z);
    const double dx = std::fabs(rx - x), dy = std::fabs(ry - y), dz = std::fabs(rz - z);
    if (dx > dy && dx > dz) rx = -ry - rz;
    else if (dy <= dz) rz = -rx - ry;
    return {(int32_t)rx, (int32_t)rz};
}

bool HexGrid::Contains(const Hex& h, const Point& p) const { return CellAt(p) == h; }

std::array<Hex, 6> HexGrid::Neighbours(const Hex& h) {
    return {{{h.q + 1, h.r}, {h.q - 1, h.r}, {h.q, h.r + 1},
             {h.q, h.r - 1}, {h.q + 1, h.r - 1}, {h.q - 1, h.r + 1}}};
}

int32_t HexGrid::Distance(const Hex& a, const Hex& b) {
    const int32_t dq = a.q - b.q, dr = a.r - b.r;
    return (std::abs(dq) + std::abs(dr) + std::abs(dq + dr)) / 2;
}

}  // namespace ns3::uavcoop
