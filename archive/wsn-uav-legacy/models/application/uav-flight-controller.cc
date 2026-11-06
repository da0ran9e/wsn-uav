#include "uav-flight-controller.h"

#include <cmath>

using namespace ns3;

namespace ns3::wsn::uav {

namespace {
constexpr double DEG2RAD = M_PI / 180.0;
}  // namespace

UavFlightController::UavFlightController()
    : m_speedMps(0.0), m_headingDeg(0.0), m_vz(0.0) {
}

void UavFlightController::AttachTo(Ptr<Node> node) {
    m_mob = node->GetObject<ConstantVelocityMobilityModel>();
}

void UavFlightController::Forward(double speedMps) {
    m_speedMps = speedMps;
    ApplyVelocity();
}

void UavFlightController::Turn(double newHeadingDeg) {
    // Normalize to [0, 360).
    double h = std::fmod(newHeadingDeg, 360.0);
    if (h < 0) h += 360.0;
    m_headingDeg = h;
    ApplyVelocity();
}

void UavFlightController::Hover() {
    m_speedMps = 0.0;
    ApplyVelocity();
}

void UavFlightController::SetClimb(double vzMps) {
    m_vz = vzMps;
    ApplyVelocity();
}

void UavFlightController::ApplyVelocity() {
    if (!m_mob) return;
    double rad = m_headingDeg * DEG2RAD;
    double vx = m_speedMps * std::cos(rad);
    double vy = m_speedMps * std::sin(rad);
    m_mob->SetVelocity(Vector(vx, vy, m_vz));
}

Vector UavFlightController::GetPosition() const {
    return m_mob ? m_mob->GetPosition() : Vector(0, 0, 0);
}

double UavFlightController::GetHeadingDeg() const { return m_headingDeg; }
double UavFlightController::GetSpeedMps() const { return m_speedMps; }
double UavFlightController::GetClimbMps() const { return m_vz; }

}  // namespace ns3::wsn::uav
