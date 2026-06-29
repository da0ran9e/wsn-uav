#ifndef WSN_UAV_TRAJECTORY_H
#define WSN_UAV_TRAJECTORY_H

#include <vector>
#include <cmath>
#include <cstdint>

namespace ns3::wsn::uav {

struct Waypoint {
    double x, y, z;
    double arrivalTime;  // in seconds

    Waypoint() : x(0), y(0), z(0), arrivalTime(0) {}
    Waypoint(double x_, double y_, double z_, double t = 0)
        : x(x_), y(y_), z(z_), arrivalTime(t) {}
};

class UavTrajectory {
public:
    UavTrajectory();
    virtual ~UavTrajectory() = default;

    // Add waypoint to trajectory
    void AddWaypoint(const Waypoint& wp);

    // Get all waypoints
    const std::vector<Waypoint>& GetWaypoints() const { return m_waypoints; }

    // Get waypoint count
    uint32_t GetWaypointCount() const { return m_waypoints.size(); }

    // Get total flight time
    double GetTotalFlightTime() const;

    // Get total distance
    double GetTotalDistance() const;

    // Clear all waypoints
    void Clear() { m_waypoints.clear(); }

    // Validate trajectory
    bool IsValid() const { return m_waypoints.size() >= 2; }

private:
    std::vector<Waypoint> m_waypoints;

    double Distance(const Waypoint& a, const Waypoint& b) const;
};

}  // namespace ns3::wsn::uav

#endif  // WSN_UAV_TRAJECTORY_H
