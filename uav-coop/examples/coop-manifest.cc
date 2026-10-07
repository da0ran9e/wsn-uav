// Step 5, first trial: the base manifest phase between cells (docs/MANIFEST-vi.md),
// at the LOGIC level -- who sends what to whom, how manifests are cut, where copies
// are kept. No radio yet: costs are counted in frame-hops and turned into an
// optimistic time (one 10 ms slot per frame-hop, no loss, no contention).
//
// State: each cell's union of chunks after the UAV pass (bitmaps of uav-coop-pass
// --bits, folded onto K chunks, split into F files). A cell is ready when its CL has
// the intra-cell summary (summary-cells.csv of the same mission).
//
// Roles, from the plan: border cells (an edge on the cluster's outline), near-border
// cells (the next cell of some border cell, not border themselves), the rest.
//   border, ready, lacking         -> MANIFEST of its state to its next cell
//   near-border, ready + wait,     -> REVERSE manifest to each border cell that should
//     lacking, not reached by one     have sent it one and did not
//   any cell a manifest reaches    -> sends back what it holds of what the origin
//                                     lacks, marks those as held, passes the rest on to
//                                     its own next cell; stops when nothing is lacking
//                                     or at the CH's cell (the rest: secondary phase)
//   any cell data passes through   -> keeps a copy of what it lacks
//   a border cell a reverse        -> sends what it holds of what the sender lacks;
//     manifest reaches               if it lacks anything itself, it is now triggered
// Received chunks are stored at the CL and the strong nodes of the cell.
//
//   uav-coop-manifest --nodes=deploy-nodes-s35.csv --bits=bits-r{r}.bin \
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

enum Role { kBorder = 0, kNear = 1, kInner = 2 };

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
    std::vector<std::vector<int32_t>> keepers;   // CL + nodes above the cell's mean strength
    size_t chCell = 0;
};

