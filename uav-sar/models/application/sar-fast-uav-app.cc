#include "sar-fast-uav-app.h"
#include "../common/sar-metrics.h"
#include "../common/sar-types.h"
#include "../common/sar-params.h"

#include "ns3/core-module.h"
#include "ns3/packet.h"
#include "ns3/mac16-address.h"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstring>

using namespace ns3;

namespace ns3::uavsar {

NS_OBJECT_ENSURE_REGISTERED(SarFastUavApp);

TypeId SarFastUavApp::GetTypeId() {
    static TypeId tid = TypeId("ns3::uavsar::SarFastUavApp")
                            .SetParent<Application>().SetGroupName("uav-sar")
                            .AddConstructor<SarFastUavApp>();
    return tid;
}
SarFastUavApp::SarFastUavApp() : m_rng(CreateObject<UniformRandomVariable>()) {}
SarFastUavApp::~SarFastUavApp() = default;

void SarFastUavApp::SendClaim(uint8_t role) {
    if (!m_dev) return;
    std::vector<uint8_t> b(kClaimLen);
    uint8_t* q = b.data();
    *q++ = (uint8_t)Msg::CLAIM;
    uint16_t rid = 1; std::memcpy(q, &rid, 2); q += 2;
    *q++ = role;
    uint16_t id = (uint16_t)m_nodeId; std::memcpy(q, &id, 2);
    m_dev->Send(Create<Packet>(b.data(), b.size()), Mac16Address("ff:ff"), 0);
    if (m_metrics) { m_metrics->AddSent(); m_metrics->AddSentBytes(b.size()); }
}

void SarFastUavApp::ClaimCourier() {
    if (m_yieldedCourier || m_courier) return;   // another FAST is the courier
    SendClaim(1);
    m_courier = true;
    m_state = State::RETURN_BS;
    if (m_metrics) {
        Vector p = m_fc.GetPosition();
        m_metrics->AddCustody();
        m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "FAST",
                         "report_pickup", "courier claimed", p.x, p.y, p.z);
    }
}

void SarFastUavApp::StartApplication() {
    m_fc.AttachTo(GetNode());
    // Plan the sweep with the (conservative) design coverage radius, not the
    // optimistic LoS link-budget range — otherwise coverage degenerates to a
    // single waypoint and the sweep becomes meaningless.
    m_radius = params::kUavBroadcastRadiusM;
    Simulator::Schedule(Seconds(1.0 + 0.3 * m_nodeId), &SarFastUavApp::TakeOff, this);
}
void SarFastUavApp::StopApplication() {
    Simulator::Cancel(m_ctrl); Simulator::Cancel(m_dis); Simulator::Cancel(m_traj);
    m_fc.Hover(); m_fc.SetClimb(0);
}

