#include "sar-data-uav-app.h"
#include "../common/sar-metrics.h"
#include "../common/sar-types.h"
#include "../common/sar-params.h"

#include "../common/gmc.h"

#include "ns3/core-module.h"
#include "ns3/packet.h"
#include "ns3/mac16-address.h"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstring>

using namespace ns3;

namespace ns3::uavsar {

NS_OBJECT_ENSURE_REGISTERED(SarDataUavApp);

TypeId SarDataUavApp::GetTypeId() {
    static TypeId tid = TypeId("ns3::uavsar::SarDataUavApp")
                            .SetParent<Application>().SetGroupName("uav-sar")
                            .AddConstructor<SarDataUavApp>();
    return tid;
}
SarDataUavApp::SarDataUavApp() : m_rng(CreateObject<UniformRandomVariable>()) {}
SarDataUavApp::~SarDataUavApp() = default;

void SarDataUavApp::StartApplication() {
    m_fc.AttachTo(GetNode());
    Simulator::Schedule(Seconds(1.0 + 0.3 * m_nodeId), &SarDataUavApp::TakeOff, this);
}
void SarDataUavApp::StopApplication() {
    Simulator::Cancel(m_ctrl); Simulator::Cancel(m_traj); Simulator::Cancel(m_claimEvent);
    Simulator::Cancel(m_cueEvent);
    m_fc.Hover(); m_fc.SetClimb(0);
}

void SarDataUavApp::TakeOff() {
    // Ground hold: Phase 2 has not started, so there is nothing worth being
    // airborne for. Re-arm and check again rather than climbing to burn hover
    // power over an empty task list. The radio is already listening, so the
    // sweep-done CLAIM still reaches us here; the deadline covers the case
    // where it does not.
    if (m_phaseGate && m_gateGround && !m_gateOpen && !GateOpen() &&
        Simulator::Now().GetSeconds() < m_gateDeadlineS) {
        Simulator::Schedule(Seconds(1.0), &SarDataUavApp::TakeOff, this);
        return;
    }
    if (m_metrics) { Vector p = m_fc.GetPosition();
        m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "DATA", "takeoff", "", p.x, p.y, p.z); }
    if (m_mode == Mode::SWEEP_DUMP) {
        // plan sweep with the design coverage radius (see FAST app note).
        m_radius = params::kUavBroadcastRadiusM;
        m_targets = m_tourOverride.empty()
                        ? BuildGmc(m_sensors, m_radius, m_fc.GetPosition(), m_alt, m_speed)
                        : m_tourOverride;   // tsp-mc: pre-planned VBS/TSP tour
        m_ti = 0;
    } else if (m_patrol && !m_sensors.empty()) {
        // Waiting productively: the same greedy coverage plan the FAST team
        // flies, over this UAV's own band. Being IN MOTION over the field is
        // what makes it reachable by a one-hop SUMMON at all.
        m_radius = params::kUavBroadcastRadiusM;
        m_targets = BuildGmc(m_sensors, m_radius, m_fc.GetPosition(), m_alt, m_speed);
        if (m_patrolReverse) std::reverse(m_targets.begin(), m_targets.end());
        m_ti = 0;
    }
    // A rotary wing turns on the spot: its escape circle is a point, so a small
    // nominal radius is all the filter needs from it.
    m_fc.SetNoFlyZones(m_zones, 5.0, m_speed, params::kControlTickS);
    m_state = State::CLIMB; m_fc.Hover(); m_fc.SetClimb(params::kClimbRateMps);
    // Start cueing from the climb: a DATA UAV that has not been summoned yet is
    // still a data source in motion over the field.
    if (m_mode == Mode::SUMMONED && m_cueEnroute && !m_phaseGate && !m_cues.empty())
        PatrolCueTick();
    m_ctrl = Simulator::Schedule(Seconds(params::kControlTickS), &SarDataUavApp::ControlTick, this);
    TrajTick();
}

void SarDataUavApp::OpenGate() {
    if (m_gateOpen) return;
    m_gateOpen = true;
    const double t = Simulator::Now().GetSeconds();
    Vector p = m_fc.GetPosition();
    if (m_metrics) {
        char det[96];
        const char* mode = m_gateMode == GateMode::Home ? "home"
                           : m_gateMode == GateMode::Flag ? "flag" : "sweep";
        const char* why = GateOpen() ? "trigger"
                          : (t >= m_gateDeadlineS ? "deadline" : "sky-quiet");
        std::snprintf(det, sizeof det, "%s/%s; swept %u landed %u flag %d of %u",
                      mode, why, (unsigned)m_sweepDone.size(),
                      (unsigned)m_landed.size(), m_launchOrder ? 1 : 0,
                      (unsigned)m_expectFast);
        m_metrics->Event(t, m_nodeId, "DATA", "gate_open", det, p.x, p.y, p.z);
    }
    // Phase 2 begins. If this UAV already has a job it keeps it; otherwise it
    // starts its patrol so it is IN MOTION over the field and reachable by a
    // one-hop SUMMON -- a UAV parked at the staging point can only be summoned
    // by a leader within one hop of the BS corner.
    if (m_state == State::IDLE) return;   // ground hold: TakeOff() picks it up
    if (m_claimed || m_state == State::DIVERT || m_state == State::DELIVER ||
        m_state == State::RETURN || m_state == State::DONE)
        return;
    if (m_patrol && !m_targets.empty()) {
        m_ti = 0;
        m_state = State::PATROL;
        Vector t0 = m_targets[m_ti];
        m_fc.Turn(std::atan2(t0.y - p.y, t0.x - p.x) * 180 / M_PI);
        m_fc.Forward(m_speed);
    }
    ConsiderTasks();          // candidates may already be waiting
}

void SarDataUavApp::SendClaim(uint8_t role) {
    if (!m_dev) return;
    std::vector<uint8_t> b(kClaimLen);
    uint8_t* q = b.data();
    *q++ = (uint8_t)Msg::CLAIM;
    // The region this UAV is claiming. It used to be hardcoded to 1, which made
    // per-region mutual exclusion impossible: every DATA UAV yielded to every
    // claim regardless of which region it was for, so one summon consumed the
    // whole team. Measured at 24x24 with two candidate places: one UAV diverted
    // and the other three yielded within the same millisecond, leaving the
    // second place with nobody.
    uint16_t rid = m_boundRegion; std::memcpy(q, &rid, 2); q += 2;
    *q++ = role;
    uint16_t id = (uint16_t)m_nodeId; std::memcpy(q, &id, 2);
    m_dev->Send(Create<Packet>(b.data(), b.size()), Mac16Address("ff:ff"), 0);
    if (m_metrics) { m_metrics->AddSent(); m_metrics->AddSentBytes(b.size()); }
}

