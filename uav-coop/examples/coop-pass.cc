// Step 3: the UAV flies the step-2 path and broadcasts; how many packets does each
// node get?
//
// Reads what uav-coop-deploy wrote -- PREFIX-nodes-sS.csv (positions, roles) and
// PREFIX-path-sS.csv (the path, every 2 m, lead-in and lead-out included) -- and
// flies it at the A2G-RUN settings: altitude 100 m, 50 m/s, a numbered 127-byte PSDU
// every 10 ms from the start of the lead-in to the end of the lead-out, +10 dBm,
// urban channel (free space to 100 m, then alpha 3.0, Rician K = 2 per packet), PHY
// direct (no MAC), every node listening.
//
// As in A2G-SWEEP the UAV sends ONE FILE of K packets cyclically: packet s carries
// chunk s mod K, so one pass evaluates every K at once. Per node and mission:
//   rx      packets received
//   run     longest run of consecutive packets received
//   cov K   distinct chunks of a K-packet file collected; done K: all K
//
// Mission r depends on (seed, r) alone, so missions can be split over processes
// with --firstRun and merged afterwards (tools/pass_report.py).
//
//   uav-coop-pass --nodes=deploy-nodes-s35.csv --path=deploy-path-s35.csv --runs=120 --out=pass

#include "coop-a2g.h"

#include "../models/common/coop-params.h"

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
#include <fstream>
#include <map>
#include <sstream>
#include <string>
#include <vector>

using namespace ns3;
using namespace ns3::uavcoop;

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

constexpr uint32_t kChannel = 11;    // 2405 MHz
constexpr double kStartS = 1.0;      // after the PHYs are set up
// Faded loss beyond this is never handed to a receiver. Exact: at +10 dBm it means
// Prx < -110 dBm, below what ns-3 tries to decode (SINR -5 dB over -104.4 dBm noise).
// Fading is drawn before the cut, so the random streams are untouched.
constexpr double kMaxLossDb = 120.0;
const std::vector<uint32_t> kFileSizes = {50, 100, 200, 500, 1000, 2000};

// One CSV with a header, read into maps of column -> text.
std::vector<std::map<std::string, std::string>> ReadCsv(const std::string& file) {
    std::ifstream in(file);
    if (!in) {
        std::fprintf(stderr, "cannot read %s\n", file.c_str());
        std::exit(1);
    }
    std::string line, cell;
    std::getline(in, line);
    std::vector<std::string> head;
    std::stringstream hs(line);
    while (std::getline(hs, cell, ',')) head.push_back(cell);
    std::vector<std::map<std::string, std::string>> rows;
    while (std::getline(in, line)) {
        if (line.empty()) continue;
        std::stringstream ls(line);
        std::map<std::string, std::string> r;
        for (size_t i = 0; std::getline(ls, cell, ','); ++i) {
            CHECK(i < head.size());
            r[head[i]] = cell;
        }
        CHECK(r.size() == head.size());
        rows.push_back(r);
    }
    return rows;
}

struct GroundNode {
    uint32_t id = 0;
    double x = 0, y = 0, dPath = 0;
    bool isCH = false;
};

// The flight path as a polyline with cumulative length; part per vertex.
struct Track {
    std::vector<double> x, y, s;
    std::vector<int> part;
    Vector At(double d, int* prt = nullptr) const {
        const size_t i = std::min<size_t>(
            std::upper_bound(s.begin(), s.end(), d) - s.begin(), s.size() - 1);
        const size_t j = i == 0 ? 0 : i - 1;
        const double L = s[i] - s[j];
        const double f = L > 0 ? std::clamp((d - s[j]) / L, 0.0, 1.0) : 0.0;
        if (prt) *prt = part[i];
        return Vector(x[j] + f * (x[i] - x[j]), y[j] + f * (y[i] - y[j]), 0);
    }
};

double Quantile(std::vector<double> v, double q) {
    std::sort(v.begin(), v.end());
    const double k = q * (v.size() - 1);
    const size_t a = (size_t)std::floor(k), b = std::min(a + 1, v.size() - 1);
    return v[a] + (k - a) * (v[b] - v[a]);
}

}  // namespace

