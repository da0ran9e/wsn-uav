#include "uav-trajectory.h"

namespace ns3::wsn::uav {

UavTrajectory::UavTrajectory() {}

void UavTrajectory::AddWaypoint(const Waypoint& wp) {
    m_waypoints.push_back(wp);
}

double UavTrajectory::GetTotalFlightTime() const {
    if (m_waypoints.empty()) return 0.0;
    return m_waypoints.back().arrivalTime;
}

double UavTrajectory::GetTotalDistance() const {
    if (m_waypoints.size() < 2) return 0.0;

    double total = 0.0;
    for (size_t i = 1; i < m_waypoints.size(); i++) {
        total += Distance(m_waypoints[i - 1], m_waypoints[i]);
    }
    return total;
}

double UavTrajectory::Distance(const Waypoint& a, const Waypoint& b) const {
    double dx = b.x - a.x;
    double dy = b.y - a.y;
    double dz = b.z - a.z;
    return std::sqrt(dx * dx + dy * dy + dz * dz);
}

}  // namespace ns3::wsn::uav
