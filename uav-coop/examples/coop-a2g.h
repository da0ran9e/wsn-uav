// The urban air-to-ground channel of uav-sar's A2G-RUN / A2G-SWEEP experiments,
// with the values of coop-params.h.
//
//   path loss   free space up to dref (= the flight altitude), then (d/dref)^-alpha
//   fading      Rician K, redrawn on every call -- every packet, every receiver
//
// One definition, included by exactly one translation unit per executable. The
// TypeId is this module's own, so it cannot clash with uav-sar's copy.

#ifndef UAVCOOP_COOP_A2G_H
#define UAVCOOP_COOP_A2G_H

#include "ns3/core-module.h"
#include "ns3/propagation-module.h"
#include "ns3/spectrum-module.h"

#include <cmath>

namespace ns3::uavcoop {

inline double A2gPathLossDb(double d, double alpha, double dref, double fspl1m) {
    if (d < dref) return fspl1m + 20.0 * std::log10(d);
    return fspl1m + 20.0 * std::log10(dref) + 10.0 * alpha * std::log10(d / dref);
}

class CoopRicianLossModel : public PropagationLossModel {
  public:
    static TypeId GetTypeId() {
        static TypeId tid = TypeId("ns3::uavcoop::CoopRicianLossModel")
                                .SetParent<PropagationLossModel>()
                                .AddConstructor<CoopRicianLossModel>()
                                .AddAttribute("K", "Rician K factor (linear)", DoubleValue(2.0),
                                              MakeDoubleAccessor(&CoopRicianLossModel::m_k),
                                              MakeDoubleChecker<double>(0.0));
        return tid;
    }
    CoopRicianLossModel() : m_n(CreateObject<NormalRandomVariable>()) {}

  private:
    double DoCalcRxPower(double txPowerDbm, Ptr<MobilityModel>, Ptr<MobilityModel>) const override {
        // Unit mean power: LoS part K/(K+1), scattered part 1/(K+1) split over I and Q.
        const double los = std::sqrt(m_k / (m_k + 1.0));
        const double sc = std::sqrt(1.0 / (m_k + 1.0) / 2.0);
        const double i = los + sc * m_n->GetValue();
        const double q = sc * m_n->GetValue();
        return txPowerDbm + 10.0 * std::log10(i * i + q * q);
    }
    int64_t DoAssignStreams(int64_t stream) override {
        m_n->SetStream(stream);
        return 1;
    }
    double m_k = 2.0;
    Ptr<NormalRandomVariable> m_n;
};
NS_OBJECT_ENSURE_REGISTERED(CoopRicianLossModel);

// Two-segment path loss, then Rician fading. `loss` returns the head of the chain.
inline Ptr<SpectrumChannel> BuildA2gChannel(double alpha, double dref, double kFactor,
                                            double fspl1m, Ptr<PropagationLossModel>& loss) {
    Ptr<SingleModelSpectrumChannel> ch = CreateObject<SingleModelSpectrumChannel>();
    // Free space (n = 2) from 1 m to dref, then alpha. Distance2 is pushed out of
    // reach so the third segment never applies.
    Ptr<ThreeLogDistancePropagationLossModel> pl = CreateObject<ThreeLogDistancePropagationLossModel>();
    pl->SetAttribute("Distance0", DoubleValue(1.0));
    pl->SetAttribute("Distance1", DoubleValue(dref));
    pl->SetAttribute("Distance2", DoubleValue(1e9));
    pl->SetAttribute("Exponent0", DoubleValue(2.0));
    pl->SetAttribute("Exponent1", DoubleValue(alpha));
    pl->SetAttribute("Exponent2", DoubleValue(alpha));
    pl->SetAttribute("ReferenceLoss", DoubleValue(fspl1m));
    Ptr<CoopRicianLossModel> f = CreateObject<CoopRicianLossModel>();
    f->SetAttribute("K", DoubleValue(kFactor));
    pl->SetNext(f);
    ch->AddPropagationLossModel(pl);
    ch->SetPropagationDelayModel(CreateObject<ConstantSpeedPropagationDelayModel>());
    loss = pl;
    return ch;
}

}  // namespace ns3::uavcoop

#endif
