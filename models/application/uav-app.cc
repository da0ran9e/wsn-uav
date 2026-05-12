#include "uav-app.h"
#include "../common/log.h"

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"

#include <cmath>
#include <iomanip>

using namespace ns3;

namespace ns3::wsn::uav {

NS_OBJECT_ENSURE_REGISTERED(UavApp);

TypeId UavApp::GetTypeId() {
    static TypeId tid = TypeId("ns3::wsn::uav::UavApp")
                            .SetParent<Application>()
                            .SetGroupName("wsn-uav")
                            .AddConstructor<UavApp>();
    return tid;
}

UavApp::UavApp()
    : m_nodeId(0),
      m_broadcastInterval(1.0),
      m_numFragments(10),
      m_nextFragIdx(0),
      m_xMin(0.0), m_yMin(0.0), m_xMax(0.0), m_yMax(0.0),
      m_altitude(20.0),
      m_speed(20.0),
      m_rowSpacing(20.0),
      m_flightAreaSet(false) {
}

UavApp::~UavApp() {
}

void UavApp::SetNodeId(uint32_t id) {
    m_nodeId = id;
}

void UavApp::SetNetDevice(Ptr<NetDevice> dev) {
    m_device = dev;
}

void UavApp::SetBroadcastInterval(double interval) {
    m_broadcastInterval = interval;
}

void UavApp::SetNumFragments(uint32_t count) {
    m_numFragments = count;
}

void UavApp::SetFlightArea(double xMin, double yMin, double xMax, double yMax) {
    m_xMin = xMin;
    m_yMin = yMin;
    m_xMax = xMax;
    m_yMax = yMax;
    m_flightAreaSet = true;
}

void UavApp::SetFlightAltitude(double z) {
    m_altitude = z;
}

void UavApp::SetFlightSpeed(double speed) {
    m_speed = speed;
}

void UavApp::SetRowSpacing(double spacing) {
    m_rowSpacing = spacing;
}

void UavApp::StartApplication() {
    LogN(GetNode()) << "UAV #" << m_nodeId << " started";

    if (m_flightAreaSet) {
        PlanAndIssueFlight();
        // Periodic position trace to verify the actuator follows commands.
        Simulator::Schedule(Seconds(2.0), &UavApp::LogPosition, this);
    } else {
        LogN(GetNode()) << "UAV #" << m_nodeId << " no flight area set, staying in place";
    }
}

void UavApp::LogPosition() {
    Ptr<MobilityModel> mob = GetNode()->GetObject<MobilityModel>();
    if (!mob) return;
    Vector v = mob->GetVelocity();
    double speed = std::sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
    LogN(GetNode()) << "UAV #" << m_nodeId << " pos sample, v=" << speed << " m/s";
    Simulator::Schedule(Seconds(2.0), &UavApp::LogPosition, this);
}

void UavApp::StopApplication() {
    LogN(GetNode()) << "UAV #" << m_nodeId << " stopped";
    Simulator::Cancel(m_broadcastEvent);
}

void UavApp::IssueWaypoint(double timeSec, const Vector& pos) {
    Ptr<WaypointMobilityModel> mob = GetNode()->GetObject<WaypointMobilityModel>();
    if (!mob) {
        LogN(GetNode()) << "UAV #" << m_nodeId << " ERROR: WaypointMobilityModel missing";
        return;
    }
    mob->AddWaypoint(Waypoint(Seconds(timeSec), pos));
    LogN(GetNode()) << "UAV #" << m_nodeId << " CMD waypoint t=" << timeSec
                    << "s -> (" << pos.x << ", " << pos.y << ", " << pos.z << ")";
}

void UavApp::PlanAndIssueFlight() {
    Ptr<WaypointMobilityModel> mob = GetNode()->GetObject<WaypointMobilityModel>();
    if (!mob) {
        LogN(GetNode()) << "UAV #" << m_nodeId
                        << " ERROR: WaypointMobilityModel not installed";
        return;
    }

    Vector start = mob->GetPosition();
    double tNow = Simulator::Now().GetSeconds();

    LogN(GetNode()) << "UAV #" << m_nodeId << " planning boustrophedon: area=["
                    << m_xMin << "," << m_xMax << "]x[" << m_yMin << "," << m_yMax
                    << "] z=" << m_altitude << "m speed=" << m_speed
                    << "m/s rowSpacing=" << m_rowSpacing << "m";

    // Anchor current position as the first waypoint so the model has a base.
    IssueWaypoint(tNow, start);

    auto travel = [this, &tNow](const Vector& from, const Vector& to) {
        double dx = to.x - from.x;
        double dy = to.y - from.y;
        double dz = to.z - from.z;
        double dist = std::sqrt(dx * dx + dy * dy + dz * dz);
        double dt = (m_speed > 0.0) ? dist / m_speed : 0.0;
        tNow += dt;
        IssueWaypoint(tNow, to);
    };

    // Boustrophedon: scan rows along x, advance along y.
    Vector cur = start;
    int rowIdx = 0;
    for (double y = m_yMin; y <= m_yMax + 1e-6; y += m_rowSpacing) {
        double xTarget = (rowIdx % 2 == 0) ? m_xMax : m_xMin;
        double xEntry  = (rowIdx % 2 == 0) ? m_xMin : m_xMax;

        Vector entry(xEntry, y, m_altitude);
        travel(cur, entry);
        cur = entry;

        Vector end(xTarget, y, m_altitude);
        travel(cur, end);
        cur = end;

        rowIdx++;
    }

    LogN(GetNode()) << "UAV #" << m_nodeId << " flight plan issued: "
                    << rowIdx << " rows, finishes at t=" << tNow << "s";
}

void UavApp::DoBroadcast() {
    LogN(GetNode()) << "UAV #" << m_nodeId << " TX fragment #" << m_nextFragIdx;
    m_nextFragIdx++;
    if (m_nextFragIdx < m_numFragments) {
        m_broadcastEvent = Simulator::Schedule(Seconds(m_broadcastInterval), &UavApp::DoBroadcast, this);
    }
}

}  // namespace ns3::wsn::uav