void SarFastUavApp::BuildMission() {
    // FIXED-WING coverage. The greedy maximum-coverage planner this used to call
    // picks whichever uncovered waypoint scores best next, which produces a path
    // that doubles back on itself constantly. A multirotor can fly that; a
    // fixed-wing cannot. At 25 m/s and a 30 deg bank the turn radius is ~110 m,
    // while consecutive greedy picks are typically one grid step apart -- so the
    // planned path demanded turns roughly an order of magnitude tighter than the
    // airframe can hold, and the flown trajectory was never the planned one.
    //
    // Replaced with a boustrophedon sweep whose lanes are visited in an
    // INTERLEAVED order: lane 0, lane k, lane 2k, ... then lane 1, lane 1+k, ...
    // with the stride k chosen so every turn-around spans at least one turn
    // diameter. The only turns left are the 180 deg reversals at the ends of
    // lanes, and each of those now has room to be flown at the design bank.
    m_targets.clear(); m_ti = 0;
    const size_t N = m_sensors.size();
    if (N == 0 || m_radius <= 0) return;

    double x0 = m_sensors[0].x, x1 = x0, y0 = m_sensors[0].y, y1 = y0;
    for (const auto& sp : m_sensors) {
        x0 = std::min(x0, sp.x); x1 = std::max(x1, sp.x);
        y0 = std::min(y0, sp.y); y1 = std::max(y1, sp.y);
    }
    const bool lanesAlongX = (x1 - x0) >= (y1 - y0);
    const double across0 = lanesAlongX ? y0 : x0;
    const double across1 = lanesAlongX ? y1 : x1;
    const double along0  = lanesAlongX ? x0 : y0;
    const double along1  = lanesAlongX ? x1 : y1;

    // Lane spacing = the cue radius, NOT the full swath. Widening it to 1.6x
    // looked free on paper -- the swath is two radii wide -- and cost 11 points
    // of coverage in measurement: FAST fell from 100 % of nodes to 89.3 %,
    // because the reception radius under fading and the link budget is smaller
    // than the nominal 50 m, so 80 m lanes leave gaps between them. Reverted.
    // The turn-excursion cut below is the part that was actually free.
    const double spacing = std::max(1.0, m_radius);
    const int lanes = std::max(1, (int)std::ceil((across1 - across0) / spacing) + 1);
    const double R = params::TurnRadiusM(m_speed);

    // TURN OUTSIDE THE FIELD. The previous version tried to make each 180 deg
    // reversal fit inside the band by visiting lanes in an interleaved order,
    // with a stride sized to one turn diameter. That cannot work here and the
    // arithmetic says so: the band is 230 m wide and the turn diameter is 220 m,
    // so the interleave spaced only the FIRST two turn-arounds (250 m, 200 m)
    // and left the last three at 50 m -- a quarter of what the airframe needs.
    // The aircraft overshot, looped, and missed lanes: FAST covered 73.4 % of
    // the nodes on average and 49.7 % in the worst seed, which is also what the
    // folded-looking track was.
    //
    // A survey aircraft does not turn inside the survey area. Lanes are now flown
    // in order, and each turn-around is two explicit waypoints placed 2R BEYOND
    // the end of the lane, so the reversal happens off the field and costs
    // distance instead of coverage.
    // Excursion beyond the lane end. 2R was a safe over-estimate; a reversal
    // with a small lateral offset needs about 1.2R of run-out to be flown at the
    // design bank, and the rest was pure waste outside the search area.
    const double turnOut = 1.2 * R;
    auto wp = [&](double along, double across) {
        return lanesAlongX ? Vector(along, across, m_alt) : Vector(across, along, m_alt);
    };

    bool forward = true;
    for (int l = 0; l < lanes; ++l) {
        const double a = std::min(across0 + l * spacing, across1);
        const double s0 = forward ? along0 : along1;
        const double s1 = forward ? along1 : along0;
        m_targets.push_back(wp(s0, a));
        m_targets.push_back(wp(s1, a));
        if (l + 1 < lanes) {
            const double aNext = std::min(across0 + (l + 1) * spacing, across1);
            const double dir = forward ? 1.0 : -1.0;
            const double out = s1 + dir * turnOut;
            m_targets.push_back(wp(out, a));       // run out past the end
            m_targets.push_back(wp(out, aNext));   // cross over, outside the field
        }
        forward = !forward;
    }
}

void SarFastUavApp::TakeOff() {
    BuildMission();
    if (m_targets.empty()) return;
    if (m_metrics) { Vector p = m_fc.GetPosition();
        m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "FAST", "takeoff", "", p.x, p.y, p.z); }
    // Fixed-wing: heading rate g tan(phi) / v, i.e. one turn diameter per 180 deg.
    m_fc.SetMaxTurnRateDegPerS(params::kGravityMps2 *
                               std::tan(params::kBankAngleDeg * M_PI / 180.0) /
                               std::max(1.0, m_speed) * 180.0 / M_PI);
    m_state = State::CLIMB; m_fc.Hover(); m_fc.SetClimb(params::kClimbRateMps);
    m_ctrl = Simulator::Schedule(Seconds(params::kControlTickS), &SarFastUavApp::ControlTick, this);
    m_dis = Simulator::Schedule(Seconds(params::kDisseminateStaggerS), &SarFastUavApp::DisseminateTick, this);
    TrajTick();
}

