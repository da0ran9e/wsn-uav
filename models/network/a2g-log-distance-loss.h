#ifndef WSN_UAV_A2G_LOG_DISTANCE_LOSS_H
#define WSN_UAV_A2G_LOG_DISTANCE_LOSS_H

#include "ns3/propagation-loss-model.h"

namespace ns3::wsn::uav {

/**
 * \brief Altitude-aware LogDistance propagation loss model.
 *
 * Switches between an air-to-ground (A2G) exponent and a ground-to-ground (G2G)
 * exponent based on the higher of the two endpoint altitudes (z-coordinate).
 * If either endpoint is above m_altitudeThreshold metres, the A2G exponent is
 * used (LoS-dominant, lower path loss). Otherwise the G2G exponent is used
 * (NLoS, higher path loss).
 *
 * Path loss formula (per branch):
 *     PL[dB] = refLoss + 10 * n * log10(d / refDist)
 * with d clamped to refDist from below.
 */
class A2GLogDistanceLossModel : public ns3::PropagationLossModel
{
  public:
    static ns3::TypeId GetTypeId();

    A2GLogDistanceLossModel();
    ~A2GLogDistanceLossModel() override = default;

    void SetA2GExponent(double n) { m_a2gExponent = n; }
    void SetG2GExponent(double n) { m_g2gExponent = n; }
    void SetAltitudeThreshold(double z) { m_altitudeThreshold = z; }
    void SetReferenceDistance(double d) { m_referenceDistance = d; }
    void SetReferenceLoss(double loss) { m_referenceLoss = loss; }

    double GetA2GExponent() const { return m_a2gExponent; }
    double GetG2GExponent() const { return m_g2gExponent; }
    double GetAltitudeThreshold() const { return m_altitudeThreshold; }

  private:
    double DoCalcRxPower(double txPowerDbm,
                         ns3::Ptr<ns3::MobilityModel> a,
                         ns3::Ptr<ns3::MobilityModel> b) const override;
    int64_t DoAssignStreams(int64_t stream) override;

    double m_a2gExponent;       //!< Path-loss exponent for air-to-ground links.
    double m_g2gExponent;       //!< Path-loss exponent for ground-to-ground links.
    double m_altitudeThreshold; //!< Above this z (m), A2G branch applies.
    double m_referenceDistance; //!< Reference distance d0 (m).
    double m_referenceLoss;     //!< Reference loss at d0 (dB).
};

}  // namespace ns3::wsn::uav

#endif  // WSN_UAV_A2G_LOG_DISTANCE_LOSS_H
