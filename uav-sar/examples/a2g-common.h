// The urban air-to-ground channel shared by the a2g-* experiments.
//
// URBAN BRANCH ONLY. Not for the forest SAR model, which has its own channel
// stack (ForestA2gLossModel) and parameters (sar-params.h).
//
//   path loss   free space up to dref, then (d/dref)^-alpha. The spec anchors
//               dref at the flight altitude H.
//   fading      Rician K (default 2), redrawn on every call -- every packet,
//               every receiver. Nakagami m is available for comparison only:
//               matched on mean and variance it still fades ~50x less often at
//               -30 dB, which is what decides a packet run.
//
// One definition, included by exactly one translation unit per executable.

#ifndef UAVSAR_A2G_COMMON_H
#define UAVSAR_A2G_COMMON_H

#include "ns3/core-module.h"
#include "ns3/propagation-module.h"
#include "ns3/spectrum-module.h"

#include <cmath>
#include <cstdint>
#include <string>

namespace a2g {

constexpr double   kFspl1mDb  = 40.05;   // 20 log10(4 pi / lambda), 2.4 GHz
constexpr double   kPeriodS   = 0.010;   // IEEE 802.15.4 default slot
constexpr uint32_t kPsduBytes = 127;     // aMaxPhyPacketSize
constexpr uint32_t kChannel   = 11;      // 2405 MHz

inline double PathLossDb(double d, double alpha, double dref) {
    if (d < dref) return kFspl1mDb + 20.0 * std::log10(d);
    return kFspl1mDb + 20.0 * std::log10(dref) + 10.0 * alpha * std::log10(d / dref);
}

}  // namespace a2g

// ---- Rician fading, redrawn on every call (i.e. every packet, every receiver) --
class RicianFadingLossModel : public ns3::PropagationLossModel {
  public:
    static ns3::TypeId GetTypeId() {
        static ns3::TypeId tid =
            ns3::TypeId("ns3::RicianFadingLossModel")
                .SetParent<ns3::PropagationLossModel>()
                .AddConstructor<RicianFadingLossModel>()
                .AddAttribute("K", "Rician K factor (linear)", ns3::DoubleValue(2.0),
                              ns3::MakeDoubleAccessor(&RicianFadingLossModel::m_k),
                              ns3::MakeDoubleChecker<double>(0.0));
        return tid;
    }
    RicianFadingLossModel() : m_n(ns3::CreateObject<ns3::NormalRandomVariable>()) {}

  private:
    double DoCalcRxPower(double txPowerDbm, ns3::Ptr<ns3::MobilityModel>,
                         ns3::Ptr<ns3::MobilityModel>) const override {
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
    ns3::Ptr<ns3::NormalRandomVariable> m_n;
};
NS_OBJECT_ENSURE_REGISTERED(RicianFadingLossModel);

namespace a2g {

// Two-segment path loss, then the fading. fading: "rician" | "nakagami" | "none".
inline ns3::Ptr<ns3::SpectrumChannel>
BuildChannel(double alpha, double dref, const std::string& fading, double kFactor,
             double nakagamiM) {
    using namespace ns3;
    Ptr<SingleModelSpectrumChannel> ch = CreateObject<SingleModelSpectrumChannel>();

    // Free space (n = 2) from 1 m to dref, then alpha. Distance2 is pushed out of
    // reach so the third segment never applies.
    Ptr<ThreeLogDistancePropagationLossModel> pl =
        CreateObject<ThreeLogDistancePropagationLossModel>();
    pl->SetAttribute("Distance0", DoubleValue(1.0));
    pl->SetAttribute("Distance1", DoubleValue(dref));
    pl->SetAttribute("Distance2", DoubleValue(1e9));
    pl->SetAttribute("Exponent0", DoubleValue(2.0));
    pl->SetAttribute("Exponent1", DoubleValue(alpha));
    pl->SetAttribute("Exponent2", DoubleValue(alpha));
    pl->SetAttribute("ReferenceLoss", DoubleValue(kFspl1mDb));

    if (fading == "rician") {
        Ptr<RicianFadingLossModel> f = CreateObject<RicianFadingLossModel>();
        f->SetAttribute("K", DoubleValue(kFactor));
        pl->SetNext(f);
    } else if (fading == "nakagami") {
        Ptr<NakagamiPropagationLossModel> f = CreateObject<NakagamiPropagationLossModel>();
        f->SetAttribute("m0", DoubleValue(nakagamiM));
        f->SetAttribute("m1", DoubleValue(nakagamiM));
        f->SetAttribute("m2", DoubleValue(nakagamiM));
        pl->SetNext(f);
    } else {
        NS_ABORT_MSG_IF(fading != "none", "unknown fading model " << fading);
    }
    ch->AddPropagationLossModel(pl);
    ch->SetPropagationDelayModel(CreateObject<ConstantSpeedPropagationDelayModel>());
    return ch;
}

}  // namespace a2g

#endif