void SarFastUavApp::ControlTick() {
    m_fc.Step(params::kControlTickS);   // fly the rate-limited turn
    Vector p = m_fc.GetPosition();
    double arriveR = std::max(1.0, m_speed * params::kControlTickS * 1.5);
    if (m_state == State::CLIMB) {
        if (p.z >= m_alt) { m_fc.SetClimb(0); m_state = State::CRUISE;
            Vector t = m_targets[m_ti];
            m_fc.Turn(std::atan2(t.y - p.y, t.x - p.x) * 180 / M_PI); m_fc.Forward(m_speed); }
    } else if (m_state == State::RETURN_BS) {
        double d = std::hypot(m_bsPos.x - p.x, m_bsPos.y - p.y);
        m_fc.Turn(std::atan2(m_bsPos.y - p.y, m_bsPos.x - p.x) * 180 / M_PI);
        m_fc.Forward(m_speed);
        if (d <= arriveR) {
            m_fc.Hover(); m_state = State::DONE;
            if (m_metrics) m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId,
                                            "FAST", "report_tx", "courier at BS",
                                            p.x, p.y, p.z);
            SendReport();
            return;
        }
    } else if (m_state == State::CRUISE) {
        Vector t = m_targets[m_ti];
        const double dNow = std::hypot(t.x - p.x, t.y - p.y);
        // CONTINUOUS guidance. The heading used to be commanded only on reaching
        // a waypoint, which was fine when Turn() snapped instantly: the aim was
        // exact and the leg was a straight line. Under a turn-rate limit the
        // initial arc puts the aircraft off course and it then flies straight
        // for ever, never re-aiming -- measured as a total of 70 deg of heading
        // change per run, identical across seeds, and zero deliveries.
        m_fc.Turn(std::atan2(t.y - p.y, t.x - p.x) * 180 / M_PI);
        m_fc.Forward(m_speed);
        // Accept the waypoint on approach OR once we are abeam of it: a
        // rate-limited aircraft with a 110 m turn radius cannot always close to
        // within the acceptance radius, and would orbit for ever trying.
        const double R = params::TurnRadiusM(m_speed);
        const bool passedAbeam = (m_prevDist > 0 && dNow > m_prevDist && dNow < 2.0 * R);
        m_prevDist = dNow;
        if (dNow <= arriveR || passedAbeam) {
            m_prevDist = 0;
            m_ti++;
            if (m_ti >= m_targets.size()) {
                // audit A10: a FAST UAV is the ONLY thing that can relay a
                // SUMMON to the loitering DATA team. Flying home the instant the
                // sweep ends means that on a small grid — where the sweep
                // finishes long before the ground has finished reporting — the
                // region forms with nobody airborne to hear it, and the mission
                // silently delivers nothing. Measured: at 8x8 this capped
                // mission completion at 63%, and made any observation window
                // >= 45 s fail outright.
                //
                // So: hold station as a relay for a BOUNDED grace period, then
                // go home. The bound is what keeps this from regressing to the
                // old hover-forever trap (which burned 620 kJ at 16x16); the
                // grace is what keeps a relay alive across the decision. Both
                // ends are local — no UAV consults the ground truth or a global
                // view to decide.
                SendClaim(3);      // sweep complete: the DATA team may stand down
                if (!m_allHome) { m_fc.Hover(); }
                else if (AllRelayedClosed()) { m_state = State::RETURN_BS; }
                else {
                    m_fc.Hover();
                    m_state = State::RELAY_HOLD;
                    m_relayUntilS = Simulator::Now().GetSeconds() + params::kRelayGraceS;
                }
            }
            // next leg: guidance above re-aims on the following tick.
        }
    } else if (m_state == State::RELAY_HOLD) {
        // Hold as an airborne relay until either the region forms (we relayed a
        // SUMMON, so the DATA team has its task) or the grace period runs out.
        if (AllRelayedClosed() || Simulator::Now().GetSeconds() >= m_relayUntilS)
            m_state = State::RETURN_BS;
    } else return;
    m_ctrl = Simulator::Schedule(Seconds(params::kControlTickS), &SarFastUavApp::ControlTick, this);
}

