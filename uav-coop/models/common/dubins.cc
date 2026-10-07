#include "dubins.h"

#include <cmath>
#include <limits>

namespace ns3::uavcoop {

namespace {
const char* kWords[6] = {"LSL", "RSR", "LSR", "RSL", "RLR", "LRL"};
// segment types per word: 'L', 'S', 'R'
const char kTypes[6][3] = {{'L', 'S', 'L'}, {'R', 'S', 'R'}, {'L', 'S', 'R'},
                           {'R', 'S', 'L'}, {'R', 'L', 'R'}, {'L', 'R', 'L'}};
}  // namespace

double Mod2Pi(double a) {
    a = std::fmod(a, 2 * M_PI);
    return a < 0 ? a + 2 * M_PI : a;
}

std::string DubinsPath::Word() const { return word >= 0 ? kWords[word] : "none"; }

DubinsPath DubinsShortest(const Pose& a, const Pose& b, double rho, std::array<DubinsPath, 6>* all) {
    // Normalised frame: start at the origin, the goal on the +x axis at distance d.
    const double dx = b.x - a.x, dy = b.y - a.y;
    const double d = std::hypot(dx, dy) / rho;
    const double phi = std::atan2(dy, dx);
    const double al = Mod2Pi(a.th - phi), be = Mod2Pi(b.th - phi);
    const double sa = std::sin(al), sb = std::sin(be), ca = std::cos(al), cb = std::cos(be);
    const double cab = std::cos(al - be);
    std::array<DubinsPath, 6> P;
    for (auto& p : P) p.rho = rho;
    {   // LSL
        const double p2 = 2 + d * d - 2 * cab + 2 * d * (sa - sb);
        if (p2 >= 0) {
            const double t = std::atan2(cb - ca, d + sa - sb);
            P[0] = {0, {Mod2Pi(-al + t), std::sqrt(p2), Mod2Pi(be - t)}, rho};
        }
    }
    {   // RSR
        const double p2 = 2 + d * d - 2 * cab + 2 * d * (sb - sa);
        if (p2 >= 0) {
            const double t = std::atan2(ca - cb, d - sa + sb);
            P[1] = {1, {Mod2Pi(al - t), std::sqrt(p2), Mod2Pi(-be + t)}, rho};
        }
    }
    {   // LSR
        const double p2 = -2 + d * d + 2 * cab + 2 * d * (sa + sb);
        if (p2 >= 0) {
            const double p = std::sqrt(p2);
            const double t = std::atan2(-ca - cb, d + sa + sb) - std::atan2(-2.0, p);
            P[2] = {2, {Mod2Pi(-al + t), p, Mod2Pi(-be + t)}, rho};
        }
    }
    {   // RSL
        const double p2 = d * d - 2 + 2 * cab - 2 * d * (sa + sb);
        if (p2 >= 0) {
            const double p = std::sqrt(p2);
            const double t = std::atan2(ca + cb, d - sa - sb) - std::atan2(2.0, p);
            P[3] = {3, {Mod2Pi(al - t), p, Mod2Pi(be - t)}, rho};
        }
    }
    {   // RLR
        const double c = (6 - d * d + 2 * cab + 2 * d * (sa - sb)) / 8;
        if (std::fabs(c) <= 1) {
            const double p = Mod2Pi(2 * M_PI - std::acos(c));
            const double t = Mod2Pi(al - std::atan2(ca - cb, d - sa + sb) + p / 2);
            P[4] = {4, {t, p, Mod2Pi(al - be - t + p)}, rho};
        }
    }
    {   // LRL
        const double c = (6 - d * d + 2 * cab + 2 * d * (sb - sa)) / 8;
        if (std::fabs(c) <= 1) {
            const double p = Mod2Pi(2 * M_PI - std::acos(c));
            const double t = Mod2Pi(-al - std::atan2(ca - cb, d + sa - sb) + p / 2);
            P[5] = {5, {t, p, Mod2Pi(be - al - t + p)}, rho};
        }
    }
    DubinsPath best;
    double bl = std::numeric_limits<double>::infinity();
    for (const auto& p : P)
        if (p.Valid() && p.Length() < bl) { bl = p.Length(); best = p; }
    if (all) *all = P;
    return best;
}

Pose DubinsAt(const Pose& a, const DubinsPath& p, double s) {
    Pose q = a;
    double left = s / p.rho;   // in units of rho
    for (int k = 0; k < 3 && left > 0; ++k) {
        const double u = std::min(left, p.seg[k]);
        const char t = kTypes[p.word][k];
        if (t == 'S') {
            q.x += p.rho * u * std::cos(q.th);
            q.y += p.rho * u * std::sin(q.th);
        } else if (t == 'L') {
            q.x += p.rho * (std::sin(q.th + u) - std::sin(q.th));
            q.y += p.rho * (-std::cos(q.th + u) + std::cos(q.th));
            q.th += u;
        } else {
            q.x += p.rho * (-std::sin(q.th - u) + std::sin(q.th));
            q.y += p.rho * (std::cos(q.th - u) - std::cos(q.th));
            q.th -= u;
        }
        left -= u;
    }
    q.th = Mod2Pi(q.th);
    return q;
}

std::vector<Pose> DubinsSample(const Pose& a, const DubinsPath& p, double step, std::vector<int>* segOut) {
    std::vector<Pose> out;
    const double L = p.Length();
    const int n = std::max(1, (int)std::ceil(L / step));
    for (int i = 0; i <= n; ++i) {
        const double s = L * i / n;
        out.push_back(DubinsAt(a, p, s));
        if (segOut) {
            double acc = 0;
            int k = 0;
            while (k < 2 && s > (acc + p.seg[k]) * p.rho + 1e-9) { acc += p.seg[k]; ++k; }
            segOut->push_back(k);
        }
    }
    return out;
}

}  // namespace ns3::uavcoop
