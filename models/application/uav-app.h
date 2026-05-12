#ifndef UAV_APP_H
#define UAV_APP_H

#include "ns3/application.h"
#include "ns3/net-device.h"
#include "ns3/ptr.h"
#include "ns3/event-id.h"
#include "ns3/vector.h"

namespace ns3::wsn::uav {

class UavApp : public Application {
public:
    static TypeId GetTypeId();

    UavApp();
    virtual ~UavApp();

    // Identity / radio
    void SetNodeId(uint32_t id);
    void SetNetDevice(ns3::Ptr<ns3::NetDevice> dev);

    // Broadcast config (kept for fragment dissemination later)
    void SetBroadcastInterval(double interval);
    void SetNumFragments(uint32_t count);

    // Flight area: rectangle [xMin,xMax] × [yMin,yMax] at fixed altitude.
    // The boustrophedon (lawn-mower) path scans rows spaced by `rowSpacing`.
    void SetFlightArea(double xMin, double yMin, double xMax, double yMax);
    void SetFlightAltitude(double z);
    void SetFlightSpeed(double speed);
    void SetRowSpacing(double spacing);

private:
    void StartApplication() override;
    void StopApplication() override;

    // Computes a boustrophedon waypoint sequence and issues commands to the
    // node's WaypointMobilityModel actuator.
    void PlanAndIssueFlight();
    void IssueWaypoint(double timeSec, const ns3::Vector& pos);
    void LogPosition();

    void DoBroadcast();

    uint32_t m_nodeId;
    ns3::Ptr<ns3::NetDevice> m_device;
    double m_broadcastInterval;
    uint32_t m_numFragments;
    uint32_t m_nextFragIdx;
    ns3::EventId m_broadcastEvent;

    // Flight parameters
    double m_xMin, m_yMin, m_xMax, m_yMax;
    double m_altitude;
    double m_speed;
    double m_rowSpacing;
    bool m_flightAreaSet;
};

}  // namespace ns3::wsn::uav

#endif  // UAV_APP_H
