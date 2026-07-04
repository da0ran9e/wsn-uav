// Packet-level PHY error validation (đánh giá lỗi mức gói).
//
// Demonstrates that packet fate in this stack is decided by the SINR error
// model (IEEE 802.15.4 O-QPSK BER curve, noise floor derived from the -95 dBm
// sensitivity, Nakagami fading + per-pair shadowing), NOT by a binary range
// check: PDR degrades through a waterfall region, and PhyStats breaks every
// loss down by cause (perFail / weak / collision / notInRx).
//
// For each (linkType, distance): one TX broadcasts K 100-byte packets to a
// ring of 8 receivers (8 independent shadowing draws); we report app-level
// PDR plus the PHY drop breakdown.

#include "../models/network/sar-network.h"
#include "../models/network/phy-stats.h"
#include "../models/common/sar-params.h"

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"
#include "ns3/lr-wpan-module.h"

#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <map>
#include <vector>

using namespace ns3;
using namespace ns3::uavsar;

struct Row {
    double dist;
    double pdr;
    uint64_t ok, per, weak, col;
};

static Row RunPass(bool a2g, double dist, uint32_t numPkts) {
    const uint32_t R = 8;  // receivers on a ring: 8 shadowing draws
    NodeContainer tx;
    tx.Create(1);
    NodeContainer rx;
    rx.Create(R);

    MobilityHelper mob;
    mob.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    mob.Install(tx);
    mob.Install(rx);
    double txAlt = a2g ? params::kCruiseAltitudeM : 0.0;
    tx.Get(0)->GetObject<MobilityModel>()->SetPosition(Vector(0, 0, txAlt));
    for (uint32_t i = 0; i < R; i++) {
        double ang = 2 * M_PI * i / R;
        // `dist` is the 3D link distance: place receivers on the ground ring
        // whose slant range to the TX equals dist (a2g), or at flat range (g2g).
        double horiz = a2g ? std::sqrt(std::max(1.0, dist * dist - txAlt * txAlt)) : dist;
        rx.Get(i)->GetObject<MobilityModel>()->SetPosition(
            Vector(horiz * std::cos(ang), horiz * std::sin(ang), 0));
    }

    LrWpanHelper lr;
    lr.SetChannel(BuildSarChannel());
    NetDeviceContainer txDev = lr.Install(tx);
    NetDeviceContainer rxDev = lr.Install(rx);

    lrwpan::LrWpanSpectrumValueHelper svh;
    Ptr<SpectrumValue> txPsd =
        svh.CreateTxPowerSpectralDensity(params::kTxPowerDbm, params::kLrwpanChannel);
    auto applyPhy = [&](Ptr<NetDevice> dev) {
        Ptr<lrwpan::LrWpanNetDevice> d = DynamicCast<lrwpan::LrWpanNetDevice>(dev);
        if (d) {
            d->GetPhy()->SetTxPowerSpectralDensity(txPsd);
            d->GetPhy()->SetRxSensitivity(params::kRxSensitivityDbm);
        }
    };
    applyPhy(txDev.Get(0));
    for (uint32_t i = 0; i < R; i++) applyPhy(rxDev.Get(i));

    uint16_t next = AssignShortAddresses(txDev, 1);
    AssignShortAddresses(rxDev, next);

    PhyStats stats;
    stats.Attach(txDev, a2g ? 'u' : 'g');
    stats.Attach(rxDev, 'g');
    stats.BuildAddressMap();

    uint64_t appRx = 0;
    for (uint32_t i = 0; i < R; i++) {
        rxDev.Get(i)->SetReceiveCallback(
            [&appRx](Ptr<NetDevice>, Ptr<const Packet>, uint16_t, const Address&) {
                appRx++;
                return true;
            });
    }

    Ptr<NetDevice> t = txDev.Get(0);
    for (uint32_t k = 0; k < numPkts; k++) {
        Simulator::Schedule(Seconds(0.05 * k + 0.1), [t]() {
            Ptr<Packet> p = Create<Packet>(100);
            t->Send(p, Mac16Address("ff:ff"), 0);
        });
    }
    Simulator::Stop(Seconds(0.05 * numPkts + 1.0));
    Simulator::Run();
    Simulator::Destroy();

    auto& c = const_cast<std::map<std::string, uint64_t>&>(stats.Counters());
    auto get = [&](const std::string& k) -> uint64_t {
        uint64_t s = 0;
        for (auto& [key, v] : c)
            if (key.rfind(k, 0) == 0) s += v;
        return s;
    };
    Row r;
    r.dist = dist;
    r.pdr = 100.0 * appRx / double(numPkts * R);
    r.ok = get("phyOk_");
    r.per = get("phyPer_");
    r.weak = get("phyWeak_");
    r.col = get("phyCol_");
    return r;
}

