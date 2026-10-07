// A small, portable random source for the pure-logic parts of the model.
//
// std::uniform_*_distribution is implementation-defined, so the same seed can give
// different deployments on different standard libraries. This draws doubles
// straight from the 53 top bits of mt19937_64, which is fully specified.

#ifndef UAVCOOP_COOP_RNG_H
#define UAVCOOP_COOP_RNG_H

#include <cstdint>
#include <random>

namespace ns3::uavcoop {

class CoopRng {
  public:
    // Independent streams from one seed: SplitMix64 of (seed, stream).
    CoopRng(uint64_t seed, uint64_t stream) : m_g(Mix(seed * 0x9E3779B97F4A7C15ull + stream)) {}

    double Uniform() { return (double)(m_g() >> 11) * 0x1.0p-53; }    // [0, 1)
    double Uniform(double a, double b) { return a + (b - a) * Uniform(); }
    uint64_t Below(uint64_t n) { return (uint64_t)(Uniform() * (double)n); }   // [0, n)

  private:
    static uint64_t Mix(uint64_t z) {
        z += 0x9E3779B97F4A7C15ull;
        z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull;
        z = (z ^ (z >> 27)) * 0x94D049BB133111EBull;
        return z ^ (z >> 31);
    }
    std::mt19937_64 m_g;
};

}  // namespace ns3::uavcoop

#endif
