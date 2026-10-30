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
//   river --prep=adaptive  Circle sized at run time (CLAUDE.md §8 items 66-67): the critical cell's
//                          nodes send their CL a summary; the CL counts what no node of the cell
//                          has, takes n = ceil(lack / share) members (--circleMin..--circleMax, rings
//                          1-2) and asks each for its group's part; members serve as on demand
//   direct                 each critical cell asks every Axe cell for what it lacks of Seg(a); --directSeg=false:
//                          without the BS's Seg table, it asks every Axe cell for all it lacks (copies overlap)
// --noSchedule: no PECEE grid schedule, every radio sends when it has frames (CSMA/CA only).
//   trickle                baseline without a plan (CLAUDE.md §8 items 134, 139): Deluge-style dissemination over
//                          the same cells, radios and gateway pairs. The object is every packet some critical cell
//                          needs, in pages of --page packets; every cell gathers what its nodes hold of it, then
//                          its CL runs a Trickle timer (RFC 6206: --tImin, --tImax, redundancy --tK): at a random
//                          time in the second half of each interval, unless it heard tK consistent adverts, it
//                          sends each adjacent cell an advert of its complete pages. A cell that hears of a page it
//                          lacks asks that neighbour for its missing packets of the lowest such page (one request
//                          at a time, again after a timeout); a cell that hears a neighbour lack one of its pages,
//                          or completes a page, resets its timer to tImin.
//                          --tScope=plan: over River's plan cells; paths: only over the Axe cells, the critical
//                          cells and the cells of the direct-pull paths between them (the reviewer's scope); all:
//                          every cell of the cluster (Deluge-lite: it cannot know which cells matter).
//                          --pageBreaks=FILE: packet indices where an image starts; a page then spans neither an
//                          image nor two Axe cells' Segs, and with --repair the Axe cells complete their Seg as in
//                          River, so every page is complete in some cell (Deluge's advert needs a complete page).
// Repair (--repair=S > 0, river --prep=full; CLAUDE.md §8 item 169): two gaps closed.
//   Axe     an Axe cell's gather also takes the packets of its own Seg that none of its nodes heard from an
//           adjacent cell that holds them (a request, then the packets over that cell pair's gateways)
//   direct  (--scheme=direct) the same Axe gather, and a stalled critical cell asks its Axe cells again
//   stalls  a critical cell that still lacks packets and has taken in none for S seconds asks its Circle
//           members again for the rest of their groups; a member that lacks one asks its Bank again, and a
//           Bank that lacks one its Axe cell (an 802.15.4 ACK carries only a sequence number, so a frame can
//           be taken as delivered on another exchange's ACK and lost)
// Writes OUT-crit.csv (per run and critical cell), OUT-runs.csv (per run) and OUT-energy.csv (per run and node: the
// time its radios spent transmitting, receiving, listening and off, from the PHY state trace, the frames they
// began to send and received, and when the last one began to send: after it a node with a planned role is idle).

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
#include <cmath>
#include <cstring>
#include <cstdio>
#include <deque>
#include <fstream>
#include <functional>
#include <map>
#include <random>
#include <set>
#include <sstream>
#include <tuple>
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

enum Phase { kGather, kBankFill, kCircleFill, kPull, kControl, kAdvert, kPhases };
const char* kPhaseName[kPhases] = {"gather", "bankfill", "circlefill", "pull", "control", "advert"};

}  // namespace

