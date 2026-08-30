#ifndef UAV_SAR_DATA_UAV_APP_H
#define UAV_SAR_DATA_UAV_APP_H

// DATA-team UAV: climbs and loiters at a staging point (does not listen to the
// ground directly). On a relayed SUMMON (A2A) it claims the event over the radio
// (a broadcast CLAIM with suppression, so exactly one responds — no shared-memory
// token), diverts to the victim region, delivers the FULL dataset, and on CONFIRM
// flies back to the BS and sends a small report.

#include "flight-controller.h"
#include "../common/target-profile.h"
#include "../common/sar-types.h"
#include "../common/sar-params.h"

#include "ns3/application.h"
#include "ns3/net-device.h"
#include "ns3/event-id.h"
#include "ns3/vector.h"
#include "ns3/address.h"
#include "ns3/ptr.h"
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

class SarDataUavApp : public ns3::Application {
public:
    static ns3::TypeId GetTypeId();
    SarDataUavApp();
    ~SarDataUavApp() override;

    void SetNodeId(uint32_t id) { m_nodeId = id; }
    void SetDevice(ns3::Ptr<ns3::NetDevice> d) { m_dev = d; }
    void SetMetrics(SarMetrics* m) { m_metrics = m; }
    void SetFullDataset(const std::vector<Fragment>& f) { m_full = f; }
    void SetCruise(double alt, double speed) { m_alt = alt; m_speed = speed; }
    void SetLoiter(ns3::Vector c) { m_loiter = c; }
    void SetBs(ns3::Vector pos, ns3::Address addr) { m_bsPos = pos; m_bsAddr = addr; }

    // Baseline behaviour: instead of loiter+summon, sweep the grid and dwell-dump
    // the full dataset at every visited cell (no ground cooperation).
    enum class Mode { SUMMONED, SWEEP_DUMP };
    void SetMode(Mode m) { m_mode = m; }
    void SetSensorPositions(const std::vector<ns3::Vector>& p) { m_sensors = p; }
    // tsp-mc baseline: fly THESE waypoints (VBS tour) instead of building a GMC
    // sweep, and return to the BS to report once the tour is done.
    void SetTourOverride(const std::vector<ns3::Vector>& t) { m_tourOverride = t; }
    void SetReportAtEnd(bool v) { m_reportAtEnd = v; }   // fly home + REPORT
    // separate from the return policy: only the coded-multicast baseline sizes
    // its hover as redundancy x dataset airtime; nocoop keeps its design budget.
    void SetMcDwell(bool v) { m_mcDwell = v; }
    void SetMcRedundancy(double r) { m_mcRedundancy = r; }
    void SetAllHome(bool v) { m_allHome = v; }        // audit F2
    // While waiting to be summoned, a DATA UAV used to park at the field centre
    // and hover. That wasted it twice: it spread nothing, and -- because SUMMON
    // is a ONE-HOP ground broadcast -- a stationary UAV at the centre is almost
    // never within radio range of the leader that fires it. At 40x40 that was
    // fatal: a correct 9 m aim was computed and never reached the sky. Patrol
    // instead: fly a coverage sweep over this UAV's own band, spreading CUES
    // exactly as the FAST team does, and stay divertible throughout.
    void SetPhaseGate(bool on, uint32_t fastCount, double deadlineS, bool ground) {
        m_phaseGate = on; m_expectFast = fastCount; m_gateDeadlineS = deadlineS;
        m_gateGround = ground;
    }
    void SetPatrol(bool v) { m_patrol = v; }
    void SetCues(const std::vector<Fragment>& c) { m_cues = c; }
    // Spread cues on every leg flown before a delivery task exists, not only
    // while patrolling. The flight is happening anyway, so the radio time is
    // free; this is NOT --dataPatrol, which pays for an extra tour.
    void SetCueEnroute(bool v) { m_cueEnroute = v; }
    // Fly the coverage plan from the far end, so DATA and FAST are separated
    // in time over the same ground rather than arriving together.
    void SetPatrolReverse(bool v) { m_patrolReverse = v; }
    // A UAV that loses a CLAIM stays available for other regions instead of
    // flying home. 0 restores the old go-home behaviour (the ablation).
    void SetStayAvailable(bool v) { m_stayAvailable = v; }
    // Report a position only for a CONFIRMED delivery. 0 restores reporting the
    // aim as soon as it is claimed (the ablation).
    void SetFixOnConfirm(bool v) { m_fixOnConfirm = v; }
    // D36: carry a confirmed fix home immediately (1) or keep serving
    // candidates first (0). See SarScenarioConfig::fixFirst for the measured
    // trade -- the two settings are opposite corners, not better and worse.
    void SetFixFirst(bool v) { m_fixFirst = v; }
    // Reliability/cost knob: how long to keep delivering after arriving. CONFIRM
    // can come from a bystander under the drop point, so a short dwell strands a
    // victim that sits further out.
    void SetDeliverDwell(double s) { m_deliverDwellS = s; }

