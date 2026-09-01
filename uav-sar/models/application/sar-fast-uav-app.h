#ifndef UAV_SAR_FAST_UAV_APP_H
#define UAV_SAR_FAST_UAV_APP_H

// FAST-team UAV: sweeps the area (GMC coverage), broadcasts small identity cues
// (L0/L1) to the ground, listens for the region SUMMON and relays it to the
// DATA team over A2A (DATA does not listen directly).

#include "flight-controller.h"
#include "../common/target-profile.h"
#include "../common/sar-types.h"

#include "ns3/application.h"
#include "ns3/net-device.h"
#include "ns3/event-id.h"
#include "ns3/vector.h"
#include "ns3/ptr.h"
#include "ns3/address.h"
#include "ns3/random-variable-stream.h"

#include <array>
#include <cmath>
#include <cstdint>
#include <map>
#include <memory>
#include <set>
#include <utility>
#include <vector>

namespace ns3::uavsar {

class SarMetrics;

class SarFastUavApp : public ns3::Application {
public:
    static ns3::TypeId GetTypeId();
    SarFastUavApp();
    ~SarFastUavApp() override;

    void SetNodeId(uint32_t id) { m_nodeId = id; }
    void SetDevice(ns3::Ptr<ns3::NetDevice> d) { m_dev = d; }
    void SetMetrics(SarMetrics* m) { m_metrics = m; }
    void SetSensorPositions(const std::vector<ns3::Vector>& p) { m_sensors = p; }
    // Phase 1: the orchestrator owns the lane split, because deciding which UAV
    // sweeps which lane needs to see the whole fleet. A UAV given a plan flies
    // it; one given none falls back to building its own over its sensor set.
    void SetMissionOverride(const std::vector<ns3::Vector>& wps) { m_mission = wps; }
    // Geofence. Planning around a zone is not the same as staying out of one:
    // a curvature-limited aircraft cuts the corner. Measured with clipped lanes
    // and bypass waypoints alone, the track was still 4.2 % inside a zone and up
    // to 46 m deep, and inflating the zones to compensate helped
    // NON-MONOTONICALLY (0.00 % at 130 m, 2.05 % at 160 m) -- i.e. any margin
    // that works is working by luck. This is the guarantee instead: the airframe
    // refuses the heading.
    void SetNoFlyZones(const std::vector<std::array<double, 3>>& z) { m_zones = z; }
    void SetCues(const std::vector<Fragment>& c) { m_cues = c; }
    void SetCruise(double alt, double speed) { m_alt = alt; m_speed = speed; }
    void SetBs(ns3::Vector pos, ns3::Address addr) { m_bsPos = pos; m_bsAddr = addr; }
    // audit F2: symmetric completion — every UAV flies home and reports, so the
    // mission clock is not stopped by a single courier while peers stay airborne.
    void SetFixOnConfirm(bool v) { m_fixOnConfirm = v; }
    void SetAllHome(bool v) { m_allHome = v; }
    // audit W4: home on the strongest DIRECT echo instead of a ground SUMMON.
    void SetEchoRelay(bool v) { m_echoRelay = v; }

    bool OnReceive(ns3::Ptr<ns3::NetDevice> dev, ns3::Ptr<const ns3::Packet> pkt,
                   uint16_t proto, const ns3::Address& from);

private:
    void StartApplication() override;
    void StopApplication() override;
    void TakeOff();
    void BuildMission();
    void ControlTick();
    void DisseminateTick();
    void TrajTick();

    enum class State { IDLE, CLIMB, CRUISE, RELAY_HOLD, RETURN_BS, DONE };

