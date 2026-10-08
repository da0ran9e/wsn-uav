// Step 5, first trial: the base manifest phase between cells (docs/MANIFEST-vi.md),
// at the LOGIC level -- who sends what to whom, how manifests are cut, where copies
// are kept. No radio yet: costs are counted in frame-hops and turned into an
// optimistic time (one 10 ms slot per frame-hop, no loss, no contention).
//
// State: each cell's union of chunks after the UAV pass (bitmaps of uav-coop-pass
// --bits, folded onto K chunks, split into F files). A cell is ready when its CL has
// the intra-cell summary (summary-cells.csv of the same mission).
//
// Roles, from the plan. "x waits for b" when x is the next cell of border cell b.
//   initiator: a border cell no other border cell sends to -> when ready and lacking,
//              MANIFEST of what it HOLDS (what it lacks is everything else) to its next
//   waiter:    any cell that is the next cell of a border cell, border or not -> waits;
//              after ready + wait, if it lacks and a border cell that should have sent
//              it a manifest has not, it sends that cell a REVERSE manifest
// A manifest reaching cell x (from cell p):
//   - x sends back toward p what it holds of what the manifest lacks;
//   - the manifest x passes on describes x as it now stands: what the manifest held
//     (plus what x just sent) AND what x itself holds -- so x's own gaps join it;
//   - passed on to x's next cell while anything is lacking; at the CH's cell the base
//     phase ends (the rest: secondary phase).
// Data going back: every cell it reaches keeps what it lacks, and passes on toward
// the origin only what the cell behind it lacked (by the manifest that cell sent).
// A border cell a reverse manifest reaches sends what it holds of what the sender
// lacks; if it lacks anything itself, it is now triggered.
// Kept chunks go to the CL; the strong nodes on the way keep a copy of their own.
//
//   uav-coop-manifest --nodes=deploy-nodes-s35.csv --bits=bits-r{r}.bin
//                     --summary=summary-cells.csv --runs=120 --out=manifest

#include "../models/common/coop-params.h"
#include "../models/common/deploy.h"
#include "../models/common/hex-grid.h"
#include "../models/common/manifest.h"
#include "../models/common/routing.h"

#include "ns3/core-module.h"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <deque>
#include <fstream>
#include <functional>
#include <map>
#include <queue>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
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

constexpr uint32_t kFramePayload = 100;   // bytes per frame
constexpr uint32_t kManifestHead = 7;     // type, origin q, origin r, seq (2), TTL, files

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

enum Role { kInit = 0, kWaitBorder = 1, kWaitInner = 2, kOther = 3 };

struct Cfg {
    std::string nodesFile = "deploy-nodes-s35.csv", bits = "bits-r{r}.bin", summary = "";
    uint32_t K = 2000, files = 4, runs = 120, firstRun = 1, ttl = 32;
    double slotS = params::kSlotS, waitS = 2.0, linkRangeM = params::kLinkRangeM, notReadyS = 30.0;
    std::string blank = "";   // cells (q:r,q:r) that received nothing: tests the reverse manifest
    std::string out = "manifest";
};

struct Plan {
    std::vector<SensorNode> nodes;
    size_t ch = 0;
    Routing R;
    std::vector<Hex> cells;
    std::map<Hex, size_t> ci;
    std::vector<std::vector<int32_t>> members;
    std::vector<int32_t> cl, next;   // per cell: CL node; next cell index (-1 at the CH's cell)
    std::vector<int> role;
    std::vector<uint8_t> border;
    std::vector<std::vector<size_t>> upstream;   // border cells whose next cell this is
    std::vector<std::vector<int32_t>> keepers;   // CL + nodes above the cell's mean strength
    size_t chCell = 0;
};

// A kept chunk goes from the node it arrives at to the CL; the strong nodes on that
// path keep a copy as it passes. Returns the hops; marks the holders.
uint32_t StoreAtCL(const Plan& P, size_t cell, int32_t e, uint32_t j, std::vector<std::vector<uint8_t>>& holder) {
    const int32_t cl = P.cl[cell];
    const std::set<int32_t> keep(P.keepers[cell].begin(), P.keepers[cell].end());
    uint32_t hops = 0;
    for (int32_t v = e;; v = P.R.table[v].toCL.next) {
        CHECK(P.nodes[v].cell == P.cells[cell]);
        if (keep.count(v)) holder[v][j] = 1;
        if (v == cl) break;
        ++hops;
    }
    CHECK(hops == P.R.table[e].toCL.hops);
    return hops;
}