int main(int argc, char* argv[]) {
    uint32_t numPkts = 200;
    CommandLine cmd;
    cmd.AddValue("numPkts", "packets per pass", numPkts);
    cmd.Parse(argc, argv);
    RngSeedManager::SetSeed(1);
    RngSeedManager::SetRun(1);

    std::cout << "=== PACKET-LEVEL PHY ERROR VALIDATION ===\n"
              << "error model: IEEE 802.15.4 O-QPSK BER over SINR (chunked),\n"
              << "noise floor derived from RxSensitivity " << params::kRxSensitivityDbm
              << " dBm (ns-3.46 SetRxSensitivity -> noise factor, NF~11.6 dB),\n"
              << "Nakagami m=" << params::kNakagamiM << ", pair shadowing sigma g2g/a2g="
              << params::kShadowingSigmaDb << "/" << params::kShadowSigmaA2gDb
              << " dB; A2G = elevation-angle LoS (Al-Hourani) + ITU-R P.833 foliage;"
              << " G2G n=" << params::kG2GExponent << "\n\n";

    auto table = [&](bool a2g, const std::vector<double>& dists) {
        std::cout << (a2g ? "--- A2G (UAV alt 20 m -> ground), 3D dist ---\n"
                          : "--- G2G (ground <-> ground) ---\n");
        std::cout << "dist(m)   PDR%     phyOk  perFail   weak  collision\n";
        std::cout << std::fixed << std::setprecision(1);
        std::vector<Row> rows;
        for (double d : dists) {
            Row r = RunPass(a2g, d, numPkts);
            rows.push_back(r);
            std::cout << std::setw(6) << d << "  " << std::setw(6) << r.pdr << "  "
                      << std::setw(8) << r.ok << " " << std::setw(8) << r.per << " "
                      << std::setw(6) << r.weak << " " << std::setw(9) << r.col << "\n";
        }
        std::cout << "\n";
        return rows;
    };

    std::vector<Row> g2g = table(false, {15, 25, 30, 35, 40, 45, 55, 70});
    std::vector<Row> a2gRows = table(true, {50, 100, 150, 200, 250, 300, 350, 400, 500, 600});

    int checks = 0, fails = 0;
    auto CHECK = [&](bool ok, const std::string& m) {
        checks++;
        if (!ok) { fails++; std::cout << "  FAIL: " << m << "\n"; }
    };
    // per-pair shadowing sigma=8.7dB: ~5%/pair chance of a deep fade even at
    // close range (a receiver behind dense foliage) -> threshold 85%, not 99%.
    CHECK(g2g.front().pdr > 85, "G2G close range should be mostly reliable");
    CHECK(g2g.back().pdr < 10, "G2G far range should mostly fail");
    CHECK(a2gRows.front().pdr > 90, "A2G close range should be reliable");
    // -95 dBm "sensitivity" = the PER<1% point, not a cliff. At the far tail
    // the mean link is ~6 dB under the criterion, but persistent per-pair
    // shadowing (sigma 8.7 dB) leaves ~1-2 of 8 receivers in a "forest
    // clearing" that still decodes — so assert the REGIME SHIFT (sync-fail
    // drops dominate and PDR halves), not an absolute PDR.
    CHECK(a2gRows.back().pdr < a2gRows.front().pdr / 2.0,
          "A2G far tail should lose most packets vs close range");
    CHECK(a2gRows.back().weak > a2gRows.back().per,
          "A2G far tail must be sync/below-noise dominated");
    // the waterfall must be driven by the error model: corrupted-completions
    // (perFail) must appear in the mid-range, not only hard sync drops
    uint64_t perMidG = 0;
    for (auto& r : g2g)
        if (r.dist >= 30 && r.dist <= 45) perMidG += r.per;
    CHECK(perMidG > 0, "G2G mid-range must show SINR-corrupted packets (perFail)");
    uint64_t perMidA = 0;
    for (auto& r : a2gRows)
        if (r.dist >= 250 && r.dist <= 360) perMidA += r.per;
    CHECK(perMidA > 0, "A2G mid-range must show SINR-corrupted packets (perFail)");
    // A2G reaches much farther than G2G at equal PDR (LoS exponent)
    CHECK(a2gRows[3].pdr > g2g.back().pdr, "A2G@200m should beat G2G@70m");

    std::cout << "=== CHECKS: " << (checks - fails) << "/" << checks << " passed ===\n";
    return fails == 0 ? 0 : 1;
}
