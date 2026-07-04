#include "forest-a2g-loss.h"
#include "../common/sar-params.h"

#include "ns3/mobility-model.h"
#include "ns3/node.h"

#include <algorithm>
#include <cmath>

namespace ns3::uavsar {

NS_OBJECT_ENSURE_REGISTERED(ForestA2gLossModel);

ns3::TypeId ForestA2gLossModel::GetTypeId() {
    static ns3::TypeId tid = ns3::TypeId("ns3::uavsar::ForestA2gLossModel")
                                 .SetParent<ns3::PropagationLossModel>()
                                 .SetGroupName("uav-sar")
                                 .AddConstructor<ForestA2gLossModel>();
    return tid;
}

ForestA2gLossModel::ForestA2gLossModel() {
    m_u01 = ns3::CreateObject<ns3::UniformRandomVariable>();
}

double ForestA2gLossModel::PLos(double thetaDeg) {
    return 1.0 / (1.0 + params::kLosA *
                            std::exp(-params::kLosB * (thetaDeg - params::kLosA)));
}

double ForestA2gLossModel::VegLossDb(double thetaDeg) {
    double s = std::sin(std::max(2.0, thetaDeg) * M_PI / 180.0);  // clamp grazing
    double dVeg = params::kAltThresholdM / s;                     // canopy crossing
    return params::kVegAmaxDb *
           (1.0 - std::exp(-dVeg * params::kVegGammaDbPerM / params::kVegAmaxDb));
}

double ForestA2gLossModel::DoCalcRxPower(double txPowerDbm,
                                         ns3::Ptr<ns3::MobilityModel> a,
                                         ns3::Ptr<ns3::MobilityModel> b) const {
    double d = std::max(params::kRefDistanceM, a->GetDistanceFrom(b));
    ns3::Vector pa = a->GetPosition(), pb = b->GetPosition();
    bool aAir = pa.z > params::kAltThresholdM;
    bool bAir = pb.z > params::kAltThresholdM;

    double pl;
    if (!aAir && !bAir) {
        // ground-ground through the forest
        pl = params::kRefLossDb +
             10.0 * params::kG2GExponent * std::log10(d / params::kRefDistanceM);
    } else if (aAir && bAir) {
        // air-air above the canopy: free space
        pl = params::kRefLossDb + 20.0 * std::log10(d / params::kRefDistanceM) +
             params::kEtaLosDb;
    } else {
        // air-ground: elevation-angle LoS with a frozen per-pair quantile
        double dz = std::fabs(pa.z - pb.z);
        double dh = std::hypot(pa.x - pb.x, pa.y - pb.y);
        double theta = std::atan2(dz, std::max(1.0, dh)) * 180.0 / M_PI;

        uint32_t ia = 0, ib = 0;
        ns3::Ptr<ns3::Node> na = a->GetObject<ns3::Node>();
        ns3::Ptr<ns3::Node> nb = b->GetObject<ns3::Node>();
        if (na) ia = na->GetId();
        if (nb) ib = nb->GetId();
        auto key = std::minmax(ia, ib);
        auto it = m_quantile.find(key);
        if (it == m_quantile.end())
            it = m_quantile.emplace(key, m_u01->GetValue()).first;

        double fspl =
            params::kRefLossDb + 20.0 * std::log10(d / params::kRefDistanceM);
        bool los = it->second < PLos(theta);
        pl = fspl + (los ? params::kEtaLosDb : VegLossDb(theta));
    }
    return txPowerDbm - pl;
}

int64_t ForestA2gLossModel::DoAssignStreams(int64_t stream) {
    m_u01->SetStream(stream);
    return 1;
}

}  // namespace ns3::uavsar
