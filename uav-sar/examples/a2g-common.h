// The urban channels shared by the a2g-* and g2g-* experiments: air-to-ground
// (below) and ground-to-ground (G2gLinkLossModel, further down).
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
#include <map>
#include <string>
#include <utility>

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


// ---- G2G: ground node to ground node ------------------------------------------
//
// Static nodes see a static channel. Unlike the passing UAV, nothing here moves
// except the scatterers around the link (cars, people), so:
//   shadowing  log-normal, drawn ONCE per node pair for the whole run, and the
//              same both ways (reciprocity). A bad link stays bad.
//   fading     Rician K (K = 0: Rayleigh, all-NLoS), held constant over a block of
//              CoherenceTime and redrawn at block boundaries. Each link has its
//              own random block phase, and a->b and b->a share the fade -- the
//              ACK sees the channel the data saw.
// Whether a retransmission meets a fresh fade or the same one is decided by the
// coherence time, which is why it is a parameter and not an assumption.
class G2gLinkLossModel : public ns3::PropagationLossModel {
  public:
    static ns3::TypeId GetTypeId() {
        static ns3::TypeId tid =
            ns3::TypeId("ns3::G2gLinkLossModel")
                .SetParent<ns3::PropagationLossModel>()
                .AddConstructor<G2gLinkLossModel>()
                .AddAttribute("ShadowSigmaDb", "log-normal shadowing, per pair, static",
                              ns3::DoubleValue(7.8),
                              ns3::MakeDoubleAccessor(&G2gLinkLossModel::m_sigma),
                              ns3::MakeDoubleChecker<double>(0.0))
                .AddAttribute("CoherenceTime", "fading block length, s (<= 0: no fading)",
                              ns3::DoubleValue(0.1),
                              ns3::MakeDoubleAccessor(&G2gLinkLossModel::m_coh),
                              ns3::MakeDoubleChecker<double>())
                .AddAttribute("K", "Rician K factor (0 = Rayleigh)", ns3::DoubleValue(0.0),
                              ns3::MakeDoubleAccessor(&G2gLinkLossModel::m_k),
                              ns3::MakeDoubleChecker<double>(0.0));
        return tid;
    }
    G2gLinkLossModel()
        : m_n(ns3::CreateObject<ns3::NormalRandomVariable>()),
          m_u(ns3::CreateObject<ns3::UniformRandomVariable>()) {}

    // The static shadowing of a pair, dB (drawn on first use).
    double ShadowDb(ns3::Ptr<ns3::MobilityModel> a, ns3::Ptr<ns3::MobilityModel> b) const {
        return Link(a, b).shadowDb;
    }
    // Draw statistics, for the caller to check against the intended distributions.
    mutable uint64_t nShadow = 0, nFade = 0, nFade10 = 0, nFade20 = 0;
    mutable double sumShadow = 0, sumShadow2 = 0, sumFade = 0;

  private:
    struct State {
        double shadowDb = 0, phase = 0, fadeDb = 0;
        int64_t block = -1;
    };
    State& Link(ns3::Ptr<ns3::MobilityModel> a, ns3::Ptr<ns3::MobilityModel> b) const {
        const void* pa = ns3::PeekPointer(a);
        const void* pb = ns3::PeekPointer(b);
        auto key = pa < pb ? std::make_pair(pa, pb) : std::make_pair(pb, pa);
        auto it = m_links.find(key);
        if (it != m_links.end()) return it->second;
        State st;
        st.shadowDb = m_sigma * m_n->GetValue();
        st.phase = m_u->GetValue(0.0, m_coh > 0 ? m_coh : 1.0);
        nShadow++;
        sumShadow += st.shadowDb;
        sumShadow2 += st.shadowDb * st.shadowDb;
        return m_links.emplace(key, st).first->second;
    }
    double DoCalcRxPower(double txPowerDbm, ns3::Ptr<ns3::MobilityModel> a,
                         ns3::Ptr<ns3::MobilityModel> b) const override {
        State& st = Link(a, b);
        double fade = 0.0;
        if (m_coh > 0) {
            const int64_t blk =
                (int64_t)std::floor((ns3::Simulator::Now().GetSeconds() + st.phase) / m_coh);
            if (blk != st.block) {
                const double los = std::sqrt(m_k / (m_k + 1.0));
                const double sc = std::sqrt(1.0 / (m_k + 1.0) / 2.0);
                const double i = los + sc * m_n->GetValue();
                const double q = sc * m_n->GetValue();
                st.fadeDb = 10.0 * std::log10(i * i + q * q);
                st.block = blk;
                nFade++;
                sumFade += i * i + q * q;
                if (st.fadeDb < -10) nFade10++;
                if (st.fadeDb < -20) nFade20++;
            }
            fade = st.fadeDb;
        }
        return txPowerDbm - st.shadowDb + fade;
    }
    int64_t DoAssignStreams(int64_t stream) override {
        m_n->SetStream(stream);
        m_u->SetStream(stream + 1);
        return 2;
    }
    double m_sigma = 7.8, m_coh = 0.1, m_k = 0.0;
    ns3::Ptr<ns3::NormalRandomVariable> m_n;
    ns3::Ptr<ns3::UniformRandomVariable> m_u;
    mutable std::map<std::pair<const void*, const void*>, State> m_links;
};
NS_OBJECT_ENSURE_REGISTERED(G2gLinkLossModel);

namespace a2g {

// Log-distance from 1 m with exponent n, then the static/block link model.
inline ns3::Ptr<ns3::SpectrumChannel>
BuildG2gChannel(double n, double sigmaDb, double coherenceS, double kFactor,
                ns3::Ptr<G2gLinkLossModel>& link) {
    using namespace ns3;
    Ptr<SingleModelSpectrumChannel> ch = CreateObject<SingleModelSpectrumChannel>();
    Ptr<LogDistancePropagationLossModel> pl = CreateObject<LogDistancePropagationLossModel>();
    pl->SetAttribute("Exponent", DoubleValue(n));
    pl->SetAttribute("ReferenceDistance", DoubleValue(1.0));
    pl->SetAttribute("ReferenceLoss", DoubleValue(kFspl1mDb));
    link = CreateObject<G2gLinkLossModel>();
    link->SetAttribute("ShadowSigmaDb", DoubleValue(sigmaDb));
    link->SetAttribute("CoherenceTime", DoubleValue(coherenceS));
    link->SetAttribute("K", DoubleValue(kFactor));
    pl->SetNext(link);
    ch->AddPropagationLossModel(pl);
    ch->SetPropagationDelayModel(CreateObject<ConstantSpeedPropagationDelayModel>());
    return ch;
}

}  // namespace a2g

#endif
