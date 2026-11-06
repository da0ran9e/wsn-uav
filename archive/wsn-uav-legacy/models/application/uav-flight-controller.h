#ifndef UAV_FLIGHT_CONTROLLER_H
#define UAV_FLIGHT_CONTROLLER_H

#include "ns3/node.h"
#include "ns3/ptr.h"
#include "ns3/vector.h"
#include "ns3/constant-velocity-mobility-model.h"

namespace ns3::wsn::uav {

// Level-2 flight controller: heading + scalar speed. The Application issues
// high-level commands (Forward / Turn / Hover / SetClimb); the controller
// translates them into a velocity vector applied to ConstantVelocityMobilityModel.
// Position is integrated by ns-3 mobility (pos += v * dt) — Application never
// programs absolute waypoints in simulator time.
class UavFlightController {
public:
    UavFlightController();

    // Hooks into the node's ConstantVelocityMobilityModel.
    void AttachTo(ns3::Ptr<ns3::Node> node);

    // High-level commands (no absolute time, no future positions).
    void Forward(double speedMps);            // cruise along current heading
    void Turn(double newHeadingDeg);          // set heading (degrees, 0=+x, 90=+y)
    void Hover();                              // speed = 0 (horizontal); vz unchanged
    void SetClimb(double vzMps);              // vertical rate (positive = up)

    // "Sensors" — what the Application can observe.
    ns3::Vector GetPosition() const;
    double GetHeadingDeg() const;
    double GetSpeedMps() const;
    double GetClimbMps() const;

private:
    void ApplyVelocity();

    ns3::Ptr<ns3::ConstantVelocityMobilityModel> m_mob;
    double m_speedMps;
    double m_headingDeg;
    double m_vz;
};

}  // namespace ns3::wsn::uav

#endif  // UAV_FLIGHT_CONTROLLER_H
