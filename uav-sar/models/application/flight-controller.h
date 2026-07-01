#ifndef UAV_SAR_FLIGHT_CONTROLLER_H
#define UAV_SAR_FLIGHT_CONTROLLER_H

// Thin wrapper over ConstantVelocityMobilityModel giving high-level flight
// commands (ref: main's uav-flight-controller). Horizontal heading+speed and
// vertical climb are composed into the velocity vector.

#include "ns3/ptr.h"
#include "ns3/node.h"
#include "ns3/vector.h"

namespace ns3::uavsar {

class FlightController {
public:
    void AttachTo(ns3::Ptr<ns3::Node> node);
    void Forward(double speedMps);     // set horizontal speed along current heading
    void Turn(double headingDeg);      // set heading (degrees, math convention)
    void Hover();                      // horizontal speed 0
    void SetClimb(double vzMps);       // vertical speed
    ns3::Vector GetPosition() const;
    double Speed() const { return m_speed; }
    double Heading() const { return m_headingDeg; }
    double Climb() const { return m_vz; }

private:
    void Apply();
    ns3::Ptr<ns3::Node> m_node;
    double m_speed = 0;
    double m_headingDeg = 0;
    double m_vz = 0;
};

}  // namespace ns3::uavsar

#endif  // UAV_SAR_FLIGHT_CONTROLLER_H