bool SarFastUavApp::AllRelayedClosed() const {
    // Nothing dispatched yet -> nothing to wait for (the RELAY_HOLD grace period
    // is what covers the "region has not formed yet" case, and it is bounded).
    if (m_relayedRegions.empty()) return false;
    for (uint16_t r : m_relayedRegions)
        if (!m_closedRegions.count(r)) return false;
    return true;
}

void SarFastUavApp::RelayBestEcho() {
    // Dispatch the DATA team to the best DIRECT echo. Byte-for-byte the same
    // A2A the cooperative arm sends, so the two arms differ in HOW the aim point
    // was formed and in nothing else downstream.
    if (m_summonSeen || m_bestEchoEv <= 0 || !m_dev) return;
    m_summonSeen = true;
    // Same rule as the cooperative arm's relay path, so the two arms still differ
    // only in HOW the aim was formed.
    m_pendFixX = m_bestEchoX; m_pendFixY = m_bestEchoY; m_hasPend = true;
    if (!m_fixOnConfirm) { m_hasFix = true; m_fixX = m_pendFixX; m_fixY = m_pendFixY; }
    std::vector<uint8_t> r(kA2ALen, 0);
    uint8_t* q = r.data();
    *q++ = (uint8_t)Msg::A2A; *q++ = kBroadcast;
    uint16_t rid = 1; std::memcpy(q, &rid, 2); q += 2;
    int16_t cx = (int16_t)(m_bestEchoX * 10), cy = (int16_t)(m_bestEchoY * 10);
    std::memcpy(q, &cx, 2); q += 2; std::memcpy(q, &cy, 2);
    m_dev->Send(Create<Packet>(r.data(), r.size()), Mac16Address("ff:ff"), 0);
    if (m_metrics) {
        m_metrics->AddSent(); m_metrics->AddSentBytes(r.size()); m_metrics->AddCustody();
        Vector p = m_fc.GetPosition();
        char det[64];
        std::snprintf(det, sizeof det, "echo ev=%.2f -> %.1f;%.1f",
                      m_bestEchoEv, m_bestEchoX, m_bestEchoY);
        m_metrics->MarkLocalize(Simulator::Now().GetSeconds());
        m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "FAST",
                         "echo_relay", det, p.x, p.y, p.z);
    }
}

