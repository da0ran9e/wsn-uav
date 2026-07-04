#ifndef UAV_SAR_FOREST_A2G_LOSS_H
#define UAV_SAR_FOREST_A2G_LOSS_H

// Elevation-angle A2G loss for forest SAR (realism v3), replacing the binary
// A2G/G2G exponent switch:
//
//   G2G (both under canopy)   log-distance n = kG2GExponent (in-forest
//                             measurement already embodies vegetation).
//   A2A (both above canopy)   free-space (n = 2) + eta_LoS.
//   A2G (one above canopy)    LoS with probability P_LoS(theta) [Al-Hourani]:
//       LoS : FSPL(d) + eta_LoS
//       NLoS: FSPL(d) + A_veg,  A_veg = Amax(1 - e^{-d_veg * gamma / Amax}),
//             d_veg = canopy / sin(theta)   [ITU-R P.833 capped exponential]
//
// Spatial consistency: each unordered pair freezes ONE uniform quantile u for
// the run; the link is LoS iff u < P_LoS(theta_now). As the UAV approaches and
// theta rises, the pair crosses its own threshold angle exactly once —
// a deterministic NLoS->LoS transition, not a per-packet lottery.

#include "ns3/propagation-loss-model.h"
#include "ns3/random-variable-stream.h"

#include <cstdint>
#include <map>
#include <utility>

namespace ns3::uavsar {

class ForestA2gLossModel : public ns3::PropagationLossModel {
public:
    static ns3::TypeId GetTypeId();
    ForestA2gLossModel();
    ~ForestA2gLossModel() override = default;

    // P_LoS at elevation angle theta (degrees) — exposed for tests/analysis.
    static double PLos(double thetaDeg);
    // Foliage attenuation for a slant path at theta (degrees).
    static double VegLossDb(double thetaDeg);

private:
    double DoCalcRxPower(double txPowerDbm,
                         ns3::Ptr<ns3::MobilityModel> a,
                         ns3::Ptr<ns3::MobilityModel> b) const override;
    int64_t DoAssignStreams(int64_t stream) override;

    ns3::Ptr<ns3::UniformRandomVariable> m_u01;
    mutable std::map<std::pair<uint32_t, uint32_t>, double> m_quantile;  // frozen u
};

}  // namespace ns3::uavsar

#endif  // UAV_SAR_FOREST_A2G_LOSS_H
