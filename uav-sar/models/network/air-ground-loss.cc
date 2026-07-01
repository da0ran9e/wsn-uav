#include "air-ground-loss.h"
#include "../common/sar-params.h"

#include "ns3/mobility-model.h"

#include <algorithm>
#include <cmath>

namespace ns3::uavsar {

NS_OBJECT_ENSURE_REGISTERED(AirGroundLossModel);

ns3::TypeId AirGroundLossModel::GetTypeId() {
    static ns3::TypeId tid =
        ns3::TypeId("ns3::uavsar::AirGroundLossModel")
            .SetParent<ns3::PropagationLossModel>()
            .SetGroupName("uav-sar")
            .AddConstructor<AirGroundLossModel>();
    return tid;
}

AirGroundLossModel::AirGroundLossModel()
    : m_a2g(params::kA2GExponent),
      m_g2g(params::kG2GExponent),
      m_altThresh(params::kAltThresholdM),
      m_refDist(params::kRefDistanceM),
      m_refLoss(params::kRefLossDb) {}

double AirGroundLossModel::DoCalcRxPower(double txPowerDbm,
                                        ns3::Ptr<ns3::MobilityModel> a,
                                        ns3::Ptr<ns3::MobilityModel> b) const {
    double dist = a->GetDistanceFrom(b);         // 3D distance (m)
    if (dist < m_refDist) dist = m_refDist;
    double za = a->GetPosition().z;
    double zb = b->GetPosition().z;
    double n = (std::max(za, zb) > m_altThresh) ? m_a2g : m_g2g;  // A2G vs G2G
    double pl = m_refLoss + 10.0 * n * std::log10(dist / m_refDist);
    return txPowerDbm - pl;
}

int64_t AirGroundLossModel::DoAssignStreams(int64_t) { return 0; }

}  // namespace ns3::uavsar