    uint32_t m_nodeId = 0;
    ns3::Ptr<ns3::NetDevice> m_dev;
    SarMetrics* m_metrics = nullptr;
    std::vector<ns3::Vector> m_sensors;
    std::vector<Fragment> m_cues;
    std::vector<ns3::Vector> m_targets;
    std::vector<ns3::Vector> m_mission;   // lane plan from the orchestrator
    std::vector<std::array<double, 3>> m_zones;   // x, y, r
    size_t m_ti = 0;
    size_t m_cueIdx = 0;      // fragment index in m_cues
    uint16_t m_cueSeq = 0;    // chunk seq within the current cue fragment
    uint32_t m_cueTxCount = 0;  // for decimated viz markers
    bool m_summonSeen = false;  // closed-loop: an aim has already been dispatched
    // D30: a UAV goes home when the places it dispatched the DATA team to have
    // all been resolved, not when the FIRST one closed. Both sets are filled
    // purely from radio traffic this UAV heard -- no global view.
    std::set<uint16_t> m_relayedRegions;   // regions this UAV relayed a summon for
    std::set<uint16_t> m_closedRegions;    // regions a CONFIRM or REJECT closed
    bool AllRelayedClosed() const;
    double m_prevDist = 0;      // waypoint range last tick (abeam detection)
    double m_relayUntilS = 0;   // audit A10: bounded post-sweep relay hold
    // audit W4: closed-loop baseline -- the best DIRECT echo this UAV heard.
    bool m_echoRelay = false;
    double m_bestEchoEv = 0, m_bestEchoX = 0, m_bestEchoY = 0;
    void RelayBestEcho();
    ns3::EventId m_echoSettle;
    bool m_hasFix = false;
    // D37: every CONFIRMED position this UAV is carrying, not just the first.
    // D38: and a second confirm for the SAME place refines it instead of being
    // discarded. Every confirming node holds the complete reference and still
    // matches it, so each one is an independent sample of where the thing is;
    // their centroid beats whichever one happened to be heard first. Measured
    // at 24x24: first-heard gave a 24.1 m median report error on a 20 m grid.
    std::vector<std::array<double, 3>> m_fixAcc;      // sumX, sumY, n
    std::vector<std::pair<double, double>> m_fixes;
    void AddFix(double x, double y) {
        for (size_t i = 0; i < m_fixAcc.size(); ++i) {
            if (std::hypot(m_fixes[i].first - x, m_fixes[i].second - y) > 50.0) continue;
            m_fixAcc[i][0] += x; m_fixAcc[i][1] += y; m_fixAcc[i][2] += 1;
            m_fixes[i] = {m_fixAcc[i][0] / m_fixAcc[i][2], m_fixAcc[i][1] / m_fixAcc[i][2]};
            return;
        }
        if (m_fixes.size() < kMaxFixes) { m_fixes.push_back({x, y});
                                          m_fixAcc.push_back({x, y, 1}); }
    }
    // A relayed aim is only a CANDIDATE until the ground confirms it.
    //
    // D38: one pending aim was not enough. A relay hears a SUMMON from every
    // region it flies over, and the ONE pending slot held whichever came last;
    // any CONFIRM, from any region, then promoted it. Measured at 24x24: a
    // decoy's aim at (380,60) rode home as a confirmed fix because a DIFFERENT
    // region's victim confirmed 3 s after the decoy summoned. Aims are now kept
    // per region, and only the confirming region's aim is promoted.
    std::map<uint16_t, std::pair<double, double>> m_pendAims;
    std::set<uint16_t> m_confirmedRegions;   // still take refining samples
    bool m_fixOnConfirm = true;
    double m_fixX = 0, m_fixY = 0;
    double m_alt = 20.0, m_speed = 25.0, m_radius = 50.0;
    State m_state = State::IDLE;
    ns3::Vector m_bsPos{0, 0, 0};
    ns3::Address m_bsAddr;
    ns3::Ptr<ns3::UniformRandomVariable> m_rng;
    bool m_courier = false;
    bool m_yieldedCourier = false;
    bool m_allHome = true;
    ns3::EventId m_courierEvent;
    uint32_t m_reportsSent = 0;
    void SendReport();
    void ClaimCourier();          // won the radio CLAIM -> race the report home
    void SendClaim(uint8_t role); // broadcast a role claim (mutual exclusion)
    ns3::EventId m_ctrl, m_dis, m_traj;
    FlightController m_fc;
};

}  // namespace ns3::uavsar

#endif  // UAV_SAR_FAST_UAV_APP_H