bool SarDataUavApp::PeerServingNear(double x, double y, uint16_t* who) const {
    for (const auto& [rid, t] : m_tasks) {
        if (!t.known) continue;
        if (t.takenBy == 0xFFFF || t.takenBy == (uint16_t)m_nodeId) continue;
        // A claim is a LEASE. A peer that went home, or whose release we never
        // heard, must not reserve a candidate for the rest of the mission.
        if (Simulator::Now().GetSeconds() - t.takenAt > params::kClaimLeaseS) continue;
        if (std::hypot(t.x - x, t.y - y) <= params::kRegionRadiusM) {
            if (who) *who = t.takenBy;
            return true;
        }
    }
    return false;
}

void SarDataUavApp::ConsiderTasks() {
    // Choose the nearest region that is not closed and that no peer has claimed.
    // Backoff before claiming is proportional to that distance, so among the UAVs
    // that want the same region the NEAREST one speaks first and the rest hear
    // the claim and re-run this, landing on a different region. That is the whole
    // coordination protocol: one message type (CLAIM) and one rule.
    if (m_claimed || m_yieldedDivert) return;
    if (m_state == State::DELIVER || m_state == State::RETURN || m_state == State::DONE)
        return;
    // The phase gate belongs HERE, not only on the patrol start. Gating the
    // patrol and the cueing looked like it separated the phases and did not:
    // a staging UAV still heard RCLAIM, still claimed, and still flew off to
    // deliver. Measured with the gate nominally on: deliveries at t = 41-128 s
    // against a gate that opened at t = 189 s -- every candidate was served
    // during Phase 1. Taking a job is what "starting" means, so that is what
    // the gate has to hold back.
    if (!GateOpen()) return;
    Vector p = m_fc.GetPosition();
    uint16_t best = 0xFFFF;
    double bestD = 0;
    for (const auto& [rid, t] : m_tasks) {
        if (!t.known) continue;          // heard OF it, do not know WHERE
        if (t.closed) continue;
        if (t.takenBy != 0xFFFF && t.takenBy != (uint16_t)m_nodeId &&
            Simulator::Now().GetSeconds() - t.takenAt <= params::kClaimLeaseS) continue;
        // Two leaders in adjacent cells can elect before either hears the
        // other's RCLAIM and summon the SAME PLACE under different region ids.
        // Measured at 24x24 with eight UAVs: two DATA UAVs delivered to points
        // 3 m apart. Region identity is not enough -- a job is taken if a peer
        // has taken any job about the same place.
        if (PeerServingNear(t.x, t.y)) continue;
        double d = std::hypot(t.x - p.x, t.y - p.y);
        if (best == 0xFFFF || d < bestD) { best = rid; bestD = d; }
    }
    if (best == 0xFFFF) {              // nothing left that is ours to do
        Simulator::Cancel(m_claimEvent);
        m_myTask = 0xFFFF;
        return;
    }
    if (best == m_myTask && m_claimEvent.IsPending()) return;   // already going for it
    m_myTask = best;
    m_pendX = m_tasks[best].x;
    m_pendY = m_tasks[best].y;
    Simulator::Cancel(m_claimEvent);
    // Distance-proportional backoff, normalised by a field-scale constant so the
    // ordering is by distance and the absolute wait stays inside the claim
    // window. Jitter breaks exact ties between equidistant UAVs.
    const double scale = std::min(1.0, bestD / 800.0);
    m_claimEvent = Simulator::Schedule(
        Seconds(params::kClaimBackoffS * scale + m_rng->GetValue(0.0, params::kFwdStaggerMaxS)),
        &SarDataUavApp::ClaimDivert, this);
}

void SarDataUavApp::ClaimDivert() {
    if (m_yieldedDivert || m_claimed) return;   // someone else already claimed
    if (m_myTask == 0xFFFF) return;
    auto it = m_tasks.find(m_myTask);
    // It may have been taken or settled while we were backing off.
    if (it == m_tasks.end() || it->second.closed ||
        (it->second.takenBy != 0xFFFF && it->second.takenBy != (uint16_t)m_nodeId)) {
        ConsiderTasks();
        return;
    }
    m_boundRegion = m_myTask;                   // bind BEFORE announcing
    m_dwellStarted = false;
    it->second.takenBy = (uint16_t)m_nodeId;
    it->second.takenAt = Simulator::Now().GetSeconds();
    SendClaim(0);                               // announce on the radio, then act
    TryClaimDivert(m_pendX, m_pendY);
}

void SarDataUavApp::TryClaimDivert(double x, double y) {
    if (m_claimed || m_state == State::DELIVER || m_state == State::RETURN) return;
    m_claimed = true;
    Vector p = m_fc.GetPosition();
    // audit B3: the SUMMON coordinates ARE the localization output. Hold them so
    // they can be flown home in the REPORT (or handed to a courier) — until this
    // the BS learned only *that* a delivery happened, never *where*.
    // Hold the coordinates for the delivery, but do NOT yet call them a fix.
    // Reporting an UNCONFIRMED aim is worse than reporting nothing once several
    // regions are being served at once: whichever UAV reaches the BS first wins,
    // and it may be the one that delivered to a confusable object. Measured at
    // 24x24: victim served 52.5% while the reported position had a 90 m median
    // error -- the victim was reached and the rescue team was sent elsewhere.
    // D32: never overwrite a CONFIRMED fix with the next job's unconfirmed aim.
    // A UAV that confirmed victim 2 and then took a third candidate carried the
    // third candidate's coordinates home -- measured: both victims received the
    // full dataset, yet victimsLocated stayed 1/2.
    if (!m_hasFix) { m_fixX = x; m_fixY = y; }
    if (!m_fixOnConfirm) m_hasFix = true;
    m_divert = Vector(x, y, m_alt);
    m_divertStartDist = std::hypot(x - p.x, y - p.y);
    // If already cruising (loiter/en-route), divert now; if still on the ground
    // or climbing, remember it and divert once we reach cruise altitude — else a
    // late TakeOff would clobber the DIVERT state.
    if (m_state == State::LOITER || m_state == State::GOTO_CENTER ||
        m_state == State::PATROL)
        m_state = State::DIVERT;
    else
        m_pendingDivert = true;
    if (m_metrics) {
        m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "DATA", "divert", "to region", p.x, p.y, p.z);
        m_metrics->AddDeviation(m_divertStartDist);
    }
}

