#ifndef UAV_SAR_P1_HEX_H
#define UAV_SAR_P1_HEX_H

// Pointy-top hexagonal geometry -- the only thing Phase 1 reuses from Phase 0.
//
// This is a DELIBERATE DUPLICATE of the same six lines in cell-grid.cc, not a
// dependency on it. The reason is not tidiness: cell-grid.h carries a cell
// leader elected by proximity to the centroid and an intra-cell tree rooted
// there, and Phase 1 elects its leader by CAPABILITY and needs the tree rooted
// at that one instead. Including the old header to get the hex maths would drag
// the old leader in with it, and the two would coexist -- which is exactly the
// failure this subtree exists to prevent.
//
// The duplicate is made safe by CHECKING it: the harness asserts these
// functions agree with cell-grid's over a dense sample. A verified duplicate is
// safe; a shared symbol carrying a second meaning is not.
//
// Quantities Phase 0 hands to Phase 1, all from R_c (the circumradius):
//   apothem (inner radius)          R_c * sqrt(3)/2
//   centre-to-centre, adjacent      R_c * sqrt(3)
//   ROW PITCH  h                    R_c * 1.5      <- the one that matters
//   area of one cell                R_c^2 * 3*sqrt(3)/2
//
// The row pitch is what connects cell size to the aircraft's turn radius, and
// it is the reason the design rule can be stated at all. The area is the other
// one worth writing down here, because the natural mistake -- treating a cell
// as a disc of radius R_c -- undercounts the cells in a field by 17.3 %.

#include <cmath>
#include <cstdint>

namespace ns3::uavsar::p1 {

namespace hex {

inline double Apothem(double rc)   { return rc * std::sqrt(3.0) / 2.0; }
inline double CentrePitch(double rc) { return rc * std::sqrt(3.0); }
inline double RowPitch(double rc)  { return rc * 1.5; }
inline double CellArea(double rc)  { return rc * rc * 1.5 * std::sqrt(3.0); }

inline void WorldToAxial(double x, double y, double size, int32_t& q, int32_t& r) {
    const double fq = (std::sqrt(3.0) / 3.0 * x - 1.0 / 3.0 * y) / size;
    const double fr = (2.0 / 3.0 * y) / size;
    const double fs = -fq - fr;                 // cube rounding keeps q+r+s == 0
    int32_t rq = (int32_t)std::lround(fq);
    int32_t rr = (int32_t)std::lround(fr);
    const int32_t rs = (int32_t)std::lround(fs);
    const double dq = std::fabs(rq - fq), dr = std::fabs(rr - fr), ds = std::fabs(rs - fs);
    if (dq > dr && dq > ds)  rq = -rr - rs;
    else if (dr > ds)        rr = -rq - rs;
    q = rq;
    r = rr;
}

inline void AxialToCentre(int32_t q, int32_t r, double size, double& cx, double& cy) {
    cx = size * (std::sqrt(3.0) * q + std::sqrt(3.0) / 2.0 * r);
    cy = size * (1.5 * r);
}

}  // namespace hex

}  // namespace ns3::uavsar::p1

#endif  // UAV_SAR_P1_HEX_H
