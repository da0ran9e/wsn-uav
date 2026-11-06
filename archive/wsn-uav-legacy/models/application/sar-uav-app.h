#ifndef WSN_UAV_SAR_UAV_APP_H
#define WSN_UAV_SAR_UAV_APP_H

// SAR UAV application. A UAV carries a set of search-data fragments and sweeps
// the sensor grid (GMC coverage), broadcasting fragment chunks to ground nodes.
//   FAST role: carries small RECOGNITION fragments, flies fast, listens for
//              emergency beacons and relays them to DATA UAVs (A2A).
//   DATA role: carries large DATA fragments; on hearing a beacon it diverts to
//              the victim's cell and delivers the FULL dataset to the target.
// Reuses UavFlightController for low-level motion. Sensor positions and the
// carried fragment set are injected by the orchestrator (BS pre-brief).

#include "uav-flight-controller.h"
#include "../common/sar-types.h"
#include "../common/sar-fragment.h"

#include "ns3/application.h"
#include "ns3/net-device.h"
#include "ns3/ptr.h"
#include "ns3/event-id.h"
#include "ns3/vector.h"
#include "ns3/address.h"

#include <cstdint>
#include <memory>
#include <vector>

namespace ns3::wsn::uav {

class SarMetrics;  // fwd (common/sar-metrics.h)

class SarUavApp : public ns3::Application {
public:
    static ns3::TypeId GetTypeId();
    SarUavApp();
    ~SarUavApp() override;

    void SetNodeId(uint32_t id) { m_nodeId = id; }
    void SetNetDevice(ns3::Ptr<ns3::NetDevice> dev) { m_device = dev; }
    void SetRole(sar::UavRole r) { m_role = r; }
    void SetScheme(sar::Scheme s) { m_scheme = s; }
    void SetMetrics(SarMetrics* m) { m_metrics = m; }
    void SetSensorPositions(const std::vector<ns3::Vector>& p) { m_sensorPositions = p; }
    void SetCarriedFragments(const std::vector<sar::Fragment>& f) { m_carried = f; }
    void SetFullDataset(const std::vector<sar::Fragment>& f) { m_fullset = f; }
    void SetCruise(double altitude, double speed) { m_cruiseAlt = altitude; m_cruiseSpeed = speed; }
    // Fleet-shared claim token (holds the node id of the DATA UAV that owns the
    // current rescue event, -1 if free) so exactly one UAV diverts/delivers.
    void SetClaimToken(std::shared_ptr<int32_t> t) { m_claimToken = std::move(t); }

    bool OnReceive(ns3::Ptr<ns3::NetDevice> dev, ns3::Ptr<const ns3::Packet> pkt,
                   uint16_t proto, const ns3::Address& from);

private:
    void StartApplication() override;
    void StopApplication() override;

    // Flight
    void TakeOff();
    void BuildMission();              // GMC coverage over m_sensorPositions
    bool AdvanceToNextTarget();
    void ControlTick();
    void LogTraj();

    // Dissemination of carried fragments while sweeping.
    void DisseminateTick();
    void SendFragChunk(uint16_t fragId, uint16_t seq, uint16_t total, sar::FragClass cls);

    // Emergency response (DATA role) / relay (FAST role).
    void DivertTo(double x, double y);
    void DeliverFullData();
    void SendFullChunk(size_t fragIdx, uint16_t seq);

    enum class State { IDLE, CLIMBING, CRUISING, DIVERTING, DELIVERING, LANDING, DONE };
    // DIVERT: proposed summoned delivery (land after). WAYPOINT: baseline
    // dwell-and-dump full data at each visited cell (resume sweep after).
    enum class DeliverMode { DIVERT, WAYPOINT };

    uint32_t m_nodeId = 0;
    ns3::Ptr<ns3::NetDevice> m_device;
    sar::UavRole m_role = sar::UavRole::FAST;
    sar::Scheme m_scheme = sar::Scheme::PROPOSED;
    SarMetrics* m_metrics = nullptr;

    std::vector<ns3::Vector> m_sensorPositions;
    std::vector<sar::Fragment> m_carried;   // what this UAV broadcasts on sweep
    std::vector<sar::Fragment> m_fullset;   // full dataset (DATA delivers on summon)

    std::vector<ns3::Vector> m_targets;     // GMC waypoints
    size_t m_targetIdx = 0;

    double m_cruiseAlt = 20.0;
    double m_cruiseSpeed = 20.0;
    double m_broadcastRadius = 50.0;

    // dissemination cursor over (carried fragment, chunk)
    size_t m_disFragIdx = 0;
    uint16_t m_disSeq = 0;

    // emergency
    std::shared_ptr<int32_t> m_claimToken;
    bool m_claimedEvent = false;
    void TryClaimAndDivert(double x, double y);
    ns3::Vector m_divertTarget{0, 0, 0};
    size_t m_deliverFragIdx = 0;
    uint16_t m_deliverSeq = 0;
    double m_divertStartDist = 0.0;
    DeliverMode m_deliverMode = DeliverMode::DIVERT;

    State m_state = State::IDLE;
    ns3::EventId m_controlEvent;
    ns3::EventId m_disEvent;
    UavFlightController m_ctrl;
};

}  // namespace ns3::wsn::uav

#endif  // WSN_UAV_SAR_UAV_APP_H