int main(int argc, char* argv[]) {
    std::string nodesCsv, routesCsv, gwCsv, planFile, bits, out = "river-ns3", scheme = "river",
                                                           prep = "full", trace, tScope = "plan", pageBreaks;
    uint32_t firstRun = 1, runs = 1;
    double limitS = 1800, maxLossDb = 130, share = 400, repairS = 0;
    uint32_t circleMin = 2, circleMax = 12, page = 64, tK = 1;
    double tImin = 1, tImax = 64;
    int colours = 7;
    bool noSchedule = false, directSeg = true;
    std::string gwSelect = "deploy";
    CommandLine cmd;
    cmd.AddValue("nodes", "deploy-nodes-sS.csv", nodesCsv);
    cmd.AddValue("routes", "deploy-routes-sS.csv", routesCsv);
    cmd.AddValue("gateways", "deploy-gateways-sS.csv", gwCsv);
    cmd.AddValue("plan", "river-plan.txt (tools/river_export.py)", planFile);
    cmd.AddValue("bits", "prefix of the pass bitmaps: PREFIX-rR.bin", bits);
    cmd.AddValue("firstRun", "first mission", firstRun);
    cmd.AddValue("runs", "missions", runs);
    cmd.AddValue("scheme", "river | direct | trickle", scheme);
    cmd.AddValue("page", "trickle: packets per page", page);
    cmd.AddValue("tImin", "trickle: shortest interval, s", tImin);
    cmd.AddValue("tImax", "trickle: longest interval, s", tImax);
    cmd.AddValue("tK", "trickle: redundancy constant", tK);
    cmd.AddValue("tScope", "trickle: plan (River's cells) | paths (Axe, critical and direct-pull path cells) | all",
                 tScope);
    cmd.AddValue("pageBreaks", "trickle: file of packet indices where an image starts (no page spans one)",
                 pageBreaks);
    cmd.AddValue("prep", "river only: full | ondemand | adaptive", prep);
    cmd.AddValue("share", "adaptive: packets of the lack per Circle member", share);
    cmd.AddValue("circleMin", "adaptive: fewest Circle members", circleMin);
    cmd.AddValue("circleMax", "adaptive: most Circle members", circleMax);
    cmd.AddValue("limit", "stop a mission after this many seconds", limitS);
    cmd.AddValue("repair", "river --prep=full: Axe cells complete their Seg from adjacent cells, and a critical cell "
                 "idle this many seconds asks again (0: off)", repairS);
    cmd.AddValue("maxLoss", "SpectrumChannel MaxLossDb", maxLossDb);
    cmd.AddValue("colours", "cell channels: 3, 4, 7 or 13 colours", colours);
    cmd.AddValue("gwSelect", "gateway pair of each cell pair: deploy (uav-coop, by geometry) | quality "
                 "(the BS picks the best link of the mission)", gwSelect);
    cmd.AddValue("noSchedule", "no PECEE schedule: every radio contends by CSMA/CA alone", noSchedule);
    cmd.AddValue("directSeg", "direct: ask each Axe cell only for its Seg (false: for everything lacking)", directSeg);
    cmd.AddValue("out", "output prefix", out);
    cmd.AddValue("trace", "prefix: the first mission's hops, CL arrivals, in-cell routes and gateway pairs",
                 trace);
    cmd.Parse(argc, argv);
    CHECK(scheme == "river" || scheme == "direct" || scheme == "trickle");
    CHECK(page > 0 && tK > 0 && 0 < tImin && tImin <= tImax);
    CHECK(tScope == "plan" || tScope == "paths" || tScope == "all");
    std::set<uint32_t> breaks;
    if (!pageBreaks.empty()) {
        std::ifstream in(pageBreaks);
        CHECK(in);
        for (uint32_t b; in >> b;) breaks.insert(b);
    }
    CHECK(prep == "full" || prep == "ondemand" || prep == "adaptive");
    CHECK(share > 0 && 1 <= circleMin && circleMin <= circleMax);
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
    const bool lean = scheme == "trickle" && tScope == "paths";
    if (!lean) {
        for (auto& x : plan.banks) used.insert(x.path.begin(), x.path.end());
        for (auto& x : plan.circ) {
            used.insert(x.path.begin(), x.path.end());
            used.insert(x.k);
        }
        for (auto& x : plan.csrc) used.insert(x.path.begin(), x.path.end());
        for (auto& x : plan.clink) used.insert(x.path.begin(), x.path.end());
    }
    if (scheme == "trickle" && tScope == "all")
        for (auto& [h, v] : clOf) used.insert(h);
    if (scheme == "direct" || lean)
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
    for (auto& x : plan.csrc) checkPath(x.path);
    for (auto& x : plan.clink) checkPath(x.path);
    if (prep == "adaptive") CHECK(!plan.cset.empty());

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
    FILE* fe = std::fopen((out + "-energy.csv").c_str(), "w");
    CHECK(fc && fr && fe);
    std::fprintf(fc, "run,scheme,q,r,D,lackCL,lackCell,gatherDoneS,doneS,missing,circle\n");
    std::fprintf(fr, "run,scheme,D,simS,wallS,hops,gather,bankfill,circlefill,pull,control,advert,macFail\n");
    std::fprintf(fe, "run,scheme,node,q,r,cl,radios,txS,rxS,listenS,offS,framesTx,framesRx,lastTxS\n");

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
            if (noSchedule) {   // a medium of its own: nothing to wait for but CSMA/CA
                medium = (int)media.size();
                media.emplace_back();
            }
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
        std::function<void(const Hex&, uint32_t)> onNew;   // trickle: a cell's CL takes in a new packet
        // done by value: the waiters it wakes may add jobs and move the vector that held it
        auto arrive = [&](const Hex& c, int32_t s, std::function<void()> done) {
            if (s >= 0) {
                auto& h = hold(c);
                if (!h[s]) {
                    h[s] = 1;
                    at[c][s] = now();
                    if (onNew) onNew(c, (uint32_t)s);
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
                    arrive(c, J.s, std::function<void()>(J.done));
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
        // Convention 1: bring what cell c needs from its own nodes to its CL. With --repair, an Axe cell also
        // asks an adjacent cell for the packets of its Seg that none of its own nodes heard.
        auto gather = [&](const Hex& c, const std::vector<uint8_t>& need) {
            auto& h = hold(c);
            const int cl = clOf.at(c);
            route(cl);
            const auto& etx = etxTo[cl];
            int n = 0;
            std::map<Hex, std::vector<std::pair<uint32_t, int>>> nbr;   // adjacent cell -> (packet, its holder)
            for (uint32_t s = 0; s < N; ++s) {
                if (!need[s] || h[s]) continue;
                int best = -1;
                for (int v : members[c])
                    if (v != cl && rx[v][s] && (best < 0 || etx.at(v) < etx.at(best))) best = v;
                if (best < 0) {
                    if (repairS > 0 && seg.count(c) && s >= seg[c].first && s <= seg[c].second)
                        for (auto [dq, dr] : {std::pair{1, 0}, {-1, 0}, {0, 1}, {0, -1}, {1, -1}, {-1, 1}}) {
                            const Hex c2{c.q + dq, c.r + dr};
                            if (!used.count(c2) || !gw.count({c, c2})) continue;
                            const auto it = std::find_if(members[c2].begin(), members[c2].end(),
                                                         [&](int v) { return rx[v][s] != 0; });
                            if (it == members[c2].end()) continue;
                            nbr[c2].push_back({s, *it});
                            n++;
                            break;
                        }
                    continue;
                }
                n++;
                forward(best, newJob(-1, (int32_t)s, kGather, [&, c] {
                            if (--gatherLeft[c] == 0) gathered(c);
                        }), 0);
            }
            for (auto& [c2, xs] : nbr) {
                const int data = addPath({c2, c});
                send(addPath({c, c2}), -1, kControl, [&, c, data, xs = xs] {
                    for (auto [s, v] : xs)
                        forward(v, newJob(data, (int32_t)s, kGather, [&, c] {
                                    if (--gatherLeft[c] == 0) gathered(c);
                                }), 0);
                });
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
        // what each critical cell needs: all of D, or with NEED records only its own window (item 120)
        std::map<Hex, std::vector<uint8_t>> needK;
        for (const Hex& k : plan.crit) needK[k] = inD;
        for (auto& x : plan.need)
            for (uint32_t s = 0; s < N; ++s) needK.at(x.k)[s] = inD[s] && s >= x.first && s <= x.last;
        for (const Hex& k : plan.crit) needOr(k, needK[k]);
        std::map<Hex, uint32_t> lackCL, lackCell, circleN;
        std::map<Hex, int> summaryLeft;
        std::vector<std::function<void()>> atStart;
        for (const Hex& k : plan.crit) {
            uint32_t a = 0, b = 0;
            for (uint32_t s = 0; s < N; ++s) {
                if (!needK[k][s]) continue;
                a += !rx[clOf.at(k)][s];
                bool any = false;
                for (int v : members[k]) any |= rx[v][s];
                b += !any;
            }
            lackCL[k] = a;
            lackCell[k] = b;
        }
        // --repair state lives for the whole run (callbacks refer to it)
        std::map<Hex, std::vector<std::function<void()>>> redo;   // a critical cell's requests again
        std::map<std::pair<Hex, Hex>, std::pair<int, int>> bankPath;   // (a, b) -> (a -> b, b -> a)
        if (scheme == "river") {
            for (auto& x : plan.axe) needOr(x.a, segMask(x.a));
            // --repair: Bank b asks its Axe cell a again for packet s
            auto refill = [&](const Hex& a, const Hex& b, uint32_t s) {
                const auto it = bankPath.find({a, b});
                if (it == bankPath.end()) return;
                const auto [fwd, back] = it->second;
                send(back, -1, kControl, [&, a, s, fwd = fwd] {
                    when(a, s, [&, s, fwd] { send(fwd, (int32_t)s, kBankFill); });
                });
            };
            // Algorithm 5: a Bank tells its Axe cell what it has of Seg(a); the Axe sends the rest.
            for (auto& bk : plan.banks) {
                if (bk.b == bk.a) continue;
                needOr(bk.b, segMask(bk.a));
                const int fwd = addPath(bk.path), back = addPath(rev(bk.path));
                bankPath[{bk.a, bk.b}] = {fwd, back};
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
            if (prep != "adaptive")
                for (auto& t : plan.circ) tasks[{t.k, t.m}].push_back(&t);
            for (auto& [km, ts] : tasks) {
                const Hex k = km.first, m = km.second;
                std::vector<uint8_t> group(N, 0);
                for (auto* t : ts) {
                    auto sm = segMask(t->a);
                    for (uint32_t s = 0; s < N; ++s) group[s] |= sm[s] && needK[k][s];
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
                    afterGather(m, [&, ts, m, group, fetch] {
                        for (size_t i = 0; i < ts.size(); ++i) {
                            auto sm = segMask(ts[i]->a);
                            std::vector<uint32_t> X;
                            for (uint32_t s = 0; s < N; ++s)
                                if (sm[s] && group[s] && !hold(m)[s]) X.push_back(s);
                            fetch(i, X);
                        }
                    });
                }
                // --repair: k asks m again for what it still lacks of m's group; m passes on what it holds and
                // asks the Banks again for the rest
                if (repairS > 0 && prep == "full")
                    redo[k].push_back([&, k, m, ts, src, group, toK, toM, refill] {
                        std::vector<uint32_t> part;
                        for (uint32_t s = 0; s < N; ++s)
                            if (group[s] && !hold(k)[s]) part.push_back(s);
                        if (part.empty()) return;
                        send(toM, -1, kControl, [&, m, ts, src, part, toK, refill] {
                            std::vector<std::vector<uint32_t>> X(ts.size());
                            for (uint32_t s : part) {
                                if (hold(m)[s]) {
                                    send(toK, (int32_t)s, kPull);
                                    continue;
                                }
                                for (size_t i = 0; i < ts.size(); ++i)
                                    if (s >= seg[ts[i]->a].first && s <= seg[ts[i]->a].second) X[i].push_back(s);
                                when(m, s, [&, s, toK] { send(toK, (int32_t)s, kPull); });
                            }
                            for (size_t i = 0; i < ts.size(); ++i) {
                                if (X[i].empty()) continue;
                                const Hex a = ts[i]->a, b = ts[i]->b;
                                const int fwd = src[i].first;
                                send(src[i].second, -1, kControl, [&, a, b, fwd, xs = X[i], refill] {
                                    for (uint32_t s : xs) {
                                        if (b != a && !hold(b)[s]) refill(a, b, s);
                                        when(b, s, [&, s, fwd] { send(fwd, (int32_t)s, kCircleFill); });
                                    }
                                });
                            }
                        });
                    });
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
            for (auto& [km, ts] : tasks) circleN[km.first]++;
            if (prep == "adaptive") {
                std::map<Hex, std::map<uint32_t, std::vector<const uavcoop2::PlanCset*>>> sets;   // k -> n
                for (auto& x : plan.cset) sets[x.k][x.n].push_back(&x);
                std::map<std::pair<Hex, Hex>, int> toM, toK;
                for (auto& x : plan.clink) {
                    toM[{x.k, x.m}] = addPath(x.path);
                    toK[{x.k, x.m}] = addPath(rev(x.path));
                }
                std::map<std::tuple<Hex, Hex, Hex>, std::tuple<Hex, int, int>> src;   // (k, m, a) -> (b, b->m, m->b)
                for (auto& x : plan.csrc) src[{x.k, x.m, x.a}] = {x.b, addPath(x.path), addPath(rev(x.path))};
                // Member m of k: k asks for part; m passes on what it holds, gets the rest from its own
                // nodes, else from the Bank of the packet's Axe cell.
                auto serve = [&, toK, src](const Hex& k, const Hex& m, std::vector<uint32_t> part) {
                    const int back = toK.at({k, m});
                    for (uint32_t s : part) when(m, s, [&, s, back] { send(back, (int32_t)s, kPull); });
                    std::vector<uint8_t> fromCell(N, 0);
                    std::map<Hex, std::vector<uint32_t>> X;   // Axe cell -> from its Bank
                    for (uint32_t s : part) {
                        if (hold(m)[s]) continue;
                        bool inCell = false;
                        for (int v : members[m]) inCell |= rx[v][s] != 0;
                        if (inCell) {
                            fromCell[s] = 1;
                            continue;
                        }
                        for (auto& x : plan.axe)
                            if (s >= x.first && s <= x.last) X[x.a].push_back(s);
                    }
                    gather(m, fromCell);
                    for (auto& [a, xs] : X) {
                        const auto [b, fwd, bk] = src.at({k, m, a});
                        send(bk, -1, kControl, [&, b = b, fwd = fwd, xs = xs] {
                            for (uint32_t s : xs) when(b, s, [&, s, fwd] { send(fwd, (int32_t)s, kCircleFill); });
                        });
                    }
                };
                // k's CL, once its nodes' summaries are in: size the Circle from the lack, ask the members.
                auto decide = [&, sets, serve, toM](const Hex& k) {
                    std::vector<uint8_t> lk(N, 0);
                    uint32_t lack = 0;
                    for (uint32_t s = 0; s < N; ++s) {
                        if (!needK[k][s]) continue;
                        bool any = false;
                        for (int v : members[k]) any |= rx[v][s] != 0;
                        lk[s] = !any;
                        lack += !any;
                    }
                    if (lack == 0) return;
                    const auto& byN = sets.at(k);
                    uint32_t n = std::clamp((uint32_t)std::ceil(lack / share), circleMin, circleMax);
                    n = std::min(n, byN.rbegin()->first);
                    circleN[k] = byN.at(n).size();
                    for (auto* x : byN.at(n)) {
                        std::vector<uint32_t> part;
                        for (uint32_t i = x->first; i <= x->last; ++i)
                            for (uint32_t s = plan.axe[i].first; s <= plan.axe[i].last; ++s)
                                if (lk[s]) part.push_back(s);
                        const Hex m = x->m;
                        send(toM.at({k, m}), -1, kControl, [&, k, m, part, serve] { serve(k, m, part); });
                    }
                };
                for (const Hex& k : plan.crit) {
                    atStart.push_back([&, k, decide] {
                        const int cl = clOf.at(k);
                        summaryLeft[k] = (int)members[k].size() - 1;
                        if (summaryLeft[k] == 0) decide(k);
                        for (int v : members[k])
                            if (v != cl)
                                forward(v, newJob(-1, -1, kControl, [&, k, decide] {
                                            if (--summaryLeft[k] == 0) decide(k);
                                        }), 0);
                    });
                }
            }
        } else if (scheme == "direct") {
            for (auto& x : plan.axe) needOr(x.a, directSeg ? segMask(x.a) : inD);   // no Seg table: all it heard
            for (auto& d : plan.direct) {
                const int toA = addPath(d.path), toK = addPath(rev(d.path));
                const Hex k = d.k, a = d.a;
                auto ask = [&, k, a, toA, toK](bool again) {
                    auto sm = directSeg ? segMask(a) : std::vector<uint8_t>(N, 1);
                    std::vector<uint32_t> part;
                    for (uint32_t s = 0; s < N; ++s)
                        if (sm[s] && needK[k][s] && !hold(k)[s]) part.push_back(s);
                    if (again && part.empty()) return;
                    send(toA, -1, kControl, [&, a, part, toK] {
                        for (uint32_t s : part) when(a, s, [&, s, toK] { send(toK, (int32_t)s, kPull); });
                    });
                };
                afterGather(k, [ask] { ask(false); });
                if (repairS > 0) redo[k].push_back([ask] { ask(true); });   // --repair: ask again, as River
            }
        }
        // Trickle state lives for the whole run (callbacks refer to it).
        std::vector<uint8_t> obj(N, 0);
        std::vector<uint32_t> pageOf(N, 0), pageSize;
        std::vector<std::vector<uint32_t>> pagePk;             // page -> its packets
        std::map<Hex, std::vector<std::pair<Hex, int>>> nbr;   // cell -> (adjacent cell, path cell -> it)
        std::map<Hex, std::vector<uint32_t>> inPage;           // cell -> packets held per page
        std::map<Hex, std::vector<uint8_t>> full;              // cell -> complete pages
        std::map<Hex, std::map<uint32_t, Hex>> avail;          // cell -> page -> a neighbour that has it
        std::map<Hex, int64_t> asked;                          // cell -> page asked for, -1 none
        std::map<Hex, uint32_t> askId;
        struct Tk {
            double I = 0;
            uint32_t c = 0;
            EventId fire, end;
        };
        std::map<Hex, Tk> tk;
        std::mt19937_64 trng(0x7c1c4e + run);
        std::function<void(const Hex&)> interval, askNext;
        if (scheme == "trickle") {
            for (const Hex& k : plan.crit)
                for (uint32_t s = 0; s < N; ++s) obj[s] |= needK[k][s];
            if (!breaks.empty())
                for (auto& [a, fl] : seg) breaks.insert(fl.first);
            uint32_t n = 0;
            int64_t prev = -1;
            for (uint32_t s = 0; s < N; ++s)
                if (obj[s]) {
                    auto b = breaks.upper_bound((uint32_t)prev);   // an image starts in (prev, s]
                    if (pageSize.empty() || pageSize.back() == page || (b != breaks.end() && *b <= s)) {
                        pageSize.push_back(0);
                        pagePk.emplace_back();
                    }
                    pageOf[s] = (uint32_t)pageSize.size() - 1;
                    pageSize.back()++;
                    pagePk.back().push_back(s);
                    n++;
                    prev = s;
                }
            const uint32_t P = (uint32_t)pageSize.size();
            for (auto& [k, v] : gw)
                if (used.count(k.first) && used.count(k.second)) nbr[k.first].push_back({k.second, addPath({k.first, k.second})});
            auto advert = [&](const Hex& c) {
                const std::vector<uint8_t> mine = full[c];
                for (auto& [b, path] : nbr[c]) {
                    const Hex from = c, to = b;
                    send(path, -1, kAdvert, [&, from, to, mine] {
                        bool more = false, less = false;
                        for (uint32_t p = 0; p < mine.size(); ++p) {
                            if (mine[p] && !full[to][p]) {
                                more = true;
                                avail[to][p] = from;
                            }
                            less |= full[to][p] && !mine[p];
                        }
                        if (!more && !less) tk[to].c++;
                        if (less && tk[to].I > tImin) {   // the sender lacks a page of mine: tell it soon
                            tk[to].I = tImin;
                            interval(to);
                        }
                        if (more) askNext(to);
                    });
                }
            };
            interval = [&, advert](const Hex& c) {
                Tk& t = tk[c];
                Simulator::Cancel(t.fire);
                Simulator::Cancel(t.end);
                t.c = 0;
                const double at = t.I / 2 + std::uniform_real_distribution<double>(0, t.I / 2)(trng);
                t.fire = Simulator::Schedule(Seconds(at), [&, c, advert] {
                    if (tk[c].c < tK) advert(c);
                });
                t.end = Simulator::Schedule(Seconds(t.I), [&, c] {
                    tk[c].I = std::min(2 * tk[c].I, tImax);
                    interval(c);
                });
            };
            askNext = [&](const Hex& me) {
                if (asked[me] >= 0) return;
                for (auto& [p, from] : avail[me]) {
                    if (full[me][p]) continue;
                    std::vector<uint32_t> lack;
                    for (uint32_t s : pagePk[p])
                        if (!hold(me)[s]) lack.push_back(s);
                    int toFrom = -1, back = -1;
                    for (auto& [b, path] : nbr[me])
                        if (b == from) toFrom = path;
                    for (auto& [b, path] : nbr[from])
                        if (b == me) back = path;
                    CHECK(toFrom >= 0 && back >= 0);
                    asked[me] = p;
                    const uint32_t id = ++askId[me];
                    const Hex prov = from;
                    send(toFrom, -1, kControl, [&, prov, back, lack] {
                        for (uint32_t s : lack) when(prov, s, [&, s, back] { send(back, (int32_t)s, kPull); });
                    });
                    Simulator::Schedule(Seconds(5 + 0.1 * lack.size()), [&, me, p, id] {
                        if (asked[me] == (int64_t)p && askId[me] == id) {   // no full page yet: ask again
                            asked[me] = -1;
                            askNext(me);
                        }
                    });
                    return;
                }
            };
            onNew = [&](const Hex& c, uint32_t s) {
                if (!obj[s] || !inPage.count(c)) return;
                const uint32_t p = pageOf[s];
                if (++inPage[c][p] < pageSize[p]) return;
                full[c][p] = 1;
                if (asked[c] == (int64_t)p) {
                    asked[c] = -1;
                    askNext(c);
                }
                if (tk[c].I > tImin) {   // new data: advertise soon
                    tk[c].I = tImin;
                    interval(c);
                }
            };
            for (const Hex& c : used) {
                needOr(c, obj);
                inPage[c].assign(P, 0);
                full[c].assign(P, 0);
                asked[c] = -1;
                for (uint32_t s = 0; s < N; ++s)
                    if (obj[s] && hold(c)[s]) inPage[c][pageOf[s]]++;
                for (uint32_t p = 0; p < P; ++p) full[c][p] = inPage[c][p] == pageSize[p];
                atStart.push_back([&, c] {
                    tk[c].I = tImin;
                    interval(c);
                });
            }
            std::printf("trickle: %u packets in %u pages over %zu cells\n", n, P, used.size());
        }
        // Completion of the critical cells.
        std::map<Hex, double> doneAt, lastNew;
        std::map<Hex, uint32_t> left;
        auto finish = [&](const Hex& k) {
            doneAt[k] = now();
            if (doneAt.size() == plan.crit.size()) Simulator::Stop();
        };
        for (const Hex& k : plan.crit) {
            for (uint32_t s = 0; s < N; ++s)
                if (needK[k][s] && !hold(k)[s]) {
                    left[k]++;
                    when(k, s, [&, k] {
                        lastNew[k] = now();
                        if (--left[k] == 0) finish(k);
                    });
                }
        }
        // --repair: every S / 2 seconds, a critical cell idle for S seconds and not done asks again
        std::function<void(const Hex&)> watch = [&](const Hex& k) {
            if (!left[k]) return;
            if (now() - lastNew[k] >= repairS) {
                lastNew[k] = now();
                for (auto& f : redo[k]) f();
            }
            Simulator::Schedule(Seconds(repairS / 2), [&, k] { watch(k); });
        };
        std::function<void()> progress = [&] {
            std::fprintf(stderr, "  run %u t=%.0f s: %llu hops, %llu MAC give-ups, %zu/%zu critical done\n", run,
                         now(), (unsigned long long)hops, (unsigned long long)macFail, doneAt.size(),
                         plan.crit.size());
            Simulator::Schedule(Seconds(10), progress);
        };

        // ---- radio energy: each radio's time per PHY state from the mission start, and its frames ----
        struct Air {
            double t[4] = {0, 0, 0, 0}, since = 0;   // sending, receiving, on and idle (listening), off
            int st = 3;
            uint64_t tx = 0, rx = 0;
            double lastTx = -1;
        };
        std::vector<Air> air(radios.size());
        auto settle = [&](size_t ri) {
            const double t = Simulator::Now().GetSeconds();
            air[ri].t[air[ri].st] += t - air[ri].since;
            air[ri].since = t;
        };
        for (size_t ri = 0; ri < radios.size(); ++ri) {
            Ptr<lrwpan::LrWpanPhy> phy = radios[ri].dev->GetPhy();
            phy->TraceConnectWithoutContext(
                "TrxStateValue", Callback<void, lrwpan::PhyEnumeration, lrwpan::PhyEnumeration>(
                                     [&, ri](lrwpan::PhyEnumeration, lrwpan::PhyEnumeration to) {
                                         settle(ri);
                                         air[ri].st = to == lrwpan::IEEE_802_15_4_PHY_BUSY_TX   ? 0
                                                      : to == lrwpan::IEEE_802_15_4_PHY_BUSY_RX ? 1
                                                      : to == lrwpan::IEEE_802_15_4_PHY_TRX_OFF ||
                                                              to == lrwpan::IEEE_802_15_4_PHY_FORCE_TRX_OFF
                                                          ? 3
                                                          : 2;
                                     }));
            phy->TraceConnectWithoutContext("PhyTxBegin",
                                            Callback<void, Ptr<const Packet>>([&, ri](Ptr<const Packet>) {
                                                air[ri].tx++;
                                                air[ri].lastTx = now();
                                            }));
            phy->TraceConnectWithoutContext(
                "PhyRxEnd", Callback<void, Ptr<const Packet>, double>([&, ri](Ptr<const Packet>, double) { air[ri].rx++; }));
        }
        Simulator::Schedule(Seconds(kT0), [&] {   // count from the mission start
            for (size_t ri = 0; ri < radios.size(); ++ri) {
                settle(ri);
                std::fill(air[ri].t, air[ri].t + 4, 0.0);
            }
        });

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
            for (auto& f : atStart) f();
            for (const Hex& k : plan.crit)
                if (!left[k]) finish(k);
            if (repairS > 0)
                for (const Hex& k : plan.crit)
                    afterGather(k, [&, k] {
                        lastNew[k] = now();
                        Simulator::Schedule(Seconds(repairS / 2), [&, k] { watch(k); });
                    });
            progress();
        });
        Simulator::Stop(Seconds(kT0 + limitS));
        Simulator::Run();
        const double simS = now();
        const double wallS =
            std::chrono::duration<double>(std::chrono::steady_clock::now() - wall0).count();
        const std::string sch = scheme == "river" ? "river-" + prep : scheme;
        for (const Hex& k : plan.crit) {
            uint32_t miss = 0, Dk = 0;
            for (uint32_t s = 0; s < N; ++s) {
                miss += needK[k][s] && !hold(k)[s];
                Dk += needK[k][s];
            }
            std::fprintf(fc, "%u,%s,%d,%d,%u,%u,%u,%.2f,%.2f,%u,%u\n", run, sch.c_str(), k.q, k.r, Dk, lackCL[k],
                         lackCell[k], gatherDone.count(k) ? gatherDone[k] : -1.0, doneAt.count(k) ? doneAt[k] : -1.0,
                         miss, circleN[k]);
        }
        std::map<int, std::vector<size_t>> radiosOf;
        for (size_t ri = 0; ri < radios.size(); ++ri) {
            settle(ri);
            radiosOf[radios[ri].node].push_back(ri);
        }
        for (auto& [v, rs] : radiosOf) {
            double t[4] = {0, 0, 0, 0};
            uint64_t tx = 0, rx = 0;
            double last = -1;
            for (size_t ri : rs) {
                for (int i = 0; i < 4; ++i) t[i] += air[ri].t[i];
                tx += air[ri].tx;
                rx += air[ri].rx;
                last = std::max(last, air[ri].lastTx);
            }
            std::fprintf(fe, "%u,%s,%d,%d,%d,%d,%zu,%.4f,%.4f,%.4f,%.4f,%llu,%llu,%.3f\n", run, sch.c_str(), v,
                         nodes[v].cell.q, nodes[v].cell.r, (int)nodes[v].cl, rs.size(), t[0], t[1], t[2], t[3],
                         (unsigned long long)tx, (unsigned long long)rx, last);
        }
        std::fflush(fe);
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
    std::fclose(fe);
    return 0;
}
