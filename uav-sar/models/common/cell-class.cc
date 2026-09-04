#include "cell-class.h"

#include "phase1-params.h"

#include <cmath>

namespace ns3::uavsar {

const char* CellClassName(CellClass c) {
    switch (c) {
        case CellClass::A: return "A";
        case CellClass::B: return "B";
        default:           return "C";
    }
}

namespace {

// Can this node run the reference match at all?
bool CanDiscriminate(const NodeCapability& c) {
    return c.modality == p1::kReferenceModality && c.obs > 0.0 &&
           c.cpu >= kCpuConfirmMin;
}

double ElectScore(const NodeCapability& c) {
    // Energy carries weight 0 today (see phase1-params.h); the term is written
    // out anyway so that giving it a weight later is a one-line change and not
    // a re-derivation.
    return p1::kElectWCompute * c.cpu +
           p1::kElectWRadio   * c.radioDuty +
           p1::kElectWEnergy  * 1.0;
}

}  // namespace

CellRolePlan BuildCellRoles(const CellGridPlan& grid,
                            const std::map<uint32_t, NodeCapability>& caps) {
    CellRolePlan out;
    for (const auto& [cid, cell] : grid.cells) {
        CellRole r;
        r.cellId = cid;
        r.members = (uint32_t)cell.members.size();

        // Pass 1: the discriminating candidates. Only these can make the cell
        // class A, so the election runs over them FIRST and falls back only if
        // there are none.
        double bestDisc = -1.0, bestAny = -1.0;
        uint32_t discId = 0, anyId = 0;
        bool hasDisc = false;
        for (uint32_t nid : cell.members) {
            auto it = caps.find(nid);
            if (it == caps.end()) continue;
            const NodeCapability& c = it->second;
            if (Images(c.modality)) r.imagingMembers++;
            const double s = ElectScore(c);
            if (s > bestAny) { bestAny = s; anyId = nid; }
            if (CanDiscriminate(c) && s > bestDisc) { bestDisc = s; discId = nid; hasDisc = true; }
        }

        if (hasDisc) {
            r.cls = CellClass::A;
            r.leaderId = discId;
            r.matcherId = discId;
            r.leaderScore = bestDisc;
        } else if (r.imagingMembers > 0) {
            // Detects, never discriminates. It still needs a leader to carry its
            // Tier-1 report out, so the election still runs -- just over
            // everyone, since modality no longer filters anything useful.
            r.cls = CellClass::B;
            r.leaderId = anyId;
            r.leaderScore = std::max(0.0, bestAny);
        } else {
            r.cls = CellClass::C;
            r.leaderId = anyId;
            r.leaderScore = std::max(0.0, bestAny);
        }

        // Hops from the elected leader to the matcher over the substrate's own
        // tree. The substrate's tree is rooted at ITS leader, so this is exact
        // only when the two coincide; otherwise it is the matcher's depth, which
        // is the right order of magnitude and the quantity T_local(R_c) needs.
        if (r.matcherId != 0) {
            auto ni = grid.nodes.find(r.matcherId);
            if (ni != grid.nodes.end() && ni->second.hopToLeader != 0xFFFFFFFFu)
                r.matcherHops = ni->second.hopToLeader;
        }

        switch (r.cls) {
            case CellClass::A: out.nA++; break;
            case CellClass::B: out.nB++; break;
            default:           out.nC++; break;
        }
        out.roles[cid] = r;
    }
    return out;
}

double LeaderScoreCv(const CellRolePlan& plan) {
    if (plan.roles.empty()) return 0.0;
    double s = 0, s2 = 0; uint32_t n = 0;
    for (const auto& [cid, r] : plan.roles) { s += r.leaderScore; s2 += r.leaderScore * r.leaderScore; n++; }
    const double mean = s / n;
    if (mean <= 0.0) return 0.0;
    const double var = std::max(0.0, s2 / n - mean * mean);
    return std::sqrt(var) / mean;
}

}  // namespace ns3::uavsar
