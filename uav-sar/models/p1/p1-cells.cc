#include "p1-cells.h"

#include <algorithm>
#include <cmath>
#include <deque>
#include <limits>

namespace ns3::uavsar::p1 {

std::vector<int32_t> CellPlan::ServedCells() const {
    std::vector<int32_t> out;
    for (const auto& [cid, c] : cells)
        if (c.cls == CellClass::SERVED) out.push_back(cid);
    return out;
}

std::vector<int32_t> CellPlan::Rows() const {
    std::vector<int32_t> out;
    for (const auto& [r, v] : cellsByRow) out.push_back(r);
    return out;
}

CellPlan BuildCells(const std::vector<Node>& nodes, const Field& field,
                    double rc, double groundRangeM, double rho,
                    Election rule, uint32_t seed) {
    CellPlan plan;
    plan.field = field;
    plan.cellRadiusM = rc;
    plan.cellPitchM = rc * std::sqrt(3.0);
    plan.rowPitchM = hex::RowPitch(rc);
    plan.maxOffsetM = MaxOffsetM(rc, rho);

    // --- P0.2: tile in the ROW FRAME so one row family lies along psi -------
    std::map<std::pair<int32_t, int32_t>, int32_t> byAxial;
    std::map<uint32_t, const Node*> byId;
    for (const Node& n : nodes) {
        byId[n.id] = &n;
        double u, w;
        field.ToRowFrame(n.x, n.y, u, w);
        int32_t q, r;
        // The hex maths runs in the row frame, so `r` IS the row index: the
        // pointy-top convention puts row centres at w = 1.5 R_c * r, which is
        // exactly the row spacing h. Nothing has to be recovered afterwards.
        hex::WorldToAxial(u, w, rc, q, r);
        auto key = std::make_pair(q, r);
        auto it = byAxial.find(key);
        if (it == byAxial.end()) {
            const int32_t cid = (int32_t)plan.cells.size();
            byAxial[key] = cid;
            Cell c;
            c.id = cid;
            c.q = q;
            c.r = r;
            c.row = r;
            double cu, cw;
            hex::AxialToCentre(q, r, rc, cu, cw);
            field.FromRowFrame(cu, cw, c.cx, c.cy);
            plan.cells[cid] = c;
            it = byAxial.find(key);
        }
        // --- P0.4: the node's own offset from its row line ------------------
        const double rowW = plan.RowLineW(r);
        CellMember m;
        m.id = n.id;
        m.offsetM = std::fabs(w - rowW);
        m.eligible = n.HasCamera() && m.offsetM <= plan.maxOffsetM;
        plan.cells[it->second].members.push_back(m);
        plan.cellOfNode[n.id] = it->second;
    }

    const double a = plan.cellPitchM;

    for (auto& [cid, c] : plan.cells) {
        // --- P0.5: elect, with the flight cost inside the objective ---------
        double best = std::numeric_limits<double>::infinity();
        uint32_t bestId = 0;
        bool found = false;
        uint32_t rnd = seed ^ (uint32_t)(cid * 2654435761u);
        for (const CellMember& m : c.members) {
            const Node& n = *byId[m.id];
            if (n.HasCamera()) c.cameras++;
            if (!m.eligible) continue;            // F1 / I2: hard constraint
            c.eligible++;
            // Capability cost in SECONDS: how long the aircraft must spend
            // over this head to deliver what its information rate demands.
            const double capS =
                DoseBytes(FilesNeeded(n.Information())) / kRefTxBytesPerS;
            // Position cost in SECONDS: the extra path length of weaving out to
            // it, divided by cruise. Same unit, so no weight to choose.
            const double posS = WeaveExtraM(m.offsetM, a) / kCruiseMps;
            double score = 0.0;
            switch (rule) {
                case Election::CAPABILITY: score = capS; break;
                case Election::CENTROID:
                    score = std::hypot(n.x - c.cx, n.y - c.cy);
                    break;
                case Election::RANDOM:
                    rnd = rnd * 1664525u + 1013904223u;
                    score = (double)rnd / 4294967296.0;
                    break;
                default: score = capS + posS;     // P0.5
            }
            if (score < best) { best = score; bestId = m.id; found = true; }
        }
        c.cls = found ? CellClass::SERVED : CellClass::BARREN;
        c.hasHead = found;
        c.head = bestId;
        if (found) {
            for (const CellMember& m : c.members)
                if (m.id == bestId) c.headOffsetM = m.offsetM;
            const Node& hn = *byId[bestId];
            // Always report the P0.5 objective of whoever was elected, whatever
            // rule chose them -- otherwise the rules cannot be compared.
            c.headScoreS = DoseBytes(FilesNeeded(hn.Information())) / kRefTxBytesPerS
                         + WeaveExtraM(c.headOffsetM, a) / kCruiseMps;
            plan.nServed++;
        } else {
            plan.nBarren++;
            // A cell with cameras but none of them reachable is an F1 failure,
            // which is a different problem from a cell with no camera at all --
            // and the spec has no branch for it, so it must at least be counted.
            if (c.cameras > 0) plan.nInfeasible++;
        }
        plan.cellsByRow[c.row].push_back(cid);

        // --- intra-cell tree, rooted at the elected head --------------------
        if (!c.hasHead) { c.unreachable = (uint32_t)c.members.size(); continue; }
        std::map<uint32_t, size_t> slot;
        for (size_t i = 0; i < c.members.size(); ++i) slot[c.members[i].id] = i;
        c.members[slot[c.head]].hops = 0;
        c.members[slot[c.head]].parent = -1;
        std::deque<uint32_t> q2{c.head};
        while (!q2.empty()) {
            const uint32_t cur = q2.front();
            q2.pop_front();
            const Node& na = *byId[cur];
            const uint32_t d = c.members[slot[cur]].hops;
            for (CellMember& m : c.members) {
                if (m.hops != 0xFFFFFFFFu) continue;
                const Node& nb = *byId[m.id];
                if (std::hypot(na.x - nb.x, na.y - nb.y) > groundRangeM) continue;
                m.hops = d + 1;
                m.parent = (int32_t)cur;
                q2.push_back(m.id);
            }
        }
        for (const CellMember& m : c.members)
            if (m.hops == 0xFFFFFFFFu) c.unreachable++;
    }
    return plan;
}

double HeadScoreCv(const CellPlan& plan) {
    double s = 0, s2 = 0;
    uint32_t n = 0;
    for (const auto& [cid, c] : plan.cells) {
        if (!c.hasHead) continue;
        s += c.headScoreS;
        s2 += c.headScoreS * c.headScoreS;
        n++;
    }
    if (!n) return 0.0;
    const double mean = s / n;
    if (mean <= 0.0) return 0.0;
    return std::sqrt(std::max(0.0, s2 / n - mean * mean)) / mean;
}

}  // namespace ns3::uavsar::p1
