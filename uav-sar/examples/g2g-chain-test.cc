// Edge cooperation inside one wide cluster: how long does a file take to cross it
// hop by hop on the ground?
//
// URBAN BRANCH ONLY -- channel from a2g-common.h (G2gLinkLossModel).
//
// A cluster too wide for the UAV to cover at once leaves one end holding packets
// the other end lacks. Here the nodes sit on a line 50-100 m apart, the head holds
// P packets, and they must reach the tail by UNICAST through every node in turn,
// on a fixed path.
//
// Ground-to-ground is not air-to-ground, in three ways that are all modelled:
//   channel   n = 3.5, static per-pair shadowing, Rayleigh fading held over a
//             coherence block -- a static link does not refresh its fade every
//             packet the way a passing aircraft does.
//   schedule  strict TDMA, because every node can both send and be interfered
//             with: slots of 10 ms, node i owns the slots with index = i (mod M).
//             M = 3 is the least a chain allows; nodes M apart share a slot.
//   unicast   in its slot a node sends the head of its queue to the next node,
//             which ACKs within the same slot. No ACK by 9 ms: try again in the
//             node's next slot. A duplicate (lost ACK) is ACKed again, not queued.
// The MAC is bypassed and all of this runs on the PHY directly, as in a2g-*.
//
// With shadowing and fading off (--selftest) every packet must arrive exactly at
//   (k M + H - 1) T_slot + turnaround + airtime,    H = number of hops,
// with no retransmission -- checked to the microsecond before anything else runs.
//
//   g2g-chain-test --spacing=75 --slots=3 --runs=200 --out=c75

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
#include <deque>
#include <functional>
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
using a2g::kFspl1mDb;

constexpr uint32_t kDataBytes = 127;   // aMaxPhyPacketSize
constexpr uint32_t kAckBytes  = 5;     // 802.15.4 ACK: FCF 2 + seq 1 + FCS 2
constexpr uint8_t  kTypeData  = 1, kTypeAck = 2;
constexpr double   kStartS    = 1.0;   // after the MAC has initialised
constexpr double   kAckWaitS  = 0.009; // into the slot: no ACK by now = failed

struct Cfg {
    double spacingM = 75.0, spanM = 1000.0;
    uint32_t packets = 100, slots = 3;
    double slotS = 0.010;
    double txDbm = 10.0, sensDbm = -100.0;
    double n = 3.5, sigmaDb = 7.8, cohS = 0.1, kFactor = 0.0;
    double limitS = 120.0;
    uint32_t runs = 200, traceRun = 1, seed = 1;
    bool selftest = false;
    std::string out = "chain";
};

struct Node {
    Ptr<lrwpan::LrWpanPhy> phy;
    Ptr<MobilityModel> mob;
    std::deque<uint16_t> queue;
    std::vector<uint8_t> seen;
    uint8_t pendType = 0, pendDst = 0;   // what the next TX_ON is for
    uint16_t pendSeq = 0;
    bool awaiting = false;
    uint16_t awaitSeq = 0;
    int64_t traceIdx = -1;               // row of the attempt in flight
};

struct Attempt { double t; uint32_t node; uint16_t seq; bool rx; bool ok; };  // rx: data arrived; ok: ACK came back

struct RunResult {
    bool complete = false;
    double completeS = -1, firstS = -1;
    uint32_t delivered = 0;
    uint64_t dataTx = 0, ackTx = 0, txFail = 0, overheard = 0;
    std::vector<uint64_t> attempts, acked, holds;   // holds[i]: distinct packets at node i
    std::vector<double> shadowDb, arrivalS;
    std::vector<Attempt> trace;
};

double PathLossDb(double d, double n) { return kFspl1mDb + 10.0 * n * std::log10(d); }

