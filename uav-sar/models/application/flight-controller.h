#ifndef UAV_SAR_FLIGHT_CONTROLLER_H
#define UAV_SAR_FLIGHT_CONTROLLER_H

// Thin wrapper over ConstantVelocityMobilityModel giving high-level flight
// commands (ref: main's uav-flight-controller). Horizontal heading+speed and
// vertical climb are composed into the velocity vector.

#include "ns3/ptr.h"
#include "ns3/node.h"
#include "ns3/vector.h"
#include <vector>
#include <array>

namespace ns3::uavsar {

class FlightController {
public:
    void AttachTo(ns3::Ptr<ns3::Node> node);
    void Forward(double speedMps);     // set horizontal speed along current heading
    void Turn(double headingDeg);      // command a heading (degrees, math convention)
    double AvoidHeading(double cmdDeg) const;   // fence-corrected command
    // FIXED-WING: a coordinated turn at bank phi gives a turn RATE of
    // g tan(phi) / v, so heading cannot change faster than that. Left at 0 the
    // vehicle turns instantly, which is a fair model for a multirotor and a
    // wrong one for an aeroplane. Turn() clamps toward the commanded heading by
    // this rate per call; the caller passes the elapsed time.
    // Geofence, at the controller rather than in each app: every state that
    // commands a heading gets it, and no future state can forget to. Measured
    // with the fence in the FAST app only, the rotary team -- which had no fence
    // at all -- spent 5.7 % of its track inside a zone.
    void SetNoFlyZones(const std::vector<std::array<double, 3>>& z, double marginM) {
        m_zones = z; m_fenceMargin = marginM;
    }
    void SetMaxTurnRateDegPerS(double r) { m_maxTurnRate = r; }
    void Step(double dtS);             // advance the rate-limited heading by dt
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
    std::vector<std::array<double, 3>> m_zones;
    double m_fenceMargin = 0;
    double m_maxTurnRate = 0;          // deg/s; 0 = instant (rotary-wing)
    double m_cmdHeadingDeg = 0;        // what the controller was ASKED for
};

}  // namespace ns3::uavsar

#endif  // UAV_SAR_FLIGHT_CONTROLLER_H
