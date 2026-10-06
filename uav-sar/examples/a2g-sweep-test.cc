// Do later passes make up the packets a node far from the track missed?
//
// URBAN BRANCH ONLY -- channel and parameters from a2g-common.h.
//
// A large sensor field, nodes every 100 m. One UAV sweeps it in a lawnmower
// pattern -- parallel lanes L apart (700 m to 1 km), fixed-wing U-turns outside
// the field -- broadcasting a numbered 127-byte PSDU every 10 ms the whole way,
// turns included.
//
// Making up for a loss needs the lost packet to come round again, so the UAV
// broadcasts ONE FILE of K packets cyclically: global packet s carries chunk
// s mod K. The sequence number still rises monotonically; the file index is
// derived from it. Since a node's whole reception history is kept, every K can
// be evaluated from the same run without flying again.
//
// For each node and each K this reports:
//   best   chunks collected by the single best segment (one lane or one turn)
//   union  chunks collected over the whole mission
//   done   the global sequence number at which the node first held all K
// union - best is exactly what the other passes made up.
//
//   a2g-sweep-test --spacing=1000 --runs=30 --out=s1000

#include "a2g-common.h"

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

using a2g::kChannel;
using a2g::kPeriodS;
using a2g::kPsduBytes;
using a2g::PathLossDb;

constexpr double kSpeedMps = 50.0;
constexpr double kBankDeg  = 45.0;      // fixed-wing turn
constexpr double kG        = 9.80665;
constexpr double kStartS   = 1.0;       // after the MAC has initialised
// Faded loss beyond this is never handed to a receiver. Exact, not an
// approximation: at +10 dBm it means Prx < -110 dBm, and ns-3 itself drops any
// signal below SINR -5 dB without trying (noise -104.4 dBm with F = 6.58 dB, so
// below -109.4 dBm). Fading is drawn before the cut, so the random streams are
// untouched -- verified: identical output at 125 dB and 120 dB.
constexpr double kMaxLossDb = 120.0;
const std::vector<uint32_t> kFileSizes = {50, 100, 200, 500, 1000, 2000};

struct Cfg {
    double spacingM = 1000.0;
    double fieldX = 4000.0, fieldY = 3000.0, gridM = 100.0;
    double altM = 100.0, drefM = -1.0, alpha = 3.0;
    double txDbm = 10.0, sensDbm = -100.0, kFactor = 2.0, nakagamiM = 1.8;
    std::string fading = "rician";
    uint32_t runs = 30, firstRun = 1, seed = 1;
    int32_t dumpRow = -1;     // grid row whose bitmaps run 1 dumps; -1: middle
    std::string out = "sweep";
};

// ---- the flight path: lanes and U-turns, parameterised by arc length --------
struct Piece {
    bool arc = false;
    double x0 = 0, y0 = 0, x1 = 0, y1 = 0;        // line
    double cx = 0, cy = 0, r = 0, th0 = 0, dth = 0; // arc, dth signed
    int32_t seg = 0;                               // 2i lane i, 2i+1 turn after lane i
    double len = 0;
};

struct Path {
    std::vector<Piece> pieces;
    std::vector<double> laneX;
    double length = 0, rho = 0;

    void Add(Piece p) {
        p.len = p.arc ? p.r * std::fabs(p.dth) : std::hypot(p.x1 - p.x0, p.y1 - p.y0);
        length += p.len;
        pieces.push_back(p);
    }
    // Position and segment at arc length s.
    Vector At(double s, int32_t& seg) const {
        for (const Piece& p : pieces) {
            if (s <= p.len || &p == &pieces.back()) {
                const double f = p.len > 0 ? std::min(1.0, std::max(0.0, s / p.len)) : 0.0;
                seg = p.seg;
                if (!p.arc) return Vector(p.x0 + f * (p.x1 - p.x0), p.y0 + f * (p.y1 - p.y0), 0);
                const double th = p.th0 + f * p.dth;
                return Vector(p.cx + p.r * std::cos(th), p.cy + p.r * std::sin(th), 0);
            }
            s -= p.len;
        }
        seg = -1;
        return Vector();
    }
};