// Bytes of a manifest of `held` (K chunks in F files): per file one byte, plus the
// manifest frames of its chunks unless the file is complete.
uint32_t ManifestBytes(const std::vector<uint8_t>& held, uint32_t files) {
    const uint32_t K = (uint32_t)held.size(), per = K / files;
    uint32_t bytes = kManifestHead;
    for (uint32_t f = 0; f < files; ++f) {
        std::vector<uint8_t> part(held.begin() + f * per, held.begin() + (f + 1) * per);
        bytes += 1;
        if (std::count(part.begin(), part.end(), 1) == (long)per) continue;   // "A": complete
        for (uint32_t a = 0; a < per;) {
            ManifestFrame mf = EncodeManifest(0, part, a, kFramePayload - kManifestHead);
            const ManifestView v = DecodeManifest(mf.bytes);   // round trip
            for (uint32_t j = a; j < mf.b; ++j) CHECK(v.member[j - a] == part[j]);
            bytes += (uint32_t)mf.bytes.size();
            a = mf.b;
        }
    }
    return bytes;
}

struct CellOut {
    uint32_t lacks0 = 0, lacksEnd = 0, manifests = 0, forwarded = 0, reverse = 0, supplied = 0,
             cached = 0, received = 0;
    double fullS = -1;
};

struct MissionOut {
    std::vector<CellOut> cell;
    uint64_t hopsManifest = 0, hopsData = 0, hopsStore = 0, manifestBytes = 0, dup = 0;
    uint32_t toCH = 0, chRemainder = 0;
    double lastS = 0;
};

