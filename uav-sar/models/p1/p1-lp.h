#ifndef UAV_SAR_P1_LP_H
#define UAV_SAR_P1_LP_H

// A small dense linear program, solved exactly.
//
//     minimise  c . x     subject to   A x <= b ,  x >= 0
//
// Two-phase primal simplex with Bland's rule. Bland's is slower than steepest
// edge and it CANNOT CYCLE, which matters more here: the speed profile is
// degenerate whenever several cells are satisfied exactly at once, which is
// precisely the interesting case, and a cycling solver in a degenerate corner
// hangs rather than fails.
//
// This exists because the environment has no LP library (no SciPy, no OR-Tools,
// no PuLP), and because T3 must be SOLVED rather than approximated: the whole
// argument for the inverse-speed change of variable is that it leaves a linear
// program behind, and answering it with a heuristic would throw that away.
//
// Rows with a negative right-hand side are handled by phase 1, so ">=" rows can
// be passed by negating them -- which is how the dose constraints arrive.

#include <cstdint>
#include <vector>

namespace ns3::uavsar::p1 {

struct LpResult {
    bool ok = false;              // an optimal solution was found
    bool infeasible = false;
    bool unbounded = false;
    double objective = 0.0;
    std::vector<double> x;
    // Shadow price of each row. For the dose rows this says which cell is
    // BINDING -- the signal T4 uses to know where to spend the next revision.
    std::vector<double> dual;
    uint32_t iterations = 0;
};

LpResult SolveLp(const std::vector<std::vector<double>>& A,
                 const std::vector<double>& b,
                 const std::vector<double>& c);

}  // namespace ns3::uavsar::p1

#endif  // UAV_SAR_P1_LP_H
