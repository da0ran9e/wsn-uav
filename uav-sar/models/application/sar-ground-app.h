#ifndef UAV_SAR_GROUND_APP_H
#define UAV_SAR_GROUND_APP_H

// Ground sensor node — fully distributed control plane (no central coordinator).
//   - Fragments arrive as byte-honest chunks over CUE (FAST) or FULL (DATA);
//     both fill the SAME per-fragment chunk set (a fragment counts once).
//   - Node evidence = Confidence(possessed) * clueQuality. When it crosses the
//     coop threshold the node sends an RPT (carrying its OWN GPS) up the cell
//     tree to its Cell Leader over the real radio.
//   - The Cell Leader aggregates its cell (union), floods a SHARE across the
//     boundary when it corroborates, and — when its cell crosses ALERT — runs a
//     DISTRIBUTED election: it schedules a SUMMON after an evidence-weighted
//     backoff and suppresses it if it hears another leader's SUMMON first. The
//     winner beacons the SUMMON carrying the strongest node's (radio-reported)
//     position as the delivery target.
//   - Any node that reconstructs the ENTIRE dataset broadcasts CONFIRM.

#include "../common/target-profile.h"
#include "../common/sar-params.h"

#include "ns3/application.h"
#include "ns3/net-device.h"
#include "ns3/event-id.h"
#include "ns3/ptr.h"
#include "ns3/address.h"
#include "ns3/random-variable-stream.h"

#include <cstdint>
#include <map>
#include <set>
#include <vector>

namespace ns3::uavsar {

class SarMetrics;

class SarGroundApp : public ns3::Application {
public:
    static ns3::TypeId GetTypeId();
    SarGroundApp();
    ~SarGroundApp() override;

    void SetNodeId(uint32_t id) { m_nodeId = id; }
    void SetDevice(ns3::Ptr<ns3::NetDevice> d) { m_dev = d; }
    void SetMetrics(SarMetrics* m) { m_metrics = m; }
    void SetCooperative(bool v) { m_cooperative = v; }  // proposed = true
    // audit W4: closed-loop NON-cooperative mode. The node answers whatever UAV
    // is overhead with a DIRECT single-hop ECHO and does nothing else -- no
    // report up a cell tree, no cross-cell SHARE, no election. It is the
    // ablation that isolates COOPERATION from feedback: this arm has closed-loop
    // feedback and homing, and none of the WSN substrate.
    void SetEchoMode(bool v) { m_echoMode = v; }
    // audit F4: Zeng'18 multicasts RATELESS/network-coded symbols — a terminal
    // recovers after ~1.05x file-worth of ANY symbols. Replaying identical chunk
    // indices (uncoded repetition) instead forces a GT to see all 382 distinct
    // indices, demanding per-packet success q>=0.878 where the coded scheme needs
    // q>=0.35 — which is what inflated the baseline's required redundancy to 3x.
    void SetCodedRecovery(bool v) { m_codedRecovery = v; }
    // audit W1: aiming rule ablation. "argmax" = deliver to the single
    // highest-evidence reporting node; "centroid" = evidence^2-weighted mean.
    void SetAimArgmax(bool v) { m_aimArgmax = v; }
    // audit B2 ablation: with suppression off, no leader ever hears another's
    // stand-down (the pre-fix behaviour), so every alerting cell summons its own
    // UAV. Turning it off is how the election's value is measured rather than
    // asserted.
    void SetElectSuppress(bool v) { m_electSuppress = v; }
    // Radius within which another cell's claim counts as the SAME region.
    // 0 restores the unscoped, field-wide stand-down (the ablation).
    void SetElectScope(double m) { m_electScope = m; }
    // How far from its own cell centre a leader may aim. 0 = unbounded.
    void SetAimScope(double m) { m_aimScope = m; }
    // audit M9/W3: this node's frozen GPS offset, in metres. Set by the
    // orchestrator from a per-run RNG so it is reproducible from the seed.
    void SetGpsBias(double dx, double dy) { m_gpsBiasX = dx; m_gpsBiasY = dy; }
    void SetMinObserve(double s) { m_minObserveS = s; } // floor on the first summon
    // audit A10: adaptive observation window (default). Off = the old fixed
    // wall-clock --minObserve, kept as the ablation arm.
    void SetAdaptiveWindow(bool v) { m_adaptiveWindow = v; }
    void SetProfile(const std::vector<Fragment>& frags);
    void SetClueQuality(double q) { m_clueQuality = q; }
    // What the same detector reads once this node holds the COMPLETE reference.
    // Equal to the cue-only reading when nothing confusable is nearby; much
    // lower next to a confusable object, because the extra reference data is
    // what separates them.
    void SetClueQualityFull(double q) { m_clueQualityFull = q; }
    void SetConfirmThreshold(double t) { m_confirmThr = t; }
    void SetCoopThreshold(double coop) { m_coop = coop; }
    void SetIsTarget(bool t) { m_isTarget = t; }
    // Intra-cell tree: next hop up toward the Cell Leader (-1 if I am the CL),
    // whether I am the CL, my cell id and centre.
    void SetTreeParent(int32_t p) { m_treeParent = p; }
    void SetCellLeader(bool v) { m_isCellLeader = v; }
    void SetCellId(int32_t c) { m_cellId = c; }
    void SetCellCenter(double x, double y) { m_cellCx = x; m_cellCy = y; }

