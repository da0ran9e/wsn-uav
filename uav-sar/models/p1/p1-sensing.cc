#include "p1-sensing.h"

#include <random>

namespace ns3::uavsar::p1 {

std::vector<Node> BuildNodes(const std::vector<std::pair<double, double>>& xy,
                             uint32_t seed) {
    std::vector<Node> out;
    out.reserve(xy.size());
    std::mt19937 rng(seed ^ 0x5BD1E995u);
    std::uniform_real_distribution<double> u01(0.0, 1.0);
    uint32_t id = 0;
    for (const auto& [x, y] : xy) {
        Node n;
        n.id = id++;
        n.x = x;
        n.y = y;
        if (u01(rng) < kImagingFraction) {
            n.obs = kObsMin + (kObsMax - kObsMin) * u01(rng);
            const double m = u01(rng);
            n.modality = m < kVisualFraction ? Modality::VISUAL
                       : m < kVisualFraction + kThermalFraction ? Modality::THERMAL
                                                                : Modality::ACOUSTIC;
        } else {
            n.obs = 0.0;
            n.modality = Modality::NONE;   // scalar node
        }
        n.cpu   = kCpuMin + (kCpuMax - kCpuMin) * u01(rng);
        n.rxBps = kRxBpsMin + (kRxBpsMax - kRxBpsMin) * u01(rng);
        out.push_back(n);
    }
    return out;
}

std::vector<Node> BuildUniformNodes(const std::vector<std::pair<double, double>>& xy) {
    std::vector<Node> out;
    out.reserve(xy.size());
    uint32_t id = 0;
    for (const auto& [x, y] : xy) {
        Node n;
        n.id = id++;
        n.x = x;
        n.y = y;
        n.modality = kReferenceModality;
        n.obs = 1.0;
        n.cpu = 1.0;
        n.rxBps = kRxBpsMax;
        out.push_back(n);
    }
    return out;
}

}  // namespace ns3::uavsar::p1
