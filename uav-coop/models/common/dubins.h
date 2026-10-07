// Dubins paths: the shortest curve between two poses for a vehicle that only moves
// forward with a minimum turn radius rho -- the fixed-wing UAV.
//
// The shortest path is always one of six words, each three segments of left turn
// (L), right turn (R) or straight (S): LSL, RSR, LSR, RSL, RLR, LRL. All six are
// evaluated in closed form and the shortest kept. Pure geometry.

#ifndef UAVCOOP_DUBINS_H
#define UAVCOOP_DUBINS_H

#include <array>
#include <cstdint>
#include <string>
#include <vector>

namespace ns3::uavcoop {

struct Pose {
    double x = 0, y = 0, th = 0;   // heading, rad, counter-clockwise from +x
};

struct DubinsPath {
    int word = -1;                       // 0..5: LSL RSR LSR RSL RLR LRL
    std::array<double, 3> seg{};         // segment lengths, in units of rho
    double rho = 0;
    double Length() const { return (seg[0] + seg[1] + seg[2]) * rho; }
    std::string Word() const;
    bool Valid() const { return word >= 0; }
};

// Shortest of the six words; `all` (optional) receives every word's path (invalid = -1).
DubinsPath DubinsShortest(const Pose& a, const Pose& b, double rho,
                          std::array<DubinsPath, 6>* all = nullptr);

// The pose `s` metres along the path from `a`.
Pose DubinsAt(const Pose& a, const DubinsPath& p, double s);

// Poses every `step` metres, start and end included. `segOut` (optional) gets the
// segment index (0, 1, 2) of each sample.
std::vector<Pose> DubinsSample(const Pose& a, const DubinsPath& p, double step,
                               std::vector<int>* segOut = nullptr);

double Mod2Pi(double a);

}  // namespace ns3::uavcoop

#endif
