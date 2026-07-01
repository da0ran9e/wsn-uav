// Phase 2 smoke test: verify the realistic channel behaves sensibly.
// A UAV transmitter broadcasts K packets; a line of ground receivers at growing
// distances count receptions. Prints PDR vs distance for two UAV altitudes.
// Expectation: PDR decreases with distance; a higher UAV (more A2G/LoS) holds
// up better at range than a low UAV (G2G-dominated).

#include "../models/network/sar-network.h"
#include "../models/common/sar-params.h"

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"
#include "ns3/lr-wpan-module.h"

#include <cstdint>
#include <iomanip>
#include <iostream>
#include <map>
#include <vector>

using namespace ns3;
using namespace ns3::uavsar;

static void RunPass(double altitude, const std::vector<double>& dists,
                    uint32_t numPkts, std::map<double, uint32_t>& rxByDist) {
    NodeContainer uav;
    uav.Create(1);
    NodeContainer ground;
    ground.Create(dists.size());

    MobilityHelper mob;
    mob.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    mob.Install(uav);
    mob.Install(ground);
    uav.Get(0)->GetObject<MobilityModel>()->SetPosition(Vector(0, 0, altitude));
    for (size_t i = 0; i < dists.size(); i++)
        ground.Get(i)->GetObject<MobilityModel>()->SetPosition(Vector(dists[i], 0, 0));

    LrWpanHelper lr;
    lr.SetChannel(BuildSarChannel());
    NetDeviceContainer uavDev = lr.Install(uav);
    NetDeviceContainer gndDev = lr.Install(ground);

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
    applyPhy(uavDev.Get(0));
    for (uint32_t i = 0; i < gndDev.GetN(); i++) applyPhy(gndDev.Get(i));

    std::vector<uint32_t> rx(dists.size(), 0);
    for (uint32_t i = 0; i < gndDev.GetN(); i++) {
        uint32_t idx = i;
        gndDev.Get(i)->SetReceiveCallback(
            [&rx, idx](Ptr<NetDevice>, Ptr<const Packet>, uint16_t, const Address&) {
                rx[idx]++;
                return true;
            });
    }

    Ptr<NetDevice> tx = uavDev.Get(0);
    for (uint32_t k = 0; k < numPkts; k++) {
        Simulator::Schedule(Seconds(0.05 * k + 0.1), [tx]() {
            Ptr<Packet> p = Create<Packet>(40);
            tx->Send(p, Mac16Address("ff:ff"), 0);
        });
    }

    Simulator::Stop(Seconds(0.05 * numPkts + 1.0));
    Simulator::Run();
    Simulator::Destroy();

    for (size_t i = 0; i < dists.size(); i++) rxByDist[dists[i]] = rx[i];
}

int main(int argc, char* argv[]) {
    uint32_t numPkts = 200;
    CommandLine cmd;
    cmd.AddValue("numPkts", "packets per pass", numPkts);
    cmd.Parse(argc, argv);

    RngSeedManager::SetSeed(1);
    RngSeedManager::SetRun(1);

    std::vector<double> dists = {10, 20, 30, 40, 50, 60, 70, 80, 100, 120, 150, 200};

    std::cout << "=== CHANNEL PDR vs distance (K=" << numPkts << " pkts/pass) ===\n";
    std::cout << "A2G exp=" << params::kA2GExponent << " G2G exp=" << params::kG2GExponent
              << " altThresh=" << params::kAltThresholdM << "m sigma=" << params::kShadowingSigmaDb
              << "dB m=" << params::kNakagamiM << " RxSens=" << params::kRxSensitivityDbm << "dBm\n\n";

    std::map<double, uint32_t> low, high;
    RunPass(20.0, dists, numPkts, low);
    RunPass(50.0, dists, numPkts, high);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "dist(m)   PDR@20m   PDR@50m\n";
    for (double d : dists) {
        std::cout << std::setw(6) << d << "    "
                  << std::setw(6) << (100.0 * low[d] / numPkts) << "%   "
                  << std::setw(6) << (100.0 * high[d] / numPkts) << "%\n";
    }
    return 0;
}