RunResult RunOnce(const Cfg& c, uint32_t run, bool keepTrace, Ptr<G2gLinkLossModel>& linkOut) {
    const uint32_t hops = (uint32_t)std::lround(c.spanM / c.spacingM);
    const uint32_t N = hops + 1;
    CHECK(N <= 255 && c.packets <= 65535 && c.slots >= 2);
    RngSeedManager::SetSeed(c.seed);
    RngSeedManager::SetRun(run);

    NodeContainer nc;
    nc.Create(N);
    MobilityHelper mh;
    mh.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    mh.Install(nc);
    for (uint32_t i = 0; i < N; ++i)
        nc.Get(i)->GetObject<MobilityModel>()->SetPosition(Vector(i * c.spacingM, 0, 1.5));

    // ONE helper, alive until Destroy: its destructor disposes the channel.
    LrWpanHelper lr;
    Ptr<G2gLinkLossModel> link;
    Ptr<SpectrumChannel> ch = a2g::BuildG2gChannel(c.n, c.selftest ? 0.0 : c.sigmaDb,
                                                   c.selftest ? 0.0 : c.cohS, c.kFactor, link);
    lr.SetChannel(ch);
    NetDeviceContainer devs = lr.Install(nc);
    CHECK(ch->GetNDevices() == N);

    std::vector<Node> node(N);
    RunResult R;
    R.attempts.assign(hops, 0);
    R.acked.assign(hops, 0);
    R.arrivalS.assign(c.packets, -1.0);
    for (uint32_t i = 0; i < N; ++i) {
        node[i].phy = DynamicCast<lrwpan::LrWpanNetDevice>(devs.Get(i))->GetPhy();
        node[i].mob = nc.Get(i)->GetObject<MobilityModel>();
        node[i].seen.assign(c.packets, 0);
    }

    auto send = [&](uint32_t i, uint8_t type, uint8_t dst, uint16_t seq) {
        node[i].pendType = type;
        node[i].pendDst = dst;
        node[i].pendSeq = seq;
        node[i].phy->PlmeSetTRXStateRequest(lrwpan::IEEE_802_15_4_PHY_TX_ON);
    };

    for (uint32_t i = 0; i < N; ++i) {
        Node& me = node[i];
        me.phy->SetPlmeSetTRXStateConfirmCallback(lrwpan::PlmeSetTRXStateConfirmCallback(
            [&, i](lrwpan::PhyEnumeration s) {
                Node& m = node[i];
                if (s != lrwpan::IEEE_802_15_4_PHY_TX_ON || m.pendType == 0) return;
                const uint32_t len = m.pendType == kTypeData ? kDataBytes : kAckBytes;
                std::vector<uint8_t> b(len, 0);
                b[0] = m.pendType; b[1] = (uint8_t)i; b[2] = m.pendDst;
                b[3] = m.pendSeq >> 8; b[4] = m.pendSeq & 0xff;
                (m.pendType == kTypeData ? R.dataTx : R.ackTx)++;
                m.pendType = 0;
                m.phy->PdDataRequest(len, Create<Packet>(b.data(), len));
            }));
        me.phy->SetPdDataConfirmCallback(lrwpan::PdDataConfirmCallback(
            [&, i](lrwpan::PhyEnumeration s) {
                if (s != lrwpan::IEEE_802_15_4_PHY_SUCCESS) R.txFail++;
                node[i].phy->PlmeSetTRXStateRequest(lrwpan::IEEE_802_15_4_PHY_RX_ON);
            }));
        me.phy->SetPdDataIndicationCallback(lrwpan::PdDataIndicationCallback(
            [&, i, N](uint32_t len, Ptr<Packet> p, uint8_t) {
                uint8_t b[5];
                if (len < 5 || p->CopyData(b, 5) != 5) return;
                const uint8_t type = b[0], src = b[1], dst = b[2];
                const uint16_t seq = (uint16_t)(b[3] << 8 | b[4]);
                Node& m = node[i];
                if (dst != i) { R.overheard++; return; }
                if (type == kTypeData && len == kDataBytes && src + 1u == i) {
                    if (node[src].traceIdx >= 0) R.trace[node[src].traceIdx].rx = true;
                    if (!m.seen[seq]) {
                        m.seen[seq] = 1;
                        if (i == N - 1) {
                            R.arrivalS[seq] = Simulator::Now().GetSeconds() - kStartS;
                            if (++R.delivered == c.packets) {
                                R.complete = true;
                                R.completeS = R.arrivalS[seq];
                                Simulator::Stop(MilliSeconds(1));
                            }
                        } else {
                            m.queue.push_back(seq);
                        }
                    }
                    send(i, kTypeAck, src, seq);   // ACK every copy, duplicates too
                } else if (type == kTypeAck && len == kAckBytes && src == i + 1 && m.awaiting &&
                           seq == m.awaitSeq) {
                    m.awaiting = false;
                    m.queue.pop_front();
                    R.acked[i]++;
                    if (m.traceIdx >= 0) R.trace[m.traceIdx].ok = true;
                }
            }));
    }

    // Radios on after the MAC's own start-up; SetRxSensitivity rebuilds the TX PSD,
    // so the PSD is set after it.
    Simulator::Schedule(Seconds(kStartS / 2), [&]() {
        lrwpan::LrWpanSpectrumValueHelper svh;
        for (Node& m : node) {
            m.phy->SetRxSensitivity(c.sensDbm);
            m.phy->SetTxPowerSpectralDensity(svh.CreateTxPowerSpectralDensity(c.txDbm, kChannel));
            m.phy->PlmeSetTRXStateRequest(lrwpan::IEEE_802_15_4_PHY_RX_ON);
        }
    });

    // The head holds the file.
    for (uint32_t k = 0; k < c.packets; ++k) {
        node[0].queue.push_back((uint16_t)k);
        node[0].seen[k] = 1;
    }

    // The schedule: one event per slot; the owners of the slot send.
    const uint64_t maxSlots = (uint64_t)std::ceil(c.limitS / c.slotS);
    std::function<void(uint64_t)> slot = [&](uint64_t s) {
        for (uint32_t i = 0; i + 1 < N; ++i) {
            if (i % c.slots != s % c.slots) continue;
            Node& m = node[i];
            if (m.queue.empty()) continue;
            m.awaiting = true;
            m.awaitSeq = m.queue.front();
            R.attempts[i]++;
            if (keepTrace) {
                m.traceIdx = (int64_t)R.trace.size();
                R.trace.push_back({Simulator::Now().GetSeconds() - kStartS, i, m.awaitSeq, false, false});
            }
            send(i, kTypeData, (uint8_t)(i + 1), m.awaitSeq);
            Simulator::Schedule(Seconds(kAckWaitS), [&, i]() {
                node[i].awaiting = false;   // no ACK: the packet stays at the head
                node[i].traceIdx = -1;
            });
        }
        if (s + 1 < maxSlots) Simulator::Schedule(Seconds(c.slotS), [&slot, s]() { slot(s + 1); });
    };
    Simulator::Schedule(Seconds(kStartS), [&slot]() { slot(0); });

    Simulator::Stop(Seconds(kStartS + c.limitS + 0.1));
    Simulator::Run();

    for (uint32_t h = 0; h < hops; ++h)
        R.shadowDb.push_back(link->ShadowDb(node[h].mob, node[h + 1].mob));
    for (uint32_t i = 0; i < N; ++i)
        R.holds.push_back((uint64_t)std::count(node[i].seen.begin(), node[i].seen.end(), 1));
    for (double a : R.arrivalS)
        if (a >= 0 && (R.firstS < 0 || a < R.firstS)) R.firstS = a;
    linkOut = link;
    Simulator::Destroy();
    return R;
}

}  // namespace

