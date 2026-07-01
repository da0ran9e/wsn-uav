#include "a2g-log-distance-loss.h"

#include "ns3/double.h"
#include "ns3/mobility-model.h"

#include <cmath>

namespace ns3::wsn::uav {

NS_OBJECT_ENSURE_REGISTERED(A2GLogDistanceLossModel);

ns3::TypeId
A2GLogDistanceLossModel::GetTypeId()
{
    static ns3::TypeId tid =
        ns3::TypeId("ns3::wsn::uav::A2GLogDistanceLossModel")
            .SetParent<ns3::PropagationLossModel>()
            .SetGroupName("WsnUav")
            .AddConstructor<A2GLogDistanceLossModel>()
            .AddAttribute("A2GExponent",
                          "Path-loss exponent used when at least one endpoint is above the "
                          "altitude threshold (LoS-dominant).",
                          ns3::DoubleValue(2.2),
                          ns3::MakeDoubleAccessor(&A2GLogDistanceLossModel::m_a2gExponent),
                          ns3::MakeDoubleChecker<double>())
            .AddAttribute("G2GExponent",
                          "Path-loss exponent used when both endpoints are at or below the "
                          "altitude threshold (NLoS, ground-to-ground).",
                          ns3::DoubleValue(3.5),
                          ns3::MakeDoubleAccessor(&A2GLogDistanceLossModel::m_g2gExponent),
                          ns3::MakeDoubleChecker<double>())
            .AddAttribute("AltitudeThreshold",
                          "Altitude (m) above which a link is considered air-to-ground.",
                          ns3::DoubleValue(5.0),
                          ns3::MakeDoubleAccessor(&A2GLogDistanceLossModel::m_altitudeThreshold),
                          ns3::MakeDoubleChecker<double>())
            .AddAttribute("ReferenceDistance",
                          "Reference distance d0 (m) for path-loss formula.",
                          ns3::DoubleValue(1.0),
                          ns3::MakeDoubleAccessor(&A2GLogDistanceLossModel::m_referenceDistance),
                          ns3::MakeDoubleChecker<double>())
            .AddAttribute("ReferenceLoss",
                          "Reference loss (dB) at d0.",
                          ns3::DoubleValue(46.6),
                          ns3::MakeDoubleAccessor(&A2GLogDistanceLossModel::m_referenceLoss),
                          ns3::MakeDoubleChecker<double>());
    return tid;
}

A2GLogDistanceLossModel::A2GLogDistanceLossModel()
    : m_a2gExponent(2.2),
      m_g2gExponent(3.5),
      m_altitudeThreshold(5.0),
      m_referenceDistance(1.0),
      m_referenceLoss(46.6)
{
}

double
A2GLogDistanceLossModel::DoCalcRxPower(double txPowerDbm,
                                       ns3::Ptr<ns3::MobilityModel> a,
                                       ns3::Ptr<ns3::MobilityModel> b) const
{
    double za = a->GetPosition().z;
    double zb = b->GetPosition().z;
    double maxZ = std::max(za, zb);
    double n = (maxZ > m_altitudeThreshold) ? m_a2gExponent : m_g2gExponent;

    double d = a->GetDistanceFrom(b);
    if (d < m_referenceDistance)
    {
        d = m_referenceDistance;
    }
    double pathLossDb = m_referenceLoss + 10.0 * n * std::log10(d / m_referenceDistance);
    return txPowerDbm - pathLossDb;
}

int64_t
A2GLogDistanceLossModel::DoAssignStreams(int64_t stream)
{
    return stream;
}

}  // namespace ns3::wsn::uav