void SarFastUavApp::DisseminateTick() {
    // Byte-honest cue dissemination: cue fragments are chunked exactly like
    // full-data fragments (same header), cycling (frag, seq).
    //
    // D30: this used to stop at the FIRST summon anywhere in the field, on the
    // reasoning that "the region is found, cues are moot". That reasoning holds
    // only if there is exactly one place worth finding. With confusable objects
    // the first summon is frequently a decoy, and switching cueing off meant the
    // unswept remainder of the field -- where the victim may well be -- never
    // received a cue, so a second candidate could not physically form. Cueing
    // now runs for as long as this UAV is flying its band.
    if (m_state == State::CRUISE && !m_cues.empty() && m_dev) {
        const Fragment& f = m_cues[m_cueIdx % m_cues.size()];
        uint16_t total = (uint16_t)std::max(1u, (f.sizeBytes + kChunkBytes - 1) / kChunkBytes);
        uint32_t payloadLen = std::min(kChunkBytes, f.sizeBytes - m_cueSeq * kChunkBytes);
        std::vector<uint8_t> b(kChunkHdr + payloadLen, 0);
        uint8_t* p = b.data();
        *p++ = (uint8_t)Msg::CUE; *p++ = kBroadcast;
        uint16_t id = (uint16_t)f.id; std::memcpy(p, &id, 2); p += 2;
        std::memcpy(p, &m_cueSeq, 2); p += 2;
        std::memcpy(p, &total, 2); p += 2;
        *p++ = (uint8_t)f.layer;
        m_dev->Send(Create<Packet>(b.data(), b.size()), Mac16Address("ff:ff"), 0);
        if (m_metrics) {
            m_metrics->AddSent(); m_metrics->AddSentBytes(b.size());
            // viz: decimated A2G cue broadcast marker (1 in 25 sends)
            if (++m_cueTxCount % 25 == 1) {
                Vector p = m_fc.GetPosition();
                m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "FAST",
                                 "cue_tx", "", p.x, p.y, p.z);
            }
        }
        m_cueSeq++;
        if (m_cueSeq >= total) { m_cueSeq = 0; m_cueIdx = (m_cueIdx + 1) % m_cues.size(); }
    }
    m_dis = Simulator::Schedule(Seconds(params::kDisseminateStaggerS), &SarFastUavApp::DisseminateTick, this);
}

void SarFastUavApp::TrajTick() {
    if (m_metrics) {
        Vector p = m_fc.GetPosition();
        m_metrics->Traj(Simulator::Now().GetSeconds(), m_nodeId, "FAST", p.x, p.y, p.z);
        // Propulsion energy over the last second (Zeng-Xu-Zhang rotary model).
        m_metrics->AddEnergy(params::EnergyPowerW(m_fc.Speed()) * params::kTrajLogS);
    }
    m_traj = Simulator::Schedule(Seconds(params::kTrajLogS), &SarFastUavApp::TrajTick, this);
}

void SarFastUavApp::SendReport() {
    if (m_reportsSent >= params::kReportRetries) return;
    if (m_dev) {
        std::vector<uint8_t> b(kReportLen, 0);
        uint8_t* q = b.data();
        *q++ = (uint8_t)Msg::REPORT; *q++ = m_hasFix ? kFlagHasFix : 0x00;
        uint16_t rid = 1; std::memcpy(q, &rid, 2); q += 2; *q++ = 255;
        int16_t fx = (int16_t)std::lround(m_fixX * 10.0);
        int16_t fy = (int16_t)std::lround(m_fixY * 10.0);
        std::memcpy(q, &fx, 2); q += 2; std::memcpy(q, &fy, 2);
        m_dev->Send(Create<Packet>(b.data(), b.size()), m_bsAddr, 0);
        if (m_metrics) { m_metrics->AddSent(); m_metrics->AddSentBytes(b.size()); }
    }
    m_reportsSent++;
    Simulator::Schedule(Seconds(params::kReportRetryS), &SarFastUavApp::SendReport, this);
}

