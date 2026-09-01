#include "flight-controller.h"

#include "ns3/constant-velocity-mobility-model.h"

#include <cmath>

namespace ns3::uavsar {

using namespace ns3;

void FlightController::AttachTo(Ptr<Node> node) {
    m_node = node;
    Apply();
}

void FlightController::Forward(double speedMps) { m_speed = speedMps; Apply(); }
double FlightController::AvoidHeading(double cmdDeg) const {
    if (m_zones.empty() || !m_node) return cmdDeg;
    const Vector p = GetPosition();
    // Nearest breach first: with overlapping zones, obeying a farther one could
    // steer straight into the near one.
    const std::array<double, 3>* worst = nullptr;
    double worstSlack = 0;
    for (const auto& z : m_zones) {
        const double d = std::hypot(p.x - z[0], p.y - z[1]);
        const double slack = z[2] + m_fenceMargin - d;
        if (slack > 0 && (!worst || slack > worstSlack)) { worst = &z; worstSlack = slack; }
    }
    if (!worst) return cmdDeg;
    const double dx = p.x - (*worst)[0], dy = p.y - (*worst)[1];
    const double d = std::hypot(dx, dy);
    const double radial = (d > 1e-6) ? std::atan2(dy, dx) : 0.0;
    // Already inside: the only right answer is straight back out.
    if (d < (*worst)[2]) return radial * 180.0 / M_PI;
    // Near the edge: fly the tangent, taking whichever way round is closer to
    // where we wanted to go, so the detour costs as little progress as possible.
    const double c = cmdDeg * M_PI / 180.0;
    const double t1 = radial + M_PI / 2, t2 = radial - M_PI / 2;
    const double e1 = std::fabs(std::atan2(std::sin(t1 - c), std::cos(t1 - c)));
    const double e2 = std::fabs(std::atan2(std::sin(t2 - c), std::cos(t2 - c)));
    return ((e1 < e2) ? t1 : t2) * 180.0 / M_PI;
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