MissionOut RunMission(const Cfg& c, const Plan& P, const std::vector<std::vector<uint8_t>>& node,
                      const std::vector<double>& ready, FILE* trace, FILE* hold) {
    // trace rows: what, sentS, atS, from q,r, to q,r, origin q,r, chunks
    auto tr = [&](const char* what, double t0, double t1, size_t a, size_t b, size_t o, uint64_t n) {
        if (!trace) return;
        std::fprintf(trace, "%s,%.4f,%.4f,%d,%d,%d,%d,%d,%d,%llu\n", what, t0, t1, P.cells[a].q, P.cells[a].r,
                     P.cells[b].q, P.cells[b].r, P.cells[o].q, P.cells[o].r, (unsigned long long)n);
    };
    const size_t nc = P.cells.size();
    const uint32_t K = c.K;
    MissionOut M;
    M.cell.resize(nc);
    std::vector<std::vector<uint8_t>> have(nc, std::vector<uint8_t>(K, 0));
    for (size_t x = 0; x < nc; ++x)
        for (int32_t i : P.members[x])
            for (uint32_t j = 0; j < K; ++j) have[x][j] |= node[i][j];
    std::vector<std::vector<uint8_t>> holder = node;   // node-level, grows where chunks are kept
    auto lacking = [&](size_t x) { return (uint32_t)std::count(have[x].begin(), have[x].end(), 0); };
    for (size_t x = 0; x < nc; ++x) {
        M.cell[x].lacks0 = lacking(x);
        if (M.cell[x].lacks0 == 0) M.cell[x].fullS = 0;
    }
    std::vector<uint8_t> sent(nc, 0);             // has sent its own manifest
    std::vector<std::set<size_t>> heardFrom(nc);   // waiters: upstream border cells heard

    // A manifest in flight: the cells it passed (origin first) and, per hop, the
    // manifest that cell sent -- what the data coming back is filtered by.
    struct Ev {
        double t;
        uint64_t seq;
        int kind;   // 0 initiator ready, 1 waiter checks, 2 manifest at cell, 3 reverse at border,
                    // 4 data at cell path[ttl] (its last chunk)
        size_t at, origin;
        std::vector<size_t> path;
        std::vector<std::vector<uint8_t>> said;   // said[k]: manifest path[k] sent to path[k+1]
        uint32_t ttl;
        int32_t entry;   // node it arrives at
        std::vector<uint32_t> js = {};   // data: the chunks
    };
    auto cmp = [](const Ev& a, const Ev& b) { return a.t != b.t ? a.t > b.t : a.seq > b.seq; };
    std::priority_queue<Ev, std::vector<Ev>, decltype(cmp)> pq(cmp);
    uint64_t seqNo = 0;
    for (size_t x = 0; x < nc; ++x) {
        if (P.role[x] == kInit) pq.push({ready[x], seqNo++, 0, x, x, {}, {}, 0, -1});
        if (!P.upstream[x].empty()) pq.push({ready[x] + c.waitS, seqNo++, 1, x, x, {}, {}, 0, -1});
    }
    const double slot = c.slotS;
    auto frames = [&](const std::vector<uint8_t>& held) {
        const uint32_t bytes = ManifestBytes(held, c.files);
        M.manifestBytes += bytes;
        return (bytes + kFramePayload - 1) / kFramePayload;
    };
    // Chunks js (all needed by path[k-1]) leave cell path[k] back toward path[0], one
    // cell per event. Pipelined: an event's time is when the batch's LAST chunk
    // arrives; each further hop of h frame-hops adds h slots.
    auto sendBack = [&](double t, size_t k, const std::vector<size_t>& path,
                        const std::vector<std::vector<uint8_t>>& said, const std::vector<uint32_t>& js) {
        if (js.empty()) return;
        const size_t from = path[k];
        const size_t to = path[k - 1];
        uint32_t firstLeg = 0;
        for (uint32_t j : js) {   // the holder nearest to the gateway toward `to`
            CHECK(!said[k - 1][j] && have[from][j]);
            uint32_t bh = kNoRoute;
            for (int32_t i : P.members[from])
                if (holder[i][j]) bh = std::min(bh, P.R.table[i].toCell.at(P.cells[to]).hops);
            CHECK(bh != kNoRoute);   // the cell holds it, so some node does
            M.hopsData += bh;
            firstLeg = std::max(firstLeg, bh);
        }
        M.cell[from].supplied += (uint32_t)js.size();
        Ev d{t + (double)(firstLeg + js.size() - 1) * slot, seqNo++, 4, to, from, path, said, (uint32_t)(k - 1),
             P.R.gateway.at({P.cells[from], P.cells[to]}).b, js};
        tr("data", t, d.t, from, to, path[0], js.size());
        pq.push(d);
    };
    // Data reaches cell path[i]: keep what it lacks (to the CL), pass on what the cell
    // behind it lacked.
    auto dataAt = [&](const Ev& e) {
        const size_t i = e.ttl;
        const size_t x = e.path[i];
        const bool origin = i == 0;
        std::vector<uint32_t> keep, pass;
        for (uint32_t j : e.js) {
            if (!have[x][j]) keep.push_back(j);
            else if (origin) M.dup++;
            if (!origin && !e.said[i - 1][j]) pass.push_back(j);
        }
        uint32_t viaCL = 0;
        for (uint32_t j : keep) {
            have[x][j] = 1;
            viaCL = StoreAtCL(P, x, e.entry, j, holder);
            M.hopsStore += viaCL;
        }
        if (!keep.empty()) {
            (origin ? M.cell[x].received : M.cell[x].cached) += (uint32_t)keep.size();
            const double atCL = e.t + viaCL * slot;
            tr(origin ? "received" : "copy", e.t, atCL, x, x, e.path[0], keep.size());
            if (M.cell[x].fullS < 0 && lacking(x) == 0) M.cell[x].fullS = atCL;
            M.lastS = std::max(M.lastS, atCL);
        }
        if (origin || pass.empty()) return;
        // on toward path[i-1]: kept ones from the CL, the others gateway to gateway
        const size_t nx = e.path[i - 1];
        const uint32_t fromCL = P.R.table[P.cl[x]].toCell.at(P.cells[nx]).hops;
        const uint32_t direct = P.R.table[e.entry].toCell.at(P.cells[nx]).hops;
        uint32_t worst = 0;
        for (uint32_t j : pass) {
            const bool kept = std::find(keep.begin(), keep.end(), j) != keep.end();
            M.hopsData += kept ? fromCL : direct;
            worst = std::max(worst, kept ? viaCL + fromCL : direct);
        }
        Ev d{e.t + worst * slot, seqNo++, 4, nx, e.origin, e.path, e.said, (uint32_t)(i - 1),
             P.R.gateway.at({P.cells[x], P.cells[nx]}).b, pass};
        tr("data", e.t, d.t, x, nx, e.path[0], pass.size());
        pq.push(d);
    };
    // Cell x passes a manifest on to its next cell.
    auto passOn = [&](double t, size_t x, int32_t fromNode, Ev e) {
        const int32_t nx = P.next[x];
        const std::vector<uint8_t>& held = e.said.back();
        if (std::count(held.begin(), held.end(), 0) == 0) return;   // nothing lacking
        if (nx < 0) { M.toCH++; M.chRemainder += (uint32_t)std::count(held.begin(), held.end(), 0); return; }
        if (e.ttl == 0) return;
        const uint32_t h = P.R.table[fromNode].toCell.at(P.cells[nx]).hops;
        const uint32_t f = frames(held);
        M.hopsManifest += (uint64_t)f * h;
        e.path.push_back((size_t)nx);
        e.at = (size_t)nx;
        e.kind = 2;
        e.ttl--;
        e.entry = P.R.gateway.at({P.cells[x], P.cells[nx]}).b;
        e.t = t + (h + f - 1) * slot;
        e.seq = seqNo++;
        tr("manifest", t, e.t, x, (size_t)nx, e.path[0], (uint64_t)std::count(held.begin(), held.end(), 0));
        pq.push(e);
    };
    auto own = [&](double t, size_t x) {   // x sends its own manifest
        sent[x] = 1;
        M.cell[x].manifests++;
        Ev e{t, 0, 2, x, x, {x}, {have[x]}, c.ttl, P.cl[x]};
        passOn(t, x, P.cl[x], e);
    };

    while (!pq.empty()) {
        Ev e = pq.top();
        pq.pop();
        const size_t x = e.at;
        if (e.kind == 0) {
            // Received nothing: never triggered (the trigger is the end of reception).
            if (!sent[x] && lacking(x) > 0 && lacking(x) < K) own(e.t, x);
        } else if (e.kind == 1) {
            if (lacking(x) == 0) continue;
            for (size_t b : P.upstream[x]) {
                if (heardFrom[x].count(b)) continue;
                const uint32_t h = P.R.table[P.cl[x]].toCell.at(P.cells[b]).hops;
                const uint32_t f = frames(have[x]);
                M.hopsManifest += (uint64_t)f * h;
                M.cell[x].reverse++;
                tr("reverse", e.t, e.t + (h + f - 1) * slot, x, b, x, lacking(x));
                pq.push({e.t + (h + f - 1) * slot, seqNo++, 3, b, x, {x, b}, {have[x]}, 1,
                         P.R.gateway.at({P.cells[x], P.cells[b]}).b});
            }
        } else if (e.kind == 2) {
            const size_t k = e.path.size() - 1;
            const size_t p = e.path[k - 1];
            heardFrom[x].insert(p);
            M.cell[x].forwarded++;
            M.hopsManifest += (uint64_t)P.R.table[e.entry].toCL.hops * frames(e.said.back());   // to the CL
            std::vector<uint32_t> give;
            std::vector<uint8_t> held = e.said.back();
            for (uint32_t j = 0; j < K; ++j)
                if (!held[j] && have[x][j]) { give.push_back(j); held[j] = 1; }
            sendBack(e.t, k, e.path, e.said, give);
            for (uint32_t j = 0; j < K; ++j) held[j] = held[j] && have[x][j];   // x as it stands
            e.said.push_back(held);
            passOn(e.t, x, P.cl[x], e);
        } else if (e.kind == 4) {
            dataAt(e);
        } else {   // reverse manifest at border cell x from waiter e.origin
            std::vector<uint32_t> give;
            for (uint32_t j = 0; j < K; ++j)
                if (!e.said[0][j] && have[x][j]) give.push_back(j);
            sendBack(e.t, 1, e.path, e.said, give);
            if (!sent[x] && lacking(x) > 0) own(e.t, x);   // it understands: its turn
        }
    }
    for (size_t x = 0; x < nc; ++x) {
        M.cell[x].lacksEnd = lacking(x);
        CHECK(M.cell[x].lacksEnd <= M.cell[x].lacks0);
        for (int32_t i : P.members[x])
            for (uint32_t j = 0; j < K; ++j) CHECK(!holder[i][j] || have[x][j]);
    }
    if (hold) {   // where the data sits now: per node, before and after
        for (size_t x = 0; x < nc; ++x)
            for (int32_t i : P.members[x]) {
                const bool strong = std::find(P.keepers[x].begin(), P.keepers[x].end(), i) != P.keepers[x].end();
                const uint32_t before = (uint32_t)std::count(node[i].begin(), node[i].end(), 1);
                const uint32_t after = (uint32_t)std::count(holder[i].begin(), holder[i].end(), 1);
                CHECK(after >= before);
                std::fprintf(hold, "node,%u,%d,%d,%d,%d,%u,%u\n", P.nodes[i].id, P.cells[x].q, P.cells[x].r,
                             i == P.cl[x] ? 1 : 0, strong && i != P.cl[x] ? 1 : 0, before, after);
            }
        // per cell: copies of each chunk among its nodes, before and after
        for (size_t x = 0; x < nc; ++x)
            for (int pass = 0; pass < 2; ++pass) {
                const auto& src = pass == 0 ? node : holder;
                uint32_t minC = UINT32_MAX, one = 0, none = 0;
                double sum = 0;
                for (uint32_t j = 0; j < K; ++j) {
                    uint32_t n = 0;
                    for (int32_t i : P.members[x]) n += src[i][j];
                    minC = std::min(minC, n);
                    one += n == 1;
                    none += n == 0;
                    sum += n;
                }
                std::fprintf(hold, "%s,%d,%d,%zu,%u,%u,%u,%.3f\n", pass == 0 ? "cellBefore" : "cellAfter",
                             P.cells[x].q, P.cells[x].r, P.members[x].size(), none, one, minC, sum / K);
            }
    }
    return M;
}

}  // namespace

