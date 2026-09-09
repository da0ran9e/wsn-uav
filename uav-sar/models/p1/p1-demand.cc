#include "p1-demand.h"

#include <algorithm>
#include <cmath>

namespace ns3::uavsar::p1 {

DoseModel::DoseModel() : m_g(kGTableBins, 0.0) {
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

double DoseModel::Prx(double d) const {
    return 1.0 / (1.0 + std::exp((d - kPrxD50M) / kPrxWidth));
}

double DoseModel::G(double b) const {
    if (b <= 0.0) return m_g.front();
    if (b >= kGmaxOffsetM) return 0.0;
    const double db = kGmaxOffsetM / (kGTableBins - 1);
    const double t = b / db;
    const size_t i = (size_t)t;
    return m_g[i] * (1.0 - (t - i)) + m_g[i + 1] * (t - i);
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
        d.row = c.row;
        d.x = c.cx;
        d.y = c.cy;
        d.offsetM = c.headOffsetM;
        if (c.cls != CellClass::SERVED) { out[cid] = d; continue; }
        const auto hi = byId.find(c.head);
        const double info = hi != byId.end() ? hi->second->Information() : 1.0;
        // P0.6, two stages: how many FILES, then how much DOSE to collect them.
        d.files = FilesNeeded(info);
        d.theta = DoseBytes(d.files);
        out[cid] = d;
    }
    return out;
}

double ServiceCost(Demand& d, const DoseModel& dose, double a, double rho) {
    d.weaveS = 0.0;
    d.doseS = 0.0;
    d.orbits = 0;
    d.serveMps = 0.0;
    d.feasible = true;
    if (d.theta <= 0.0) return 0.0;

    // Following the head costs the same whatever the dose demands.
    d.weaveS = WeaveExtraM(d.offsetM, a) / kCruiseMps;

    const double g = dose.G(DoseAtHead(d));
    if (g <= 0.0) {                       // F3: unservable at any speed
        d.feasible = false;
        return d.weaveS;
    }

    const double vN = kRefTxBytesPerS * g / d.theta;   // T0.3
    if (vN >= kMinMps) {
        // One pass suffices. Charge only the time LOST by holding a lower speed
        // over one cell pitch -- the pass was going to happen anyway.
        const double v = std::min(vN, kCruiseMps);
        d.serveMps = v;
        d.doseS = a * std::max(0.0, 1.0 / v - 1.0 / kCruiseMps);
        return d.CostS();
    }

    // One pass is not enough even at stall: the aircraft has to come back round.
    const double loopS = 2.0 * M_PI * rho / kMinMps;
    const double perPass = kRefTxBytesPerS * g / kMinMps;
    d.orbits = (uint32_t)std::max(1.0, std::ceil(d.theta / std::max(1.0, perPass)) - 1.0);
    d.doseS = d.orbits * loopS + a * (1.0 / kMinMps - 1.0 / kCruiseMps);
    return d.CostS();
}

}  // namespace ns3::uavsar::p1