void SarDataUavApp::ControlTick() {
    Vector p = m_fc.GetPosition();
    double arriveR = std::max(1.0, m_speed * params::kControlTickS * 1.5);
    switch (m_state) {
        case State::CLIMB:
            if (p.z >= m_alt) {
                m_fc.SetClimb(0);
                if (m_mode == Mode::SWEEP_DUMP) {
                    if (m_targets.empty()) { m_state = State::DONE; return; }
                    m_state = State::SWEEP;
                    Vector t = m_targets[m_ti];
                    m_fc.Turn(std::atan2(t.y - p.y, t.x - p.x) * 180 / M_PI); m_fc.Forward(m_speed);
                } else if (m_pendingDivert) {   // claimed before takeoff -> region
                    m_pendingDivert = false;
                    m_state = State::DIVERT;
                } else if (m_patrol && !m_targets.empty() && GateOpen()) {
                    m_state = State::PATROL;
                    Vector t = m_targets[m_ti];
                    m_fc.Turn(std::atan2(t.y - p.y, t.x - p.x) * 180 / M_PI);
                    m_fc.Forward(m_speed);
                    if (!m_cueEvent.IsPending()) PatrolCueTick();
                } else {
                    m_state = State::GOTO_CENTER;
                    m_fc.Turn(std::atan2(m_loiter.y - p.y, m_loiter.x - p.x) * 180 / M_PI);
                    m_fc.Forward(m_speed);
                }
            }
            break;
        case State::SWEEP: {
            Vector t = m_targets[m_ti];
            if (std::hypot(t.x - p.x, t.y - p.y) <= arriveR) {
                m_fc.Hover(); m_state = State::DELIVER;
                // blind dwell: cycle chunks with no ground feedback. tsp-mc sizes
                // the connection time as kMcRedundancy x the dataset airtime (the
                // coded-multicast overhead of Zeng'18: send extra to ride out
                // drops); nocoop keeps the fixed design budget.
                double dwell = params::kBaselineDwellS;
                if (m_mcDwell) {
                    uint32_t chunks = 0;
                    for (const auto& f : m_full)
                        chunks += std::max(1u, (f.sizeBytes + kChunkBytes - 1) / kChunkBytes);
                    dwell = m_mcRedundancy * chunks * params::kDeliverStaggerS;
                }
                m_dwellUntil = Simulator::Now().GetSeconds() + dwell;
                SendFullChunk(0, 0);
            }
            break;
        }
        case State::GOTO_CENTER:
            if (std::hypot(m_loiter.x - p.x, m_loiter.y - p.y) <= arriveR) {
                m_fc.Hover(); m_state = State::LOITER; }
            if (m_phaseGate && !m_gateOpen &&
                (GateOpen() || Simulator::Now().GetSeconds() >= m_gateDeadlineS))
                OpenGate();
            break;
        case State::PATROL: {
            // Fly the coverage plan while remaining divertible. When the plan is
            // exhausted the UAV keeps station where it is: it is still the only
            // thing that can accept a summon, and the sky-quiet rule below (via
            // LOITER) bounds how long that lasts.
            // OUT-OF-BOUNDS READ, and it produced a runaway aircraft.
            // ReleaseAndContinue and the yield paths set PATROL unconditionally,
            // but by then the patrol plan is often already exhausted, so
            // m_targets[m_ti] indexed past the end. The UAV picked up whatever
            // that memory held as a waypoint and flew toward it at constant
            // heading for the rest of the run: measured at 24x24 seed 8, DATA
            // uav4 left the field after its delivery at t=47 s and was still
            // flying due south at t=500 s, 6 177 m off the map, deaf to
            // everything and serving nothing.
            if (m_ti >= m_targets.size()) {
                m_fc.Hover();
                m_state = State::LOITER;
                break;
            }
            Vector t = m_targets[m_ti];
            // CONTINUOUS guidance, the same fix the FAST app needed. The heading
            // used to be commanded only on reaching a waypoint, so a UAV that
            // entered PATROL from anywhere else -- ReleaseAndContinue, a yield --
            // kept whatever heading it happened to hold and flew that way for
            // ever. Diagnosed by logging the state on leaving the world:
            // `state=PATROL spd=15.0 hdg=-90` at 3 km south, still "patrolling".
            m_fc.Turn(std::atan2(t.y - p.y, t.x - p.x) * 180 / M_PI);
            m_fc.Forward(m_speed);
            if (std::hypot(t.x - p.x, t.y - p.y) <= arriveR) {
                m_ti++;
                if (m_ti >= m_targets.size()) {
                    m_fc.Hover();
                    m_state = State::LOITER;   // plan done; sky-quiet rule takes over
                } else {
                    Vector n = m_targets[m_ti];
                    m_fc.Turn(std::atan2(n.y - p.y, n.x - p.x) * 180 / M_PI);
                    m_fc.Forward(m_speed);
                }
            }
            break;
        }
        case State::LOITER:
            if (m_phaseGate && !m_gateOpen &&
                (GateOpen() || Simulator::Now().GetSeconds() >= m_gateDeadlineS)) {
                OpenGate();
                break;
            }
            // LOITER means STOPPED. Saying so every tick, rather than trusting
            // whoever set the state to have called Hover(), is what makes it
            // true: the runaway that survived the out-of-bounds fix was a UAV
            // dropped into LOITER by the yield path while the flight controller
            // still held the last heading and speed, so it flew straight out of
            // the world at cruise speed. Measured: seed 8, DATA uav4 left at
            // t=67 s and was 6 km south by the horizon.
            m_fc.Hover();
            // Wait for an A2A relay -- but not forever. If the sky has gone
            // quiet (no FAST UAV cueing for kSkyQuietS) the sweep is over and
            // no summon is coming, so under the all-home rule there is nothing
            // left to wait for. The trigger is an OBSERVED radio silence, not a
            // clock, so it scales with the field instead of against it.
            if (m_allHome && !m_claimed && m_lastCueHeardS > 0 &&
                Simulator::Now().GetSeconds() - m_lastCueHeardS > params::kSkyQuietS) {
                // Under the phase gate the SAME observation means the opposite
                // thing. A quiet sky is exactly what "the fixed-wing team has
                // stopped sweeping" sounds like from the staging point, so it is
                // the signal to START, not to go home.
                //
                // This is also what makes the gate safe. Keying it solely on the
                // sweep-done CLAIM made it fail closed on one lost broadcast:
                // measured over 5 seeds, one seed opened NO gate at all and
                // another opened only one of two, and those DATA UAVs sat at the
                // staging point for the whole mission. A gate that depends on a
                // single unacknowledged packet is not a gate.
                if (m_phaseGate && !m_gateOpen) { OpenGate(); break; }
                m_state = State::RETURN;
                if (m_metrics) {
                    m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "DATA",
                                     "quiet_return", "no cues, no summon", p.x, p.y, p.z);
                }
            }
            break;
        case State::DIVERT: {
            double d = std::hypot(m_divert.x - p.x, m_divert.y - p.y);
            m_fc.Turn(std::atan2(m_divert.y - p.y, m_divert.x - p.x) * 180 / M_PI);
            m_fc.Forward(m_speed);
            if (d <= arriveR) {
                // D32: last check before committing. Claims race and travel
                // takes tens of seconds, so a peer can take this place while we
                // are still flying to it. Measured: two DATA UAVs delivering 1 m
                // apart, twice in one run. Lower id keeps the place; the other
                // turns around rather than doubling up.
                uint16_t who = 0xFFFF;
                if (PeerServingNear(m_divert.x, m_divert.y, &who) &&
                    who < (uint16_t)m_nodeId) {
                    if (m_metrics)
                        m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "DATA",
                                         "yield_stay", "peer already serving this place",
                                         p.x, p.y, p.z);
                    // Just step aside: we never delivered here, so this must
                    // NOT count as a served dwell (that would push the place
                    // down the breadth-first order while a peer is still on it).
                    m_claimed = false;
                    m_yieldedDivert = false;
                    m_myTask = 0xFFFF;
                    m_boundRegion = 0xFFFF;
                    m_state = (m_ti < m_targets.size()) ? State::PATROL : State::LOITER;
                    ConsiderTasks();   // stay available if nothing right now
                    break;
                }
                m_fc.Hover(); m_state = State::DELIVER;
                // Only the FIRST arrival in a region starts the dwell clock. A
                // leader re-aim moves the hover point by a few tens of metres
                // and used to restart the whole 382-chunk delivery, which is
                // where 14 of the 35 repeat episodes came from.
                const bool first = !m_dwellStarted;
                if (first) {
                    m_dwellStarted = true;
                    m_deliverUntil = Simulator::Now().GetSeconds() + m_deliverDwellS;
                }
                // A re-aim resumes the SAME delivery at a shifted hover point.
                // Labelling it deliver_start made the analysis count it as a
                // second service of the place: 12 of the 13 apparent repeats
                // were this, and the UAV had never left the region.
                if (m_metrics) m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "DATA",
                                                first ? "deliver_start" : "deliver_move",
                                                "", p.x, p.y, p.z);
                SendFullChunk(0, 0); }
            break;
        }
        case State::DELIVER:
            break;  // delivery chain runs; then we wait for CONFIRM
        case State::RETURN: {
            double d = std::hypot(m_bsPos.x - p.x, m_bsPos.y - p.y);
            m_fc.Turn(std::atan2(m_bsPos.y - p.y, m_bsPos.x - p.x) * 180 / M_PI);
            m_fc.Forward(m_speed);
            if (d <= arriveR) {
                m_fc.Hover(); m_state = State::DONE;
                if (m_metrics) m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "DATA",
                                                "report_tx", "to BS", p.x, p.y, p.z);
                SendReport();   // retried until quota (F2: no single-shot loss)
                return;
            }
            break;
        }
        case State::IDLE: case State::DONE: return;
    }
    m_ctrl = Simulator::Schedule(Seconds(params::kControlTickS), &SarDataUavApp::ControlTick, this);
}