int main(int argc, char* argv[]) {
    Cfg c;
    double slotMs = 10.0;
    CommandLine cmd(__FILE__);
    cmd.AddValue("spacing", "node spacing, m", c.spacingM);
    cmd.AddValue("span", "cluster width, m (hops = span / spacing)", c.spanM);
    cmd.AddValue("packets", "packets the head holds", c.packets);
    cmd.AddValue("slots", "TDMA reuse factor M: node i sends in slots = i mod M", c.slots);
    cmd.AddValue("slotMs", "slot length, ms", slotMs);
    cmd.AddValue("tx", "node transmit power, dBm", c.txDbm);
    cmd.AddValue("sens", "receiver sensitivity, dBm (ns-3 semantics)", c.sensDbm);
    cmd.AddValue("n", "G2G path-loss exponent from 1 m", c.n);
    cmd.AddValue("sigma", "static shadowing per pair, dB", c.sigmaDb);
    cmd.AddValue("coh", "fading coherence time, s", c.cohS);
    cmd.AddValue("K", "Rician K of the fading (0 = Rayleigh)", c.kFactor);
    cmd.AddValue("limit", "give up after this long, s", c.limitS);
    cmd.AddValue("runs", "independent chains", c.runs);
    // ns-3 hands out random-stream indices from a process-wide counter that is not
    // reset between chains, so chain r is reproduced only by running 1..r again in
    // one process: --runs=r --traceRun=r. (Chains stay independent: each has its
    // own streams and its own substream.)
    cmd.AddValue("traceRun", "chain whose attempt-by-attempt trace is dumped", c.traceRun);
    cmd.AddValue("seed", "RNG seed", c.seed);
    cmd.AddValue("selftest", "no shadowing, no fading: arrivals must match the schedule", c.selftest);
    cmd.AddValue("out", "output prefix", c.out);
    cmd.Parse(argc, argv);
    c.slotS = slotMs / 1000.0;
    CHECK(c.slotS >= 0.006);   // data + turnaround + ACK must fit: ~5.2 ms

    const uint32_t hops = (uint32_t)std::lround(c.spanM / c.spacingM);
    // The self-test checks the SCHEDULE, so it needs a link that does not lose
    // packets by itself: >= 6 dB above sensitivity with no shadowing or fading.
    // (At 100 m, +10 dBm, n = 3.5 the median link sits 1 dB above ns-3's PER-50%
    // point and loses ~6 % of frames -- a finding, not a schedule fault.)
    if (c.selftest) CHECK(c.txDbm - PathLossDb(c.spacingM, c.n) >= c.sensDbm + 6.0);
    const double airData = (6 + kDataBytes) * 8 / 250e3;   // SHR+PHR + PSDU
    const double turn = 12 * 16e-6;                         // aTurnaroundTime, 12 symbols
    std::printf("chain: %u nodes, %u hops of %.0f m (%.0f m); %u packets; TDMA M=%u, slot "
                "%.0f ms; TX %+.0f dBm, n %.2f, shadowing %.1f dB static, fading K=%.0f "
                "coherence %.0f ms%s\n",
                hops + 1, hops, c.spacingM, hops * c.spacingM, c.packets, c.slots,
                c.slotS * 1000, c.txDbm, c.n, c.selftest ? 0.0 : c.sigmaDb, c.kFactor,
                c.selftest ? 0.0 : c.cohS * 1000, c.selftest ? "  [SELFTEST]" : "");
    std::printf("  median link margin per hop: Prx %.1f dBm vs ns-3 PER-50%% point ~%.1f dBm\n",
                c.txDbm - PathLossDb(c.spacingM, c.n), c.sensDbm - 1.0);

    FILE* fr = std::fopen((c.out + "-runs.csv").c_str(), "w");
    FILE* fh = std::fopen((c.out + "-hops.csv").c_str(), "w");
    FILE* fa = std::fopen((c.out + "-arrivals.csv").c_str(), "w");
    std::fprintf(fr, "run,complete,completeS,firstS,delivered,dataTx,ackTx,overheard\n");
    std::fprintf(fh, "run,hop,attempts,acked,shadowDb,medianPrxDbm\n");
    std::fprintf(fa, "run,seq,arrivalS\n");

    uint64_t nSh = 0, nF = 0, nF10 = 0, nF20 = 0;
    double sSh = 0, sSh2 = 0, sF = 0;
    uint32_t nComplete = 0;
    std::vector<double> times;
    for (uint32_t run = 1; run <= c.runs; ++run) {
        Ptr<G2gLinkLossModel> link;
        RunResult R = RunOnce(c, run, run == c.traceRun, link);
        CHECK(R.txFail == 0);
        CHECK(R.delivered <= c.packets);
        // Flow conservation: a node only holds what its predecessor sent it, so the
        // count of distinct packets can only fall along the chain. An ACK is only
        // ever counted for a packet the next node really holds. (A lost ACK lets a
        // packet run ahead of its sender's bookkeeping, so acked < delivered is legal.)
        CHECK(R.holds.front() == c.packets && R.holds.back() == R.delivered);
        for (uint32_t h = 0; h < hops; ++h) {
            CHECK(R.holds[h + 1] <= R.holds[h]);
            CHECK(R.acked[h] <= R.attempts[h]);
            CHECK(R.acked[h] <= R.holds[h + 1]);
        }
        nSh += link->nShadow; sSh += link->sumShadow; sSh2 += link->sumShadow2;
        nF += link->nFade; nF10 += link->nFade10; nF20 += link->nFade20; sF += link->sumFade;

        if (c.selftest) {
            // The schedule, exactly: packet k leaves the head in slot kM, moves one
            // hop per slot, and lands at the tail in slot kM + H - 1.
            CHECK(R.complete);
            for (uint32_t h = 0; h < hops; ++h) CHECK(R.attempts[h] == c.packets);
            const double prop = c.spacingM / 299792458.0;
            for (uint32_t k = 0; k < c.packets; ++k) {
                const double want = (k * c.slots + hops - 1) * c.slotS + turn + airData + prop;
                CHECK(std::fabs(R.arrivalS[k] - want) < 1e-6);
            }
        }
        if (R.complete) { nComplete++; times.push_back(R.completeS); }
        std::fprintf(fr, "%u,%d,%.6f,%.6f,%u,%lu,%lu,%lu\n", run, R.complete ? 1 : 0,
                     R.completeS, R.firstS, R.delivered, (unsigned long)R.dataTx,
                     (unsigned long)R.ackTx, (unsigned long)R.overheard);
        for (uint32_t h = 0; h < hops; ++h)
            std::fprintf(fh, "%u,%u,%lu,%lu,%.3f,%.2f\n", run, h, (unsigned long)R.attempts[h],
                         (unsigned long)R.acked[h], R.shadowDb[h],
                         c.txDbm - PathLossDb(c.spacingM, c.n) - R.shadowDb[h]);
        for (uint32_t k = 0; k < c.packets; ++k)
            std::fprintf(fa, "%u,%u,%.6f\n", run, k, R.arrivalS[k]);
        if (run == c.traceRun) {
            FILE* ft = std::fopen((c.out + "-trace.csv").c_str(), "w");
            std::fprintf(ft, "t,node,seq,rx,ok\n");
            for (const Attempt& a : R.trace) {
                CHECK(!a.ok || a.rx);   // an ACK only ever answers data that arrived
                std::fprintf(ft, "%.6f,%u,%u,%d,%d\n", a.t, a.node, a.seq, a.rx ? 1 : 0,
                             a.ok ? 1 : 0);
            }
            std::fclose(ft);
        }
    }
    std::fclose(fr); std::fclose(fh); std::fclose(fa);

    // The channel drew what it was asked to draw.
    if (!c.selftest && nSh > 500) {
        const double m = sSh / nSh, sd = std::sqrt(sSh2 / nSh - m * m);
        std::printf("  shadowing drawn: %lu pairs, mean %+.2f dB, sd %.2f dB (asked %.1f)\n",
                    (unsigned long)nSh, m, sd, c.sigmaDb);
        CHECK(std::fabs(m) < 0.1 * c.sigmaDb + 0.2);
        CHECK(std::fabs(sd / c.sigmaDb - 1.0) < 0.05);
    }
    if (!c.selftest && nF > 5000) {
        std::printf("  fading drawn: %lu blocks, mean power %.3f, P(<-10dB) %.4f, P(<-20dB) "
                    "%.5f\n", (unsigned long)nF, sF / nF, (double)nF10 / nF, (double)nF20 / nF);
        CHECK(std::fabs(sF / nF - 1.0) < 0.03);
        if (c.kFactor == 0.0) {   // Rayleigh: P(g < x) = 1 - exp(-x)
            CHECK(std::fabs((double)nF10 / nF / (1 - std::exp(-0.1)) - 1.0) < 0.06);
            CHECK(std::fabs((double)nF20 / nF / (1 - std::exp(-0.01)) - 1.0) < 0.25);
        }
    }
    std::sort(times.begin(), times.end());
    std::printf("  complete within %.0f s: %u / %u", c.limitS, nComplete, c.runs);
    if (!times.empty())
        std::printf("   time: median %.2f s, p10 %.2f, p90 %.2f, best %.2f\n",
                    times[times.size() / 2], times[(size_t)(0.1 * (times.size() - 1))],
                    times[(size_t)(0.9 * (times.size() - 1))], times.front());
    else
        std::printf("\n");
    std::printf("%u CHECKS PASSED\n", g_checks);
    return 0;
}
