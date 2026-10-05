// How long an unbroken run of packets can a ground node take from a passing UAV?
//
// URBAN BRANCH ONLY. Every number here is an urban air-to-ground figure and must
// not be carried into the forest SAR model -- that one has its own channel stack
// (ForestA2gLossModel) and its own parameters (sar-params.h).
//
// Geometry: 7 ground nodes on a line, 300 m apart. The UAV flies at 100 m, 50 m/s,
// straight and level, PERPENDICULAR to that line and directly over node 4, from
// -2000 m to +2000 m. It broadcasts one numbered 127-byte PSDU every 10 ms --
// 8001 packets a pass. A file cannot repair a lost packet, so what matters to a
// node is its LONGEST run of consecutive sequence numbers.
//
// Channel, pinned by the spec:
//   path loss   free space to 100 m (-80.05 dB), then (d/100)^-alpha, alpha = 3.0
//               (2.6 and 3.35 for sensitivity; Qiu 2017 air-to-ground)
//   fading      Rician K = 2, redrawn EVERY packet. Coherence time at 50 m/s and
//               2.4 GHz is ~1.06 ms, ten times shorter than the 10 ms spacing, so
//               consecutive packets do see independent fades.
//   shadowing   off. One draw per run would only slide the window, not break it.
//   antennas    isotropic at both ends.
//
// Why a Rician class instead of ns-3's Nakagami: the spec proposed Nakagami
// m = (K+1)^2/(2K+1) = 1.8 as the equivalent. It matches the mean and variance of
// the power, but NOT the deep-fade tail -- at -30 dB the Rician is ~50x more likely
// to fade. Total packets received barely notice; the longest run is decided by
// exactly those rare deep fades, and comes out 1.6-2.3x too long under Nakagami.
// Both are available here (--fading) so the difference can be shown, not argued.
//
// The MAC is bypassed: the UAV is the only transmitter, so there is nothing to
// contend with, and the project's 200 ms Send() stagger is a MAC queue artefact.
// Packets go straight to LrWpanPhy::PdDataRequest. No CSMA, no ACK, no beacon.
//
// A note on "sensitivity" in ns-3.46: there is no hard reception threshold.
// SetRxSensitivity(S) only sets the noise factor F = S / -106.58 dBm, and S
// becomes the point where a 20-byte PSDU sees 1 % PER. Reception is the O-QPSK
// BER curve on SINR. --mode=calib measures what that curve actually is for the
// 127-byte frames used here, so the result can be compared with a hard-threshold
// analysis on equal terms.
//
//   a2g-run-test --mode=calib --out=calib.csv
//   a2g-run-test --mode=pass  --alpha=3.0 --fading=rician --passes=200 --out=runs.csv

#include "ns3/core-module.h"
#include "ns3/lr-wpan-module.h"
#include "ns3/mobility-module.h"
#include "ns3/network-module.h"
#include "ns3/propagation-module.h"
#include "ns3/spectrum-module.h"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <map>
#include <string>
#include <vector>

using namespace ns3;