void SarDataUavApp::SendFullChunk(size_t fi, uint16_t seq) {
    if (m_state != State::DELIVER || m_full.empty()) return;  // stopped / nothing to send
    if (fi >= m_full.size()) {
        // One full pass over the dataset finished.
        if (m_mode == Mode::SWEEP_DUMP) {
            if (Simulator::Now().GetSeconds() < m_dwellUntil) {
                SendFullChunk(0, 0);   // keep cycling within the dwell budget
                return;
            }
            m_ti++;
            Vector p = m_fc.GetPosition();
            if (m_ti >= m_targets.size()) {
                // tsp-mc: mission ends only when the UAV is back at the BS and
                // the report is received — fly home now (ControlTick services it).
                m_state = m_reportAtEnd ? State::RETURN : State::DONE;
                return;
            }
            m_state = State::SWEEP;
            Vector t = m_targets[m_ti];
            m_fc.Turn(std::atan2(t.y - p.y, t.x - p.x) * 180 / M_PI); m_fc.Forward(m_speed);
            // ControlTick is still looping (from DELIVER); it will service SWEEP.
            return;
        }
        // SUMMONED: cycle so lost chunks get retransmitted -- but only until the
        // delivery dwell expires.
        //
        // D32: this used to cycle FOREVER, ending only on a CONFIRM for this
        // region. At a confusable object no CONFIRM ever comes, so the UAV
        // delivered to a decoy until the horizon and served exactly ONE place
        // per mission however many candidates existed. This is the single line
        // behind "the DATA team only ever serves one point".
        if (Simulator::Now().GetSeconds() >= m_deliverUntil) {
            ReleaseAndContinue();
            return;
        }
        SendFullChunk(0, 0);
        return;
    }
    const Fragment& f = m_full[fi];
    uint16_t total = (uint16_t)std::max(1u, (f.sizeBytes + kChunkBytes - 1) / kChunkBytes);
    if (m_dev) {
        uint32_t payloadLen = std::min(kChunkBytes, f.sizeBytes - seq * kChunkBytes);
        std::vector<uint8_t> b(kChunkHdr + payloadLen, 0);
        uint8_t* p = b.data();
        *p++ = (uint8_t)Msg::FULL; *p++ = kBroadcast;
        uint16_t id = (uint16_t)f.id; std::memcpy(p, &id, 2); p += 2;
        std::memcpy(p, &seq, 2); p += 2;
        std::memcpy(p, &total, 2); p += 2;
        *p++ = (uint8_t)f.layer;
        m_dev->Send(Create<Packet>(b.data(), b.size()), Mac16Address("ff:ff"), 0);
        if (m_metrics) {
            m_metrics->AddSent(); m_metrics->AddSentBytes(b.size());
            // viz: decimated A2G full-data broadcast marker (1 in 50 chunks)
            if (++m_fullTxCount % 50 == 1) {
                Vector p = m_fc.GetPosition();
                m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "DATA",
                                 "full_tx", "", p.x, p.y, p.z);
            }
        }
    }
    uint16_t ns = seq + 1; size_t nf = fi;
    if (ns >= total) { ns = 0; nf = fi + 1; }
    Simulator::Schedule(Seconds(params::kDeliverStaggerS), &SarDataUavApp::SendFullChunk, this, nf, ns);
}

