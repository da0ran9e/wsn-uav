#ifndef UAV_SAR_P1_FIELD_H
#define UAV_SAR_P1_FIELD_H

// P0.0 - P0.4: the mission domain, the sweep direction, and the rotated grid.
//
// This is where PA1 differs most from what came before. The aircraft no longer
// visits cell centres as points -- it flies ROW LINES and weaves to reach the
// heads. Everything downstream depends on the rows existing, so they are built
// here, once, before anything else.
//
//   P0.0  simplify the boundary, take the convex hull
//   P0.1  choose psi, the sweep direction
//   P0.2  tile with the grid ROTATED so one row family lies along psi
//   P0.4  every node computes its own row and its own offset from it
//
// ---------------------------------------------------------------------------
// WHY psi IS THE PERPENDICULAR TO THE MINIMUM WIDTH
// ---------------------------------------------------------------------------
// The per-turn cost L(h, rho) does not depend on psi: h = 1.5 R_c comes from the
// lattice and rho from the airframe, and neither knows which way the rows point.
// The total length of the rows themselves is about Area / h whichever way they
// run. So the only thing psi changes is HOW MANY turns there are, which is the
// number of rows, which is the extent perpendicular to psi divided by h. Hence
//
//     min total turn cost  <=>  min number of rows  <=>  min width perpendicular
//
// and the answer is the direction perpendicular to the hull's minimum width,
// which rotating calipers gives in O(n log n).
//
// A0, stated because it is load-bearing: ONE psi for the whole domain. A deeply
// concave region gets swept in a direction that is wrong for its concavities;
// the convex hull hides that rather than fixing it. See F0.

#include "p1-hex.h"

#include <cstdint>
#include <map>
#include <vector>

namespace ns3::uavsar::p1 {

struct Point {
    double x = 0, y = 0;
};

struct Field {
    std::vector<Point> hull;       // P0.0, counter-clockwise
    double psiRad = 0.0;           // P0.1, direction the rows run
    double minWidthM = 0.0;        // extent perpendicular to psi
    double areaM2 = 0.0;
    // The grid is stored in ROW FRAME: u along psi, w across it. A node's row is
    // decided by w, and its offset delta by the distance from w to the row line.
    void ToRowFrame(double x, double y, double& u, double& w) const;
    void FromRowFrame(double u, double w, double& x, double& y) const;
};

// P0.0 + P0.1. `tolM` is the Douglas-Peucker tolerance.
Field BuildField(const std::vector<Point>& boundary, double tolM = 5.0);

// Convenience for a rectangular deployment.
Field BuildFieldFromBox(double x0, double y0, double x1, double y1);

// Rotating calipers minimum width of a convex polygon, and the direction of the
// supporting edge that achieves it. Exposed so the harness can check it against
// a brute-force scan over angles.
double MinWidth(const std::vector<Point>& hull, double& bestPsiRad);

std::vector<Point> ConvexHull(std::vector<Point> pts);
std::vector<Point> Simplify(const std::vector<Point>& poly, double tolM);

}  // namespace ns3::uavsar::p1

#endif  // UAV_SAR_P1_FIELD_H