// In-cell multicast from node e to the cell's keepers: nodes on the union of the
// shortest in-cell paths, e excluded (= frame-hops if each forwards once).
uint32_t StoreCost(const Plan& P, size_t cell, int32_t e) {
    std::set<int32_t> mem(P.members[cell].begin(), P.members[cell].end());
    std::map<int32_t, int32_t> parent{{e, -1}};
    std::deque<int32_t> q{e};
    while (!q.empty()) {
        const int32_t u = q.front();
        q.pop_front();
        for (int32_t v : P.R.links[u])
            if (mem.count(v) && !parent.count(v)) { parent[v] = u; q.push_back(v); }
    }
    std::set<int32_t> used;
    for (int32_t k : P.keepers[cell]) {
        CHECK(parent.count(k));   // the cell is in one piece (routing's bridges)
        for (int32_t v = k; v != e; v = parent.at(v)) used.insert(v);
    }
    return (uint32_t)used.size();
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
                      const std::vector<double>& ready) {
    const size_t nc = P.cells.size();
    const uint32_t K = c.K;
    MissionOut M;
    M.cell.resize(nc);
    std::vector<std::vector<uint8_t>> have(nc, std::vector<uint8_t>(K, 0));
    for (size_t x = 0; x < nc; ++x)
        for (int32_t i : P.members[x])
            for (uint32_t j = 0; j < K; ++j) have[x][j] |= node[i][j];
    std::vector<std::vector<uint8_t>> holder = node;   // node-level, grows at the keepers
    auto lacking = [&](size_t x) { return (uint32_t)std::count(have[x].begin(), have[x].end(), 0); };
    for (size_t x = 0; x < nc; ++x) {
        M.cell[x].lacks0 = lacking(x);
        if (M.cell[x].lacks0 == 0) M.cell[x].fullS = 0;
    }
    std::vector<uint8_t> sent(nc, 0);            // a border cell has sent its manifest
    std::vector<std::set<size_t>> heardFrom(nc);  // near-border: manifests received from

    // Events: (time, seq, kind, ...). Manifests carry the origin's state as known
    // along the way ("held"), the path so far, and the TTL.
    struct Ev {
        double t;
        uint64_t seq;
        int kind;           // 0 trigger border, 1 near-border check, 2 manifest at cell, 3 reverse at border
        size_t at;
        size_t origin;
        std::vector<size_t> path;          // cells from the origin to `at`
        std::vector<uint8_t> held;         // the origin's state as the manifest says
        uint32_t ttl;
        int32_t entry;                     // node it arrives at
    };
    auto cmp = [](const Ev& a, const Ev& b) { return a.t != b.t ? a.t > b.t : a.seq > b.seq; };
    std::priority_queue<Ev, std::vector<Ev>, decltype(cmp)> pq(cmp);
    uint64_t seqNo = 0;
    for (size_t x = 0; x < nc; ++x) {
        if (P.role[x] == kBorder) pq.push({ready[x], seqNo++, 0, x, x, {}, {}, 0, -1});
        if (P.role[x] == kNear) pq.push({ready[x] + c.waitS, seqNo++, 1, x, x, {}, {}, 0, -1});
    }
    const double slot = c.slotS;
    auto markFull = [&](size_t x, double t) {
        if (M.cell[x].fullS < 0 && lacking(x) == 0) M.cell[x].fullS = t;
    };
    // Chunks js go from cell `from` back along `back` (cells, from's neighbour first,
    // ending at the destination). Every cell on the way keeps what it lacks; the
    // destination keeps them all. Pipelined: the last chunk arrives (hops + m - 1)
    // slots after t.
    auto sendBack = [&](double t, size_t from, const std::vector<size_t>& back, const std::vector<uint32_t>& js) {
        if (js.empty() || back.empty()) return;
        const uint32_t m = (uint32_t)js.size();
        // the holder nearest to the gateway toward the first cell, per chunk
        uint64_t hops = 0;
        uint32_t firstLeg = 0;   // the farthest holder, for the timing
        int32_t entry = -1;
        for (uint32_t j : js) {
            int32_t best = -1;
            uint32_t bh = kNoRoute;
            for (int32_t i : P.members[from])
                if (holder[i][j] && P.R.table[i].toCell.at(P.cells[back[0]]).hops < bh) {
                    bh = P.R.table[i].toCell.at(P.cells[back[0]]).hops;
                    best = i;
                }
            CHECK(best >= 0);   // the cell holds it, so some node does
            hops += bh;
            firstLeg = std::max(firstLeg, bh);
        }
        M.cell[from].supplied += m;
        const Gateway& g0 = P.R.gateway.at({P.cells[from], P.cells[back[0]]});
        entry = g0.b;
        uint64_t pathHops = 0;   // per chunk, for the timing
        for (size_t k = 0; k < back.size(); ++k) {
            const size_t x = back[k];
            const bool last = k + 1 == back.size();
            uint32_t kept = 0;
            for (uint32_t j : js)
                if (!have[x][j]) {
                    have[x][j] = 1;
                    kept++;
                    for (int32_t i : P.keepers[x]) holder[i][j] = 1;
                } else if (last) {
                    M.dup++;
                }
            const double tArr = t + (double)(firstLeg + pathHops + m - 1) * slot;
            if (kept) {
                (last ? M.cell[x].received : M.cell[x].cached) += kept;
                M.hopsStore += (uint64_t)kept * StoreCost(P, x, entry);
                markFull(x, tArr);
                M.lastS = std::max(M.lastS, tArr);
            }
            if (!last) {   // through x toward the next cell back
                const Gateway& g = P.R.gateway.at({P.cells[x], P.cells[back[k + 1]]});
                const uint32_t h = P.R.table[entry].toCell.at(P.cells[back[k + 1]]).hops;
                CHECK(h >= 1);
                hops += (uint64_t)m * h;
                pathHops += h;
                entry = g.b;
            }
        }
        M.hopsData += hops;
    };
    auto forward = [&](double t, size_t from, int32_t fromNode, size_t origin, std::vector<size_t> path,
                       const std::vector<uint8_t>& held, uint32_t ttl) {
        const int32_t nx = P.next[from];
        if (nx < 0) { M.toCH++; M.chRemainder += (uint32_t)std::count(held.begin(), held.end(), 0); return; }
        if (ttl == 0) return;
        const uint32_t h = P.R.table[fromNode].toCell.at(P.cells[nx]).hops;
        const uint32_t bytes = ManifestBytes(held, c.files);
        const uint32_t frames = (bytes + kFramePayload - 1) / kFramePayload;
        M.hopsManifest += (uint64_t)frames * h;
        M.manifestBytes += bytes;
        path.push_back((size_t)nx);
        const Gateway& g = P.R.gateway.at({P.cells[from], P.cells[nx]});
        pq.push({t + (h + frames - 1) * slot, seqNo++, 2, (size_t)nx, origin, path, held, ttl - 1, g.b});
    };

    while (!pq.empty()) {
        Ev e = pq.top();
        pq.pop();
        const size_t x = e.at;
        if (e.kind == 0) {   // a border cell is ready
            if (sent[x] || lacking(x) == 0) continue;
            // A cell that received nothing is never triggered (the trigger is the end of
            // reception); only a reverse manifest wakes it.
            if (lacking(x) == K) continue;
            sent[x] = 1;
            M.cell[x].manifests++;
            forward(e.t, x, P.cl[x], x, {x}, have[x], c.ttl);
        } else if (e.kind == 1) {   // a near-border cell checks
            if (lacking(x) == 0) continue;
            for (size_t b = 0; b < nc; ++b) {
                if (P.role[b] != kBorder || P.next[b] != (int32_t)x || heardFrom[x].count(b)) continue;
                const uint32_t h = P.R.table[P.cl[x]].toCell.at(P.cells[b]).hops;
                const uint32_t bytes = ManifestBytes(have[x], c.files);
                const uint32_t frames = (bytes + kFramePayload - 1) / kFramePayload;
                M.hopsManifest += (uint64_t)frames * h;
                M.manifestBytes += bytes;
                M.cell[x].reverse++;
                const Gateway& g = P.R.gateway.at({P.cells[x], P.cells[b]});
                pq.push({e.t + (h + frames - 1) * slot, seqNo++, 3, b, x, {x, b}, have[x], 1, g.b});
            }
        } else if (e.kind == 2) {   // a manifest reaches cell x
            if (P.role[x] == kNear) heardFrom[x].insert(e.path[e.path.size() - 2]);
            M.cell[x].forwarded++;
            // to the CL, which knows the cell's state
            M.hopsManifest += (uint64_t)P.R.table[e.entry].toCL.hops *
                              ((ManifestBytes(e.held, c.files) + kFramePayload - 1) / kFramePayload);
            std::vector<uint32_t> give;
            for (uint32_t j = 0; j < K; ++j)
                if (!e.held[j] && have[x][j]) give.push_back(j);
            std::vector<uint8_t> held = e.held;
            for (uint32_t j : give) held[j] = 1;   // cut: "A4689" -> "AB89"
            std::vector<size_t> back(e.path.rbegin() + 1, e.path.rend());
            sendBack(e.t, x, back, give);
            if (std::count(held.begin(), held.end(), 0) == 0) continue;
            forward(e.t, x, P.cl[x], e.origin, e.path, held, e.ttl);
        } else {   // a reverse manifest reaches border cell x from near-border e.origin
            std::vector<uint32_t> give;
            for (uint32_t j = 0; j < K; ++j)
                if (!e.held[j] && have[x][j]) give.push_back(j);
            sendBack(e.t, x, {e.origin}, give);
            if (!sent[x] && lacking(x) > 0) {   // it understands: it must send its own
                sent[x] = 1;
                M.cell[x].manifests++;
                forward(e.t, x, P.cl[x], x, {x}, have[x], c.ttl);
            }
        }
    }
    for (size_t x = 0; x < nc; ++x) {
        M.cell[x].lacksEnd = lacking(x);
        CHECK(M.cell[x].lacksEnd <= M.cell[x].lacks0);
        for (int32_t i : P.members[x])            // node-level holdings stay inside the cell's
            for (uint32_t j = 0; j < K; ++j) CHECK(!holder[i][j] || have[x][j]);
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
    P.role.assign(nc, kInner);
    P.keepers.resize(nc);
    for (size_t x = 0; x < nc; ++x) {
        CHECK(P.cl[x] >= 0);
        // next cell: the first other cell on the CL's main route
        for (int32_t v = P.cl[x]; v != kNoHop; v = P.R.table[v].mainNext)
            if (P.nodes[v].cell != P.cells[x]) { P.next[x] = (int32_t)P.ci.at(P.nodes[v].cell); break; }
        CHECK((P.next[x] < 0) == (x == P.chCell));
        if (P.next[x] >= 0) CHECK(HexGrid::Distance(P.cells[x], P.cells[P.next[x]]) == 1);
        for (const Hex& h : HexGrid::Neighbours(P.cells[x]))
            if (!P.ci.count(h)) P.role[x] = kBorder;
        double mean = 0;
        for (int32_t i : P.members[x]) mean += P.nodes[i].Score();
        mean /= P.members[x].size();
        for (int32_t i : P.members[x])
            if (i == P.cl[x] || P.nodes[i].Score() > mean) P.keepers[x].push_back(i);
    }
    for (size_t x = 0; x < nc; ++x)
        if (P.role[x] == kBorder && P.next[x] >= 0 && P.role[P.next[x]] == kInner) P.role[P.next[x]] = kNear;
    uint32_t nb = 0, nn = 0, nk = 0;
    for (size_t x = 0; x < nc; ++x) {
        nb += P.role[x] == kBorder;
        nn += P.role[x] == kNear;
        nk += (uint32_t)P.keepers[x].size();
    }
    std::printf("%zu cells: %u border, %u near-border, %zu other; keepers (CL + above-mean) %u, %.1f per "
                "cell; %u chunks in %u files; near-border wait %.1f s\n", nc, nb, nn, nc - nb - nn, nk,
                (double)nk / nc, c.K, c.files, c.waitS);

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
        const MissionOut M = RunMission(c, P, node, ready);
        uint32_t l0 = 0, l1 = 0, b0 = 0;
        for (size_t x = 0; x < nc; ++x) {
            const CellOut& o = M.cell[x];
            l0 += o.lacks0 > 0;
            l1 += o.lacksEnd > 0;
            b0 += o.lacks0 > 0 && P.role[x] == kBorder;
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