int main(int argc, char* argv[]) {
    std::string nodesFile = "deploy-nodes-s35.csv", pathFile = "deploy-path-s35.csv";
    double alt = params::kUavAltM, speed = params::kUavSpeedMps, alpha = params::kA2gAlpha;
    double kFactor = params::kA2gRicianK, txDbm = params::kTxPowerDbm, sens = params::kRxSensDbm;
    uint32_t runs = 120, firstRun = 1, seed = 1;
    std::string out = "pass";
    CommandLine cmd(__FILE__);
    cmd.AddValue("nodes", "nodes CSV from uav-coop-deploy", nodesFile);
    cmd.AddValue("path", "path CSV from uav-coop-deploy (same spacing)", pathFile);
    cmd.AddValue("alt", "flight altitude, m (also the end of the free-space segment)", alt);
    cmd.AddValue("speed", "ground speed, m/s", speed);
    cmd.AddValue("alpha", "path-loss exponent beyond the free-space segment", alpha);
    cmd.AddValue("K", "Rician K factor", kFactor);
    cmd.AddValue("runs", "independent missions (method rule: >= 120)", runs);
    cmd.AddValue("firstRun", "index of the first mission", firstRun);
    cmd.AddValue("seed", "RNG seed", seed);
    cmd.AddValue("out", "output prefix", out);
    cmd.Parse(argc, argv);
    const double dref = alt;
    const double dt = params::kSlotS;
    const uint32_t psdu = params::kPsduBytes;

    // ---- the path ----------------------------------------------------------
    Track T;
    for (const auto& r : ReadCsv(pathFile)) {
        const double x = std::stod(r.at("x")), y = std::stod(r.at("y"));
        if (!T.x.empty() && std::hypot(x - T.x.back(), y - T.y.back()) < 1e-6) continue;   // shared joint
        T.s.push_back(T.x.empty() ? 0.0 : T.s.back() + std::hypot(x - T.x.back(), y - T.y.back()));
        T.x.push_back(x);
        T.y.push_back(y);
        T.part.push_back(std::stoi(r.at("part")));
    }
    CHECK(T.x.size() > 2);
    for (size_t i = 1; i < T.x.size(); ++i) {
        const double d = T.s[i] - T.s[i - 1];
        CHECK(d > 0 && d <= 2.0 + 1e-2);   // every <= 2 m (CSV rounds to 1 mm): continuous
        CHECK(T.part[i] >= T.part[i - 1]);
    }
    const double length = T.s.back();
    const uint32_t nPk = (uint32_t)std::floor(length / (speed * dt)) + 1;
    std::vector<Vector> pkPos(nPk);
    std::vector<int> pkPart(nPk);
    for (uint32_t s = 0; s < nPk; ++s) pkPos[s] = T.At(s * speed * dt, &pkPart[s]);

    // ---- the nodes ---------------------------------------------------------
    std::vector<GroundNode> nodes;
    for (const auto& r : ReadCsv(nodesFile)) {
        GroundNode n;
        n.id = (uint32_t)std::stoul(r.at("id"));
        n.x = std::stod(r.at("x"));
        n.y = std::stod(r.at("y"));
        n.isCH = r.at("isCH") == "1";
        n.dPath = 1e18;
        for (size_t i = 0; i < T.x.size(); ++i)    // vertices 2 m apart: within 1 m
            n.dPath = std::min(n.dPath, std::hypot(n.x - T.x[i], n.y - T.y[i]));
        nodes.push_back(n);
    }
    const uint32_t nNodes = (uint32_t)nodes.size();
    size_t chIdx = nNodes;
    for (size_t k = 0; k < nNodes; ++k)
        if (nodes[k].isCH) { CHECK(chIdx == nNodes); chIdx = k; }
    CHECK(chIdx < nNodes);
    CHECK(nodes[chIdx].dPath < 1.0);                 // the path flies over the CH

    std::printf("path %s: %.0f m = %.1f s at %.0f m/s, %u packets (one every %.0f ms); altitude "
                "%.0f m\nnodes %s: %u, CH #%u\nchannel: free space to %.0f m, then alpha %.2f, "
                "Rician K %.1f; +%.0f dBm, sensitivity %.0f dBm, %u B PSDU\n", pathFile.c_str(),
                length, length / speed, speed, nPk, dt * 1e3, alt, nodesFile.c_str(), nNodes,
                nodes[chIdx].id, dref, alpha, kFactor, txDbm, sens, psdu);

    // Per node over missions.
    const size_t nK = kFileSizes.size();
    std::vector<std::vector<double>> rxAll(nNodes), runAll(nNodes);
    std::vector<std::vector<uint32_t>> doneN(nNodes, std::vector<uint32_t>(nK, 0));
    std::vector<std::vector<double>> covSum(nNodes, std::vector<double>(nK, 0));
    std::vector<std::vector<uint8_t>> strip;      // mission 1, every node, for the figures
    FILE* fr = std::fopen((out + "-runs.csv").c_str(), "w");
    std::fprintf(fr, "run,heard,rxMean,chRx,chRun");
    for (uint32_t K : kFileSizes) std::fprintf(fr, ",done%u", K);
    std::fprintf(fr, "\n");

    FILE* fw = std::fopen((out + "-raw.csv").c_str(), "w");
    std::fprintf(fw, "run,id,rx,maxRun");
    for (uint32_t K : kFileSizes) std::fprintf(fw, ",cov%u", K);
    std::fprintf(fw, "\n");

    for (uint32_t run = firstRun; run < firstRun + runs; ++run) {
        RngSeedManager::SetSeed(seed);
        RngSeedManager::SetRun(run);

        NodeContainer uav, ground;
        uav.Create(1);
        ground.Create(nNodes);
        MobilityHelper st;
        st.SetMobilityModel("ns3::ConstantPositionMobilityModel");
        st.Install(ground);
        std::vector<Ptr<MobilityModel>> gm(nNodes);
        for (uint32_t k = 0; k < nNodes; ++k) {
            gm[k] = ground.Get(k)->GetObject<MobilityModel>();
            gm[k]->SetPosition(Vector(nodes[k].x, nodes[k].y, 0));
        }
        MobilityHelper wp;
        wp.SetMobilityModel("ns3::WaypointMobilityModel");
        wp.Install(uav);
        Ptr<WaypointMobilityModel> um = uav.Get(0)->GetObject<WaypointMobilityModel>();
        um->AddWaypoint(Waypoint(Seconds(0), Vector(T.x[0], T.y[0], alt)));
        for (size_t i = 0; i < T.x.size(); ++i)
            um->AddWaypoint(Waypoint(Seconds(kStartS + T.s[i] / speed), Vector(T.x[i], T.y[i], alt)));

        // ONE helper for every node, alive until Destroy: its destructor disposes the
        // channel and would silently stop all reception.
        LrWpanHelper lr;
        Ptr<PropagationLossModel> loss;
        Ptr<SpectrumChannel> ch = BuildA2gChannel(alpha, dref, kFactor, params::kFspl1mDb, loss);
        ch->SetAttribute("MaxLossDb", DoubleValue(kMaxLossDb));
        lr.SetChannel(ch);
        NetDeviceContainer uavDev = lr.Install(uav);
        NetDeviceContainer gndDev = lr.Install(ground);
        CHECK(ch->GetNDevices() == 1 + nNodes);
        // Fixed streams: mission r depends on (seed, r) alone, not on the missions before.
        loss->AssignStreams(0);
        lr.AssignStreams(uavDev, 10);
        lr.AssignStreams(gndDev, 20);

        Ptr<lrwpan::LrWpanPhy> uphy = DynamicCast<lrwpan::LrWpanNetDevice>(uavDev.Get(0))->GetPhy();
        std::vector<Ptr<lrwpan::LrWpanPhy>> gphy(nNodes);
        std::map<const SpectrumPhy*, uint32_t> idx;
        for (uint32_t k = 0; k < nNodes; ++k) {
            gphy[k] = DynamicCast<lrwpan::LrWpanNetDevice>(gndDev.Get(k))->GetPhy();
            idx[PeekPointer(gphy[k])] = k;
        }

        std::vector<std::vector<uint8_t>> got(nNodes, std::vector<uint8_t>(nPk, 0));
        uint32_t txOk = 0, txFail = 0, dupes = 0, bad = 0, posErr = 0;
        double txMin = 1e9, txMax = -1e9;
        uint64_t fadeN = 0, fade10 = 0, fade20 = 0;
        double fadeSum = 0;

        auto noState = lrwpan::PlmeSetTRXStateConfirmCallback([](lrwpan::PhyEnumeration) {});
        uphy->SetPlmeSetTRXStateConfirmCallback(noState);
        uphy->SetPdDataConfirmCallback(lrwpan::PdDataConfirmCallback(
            [&](lrwpan::PhyEnumeration s) { (s == lrwpan::IEEE_802_15_4_PHY_SUCCESS ? txOk : txFail)++; }));
        for (uint32_t k = 0; k < nNodes; ++k) {
            gphy[k]->SetPlmeSetTRXStateConfirmCallback(noState);
            gphy[k]->SetPdDataIndicationCallback(lrwpan::PdDataIndicationCallback(
                [&got, &dupes, &bad, k, nPk, psdu](uint32_t len, Ptr<Packet> p, uint8_t) {
                    uint8_t b[4];
                    if (len != psdu || p->CopyData(b, 4) != 4) { bad++; return; }
                    const uint32_t s = (uint32_t)b[0] << 24 | (uint32_t)b[1] << 16 |
                                       (uint32_t)b[2] << 8 | b[3];
                    if (s >= nPk) { bad++; return; }
                    if (got[k][s]) dupes++;
                    got[k][s] = 1;
                }));
        }
        ch->TraceConnectWithoutContext("TxSigParams",
            Callback<void, Ptr<SpectrumSignalParameters>>([&](Ptr<SpectrumSignalParameters> sp) {
                const double dbm = 10.0 * std::log10(
                    lrwpan::LrWpanSpectrumValueHelper::TotalAvgPower(sp->psd, kChannel)) + 30.0;
                txMin = std::min(txMin, dbm);
                txMax = std::max(txMax, dbm);
            }));
        // The fade the channel applied = closed-form path loss - traced loss.
        ch->TraceConnectWithoutContext("PathLoss",
            Callback<void, Ptr<const SpectrumPhy>, Ptr<const SpectrumPhy>, double>(
                [&](Ptr<const SpectrumPhy>, Ptr<const SpectrumPhy> rx, double lossDb) {
                    auto it = idx.find(PeekPointer(rx));
                    if (it == idx.end()) return;
                    const double d = um->GetDistanceFrom(gm[it->second]);
                    const double f = A2gPathLossDb(d, alpha, dref, params::kFspl1mDb) - lossDb;
                    fadeN++;
                    fadeSum += std::pow(10.0, f / 10.0);
                    if (f < -10) fade10++;
                    if (f < -20) fade20++;
                }));

        Simulator::Schedule(Seconds(kStartS / 2), [&]() {
            for (auto& g : gphy) {
                g->SetRxSensitivity(sens);
                g->PlmeSetTRXStateRequest(lrwpan::IEEE_802_15_4_PHY_RX_ON);
            }
            // After SetRxSensitivity, which rebuilds the TX PSD.
            lrwpan::LrWpanSpectrumValueHelper svh;
            uphy->SetTxPowerSpectralDensity(svh.CreateTxPowerSpectralDensity(txDbm, kChannel));
            uphy->PlmeSetTRXStateRequest(lrwpan::IEEE_802_15_4_PHY_TX_ON);
        });
        for (uint32_t s = 0; s < nPk; ++s) {
            Simulator::Schedule(Seconds(kStartS + s * dt), [&, s]() {
                // The aircraft must be where the plan says (2 m chords: sag < 0.01 m).
                const Vector p = um->GetPosition();
                if (std::hypot(p.x - pkPos[s].x, p.y - pkPos[s].y) > 0.05 || std::fabs(p.z - alt) > 1e-6)
                    posErr++;
                uint8_t buf[256] = {};
                buf[0] = s >> 24; buf[1] = s >> 16; buf[2] = s >> 8; buf[3] = s;
                uphy->PdDataRequest(psdu, Create<Packet>(buf, psdu));
            });
        }
        Simulator::Stop(Seconds(kStartS + nPk * dt + 0.1));
        Simulator::Run();
        Simulator::Destroy();

        CHECK(txOk == nPk && txFail == 0);
        CHECK(std::fabs(txMin - txDbm) < 0.01 && std::fabs(txMax - txDbm) < 0.01);
        CHECK(dupes == 0 && bad == 0);
        CHECK(posErr == 0);
        CHECK(fadeN == (uint64_t)nPk * nNodes);
        const double fMean = fadeSum / fadeN;
        CHECK(std::fabs(fMean - 1.0) < 0.01);
        if (kFactor == 2.0) {      // Rician K = 2 tail, closed form
            CHECK(std::fabs((double)fade10 / fadeN / 4.61e-2 - 1.0) < 0.05);
            CHECK(std::fabs((double)fade20 / fadeN / 4.09e-3 - 1.0) < 0.10);
        }

        // ---- per node ----------------------------------------------------------
        uint32_t heard = 0;
        double rxTot = 0;
        std::vector<uint32_t> doneRun(nK, 0);
        std::vector<uint8_t> have;
        for (uint32_t k = 0; k < nNodes; ++k) {
            uint32_t rx = 0, best = 0, cur = 0;
            for (uint32_t s = 0; s < nPk; ++s) {
                if (got[k][s]) { rx++; best = std::max(best, ++cur); }
                else cur = 0;
            }
            CHECK(best <= rx && rx <= nPk);
            heard += rx > 0;
            rxTot += rx;
            rxAll[k].push_back(rx);
            runAll[k].push_back(best);
            std::fprintf(fw, "%u,%u,%u,%u", run, nodes[k].id, rx, best);
            for (size_t i = 0; i < nK; ++i) {
                const uint32_t K = kFileSizes[i];
                have.assign(K, 0);
                uint32_t cov = 0;
                for (uint32_t s = 0; s < nPk; ++s)
                    if (got[k][s] && !have[s % K]) { have[s % K] = 1; cov++; }
                CHECK(cov <= std::min(K, rx));
                if (best >= K) CHECK(cov == K);          // a run of K holds every chunk
                covSum[k][i] += cov;
                std::fprintf(fw, ",%u", cov);
                if (cov == K) { doneN[k][i]++; doneRun[i]++; }
            }
            std::fprintf(fw, "\n");
        }
        std::fflush(fw);
        if (run == firstRun) strip = got;
        std::fprintf(fr, "%u,%u,%.3f,%u,%u", run, heard, rxTot / nNodes,
                     (uint32_t)rxAll[chIdx].back(), (uint32_t)runAll[chIdx].back());
        for (uint32_t d : doneRun) std::fprintf(fr, ",%u", d);
        std::fprintf(fr, "\n");
        std::fflush(fr);
        if (run == firstRun || run % 10 == 0) {
            std::printf("  mission %u: %u/%u nodes heard something, mean %.0f packets; CH %u "
                        "(run %u); mean fade power %.4f\n", run, heard, nNodes, rxTot / nNodes,
                        (uint32_t)rxAll[chIdx].back(), (uint32_t)runAll[chIdx].back(), fMean);
            std::fflush(stdout);
        }
    }
    std::fclose(fr);
    std::fclose(fw);

    // ---- per node over this process's missions ------------------------------------
    FILE* fn = std::fopen((out + "-nodes.csv").c_str(), "w");
    std::fprintf(fn, "id,x,y,isCH,dPathM,rxMean,rxP10,rxP50,rxP90,runMean,runP10,runP50");
    for (uint32_t K : kFileSizes) std::fprintf(fn, ",pDone%u,covMean%u", K, K);
    std::fprintf(fn, "\n");
    for (uint32_t k = 0; k < nNodes; ++k) {
        double m = 0, rm = 0;
        for (double v : rxAll[k]) m += v;
        for (double v : runAll[k]) rm += v;
        std::fprintf(fn, "%u,%.3f,%.3f,%d,%.1f,%.2f,%.1f,%.1f,%.1f,%.2f,%.1f,%.1f", nodes[k].id,
                     nodes[k].x, nodes[k].y, nodes[k].isCH ? 1 : 0, nodes[k].dPath, m / runs,
                     Quantile(rxAll[k], .1), Quantile(rxAll[k], .5), Quantile(rxAll[k], .9),
                     rm / runs, Quantile(runAll[k], .1), Quantile(runAll[k], .5));
        for (size_t i = 0; i < nK; ++i)
            std::fprintf(fn, ",%.4f,%.2f", (double)doneN[k][i] / runs, covSum[k][i] / runs);
        std::fprintf(fn, "\n");
    }
    std::fclose(fn);

    // ---- first mission's bitmaps (hex nibbles, 4 packets each) and the packet track --
    FILE* fs = std::fopen((out + "-strip.csv").c_str(), "w");
    std::fprintf(fs, "run,id,dPathM,packets,bitsHex\n");
    for (uint32_t k = 0; k < nNodes; ++k) {
        std::fprintf(fs, "%u,%u,%.1f,%u,", firstRun, nodes[k].id, nodes[k].dPath, nPk);
        for (uint32_t s = 0; s < nPk; s += 4) {
            uint32_t nib = 0;
            for (uint32_t b = 0; b < 4; ++b) nib = nib << 1 | (s + b < nPk ? strip[k][s + b] : 0);
            std::fputc("0123456789abcdef"[nib], fs);
        }
        std::fputc('\n', fs);
    }
    std::fclose(fs);
    FILE* ft = std::fopen((out + "-track.csv").c_str(), "w");
    std::fprintf(ft, "seq,t,x,y,part\n");
    for (uint32_t s = 0; s < nPk; ++s)
        std::fprintf(ft, "%u,%.2f,%.2f,%.2f,%d\n", s, s * dt, pkPos[s].x, pkPos[s].y, pkPart[s]);
    std::fclose(ft);

    // ---- summary by distance from the path ----------------------------------------
    std::printf("\nby horizontal distance from the path (%u missions):\n", runs);
    std::printf("%10s %6s %9s %9s", "dist", "nodes", "rx mean", "run mean");
    for (uint32_t K : kFileSizes) std::printf(" %8s", ("done" + std::to_string(K)).c_str());
    std::printf("\n");
    for (double lo = 0; lo < 2500; lo += 100) {
        uint32_t n = 0;
        double rx = 0, rn = 0;
        std::vector<double> pd(nK, 0);
        for (uint32_t k = 0; k < nNodes; ++k) {
            if (nodes[k].dPath < lo || nodes[k].dPath >= lo + 100) continue;
            n++;
            for (double v : rxAll[k]) rx += v;
            for (double v : runAll[k]) rn += v;
            for (size_t i = 0; i < nK; ++i) pd[i] += (double)doneN[k][i] / runs;
        }
        if (!n) continue;
        std::printf("%4.0f-%4.0f m %6u %9.0f %9.0f", lo, lo + 100, n, rx / n / runs, rn / n / runs);
        for (double p : pd) std::printf(" %7.1f%%", 100 * p / n);
        std::printf("\n");
    }
    std::printf("CH #%u: rx mean %.0f of %u, longest run mean %.0f\n", nodes[chIdx].id,
                [&] { double m = 0; for (double v : rxAll[chIdx]) m += v; return m / runs; }(), nPk,
                [&] { double m = 0; for (double v : runAll[chIdx]) m += v; return m / runs; }());
    std::printf("%u CHECKS PASSED\n", g_checks);
    return 0;
}