void SarDataUavApp::PatrolCueTick() {
    // Byte-identical to the FAST team's cue dissemination, so a cue costs the
    // same wherever it came from. Stops the moment this UAV has a delivery task.
    //
    // A DATA UAV is airborne from takeoff, and radio time spent flying to a
    // staging point is radio time that costs NOTHING extra: the flight is
    // happening either way. It therefore cues on every leg before it has a
    // delivery -- climbing, transiting, loitering, patrolling -- not only while
    // patrolling. That is different from --dataPatrol, which buys coverage by
    // flying an EXTRA tour and was measured net-negative; this buys coverage
    // along a path already being flown.
    // With --phaseGate the two phases are separated BY FUNCTION, not just in
    // time: the fixed-wing team cues (screening) and the rotary team delivers
    // (confirmation). Without that, DATA cueing lands in the middle of the very
    // measurement Phase 1 is supposed to own, and the screening coverage can no
    // longer be attributed to the FAST team.
    const bool cueing = m_phaseGate
        ? false
        : (m_cueEnroute
               ? (m_state == State::CLIMB || m_state == State::GOTO_CENTER ||
                  m_state == State::LOITER || m_state == State::PATROL)
               : (m_state == State::PATROL));
    if (cueing && !m_cues.empty() && m_dev) {
        const Fragment& f = m_cues[m_cueIdx % m_cues.size()];
        uint16_t total = (uint16_t)std::max(1u, (f.sizeBytes + kChunkBytes - 1) / kChunkBytes);
        uint32_t payloadLen = std::min(kChunkBytes, f.sizeBytes - m_cueSeq * kChunkBytes);
        std::vector<uint8_t> b(kChunkHdr + payloadLen, 0);
        uint8_t* q = b.data();
        *q++ = (uint8_t)Msg::CUE; *q++ = kBroadcast;
        uint16_t id = (uint16_t)f.id; std::memcpy(q, &id, 2); q += 2;
        std::memcpy(q, &m_cueSeq, 2); q += 2;
        std::memcpy(q, &total, 2); q += 2;
        *q++ = (uint8_t)f.layer;
        m_dev->Send(Create<Packet>(b.data(), b.size()), Mac16Address("ff:ff"), 0);
        if (m_metrics) {
            m_metrics->AddSent(); m_metrics->AddSentBytes(b.size());
            if (++m_cueTxCount % 25 == 1) {
                Vector p = m_fc.GetPosition();
                m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "DATA",
                                 "cue_tx", m_state == State::PATROL ? "patrol" : "enroute",
                                 p.x, p.y, p.z);
            }
        }
        m_cueSeq++;
        if (m_cueSeq >= total) { m_cueSeq = 0; m_cueIdx = (m_cueIdx + 1) % m_cues.size(); }
    }
    if (cueing)
        m_cueEvent = Simulator::Schedule(Seconds(params::kDisseminateStaggerS),
                                         &SarDataUavApp::PatrolCueTick, this);
}

void SarDataUavApp::SendReport() {
    if (m_reportsSent >= params::kReportRetries) return;
    if (m_dev) {
        // Only as a fallback: the confirm path already accumulated this place,
        // and re-adding it here would double-count one sample in the centroid.
        if (m_hasFix && m_fixes.empty()) AddFix(m_fixX, m_fixY);
        std::vector<uint8_t> b(kReportLen, 0);
        uint8_t* q = b.data();
        *q++ = (uint8_t)Msg::REPORT;
        *q++ = m_fixes.empty() ? 0x00 : kFlagHasFix;
        *q++ = (uint8_t)m_fixes.size();
        for (const auto& f : m_fixes) {
            int16_t fx = (int16_t)std::lround(f.first * 10.0);
            int16_t fy = (int16_t)std::lround(f.second * 10.0);
            std::memcpy(q, &fx, 2); q += 2; std::memcpy(q, &fy, 2); q += 2;
        }
        m_dev->Send(Create<Packet>(b.data(), b.size()), m_bsAddr, 0);
        if (m_metrics) { m_metrics->AddSent(); m_metrics->AddSentBytes(b.size()); }
    }
    m_reportsSent++;
    Simulator::Schedule(Seconds(params::kReportRetryS), &SarDataUavApp::SendReport, this);
}

void SarDataUavApp::SendHandoff() {
    if (m_handoffsSent >= params::kConfirmRetries) return;
    if (m_dev) {
        std::vector<uint8_t> b(kHandoffLen, 0);
        uint8_t* q = b.data();
        *q++ = (uint8_t)Msg::HANDOFF; *q++ = m_hasFix ? kFlagHasFix : 0x00;
        uint16_t rid = 1; std::memcpy(q, &rid, 2); q += 2;
        // audit B3: the courier must inherit the fix, otherwise handing the
        // report to a faster UAV would silently throw the location away.
        int16_t fx = (int16_t)std::lround(m_fixX * 10.0);
        int16_t fy = (int16_t)std::lround(m_fixY * 10.0);
        std::memcpy(q, &fx, 2); q += 2; std::memcpy(q, &fy, 2);
        m_dev->Send(Create<Packet>(b.data(), b.size()), Mac16Address("ff:ff"), 0);
        if (m_metrics) { m_metrics->AddSent(); m_metrics->AddSentBytes(b.size()); }
    }
    m_handoffsSent++;
    Simulator::Schedule(Seconds(params::kConfirmRetryS), &SarDataUavApp::SendHandoff, this);
}

static const char* StateName(int s) {
    static const char* n[] = {"IDLE","CLIMB","GOTO_CENTER","LOITER","PATROL",
                              "DIVERT","DELIVER","SWEEP","RETURN","DONE"};
    return (s >= 0 && s < 10) ? n[s] : "?";
}

void SarDataUavApp::TrajTick() {
    // Diagnostic: a UAV that leaves the world says so ONCE, with the state it is
    // in. Three fixes in a row produced byte-identical results because each was
    // aimed at a state the aircraft was not actually in; guessing a fourth time
    // is not a method.
    if (!m_lostLogged && m_metrics) {
        Vector q = m_fc.GetPosition();
        if (std::abs(q.x) > 3000 || std::abs(q.y) > 3000) {
            m_lostLogged = true;
            char det[64];
            std::snprintf(det, sizeof det, "state=%s spd=%.1f hdg=%.0f",
                          StateName((int)m_state), m_fc.Speed(), m_fc.Heading());
            m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "DATA",
                             "lost", det, q.x, q.y, q.z);
        }
    }

    if (m_metrics) {
        Vector p = m_fc.GetPosition();
        m_metrics->Traj(Simulator::Now().GetSeconds(), m_nodeId, "DATA", p.x, p.y, p.z);
        m_metrics->AddEnergy(params::EnergyPowerW(m_fc.Speed()) * params::kTrajLogS);
    }
    if (m_state != State::DONE)
        m_traj = Simulator::Schedule(Seconds(params::kTrajLogS), &SarDataUavApp::TrajTick, this);
}

