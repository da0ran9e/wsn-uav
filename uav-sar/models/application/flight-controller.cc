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
void FlightController::Turn(double headingDeg)  { m_headingDeg = headingDeg; Apply(); }
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
