// Step 4: inside one cell, after the UAV pass, every node holds part of a K-chunk
// file. The CL needs a short summary: what does the cell hold, what does it lack?
//
// The CL does not need each node's set, only their union -- or, smaller, what the
// cell LACKS: the chunks no node has. That is an intersection, so it is gathered up
// the in-cell tree to the CL (the toCL next hops of the pre-built routes):
//   each node sends its parent  lacks(subtree) = lacks(self) AND lacks(child) ...
// It shrinks on the way up: near the CL it is usually empty.
//
// A summary is a manifest (manifest.h) of the subtree's lacks: self-contained frames
// over segments of the file, each the shortest of Rice-coded lists or a bitmap. The
// frame also says how many nodes it covers, so the CL knows when it has heard all.
//
// Schedule, planned with the routes: one sender at a time in the cell, slots in
// post-order of the tree (children before their parent), repeated in rounds. In
// its slot a node sends its next frame, unicast to its parent, which ACKs in the
// same slot; no ACK -> the same frame next round. A node starts once all its
// children have delivered (or, with what it has, once a child has stayed quiet for a
// few rounds per level below it: a dead link must not stall the cell). The tree was
// planned from distances; static shadowing can kill a planned link, so after three
// missed ACKs in a row a node reports to another node within 1.5x the link range that
// is closer to the CL in the order (hops, id) -- no loops -- and that node reports
// again with the newcomer included. Which nodes a summary covers travels as a mask,
// so a node heard through two parents is counted once.
// Each cell is on its own channel (PECEE colours neighbours apart).
//
// Radio: the urban G2G channel of G2G-CHAIN (n 3.5, static per-pair shadowing
// 7.8 dB, Rayleigh fading held over 100 ms), +10 dBm, PHY direct. Initial state:
// the per-node reception bitmaps of uav-coop-pass --bits, folded onto K chunks.
//
// Writes PREFIX-cells.csv (per mission and cell: what the CL learned, how fast, at
// what cost) and PREFIX-nodes.csv (the first mission, per node: its final parent and
// what it sent).
//
//   uav-coop-summary --nodes=deploy-nodes-s35.csv --routes=deploy-routes-s35.csv
//                    --bits=bits-r{r}.bin --K=2000 --runs=120 --out=summary

#include "coop-g2g.h"

#include "../models/common/coop-params.h"
#include "../models/common/hex-grid.h"
#include "../models/common/manifest.h"

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
#include <functional>
#include <map>
#include <memory>
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

constexpr uint32_t kChannel = 11;
constexpr uint32_t kManifestMax = 100;   // manifest bytes per frame (app payload ceiling)
constexpr uint32_t kSumHeader = 5;       // type, src, dst, seq, flags; then the covered mask, ceil(n / 8) B
constexpr uint32_t kAckBytes = 5;        // as an 802.15.4 ACK: 2 FCF + 1 seq + 2 FCS
constexpr uint8_t kSum = 1, kAck = 2;
constexpr double kStartS = 1.0;
constexpr uint32_t kSwitchAfter = 3;   // missed ACKs in a row before trying another parent
constexpr double kAltRangeFactor = 1.5;   // other parents up to this x the link range

struct Cfg {
    std::string nodesFile = "deploy-nodes-s35.csv", routesFile = "deploy-routes-s35.csv";
    std::string bits = "bits-r{r}.bin";
    uint32_t K = 2000, runs = 120, firstRun = 1, seed = 1, giveUpRounds = 3;
    double slotS = params::kSlotS, txDbm = params::kTxPowerDbm, sensDbm = params::kRxSensDbm;
    double n = params::kG2gExponent, sigmaDb = params::kG2gShadowDb, cohS = params::kG2gCoherenceS;
    double kFactor = params::kG2gRicianK, limitS = 30.0, linkRangeM = params::kLinkRangeM;
    bool selftest = false;
    std::string out = "summary";
};

using Rows = std::vector<std::map<std::string, std::string>>;

