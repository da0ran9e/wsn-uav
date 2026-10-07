// The urban ground-to-ground channel of uav-sar's G2G-CHAIN experiment, with the
// values of coop-params.h:
//
//   path loss   log-distance from 1 m, exponent n (3.5)
//   shadowing   log-normal, drawn ONCE per node pair for the whole run, the same
//               both ways (reciprocity): a bad link stays bad
//   fading      Rician K (0: Rayleigh), held over a block of CoherenceTime and
//               redrawn at block boundaries; each link has its own block phase, and
//               a->b and b->a share the fade
//
// One definition, included by exactly one translation unit per executable. The
// TypeId is this module's own, so it cannot clash with uav-sar's copy.

#ifndef UAVCOOP_COOP_G2G_H
#define UAVCOOP_COOP_G2G_H

#include "ns3/core-module.h"
#include "ns3/propagation-module.h"
#include "ns3/spectrum-module.h"

#include <cmath>
#include <map>
#include <utility>

namespace ns3::uavcoop {

class CoopG2gLossModel : public PropagationLossModel {
  public:
    static TypeId GetTypeId() {
        static TypeId tid =
            TypeId("ns3::uavcoop::CoopG2gLossModel")
                .SetParent<PropagationLossModel>()
                .AddConstructor<CoopG2gLossModel>()
                .AddAttribute("ShadowSigmaDb", "log-normal shadowing, per pair, static",
                              DoubleValue(7.8),
                              MakeDoubleAccessor(&CoopG2gLossModel::m_sigma),
                              MakeDoubleChecker<double>(0.0))
                .AddAttribute("CoherenceTime", "fading block length, s (<= 0: no fading)",
                              DoubleValue(0.1),
                              MakeDoubleAccessor(&CoopG2gLossModel::m_coh),
                              MakeDoubleChecker<double>())
                .AddAttribute("K", "Rician K factor (0 = Rayleigh)", DoubleValue(0.0),
                              MakeDoubleAccessor(&CoopG2gLossModel::m_k),
                              MakeDoubleChecker<double>(0.0));
        return tid;
    }
    CoopG2gLossModel()
        : m_n(CreateObject<NormalRandomVariable>()),
          m_u(CreateObject<UniformRandomVariable>()) {}

    // The static shadowing of a pair, dB (drawn on first use).
    double ShadowDb(Ptr<MobilityModel> a, Ptr<MobilityModel> b) const {
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
    State& Link(Ptr<MobilityModel> a, Ptr<MobilityModel> b) const {
        const void* pa = PeekPointer(a);
        const void* pb = PeekPointer(b);
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
    double DoCalcRxPower(double txPowerDbm, Ptr<MobilityModel> a,
                         Ptr<MobilityModel> b) const override {
        State& st = Link(a, b);
        double fade = 0.0;
        if (m_coh > 0) {
            const int64_t blk =
                (int64_t)std::floor((Simulator::Now().GetSeconds() + st.phase) / m_coh);
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
    Ptr<NormalRandomVariable> m_n;
    Ptr<UniformRandomVariable> m_u;
    mutable std::map<std::pair<const void*, const void*>, State> m_links;
};
NS_OBJECT_ENSURE_REGISTERED(CoopG2gLossModel);

inline Ptr<SpectrumChannel> BuildG2gChannel(double n, double sigmaDb, double coherenceS, double kFactor,
                                            double fspl1m, Ptr<CoopG2gLossModel>& link) {
    Ptr<SingleModelSpectrumChannel> ch = CreateObject<SingleModelSpectrumChannel>();
    Ptr<LogDistancePropagationLossModel> pl = CreateObject<LogDistancePropagationLossModel>();
    pl->SetAttribute("Exponent", DoubleValue(n));
    pl->SetAttribute("ReferenceDistance", DoubleValue(1.0));
    pl->SetAttribute("ReferenceLoss", DoubleValue(fspl1m));
    link = CreateObject<CoopG2gLossModel>();
    link->SetAttribute("ShadowSigmaDb", DoubleValue(sigmaDb));
    link->SetAttribute("CoherenceTime", DoubleValue(coherenceS));
    link->SetAttribute("K", DoubleValue(kFactor));
    pl->SetNext(link);
    ch->AddPropagationLossModel(pl);
    ch->SetPropagationDelayModel(CreateObject<ConstantSpeedPropagationDelayModel>());
    return ch;
}

}  // namespace ns3::uavcoop

#endif
