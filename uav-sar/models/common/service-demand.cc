#include "service-demand.h"

#include "phase1-params.h"

#include <algorithm>
#include <cmath>

namespace ns3::uavsar {

DosePerPass::DosePerPass() : m_g(p1::kGTableBins, 0.0) {
    // G(b) = integral over the along-track axis of p(sqrt(b^2 + x^2)).
    // Integrated by Simpson out to where p has died; the integrand is even, so
    // only the positive half is summed and doubled.
    const double db = p1::kGmaxOffsetM / (p1::kGTableBins - 1);
    const double xmax = 4.0 * p1::kGmaxOffsetM;
    const int n = 4000;                      // even, for Simpson
    const double h = xmax / n;
    for (uint32_t i = 0; i < p1::kGTableBins; ++i) {
        const double b = i * db;
        double s = Prx(b);                   // x = 0
        for (int k = 1; k < n; ++k) {
            const double x = k * h;
            s += (k % 2 ? 4.0 : 2.0) * Prx(std::hypot(b, x));
        }
        s += Prx(std::hypot(b, xmax));
        m_g[i] = 2.0 * s * h / 3.0;
    }
}

double DosePerPass::Prx(double distanceM) const {
    return 1.0 / (1.0 + std::exp((distanceM - p1::kPrxD50M) / p1::kPrxWidth));
}

double DosePerPass::G(double offsetM) const {
    if (offsetM <= 0.0) return m_g.front();
    if (offsetM >= p1::kGmaxOffsetM) return 0.0;
    const double db = p1::kGmaxOffsetM / (p1::kGTableBins - 1);
    const double t = offsetM / db;
    const size_t i = (size_t)t;
    const double f = t - i;
    return m_g[i] * (1.0 - f) + m_g[i + 1] * f;
}

double DosePerPass::InteractionLength(double offsetM) const {
    const double p = Prx(offsetM);
    return p > 1e-9 ? G(offsetM) / p : 0.0;
}

std::map<int32_t, CellDemand>
BuildDemands(const CellGridPlan& grid, const CellRolePlan& roles,
             const Tier1Result& tier1,
             const std::map<uint32_t, NodeCapability>& caps) {
    std::map<int32_t, CellDemand> out;
    for (const auto& [cid, role] : roles.roles) {
        CellDemand d;
        d.cellId = cid;
        d.cls = role.cls;
        auto ci = grid.cells.find(cid);
        if (ci != grid.cells.end()) { d.x = ci->second.centerX; d.y = ci->second.centerY; }

        auto ti = tier1.cells.find(cid);
        if (ti != tier1.cells.end()) { d.suspect = ti->second.suspect; d.weight = ti->second.weight; }

        if (role.cls != CellClass::A) {
            // B can detect but never discriminate; C does neither. Reference
            // bytes spent here buy nothing, at any price. This is where the
            // network's heterogeneity first removes work from the aircraft.
            d.theta = 0.0;
        } else {
            // theta ~ 1 / I_n : a better sensor needs LESS reference to settle
            // the same question. This is what turns "the network is
            // heterogeneous" from an adjective into a term in the objective.
            // TODO(param): I_n is standing in as the matcher's obs. The Chernoff
            // derivation gives the real form.
            double info = 1.0;
            auto capIt = caps.find(role.matcherId);
            if (capIt != caps.end()) info = std::max(0.05, capIt->second.obs);
            const double full = p1::kThetaFullBytes / info;
            d.theta = d.suspect ? full : full * p1::kThetaHedgeFrac;
        }
        out[cid] = d;
    }
    return out;
}

double ServiceCost(CellDemand& d, double offsetM, const DosePerPass& dose) {
    d.servePenaltyS = 0.0;
    d.serveSpeedMps = 0.0;
    d.loiterLoops = 0;
    if (d.theta <= 0.0) return 0.0;

    const double g = dose.G(offsetM);
    // Fastest speed at which ONE pass still delivers theta.
    const double vOk = g > 0.0 ? p1::kRefTxBytesPerS * g / d.theta : 0.0;

    if (vOk >= p1::kMinMps) {
        // One pass is enough. The cost is only the time LOST by holding a lower
        // speed over the interaction length -- flying past was going to happen
        // anyway, so the transit itself is not charged here.
        const double v = std::min(vOk, p1::kCruiseMps);
        d.serveSpeedMps = v;
        const double L = dose.InteractionLength(offsetM);
        d.servePenaltyS = L * (1.0 / v - 1.0 / p1::kCruiseMps);
        return d.servePenaltyS;
    }

    // One pass can never be enough, even at stall. The aircraft has to come
    // back round: a minimum-radius orbit centred on the cell, at the slowest
    // speed it can hold -- which is also the tightest circle it can fly, so the
    // orbit sits as close to the cell as the airframe allows.
    const double rho = p1::TurnRadiusM(p1::kMinMps);
    const double loopS = 2.0 * M_PI * rho / p1::kMinMps;
    const double perLoop = p1::kRefTxBytesPerS * loopS * dose.Prx(rho);
    d.serveSpeedMps = 0.0;
    d.loiterLoops = perLoop > 0.0 ? (uint32_t)std::ceil(d.theta / perLoop) : 0u;
    d.servePenaltyS = d.loiterLoops * loopS;
    return d.servePenaltyS;
}

}  // namespace ns3::uavsar
