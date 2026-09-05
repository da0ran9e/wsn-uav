#include "p1-demand.h"

#include <algorithm>
#include <cmath>

namespace ns3::uavsar::p1 {

DoseModel::DoseModel() : m_g(kGTableBins, 0.0) {
    // G(b) = integral along the track of p(sqrt(b^2 + x^2)). Simpson over the
    // positive half, doubled: the integrand is even in x.
    const double db = kGmaxOffsetM / (kGTableBins - 1);
    const double xmax = 4.0 * kGmaxOffsetM;
    const int n = 4000;                    // even, for Simpson
    const double h = xmax / n;
    for (uint32_t i = 0; i < kGTableBins; ++i) {
        const double b = i * db;
        double s = Prx(b);
        for (int k = 1; k < n; ++k) {
            const double x = k * h;
            s += (k % 2 ? 4.0 : 2.0) * Prx(std::hypot(b, x));
        }
        s += Prx(std::hypot(b, xmax));
        m_g[i] = 2.0 * s * h / 3.0;
    }
}

double DoseModel::Prx(double distanceM) const {
    return 1.0 / (1.0 + std::exp((distanceM - kPrxD50M) / kPrxWidth));
}

double DoseModel::G(double offsetM) const {
    if (offsetM <= 0.0) return m_g.front();
    if (offsetM >= kGmaxOffsetM) return 0.0;
    const double db = kGmaxOffsetM / (kGTableBins - 1);
    const double t = offsetM / db;
    const size_t i = (size_t)t;
    const double f = t - i;
    return m_g[i] * (1.0 - f) + m_g[i + 1] * f;
}

double DoseModel::InteractionLength(double offsetM) const {
    const double p = Prx(offsetM);
    return p > 1e-9 ? G(offsetM) / p : 0.0;
}

std::map<int32_t, Demand> BuildDemands(const CellPlan& plan,
                                       const std::vector<Node>& nodes) {
    std::map<uint32_t, const Node*> byId;
    for (const Node& n : nodes) byId[n.id] = &n;

    std::map<int32_t, Demand> out;
    for (const auto& [cid, c] : plan.cells) {
        Demand d;
        d.cellId = cid;
        d.cls = c.cls;
        d.x = c.cx;
        d.y = c.cy;
        if (c.cls != CellClass::SERVED) {
            // No camera, so no head, so nothing to match. Reference bytes here
            // buy nothing at any price -- the cell leaves the routing problem.
            d.theta = 0.0;
        } else {
            const auto li = byId.find(c.leader);
            const double info = li != byId.end() ? li->second->Information() : 1.0;
            // No tiering: at planning time there is nothing to tier ON. The
            // only heterogeneity is capability -- feature quality AND matcher
            // strength, both of which raise the Chernoff information per byte.
            d.theta = ThetaFullBytes() / info;
        }
        out[cid] = d;
    }
    return out;
}

double OnePassSpeed(double theta, double offsetM, const DoseModel& dose) {
    if (theta <= 0.0) return kMaxMps;
    const double g = dose.G(offsetM);
    return g > 0.0 ? kRefTxBytesPerS * g / theta : 0.0;
}

double ServiceCost(Demand& d, double offsetM, const DoseModel& dose) {
    d.penaltyS = 0.0;
    d.serveMps = 0.0;
    d.orbits = 0;
    if (d.theta <= 0.0) return 0.0;

    const double vOk = OnePassSpeed(d.theta, offsetM, dose);
    if (vOk >= kMinMps) {
        // One pass is enough. Only the time LOST to holding a lower speed is
        // charged: the transit was going to happen anyway, and charging it here
        // would double-count it against the routing cost.
        const double v = std::min(vOk, kCruiseMps);
        d.serveMps = v;
        d.penaltyS = dose.InteractionLength(offsetM) * (1.0 / v - 1.0 / kCruiseMps);
        return d.penaltyS;
    }

    // One pass can never be enough, even at stall. The aircraft has to come
    // back round: a minimum-radius orbit at the slowest speed it can hold --
    // which is also the tightest circle it can fly, so the orbit sits as close
    // to the cell as the airframe allows.
    const double rho = TurnRadiusM(kMinMps);
    const double loopS = 2.0 * M_PI * rho / kMinMps;
    const double perLoop = kRefTxBytesPerS * loopS * dose.Prx(rho);
    d.orbits = perLoop > 0.0 ? (uint32_t)std::ceil(d.theta / perLoop) : 0u;
    d.penaltyS = d.orbits * loopS;
    return d.penaltyS;
}

}  // namespace ns3::uavsar::p1