Path BuildPath(const Cfg& c) {
    Path P;
    P.rho = kSpeedMps * kSpeedMps / (kG * std::tan(kBankDeg * M_PI / 180.0));
    CHECK(c.spacingM >= 2.0 * P.rho);       // the U-turn fits between lanes
    const uint32_t n = (uint32_t)std::ceil(c.fieldX / c.spacingM - 1e-9);
    const double x0 = (c.fieldX - (n - 1) * c.spacingM) / 2.0;   // pattern centred
    for (uint32_t i = 0; i < n; ++i) P.laneX.push_back(x0 + i * c.spacingM);
    const double Y = c.fieldY, r = P.rho, L = c.spacingM;
    for (uint32_t i = 0; i < n; ++i) {
        const double x = P.laneX[i];
        const bool up = (i % 2 == 0);
        Piece lane;
        lane.seg = 2 * i;
        lane.x0 = x; lane.x1 = x;
        lane.y0 = up ? 0 : Y; lane.y1 = up ? Y : 0;
        P.Add(lane);
        if (i + 1 == n) break;
        // U-turn towards +x, outside the field: quarter arc, straight, quarter arc.
        Piece a1, st, a2;
        a1.arc = a2.arc = true;
        a1.seg = st.seg = a2.seg = 2 * i + 1;
        a1.r = a2.r = r;
        if (up) {    // heading +y at (x, Y): clockwise
            a1.cx = x + r;     a1.cy = Y; a1.th0 = M_PI;     a1.dth = -M_PI / 2;
            st.x0 = x + r;     st.y0 = Y + r; st.x1 = x + L - r; st.y1 = Y + r;
            a2.cx = x + L - r; a2.cy = Y; a2.th0 = M_PI / 2; a2.dth = -M_PI / 2;
        } else {     // heading -y at (x, 0): counter-clockwise
            a1.cx = x + r;     a1.cy = 0; a1.th0 = M_PI;         a1.dth = M_PI / 2;
            st.x0 = x + r;     st.y0 = -r; st.x1 = x + L - r; st.y1 = -r;
            a2.cx = x + L - r; a2.cy = 0; a2.th0 = 1.5 * M_PI;   a2.dth = M_PI / 2;
        }
        P.Add(a1); P.Add(st); P.Add(a2);
    }
    // The path must be continuous and travelled at constant speed: consecutive
    // 1 m samples must be ~1 m apart everywhere, turns included.
    int32_t sg;
    Vector prev = P.At(0, sg);
    for (double s = 1.0; s <= P.length; s += 1.0) {
        Vector v = P.At(s, sg);
        const double d = std::hypot(v.x - prev.x, v.y - prev.y);
        CHECK(d > 0.999 && d < 1.001);
        prev = v;
    }
    return P;
}

struct NodeOut {
    uint32_t received = 0, segs = 0, lanes = 0;
    std::vector<uint32_t> covUnion, covBest;
    std::vector<int64_t> done;
};

}  // namespace