bool SarDataUavApp::OnReceive(Ptr<NetDevice>, Ptr<const Packet> pkt, uint16_t, const Address&) {
    uint32_t sz = pkt->GetSize();
    if (sz < 2) return true;
    std::vector<uint8_t> b(sz); pkt->CopyData(b.data(), sz);
    uint8_t type = b[0];
    if (type == (uint8_t)Msg::CUE) {
        m_lastCueHeardS = Simulator::Now().GetSeconds();   // the sky is still busy
        return true;
    }
    if (type == (uint8_t)Msg::SUMMON && sz >= kSummonLen && m_claimed && !m_confirmed &&
        (m_state == State::DELIVER || m_state == State::DIVERT)) {
        // Delivery fallback: while delivering, this UAV is hovering directly
        // over the region, so the leader's ground SUMMON is a short A2G hop and
        // reaches it without a FAST relay (the relays have usually gone home by
        // now). A summon carrying DIFFERENT coordinates is the leader telling us
        // its first candidate was wrong — re-aim rather than keep transmitting
        // at a place the victim demonstrably cannot decode.
        uint16_t rid; std::memcpy(&rid, &b[2], 2);
        // Only OUR leader may re-aim us. Without this bind, any cell's summon
        // could drag a delivering UAV away mid-delivery.
        // D32: STRICT. The old test let a UAV whose binding was 0xFFFF accept a
        // re-aim from any leader, which is one of the paths by which the whole
        // team converged on a single decoy.
        if (rid != m_boundRegion) return true;
        int16_t cx, cy; std::memcpy(&cx, &b[4], 2); std::memcpy(&cy, &b[6], 2);
        double nx = cx / 10.0, ny = cy / 10.0;
        if (std::hypot(nx - m_divert.x, ny - m_divert.y) > 5.0) {
            m_divert = Vector(nx, ny, m_alt);
            m_fixX = nx; m_fixY = ny;                   // B3: report the CORRECTED fix
            if (!m_fixOnConfirm) m_hasFix = true;
            m_state = State::DIVERT;
            if (m_metrics) {
                Vector p = m_fc.GetPosition();
                m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "DATA",
                                 "retarget_divert", "leader re-aimed", p.x, p.y, p.z);
            }
        }
        return true;
    }
    if (type == (uint8_t)Msg::REJECT || type == (uint8_t)Msg::CONFIRM) {
        // D32: closure retires a job for EVERY UAV that heard it, so nobody
        // flies to a place that has already been settled.
        if (sz >= kConfirmLen) {
            uint16_t rid; std::memcpy(&rid, &b[2], 2);
            if (rid != 0xFFFF) { m_tasks[rid].closed = true; }
        }
        if (!m_claimed) ConsiderTasks();
    }
    if (type == (uint8_t)Msg::REJECT && !m_confirmed) {
        // The ground has told us this place is not the victim. Drop the fix so a
        // known-wrong position cannot beat a correct one home to the BS.
        // D38: only if it is OUR place. A REJECT from another region says
        // nothing about the aim this UAV is holding.
        uint16_t rrid = 0xFFFF;
        if (sz >= kRejectLen) std::memcpy(&rrid, &b[2], 2);
        if (m_fixOnConfirm && (m_boundRegion == 0xFFFF || rrid == m_boundRegion))
            m_hasFix = false;
        // NOT a reason to leave: a region can hold both a match and a bystander,
        // and the match wins. Leaving on the first REJECT abandons places where
        // the victim is still reachable. The dwell bound below is what ends a
        // fruitless delivery, on time rather than on the first dissenting voice.
        return true;
    }
    if (type == (uint8_t)Msg::RCLAIM && sz >= kRclaimLen) {
        // The election's stand-down FLOOD doubles as the job advert, and it is
        // the only announcement that physically reaches a sparse sky. SUMMON is
        // a ONE-HOP ground broadcast, so a candidate is only ever relayed if a
        // FAST UAV happens to be within ~50 m while its leader is beaconing --
        // and with fixed-wing lanes 250 m apart that is rare. Measured at 24x24
        // seed 1: three regions summoned, only two ever reached the DATA team,
        // and the third was never served by anyone. RCLAIM floods the whole
        // field, so wherever the sky is, some forwarding node is under it.
        //
        // This is the cooperative ground plane doing the job it exists for:
        // covering for a sky that cannot be everywhere.
        uint16_t rid; std::memcpy(&rid, &b[1], 2);
        int16_t cx, cy; std::memcpy(&cx, &b[5], 2); std::memcpy(&cy, &b[7], 2);
        Task& t = m_tasks[rid];
        if (!t.known) { t.x = cx / 10.0; t.y = cy / 10.0; t.known = true; }
        ConsiderTasks();
        return true;
    }
    if (type == (uint8_t)Msg::A2A && sz >= kA2ALen) {
        int16_t cx, cy; std::memcpy(&cx, &b[4], 2); std::memcpy(&cy, &b[6], 2);
        uint16_t rid; std::memcpy(&rid, &b[2], 2);
        // D32: an A2A is a JOB ADVERT, not an order. It used to latch straight
        // into m_pendX/m_pendY, so every free DATA UAV adopted whichever aim was
        // relayed most recently -- and since a leader re-announces on hearing a
        // cue, the busiest relay won. Measured at 40x40 with two victims and
        // four decoys: all FOUR DATA UAVs ended up delivering to the same decoy
        // at (281,280), in lockstep, re-aiming together on the same summons.
        // Record it as one job among several and choose deliberately.
        Task& t = m_tasks[rid];
        t.x = cx / 10.0; t.y = cy / 10.0; t.known = true;
        ConsiderTasks();
    } else if (type == (uint8_t)Msg::CLAIM && sz >= kClaimLen) {
        uint8_t role = b[3]; uint16_t id; std::memcpy(&id, &b[4], 2);
        uint16_t crid; std::memcpy(&crid, &b[1], 2);
        // Mutual exclusion is PER REGION. A peer claiming a different region has
        // taken a different job, and this UAV is still needed -- with several
        // candidate places, yielding globally is how a whole team ends up
        // serving one of them.
        // D32: a peer's claim is now a fact about the WORK, recorded first.
        if (role == 0 && id != (uint16_t)m_nodeId && crid != 0xFFFF) {
            // MUTUAL DEADLOCK, observed end to end: two UAVs claim the same
            // region within a millisecond; the higher id yields under the
            // tie-break, while the lower id overwrites its OWN ownership with
            // the peer's claim. Both then read the region as "taken by the
            // other" and nobody ever serves it -- diagnosed as known=3 closed=2
            // taken=1 on both UAVs at once, with the candidate never delivered.
            //
            // Record a peer's claim only when it actually wins: either the
            // region is not mine, or the peer's id is lower, which is exactly
            // the condition under which I stand down.
            const bool mine = (m_tasks.count(crid) &&
                               m_tasks[crid].takenBy == (uint16_t)m_nodeId);
            if (!mine || id < (uint16_t)m_nodeId) {
                m_tasks[crid].takenBy = id;
                m_tasks[crid].takenAt = Simulator::Now().GetSeconds();
            }
        }
        if (role == 4) {
            m_landed.insert(id);
            if (m_phaseGate && !m_gateOpen && GateOpen()) OpenGate();
        }
        if (role == 5) {                 // base: a candidate exists, launch
            m_launchOrder = true;
            if (m_phaseGate && !m_gateOpen && GateOpen()) OpenGate();
        }
        if (role == 3) {
            // A FAST UAV has finished its band. Until every sweep is done the
            // field can still produce a new candidate, so a DATA UAV that has
            // run out of work must WAIT, not land. Measured before this: DATA
            // landed at t=75-215 s while cues were still going out at t=306 s,
            // and 11 of 32 candidates were never served because nobody was
            // airborne when they were summoned.
            m_sweepDone.insert(id);
            if (m_phaseGate && !m_gateOpen && GateOpen()) OpenGate();
        }
        if (role == 2 && crid != 0xFFFF) {
            Task& t = m_tasks[crid];
            t.served++;
            t.closed = true;                // a peer has delivered there: done
            if (t.takenBy == id) t.takenBy = 0xFFFF;
            if (!m_claimed) ConsiderTasks();
        }
        // Two UAVs can claim the same place within the same millisecond -- the
        // backoff orders them by distance, but equidistant peers still collide
        // (measured: two DATA UAVs delivering 3 m apart at 24x24). Break the tie
        // deterministically by node id, and only while still en route: a UAV
        // that has begun delivering keeps its region.
        if (role == 0 && id != (uint16_t)m_nodeId && m_claimed && crid != 0xFFFF &&
            m_state == State::DIVERT && id < (uint16_t)m_nodeId) {
            auto mine = m_tasks.find(m_boundRegion);
            auto theirs = m_tasks.find(crid);
            if (mine != m_tasks.end() && theirs != m_tasks.end() &&
                std::hypot(mine->second.x - theirs->second.x,
                           mine->second.y - theirs->second.y) <= params::kRegionRadiusM) {
                if (m_metrics) {
                    Vector p = m_fc.GetPosition();
                    m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "DATA",
                                     "yield_stay", "lower id claimed the same place",
                                     p.x, p.y, p.z);
                }
                m_claimed = false; m_myTask = 0xFFFF; m_boundRegion = 0xFFFF;
                m_state = State::PATROL;
                ConsiderTasks();
                return true;
            }
        }
        const bool sameRegion = (crid != 0xFFFF && crid == m_myTask);
        if (role == 0 && id != (uint16_t)m_nodeId && !m_claimed && sameRegion) {
            m_yieldedDivert = true;                 // another DATA UAV took it
            Simulator::Cancel(m_claimEvent);
            // Yielding means this UAV has no task left. Waiting for a CONFIRM
            // instead was a hover-forever trap: CONFIRM is a one-hop ground
            // broadcast from the victim region, and at 300x300 m a UAV loitering
            // at its staging point usually cannot hear it — 3/20 runs at 16x16
            // never came home, which is where the 620 kJ p90 came from. The
            // peer's CLAIM is itself radio-delivered local information, so
            // acting on it needs no oracle.
            // ...but losing THIS region does not mean the mission is over for
            // this UAV: another region may still be summoning. Release the
            // binding and stay available instead of flying home. The
            // hover-forever trap the old code was avoiding is still avoided,
            // because the sky-quiet rule sends a UAV home once no cue has been
            // heard for kSkyQuietS -- that bound is what makes staying safe.
            m_boundRegion = 0xFFFF;
            m_myTask = 0xFFFF;
            m_yieldedDivert = false;   // eligible for the NEXT region's summon
            // D32: losing this job does not end the mission -- pick the next
            // nearest region nobody has taken, which is the whole point of
            // dividing the work rather than racing for it.
            ConsiderTasks();
            if (m_stayAvailable && (m_state == State::LOITER || m_state == State::PATROL ||
                                    m_state == State::GOTO_CENTER || m_state == State::CLIMB)) {
                if (m_metrics) {
                    Vector p = m_fc.GetPosition();
                    m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "DATA",
                                     "yield_stay", "peer took that region; staying available",
                                     p.x, p.y, p.z);
                }
            } else if (m_allHome && (m_state == State::LOITER || m_state == State::GOTO_CENTER ||
                              m_state == State::PATROL || m_state == State::CLIMB ||
                              m_state == State::IDLE)) {
                m_state = State::RETURN;
                if (m_metrics) {
                    Vector p = m_fc.GetPosition();
                    m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "DATA",
                                     "yield_return", "peer claimed the divert",
                                     p.x, p.y, p.z);
                }
            }
        }
        // A FAST courier claimed the report over the radio: the faster UAV owns
        // the trip home now — stop our slow (15 vs 25 m/s) fallback return and
        // hover in place, saving the transit energy.
        // audit F2: under the symmetric completion rule every UAV must come home,
        // so the courier hand-off no longer cancels our own return leg.
        if (role == 1 && m_confirmed && m_state == State::RETURN && !m_allHome) {
            m_fc.Hover();
            m_state = State::DONE;
            if (m_metrics) {
                Vector p = m_fc.GetPosition();
                m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "DATA",
                                 "return_yield", "courier took the report", p.x, p.y, p.z);
            }
        }
    } else if (type == (uint8_t)Msg::CONFIRM && sz >= kConfirmLen) {
        // audit F2: a DATA UAV that never won the divert is still loitering; the
        // mission is over for it too, so it flies home and reports like the rest.
        // D30: PATROL is deliberately NOT in this list any more. A UAV still
        // flying its band has coverage work left, and another candidate place
        // may still need serving; going home because someone else's region
        // closed is the single-candidate assumption again. LOITER/GOTO_CENTER
        // mean the plan is finished, so there the mission really is over for
        // this UAV. The sky-quiet rule still bounds how long a patrol can last.
        if (m_allHome && !m_claimed &&
            (m_state == State::LOITER || m_state == State::GOTO_CENTER)) {
            m_state = State::RETURN;
            return true;
        }
        // our delivery confirmed -> hand the report to the FAST team (25 m/s
        // courier beats our 15 m/s) and still fly home as the fallback; the BS
        // deduplicates, first REPORT wins.
        // D38: and it must be OUR region that confirmed. Two regions being
        // served at once means a CONFIRM in the air is as likely to be the peer's
        // as ours; taking it as ours stamps "confirmed" on an unexamined aim.
        uint16_t crid; std::memcpy(&crid, &b[2], 2);
        const bool oursConfirmed = (m_boundRegion == 0xFFFF || crid == m_boundRegion);
        // D38: a confirm for our region is a POSITION SAMPLE whether or not it is
        // the first one. Several nodes around the victim match, and each one is
        // an independent sample; folding them all in is free (they are already
        // on the air) and the accumulator averages them. Doing this only on the
        // first confirm -- as the state transition below does, correctly -- left
        // the report sitting on whichever node happened to be heard first.
        int16_t sx, sy; std::memcpy(&sx, &b[5], 2); std::memcpy(&sy, &b[7], 2);
        if (m_claimed && oursConfirmed) {
            AddFix(sx / 10.0, sy / 10.0);
            m_hasFix = true;
            m_fixX = m_fixes[0].first; m_fixY = m_fixes[0].second;
        }
        if (m_claimed && oursConfirmed && !m_confirmed &&
            (m_state == State::DELIVER || m_state == State::DIVERT)) {
            m_confirmed = true;
            // Keep delivering until the coverage dwell elapses so the whole
            // localized footprint (incl. a slightly-off victim) reconstructs the
            // data — then head home and hand the report to the FAST courier.
            SendHandoff();   // a FAST that has finished sweeping may take it
            double wait = std::max(0.0, m_deliverUntil - Simulator::Now().GetSeconds());
            // Holding a CONFIRMED victim fix changes this UAV's job: carrying it
            // home is now worth more than serving another candidate, because the
            // fix rides at 15 m/s and every extra job it takes first is added
            // straight onto the mission clock. Measured when it kept working:
            // time-to-fix went from 99 s to 352 s. The peer DATA UAV and the
            // cue sweep still cover the remaining candidates -- they stayed at
            // 100 % served.
            Simulator::Schedule(Seconds(wait),
                                m_fixFirst ? &SarDataUavApp::BeginReturn
                                           : &SarDataUavApp::ReleaseAndContinue, this);
        }
    }
    return true;
}