    bool OnReceive(ns3::Ptr<ns3::NetDevice> dev, ns3::Ptr<const ns3::Packet> pkt,
                   uint16_t proto, const ns3::Address& from);

private:
    struct NodeEv { double ev = 0, x = 0, y = 0; };
    // Ranked delivery candidates, strongest first: own members + neighbour peaks.
    // Holding the ranking is what makes a wrong first guess recoverable.
    struct Cand { double ev, x, y; };

    void StartApplication() override;
    void StopApplication() override;
    void StartSummon(double cx, double cy);   // I won the election -> beacon
    void BeaconTick();
    void SendConfirm();                        // retried kConfirmRetries times
    void DeliverEvidence(double ev);           // my own evidence -> CL (local or RPT)
    void SendRpt(uint16_t orig, uint8_t evQ8, int16_t x, int16_t y, int32_t nextHop, uint8_t ttl);
    void SendEcho();                           // audit W4: direct reply to the sky
    void LeaderIngest(uint16_t orig, double ev, double x, double y);  // CL aggregation
    void FloodShare();
    void SendShare(int32_t cell, uint8_t evQ8, uint8_t peakQ8,
                   int16_t cx, int16_t cy, uint8_t ttl);
    // audit B2: multi-hop election suppression on the SHARE plane.
    void SendRclaim(int32_t cell, uint8_t evQ8, uint8_t peakQ8,
                    int16_t cx, int16_t cy, uint8_t ttl);
    void MaybeElect();                         // schedule a summon if I lead
    void MaybeRetarget();                      // no CONFIRM -> aim at the next candidate
    void Elect();                              // fire the summon (winner)
    double PossessedConfidence() const;
    // D31: the FRACTION of the reference dataset this node actually holds, by
    // bytes. Distinct from PossessedConfidence(), which is the union recognition
    // probability 1-prod(1-p_i) and is already 0.926 on the cue fragments alone
    // -- 7% of the bytes. Using that as the two-tier mixing weight made a node
    // holding only cues behave as if it were 92.6% informed, which silently
    // disabled the entire false-positive premise. Confidence stays where it
    // belongs (the reporting threshold); the mixing weight is this.
    double PossessedFraction() const;
    bool HasEntireDataset() const;
    double CellAggregate() const;

    uint32_t m_nodeId = 0;
    ns3::Ptr<ns3::NetDevice> m_dev;
    SarMetrics* m_metrics = nullptr;
    bool m_cooperative = false;
    bool m_codedRecovery = false;
    bool m_aimArgmax = true;
    bool m_electSuppress = true;
    double m_electScope = params::kRegionRadiusM;
    double m_aimScope = params::kAimScopeM;
    bool m_echoMode = false;      // audit W4
    uint32_t m_echoesSent = 0;
    ns3::EventId m_echoEvent;
    double m_gpsBiasX = 0, m_gpsBiasY = 0;
    uint32_t m_chunksRx = 0;      // total chunks received (duplicates count: coded)
    double m_minObserveS = 20.0;

