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
void FlightController::Turn(double headingDeg) {
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