void SarDataUavApp::ReleaseAndContinue() {
    if (m_boundRegion != 0xFFFF) {
        // Tell the fleet. Without this a peer's table keeps the region marked
        // taken forever, so once every candidate had been claimed ONCE no UAV
        // could take another one and the whole "serve them all" behaviour never
        // fired -- measured as next_task = 0 in every run.
        SendClaim(2);                       // role 2 = released / dwell served
        Task& t = m_tasks[m_boundRegion];
        t.served++;
        t.takenBy = 0xFFFF;
        // A place that has had a full delivery dwell is DONE. Leaving it merely
        // "least served" let the fleet come back to it once every other
        // candidate had been visited: measured 60 delivery episodes for 25
        // distinct places, 58 % of the delivery effort spent re-serving ground
        // that had already had the whole dataset dropped on it.
        t.closed = true;
    }
    m_claimed = false;
    m_yieldedDivert = false;
    m_myTask = 0xFFFF;
    m_boundRegion = 0xFFFF;
    m_confirmed = false;
    m_dwellStarted = false;               // free to serve and confirm another place
    // Divertible again -- but only PATROL if there is a plan left to fly.
    m_state = (m_ti < m_targets.size()) ? State::PATROL : State::LOITER;
    ConsiderTasks();
    if (m_myTask == 0xFFFF) {
        // D32b: STAY AVAILABLE. Going home here was the reason candidates went
        // unserved: a UAV that finished or lost a job at t=66 s flew home, and
        // the two regions summoned at t=71 s and t=94 s had nobody left to serve
        // them -- with 400 s of horizon still unspent. "No job at this instant"
        // is not "no job". The sky-quiet rule is the bound that sends a UAV home,
        // and it is a bound on the SKY going silent, which is the right one.
        if (m_metrics) {
            // Say WHY there is nothing to do, or this line is unfalsifiable.
            int known=0, closed=0, taken=0, nearBlocked=0;
            for (const auto& [rid, t] : m_tasks) {
                if (!t.known) continue;
                known++;
                if (t.closed) { closed++; continue; }
                if (t.takenBy != 0xFFFF && t.takenBy != (uint16_t)m_nodeId &&
                    Simulator::Now().GetSeconds() - t.takenAt <= params::kClaimLeaseS) { taken++; continue; }
                if (PeerServingNear(t.x, t.y)) nearBlocked++;
            }
            char det[96];
            std::snprintf(det, sizeof det, "idle: known=%d closed=%d taken=%d nearBlocked=%d tbl=%d",
                          known, closed, taken, nearBlocked, (int)m_tasks.size());
            Vector p = m_fc.GetPosition();
            m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "DATA",
                             "yield_stay", det, p.x, p.y, p.z);
        }
        return;
    }
    if (m_metrics) {
        Vector p = m_fc.GetPosition();
        m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "DATA",
                         "next_task", "region settled; taking the next candidate",
                         p.x, p.y, p.z);
    }
}

void SarDataUavApp::BeginReturn() {
    if (m_state == State::RETURN || m_state == State::DONE) return;
    // Gate: the sweep must be over. The sky-quiet rule remains the upper bound,
    // so this cannot hang -- it only stops an early landing.
    if (m_sweepDone.empty() && m_lastCueHeardS > 0 &&
        Simulator::Now().GetSeconds() - m_lastCueHeardS <= params::kSkyQuietS) {
        m_state = (m_ti < m_targets.size()) ? State::PATROL : State::LOITER;
        return;
    }
    m_state = State::RETURN;
    SendHandoff();
}

}  // namespace ns3::uavsar
