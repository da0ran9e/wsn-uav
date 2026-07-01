#ifndef UAV_APP_H
#define UAV_APP_H

#include "uav-flight-controller.h"
#include "uav-dissemination-model.h"
#include "../common/semantic-fragment.h"

#include "ns3/application.h"
#include "ns3/net-device.h"
#include "ns3/ptr.h"
#include "ns3/event-id.h"
#include "ns3/vector.h"
#include "ns3/address.h"

#include <cstdint>
#include <set>
#include <vector>

namespace ns3::wsn::uav {

enum class FlightPathModel : uint8_t {
    CELL_AWARE_GMC = 0,
    PER_NODE_GMC   = 1,
    NEAREST_NEIGHBOR = 2,
    CELL_CENTROID_SWEEP = 3,
    RANDOM_WAYPOINT = 4,
};

class UavApp : public Application {
public:
    static TypeId GetTypeId();

    UavApp();
    virtual ~UavApp();

    // Identity / radio
    void SetNodeId(uint32_t id);
    void SetNetDevice(ns3::Ptr<ns3::NetDevice> dev);
    void SetGroundNodeDestinations(const std::vector<uint32_t>& nodeIds,
                                   const std::vector<ns3::Address>& addresses);
    void SetFlightPathModel(FlightPathModel model);
    void SetBroadcastModel(BroadcastModel model);
    void SetRandomWaypointBudget(uint32_t budget);

    // Total search-fragment packets emitted during the flight.
    uint32_t L0BroadcastCount() const { return m_dissemination.TxSuccessCount(); }
    uint32_t L0SendAttemptCount() const { return m_dissemination.TxAttemptCount(); }
    uint32_t L0SendSuccessCount() const { return m_dissemination.TxSuccessCount(); }
    uint32_t L0SendFailCount() const { return m_dissemination.TxFailCount(); }
    uint32_t L0FragmentCount() const { return m_dissemination.FragmentCount(); }
    uint32_t L0SubPacketsPerFragment() const {
        return m_dissemination.DataSubPacketsPerFragment();
    }
    uint32_t WaypointCount() const { return static_cast<uint32_t>(m_targets.size()); }
    double PlannedPathLengthMeters() const { return m_plannedPathLengthMeters; }
    double TakeoffTimeSec() const { return m_takeoffTimeSec; }
    double LandingTimeSec() const { return m_landingTimeSec; }
    double FlightDurationSec() const {
        return (m_takeoffTimeSec >= 0.0 && m_landingTimeSec >= 0.0)
                   ? (m_landingTimeSec - m_takeoffTimeSec)
                   : -1.0;
    }
    const char* GetFlightPathModelName() const { return FlightPathModelName(); }
    const char* GetBroadcastModelName() const { return BroadcastModelName(); }

    // Handle incoming messages from BaseStation
    bool OnMessageReceived(ns3::Ptr<ns3::NetDevice> dev,
                          ns3::Ptr<const ns3::Packet> pkt,
                          uint16_t proto,
                          const ns3::Address& from);

private:
    enum class MsgType : uint8_t {
        TOPO_FRAGMENT = 1,
        TOPO_ACK      = 2,
        DATA_FRAGMENT = 3,
        DATA_ACK      = 4,
    };

    void StartApplication() override;
    void StopApplication() override;

    // Lifecycle
    void TakeOff();
    double ComputeL0AirtimeSeconds(uint32_t fragSizeBytes) const;
    void ComputeFlightSpeed();    // derives cruise speed from the contact window
    void TransmitSearchPacket();  // periodic search dissemination during flight

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
    void   BuildCellAwareGmcMission();
    void   BuildPerNodeGmcMission();
    void   BuildNearestNeighborMission();
    void   BuildCellCentroidSweepMission();
    void   BuildRandomWaypointMission();
    void   UpdatePlannedPathLength();
    const char* FlightPathModelName() const;
    const char* BroadcastModelName() const;
    bool   AdvanceToNextTarget();   // returns false when mission finished
    void   SendTopologyAck(bool complete);
    void   SendDataAck(uint16_t fragId,
                       uint32_t chunkOffset,
                       uint16_t chunkLen,
                       uint32_t fragmentsComplete,
                       bool complete);
    void   ProcessDataFragment(const std::vector<uint8_t>& buf,
                               const ns3::Address& from);
    void   MaybeScheduleTakeoff();  // takes off once topology AND data are in

    enum class FlightState {
        IDLE,         // waiting for topology
        CLIMBING,     // ascending to cruise altitude
        CRUISING,     // heading toward current target (x,y)
        LANDING,      // mission complete, descending
        DONE
    };

    uint32_t m_nodeId;
    ns3::Ptr<ns3::NetDevice> m_device;
    ns3::EventId m_takeoffEvent;
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
    FlightPathModel m_flightPathModel;
    BroadcastModel m_broadcastModel;
    uint32_t m_randomWaypointBudget;

    double m_cruiseAltitude;
    double m_cruiseSpeed;
    double m_maxCruiseSpeedMps;
    double m_plannedPathLengthMeters;
    double m_takeoffTimeSec;
    double m_landingTimeSec;
    bool m_appStarted;
    bool m_ctrlAttached;
    bool m_flightScheduled;
    bool m_takeoffPending;

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

    // Fragment-data reassembly state. BS sends the semantic profile right
    // after the topology; the UAV takes off only once BOTH are complete.
    bool m_dataComplete;
    uint32_t m_numDataFragmentsExpected;
    std::vector<Fragment> m_dataFragments;      // metadata, indexed by fragId
    std::vector<uint32_t> m_fragReceivedBytes;  // bytes received per fragId
    std::vector<std::set<uint32_t>> m_fragReceivedOffsets;  // dedupe per fragId
    std::vector<bool>     m_fragSeen;           // metadata recorded per fragId

    double   m_l0BroadcastPeriod;            // approx per-packet airtime
    bool     m_l0BroadcastActive;            // true until mission actually ends
    std::vector<uint32_t> m_groundNodeIds;
    std::vector<ns3::Address> m_groundNodeAddresses;
    UavDisseminationModel m_dissemination;

    FlightState m_state;
    UavFlightController m_ctrl;
};

}  // namespace ns3::wsn::uav

#endif  // UAV_APP_H
