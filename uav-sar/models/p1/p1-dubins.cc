#include "p1-dubins.h"

#include <cmath>
#include <initializer_list>
#include <limits>

namespace ns3::uavsar::p1 {

namespace {

constexpr double kTwoPi = 2.0 * M_PI;

double Mod2Pi(double t) { return t - kTwoPi * std::floor(t / kTwoPi); }
double Ang(double vx, double vy) { return std::atan2(vy, vx); }

struct Seg { double t, p, q; bool ok; };

Seg Lsl(double a, double b, double d) {
    const double tmp = std::atan2(std::cos(b) - std::cos(a),
                                  d + std::sin(a) - std::sin(b));
    const double p2 = 2 + d * d - 2 * std::cos(a - b) + 2 * d * (std::sin(a) - std::sin(b));
    if (p2 < 0) return {0, 0, 0, false};
    return {Mod2Pi(tmp - a), std::sqrt(p2), Mod2Pi(b - tmp), true};
}

Seg Rsr(double a, double b, double d) {
    const double tmp = std::atan2(std::cos(a) - std::cos(b),
                                  d - std::sin(a) + std::sin(b));
    const double p2 = 2 + d * d - 2 * std::cos(a - b) + 2 * d * (std::sin(b) - std::sin(a));
    if (p2 < 0) return {0, 0, 0, false};
    return {Mod2Pi(a - tmp), std::sqrt(p2), Mod2Pi(tmp - b), true};
}

Seg Lsr(double a, double b, double d) {
    const double p2 = -2 + d * d + 2 * std::cos(a - b) + 2 * d * (std::sin(a) + std::sin(b));
    if (p2 < 0) return {0, 0, 0, false};
    const double p = std::sqrt(p2);
    const double tmp = std::atan2(-std::cos(a) - std::cos(b),
                                  d + std::sin(a) + std::sin(b)) - std::atan2(-2.0, p);
    return {Mod2Pi(tmp - a), p, Mod2Pi(tmp - Mod2Pi(b)), true};
}

Seg Rsl(double a, double b, double d) {
    const double p2 = -2 + d * d + 2 * std::cos(a - b) - 2 * d * (std::sin(a) + std::sin(b));
    if (p2 < 0) return {0, 0, 0, false};
    const double p = std::sqrt(p2);
    const double tmp = std::atan2(std::cos(a) + std::cos(b),
                                  d - std::sin(a) - std::sin(b)) - std::atan2(2.0, p);
    return {Mod2Pi(a - tmp), p, Mod2Pi(Mod2Pi(b) - tmp), true};
}

// The middle circle is PLACED, not remembered: every quantity below can be
// checked by eye against a drawing, which a closed form cannot.
Seg Ccc(double a, double b, double d, bool leftOuter) {
    const double s = leftOuter ? 1.0 : -1.0;
    const double p1x = 0.0, p1y = 0.0, p2x = d, p2y = 0.0;
    const double c1x = p1x - s * std::sin(a), c1y = p1y + s * std::cos(a);
    const double c3x = p2x - s * std::sin(b), c3y = p2y + s * std::cos(b);
    const double vx = c3x - c1x, vy = c3y - c1y;
    const double D = std::hypot(vx, vy);
    if (D > 4.0 || D < 1e-12) return {0, 0, 0, false};
    const double theta = Ang(vx, vy), phi = std::acos(D / 4.0);
    Seg best{0, 0, 0, false};
    double bestL = std::numeric_limits<double>::infinity();
    for (double sign : {+1.0, -1.0}) {
        const double ang = theta + sign * phi;
        const double c2x = c1x + 2 * std::cos(ang), c2y = c1y + 2 * std::sin(ang);
        const double t = Mod2Pi(s * (Ang(c2x - c1x, c2y - c1y) - Ang(p1x - c1x, p1y - c1y)));
        const double p = Mod2Pi(-s * (Ang(c3x - c2x, c3y - c2y) - Ang(c1x - c2x, c1y - c2y)));
        const double q = Mod2Pi(s * (Ang(p2x - c3x, p2y - c3y) - Ang(c2x - c3x, c2y - c3y)));
        const double L = t + p + q;
        if (L < bestL) { bestL = L; best = {t, p, q, true}; }
    }
    return best;
}

}  // namespace

const char* WordName(Word w) {
    switch (w) {
        case Word::LSL: return "LSL";
        case Word::RSR: return "RSR";
        case Word::LSR: return "LSR";
        case Word::RSL: return "RSL";
        case Word::RLR: return "RLR";
        case Word::LRL: return "LRL";
        default:        return "--";
    }
}

DubinsPath Dubins(const Config& a, const Config& b, double R) {
    DubinsPath out;
    if (R <= 0) return out;
    const double dx = b.x - a.x, dy = b.y - a.y;
    const double D = std::hypot(dx, dy);
    const double d = D / R;
    const double theta = D > 1e-12 ? Mod2Pi(std::atan2(dy, dx)) : 0.0;
    const double aa = Mod2Pi(a.hdg - theta), bb = Mod2Pi(b.hdg - theta);

    const Seg cand[6] = {Lsl(aa, bb, d), Rsr(aa, bb, d), Lsr(aa, bb, d),
                         Rsl(aa, bb, d), Ccc(aa, bb, d, false), Ccc(aa, bb, d, true)};
    const Word names[6] = {Word::LSL, Word::RSR, Word::LSR,
                           Word::RSL, Word::RLR, Word::LRL};
    double bestL = std::numeric_limits<double>::infinity();
    for (int i = 0; i < 6; ++i) {
        if (!cand[i].ok) continue;
        const double L = cand[i].t + cand[i].p + cand[i].q;
        if (L < bestL) {
            bestL = L;
            out.word = names[i];
            out.seg[0] = cand[i].t; out.seg[1] = cand[i].p; out.seg[2] = cand[i].q;
            out.valid = true;
        }
    }
    out.length = out.valid ? bestL * R : 0.0;
    return out;
}

double DubinsLength(const Config& a, const Config& b, double R) {
    const DubinsPath p = Dubins(a, b, R);
    return p.valid ? p.length : std::numeric_limits<double>::infinity();
}

Config Integrate(const Config& start, const DubinsPath& p, double R, double fraction) {
    Config c = start;
    if (!p.valid) return c;
    const char* w = WordName(p.word);
    double budget = fraction * (p.seg[0] + p.seg[1] + p.seg[2]);
    for (int i = 0; i < 3; ++i) {
        const double s = std::min(budget, p.seg[i]);
        if (s <= 0) break;
        budget -= s;
        if (w[i] == 'S') {
            c.x += s * R * std::cos(c.hdg);
            c.y += s * R * std::sin(c.hdg);
        } else {
            const double turn = w[i] == 'L' ? 1.0 : -1.0;
            const double cx = c.x - turn * R * std::sin(c.hdg);
            const double cy = c.y + turn * R * std::cos(c.hdg);
            const double h2 = c.hdg + turn * s;
            c.x = cx + turn * R * std::sin(h2);
            c.y = cy - turn * R * std::cos(h2);
            c.hdg = Mod2Pi(h2);
        }
        if (budget <= 1e-15) break;
    }
    return c;
}

}  // namespace ns3::uavsar::p1