Rows ReadCsv(const std::string& file) {
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
    Rows rows;
    while (std::getline(in, line)) {
        if (line.empty()) continue;
        std::stringstream ls(line);
        std::map<std::string, std::string> r;
        for (size_t i = 0; std::getline(ls, cell, ',') && i < head.size(); ++i) r[head[i]] = cell;
        rows.push_back(r);
    }
    return rows;
}

struct GroundNode {
    uint32_t id;
    double x, y;
    Hex cell;
    bool isCL;
    int64_t toCL;   // node id of the next hop to the CL; -1 at the CL
    int32_t hopsCL;
};

// Per node and chunk: did the node receive any packet carrying the chunk?
std::vector<std::vector<uint8_t>> ReadChunks(const std::string& file, size_t nNodes, uint32_t K) {
    std::ifstream in(file, std::ios::binary | std::ios::ate);
    if (!in) {
        std::fprintf(stderr, "cannot read %s\n", file.c_str());
        std::exit(1);
    }
    const size_t bytes = (size_t)in.tellg();
    CHECK(bytes % nNodes == 0);
    const size_t row = bytes / nNodes;
    in.seekg(0);
    std::vector<uint8_t> buf(bytes);
    in.read((char*)buf.data(), bytes);
    std::vector<std::vector<uint8_t>> have(nNodes, std::vector<uint8_t>(K, 0));
    for (size_t i = 0; i < nNodes; ++i)
        for (size_t s = 0; s < row * 8; ++s)
            if (buf[i * row + s / 8] >> (s % 8) & 1) have[i][s % K] = 1;
    return have;
}

struct Member {
    Ptr<lrwpan::LrWpanPhy> phy;
    int32_t parent = -1;                       // local index; -1 at the CL
    std::vector<int32_t> children;
    uint32_t subtree = 1;                      // nodes in its subtree, itself included
    std::vector<uint8_t> lacks;                // own lacks, AND the children's as they arrive
    std::map<int32_t, std::vector<uint8_t>> childKnown;   // chunks of the child's summary heard
    std::map<int32_t, uint64_t> childCovered;  // nodes the child's final summary covers (bit = node)
    std::map<int32_t, bool> childFinal;
    std::map<int32_t, uint64_t> childHeard;    // round of the child's last frame
    uint32_t height = 0;                       // levels below it
    bool started = false, done = false;        // sending its summary / all of it ACKed
    bool stale = false;                        // lacks shrank after it began: send again
    uint32_t ptr = 0;                          // next segment to send
    uint8_t seq = 0;
    std::vector<uint8_t> frame;                // in flight, for the ACK and a retry
    uint32_t frameEnd = 0;
    bool awaiting = false, acked = false;
    uint8_t lastSeqFrom[256] = {};
    bool seenFrom[256] = {};
    double doneS = -1;
    uint32_t frames = 0, bytes = 0, retries = 0, failsInRow = 0, switches = 0;
    std::vector<int32_t> alternates;           // other parents closer to the CL, nearest first
};

struct NodeRow {
    uint32_t id, parentId, frames, bytes, retries, switches, lacksSelf, lacksSent;
    double doneS;
};

struct CellResult {
    std::vector<NodeRow> rows;
    uint32_t nodes = 0, depth = 0, lacksTrue = 0, lacksAtCL = 0, coveredAtCL = 0;
    bool complete = false, exact = false;
    double doneS = -1;
    uint64_t frames = 0, bytes = 0, retries = 0, acks = 0, maxFramesNode = 0, switches = 0;
};