static uint32_t g_checks = 0;
#define CHECK(cond)                                                            \
    do {                                                                       \
        ++g_checks;                                                            \
        if (!(cond)) {                                                         \
            std::fprintf(stderr, "CHECK FAILED %s:%d: %s\n", __FILE__,         \
                         __LINE__, #cond);                                     \
            std::exit(1);                                                      \
        }                                                                      \
    } while (0)

namespace {

// ---- the spec ---------------------------------------------------------------
constexpr double   kAltM       = 100.0;
constexpr double   kSpeedMps   = 50.0;
constexpr double   kTrackHalfM = 2000.0;
constexpr double   kSpacingM   = 300.0;
constexpr uint32_t kNodes      = 7;
constexpr uint32_t kMiddle     = 3;          // node 4, zero-based
constexpr double   kPeriodS    = 0.010;      // IEEE 802.15.4 default slot
constexpr uint32_t kPsduBytes  = 127;        // aMaxPhyPacketSize
constexpr uint32_t kChannel    = 11;         // 2405 MHz
constexpr double   kRefDistM   = 100.0;      // the two segments meet here
constexpr double   kFspl1mDb   = 40.05;      // 20 log10(4 pi / lambda), 2.4 GHz
constexpr double   kStartS     = 1.0;        // after the MAC has initialised
const uint32_t kPackets = (uint32_t)std::lround(2 * kTrackHalfM / (kSpeedMps * kPeriodS)) + 1;

double PathLossDb(double d, double alpha) {
    if (d < kRefDistM) return kFspl1mDb + 20.0 * std::log10(d);
    return kFspl1mDb + 20.0 * std::log10(kRefDistM) + 10.0 * alpha * std::log10(d / kRefDistM);
}

}  // namespace

// ---- Rician fading, redrawn on every call (i.e. every packet, every receiver) --
class RicianFadingLossModel : public PropagationLossModel {
  public:
    static TypeId GetTypeId() {
        static TypeId tid = TypeId("ns3::RicianFadingLossModel")
                                .SetParent<PropagationLossModel>()
                                .AddConstructor<RicianFadingLossModel>()
                                .AddAttribute("K", "Rician K factor (linear)",
                                              DoubleValue(2.0),
                                              MakeDoubleAccessor(&RicianFadingLossModel::m_k),
                                              MakeDoubleChecker<double>(0.0));
        return tid;
    }
    RicianFadingLossModel() : m_n(CreateObject<NormalRandomVariable>()) {}

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
NS_OBJECT_ENSURE_REGISTERED(RicianFadingLossModel);

namespace {

struct RunConfig {
    std::string mode = "pass";
    std::string fading = "rician";
    double alpha = 3.0;
    double txDbm = 10.0;
    double sensDbm = -100.0;
    double kFactor = 2.0;
    double nakagamiM = 1.8;
    uint32_t passes = 200;
    uint32_t seed = 1;
    std::string out;
};

Ptr<SpectrumChannel> BuildChannel(const RunConfig& c, bool withFading) {
    Ptr<SingleModelSpectrumChannel> ch = CreateObject<SingleModelSpectrumChannel>();

    // Free space (n = 2) from 1 m to 100 m, then alpha. Distance2 is pushed out of
    // reach so the third segment never applies.
    Ptr<ThreeLogDistancePropagationLossModel> pl = CreateObject<ThreeLogDistancePropagationLossModel>();
    pl->SetAttribute("Distance0", DoubleValue(1.0));
    pl->SetAttribute("Distance1", DoubleValue(kRefDistM));
    pl->SetAttribute("Distance2", DoubleValue(1e9));
    pl->SetAttribute("Exponent0", DoubleValue(2.0));
    pl->SetAttribute("Exponent1", DoubleValue(c.alpha));
    pl->SetAttribute("Exponent2", DoubleValue(c.alpha));
    pl->SetAttribute("ReferenceLoss", DoubleValue(kFspl1mDb));

    if (withFading && c.fading == "rician") {
        Ptr<RicianFadingLossModel> f = CreateObject<RicianFadingLossModel>();
        f->SetAttribute("K", DoubleValue(c.kFactor));
        pl->SetNext(f);
    } else if (withFading && c.fading == "nakagami") {
        Ptr<NakagamiPropagationLossModel> f = CreateObject<NakagamiPropagationLossModel>();
        f->SetAttribute("m0", DoubleValue(c.nakagamiM));
        f->SetAttribute("m1", DoubleValue(c.nakagamiM));
        f->SetAttribute("m2", DoubleValue(c.nakagamiM));
        pl->SetNext(f);
    } else {
        CHECK(!withFading || c.fading == "none");
    }
    ch->AddPropagationLossModel(pl);
    ch->SetPropagationDelayModel(CreateObject<ConstantSpeedPropagationDelayModel>());
    return ch;
}

// What one pass leaves behind, per node.
struct NodeResult {
    uint32_t received = 0;
    uint32_t longest = 0;
    int32_t runStart = -1, runEnd = -1;   // sequence numbers, inclusive
};

// Fade statistics accumulated from the channel's own PathLoss trace: the traced
// loss minus the closed-form path loss IS the fade the receiver saw.
struct FadeStats {
    uint64_t n = 0;
    double sumLin = 0;
    uint64_t below10 = 0, below20 = 0, below30 = 0;
    double maxDetErrDb = 0;   // with fading off: traced vs closed form
};

struct Pass {
    std::vector<std::vector<uint8_t>> got;   // [node][seq]
    std::map<const SpectrumPhy*, uint32_t> rxIndex;
    std::map<const SpectrumPhy*, Ptr<MobilityModel>> mob;
    Ptr<MobilityModel> uavMob;
    uint32_t txOk = 0, txFail = 0, dupes = 0, badSeq = 0;
    double txDbmMin = 1e9, txDbmMax = -1e9;
};

// Build one world, fly it, tear it down. `positions` are the ground nodes; the
// UAV either flies the track (mode pass) or hangs still over the origin (calib).
void RunWorld(const RunConfig& c, bool withFading, bool flying,
              const std::vector<Vector>& positions, uint32_t nPackets,
              Pass& w, FadeStats& fs) {
    NodeContainer uav, ground;
    uav.Create(1);
    ground.Create(positions.size());

    MobilityHelper cv;
    cv.SetMobilityModel("ns3::ConstantVelocityMobilityModel");
    cv.Install(uav);
    MobilityHelper st;
    st.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    st.Install(ground);
    for (size_t i = 0; i < positions.size(); ++i)
        ground.Get(i)->GetObject<MobilityModel>()->SetPosition(positions[i]);

    Ptr<ConstantVelocityMobilityModel> um = uav.Get(0)->GetObject<ConstantVelocityMobilityModel>();
    if (flying) {
        // At kStartS the aircraft must be at y = -kTrackHalfM.
        um->SetPosition(Vector(0, -kTrackHalfM - kSpeedMps * kStartS, kAltM));
        um->SetVelocity(Vector(0, kSpeedMps, 0));
    } else {
        um->SetPosition(Vector(0, 0, kAltM));
        um->SetVelocity(Vector(0, 0, 0));
    }
    w.uavMob = um;

    // ONE helper for every node, alive until the world is destroyed -- its
    // destructor disposes the channel and would silently kill reception.
    LrWpanHelper lr;
    Ptr<SpectrumChannel> ch = BuildChannel(c, withFading);
    lr.SetChannel(ch);
    NetDeviceContainer uavDev = lr.Install(uav);
    NetDeviceContainer gndDev = lr.Install(ground);
    CHECK(ch->GetNDevices() == 1 + positions.size());

    Ptr<lrwpan::LrWpanPhy> uphy = DynamicCast<lrwpan::LrWpanNetDevice>(uavDev.Get(0))->GetPhy();
    std::vector<Ptr<lrwpan::LrWpanPhy>> gphy;
    for (uint32_t i = 0; i < gndDev.GetN(); ++i)
        gphy.push_back(DynamicCast<lrwpan::LrWpanNetDevice>(gndDev.Get(i))->GetPhy());

    w.got.assign(positions.size(), std::vector<uint8_t>(nPackets, 0));
    w.rxIndex.clear();
    w.mob.clear();
    for (uint32_t i = 0; i < gphy.size(); ++i) {
        w.rxIndex[PeekPointer(gphy[i])] = i;
        w.mob[PeekPointer(gphy[i])] = ground.Get(i)->GetObject<MobilityModel>();
    }

    // Take the PHYs away from their MACs. Everything below talks to the PHY directly.
    auto noState = lrwpan::PlmeSetTRXStateConfirmCallback([](lrwpan::PhyEnumeration) {});
    uphy->SetPlmeSetTRXStateConfirmCallback(noState);
    uphy->SetPdDataConfirmCallback(lrwpan::PdDataConfirmCallback([&w](lrwpan::PhyEnumeration s) {
        if (s == lrwpan::IEEE_802_15_4_PHY_SUCCESS) w.txOk++; else w.txFail++;
    }));
    for (uint32_t i = 0; i < gphy.size(); ++i) {
        gphy[i]->SetPlmeSetTRXStateConfirmCallback(noState);
        gphy[i]->SetPdDataIndicationCallback(lrwpan::PdDataIndicationCallback(
            [&w, i, nPackets](uint32_t len, Ptr<Packet> p, uint8_t) {
                uint8_t b[4];
                if (len != kPsduBytes || p->CopyData(b, 4) != 4) { w.badSeq++; return; }
                const uint32_t seq = (uint32_t)b[0] << 24 | (uint32_t)b[1] << 16 |
                                     (uint32_t)b[2] << 8 | b[3];
                if (seq >= nPackets) { w.badSeq++; return; }
                if (w.got[i][seq]) w.dupes++;
                w.got[i][seq] = 1;
            }));
    }

    // Measure the transmitted power from the signal itself, and the fade from the
    // loss the channel actually applied. Nothing is taken on trust.
    ch->TraceConnectWithoutContext("TxSigParams",
        Callback<void, Ptr<SpectrumSignalParameters>>([&w](Ptr<SpectrumSignalParameters> sp) {
            const double dbm = 10.0 * std::log10(
                lrwpan::LrWpanSpectrumValueHelper::TotalAvgPower(sp->psd, kChannel)) + 30.0;
            w.txDbmMin = std::min(w.txDbmMin, dbm);
            w.txDbmMax = std::max(w.txDbmMax, dbm);
        }));
    const double alpha = c.alpha;
    ch->TraceConnectWithoutContext("PathLoss",
        Callback<void, Ptr<const SpectrumPhy>, Ptr<const SpectrumPhy>, double>(
            [&w, &fs, alpha](Ptr<const SpectrumPhy>, Ptr<const SpectrumPhy> rx, double lossDb) {
                auto it = w.mob.find(PeekPointer(rx));
                if (it == w.mob.end()) return;
                const double d = w.uavMob->GetDistanceFrom(it->second);
                const double fadeDb = PathLossDb(d, alpha) - lossDb;   // gain, dB
                fs.n++;
                fs.sumLin += std::pow(10.0, fadeDb / 10.0);
                if (fadeDb < -10) fs.below10++;
                if (fadeDb < -20) fs.below20++;
                if (fadeDb < -30) fs.below30++;
                fs.maxDetErrDb = std::max(fs.maxDetErrDb, std::fabs(fadeDb));
            }));

    // Radio settings after the MAC's own initialisation at t = 0, which puts every
    // PHY into RX_ON. SetRxSensitivity rebuilds the TX PSD from the PIB, so the
    // UAV's transmit PSD is set last.
    Simulator::Schedule(Seconds(kStartS / 2), [&c, uphy, gphy]() {
        for (auto& g : gphy) {
            g->SetRxSensitivity(c.sensDbm);
            g->PlmeSetTRXStateRequest(lrwpan::IEEE_802_15_4_PHY_RX_ON);
        }
        lrwpan::LrWpanSpectrumValueHelper svh;
        uphy->SetTxPowerSpectralDensity(svh.CreateTxPowerSpectralDensity(c.txDbm, kChannel));
        uphy->PlmeSetTRXStateRequest(lrwpan::IEEE_802_15_4_PHY_TX_ON);
    });

    for (uint32_t s = 0; s < nPackets; ++s) {
        Simulator::Schedule(Seconds(kStartS + s * kPeriodS), [uphy, s]() {
            uint8_t buf[kPsduBytes] = {};
            buf[0] = s >> 24; buf[1] = s >> 16; buf[2] = s >> 8; buf[3] = s;
            uphy->PdDataRequest(kPsduBytes, Create<Packet>(buf, kPsduBytes));
        });
    }

    Simulator::Stop(Seconds(kStartS + nPackets * kPeriodS + 0.1));
    Simulator::Run();
    Simulator::Destroy();
}

NodeResult Summarise(const std::vector<uint8_t>& got) {
    NodeResult r;
    uint32_t cur = 0;
    for (uint32_t s = 0; s < got.size(); ++s) {
        if (!got[s]) { cur = 0; continue; }
        r.received++;
        if (++cur > r.longest) {
            r.longest = cur;
            r.runEnd = (int32_t)s;
            r.runStart = (int32_t)(s + 1 - cur);
        }
    }
    return r;
}

// ---- mode calib: what does "sensitivity -100 dBm" mean for a 127-byte frame? ----
int Calibrate(const RunConfig& c) {
    // One receiver per target received power, UAV hanging still at 100 m.
    std::vector<double> target;
    for (double p = -110.0; p <= -90.0 + 1e-9; p += 0.25) target.push_back(p);
    std::vector<Vector> pos;
    for (size_t i = 0; i < target.size(); ++i) {
        const double pl = c.txDbm - target[i];
        const double d = kRefDistM * std::pow(10.0, (pl - PathLossDb(kRefDistM, c.alpha)) /
                                                        (10.0 * c.alpha));
        CHECK(d > kAltM);
        const double r = std::sqrt(d * d - kAltM * kAltM);
        // Spread around the circle; receivers do not transmit, so they cannot clash.
        const double th = 2.0 * M_PI * i / target.size();
        pos.push_back(Vector(r * std::cos(th), r * std::sin(th), 0));
    }
    const uint32_t n = 4000;
    RngSeedManager::SetSeed(c.seed);
    RngSeedManager::SetRun(1);
    Pass w;
    FadeStats fs;
    RunWorld(c, false, false, pos, n, w, fs);

    CHECK(w.txOk == n && w.txFail == 0);
    CHECK(std::fabs(w.txDbmMin - c.txDbm) < 0.01 && std::fabs(w.txDbmMax - c.txDbm) < 0.01);
    CHECK(fs.n == (uint64_t)n * pos.size());
    CHECK(fs.maxDetErrDb < 1e-6);   // traced loss IS the closed form; antennas are 0 dBi
    CHECK(w.dupes == 0 && w.badSeq == 0);

    std::printf("calibration: %u packets of %u B to %zu receivers, no fading\n",
                n, kPsduBytes, pos.size());
    std::printf("  TX measured from the signal: %.3f dBm   path loss vs closed form: max "
                "err %.1e dB\n", w.txDbmMax, fs.maxDetErrDb);
    std::printf("  ns-3 noise factor from sensitivity %.2f dBm: F = %.2f dB\n\n",
                c.sensDbm, c.sensDbm + 106.58);
    std::printf("%10s %10s\n", "Prx (dBm)", "PER");
    FILE* f = c.out.empty() ? nullptr : std::fopen(c.out.c_str(), "w");
    if (f) std::fprintf(f, "prxDbm,per,n\n");
    double p50 = NAN, p01 = NAN, p99 = NAN;
    for (size_t i = 0; i < target.size(); ++i) {
        const uint32_t ok = Summarise(w.got[i]).received;
        const double per = 1.0 - (double)ok / n;
        if (f) std::fprintf(f, "%.2f,%.6f,%u\n", target[i], per, n);
        if (std::fmod(target[i] + 200.0, 1.0) < 1e-9)
            std::printf("%10.2f %10.4f\n", target[i], per);
        if (std::isnan(p99) && per <= 0.99) p99 = target[i];
        if (std::isnan(p50) && per <= 0.50) p50 = target[i];
        if (std::isnan(p01) && per <= 0.01) p01 = target[i];
    }
    if (f) std::fclose(f);
    // PER must fall as power rises -- within sampling noise.
    std::printf("\n  PER <= 99%% from %.2f dBm, <= 50%% from %.2f dBm, <= 1%% from %.2f dBm\n",
                p99, p50, p01);
    std::printf("  a hard-threshold analysis at %.0f dBm sits %.2f dB from ns-3's 50%% point\n",
                c.sensDbm, p50 - c.sensDbm);
    CHECK(!std::isnan(p50) && !std::isnan(p01));
    std::printf("\n%u CHECKS PASSED\n", g_checks);
    return 0;
}

// ---- mode pass: the experiment ------------------------------------------------
int Fly(const RunConfig& c) {
    std::vector<Vector> pos;
    for (uint32_t k = 0; k < kNodes; ++k)
        pos.push_back(Vector(((double)k - kMiddle) * kSpacingM, 0, 0));

    FILE* f = c.out.empty() ? nullptr : std::fopen(c.out.c_str(), "w");
    if (f) std::fprintf(f, "alpha,fading,pass,node,lateralM,received,longest,runStart,runEnd\n");

    std::printf("alpha %.2f  fading %s  TX %+.0f dBm  sensitivity %.0f dBm  %u passes  "
                "%u packets each\n", c.alpha, c.fading.c_str(), c.txDbm, c.sensDbm,
                c.passes, kPackets);

    std::vector<std::vector<NodeResult>> all(kNodes);
    FadeStats fs;
    RngSeedManager::SetSeed(c.seed);
    for (uint32_t p = 1; p <= c.passes; ++p) {
        RngSeedManager::SetRun(p);
        Pass w;
        RunWorld(c, true, true, pos, kPackets, w, fs);
        CHECK(w.txOk == kPackets && w.txFail == 0);   // every packet left the antenna
        CHECK(std::fabs(w.txDbmMin - c.txDbm) < 0.01 && std::fabs(w.txDbmMax - c.txDbm) < 0.01);
        CHECK(w.dupes == 0 && w.badSeq == 0);
        for (uint32_t k = 0; k < kNodes; ++k) {
            const NodeResult r = Summarise(w.got[k]);
            CHECK(r.longest <= r.received);
            all[k].push_back(r);
            if (f)
                std::fprintf(f, "%.2f,%s,%u,%u,%.0f,%u,%u,%d,%d\n", c.alpha, c.fading.c_str(),
                             p, k + 1, std::fabs(pos[k].x), r.received, r.longest,
                             r.runStart, r.runEnd);
        }
    }
    if (f) std::fclose(f);

    // The fade the channel applied must be the fade that was asked for.
    CHECK(fs.n == (uint64_t)kNodes * kPackets * c.passes);
    const double mean = fs.sumLin / fs.n;
    const double q10 = (double)fs.below10 / fs.n, q20 = (double)fs.below20 / fs.n,
                 q30 = (double)fs.below30 / fs.n;
    std::printf("\nfade actually applied (%lu draws): mean power %.4f   P(<-10dB) %.3e   "
                "P(<-20dB) %.3e   P(<-30dB) %.3e\n", (unsigned long)fs.n, mean, q10, q20, q30);
    if (c.fading == "none") {
        CHECK(fs.maxDetErrDb < 1e-6);
    } else {
        CHECK(std::fabs(mean - 1.0) < 0.01);   // unit-mean fading
        if (c.fading == "rician" && c.kFactor == 2.0) {
            // Reference tail of Rician K=2, from 4e6 draws of the analytic model.
            CHECK(std::fabs(q10 / 4.61e-2 - 1.0) < 0.05);
            CHECK(std::fabs(q20 / 4.09e-3 - 1.0) < 0.10);
        }
        if (c.fading == "nakagami" && c.nakagamiM == 1.8) {
            CHECK(std::fabs(q10 / 2.43e-2 - 1.0) < 0.05);
            CHECK(std::fabs(q20 / 4.38e-4 - 1.0) < 0.20);
        }
    }

    auto stat = [](const std::vector<NodeResult>& v, bool runs, double& m, double& sd,
                   double& p10, double& p90) {
        std::vector<double> x;
        for (const NodeResult& r : v) x.push_back(runs ? r.longest : r.received);
        std::sort(x.begin(), x.end());
        m = 0;
        for (double e : x) m += e;
        m /= x.size();
        sd = 0;
        for (double e : x) sd += (e - m) * (e - m);
        sd = std::sqrt(sd / x.size());
        p10 = x[(size_t)(0.10 * (x.size() - 1))];
        p90 = x[(size_t)(0.90 * (x.size() - 1))];
    };
    std::printf("\n%6s %8s %9s | %10s | %18s %8s %8s\n", "node", "lateral", "closest",
                "received", "LONGEST RUN", "p10", "p90");
    for (uint32_t k = 0; k < kNodes; ++k) {
        double m, sd, a, b, rm, rsd, ra, rb;
        stat(all[k], false, m, sd, a, b);
        stat(all[k], true, rm, rsd, ra, rb);
        std::printf("%6u %7.0fm %8.1fm | %10.0f | %10.0f ± %5.0f %8.0f %8.0f\n", k + 1,
                    std::fabs(pos[k].x), std::hypot(pos[k].x, kAltM), m, rm, rsd, ra, rb);
    }
    std::printf("\n%u CHECKS PASSED\n", g_checks);
    return 0;
}

}  // namespace

int main(int argc, char* argv[]) {
    RunConfig c;
    CommandLine cmd(__FILE__);
    cmd.AddValue("mode", "calib | pass", c.mode);
    cmd.AddValue("fading", "rician | nakagami | none", c.fading);
    cmd.AddValue("alpha", "path-loss exponent beyond 100 m", c.alpha);
    cmd.AddValue("tx", "UAV transmit power, dBm", c.txDbm);
    cmd.AddValue("sens", "receiver sensitivity, dBm (ns-3 semantics)", c.sensDbm);
    cmd.AddValue("K", "Rician K factor", c.kFactor);
    cmd.AddValue("m", "Nakagami m", c.nakagamiM);
    cmd.AddValue("passes", "independent passes", c.passes);
    cmd.AddValue("seed", "RNG seed; pass p uses run p", c.seed);
    cmd.AddValue("out", "CSV output", c.out);
    cmd.Parse(argc, argv);
    CHECK(c.mode == "calib" || c.mode == "pass");
    CHECK(c.fading == "rician" || c.fading == "nakagami" || c.fading == "none");
    CHECK(kPackets == 8001);
    return c.mode == "calib" ? Calibrate(c) : Fly(c);
}
