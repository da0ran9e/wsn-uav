#include "node-capability.h"

#include <random>

namespace ns3::uavsar {

std::map<uint32_t, NodeCapability>
BuildCapabilities(const std::vector<uint32_t>& nodeIds, const CapabilityConfig& cfg) {
    std::map<uint32_t, NodeCapability> out;
    if (cfg.uniform) {
        for (uint32_t id : nodeIds) out[id] = NodeCapability{};
        return out;
    }
    // Own stream, own salt: adding heterogeneity must not perturb the clue field,
    // the clutter placement or the channel, otherwise no comparison against the
    // uniform world means anything.
    std::mt19937 rng(cfg.seed ^ 0x5BD1E995u);
    std::uniform_real_distribution<double> u01(0.0, 1.0);
    for (uint32_t id : nodeIds) {
        NodeCapability c;
        c.obs = (u01(rng) < cfg.cameraFraction)
                    ? cfg.obsMin + (cfg.obsMax - cfg.obsMin) * u01(rng)
                    : 0.0;
        c.cpu = cfg.cpuMin + (cfg.cpuMax - cfg.cpuMin) * u01(rng);
        c.radioDuty = cfg.dutyMin + (cfg.dutyMax - cfg.dutyMin) * u01(rng);
        out[id] = c;
    }
    return out;
}

}  // namespace ns3::uavsar
