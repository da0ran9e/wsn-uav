// The River scheme (L3-vi.md, Algorithms 5-7) on ns-3, after a uav-coop pass.
//
//   uav-coop2-river --nodes=deploy-nodes-s35.csv --routes=deploy-routes-s35.csv
//       --gateways=deploy-gateways-s35.csv --plan=river-plan.txt --bits=BITS/p --runs=1
//       --scheme=river --prep=full --out=OUT
//
// Radio: every node has a full IEEE 802.15.4 device (MAC with unslotted CSMA/CA, ACK,
// retries; ns-3 lr-wpan) on its cell's channel; every gateway of a cell pair has one more
// device, on that pair's own channel. The PECEE cell grid sets the channels:
//   --colours=n  cell (q, r) on 11 + (q + k r) mod n, gateway pairs on 11+n .. 26:
//                n = 3, k = 2: same channel 2 cells apart     n = 4, k = 2: 2 cells apart
//                n = 7, k = 3: 3 cells apart                  n = 13, k = 4: 4 cells apart
//   a gateway pair takes the lowest of its channels not used by a pair within 300 m
// Each channel number is its own SpectrumChannel (the 802.15.4 channels do not overlap).
// G2G loss: n = 3.5 from 1 m, static shadowing per pair (sigma 7.8 dB), Rayleigh blocks of
// 100 ms (the statistics of uav-coop coop-g2g.h). Shadowing and fading are drawn from a hash
// of (mission, node pair, block), so every configuration of a mission sees the same channel.
// Schedule (PECEE grid, over the MAC): one transmitter at a time per cell and per gateway
// pair, round robin among the radios with frames; a frame the MAC gives up on waits for the
// radio's next turn.
//
// Routing: a cell path is CL -> gateway -> ... -> CL over one gateway pair per adjacent cell
// pair (--gwSelect=deploy: those of uav-coop, chosen by geometry; quality: the pair of nodes
// with the best link in the mission, as the BS would pick knowing the static shadowing);
// inside a cell, least ETX on the run's links.
// A cell's data lives at its CL (gathered from its nodes).
// The pass: the node's reception bitmaps from uav-coop-pass --bits (BITS-rR.bin).
//
// Schemes:
//   river --prep=full      Banks filled by their Axe (Alg. 5), Circle members fetch their
//                          whole share from the Banks ahead (Alg. 6), critical cells pull
//                          what they lack from their members (Alg. 7)
//   river --prep=ondemand  as above, but a member fetches only what its critical cell asks for,
//                          after it asks
//   direct                 each critical cell asks every Axe cell for what it lacks of Seg(a)
// Writes OUT-crit.csv (per run and critical cell) and OUT-runs.csv (per run).

#include "ns3/core-module.h"
#include "ns3/lr-wpan-module.h"
#include "ns3/mobility-module.h"
#include "ns3/network-module.h"
#include "ns3/propagation-module.h"
#include "ns3/river-plan.h"
#include "ns3/spectrum-module.h"

#include "../../uav-coop/models/common/coop-params.h"

#include <algorithm>
#include <chrono>
#include <cstring>
#include <cstdio>
#include <deque>
#include <fstream>
#include <functional>
#include <map>
#include <set>
#include <sstream>
#include <unordered_map>
#include <unordered_set>

using namespace ns3;
using namespace ns3::uavcoop;
using ns3::uavcoop2::Plan;

