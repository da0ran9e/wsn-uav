#ifndef UAV_SAR_P1_DUBINS_H
#define UAV_SAR_P1_DUBINS_H

// Shortest paths for a vehicle that cannot turn on the spot.
//
// This is what makes Phase 1 routing a different problem from the one the
// coverage literature solves. The distance between two places depends on the
// HEADING at both ends, so the cost matrix is neither symmetric nor metric, and
// a tour that is short in Euclidean terms can be long to fly.
//
// A port of the implementation in tools/dubins_lanes.py, which is checked to
// 5.6e-13 m against forward integration. The CCC words are built GEOMETRICALLY
// rather than transcribed from a closed form: a remembered CCC expression with
// one sign wrong still returns plausible lengths, and an earlier version of this
// algorithm did exactly that -- 208 m of endpoint error on LRL while the other
// five words were exact. Only an integration check finds that, so the harness
// runs one.

#include <cstdint>

namespace ns3::uavsar::p1 {

struct Config {
    double x = 0, y = 0, hdg = 0;   // heading in radians
};

enum class Word : uint8_t { LSL, RSR, LSR, RSL, RLR, LRL, NONE };

struct DubinsPath {
    double length = 0.0;            // metres
    Word   word = Word::NONE;
    double seg[3] = {0, 0, 0};      // NORMALISED units; multiply by R for metres
    bool   valid = false;
};

DubinsPath Dubins(const Config& a, const Config& b, double radiusM);
double DubinsLength(const Config& a, const Config& b, double radiusM);

// Fly the control word forward. Used by the harness to verify the closed form,
// and by the visualiser to draw the path.
Config Integrate(const Config& start, const DubinsPath& p, double radiusM,
                 double fraction = 1.0);

const char* WordName(Word w);

}  // namespace ns3::uavsar::p1

#endif  // UAV_SAR_P1_DUBINS_H
