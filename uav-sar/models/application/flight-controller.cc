#include "flight-controller.h"

#include "ns3/constant-velocity-mobility-model.h"

#include <array>
#include <cmath>

namespace ns3::uavsar {

using namespace ns3;

void FlightController::AttachTo(Ptr<Node> node) {
    m_node = node;
    Apply();
}

void FlightController::Forward(double speedMps) { m_speed = speedMps; Apply(); }
bool FlightController::EscapeExists(double px, double py, double headingDeg) const {
    // Can the aircraft still peel away without entering anything?
    //
    // The first version asked whether a whole max-rate turn CIRCLE was clear.
    // That is far too strict beside a large zone -- both circles clip a 160 m
    // rectangle from over 100 m away -- so the filter declared danger almost
    // everywhere near a zone, sat in its fallback, and fought the mission
    // instead of flying it. Measured: 0.61 % of the track inside, worse than
    // the crude rule it replaced.
    //
    // What actually matters is whether the ARC flown while turning away stays
    // clear, so that is what is simulated: a hardest-possible turn, each way,
    // until the aircraft has swung 180 degrees. If either arc gets round
    // without touching a zone, the aircraft is not committed to entering one.
    if (m_zones.empty()) return true;
    const double rate = (m_maxTurnRate > 0) ? m_maxTurnRate : 360.0;
    const double dt = (m_fenceDt > 0) ? m_fenceDt : 0.1;
    const int steps = (int)std::ceil(180.0 / std::max(1e-6, rate * dt));
    for (int side = -1; side <= 1; side += 2) {
        double x = px, y = py, h = headingDeg;
        bool clear = true;
        for (int k = 0; k < steps && clear; ++k) {
            h += side * rate * dt;
            const double r = h * M_PI / 180.0;
            x += m_fenceV * dt * std::cos(r);
            y += m_fenceV * dt * std::sin(r);
            for (const NoFlyZone& z : m_zones)
                if (z.Contains(x, y)) { clear = false; break; }
        }
        if (clear) return true;
    }
    return false;
}

double FlightController::AvoidHeading(double cmdDeg) const {
    if (m_zones.empty() || !m_node || m_fenceR <= 0) return cmdDeg;
    const Vector p = GetPosition();

    // Already inside (should not happen, but a fence that gives up when the
    // invariant breaks is worse than useless): leave by the shortest way out.
    for (const NoFlyZone& z : m_zones) {
        if (!z.Contains(p.x, p.y)) continue;
        double ux, uy; z.Outward(p.x, p.y, ux, uy);
        return std::atan2(uy, ux) * 180.0 / M_PI;
    }

    // VIABILITY FILTER. Steering away from a zone and hoping is not a
    // guarantee: measured with a "turn tangential when close" rule, the
    // fixed-wing still ended up 6.7 m inside, because by the time the rule
    // fired the turn could no longer be completed. So the test is not "am I
    // near a zone" but "after obeying this command for one tick, can I STILL
    // turn away". If yes the command is safe to obey; if not, take the escape
    // turn now, while one still exists.
    auto step = [&](double cmd) {
        double d = cmd - m_headingDeg;
        while (d > 180.0) d -= 360.0;
        while (d < -180.0) d += 360.0;
        const double lim = (m_maxTurnRate > 0) ? m_maxTurnRate * m_fenceDt : 360.0;
        const double h2 = m_headingDeg + std::max(-lim, std::min(lim, d));
        const double r = h2 * M_PI / 180.0;
        return std::array<double, 3>{p.x + m_fenceV * m_fenceDt * std::cos(r),
                                     p.y + m_fenceV * m_fenceDt * std::sin(r), h2};
    };

    const auto n = step(cmdDeg);
    bool entersNow = false;
    for (const NoFlyZone& z : m_zones)
        if (z.Contains(n[0], n[1])) { entersNow = true; break; }
    if (!entersNow && EscapeExists(n[0], n[1], n[2])) return cmdDeg;

    // The command is not safe. Search headings outward from it and take the
    // nearest one that keeps an escape available, so avoidance costs as little
    // progress as possible.
    for (int k = 1; k <= 36; ++k)
        for (int side = -1; side <= 1; side += 2) {
            const double cand = cmdDeg + side * k * 5.0;
            const auto m = step(cand);
            bool bad = false;
            for (const NoFlyZone& z : m_zones)
                if (z.Contains(m[0], m[1])) { bad = true; break; }
            if (!bad && EscapeExists(m[0], m[1], m[2])) return cand;
        }
    // Nothing keeps an escape open: run directly away from the nearest zone.
    const NoFlyZone* near = nullptr; double best = 0;
    for (const NoFlyZone& z : m_zones) {
        const double d = z.Distance(p.x, p.y);
        if (!near || d < best) { near = &z; best = d; }
    }
    if (near) {
        double ux, uy; near->Outward(p.x, p.y, ux, uy);
        return std::atan2(uy, ux) * 180.0 / M_PI;
    }
    return cmdDeg;
}

void FlightController::Turn(double headingDeg) {
    headingDeg = AvoidHeading(headingDeg);
    m_cmdHeadingDeg = headingDeg;
    if (m_maxTurnRate <= 0) { m_headingDeg = headingDeg; Apply(); }
    // Rate-limited: the heading itself moves in Step(), so a fixed-wing cannot
    // snap onto a new course the way the old code let it.
}

void FlightController::Step(double dtS) {
    if (m_maxTurnRate <= 0 || dtS <= 0) return;
    // Re-check the fence every tick, not only when the application happens to
    // issue a new heading. A state that commands once and then coasts would
    // otherwise fly on unchecked, and the fence has to be a property of the
    // vehicle rather than of whoever remembered to call Turn().
    m_cmdHeadingDeg = AvoidHeading(m_cmdHeadingDeg);
    double d = m_cmdHeadingDeg - m_headingDeg;
    while (d > 180.0) d -= 360.0;
    while (d < -180.0) d += 360.0;
    const double lim = m_maxTurnRate * dtS;
    if (d > lim) d = lim;
    if (d < -lim) d = -lim;
    m_headingDeg += d;
    Apply();
}
void FlightController::Hover()                  { m_speed = 0; Apply(); }
void FlightController::SetClimb(double vzMps)   { m_vz = vzMps; Apply(); }

Vector FlightController::GetPosition() const {
    Ptr<MobilityModel> m = m_node->GetObject<MobilityModel>();
    return m ? m->GetPosition() : Vector(0, 0, 0);
}

void FlightController::Apply() {
    if (!m_node) return;
    Ptr<ConstantVelocityMobilityModel> mob =
        m_node->GetObject<ConstantVelocityMobilityModel>();
    if (!mob) return;
    double rad = m_headingDeg * M_PI / 180.0;
    mob->SetVelocity(Vector(m_speed * std::cos(rad), m_speed * std::sin(rad), m_vz));
}

}  // namespace ns3::uavsar
