#ifndef UAV_SAR_AIR_GROUND_LOSS_H
#define UAV_SAR_AIR_GROUND_LOSS_H

// Deterministic large-scale path loss with distinct exponents for air-to-ground
// (a UAV is involved, mostly LoS) vs ground-to-ground (sensor↔sensor, NLoS
// through vegetation). Clean reimplementation (ref: main's a2g-log-distance-loss)
// grounded in 3GPP TR 36.777 / Khawaja 2019: A2G exponent ~2.2, G2G ~3.5.
//
// A link is treated as A2G when either endpoint is above the altitude threshold
// (canopy top); otherwise G2G. Small-scale fading (Nakagami) and shadowing
// (log-normal) are added separately as extra loss models on the channel.
//
//   PL(d) = refLoss + 10 * n * log10(d / d0),   n = A2G or G2G exponent
//   RxPower = TxPower - PL(d)

#include "ns3/propagation-loss-model.h"

namespace ns3::uavsar {

class AirGroundLossModel : public ns3::PropagationLossModel {
public:
    static ns3::TypeId GetTypeId();
    AirGroundLossModel();
    ~AirGroundLossModel() override = default;

    void SetA2GExponent(double n) { m_a2g = n; }
    void SetG2GExponent(double n) { m_g2g = n; }
    void SetAltitudeThreshold(double z) { m_altThresh = z; }
    void SetReferenceDistance(double d) { m_refDist = d; }
    void SetReferenceLoss(double l) { m_refLoss = l; }

private:
    double DoCalcRxPower(double txPowerDbm,
                         ns3::Ptr<ns3::MobilityModel> a,
                         ns3::Ptr<ns3::MobilityModel> b) const override;
    int64_t DoAssignStreams(int64_t stream) override;

    double m_a2g;
    double m_g2g;
    double m_altThresh;
    double m_refDist;
    double m_refLoss;
};

}  // namespace ns3::uavsar

#endif  // UAV_SAR_AIR_GROUND_LOSS_H