CellResult RunCell(const Cfg& c, const std::vector<GroundNode>& nodes, const std::vector<size_t>& mem,
                   const std::vector<std::vector<uint8_t>>& chunks, uint32_t cellIdx) {
    const uint32_t n = (uint32_t)mem.size(), K = c.K;
    CellResult R;
    R.nodes = n;
    std::map<uint32_t, int32_t> local;
    for (uint32_t k = 0; k < n; ++k) local[nodes[mem[k]].id] = (int32_t)k;
    std::vector<Member> m(n);
    int32_t cl = -1;
    for (uint32_t k = 0; k < n; ++k) {
        const GroundNode& g = nodes[mem[k]];
        if (g.isCL) { CHECK(cl < 0 && g.toCL < 0); cl = (int32_t)k; continue; }
        CHECK(local.count((uint32_t)g.toCL));   // the tree stays inside the cell
        m[k].parent = local.at((uint32_t)g.toCL);
        m[m[k].parent].children.push_back((int32_t)k);
    }
    CHECK(cl >= 0);
    // Local repair: other parents in range and strictly closer to the CL (no loops).
    for (uint32_t k = 0; k < n; ++k) {
        if ((int32_t)k == cl) continue;
        const GroundNode& g = nodes[mem[k]];
        std::vector<std::pair<double, int32_t>> alt;
        for (uint32_t o = 0; o < n; ++o) {
            const GroundNode& h = nodes[mem[o]];
            const double d = std::hypot(g.x - h.x, g.y - h.y);
            // closer to the CL in the order (hops, id): no loops; a little beyond the
            // planned range (weaker, but better than a dead link)
            const bool closer = h.hopsCL < g.hopsCL || (h.hopsCL == g.hopsCL && h.id < g.id);
            if ((int32_t)o != m[k].parent && closer && d <= kAltRangeFactor * c.linkRangeM)
                alt.push_back({d, (int32_t)o});
        }
        std::sort(alt.begin(), alt.end());
        for (const auto& [d, o] : alt) m[k].alternates.push_back(o);
    }
    // Post-order from the CL: the sending order; depth and subtree sizes.
    std::vector<int32_t> order;
    std::vector<uint32_t> depth(n, 0);
    std::function<void(int32_t)> visit = [&](int32_t k) {
        for (int32_t ch : m[k].children) {
            depth[ch] = depth[k] + 1;
            visit(ch);
            m[k].subtree += m[ch].subtree;
            m[k].height = std::max(m[k].height, m[ch].height + 1);
        }
        if (k != cl) order.push_back(k);
    };
    visit(cl);
    CHECK(order.size() == n - 1 && m[cl].subtree == n);   // a tree: every node reached once
    R.depth = *std::max_element(depth.begin(), depth.end());

    std::vector<uint8_t> trueLacks(K, 1);
    for (uint32_t k = 0; k < n; ++k)
        for (uint32_t j = 0; j < K; ++j) {
            m[k].lacks.push_back(chunks[mem[k]][j] ? 0 : 1);
            trueLacks[j] &= m[k].lacks[j];
        }
    R.lacksTrue = (uint32_t)std::count(trueLacks.begin(), trueLacks.end(), 1);
    for (uint32_t k = 0; k < n; ++k)
        for (int32_t ch : m[k].children) {
            m[k].childKnown[ch].assign(K, 0);
            m[k].childFinal[ch] = false;
            m[k].childHeard[ch] = 0;
        }

    NodeContainer nc;
    nc.Create(n);
    MobilityHelper mh;
    mh.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    mh.Install(nc);
    for (uint32_t k = 0; k < n; ++k)
        nc.Get(k)->GetObject<MobilityModel>()->SetPosition(Vector(nodes[mem[k]].x, nodes[mem[k]].y, 1.5));
    // ONE helper per cell, alive until Destroy: its destructor disposes the channel.
    auto lr = std::make_unique<LrWpanHelper>();
    Ptr<CoopG2gLossModel> link;
    Ptr<SpectrumChannel> ch = BuildG2gChannel(c.n, c.selftest ? 0.0 : c.sigmaDb, c.selftest ? 0.0 : c.cohS,
                                              c.kFactor, params::kFspl1mDb, link);
    lr->SetChannel(ch);
    NetDeviceContainer devs = lr->Install(nc);
    CHECK(ch->GetNDevices() == n);
    // Fixed streams: cell i of mission r depends on (seed, r, i) alone.
    link->AssignStreams(10 * cellIdx);
    lr->AssignStreams(devs, 100000 + 1000 * (int64_t)cellIdx);
    for (uint32_t k = 0; k < n; ++k) m[k].phy = DynamicCast<lrwpan::LrWpanNetDevice>(devs.Get(k))->GetPhy();

    std::vector<std::vector<uint8_t>> pending(n);   // what to send on TX_ON
    bool finished = false;
    auto transmit = [&](uint32_t k, std::vector<uint8_t> f) {
        pending[k] = std::move(f);
        m[k].phy->PlmeSetTRXStateRequest(lrwpan::IEEE_802_15_4_PHY_TX_ON);
    };
    uint64_t roundNow = 0;
    // The nodes a node's summary covers: itself and its children's final summaries.
    // A mask, not a count: a node that re-parented after its old parent already had
    // its summary is then covered twice, and must be counted once.
    auto coveredBy = [&](uint32_t k) {
        uint64_t mask = 1ull << k;
        for (int32_t ch2 : m[k].children)
            if (m[k].childFinal[ch2]) mask |= m[k].childCovered[ch2];
        return mask;
    };
    const uint64_t all = n == 64 ? ~0ull : (1ull << n) - 1;
    const uint32_t maskBytes = (n + 7) / 8;
    auto clComplete = [&]() { return coveredBy(cl) == all; };   // every node is in the CL's summary

    for (uint32_t k = 0; k < n; ++k) {
        m[k].phy->SetPlmeSetTRXStateConfirmCallback(lrwpan::PlmeSetTRXStateConfirmCallback(
            [&, k](lrwpan::PhyEnumeration s) {
                if (s != lrwpan::IEEE_802_15_4_PHY_TX_ON || pending[k].empty()) return;
                std::vector<uint8_t> f = std::move(pending[k]);
                pending[k].clear();
                m[k].phy->PdDataRequest((uint32_t)f.size(), Create<Packet>(f.data(), (uint32_t)f.size()));
            }));
        m[k].phy->SetPdDataConfirmCallback(lrwpan::PdDataConfirmCallback([&, k](lrwpan::PhyEnumeration s) {
            CHECK(s == lrwpan::IEEE_802_15_4_PHY_SUCCESS);
            m[k].phy->PlmeSetTRXStateRequest(lrwpan::IEEE_802_15_4_PHY_RX_ON);
        }));
        m[k].phy->SetPdDataIndicationCallback(lrwpan::PdDataIndicationCallback(
            [&, k](uint32_t len, Ptr<Packet> p, uint8_t) {
                std::vector<uint8_t> f(len);
                p->CopyData(f.data(), len);
                const uint8_t type = f[0], src = f[1], dst = f[2], seq = f[3];
                if (dst != k) return;   // overheard
                Member& me = m[k];
                if (type == kAck) {
                    CHECK(len == kAckBytes);
                    if (me.awaiting && src == (uint8_t)me.parent && seq == me.seq) me.acked = true;
                    return;
                }
                CHECK(type == kSum && len >= kSumHeader + maskBytes + kManifestHeader);
                const int32_t child = src;
                CHECK(nodes[mem[child]].hopsCL > nodes[mem[k]].hopsCL ||
                      (nodes[mem[child]].hopsCL == nodes[mem[k]].hopsCL && nodes[mem[child]].id > nodes[mem[k]].id));
                if (!me.childKnown.count(child)) {   // a node that switched to this parent
                    me.childKnown[child].assign(K, 0);
                    me.childFinal[child] = false;
                    me.children.push_back(child);
                }
                transmit(k, {kAck, (uint8_t)k, src, seq, 0});   // ACK every copy
                if (me.seenFrom[src] && me.lastSeqFrom[src] == seq) return;   // a retry: ACKed again
                me.seenFrom[src] = true;
                me.lastSeqFrom[src] = seq;
                me.childHeard[child] = roundNow;
                const bool final = f[4] & 1;
                const ManifestView v = DecodeManifest(std::vector<uint8_t>(f.begin() + kSumHeader + maskBytes, f.end()));
                CHECK(v.kind == kSum && v.b <= K && v.a < v.b);
                for (uint32_t j = v.a; j < v.b; ++j) {
                    me.childKnown[child][j] = 1;
                    if (!v.member[j - v.a] && me.lacks[j]) {   // the child's subtree holds j
                        me.lacks[j] = 0;
                        if (me.started) me.stale = true;      // a late child (after the give-up)
                    }
                }
                if (final) {
                    for (uint32_t j = 0; j < K; ++j) CHECK(me.childKnown[child][j]);
                    uint64_t mask = 0;
                    for (uint32_t b = 0; b < maskBytes; ++b) mask |= (uint64_t)f[kSumHeader + b] << (8 * b);
                    CHECK(mask >> child & 1);
                    if (me.started && (coveredBy(k) | mask) != coveredBy(k))
                        me.stale = true;   // more of the cell to report upward
                    me.childFinal[child] = true;
                    me.childCovered[child] |= mask;
                }
                if ((int32_t)k == cl && clComplete() && !finished) {
                    finished = true;
                    R.doneS = Simulator::Now().GetSeconds() - kStartS;
                    Simulator::Stop(MilliSeconds(5));
                }
            }));
    }

    Simulator::Schedule(Seconds(kStartS / 2), [&]() {
        lrwpan::LrWpanSpectrumValueHelper svh;
        for (Member& me : m) {
            me.phy->SetRxSensitivity(c.sensDbm);
            me.phy->SetTxPowerSpectralDensity(svh.CreateTxPowerSpectralDensity(c.txDbm, kChannel));
            me.phy->PlmeSetTRXStateRequest(lrwpan::IEEE_802_15_4_PHY_RX_ON);
        }
    });

    const uint64_t round = order.size(), maxSlots = (uint64_t)std::ceil(c.limitS / c.slotS);
    std::function<void(uint64_t)> slot = [&](uint64_t s) {
        const int32_t k = order[s % round];
        Member& me = m[k];
        const uint64_t r = s / round;
        roundNow = r;
        if (me.awaiting) {   // the outcome of its previous frame
            me.awaiting = false;
            if (me.acked) {
                me.ptr = me.frameEnd;
                me.frame.clear();
                if (me.ptr == K) { me.done = true; me.doneS = Simulator::Now().GetSeconds() - kStartS; }
                me.failsInRow = 0;
            } else {
                me.retries++;
                // A link the plan thought good may be dead (static shadowing): after a
                // few misses, report to the next candidate parent, from the start.
                if (++me.failsInRow >= kSwitchAfter && !me.alternates.empty()) {
                    me.parent = me.alternates.front();
                    me.alternates.erase(me.alternates.begin());
                    me.failsInRow = 0;
                    me.switches++;
                    me.ptr = 0;
                    me.done = false;
                    me.frame.clear();
                }
            }
        }
        if (me.stale && !me.awaiting) {   // start the summary over: lacks only shrink
            me.stale = false;
            me.done = false;
            me.ptr = 0;
            me.frame.clear();
        }
        if (!me.done) {
            // Start when every child has delivered, or the rest have gone quiet: no
            // frame for giveUp rounds per level below them (they may be waiting too).
            bool ready = true;
            for (int32_t ch2 : me.children)
                ready = ready && (me.childFinal[ch2] ||
                                  r - me.childHeard[ch2] >= (uint64_t)c.giveUpRounds * (m[ch2].height + 1));
            if (!me.started && ready) me.started = true;
            if (me.started) {
                if (me.frame.empty()) {   // the next segment of the subtree's lacks
                    ManifestFrame mf = EncodeManifest(kSum, me.lacks, me.ptr, kManifestMax);
                    const ManifestView v = DecodeManifest(mf.bytes);   // round trip, every frame
                    CHECK(v.a == me.ptr && v.b == mf.b);
                    for (uint32_t j = v.a; j < v.b; ++j) CHECK(v.member[j - v.a] == me.lacks[j]);
                    const uint64_t covered = coveredBy(k);
                    me.seq++;
                    me.frame = {kSum, (uint8_t)k, (uint8_t)me.parent, me.seq, (uint8_t)(mf.b == K ? 1 : 0)};
                    for (uint32_t b = 0; b < maskBytes; ++b) me.frame.push_back((uint8_t)(covered >> (8 * b)));
                    me.frame.insert(me.frame.end(), mf.bytes.begin(), mf.bytes.end());
                    me.frameEnd = mf.b;
                }
                me.awaiting = true;
                me.acked = false;
                me.frames++;
                me.bytes += (uint32_t)me.frame.size();
                transmit(k, me.frame);
            }
        }
        if (s + 1 < maxSlots && !finished)
            Simulator::Schedule(Seconds(c.slotS), [&slot, s]() { slot(s + 1); });
    };
    Simulator::Schedule(Seconds(kStartS), [&slot]() { slot(0); });
    Simulator::Stop(Seconds(kStartS + c.limitS + 0.1));
    Simulator::Run();
    Simulator::Destroy();

    // What the CL now knows: its own lacks AND everything its children reported.
    R.complete = finished;
    R.lacksAtCL = (uint32_t)std::count(m[cl].lacks.begin(), m[cl].lacks.end(), 1);
    R.coveredAtCL = (uint32_t)__builtin_popcountll(coveredBy(cl));
    R.exact = m[cl].lacks == trueLacks;
    for (uint32_t j = 0; j < K; ++j) CHECK(m[cl].lacks[j] >= trueLacks[j]);   // never claims too much
    if (R.complete && R.coveredAtCL == n) CHECK(R.exact);   // heard everyone: exact
    for (uint32_t k = 0; k < n; ++k) {
        const Member& me = m[k];
        uint32_t self = 0;
        for (uint32_t j = 0; j < K; ++j) self += chunks[mem[k]][j] ? 0 : 1;
        R.rows.push_back({nodes[mem[k]].id, me.parent < 0 ? nodes[mem[k]].id : nodes[mem[me.parent]].id,
                          me.frames, me.bytes, me.retries, me.switches, self,
                          (uint32_t)std::count(me.lacks.begin(), me.lacks.end(), 1), me.doneS});
        R.frames += me.frames;
        R.bytes += me.bytes;
        R.retries += me.retries;
        R.maxFramesNode = std::max<uint64_t>(R.maxFramesNode, me.frames);
        R.switches += me.switches;
    }
    return R;
}

}  // namespace

