#ifndef UAV_APP_H
#define UAV_APP_H

#include "uav-flight-controller.h"

#include "ns3/application.h"
#include "ns3/net-device.h"
#include "ns3/ptr.h"
#include "ns3/event-id.h"
#include "ns3/vector.h"
#include "ns3/address.h"

#include <cstdint>
#include <vector>

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

    // Handle incoming messages from BaseStation
    bool OnMessageReceived(ns3::Ptr<ns3::NetDevice> dev,
                          ns3::Ptr<const ns3::Packet> pkt,
                          uint16_t proto,
                          const ns3::Address& from);

private:
    enum class MsgType : uint8_t {
        TOPO_FRAGMENT = 1,
        TOPO_ACK = 2,
    };

    void StartApplication() override;
    void StopApplication() override;

    // Lifecycle
    void TakeOff();
    void DoBroadcast();

    // Autopilot loop: runs every CONTROL_TICK seconds, drives the state
    // machine based on GPS position relative to the current target.
    void ControlTick();
    void LogPosition();

    // Mission planning. ComputeBroadcastRadius() solves the LogDistance
    // equation for the max distance at which RX power equals sensitivity.
    // BuildMission() runs simplified GMC: greedy maximum coverage over all
    // sensor positions, using the computed broadcast radius.
    void   ComputeBroadcastRadius();
    void   BuildMission();
    bool   AdvanceToNextTarget();   // returns false when mission finished
    void   SendTopologyAck(bool complete);

    enum class FlightState {
        IDLE,         // waiting for topology
        CLIMBING,     // ascending to cruise altitude
        CRUISING,     // heading toward current target (x,y)
        LANDING,      // mission complete, descending
        DONE
    };

    uint32_t m_nodeId;
    ns3::Ptr<ns3::NetDevice> m_device;
    double m_broadcastInterval;
    uint32_t m_numFragments;
    uint32_t m_nextFragIdx;
    ns3::EventId m_broadcastEvent;
    ns3::EventId m_controlEvent;

    // Pre-flight calibration: assumed LogDistance path loss model + radio
    // params. Used to derive broadcastRadius before mission planning.
    double m_txPowerDbm;
    double m_rxSensitivityDbm;
    double m_pathLossExponent;
    double m_refDistance;
    double m_refLossDb;
    double m_broadcastRadius;  // computed by ComputeBroadcastRadius()

    double m_cruiseAltitude;
    double m_cruiseSpeed;
    bool m_flightScheduled;

    // Topology reassembly state (BS sends N fragments).
    std::vector<ns3::Vector> m_sensorPositions;  // learned from topology
    uint32_t m_topoTotalExpected;                // total nodes BS will send
    uint32_t m_topoReceived;                     // unique sensor slots merged so far
    std::vector<bool> m_sensorSlotFilled;        // per-sensor slot dedupe marker
    std::vector<ns3::Vector> m_targets;          // GMC-planned waypoints
    size_t m_targetIdx;
    ns3::Address m_bsAddress;
    uint8_t m_bsNodeId;
    bool m_hasBsAddress;
    bool m_topologyComplete;

    FlightState m_state;
    UavFlightController m_ctrl;
};

}  // namespace ns3::wsn::uav

#endif  // UAV_APP_H
