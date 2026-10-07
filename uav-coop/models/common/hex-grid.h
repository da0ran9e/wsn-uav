// Regular hexagonal lattice anchored at the origin.
//
// Pointy-top hexagons, axial coordinates (q, r). Cell (0, 0) is centred on the
// origin. "Width" is the flat-to-flat width, which is also the distance between
// the centres of two neighbouring cells:
//
//   corner radius  R    = width / sqrt(3)
//   centre         x    = width * (q + r / 2),   y = 1.5 R * r
//   area                = (sqrt(3) / 2) * width^2
//
// Pure geometry: no ns-3, no randomness.

#ifndef UAVCOOP_HEX_GRID_H
#define UAVCOOP_HEX_GRID_H

#include <array>
#include <cstdint>
#include <functional>
#include <utility>

namespace ns3::uavcoop {

struct Hex {
    int32_t q = 0, r = 0;
    bool operator==(const Hex& o) const { return q == o.q && r == o.r; }
    bool operator!=(const Hex& o) const { return !(*this == o); }
    bool operator<(const Hex& o) const { return q != o.q ? q < o.q : r < o.r; }
};

struct HexHash {
    size_t operator()(const Hex& h) const {
        return std::hash<int64_t>()(((int64_t)h.q << 32) ^ (uint32_t)h.r);
    }
};

struct Point {
    double x = 0, y = 0;
};

class HexGrid {
  public:
    explicit HexGrid(double width);

    double Width() const { return m_w; }
    double Radius() const { return m_R; }     // centre to corner
    double CellArea() const;

    Point Centre(const Hex& h) const;
    std::array<Point, 6> Corners(const Hex& h) const;
    Hex CellAt(const Point& p) const;         // the cell whose hexagon holds p
    bool Contains(const Hex& h, const Point& p) const;

    static std::array<Hex, 6> Neighbours(const Hex& h);
    static int32_t Distance(const Hex& a, const Hex& b);   // in cells

  private:
    double m_w, m_R;
};

}  // namespace ns3::uavcoop

#endif