    std::map<uint16_t, Fragment> m_byId;                 // full profile (briefing)
    std::map<uint16_t, std::set<uint16_t>> m_chunks;     // fragId -> received seqs
    std::map<uint16_t, uint16_t> m_totals;               // fragId -> total chunks
    std::set<uint16_t> m_have;                           // complete fragment ids
    double m_clueQuality = 0.0;
    double m_clueQualityFull = -1.0;   // < 0 = unset, falls back to m_clueQuality
    // Interpolated by how much of the dataset this node actually holds: judging
    // on cue fragments alone is what makes a false positive possible in the
    // first place, so the reading has to improve as the dataset arrives.
    bool InAimScope(double x, double y) const;
    bool BestAim(double& bx, double& by) const;
    // D30: has some other cell already claimed a region around this point?
    // Replaces the boolean stand-down latch, which was decided by whoever
    // flooded first rather than by whether the two cells meant the same place.
    bool ClaimedNearby(double x, double y) const;
    double ClueNow() const;
    void SendReject();
    uint32_t m_rejectsSent = 0;
    ns3::EventId m_rejectEvent;
    bool m_rejectHeard = false;   // a node under the drop resolved it as a miss
    double m_coop = 0.30;
    double m_confirmThr = params::kConfirmThreshold;

    // intra-cell tree + CL aggregation
    int32_t m_treeParent = -1;
    bool m_isCellLeader = false;
    int32_t m_cellId = -1;
    double m_cellCx = 0, m_cellCy = 0;
    ns3::Ptr<ns3::UniformRandomVariable> m_rng;
    std::map<uint16_t, uint8_t> m_rptSeen;      // origNode -> best evQ8 seen (RPT dedup)
    std::map<uint16_t, NodeEv> m_cellEvidence;  // CL: origNode -> {ev, GPS}
    bool m_sharedFlooded = false;
    std::map<uint16_t, uint8_t> m_shareSeen;    // SHARE flood dedup by origCell
    std::set<uint16_t> m_rclaimSeen;            // RCLAIM flood dedup by origCell
    std::set<int32_t> m_regionNeighbors;        // corroborating cells heard via SHARE
    // audit A4: ev is the neighbour's CELL AGGREGATE (noisy-OR, used to compare
    // cell strengths in the election); peak is its single strongest reporter's
    // evidence, at (x,y). Only peak is comparable with one of our own members.
    struct NbInfo { double ev = 0, peak = 0, x = 0, y = 0; };
    std::map<int32_t, NbInfo> m_neighborEv;     // cellId -> {aggregate, peak, peak pos}
    double m_lastFloodEv = 0;                   // re-flood SHARE as evidence grows
    uint32_t m_deferCount = 0;                  // times we yielded to a stronger cell

    // periodic report retry (single-shot RPTs die on deep trees / large areas)
    double m_lastEff = 0;
    uint32_t m_rptRepeats = 0;
    ns3::EventId m_rptRepeatEvent;
    void RptRepeatTick();

    // distributed region-leader election
    bool m_adaptiveWindow = true;
    double m_lastGrowthS = 0;    // last meaningful cell-evidence increase
    double m_alertAtS = -1;      // when this cell first crossed ALERT
    double m_electFireAtS = 0;   // currently scheduled firing time
    bool m_electScheduled = false;
    bool m_regionFormed = false;                // I fired a SUMMON, or stood down
    // D30: every aim another cell has claimed, so the stand-down can be decided
    // at ELECTION time (when this cell finally has an aim of its own) instead of
    // at ARRIVAL time (when it usually has none and therefore yielded blindly).
    std::vector<std::pair<double, double>> m_claimedAims;
    ns3::EventId m_electEvent;

    // region-leader beaconing + closure
    bool m_isLeader = false;
    bool m_isTarget = false;
    bool m_confirmed = false;    // I hold the entire dataset
    bool m_confirmHeard = false; // somebody's CONFIRM reached me -> delivery closed
    bool m_heardCue = false;    // viz: first-cue marker emitted
    uint16_t m_regionId = 1;
    // D30: the region a NON-leader belongs to, learned from the SUMMON it heard.
    // Without it every ordinary node stamped regionId=1 on its CONFIRM/REJECT,
    // so closure could not be attributed to a region and one confirm anywhere
    // silenced the whole field.
    uint16_t m_heardRegionId = 0xFFFF;
    double m_heardAimX = 0, m_heardAimY = 0;
    double m_heardAimD = 1e18;   // distance to the nearest summon aim heard
    std::vector<Cand> m_candidates;
    size_t m_candIdx = 0;
    uint32_t m_retargets = 0;
    double m_cx = 0, m_cy = 0;  // beacon coords = strongest node position
    uint32_t m_beacons = 0;
    double m_lastCueSummonS = -1e9;  // rate-limit cue-triggered re-announce
    uint32_t m_confirmsSent = 0;
    ns3::EventId m_beaconEvent;
    ns3::EventId m_confirmEvent;
};

}  // namespace ns3::uavsar

#endif  // UAV_SAR_GROUND_APP_H
