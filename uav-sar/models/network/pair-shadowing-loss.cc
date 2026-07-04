#include "pair-shadowing-loss.h"
#include "../common/sar-params.h"

#include "ns3/mobility-model.h"
#include "ns3/node.h"
#include "ns3/double.h"

#include <algorithm>

namespace ns3::uavsar {

NS_OBJECT_ENSURE_REGISTERED(PairShadowingLossModel);

ns3::TypeId PairShadowingLossModel::GetTypeId() {
    static ns3::TypeId tid = ns3::TypeId("ns3::uavsar::PairShadowingLossModel")
                                 .SetParent<ns3::PropagationLossModel>()
                                 .SetGroupName("uav-sar")
                                 .AddConstructor<PairShadowingLossModel>();
    return tid;
}

PairShadowingLossModel::PairShadowingLossModel()
    : m_sigmaDb(params::kShadowingSigmaDb),
      m_sigmaA2gDb(params::kShadowSigmaA2gDb) {
    m_rv = ns3::CreateObject<ns3::NormalRandomVariable>();
    m_rv->SetAttribute("Mean", ns3::DoubleValue(0.0));
    m_rv->SetAttribute("Variance", ns3::DoubleValue(1.0));  // scaled by sigma below
}

double PairShadowingLossModel::DoCalcRxPower(double txPowerDbm,
                                             ns3::Ptr<ns3::MobilityModel> a,
                                             ns3::Ptr<ns3::MobilityModel> b) const {
    uint32_t ia = 0, ib = 0;
    ns3::Ptr<ns3::Node> na = a->GetObject<ns3::Node>();
    ns3::Ptr<ns3::Node> nb = b->GetObject<ns3::Node>();
    if (na) ia = na->GetId();
    if (nb) ib = nb->GetId();
    auto key = std::minmax(ia, ib);

    auto it = m_cache.find(key);
    if (it == m_cache.end()) {
        double unit = m_rv->GetValue();  // one persistent UNIT draw per pair
        it = m_cache.emplace(key, unit).first;
    }
    // Scale by the link-class sigma: links with an airborne endpoint use the
    // smaller residual (LoS/foliage excess is now explicit in ForestA2gLoss;
    // keeping the full woodland sigma there would double-count vegetation).
    bool air = a->GetPosition().z > params::kAltThresholdM ||
               b->GetPosition().z > params::kAltThresholdM;
    double sigma = air ? m_sigmaA2gDb : m_sigmaDb;
    return txPowerDbm + it->second * sigma;
}

int64_t PairShadowingLossModel::DoAssignStreams(int64_t stream) {
    m_rv->SetStream(stream);
    return 1;
}

}  // namespace ns3::uavsar