    bool OnReceive(ns3::Ptr<ns3::NetDevice> dev, ns3::Ptr<const ns3::Packet> pkt,
                   uint16_t proto, const ns3::Address& from);

private:
    void StartApplication() override;
    void StopApplication() override;
    void TakeOff();
    void ControlTick();
    void TrajTick();
    void SendFullChunk(size_t fi, uint16_t seq);
    void PatrolCueTick();               // spread cues while patrolling
    void SendReport();
    void ClaimDivert();                 // won the radio CLAIM -> divert+deliver
    void SendClaim(uint8_t role);       // broadcast a role claim (mutual exclusion)
    void TryClaimDivert(double x, double y);
    // D32: cooperative task division over A2A. Every DATA UAV keeps the same
    // candidate table, built purely from radio traffic (A2A carries a region and
    // its aim, a peer's CLAIM says who took it, CONFIRM/REJECT says it is done),
    // and picks the NEAREST region nobody has taken. The claim backoff is
    // proportional to that distance, so the nearest UAV speaks first and the
    // others see the claim and move on to their own region.
    void ConsiderTasks();
    // D32: this region is settled (CONFIRM or REJECT). Release it and take the
    // next unserved candidate; fly home only when there is nothing left. Without
    // this a UAV served exactly ONE point per mission however many candidates
    // existed, which is the behaviour the whole multi-candidate design exists to
    // remove.
    void ReleaseAndContinue();
    // True if a peer has claimed a place within kRegionRadiusM of (x,y).
    bool PeerServingNear(double x, double y, uint16_t* who = nullptr) const;

    enum class State { IDLE, CLIMB, GOTO_CENTER, LOITER, PATROL, DIVERT, DELIVER, SWEEP, RETURN, DONE };

    // Phase gate. With --phaseGate the rotary team is Phase 2 proper: it stages
    // near the BS and does not enter the field until the fixed-wing team has
    // announced every band swept (CLAIM role 3, one per FAST UAV). That makes
    // Phase 1 attributable -- the screening coverage and the candidate set are
    // then produced by the FAST team ALONE, with no DATA cueing mixed in.
    //
    // The gate is radio-only, like every other coordination rule here, so it can
    // fail closed: if the announcements are never heard the DATA team would
    // never start, and the mission would silently deliver nothing. m_gateDeadline
    // is the bound that stops that.
    bool m_phaseGate = false;
    uint32_t m_expectFast = 0;
    double m_gateDeadlineS = 0;
    bool m_gateOpen = false;
    // Where the rotary team waits. Staging AIRBORNE over the field centre keeps
    // it one hop from any leader, but a rotary wing pays full hover power to do
    // nothing: measured, 190 s of staging cost +36 % mission energy. Waiting on
    // the ground costs nothing and is what a real crew would do; the price is
    // the transit from the BS once the gate opens, and a weaker radio position
    // while waiting (which is why the deadline exists).
    bool m_gateGround = false;
    bool GateOpen() const {
        if (!m_phaseGate || m_gateOpen) return true;
        return m_sweepDone.size() >= m_expectFast;
    }
    void OpenGate();          // leave staging, begin the patrol plan