int main(int argc, char* argv[]) {
    Cfg c;
    double slotMs = c.slotS * 1e3;
    CommandLine cmd(__FILE__);
    cmd.AddValue("nodes", "nodes CSV from uav-coop-deploy", c.nodesFile);
    cmd.AddValue("routes", "routes CSV from uav-coop-deploy (the toCL tree)", c.routesFile);
    cmd.AddValue("bits", "reception bitmaps from uav-coop-pass --bits; {r} = mission", c.bits);
    cmd.AddValue("K", "file size in chunks (packet s carries chunk s mod K)", c.K);
    cmd.AddValue("runs", "missions", c.runs);
    cmd.AddValue("firstRun", "first mission", c.firstRun);
    cmd.AddValue("seed", "RNG seed", c.seed);
    cmd.AddValue("slotMs", "TDMA slot, ms", slotMs);
    cmd.AddValue("giveUp", "quiet rounds per level below a child before a node sends without it", c.giveUpRounds);
    cmd.AddValue("limit", "give up on a cell after this long, s", c.limitS);
    cmd.AddValue("selftest", "no shadowing, no fading", c.selftest);
    cmd.AddValue("out", "output prefix", c.out);
    cmd.Parse(argc, argv);
    c.slotS = slotMs / 1e3;
    CHECK(c.K >= 1 && c.K <= 65535 && c.slotS >= 0.006);   // frame + turnaround + ACK fit

    std::map<std::string, int64_t> toCL;
    std::map<std::string, int32_t> hopsCL;
    for (const auto& r : ReadCsv(c.routesFile)) {
        toCL[r.at("id")] = std::stoll(r.at("toCL"));
        hopsCL[r.at("id")] = std::stoi(r.at("hopsCL"));
    }
    std::vector<GroundNode> nodes;
    for (const auto& r : ReadCsv(c.nodesFile))
        nodes.push_back({(uint32_t)std::stoul(r.at("id")), std::stod(r.at("x")), std::stod(r.at("y")),
                         {std::stoi(r.at("q")), std::stoi(r.at("r"))}, r.at("isCL") == "1", toCL.at(r.at("id")),
                         hopsCL.at(r.at("id"))});
    std::map<Hex, std::vector<size_t>> cells;
    for (size_t i = 0; i < nodes.size(); ++i) cells[nodes[i].cell].push_back(i);
    for (const auto& [h, v] : cells) CHECK(v.size() <= 64);   // the covered mask
    std::printf("%zu nodes in %zu cells; file of %u chunks; summaries up the toCL tree, %.0f ms slots in "
                "post-order, one sender per cell; G2G n %.1f, shadowing %.1f dB, coherence %.0f ms%s\n",
                nodes.size(), cells.size(), c.K, c.slotS * 1e3, c.n, c.selftest ? 0.0 : c.sigmaDb,
                c.selftest ? 0.0 : c.cohS * 1e3, c.selftest ? "  [SELFTEST]" : "");

    FILE* fc = std::fopen((c.out + "-cells.csv").c_str(), "w");
    std::fprintf(fc, "run,q,r,nodes,depth,lacksTrue,lacksAtCL,coveredAtCL,complete,exact,doneS,frames,"
                     "bytes,retries,maxFramesNode,switches\n");
    FILE* fn = std::fopen((c.out + "-nodes.csv").c_str(), "w");   // the first mission
    std::fprintf(fn, "run,id,parent,frames,bytes,retries,switches,lacksSelf,lacksSent,doneS\n");
    for (uint32_t run = c.firstRun; run < c.firstRun + c.runs; ++run) {
        RngSeedManager::SetSeed(c.seed);
        RngSeedManager::SetRun(run);
        std::string file = c.bits;
        const size_t at = file.find("{r}");
        if (at != std::string::npos) file.replace(at, 3, std::to_string(run));
        const auto chunks = ReadChunks(file, nodes.size(), c.K);
        uint32_t idx = 0, exact = 0;
        double worst = 0;
        uint64_t frames = 0;
        for (const auto& [h, mem] : cells) {
            const CellResult R = RunCell(c, nodes, mem, chunks, idx++);
            if (run == c.firstRun)
                for (const NodeRow& w : R.rows)
                    std::fprintf(fn, "%u,%u,%u,%u,%u,%u,%u,%u,%u,%.4f\n", run, w.id, w.parentId, w.frames, w.bytes,
                                 w.retries, w.switches, w.lacksSelf, w.lacksSent, w.doneS);
            exact += R.complete && R.exact;
            worst = std::max(worst, R.complete ? R.doneS : c.limitS);
            frames += R.frames;
            std::fprintf(fc, "%u,%d,%d,%u,%u,%u,%u,%u,%d,%d,%.4f,%llu,%llu,%llu,%llu,%llu\n", run, h.q, h.r,
                         R.nodes, R.depth, R.lacksTrue, R.lacksAtCL, R.coveredAtCL, R.complete ? 1 : 0,
                         R.exact ? 1 : 0, R.doneS, (unsigned long long)R.frames,
                         (unsigned long long)R.bytes, (unsigned long long)R.retries,
                         (unsigned long long)R.maxFramesNode, (unsigned long long)R.switches);
        }
        std::fflush(fc);
        std::printf("  mission %u: %u/%zu CLs hold the exact cell summary, slowest %.2f s, %llu frames\n", run,
                    exact, cells.size(), worst, (unsigned long long)frames);
        std::fflush(stdout);
    }
    std::fclose(fc);
    std::fclose(fn);
    std::printf("%u CHECKS PASSED\n", g_checks);
    return 0;
}