int main(int argc, char* argv[]) {
    Cfg c;
    CommandLine cmd(__FILE__);
    cmd.AddValue("spacing", "lane spacing, m", c.spacingM);
    cmd.AddValue("fieldX", "field width across lanes, m", c.fieldX);
    cmd.AddValue("fieldY", "field length along lanes, m", c.fieldY);
    cmd.AddValue("grid", "node spacing, m", c.gridM);
    cmd.AddValue("alt", "flight altitude, m", c.altM);
    cmd.AddValue("dref", "free space up to here, m (<= 0: the altitude)", c.drefM);
    cmd.AddValue("alpha", "path-loss exponent beyond dref", c.alpha);
    cmd.AddValue("fading", "rician | nakagami | none", c.fading);
    cmd.AddValue("runs", "independent missions", c.runs);
    cmd.AddValue("firstRun", "RNG run index of the first mission", c.firstRun);
    cmd.AddValue("seed", "RNG seed", c.seed);
    cmd.AddValue("dumpRow", "grid row to dump bitmaps for (mission 1); -1 middle", c.dumpRow);
    cmd.AddValue("out", "output prefix", c.out);
    cmd.Parse(argc, argv);
    if (c.drefM <= 0) c.drefM = c.altM;

    const Path path = BuildPath(c);
    const double dt = kPeriodS;
    const uint32_t nPk = (uint32_t)std::floor(path.length / (kSpeedMps * dt)) + 1;
    const uint32_t nx = (uint32_t)std::lround(c.fieldX / c.gridM) + 1;
    const uint32_t ny = (uint32_t)std::lround(c.fieldY / c.gridM) + 1;
    const uint32_t nNodes = nx * ny;
    if (c.dumpRow < 0) c.dumpRow = (int32_t)(ny / 2);

    // Per packet: where the UAV is and which segment it is on.
    std::vector<Vector> pkPos(nPk);
    std::vector<int32_t> pkSeg(nPk);
    for (uint32_t s = 0; s < nPk; ++s) pkPos[s] = path.At(s * kSpeedMps * dt, pkSeg[s]);
    const int32_t nSeg = 2 * (int32_t)path.laneX.size() - 1;

    std::vector<Vector> nodePos(nNodes);
    std::vector<double> dLane(nNodes);
    for (uint32_t iy = 0; iy < ny; ++iy)
        for (uint32_t ix = 0; ix < nx; ++ix) {
            const uint32_t k = iy * nx + ix;
            nodePos[k] = Vector(ix * c.gridM, iy * c.gridM, 0);
            double d = 1e18;
            for (double lx : path.laneX) d = std::min(d, std::fabs(nodePos[k].x - lx));
            dLane[k] = d;
        }

    std::printf("field %.0f x %.0f m, %u nodes @%.0f m; %zu lanes %.0f m apart at x =",
                c.fieldX, c.fieldY, nNodes, c.gridM, path.laneX.size(), c.spacingM);
    for (double lx : path.laneX) std::printf(" %.0f", lx);
    std::printf("\nflight %.0f m = %.0f s at %.0f m/s, turn radius %.0f m, %u packets; "
                "altitude %.0f m, free space to %.0f m, alpha %.2f, %s\n",
                path.length, path.length / kSpeedMps, kSpeedMps, path.rho, nPk, c.altM,
                c.drefM, c.alpha, c.fading.c_str());

    // ---- the flight path, once -------------------------------------------
    if (c.firstRun == 1) {
        FILE* fp = std::fopen((c.out + "-path.csv").c_str(), "w");
        std::fprintf(fp, "seq,t,x,y,seg\n");
        for (uint32_t s = 0; s < nPk; ++s)
            if (s % 25 == 0 || s + 1 == nPk || (s > 0 && pkSeg[s] != pkSeg[s - 1]))
                std::fprintf(fp, "%u,%.2f,%.2f,%.2f,%d\n", s, s * dt, pkPos[s].x, pkPos[s].y,
                             pkSeg[s]);
        std::fclose(fp);
        FILE* fl = std::fopen((c.out + "-lanes.csv").c_str(), "w");
        std::fprintf(fl, "lane,x\n");
        for (size_t i = 0; i < path.laneX.size(); ++i)
            std::fprintf(fl, "%zu,%.1f\n", i, path.laneX[i]);
        std::fclose(fl);
    }

    FILE* fn = std::fopen((c.out + "-nodes.csv").c_str(), "w");
    std::fprintf(fn, "run,node,x,y,dLane,received,segs,lanes");
    for (uint32_t K : kFileSizes) std::fprintf(fn, ",union%u,best%u,done%u", K, K, K);
    std::fprintf(fn, "\n");

    for (uint32_t run = c.firstRun; run < c.firstRun + c.runs; ++run) {
        RngSeedManager::SetSeed(c.seed);
        RngSeedManager::SetRun(run);

        NodeContainer uav, ground;
        uav.Create(1);
        ground.Create(nNodes);
        MobilityHelper st;
        st.SetMobilityModel("ns3::ConstantPositionMobilityModel");
        st.Install(ground);
        for (uint32_t k = 0; k < nNodes; ++k)
            ground.Get(k)->GetObject<MobilityModel>()->SetPosition(nodePos[k]);
        MobilityHelper wp;
        wp.SetMobilityModel("ns3::WaypointMobilityModel");
        wp.Install(uav);
        Ptr<WaypointMobilityModel> um = uav.Get(0)->GetObject<WaypointMobilityModel>();
        {
            int32_t sg;
            const Vector p0 = path.At(0, sg);
            um->AddWaypoint(Waypoint(Seconds(0), Vector(p0.x, p0.y, c.altM)));
            // Every 0.25 s: on a 255 m arc the chord sags 0.08 m from the circle.
            for (double s = 0; ; s += 0.25 * kSpeedMps) {
                const double ss = std::min(s, path.length);
                const Vector p = path.At(ss, sg);
                um->AddWaypoint(Waypoint(Seconds(kStartS + ss / kSpeedMps),
                                         Vector(p.x, p.y, c.altM)));
                if (ss >= path.length) break;
            }
        }

        // ONE helper for every node, alive until Destroy: its destructor disposes
        // the channel and would silently stop all reception.
        LrWpanHelper lr;
        Ptr<SpectrumChannel> ch =
            a2g::BuildChannel(c.alpha, c.drefM, c.fading, c.kFactor, c.nakagamiM);
        ch->SetAttribute("MaxLossDb", DoubleValue(kMaxLossDb));
        lr.SetChannel(ch);
        NetDeviceContainer uavDev = lr.Install(uav);
        NetDeviceContainer gndDev = lr.Install(ground);
        CHECK(ch->GetNDevices() == 1 + nNodes);

        Ptr<lrwpan::LrWpanPhy> uphy = DynamicCast<lrwpan::LrWpanNetDevice>(uavDev.Get(0))->GetPhy();
        std::vector<Ptr<lrwpan::LrWpanPhy>> gphy(nNodes);
        std::map<const SpectrumPhy*, uint32_t> idx;
        std::vector<Ptr<MobilityModel>> gm(nNodes);
        for (uint32_t k = 0; k < nNodes; ++k) {
            gm[k] = ground.Get(k)->GetObject<MobilityModel>();
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
                [&got, &dupes, &bad, k, nPk](uint32_t len, Ptr<Packet> p, uint8_t) {
                    uint8_t b[4];
                    if (len != kPsduBytes || p->CopyData(b, 4) != 4) { bad++; return; }
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
                    const double f = PathLossDb(d, c.alpha, c.drefM) - lossDb;
                    fadeN++;
                    fadeSum += std::pow(10.0, f / 10.0);
                    if (f < -10) fade10++;
                    if (f < -20) fade20++;
                }));

        Simulator::Schedule(Seconds(kStartS / 2), [&]() {
            for (auto& g : gphy) {
                g->SetRxSensitivity(c.sensDbm);
                g->PlmeSetTRXStateRequest(lrwpan::IEEE_802_15_4_PHY_RX_ON);
            }
            lrwpan::LrWpanSpectrumValueHelper svh;
            uphy->SetTxPowerSpectralDensity(svh.CreateTxPowerSpectralDensity(c.txDbm, kChannel));
            uphy->PlmeSetTRXStateRequest(lrwpan::IEEE_802_15_4_PHY_TX_ON);
        });
        for (uint32_t s = 0; s < nPk; ++s) {
            Simulator::Schedule(Seconds(kStartS + s * dt), [&, s]() {
                // The aircraft must be where the plan says, to within the arc sag.
                const Vector p = um->GetPosition();
                if (std::hypot(p.x - pkPos[s].x, p.y - pkPos[s].y) > 0.5 ||
                    std::fabs(p.z - c.altM) > 1e-6)
                    posErr++;
                uint8_t buf[kPsduBytes] = {};
                buf[0] = s >> 24; buf[1] = s >> 16; buf[2] = s >> 8; buf[3] = s;
                uphy->PdDataRequest(kPsduBytes, Create<Packet>(buf, kPsduBytes));
            });
        }
        Simulator::Stop(Seconds(kStartS + nPk * dt + 0.1));
        Simulator::Run();
        Simulator::Destroy();

        CHECK(txOk == nPk && txFail == 0);
        CHECK(std::fabs(txMin - c.txDbm) < 0.01 && std::fabs(txMax - c.txDbm) < 0.01);
        CHECK(dupes == 0 && bad == 0);
        CHECK(posErr == 0);
        CHECK(fadeN == (uint64_t)nPk * nNodes);
        const double fMean = fadeSum / fadeN;
        if (c.fading != "none") CHECK(std::fabs(fMean - 1.0) < 0.01);
        if (c.fading == "rician" && c.kFactor == 2.0) {
            CHECK(std::fabs((double)fade10 / fadeN / 4.61e-2 - 1.0) < 0.05);
            CHECK(std::fabs((double)fade20 / fadeN / 4.09e-3 - 1.0) < 0.10);
        }

        // ---- per node: what one segment gave, what the mission gave ----------
        std::vector<uint32_t> perSeg(nSeg);
        std::vector<uint8_t> have;
        std::vector<std::vector<uint8_t>> segHave(nSeg);
        uint64_t totRx = 0;
        for (uint32_t k = 0; k < nNodes; ++k) {
            NodeOut o;
            std::fill(perSeg.begin(), perSeg.end(), 0);
            for (uint32_t s = 0; s < nPk; ++s)
                if (got[k][s]) { o.received++; perSeg[pkSeg[s]]++; }
            for (int32_t g = 0; g < nSeg; ++g)
                if (perSeg[g]) { o.segs++; if (g % 2 == 0) o.lanes++; }
            totRx += o.received;
            for (uint32_t K : kFileSizes) {
                have.assign(K, 0);
                for (auto& h : segHave) h.assign(K, 0);
                uint32_t cov = 0;
                int64_t done = -1;
                std::vector<uint32_t> segCov(nSeg, 0);
                for (uint32_t s = 0; s < nPk; ++s) {
                    if (!got[k][s]) continue;
                    const uint32_t chunk = s % K;
                    if (!segHave[pkSeg[s]][chunk]) { segHave[pkSeg[s]][chunk] = 1; segCov[pkSeg[s]]++; }
                    if (!have[chunk]) {
                        have[chunk] = 1;
                        if (++cov == K && done < 0) done = s;
                    }
                }
                const uint32_t best = *std::max_element(segCov.begin(), segCov.end());
                CHECK(best <= cov && cov <= std::min(K, o.received));
                CHECK((done >= 0) == (cov == K));
                o.covUnion.push_back(cov);
                o.covBest.push_back(best);
                o.done.push_back(done);
            }
            std::fprintf(fn, "%u,%u,%.0f,%.0f,%.0f,%u,%u,%u", run, k, nodePos[k].x,
                         nodePos[k].y, dLane[k], o.received, o.segs, o.lanes);
            for (size_t i = 0; i < kFileSizes.size(); ++i)
                std::fprintf(fn, ",%u,%u,%lld", o.covUnion[i], o.covBest[i],
                             (long long)o.done[i]);
            std::fprintf(fn, "\n");
        }
        std::fflush(fn);

        // ---- bitmaps of one row, for the strip figures ------------------------
        if (run == 1) {
            FILE* fr = std::fopen((c.out + "-row.csv").c_str(), "w");
            std::fprintf(fr, "node,x,y,dLane,packets,bitsHex\n");
            for (uint32_t ix = 0; ix < nx; ++ix) {
                const uint32_t k = (uint32_t)c.dumpRow * nx + ix;
                std::fprintf(fr, "%u,%.0f,%.0f,%.0f,%u,", k, nodePos[k].x, nodePos[k].y,
                             dLane[k], nPk);
                for (uint32_t s = 0; s < nPk; s += 4) {
                    uint32_t nib = 0;
                    for (uint32_t b = 0; b < 4; ++b)
                        nib = nib << 1 | (s + b < nPk ? got[k][s + b] : 0);
                    std::fputc("0123456789abcdef"[nib], fr);
                }
                std::fputc('\n', fr);
            }
            std::fclose(fr);
        }
        std::printf("  mission %u: %lu receptions, mean fade power %.4f, P(<-10dB) %.3e\n",
                    run, (unsigned long)totRx, fMean, (double)fade10 / fadeN);
        std::fflush(stdout);
    }
    std::fclose(fn);
    std::printf("%u CHECKS PASSED\n", g_checks);
    return 0;
}