#define CHECK(cond)                                                                \
    do {                                                                           \
        if (!(cond)) {                                                             \
            std::fprintf(stderr, "CHECK failed at line %d: %s\n", __LINE__, #cond); \
            std::exit(1);                                                          \
        }                                                                          \
    } while (0)

namespace {

// The G2G channel of coop-g2g.h with its draws taken from a hash instead of a stream: the
// static shadowing of a node pair, and the fade of each of its blocks, depend only on the
// mission and the deploy ids of the two nodes (reciprocal), never on what else is simulated.
class PairG2gLoss : public PropagationLossModel {
  public:
    static TypeId GetTypeId() {
        static TypeId tid = TypeId("ns3::uavcoop2::PairG2gLoss")
                                .SetParent<PropagationLossModel>()
                                .AddConstructor<PairG2gLoss>();
        return tid;
    }
    uint64_t mission = 0;
    std::unordered_map<const MobilityModel*, int> id;   // mobility -> deploy node id

    // The static shadowing of nodes ia, ib in a mission, dB (what Link draws for them).
    static double Shadow(uint64_t mission, int ia, int ib) {
        return params::kG2gShadowDb * Normal(Mix(Key(mission, ia, ib) ^ 1));
    }

  private:
    struct State {
        uint64_t key = 0;
        double shadowDb = 0, phase = 0, fadeDb = 0;
        int64_t block = -1;
    };
    static uint64_t Mix(uint64_t x) {   // splitmix64
        x += 0x9e3779b97f4a7c15ULL;
        x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
        x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
        return x ^ (x >> 31);
    }
    static double Unit(uint64_t h) { return ((h >> 11) + 0.5) * 0x1.0p-53; }
    static double Normal(uint64_t h) {
        return std::sqrt(-2 * std::log(Unit(h))) * std::cos(2 * M_PI * Unit(Mix(h)));
    }
    static uint64_t Key(uint64_t mission, int ia, int ib) {
        return Mix(Mix(mission) ^ ((uint64_t)std::min(ia, ib) << 32 | (uint64_t)std::max(ia, ib)));
    }
    State& Link(Ptr<MobilityModel> a, Ptr<MobilityModel> b) const {
        const int ia = id.at(PeekPointer(a)), ib = id.at(PeekPointer(b));
        const uint64_t pair = (uint64_t)std::min(ia, ib) << 32 | (uint64_t)std::max(ia, ib);
        auto it = m_links.find(pair);
        if (it != m_links.end()) return it->second;
        State st;
        st.key = Key(mission, ia, ib);
        st.shadowDb = Shadow(mission, ia, ib);
        st.phase = Unit(Mix(st.key ^ 2)) * params::kG2gCoherenceS;
        return m_links.emplace(pair, st).first->second;
    }
    double DoCalcRxPower(double txPowerDbm, Ptr<MobilityModel> a, Ptr<MobilityModel> b) const override {
        State& st = Link(a, b);
        const int64_t blk = (int64_t)std::floor((Simulator::Now().GetSeconds() + st.phase) / params::kG2gCoherenceS);
        if (blk != st.block) {
            const double k = params::kG2gRicianK;
            const uint64_t h = Mix(st.key ^ Mix((uint64_t)blk + 3));
            const double i = std::sqrt(k / (k + 1)) + std::sqrt(0.5 / (k + 1)) * Normal(h);
            const double q = std::sqrt(0.5 / (k + 1)) * Normal(Mix(h ^ 0x5bd1e9955bd1e995ULL));
            st.fadeDb = 10 * std::log10(i * i + q * q);
            st.block = blk;
        }
        return txPowerDbm - st.shadowDb + st.fadeDb;
    }
    int64_t DoAssignStreams(int64_t) override { return 0; }
    mutable std::unordered_map<uint64_t, State> m_links;
};
NS_OBJECT_ENSURE_REGISTERED(PairG2gLoss);

constexpr double kT0 = 0.01;          // protocol start (s); the PHYs are set up just before
constexpr uint32_t kDataBytes = 100;  // MSDU of a data frame (99 B payload + header, capped)
constexpr uint32_t kCtrlBytes = 20;   // MSDU of a request frame
constexpr uint16_t kPan = 1;

std::vector<std::vector<std::string>> ReadCsv(const std::string& f) {
    std::ifstream in(f);
    CHECK(in.good());
    std::vector<std::vector<std::string>> rows;
    std::string line;
    while (std::getline(in, line)) {
        std::vector<std::string> r;
        std::stringstream ss(line);
        std::string x;
        while (std::getline(ss, x, ',')) r.push_back(x);
        rows.push_back(r);
    }
    return rows;
}

struct NodeInfo {
    double x = 0, y = 0;
    Hex cell;
    bool cl = false;
    std::map<Hex, int> toCell;
};

struct Radio {
    Ptr<lrwpan::LrWpanNetDevice> dev;
    int node = -1;
    uint16_t addr = 0;
    std::deque<std::pair<uint32_t, uint8_t>> q;   // (job, hop index it carries), next hop below
    std::deque<int> qNext;
    int medium = -1;                              // the cell, or the gateway pair, it sends on
    bool waiting = false;
    std::unordered_set<uint64_t> seen;            // (job, index) already taken in
};

// One transmitter at a time per cell medium and per gateway pair (the PECEE grid schedule);
// the radios that have frames wait their turn, round robin.
struct Medium {
    int owner = -1;
    std::deque<int> wait;
};

struct Job {
    int path = -1;              // -1: gather to the start node's CL
    int32_t s = -1;             // packet, or -1 for a request frame
    int phase = 0;
    std::function<void()> done;
    Hex dst;
};

enum Phase { kGather, kBankFill, kCircleFill, kPull, kControl, kPhases };
const char* kPhaseName[kPhases] = {"gather", "bankfill", "circlefill", "pull", "control"};

}  // namespace

int main(int argc, char* argv[]) {
    std::string nodesCsv, routesCsv, gwCsv, planFile, bits, out = "river-ns3", scheme = "river",
                                                           prep = "full", trace;
    uint32_t firstRun = 1, runs = 1;
    double limitS = 1800, maxLossDb = 130;
    int colours = 7;
    std::string gwSelect = "deploy";
    CommandLine cmd;
    cmd.AddValue("nodes", "deploy-nodes-sS.csv", nodesCsv);
    cmd.AddValue("routes", "deploy-routes-sS.csv", routesCsv);
    cmd.AddValue("gateways", "deploy-gateways-sS.csv", gwCsv);
    cmd.AddValue("plan", "river-plan.txt (tools/river_export.py)", planFile);
    cmd.AddValue("bits", "prefix of the pass bitmaps: PREFIX-rR.bin", bits);
    cmd.AddValue("firstRun", "first mission", firstRun);
    cmd.AddValue("runs", "missions", runs);
    cmd.AddValue("scheme", "river | direct", scheme);
    cmd.AddValue("prep", "river only: full | ondemand", prep);
    cmd.AddValue("limit", "stop a mission after this many seconds", limitS);
    cmd.AddValue("maxLoss", "SpectrumChannel MaxLossDb", maxLossDb);
    cmd.AddValue("colours", "cell channels: 3, 4, 7 or 13 colours", colours);
    cmd.AddValue("gwSelect", "gateway pair of each cell pair: deploy (uav-coop, by geometry) | quality "
                 "(the BS picks the best link of the mission)", gwSelect);
    cmd.AddValue("out", "output prefix", out);
    cmd.AddValue("trace", "prefix: the first mission's hops, CL arrivals, in-cell routes and gateway pairs",
                 trace);
    cmd.Parse(argc, argv);
    CHECK(scheme == "river" || scheme == "direct");
    CHECK(prep == "full" || prep == "ondemand");
    CHECK(colours == 3 || colours == 4 || colours == 7 || colours == 13);
    CHECK(gwSelect == "deploy" || gwSelect == "quality");

    // ---- static inputs ----------------------------------------------------------
    const Plan plan = uavcoop2::ReadPlan(planFile);
    auto nrows = ReadCsv(nodesCsv);
    std::vector<NodeInfo> nodes(nrows.size() - 1);
    std::map<Hex, int> clOf;
    std::map<Hex, std::vector<int>> members;
    for (size_t i = 1; i < nrows.size(); ++i) {
        auto& r = nrows[i];   // id,x,y,q,r,nnM,edgeM,obs,cpu,comm,score,isCH,isCL
        CHECK(std::stoul(r[0]) == i - 1);
        NodeInfo& n = nodes[i - 1];
        n.x = std::stod(r[1]);
        n.y = std::stod(r[2]);
        n.cell = Hex{std::stoi(r[3]), std::stoi(r[4])};
        n.cl = r[12] == "1";
        if (n.cl) clOf[n.cell] = (int)i - 1;
        members[n.cell].push_back((int)i - 1);
    }
    auto rrows = ReadCsv(routesCsv);   // id,...,toCells (only to check the gateway pairs)
    CHECK(rrows.size() == nrows.size());
    for (size_t i = 1; i < rrows.size(); ++i) {
        auto& r = rrows[i];
        NodeInfo& n = nodes[std::stoul(r[0])];
        std::stringstream ss(r.back());
        std::string e;
        while (std::getline(ss, e, '|')) {   // q:r>next/hops
            int q, rr, nx, h;
            CHECK(std::sscanf(e.c_str(), "%d:%d>%d/%d", &q, &rr, &nx, &h) == 4);
            n.toCell[Hex{q, rr}] = nx;
        }
    }
    std::map<std::pair<Hex, Hex>, std::pair<int, int>> gw;   // (A,B) -> (gw in A, gw in B)
    for (auto& r : ReadCsv(gwCsv)) {
        if (r[0] == "qA") continue;
        Hex A{std::stoi(r[0]), std::stoi(r[1])}, B{std::stoi(r[2]), std::stoi(r[3])};
        int a = std::stoi(r[4]), b = std::stoi(r[5]);
        gw[{A, B}] = {a, b};
        gw[{B, A}] = {b, a};
        CHECK(nodes[a].toCell.at(B) == b && nodes[b].toCell.at(A) == a);
    }
    const uint32_t N = plan.packets;

    // Paths: every cell path the plan can use, with the reversed ones for the requests.
    std::vector<std::vector<Hex>> paths;
    auto addPath = [&](std::vector<Hex> p) {
        paths.push_back(std::move(p));
        return (int)paths.size() - 1;
    };
    std::set<Hex> used;
    for (auto& x : plan.axe) used.insert(x.a);
    for (auto& x : plan.crit) used.insert(x);
    for (auto& x : plan.banks) used.insert(x.path.begin(), x.path.end());
    for (auto& x : plan.circ) {
        used.insert(x.path.begin(), x.path.end());
        used.insert(x.k);
    }
    if (scheme == "direct")
        for (auto& x : plan.direct) used.insert(x.path.begin(), x.path.end());
    for (const Hex& h : used) CHECK(clOf.count(h));
    for (const Hex& h : used)   // every hop of every path is a real gateway link
        (void)h;
    auto checkPath = [&](const std::vector<Hex>& p) {
        for (size_t i = 0; i + 1 < p.size(); ++i) CHECK(gw.count({p[i], p[i + 1]}));
    };
    for (auto& x : plan.banks) checkPath(x.path);
    for (auto& x : plan.circ) checkPath(x.path);
    for (auto& x : plan.direct) checkPath(x.path);

    // Channels from the PECEE cell grid.
    const int colourK = colours == 13 ? 4 : colours == 7 ? 3 : 2;
    auto cellChannel = [&](const Hex& h) { return 11 + (((h.q + colourK * h.r) % colours) + colours) % colours; };
    const int firstPairChannel = 11 + colours, pairChannels = 26 - firstPairChannel + 1;
    std::map<std::pair<Hex, Hex>, int> pairChannel;   // key with A < B
    auto assignPairChannels = [&](bool print) {
        pairChannel.clear();
        std::vector<std::pair<Hex, Hex>> keys;
        for (auto& [k, v] : gw)
            if (k.first < k.second && used.count(k.first) && used.count(k.second)) keys.push_back(k);
        uint32_t clashes = 0;
        for (auto& k : keys) {
            auto [a, b] = gw[k];
            std::set<int> taken;
            for (auto& [k2, ch] : pairChannel) {
                auto [c, d] = gw[k2];
                double dmin = 1e9;
                for (int u : {a, b})
                    for (int v : {c, d}) dmin = std::min(dmin, std::hypot(nodes[u].x - nodes[v].x, nodes[u].y - nodes[v].y));
                if (dmin < 300) taken.insert(ch);
            }
            int ch = -1;
            for (int c = firstPairChannel; c <= 26 && ch < 0; ++c)
                if (!taken.count(c)) ch = c;
            if (ch < 0) {
                ch = firstPairChannel + (int)(pairChannel.size() % pairChannels);
                clashes++;
            }
            pairChannel[k] = ch;
        }
        if (print)
            std::printf("channels: cells 11-%d (%d-colour grid), %zu gateway pairs on %d-26, %u pairs share a "
                        "channel with a pair within 300 m\n", 10 + colours, colours, keys.size(), firstPairChannel,
                        clashes);
    };
    // Mean success probability of link a-b in a mission: Rayleigh around the mean (path loss, the
    // pair's static shadowing) against the sensitivity.
    auto linkQ = [&](uint32_t mission, int a, int b) {
        const double d = std::max(1.0, std::hypot(nodes[a].x - nodes[b].x, nodes[a].y - nodes[b].y));
        const double meanDbm = params::kTxPowerDbm - params::kFspl1mDb - 10 * params::kG2gExponent * std::log10(d) -
                               PairG2gLoss::Shadow(mission, a, b);
        return std::max(1e-6, std::exp(-std::pow(10.0, (params::kRxSensDbm - meanDbm) / 10)));
    };
    const auto gwDeploy = gw;
    std::vector<int> nodeIds;
    for (const Hex& h : used)
        for (int v : members[h]) nodeIds.push_back(v);
    std::printf("plan: %zu Axe, %zu critical, %zu cells and %zu nodes simulated, %u packets\n", plan.axe.size(),
                plan.crit.size(), used.size(), nodeIds.size(), N);

    FILE* fc = std::fopen((out + "-crit.csv").c_str(), "w");
    FILE* fr = std::fopen((out + "-runs.csv").c_str(), "w");
    CHECK(fc && fr);
    std::fprintf(fc, "run,scheme,q,r,D,lackCL,lackCell,gatherDoneS,doneS,missing\n");
    std::fprintf(fr, "run,scheme,D,simS,wallS,hops,gather,bankfill,circlefill,pull,control,macFail\n");

    for (uint32_t run = firstRun; run < firstRun + runs; ++run) {
        const auto wall0 = std::chrono::steady_clock::now();
        // ---- gateway pairs and their channels ---------------------------------------
        gw = gwDeploy;
        if (gwSelect == "quality")   // still one gateway pair per cell pair: the best link
            for (auto& [k, v] : gwDeploy) {
                if (!(k.first < k.second) || !used.count(k.first) || !used.count(k.second)) continue;
                std::pair<int, int> best = v;
                for (int a : members[k.first])
                    for (int b : members[k.second])
                        if (linkQ(run, a, b) > linkQ(run, best.first, best.second)) best = {a, b};
                gw[k] = best;
                gw[{k.second, k.first}] = {best.second, best.first};
            }
        assignPairChannels(run == firstRun);
        // ---- the pass: who received what -----------------------------------------
        const uint32_t rowBytes = (N + 7) / 8;
        std::vector<std::vector<uint8_t>> rx(nodes.size());
        {
            std::ifstream in(bits + "-r" + std::to_string(run) + ".bin", std::ios::binary);
            CHECK(in.good());
            std::vector<uint8_t> row(rowBytes);
            for (size_t k = 0; k < nodes.size(); ++k) {
                in.read((char*)row.data(), rowBytes);
                CHECK((size_t)in.gcount() == rowBytes);
                rx[k].assign(N, 0);
                for (uint32_t s = 0; s < N; ++s) rx[k][s] = (row[s / 8] >> (s % 8)) & 1;
            }
        }
        std::vector<uint8_t> inD(N, 0);
        std::map<Hex, std::pair<uint32_t, uint32_t>> seg;
        for (auto& x : plan.axe) {
            seg[x.a] = {x.first, x.last};
            for (uint32_t s = x.first; s <= x.last; ++s)
                for (size_t k = 0; k < nodes.size() && !inD[s]; ++k) inD[s] |= rx[k][s];
        }
        uint32_t Dn = 0;
        for (uint32_t s = 0; s < N; ++s) Dn += inD[s];

        // ---- ns-3 network ------------------------------------------------------------
        std::map<int, Ptr<SpectrumChannel>> chans;
        // One loss chain for every channel: shadowing and fading belong to the node pair, so
        // the channel plan does not change which links are weak.
        Ptr<LogDistancePropagationLossModel> pl = CreateObject<LogDistancePropagationLossModel>();
        pl->SetAttribute("Exponent", DoubleValue(params::kG2gExponent));
        pl->SetAttribute("ReferenceDistance", DoubleValue(1.0));
        pl->SetAttribute("ReferenceLoss", DoubleValue(params::kFspl1mDb));
        Ptr<PairG2gLoss> link = CreateObject<PairG2gLoss>();
        link->mission = run;
        pl->SetNext(link);
        auto chanOf = [&](int c) {
            if (!chans.count(c)) {
                Ptr<SingleModelSpectrumChannel> ch = CreateObject<SingleModelSpectrumChannel>();
                ch->AddPropagationLossModel(pl);
                ch->SetPropagationDelayModel(CreateObject<ConstantSpeedPropagationDelayModel>());
                ch->SetAttribute("MaxLossDb", DoubleValue(maxLossDb));
                chans[c] = ch;
            }
            return chans[c];
        };
        std::vector<Radio> radios;
        std::unordered_map<int, int> cellRadio;                      // node -> radio
        std::map<std::pair<int, Hex>, int> pairRadio;                 // (node, other cell) -> radio
        std::unordered_map<uint16_t, int> byAddr;
        std::vector<std::pair<int, int>> phyChan;                     // radio -> channel
        NodeContainer nc;
        std::unordered_map<int, Ptr<Node>> nsNode;
        for (int v : nodeIds) {
            Ptr<Node> n = CreateObject<Node>();
            Ptr<ConstantPositionMobilityModel> mob = CreateObject<ConstantPositionMobilityModel>();
            mob->SetPosition(Vector(nodes[v].x, nodes[v].y, 1.5));
            n->AggregateObject(mob);
            link->id[PeekPointer(mob)] = v;
            nsNode[v] = n;
            nc.Add(n);
        }
        std::vector<Medium> media;
        std::map<Hex, int> cellMedium;
        auto addRadio = [&](int v, int channel, int medium) {
            Radio r;
            r.node = v;
            r.medium = medium;
            r.addr = (uint16_t)(radios.size() + 1);
            r.dev = CreateObject<lrwpan::LrWpanNetDevice>();
            r.dev->SetChannel(chanOf(channel));
            nsNode[v]->AddDevice(r.dev);
            r.dev->SetAddress(Mac16Address(r.addr));
            r.dev->GetMac()->SetPanId(kPan);
            r.dev->GetMac()->SetRxOnWhenIdle(true);
            radios.push_back(r);
            byAddr[r.addr] = (int)radios.size() - 1;
            phyChan.push_back({(int)radios.size() - 1, channel});
            return (int)radios.size() - 1;
        };
        for (int v : nodeIds) {
            const Hex c = nodes[v].cell;
            if (!cellMedium.count(c)) {
                cellMedium[c] = (int)media.size();
                media.emplace_back();
            }
            cellRadio[v] = addRadio(v, cellChannel(c), cellMedium[c]);
        }
        for (auto& [k, ch] : pairChannel) {
            auto [a, b] = gw[k];
            media.emplace_back();
            pairRadio[{a, k.second}] = addRadio(a, ch, (int)media.size() - 1);
            pairRadio[{b, k.first}] = addRadio(b, ch, (int)media.size() - 1);
        }
        int64_t stream = 100000 * (int64_t)run;
        for (auto& r : radios) stream += r.dev->AssignStreams(stream);

        // ---- in-cell routes: least ETX on this run's links ---------------------------------
        // q = P(Rayleigh-faded RX power > sensitivity), from the mean (path loss, the pair's
        // shadowing); a node forwards toward its CL, or the gateway of the next cell, along
        // the least sum of 1/q. The gateway pairs themselves stay the PECEE ones.
        std::unordered_map<int, std::unordered_map<int, int>> nextTo;      // target -> node -> next hop
        std::unordered_map<int, std::unordered_map<int, double>> etxTo;    // target -> node -> ETX
        auto route = [&](int target) -> std::unordered_map<int, int>& {
            auto it = nextTo.find(target);
            if (it != nextTo.end()) return it->second;
            const auto& mem = members[nodes[target].cell];
            auto& dist = etxTo[target];
            auto& nx = nextTo[target];
            for (int v : mem) dist[v] = 1e18;
            dist[target] = 0;
            std::set<std::pair<double, int>> open{{0.0, target}};
            while (!open.empty()) {
                auto [du, u] = *open.begin();
                open.erase(open.begin());
                for (int v : mem) {
                    if (v == u) continue;
                    const double dv = du + 1.0 / linkQ(run, u, v);
                    if (dv < dist[v]) {
                        open.erase({dist[v], v});
                        dist[v] = dv;
                        nx[v] = u;
                        open.insert({dv, v});
                    }
                }
            }
            return nx;
        };
        uint32_t weakPairs = 0;
        for (auto& [k, ch] : pairChannel)
            weakPairs += linkQ(run, gw[k].first, gw[k].second) < 0.5;
        // all routes now, so that the shadowing draws do not interleave with the fading draws
        for (const Hex& h : used) route(clOf.at(h));
        for (auto& [k, ch] : pairChannel) {
            route(gw[k].first);
            route(gw[k].second);
        }
        FILE* fh = nullptr;   // per-hop trace of the first mission
        if (!trace.empty() && run == firstRun) {
            FILE* f = std::fopen((trace + "-routes.csv").c_str(), "w");
            CHECK(f);
            std::fprintf(f, "node,next,etx\n");
            for (const Hex& h : used) {
                const int cl = clOf.at(h);
                auto& nx = route(cl);
                for (int v : members[h])
                    std::fprintf(f, "%d,%d,%.3f\n", v, v == cl ? -1 : nx.at(v), etxTo[cl].at(v));
            }
            std::fclose(f);
            f = std::fopen((trace + "-pairs.csv").c_str(), "w");
            CHECK(f);
            std::fprintf(f, "a,b,channel,q\n");
            for (auto& [k, ch] : pairChannel)
                std::fprintf(f, "%d,%d,%d,%.4f\n", gw[k].first, gw[k].second, ch, linkQ(run, gw[k].first, gw[k].second));
            std::fclose(f);
            fh = std::fopen((trace + "-hops.csv").c_str(), "w");
            CHECK(fh);
            std::fprintf(fh, "t,phase,from,to\n");
        }

        // ---- protocol state ----------------------------------------------------------
        std::vector<Job> jobs;
        std::map<Hex, std::vector<uint8_t>> have;
        std::map<Hex, std::vector<double>> at;
        std::map<std::pair<Hex, uint32_t>, std::vector<std::function<void()>>> waiters;
        std::map<Hex, int> gatherLeft;
        std::map<Hex, std::vector<std::function<void()>>> onGathered;
        std::map<Hex, double> gatherDone;
        uint64_t phaseHops[kPhases] = {0}, macFail = 0, hops = 0;
        auto hold = [&](const Hex& c) -> std::vector<uint8_t>& {
            if (!have.count(c)) {
                have[c] = rx[clOf.at(c)];
                at[c].assign(N, -1.0);
                for (uint32_t s = 0; s < N; ++s)
                    if (have[c][s]) at[c][s] = 0;
            }
            return have[c];
        };
        auto now = [] { return Simulator::Now().GetSeconds() - kT0; };

        std::function<void(int, uint32_t, uint8_t)> forward;
        // The head frame of radio ri goes to the MAC (CSMA/CA, ACK, retries).
        auto transmit = [&](int ri) {
            Radio& r = radios[ri];
            auto [j, idx] = r.q.front();
            const int nx = r.qNext.front();
            const Radio& dst = nodes[nx].cell == nodes[r.node].cell ? radios[cellRadio.at(nx)]
                                                                     : radios[pairRadio.at({nx, nodes[r.node].cell})];
            const uint32_t bytes = jobs[j].s >= 0 ? kDataBytes : kCtrlBytes;
            std::vector<uint8_t> buf(bytes, 0);
            buf[0] = jobs[j].s >= 0 ? 1 : 2;
            std::memcpy(&buf[1], &j, 4);
            buf[5] = idx;
            lrwpan::McpsDataRequestParams p;
            p.m_srcAddrMode = lrwpan::SHORT_ADDR;
            p.m_dstAddrMode = lrwpan::SHORT_ADDR;
            p.m_dstPanId = kPan;
            p.m_dstAddr = Mac16Address(dst.addr);
            p.m_txOptions = lrwpan::TX_OPTION_ACK;
            r.dev->GetMac()->McpsDataRequest(p, Create<Packet>(buf.data(), bytes));
        };
        auto grant = [&](int m) {
            Medium& M = media[m];
            if (M.owner >= 0 || M.wait.empty()) return;
            M.owner = M.wait.front();
            M.wait.pop_front();
            radios[M.owner].waiting = false;
            transmit(M.owner);
        };
        auto request = [&](int ri) {
            Radio& r = radios[ri];
            if (r.q.empty() || r.waiting || media[r.medium].owner == ri) return;
            r.waiting = true;
            media[r.medium].wait.push_back(ri);
            grant(r.medium);
        };
        auto enqueue = [&](int from, int to, uint32_t j, uint8_t idx) {
            const int ri = nodes[to].cell == nodes[from].cell ? cellRadio.at(from)
                                                              : pairRadio.at({from, nodes[to].cell});
            radios[ri].q.push_back({j, idx});
            radios[ri].qNext.push_back(to);
            request(ri);
        };
        auto arrive = [&](const Hex& c, int32_t s, const std::function<void()>& done) {
            if (s >= 0) {
                auto& h = hold(c);
                if (!h[s]) {
                    h[s] = 1;
                    at[c][s] = now();
                    auto it = waiters.find({c, (uint32_t)s});
                    if (it != waiters.end()) {
                        auto fns = std::move(it->second);
                        waiters.erase(it);
                        for (auto& f : fns) f();
                    }
                }
            }
            if (done) done();
        };
        // Node v holds frame j, which has entered path cell number idx: pass it one hop on.
        forward = [&](int v, uint32_t j, uint8_t idx) {
            Job& J = jobs[j];
            const Hex c = nodes[v].cell;
            int next;
            uint8_t nidx = idx;
            const bool last = J.path < 0 || idx + 1u >= paths[J.path].size();
            if (last) {
                if (v == clOf.at(c)) {
                    arrive(c, J.s, J.done);
                    return;
                }
                next = route(clOf.at(c)).at(v);
            } else {
                CHECK(paths[J.path][idx] == c);
                const Hex nc2 = paths[J.path][idx + 1];
                const auto [ga, gb] = gw.at({c, nc2});
                next = v == ga ? gb : route(ga).at(v);
                if (nodes[next].cell == nc2) nidx = idx + 1;
            }
            CHECK(next >= 0);
            enqueue(v, next, j, nidx);
        };
        for (size_t ri = 0; ri < radios.size(); ++ri) {
            Ptr<lrwpan::LrWpanMac> mac = radios[ri].dev->GetMac();
            mac->SetMcpsDataConfirmCallback([&, ri](lrwpan::McpsDataConfirmParams p) {
                Radio& r = radios[ri];
                media[r.medium].owner = -1;
                if (p.m_status == lrwpan::MacStatus::SUCCESS) {
                    const uint32_t j = r.q.front().first;
                    phaseHops[jobs[j].phase]++;
                    hops++;
                    if (fh)
                        std::fprintf(fh, "%.4f,%s,%d,%d\n", now(), kPhaseName[jobs[j].phase], r.node, r.qNext.front());
                    r.q.pop_front();
                    r.qNext.pop_front();
                } else {
                    macFail++;   // the MAC gave up: keep the frame for the radio's next turn
                }
                request((int)ri);
                grant(r.medium);
            });
            mac->SetMcpsDataIndicationCallback([&, ri](lrwpan::McpsDataIndicationParams, Ptr<Packet> pkt) {
                Radio& r = radios[ri];
                uint8_t buf[8];
                pkt->CopyData(buf, 8);
                uint32_t j;
                std::memcpy(&j, &buf[1], 4);
                const uint8_t idx = buf[5];
                if (!r.seen.insert(((uint64_t)j << 8) | idx).second) return;   // a duplicate (lost ACK)
                forward(r.node, j, idx);
            });
        }
        auto newJob = [&](int path, int32_t s, int phase, std::function<void()> done) {
            jobs.push_back({path, s, phase, std::move(done), Hex{}});
            return (uint32_t)jobs.size() - 1;
        };
        // Send from cell path[0]'s CL along path (data s, or a request when s < 0).
        auto send = [&](int path, int32_t s, int phase, std::function<void()> done = nullptr) {
            const Hex src = paths[path].front();
            if (paths[path].size() == 1) {
                arrive(src, s, done);
                return;
            }
            forward(clOf.at(src), newJob(path, s, phase, std::move(done)), 0);
        };
        auto when = [&](const Hex& c, uint32_t s, std::function<void()> fn) {
            if (hold(c)[s]) fn();
            else waiters[{c, s}].push_back(std::move(fn));
        };
        auto gathered = [&](const Hex& c) {
            gatherDone[c] = now();
            auto fns = std::move(onGathered[c]);
            onGathered.erase(c);
            for (auto& f : fns) f();
        };
        auto afterGather = [&](const Hex& c, std::function<void()> fn) {
            if (gatherLeft.count(c) && gatherLeft[c] == 0) fn();
            else onGathered[c].push_back(std::move(fn));
        };
        // Convention 1: bring what cell c needs from its own nodes to its CL.
        auto gather = [&](const Hex& c, const std::vector<uint8_t>& need) {
            auto& h = hold(c);
            const int cl = clOf.at(c);
            route(cl);
            const auto& etx = etxTo[cl];
            int n = 0;
            for (uint32_t s = 0; s < N; ++s) {
                if (!need[s] || h[s]) continue;
                int best = -1;
                for (int v : members[c])
                    if (v != cl && rx[v][s] && (best < 0 || etx.at(v) < etx.at(best))) best = v;
                if (best < 0) continue;
                n++;
                forward(best, newJob(-1, (int32_t)s, kGather, [&, c] {
                            if (--gatherLeft[c] == 0) gathered(c);
                        }), 0);
            }
            gatherLeft[c] = n;
            if (n == 0) gathered(c);
        };
        auto segMask = [&](const Hex& a) {
            std::vector<uint8_t> m(N, 0);
            for (uint32_t s = seg[a].first; s <= seg[a].second; ++s) m[s] = inD[s];
            return m;
        };
        auto rev = [](std::vector<Hex> p) {
            std::reverse(p.begin(), p.end());
            return p;
        };

        // ---- the scheme ---------------------------------------------------------------
        std::map<Hex, std::vector<uint8_t>> need;
        auto needOr = [&](const Hex& c, const std::vector<uint8_t>& m) {
            auto& x = need[c];
            if (x.empty()) x.assign(N, 0);
            for (uint32_t s = 0; s < N; ++s) x[s] |= m[s];
        };
        for (const Hex& k : plan.crit) needOr(k, inD);
        std::map<Hex, uint32_t> lackCL, lackCell;
        for (const Hex& k : plan.crit) {
            uint32_t a = 0, b = 0;
            for (uint32_t s = 0; s < N; ++s) {
                if (!inD[s]) continue;
                a += !rx[clOf.at(k)][s];
                bool any = false;
                for (int v : members[k]) any |= rx[v][s];
                b += !any;
            }
            lackCL[k] = a;
            lackCell[k] = b;
        }
        if (scheme == "river") {
            for (auto& x : plan.axe) needOr(x.a, segMask(x.a));
            // Algorithm 5: a Bank tells its Axe cell what it has of Seg(a); the Axe sends the rest.
            for (auto& bk : plan.banks) {
                if (bk.b == bk.a) continue;
                needOr(bk.b, segMask(bk.a));
                const int fwd = addPath(bk.path), back = addPath(rev(bk.path));
                const Hex a = bk.a, b = bk.b;
                afterGather(b, [&, a, b, fwd, back] {
                    auto m = segMask(a);
                    std::vector<uint32_t> lack;
                    for (uint32_t s = 0; s < N; ++s)
                        if (m[s] && !hold(b)[s]) lack.push_back(s);
                    send(back, -1, kControl, [&, a, fwd, lack] {
                        for (uint32_t s : lack) when(a, s, [&, s, fwd] { send(fwd, (int32_t)s, kBankFill); });
                    });
                });
            }
            // Circle members, and Algorithm 7 at each critical cell.
            std::map<std::pair<Hex, Hex>, std::vector<const uavcoop2::PlanCirc*>> tasks;   // (k, m)
            for (auto& t : plan.circ) tasks[{t.k, t.m}].push_back(&t);
            for (auto& [km, ts] : tasks) {
                const Hex k = km.first, m = km.second;
                std::vector<uint8_t> group(N, 0);
                for (auto* t : ts) {
                    auto sm = segMask(t->a);
                    for (uint32_t s = 0; s < N; ++s) group[s] |= sm[s];
                }
                std::vector<std::pair<int, int>> src;   // per task: (b -> m path, m -> b path)
                for (auto* t : ts) src.push_back({addPath(t->path), addPath(rev(t->path))});
                const int toK = addPath({m, k}), toM = addPath({k, m});
                // Fetch the part X of task i (Seg of t->a) from its Bank, then keep it at m.
                auto fetch = [&, ts, src, m](size_t i, std::vector<uint32_t> X) {
                    const Hex b = ts[i]->b;
                    const int fwd = src[i].first, back = src[i].second;
                    send(back, -1, kControl, [&, b, fwd, X] {
                        for (uint32_t s : X) when(b, s, [&, s, fwd] { send(fwd, (int32_t)s, kCircleFill); });
                    });
                };
                if (prep == "full") {
                    // Algorithm 6, ahead: m fetches its whole share once it has gathered its own.
                    needOr(m, group);
                    afterGather(m, [&, ts, m, fetch] {
                        for (size_t i = 0; i < ts.size(); ++i) {
                            auto sm = segMask(ts[i]->a);
                            std::vector<uint32_t> X;
                            for (uint32_t s = 0; s < N; ++s)
                                if (sm[s] && !hold(m)[s]) X.push_back(s);
                            fetch(i, X);
                        }
                    });
                }
                // Algorithm 7: k asks m for what it lacks of m's group, once k has gathered.
                afterGather(k, [&, k, m, ts, group, toK, toM, fetch] {
                    std::vector<uint32_t> part;
                    for (uint32_t s = 0; s < N; ++s)
                        if (group[s] && !hold(k)[s]) part.push_back(s);
                    send(toM, -1, kControl, [&, k, m, ts, part, toK, fetch] {
                        for (uint32_t s : part) when(m, s, [&, s, toK] { send(toK, (int32_t)s, kPull); });
                        if (prep != "ondemand") return;
                        // on demand: m gets each asked packet from its own nodes, else from the Bank
                        std::vector<std::vector<uint32_t>> X(ts.size());
                        std::vector<uint8_t> fromCell(N, 0);
                        for (uint32_t s : part) {
                            if (hold(m)[s]) continue;
                            bool inCell = false;
                            for (int v : members[m]) inCell |= rx[v][s] != 0;
                            if (inCell) fromCell[s] = 1;
                            else
                                for (size_t i = 0; i < ts.size(); ++i)
                                    if (s >= seg[ts[i]->a].first && s <= seg[ts[i]->a].second) X[i].push_back(s);
                        }
                        gather(m, fromCell);
                        for (size_t i = 0; i < ts.size(); ++i)
                            if (!X[i].empty()) fetch(i, X[i]);
                    });
                });
            }
        } else {
            for (auto& x : plan.axe) needOr(x.a, segMask(x.a));
            for (auto& d : plan.direct) {
                const int toA = addPath(d.path), toK = addPath(rev(d.path));
                const Hex k = d.k, a = d.a;
                afterGather(k, [&, k, a, toA, toK] {
                    auto sm = segMask(a);
                    std::vector<uint32_t> part;
                    for (uint32_t s = 0; s < N; ++s)
                        if (sm[s] && !hold(k)[s]) part.push_back(s);
                    send(toA, -1, kControl, [&, a, part, toK] {
                        for (uint32_t s : part) when(a, s, [&, s, toK] { send(toK, (int32_t)s, kPull); });
                    });
                });
            }
        }
        // Completion of the critical cells.
        std::map<Hex, double> doneAt;
        std::map<Hex, uint32_t> left;
        auto finish = [&](const Hex& k) {
            doneAt[k] = now();
            if (doneAt.size() == plan.crit.size()) Simulator::Stop();
        };
        for (const Hex& k : plan.crit) {
            for (uint32_t s = 0; s < N; ++s)
                if (inD[s] && !hold(k)[s]) {
                    left[k]++;
                    when(k, s, [&, k] {
                        if (--left[k] == 0) finish(k);
                    });
                }
        }
        std::function<void()> progress = [&] {
            std::fprintf(stderr, "  run %u t=%.0f s: %llu hops, %llu MAC give-ups, %zu/%zu critical done\n", run,
                         now(), (unsigned long long)hops, (unsigned long long)macFail, doneAt.size(),
                         plan.crit.size());
            Simulator::Schedule(Seconds(10), progress);
        };

        // ---- run ----------------------------------------------------------------------
        Simulator::Schedule(Seconds(kT0 / 2), [&] {
            lrwpan::LrWpanSpectrumValueHelper svh;
            for (auto [ri, ch] : phyChan) {
                Ptr<lrwpan::LrWpanPhy> phy = radios[ri].dev->GetPhy();
                phy->SetRxSensitivity(params::kRxSensDbm);
                Ptr<lrwpan::PhyPibAttributes> pib = Create<lrwpan::PhyPibAttributes>();
                pib->phyCurrentChannel = (uint8_t)ch;
                phy->PlmeSetAttributeRequest(lrwpan::PhyPibAttributeIdentifier::phyCurrentChannel, pib);
                phy->SetTxPowerSpectralDensity(svh.CreateTxPowerSpectralDensity(params::kTxPowerDbm, ch));
                // a channel change leaves the transceiver off (lr-wpan-phy.cc): listen again
                phy->PlmeSetTRXStateRequest(lrwpan::IEEE_802_15_4_PHY_RX_ON);
            }
        });
        Simulator::Schedule(Seconds(kT0), [&] {
            for (auto& [c, m] : need) gather(c, m);
            for (const Hex& k : plan.crit)
                if (!left[k]) finish(k);
            progress();
        });
        Simulator::Stop(Seconds(kT0 + limitS));
        Simulator::Run();
        const double simS = now();
        const double wallS =
            std::chrono::duration<double>(std::chrono::steady_clock::now() - wall0).count();
        const std::string sch = scheme == "river" ? "river-" + prep : scheme;
        for (const Hex& k : plan.crit) {
            uint32_t miss = 0;
            for (uint32_t s = 0; s < N; ++s) miss += inD[s] && !hold(k)[s];
            std::fprintf(fc, "%u,%s,%d,%d,%u,%u,%u,%.2f,%.2f,%u\n", run, sch.c_str(), k.q, k.r, Dn, lackCL[k],
                         lackCell[k], gatherDone.count(k) ? gatherDone[k] : -1.0, doneAt.count(k) ? doneAt[k] : -1.0,
                         miss);
        }
        std::fprintf(fr, "%u,%s,%u,%.2f,%.1f,%llu", run, sch.c_str(), Dn, simS, wallS, (unsigned long long)hops);
        for (int p = 0; p < kPhases; ++p) std::fprintf(fr, ",%llu", (unsigned long long)phaseHops[p]);
        std::fprintf(fr, ",%llu\n", (unsigned long long)macFail);
        std::fflush(fc);
        std::fflush(fr);
        std::printf("run %u %s: D %u, %zu/%zu critical done, sim %.1f s, wall %.0f s, %llu hops, %llu MAC give-ups, "
                    "%u/%zu gateway pairs with q < 0.5\n",
                    run, sch.c_str(), Dn, doneAt.size(), plan.crit.size(), simS, wallS, (unsigned long long)hops,
                    (unsigned long long)macFail, weakPairs, pairChannel.size());
        std::fflush(stdout);
        if (fh) {
            std::fclose(fh);
            FILE* f = std::fopen((trace + "-held.csv").c_str(), "w");   // when each packet of D reached each CL
            CHECK(f);
            std::fprintf(f, "q,r,s,t\n");
            for (auto& [c, ts] : at)
                for (uint32_t s = 0; s < N; ++s)
                    if (inD[s] && ts[s] >= 0) std::fprintf(f, "%d,%d,%u,%.4f\n", c.q, c.r, s, ts[s]);
            std::fclose(f);
        }
        Simulator::Destroy();
    }
    std::fclose(fc);
    std::fclose(fr);
    return 0;
}