    uint32_t m_nodeId = 0;
    ns3::Ptr<ns3::NetDevice> m_dev;
    SarMetrics* m_metrics = nullptr;
    Mode m_mode = Mode::SUMMONED;
    std::vector<Fragment> m_full;
    std::vector<Fragment> m_cues;       // cue fragments spread while patrolling
    bool m_patrol = true;
    bool m_cueEnroute = true;
    bool m_patrolReverse = false;
    bool m_stayAvailable = true;
    bool m_fixOnConfirm = true;
    bool m_fixFirst = true;
    size_t m_cueIdx = 0;
    uint16_t m_cueSeq = 0;
    uint32_t m_cueTxCount = 0;
    ns3::EventId m_cueEvent;
    std::vector<ns3::Vector> m_sensors;   // for SWEEP_DUMP GMC
    std::vector<ns3::Vector> m_tourOverride;  // tsp-mc: pre-planned VBS tour
    bool m_reportAtEnd = false;               // tsp-mc: tour -> BS -> REPORT
    bool m_mcDwell = false;                   // use the redundancy dwell
    double m_mcRedundancy = 3.0;              // tsp-mc: coded-multicast overhead
    bool m_allHome = true;                    // audit F2: always fly home
    std::vector<ns3::Vector> m_targets;
    size_t m_ti = 0;
    double m_radius = 50.0;
    double m_alt = 20.0, m_speed = 15.0;
    ns3::Vector m_loiter{0, 0, 0};
    ns3::Vector m_divert{0, 0, 0};
    ns3::Vector m_bsPos{0, 0, 0};
    ns3::Address m_bsAddr;
    ns3::Ptr<ns3::UniformRandomVariable> m_rng;
    bool m_claimed = false;
    bool m_yieldedDivert = false;   // heard another UAV's CLAIM first -> stand down
    double m_pendX = 0, m_pendY = 0;
    ns3::EventId m_claimEvent;
    bool m_pendingDivert = false;   // claimed before airborne; divert after climb
    bool m_dwellStarted = false;    // dwell clock runs once per region, not per re-aim
    bool m_lostLogged = false;      // diagnostic: left the world, logged once
    bool m_confirmed = false;
    uint16_t m_boundRegion = 0xFFFF;  // leader whose re-aims we accept
    // D32: shared picture of the work, kept per UAV from what it heard.
    // served = how many delivery dwells this place has already had. Selection is
    // BREADTH-FIRST: every candidate gets one delivery before any gets a second.
    // closed = settled outright by a CONFIRM or a REJECT.
    struct Task { double x = 0, y = 0; uint16_t takenBy = 0xFFFF;
                  bool closed = false; uint8_t served = 0;
                  // known = we have heard this region's AIM (from an A2A). A
                  // CLAIM tells us a region is taken but not where it is, and
                  // std::map::operator[] happily created an entry at (0,0) for
                  // it -- which then both defeated the same-place check and
                  // became a selectable job at the origin.
                  bool known = false;
                  double takenAt = -1e9; };   // claim = lease, see kClaimLeaseS
    std::map<uint16_t, Task> m_tasks;
    uint16_t m_myTask = 0xFFFF;       // region I intend to claim, or am serving
    std::set<uint16_t> m_sweepDone;   // FAST UAVs that announced their sweep done
    double m_lastCueHeardS = -1;      // last time a FAST UAV was heard cueing
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
    }          // audit B3: carry the victim fix home
    double m_fixX = 0, m_fixY = 0;
    double m_deliverDwellS = params::kMinDeliverDwellS;
    double m_divertStartDist = 0;
    double m_dwellUntil = 0;        // SWEEP_DUMP: cycle chunks until this time
    uint32_t m_reportsSent = 0;     // REPORT retransmissions (bounded)
    uint32_t m_handoffsSent = 0;    // HANDOFF broadcasts to the FAST team
    double m_deliverUntil = 0;      // keep delivering (coverage dwell) until this
    void SendHandoff();
    void BeginReturn();             // stop delivering, head home + hand off
    uint32_t m_fullTxCount = 0;     // for decimated viz markers

    State m_state = State::IDLE;
    ns3::EventId m_ctrl, m_traj;
    FlightController m_fc;
};

}  // namespace ns3::uavsar

#endif  // UAV_SAR_DATA_UAV_APP_H
