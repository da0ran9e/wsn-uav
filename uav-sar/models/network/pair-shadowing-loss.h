#ifndef UAV_SAR_PAIR_SHADOWING_LOSS_H
#define UAV_SAR_PAIR_SHADOWING_LOSS_H

// Log-normal shadowing that is SPATIALLY PERSISTENT: one zero-mean Normal draw
// (sigma dB) per unordered node pair, cached for the whole run. Fixes the
// review finding that ns-3's RandomPropagationLossModel redraws per packet,
// which behaves like extra fast fading and produces unrealistic "lucky long
// shots" far beyond the deterministic range.

#include "ns3/propagation-loss-model.h"
#include "ns3/random-variable-stream.h"

#include <cstdint>
#include <map>
#include <utility>

namespace ns3::uavsar {

class PairShadowingLossModel : public ns3::PropagationLossModel {
public:
    static ns3::TypeId GetTypeId();
    PairShadowingLossModel();
    ~PairShadowingLossModel() override = default;

    void SetSigmaDb(double s) { m_sigmaDb = s; }
    void SetSigmaA2gDb(double s) { m_sigmaA2gDb = s; }

private:
    double DoCalcRxPower(double txPowerDbm,
                         ns3::Ptr<ns3::MobilityModel> a,
                         ns3::Ptr<ns3::MobilityModel> b) const override;
    int64_t DoAssignStreams(int64_t stream) override;

    double m_sigmaDb;      // ground-ground (woodland total)
    double m_sigmaA2gDb;   // residual once LoS/foliage is explicit
    ns3::Ptr<ns3::NormalRandomVariable> m_rv;
    mutable std::map<std::pair<uint32_t, uint32_t>, double> m_cache;  // pair -> dB
};

}  // namespace ns3::uavsar

#endif  // UAV_SAR_PAIR_SHADOWING_LOSS_H
