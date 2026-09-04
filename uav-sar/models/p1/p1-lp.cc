#include "p1-lp.h"

#include <cmath>
#include <limits>

namespace ns3::uavsar::p1 {

namespace {

constexpr double kEps = 1e-9;

// One simplex pass over a tableau already in canonical form. `basis` holds the
// basic variable of each row; the last row is the objective, the last column is
// the right-hand side.
//
// PIVOT RULE. Bland's rule cannot cycle, which is what a degenerate problem
// needs -- and the speed LP is degenerate whenever several cells are satisfied
// exactly at once, which is the interesting case. But Bland's is also slow, and
// slow here was not academic: instances of this LP ran into a 200000-iteration
// cap and came back neither optimal nor infeasible, which the caller then had to
// read as "unsolved".
//
// So: Dantzig's rule (most negative reduced cost) for speed, falling back to
// Bland's only when progress stalls. A run of degenerate pivots -- ones that
// move the objective nowhere -- is the signature of an incipient cycle, so
// counting them is the trigger. The fallback is released once the objective
// moves again.
bool Pivot(std::vector<std::vector<double>>& T, std::vector<int>& basis,
           uint32_t& iters, bool& unbounded) {
    const size_t m = T.size() - 1, n = T[0].size() - 1;
    uint32_t stalled = 0;
    while (true) {
        if (++iters > 200000) return false;
        const bool bland = stalled > 24;

        int col = -1;
        if (bland) {
            for (size_t j = 0; j < n; ++j)
                if (T[m][j] < -kEps) { col = (int)j; break; }
        } else {
            double best = -kEps;
            for (size_t j = 0; j < n; ++j)
                if (T[m][j] < best) { best = T[m][j]; col = (int)j; }
        }
        if (col < 0) return true;                       // optimal

        int row = -1;
        double best = std::numeric_limits<double>::infinity();
        for (size_t i = 0; i < m; ++i) {
            if (T[i][col] <= kEps) continue;
            const double r = T[i][n] / T[i][col];
            const bool better = r < best - kEps;
            const bool tie = std::fabs(r - best) <= kEps;
            // On ties Bland's takes the lowest-index basic variable; Dantzig's
            // takes the largest pivot, which keeps the tableau better behaved.
            const bool tieWins = tie && (row < 0 ||
                (bland ? basis[i] < basis[row] : T[i][col] > T[row][col]));
            if (better || tieWins) { best = r; row = (int)i; }
        }
        if (row < 0) { unbounded = true; return false; }

        stalled = best <= kEps ? stalled + 1 : 0;

        const double p = T[row][col];
        for (size_t j = 0; j <= n; ++j) T[row][j] /= p;
        for (size_t i = 0; i <= m; ++i) {
            if ((int)i == row) continue;
            const double f = T[i][col];
            if (std::fabs(f) < kEps) continue;
            for (size_t j = 0; j <= n; ++j) T[i][j] -= f * T[row][j];
        }
        basis[row] = col;
    }
}

}  // namespace

LpResult SolveLp(const std::vector<std::vector<double>>& A0,
                 const std::vector<double>& b0,
                 const std::vector<double>& c) {
    LpResult r;
    const size_t m = A0.size();
    const size_t n = c.size();
    if (m == 0 || n == 0) { r.ok = true; r.x.assign(n, 0.0); return r; }

    // SCALE FIRST. The speed LP arrives badly conditioned -- dose coefficients of
    // order 1e4, right-hand sides of order 1e5, objective coefficients of order
    // 10 -- and a dense tableau pivoted tens of thousands of times without
    // refactorisation drifts until the optimality test stops firing. That was
    // measured: two instances ran into the 200000-iteration cap, one in phase 1
    // and one in phase 2, and came back neither optimal nor infeasible. Dividing
    // each row by its largest coefficient costs one pass and fixes it; the
    // feasible set is unchanged, only the slack and the dual of that row scale.
    std::vector<std::vector<double>> A = A0;
    std::vector<double> b = b0;
    std::vector<double> rowScale(m, 1.0);
    for (size_t i = 0; i < m; ++i) {
        double mx = 0.0;
        for (double v : A[i]) mx = std::max(mx, std::fabs(v));
        if (mx > 0.0) {
            rowScale[i] = mx;
            for (double& v : A[i]) v /= mx;
            b[i] /= mx;
        }
    }
    double objScale = 0.0;
    for (double v : c) objScale = std::max(objScale, std::fabs(v));
    if (objScale <= 0.0) objScale = 1.0;

    std::vector<int> needArt;
    for (size_t i = 0; i < m; ++i) {
        if (b[i] < 0) {
            for (double& v : A[i]) v = -v;
            b[i] = -b[i];
            needArt.push_back((int)i);
        }
    }
    const size_t nArt = needArt.size();
    const size_t cols = n + m + nArt;               // structural | slack | artificial

    std::vector<std::vector<double>> T(m + 1, std::vector<double>(cols + 1, 0.0));
    std::vector<int> basis(m, -1);
    for (size_t i = 0; i < m; ++i) {
        for (size_t j = 0; j < n; ++j) T[i][j] = A[i][j];
        T[i][cols] = b[i];
    }
    // slack sign: +1 on untouched rows, -1 on rows that were negated (they were
    // "<=" with negative RHS, i.e. ">=" rows after the flip)
    size_t art = 0;
    std::vector<bool> flipped(m, false);
    for (int i : needArt) flipped[i] = true;
    for (size_t i = 0; i < m; ++i) {
        T[i][n + i] = flipped[i] ? -1.0 : 1.0;
        if (flipped[i]) { T[i][n + m + art] = 1.0; basis[i] = (int)(n + m + art); art++; }
        else            { basis[i] = (int)(n + i); }
    }

    uint32_t iters = 0;
    bool unbounded = false;

    if (nArt > 0) {
        // Phase 1: drive the artificials to zero.
        for (size_t j = n + m; j < cols; ++j) T[m][j] = 1.0;
        for (size_t i = 0; i < m; ++i)
            if (basis[i] >= (int)(n + m))
                for (size_t j = 0; j <= cols; ++j) T[m][j] -= T[i][j];
        if (!Pivot(T, basis, iters, unbounded)) {
            r.unbounded = unbounded;
            r.iterations = iters;      // was dropped here, so a capped phase 1
            return r;                  // reported 0 iterations and looked like a no-op
        }
        if (T[m][cols] < -kEps) { r.infeasible = true; r.iterations = iters; return r; }
        // Drive any artificial still in the basis out at zero level.
        for (size_t i = 0; i < m; ++i) {
            if (basis[i] < (int)(n + m)) continue;
            for (size_t j = 0; j < n + m; ++j) {
                if (std::fabs(T[i][j]) <= kEps) continue;
                const double p = T[i][j];
                for (size_t k = 0; k <= cols; ++k) T[i][k] /= p;
                for (size_t k2 = 0; k2 <= m; ++k2) {
                    if (k2 == i) continue;
                    const double f = T[k2][j];
                    if (std::fabs(f) < kEps) continue;
                    for (size_t k = 0; k <= cols; ++k) T[k2][k] -= f * T[i][k];
                }
                basis[i] = (int)j;
                break;
            }
        }
        for (size_t j = n + m; j < cols; ++j)
            for (size_t i = 0; i <= m; ++i) T[i][j] = 0.0;
    }

    // Phase 2 with the real objective.
    for (size_t j = 0; j <= cols; ++j) T[m][j] = 0.0;
    for (size_t j = 0; j < n; ++j) T[m][j] = c[j] / objScale;
    for (size_t i = 0; i < m; ++i) {
        if (basis[i] < 0 || basis[i] >= (int)n) continue;
        const double f = T[m][basis[i]];
        if (std::fabs(f) < kEps) continue;
        for (size_t j = 0; j <= cols; ++j) T[m][j] -= f * T[i][j];
    }
    if (!Pivot(T, basis, iters, unbounded)) { r.unbounded = unbounded; r.iterations = iters; return r; }

    r.x.assign(n, 0.0);
    for (size_t i = 0; i < m; ++i)
        if (basis[i] >= 0 && basis[i] < (int)n) r.x[basis[i]] = T[i][cols];
    r.objective = -T[m][cols] * objScale;
    // Shadow prices sit in the objective row under the slack columns. A row with
    // a non-zero price is one the optimum is pressed against.
    r.dual.assign(m, 0.0);
    // Undo both scalings so the duals are prices on the ORIGINAL rows.
    for (size_t i = 0; i < m; ++i)
        r.dual[i] = (flipped[i] ? T[m][n + i] : -T[m][n + i]) * objScale / rowScale[i];
    r.iterations = iters;
    r.ok = true;
    return r;
}

}  // namespace ns3::uavsar::p1