int main(int argc, char* argv[]) {
    Cfg c;
    std::string routesFile = "deploy-routes-s35.csv";
    CommandLine cmd(__FILE__);
    cmd.AddValue("nodes", "nodes CSV from uav-coop-deploy", c.nodesFile);
    cmd.AddValue("routes", "routes CSV from uav-coop-deploy (to check the rebuilt routes)", routesFile);
    cmd.AddValue("bits", "reception bitmaps from uav-coop-pass --bits; {r} = mission", c.bits);
    cmd.AddValue("summary", "summary-cells.csv: when each CL had its cell summary (empty: all at 0)", c.summary);
    cmd.AddValue("K", "chunks in all", c.K);
    cmd.AddValue("files", "files (the K chunks split evenly)", c.files);
    cmd.AddValue("wait", "near-border cells wait this long after their summary, s", c.waitS);
    cmd.AddValue("runs", "missions", c.runs);
    cmd.AddValue("firstRun", "first mission", c.firstRun);
    cmd.AddValue("blank", "cells q:r,q:r that received nothing (scenario test)", c.blank);
    cmd.AddValue("out", "output prefix", c.out);
    cmd.Parse(argc, argv);
    CHECK(c.files >= 1 && c.K % c.files == 0 && c.K <= 65535);

    // ---- the plan: nodes, routes (rebuilt, checked against the CSV), roles ----
    Plan P;
    const Rows nr = ReadCsv(c.nodesFile);
    for (const auto& r : nr) {
        SensorNode s;
        s.id = (uint32_t)std::stoul(r.at("id"));
        s.pos = {std::stod(r.at("x")), std::stod(r.at("y"))};
        s.cell = {std::stoi(r.at("q")), std::stoi(r.at("r"))};
        s.obs = std::stod(r.at("obs")); s.cpu = std::stod(r.at("cpu")); s.comm = std::stod(r.at("comm"));
        s.isCH = r.at("isCH") == "1";
        s.isCL = r.at("isCL") == "1";
        if (s.isCH) P.ch = P.nodes.size();
        P.nodes.push_back(s);
    }
    P.R = BuildRouting(P.nodes, P.ch, c.linkRangeM);
    {
        std::map<std::string, std::string> mainNext;
        for (const auto& r : ReadCsv(routesFile)) mainNext[r.at("id")] = r.at("mainNext");
        for (size_t i = 0; i < P.nodes.size(); ++i) {
            const int32_t nx = P.R.table[i].mainNext;
            CHECK(mainNext.at(std::to_string(P.nodes[i].id)) ==
                  (nx < 0 ? std::string("-1") : std::to_string(P.nodes[nx].id)));
        }
    }
    for (size_t i = 0; i < P.nodes.size(); ++i) {
        auto [it, fresh] = P.ci.insert({P.nodes[i].cell, P.cells.size()});
        if (fresh) { P.cells.push_back(P.nodes[i].cell); P.members.emplace_back(); P.cl.push_back(-1); }
        P.members[it->second].push_back((int32_t)i);
        if (P.nodes[i].isCL) P.cl[it->second] = (int32_t)i;
    }
    const size_t nc = P.cells.size();
    P.chCell = P.ci.at(P.nodes[P.ch].cell);
    P.next.assign(nc, -1);
    P.role.assign(nc, kOther);
    P.border.assign(nc, 0);
    P.upstream.resize(nc);
    P.keepers.resize(nc);
    for (size_t x = 0; x < nc; ++x) {
        CHECK(P.cl[x] >= 0);
        // next cell: the first other cell on the CL's main route
        for (int32_t v = P.cl[x]; v != kNoHop; v = P.R.table[v].mainNext)
            if (P.nodes[v].cell != P.cells[x]) { P.next[x] = (int32_t)P.ci.at(P.nodes[v].cell); break; }
        CHECK((P.next[x] < 0) == (x == P.chCell));
        if (P.next[x] >= 0) CHECK(HexGrid::Distance(P.cells[x], P.cells[P.next[x]]) == 1);
        for (const Hex& h : HexGrid::Neighbours(P.cells[x]))
            if (!P.ci.count(h)) P.border[x] = 1;
        double mean = 0;
        for (int32_t i : P.members[x]) mean += P.nodes[i].Score();
        mean /= P.members[x].size();
        for (int32_t i : P.members[x])
            if (i == P.cl[x] || P.nodes[i].Score() > mean) P.keepers[x].push_back(i);
    }
    for (size_t x = 0; x < nc; ++x)
        if (P.border[x] && P.next[x] >= 0) P.upstream[P.next[x]].push_back(x);
    uint32_t cnt[4] = {}, nk = 0, nb = 0;
    for (size_t x = 0; x < nc; ++x) {
        if (!P.upstream[x].empty()) P.role[x] = P.border[x] ? kWaitBorder : kWaitInner;
        else if (P.border[x]) P.role[x] = kInit;
        cnt[P.role[x]]++;
        nb += P.border[x];
        nk += (uint32_t)P.keepers[x].size();
    }
    std::printf("%zu cells, %u border: %u initiate, %u border cells wait, %u other cells wait, %u neither; "
                "keepers (CL + above-mean) %.1f per cell; %u chunks in %u files; wait %.1f s\n", nc, nb,
                cnt[kInit], cnt[kWaitBorder], cnt[kWaitInner], cnt[kOther], (double)nk / nc, c.K, c.files, c.waitS);

    std::map<std::pair<std::string, std::string>, double> readyAt;   // (run, "q:r") -> s
    if (!c.summary.empty())
        for (const auto& r : ReadCsv(c.summary))
            readyAt[{r.at("run"), r.at("q") + ":" + r.at("r")}] =
                r.at("complete") == "1" ? std::stod(r.at("doneS")) : c.notReadyS;

    FILE* fc = std::fopen((c.out + "-cells.csv").c_str(), "w");
    std::fprintf(fc, "run,q,r,role,readyS,lacks0,lacksEnd,fullS,manifests,forwarded,reverse,supplied,cached,"
                     "received\n");
    FILE* fm = std::fopen((c.out + "-missions.csv").c_str(), "w");
    std::fprintf(fm, "run,cellsLacking0,cellsLackingEnd,borderLacking0,lastS,hopsManifest,hopsData,hopsStore,"
                     "manifestBytes,dup,toCH,chRemainder\n");
    for (uint32_t run = c.firstRun; run < c.firstRun + c.runs; ++run) {
        std::string file = c.bits;
        const size_t at = file.find("{r}");
        if (at != std::string::npos) file.replace(at, 3, std::to_string(run));
        auto node = ReadChunks(file, P.nodes.size(), c.K);
        if (!c.blank.empty()) {
            std::stringstream bs(c.blank);
            std::string tok;
            while (std::getline(bs, tok, ',')) {
                const size_t colon = tok.find(':');
                const Hex h{std::stoi(tok.substr(0, colon)), std::stoi(tok.substr(colon + 1))};
                CHECK(P.ci.count(h));
                for (int32_t i : P.members[P.ci.at(h)]) std::fill(node[i].begin(), node[i].end(), 0);
            }
        }
        std::vector<double> ready(nc, 0.0);
        if (!c.summary.empty())
            for (size_t x = 0; x < nc; ++x)
                ready[x] = readyAt.at({std::to_string(run), std::to_string(P.cells[x].q) + ":" +
                                                                std::to_string(P.cells[x].r)});
        FILE* trace = nullptr;
        if (run == c.firstRun) {
            trace = std::fopen((c.out + "-trace.csv").c_str(), "w");
            std::fprintf(trace, "what,sentS,atS,fq,fr,tq,tr,oq,or,chunks\n");
        }
        FILE* hold = nullptr;
        if (run == c.firstRun) {
            hold = std::fopen((c.out + "-holdings.csv").c_str(), "w");
            // node rows: kind,id,q,r,isCL,isStrong,before,after
            // cell rows: kind,q,r,nodes,chunksNowhere,chunksOneCopy,minCopies,meanCopies
            std::fprintf(hold, "kind,a,b,c,d,e,f,g\n");
        }
        const MissionOut M = RunMission(c, P, node, ready, trace, hold);
        if (trace) std::fclose(trace);
        if (hold) std::fclose(hold);
        uint32_t l0 = 0, l1 = 0, b0 = 0;
        for (size_t x = 0; x < nc; ++x) {
            const CellOut& o = M.cell[x];
            l0 += o.lacks0 > 0;
            l1 += o.lacksEnd > 0;
            b0 += o.lacks0 > 0 && P.border[x];
            std::fprintf(fc, "%u,%d,%d,%d,%.3f,%u,%u,%.3f,%u,%u,%u,%u,%u,%u\n", run, P.cells[x].q, P.cells[x].r,
                         P.role[x], ready[x], o.lacks0, o.lacksEnd, o.fullS, o.manifests, o.forwarded, o.reverse,
                         o.supplied, o.cached, o.received);
        }
        std::fprintf(fm, "%u,%u,%u,%u,%.3f,%llu,%llu,%llu,%llu,%llu,%u,%u\n", run, l0, l1, b0, M.lastS,
                     (unsigned long long)M.hopsManifest, (unsigned long long)M.hopsData,
                     (unsigned long long)M.hopsStore, (unsigned long long)M.manifestBytes,
                     (unsigned long long)M.dup, M.toCH, M.chRemainder);
        if (run == c.firstRun || run % 20 == 0)
            std::printf("  mission %u: cells lacking %u -> %u (border %u); last delivery %.2f s; frame-hops "
                        "manifest %llu, data %llu, store %llu\n", run, l0, l1, b0, M.lastS,
                        (unsigned long long)M.hopsManifest, (unsigned long long)M.hopsData,
                        (unsigned long long)M.hopsStore);
    }
    std::fclose(fc);
    std::fclose(fm);
    std::printf("%u CHECKS PASSED\n", g_checks);
    return 0;
}