bool SarFastUavApp::OnReceive(Ptr<NetDevice>, Ptr<const Packet> pkt, uint16_t, const Address&) {
    uint32_t sz = pkt->GetSize();
    if (sz < 2) return true;
    std::vector<uint8_t> b(sz); pkt->CopyData(b.data(), sz);
    if (b[0] == (uint8_t)Msg::HANDOFF && sz >= kHandoffLen) {
        // audit B3: take custody of the fix as well as of the errand.
        if (b[1] & kFlagHasFix) {
            int16_t fx, fy; std::memcpy(&fx, &b[4], 2); std::memcpy(&fy, &b[6], 2);
            m_hasFix = true; m_fixX = fx / 10.0; m_fixY = fy / 10.0;
        }
        // Radio courier election: schedule a CLAIM after a short backoff; the
        // first FAST to claim on the radio wins, the rest yield.
        //
        // ...but ONLY a UAV that has finished sweeping may volunteer. Couriering
        // ends the sweep, and with two FAST UAVs that costs half the cue
        // coverage: measured at 24x24, the courier flew 2.1 km and landed at
        // t=90 s while its peer flew 5.7 km to t=264 s, and FAST reached only
        // 73 % of the nodes. The DATA UAV already flies home as the fallback
        // carrier, so an unfinished sweep is worth more than a faster courier.
        const bool sweepDone = (m_state == State::RELAY_HOLD ||
                                m_state == State::RETURN_BS ||
                                m_ti >= m_targets.size());
        if (sweepDone && !m_courier && !m_yieldedCourier && !m_courierEvent.IsPending())
            m_courierEvent = Simulator::Schedule(
                Seconds(m_rng->GetValue(0.0, params::kClaimBackoffS)),
                &SarFastUavApp::ClaimCourier, this);
        return true;
    }
    if (b[0] == (uint8_t)Msg::REJECT) {
        if (sz >= kRejectLen) { uint16_t rid; std::memcpy(&rid, &b[2], 2);
                                m_closedRegions.insert(rid); }
        if (m_fixOnConfirm && !m_hasFix) m_hasPend = false;  // ground contradicted the aim
        return true;
    }
    if (b[0] == (uint8_t)Msg::CONFIRM) {
        if (sz >= kConfirmLen) { uint16_t rid; std::memcpy(&rid, &b[2], 2);
                                 m_closedRegions.insert(rid); }
        // A node under the drop held the whole reference and still matched it.
        // Only now is the relayed aim worth carrying home.
        if (m_fixOnConfirm && m_hasPend && !m_hasFix) {
            m_hasFix = true; m_fixX = m_pendFixX; m_fixY = m_pendFixY;
        }
    }
    // D30: a CONFIRM used to abort the sweep outright and send this UAV home,
    // whichever region it was about. That is the single-candidate assumption in
    // its purest form: one place closing ended the search everywhere. A FAST UAV
    // now finishes its band; the end-of-sweep branch decides whether anything is
    // still open before it leaves.
    if (b[0] == (uint8_t)Msg::CLAIM && sz >= kClaimLen) {
        uint8_t role = b[3]; uint16_t id; std::memcpy(&id, &b[4], 2);
        if (role == 1 && id != (uint16_t)m_nodeId && !m_courier) {
            m_yieldedCourier = true;               // another FAST is the courier
            Simulator::Cancel(m_courierEvent);
        }
        return true;
    }
    if (b[0] == (uint8_t)Msg::A2A && sz >= kA2ALen) {
        // A peer already dispatched the DATA team, so the region is found and
        // cues are moot. In the cooperative arm the ground SUMMON reaches every
        // FAST at once; the closed-loop arm has no such shared plane, so the
        // fleet message is what stops the others cueing.
        m_summonSeen = true;
        { uint16_t rid; std::memcpy(&rid, &b[2], 2); m_relayedRegions.insert(rid); }
        Simulator::Cancel(m_echoSettle);
        return true;
    }
    if (b[0] == (uint8_t)Msg::ECHO && sz >= kEchoLen && m_echoRelay && !m_summonSeen) {
        // audit W4: closed-loop NON-cooperative arm. There is no ground leader
        // and no region, so this UAV aims at the strongest thing it personally
        // overheard. Track the running argmax; the relay is scheduled once the
        // evidence stops improving (same "aim when it settles" rule the
        // cooperative arm uses, so the two differ ONLY in whether the ground
        // aggregates for them).
        uint8_t evQ8 = b[3];
        int16_t x, y; std::memcpy(&x, &b[4], 2); std::memcpy(&y, &b[6], 2);
        double ev = evQ8 / 255.0;
        if (ev > m_bestEchoEv) {
            m_bestEchoEv = ev; m_bestEchoX = x / 10.0; m_bestEchoY = y / 10.0;
            Simulator::Cancel(m_echoSettle);
            m_echoSettle = Simulator::Schedule(Seconds(params::kEvidenceStableS),
                                               &SarFastUavApp::RelayBestEcho, this);
        }
        return true;
    }
    if (b[0] == (uint8_t)Msg::RCLAIM && sz >= kRclaimLen && m_dev) {
        // Same reasoning as in the DATA app: relay the flood as a job advert so
        // a DATA UAV out of ground range still learns the candidate exists.
        uint16_t rid; std::memcpy(&rid, &b[1], 2);
        int16_t cx, cy; std::memcpy(&cx, &b[5], 2); std::memcpy(&cy, &b[7], 2);
        if (!m_relayedRegions.count(rid)) {
            m_relayedRegions.insert(rid);
            std::vector<uint8_t> r(kA2ALen, 0);
            uint8_t* q = r.data();
            *q++ = (uint8_t)Msg::A2A; *q++ = kBroadcast;
            std::memcpy(q, &rid, 2); q += 2;
            std::memcpy(q, &cx, 2); q += 2; std::memcpy(q, &cy, 2);
            m_dev->Send(Create<Packet>(r.data(), r.size()), Mac16Address("ff:ff"), 0);
            if (m_metrics) {
                m_metrics->AddSent(); m_metrics->AddSentBytes(r.size());
                Vector p = m_fc.GetPosition();
                char det[48];
                std::snprintf(det, sizeof det, "rclaim aim=%.0f;%.0f", cx / 10.0, cy / 10.0);
                m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "FAST",
                                 "a2a_relay", det, p.x, p.y, p.z);
            }
        }
        return true;
    }
    if (b[0] == (uint8_t)Msg::SUMMON && sz >= kSummonLen && m_dev) {
        // relay to DATA team over A2A (same body, different type).
        m_summonSeen = true;   // region found -> stop spreading cues
        // audit B3: a relaying FAST heard the coordinates itself, so it can also
        // carry them home — the fix is not the courier's private property.
        {
            int16_t cx, cy; std::memcpy(&cx, &b[4], 2); std::memcpy(&cy, &b[6], 2);
            // Relaying a summon is not evidence that the summon was RIGHT. With
            // several regions summoning, a relay hears several aims and would
            // carry the last one home whether or not anyone confirmed it -- and
            // that report can beat a correct one to the BS. Hold it pending; a
            // CONFIRM promotes it, a REJECT drops it.
            m_pendFixX = cx / 10.0; m_pendFixY = cy / 10.0; m_hasPend = true;
            if (!m_fixOnConfirm) { m_hasFix = true; m_fixX = m_pendFixX; m_fixY = m_pendFixY; }
        }
        { uint16_t rid; std::memcpy(&rid, &b[2], 2); m_relayedRegions.insert(rid); }
        double b_aimX = 0, b_aimY = 0;
        { int16_t ax, ay; std::memcpy(&ax, &b[4], 2); std::memcpy(&ay, &b[6], 2);
          b_aimX = ax / 10.0; b_aimY = ay / 10.0; }
        std::vector<uint8_t> r(b.begin(), b.begin() + kSummonLen);
        r[0] = (uint8_t)Msg::A2A;
        m_dev->Send(Create<Packet>(r.data(), r.size()), Mac16Address("ff:ff"), 0);
        if (m_metrics) {
            m_metrics->AddSent();
            m_metrics->AddSentBytes(r.size());
            m_metrics->AddCustody();
            // viz: A2A relay marker at the relaying FAST UAV
            Vector p = m_fc.GetPosition();
            char det[48];
            std::snprintf(det, sizeof det, "aim=%.0f;%.0f", b_aimX, b_aimY);
            m_metrics->Event(Simulator::Now().GetSeconds(), m_nodeId, "FAST",
                             "a2a_relay", det, p.x, p.y, p.z);
        }
    }
    return true;
}

}  // namespace ns3::uavsar
