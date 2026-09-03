#ifndef UAV_SAR_TYPES_H
#define UAV_SAR_TYPES_H

// Wire message types + layout constants for the packet-level plane (radio).
// byte[0]=MsgType, byte[1]=dst (0xFF broadcast). Little-endian; coords in dm.
// The WSN control plane (clue report up the cell tree, cross-cell share) now
// crosses the radio too — RPT/SHARE below — and is subject to the same channel
// as every other packet (A2G/G2G path loss + Nakagami fading + shadowing).

#include <cstdint>

namespace ns3::uavsar {

enum class Msg : uint8_t {
    CUE      = 1,   // FAST -> ground: chunk of a cue fragment (same layout as FULL)
    SUMMON   = 2,   // region-leader -> sky: come here  [regionId:u16][cx:i16][cy:i16]
                    //   (cx,cy) = strongest node's own GPS, learned via RPT
    A2A      = 3,   // FAST -> DATA relay of a SUMMON            (SUMMON body)
    FULL     = 4,   // DATA -> ground: full-data chunk           [id:u16][seq:u16][total:u16][layer:u8]
    CONFIRM  = 5,   // ground -> DATA: full dataset received/confirmed [regionId:u16][nodeId:u8]
    REPORT   = 6,   // UAV -> BS: mission report (small)          [regionId:u16][resultQ8:u8]
    HANDOFF  = 7,   // DATA -> FAST: carry the report home (fast) [regionId:u16]
    RPT      = 8,   // member -> up the cell tree -> Cell Leader: clue evidence + own GPS
                    //   [nextHop:u16][origNode:u16][evQ8:u8][hopsLeft:u8][x:i16][y:i16]
    SHARE    = 9,   // Cell Leader -> flood: cross-cell evidence share
                    //   [origCell:u16][evQ8:u8][cx:i16][cy:i16][hopsLeft:u8]
    CLAIM    = 10,  // UAV -> fleet: I am taking this role (radio mutual exclusion,
                    //   replaces the shared-memory token) [regionId:u16][role:u8][id:u16]
                    //   role 0 = DATA delivery diverter, 1 = FAST report courier
    RCLAIM   = 11,  // audit B2: Cell Leader -> flood: I have summoned, stand down.
                    //   Same body and flood machinery as SHARE. SUMMON is a
                    //   ONE-HOP broadcast, but cell leaders sit 63-156 m apart
                    //   while the ground radio reaches ~37 m, so the suppression
                    //   half of the election could never physically arrive and
                    //   every alerting cell summoned independently.
    ECHO     = 12,  // audit W4: node -> whatever UAV is overhead, DIRECT and
                    //   single-hop: "my evidence is X, I am at (x,y)". This is
                    //   the closed-loop NON-cooperative baseline's entire
                    //   feedback path -- no cell tree, no cross-cell SHARE, no
                    //   election. It exists so the proposed scheme's gain can be
                    //   attributed to COOPERATION rather than merely to having
                    //   feedback at all. [origNode:u16][evQ8:u8][x:i16][y:i16]
    REJECT   = 13,  // ground -> sky + leader: I now hold the COMPLETE reference
                    //   dataset and I do NOT match it. Only a node with the whole
                    //   dataset can say this, which is exactly why delivering is
                    //   an act of disambiguation rather than only of service: the
                    //   cue fragments a false positive matched on are not enough
                    //   to rule it out, the full reference is. Same body as
                    //   CONFIRM. It is the negative half of loop closure, and it
                    //   is what lets a DATA UAV leave a wrong region on evidence
                    //   instead of on a timeout. [regionId:u16][nodeId:u8]
};

inline constexpr uint8_t kBroadcast = 0xFF;

// CUE and FULL share the chunk layout so a fragment is byte-honest whichever
// path delivered it: [type][dst][fragId:u16][seq:u16][total:u16][layer:u8]+payload.
inline constexpr uint32_t kChunkHdr   = 1 + 1 + 2 + 2 + 2 + 1;      // 9, payload follows
inline constexpr uint32_t kSummonLen  = 1 + 1 + 2 + 2 + 2;          // 8
inline constexpr uint32_t kA2ALen     = 1 + 1 + 2 + 2 + 2;          // 8 (same body)
// D38: [type][dst][rid:u16][nodeId:u8][x:i16_dm][y:i16_dm] = 9.
// The coordinates are the CONFIRMING NODE's own position, and they are the
// reason they are here: the fleet used to carry the SUMMON aim home as the
// answer, but the aim is the leader's guess at where the evidence points,
// whereas a confirming node is one that holds the complete reference AND still
// matches it, so it is within sensing range of the real thing. Measured at
// 24x24: an aim 45 m from the victim, and closer to a decoy than to the victim,
// was reported as the fix while the nodes that actually matched sat 20 m away.
inline constexpr uint32_t kConfirmLen = 1 + 1 + 2 + 1 + 2 + 2;      // 9
inline constexpr uint32_t kRejectLen  = kConfirmLen;                // same body
// audit B3: REPORT and HANDOFF carry the victim fix (decimetres, i16) so the
// estimate physically travels to the BS over the radio instead of being read out
// of simulator state. flags bit0 = "a fix follows"; a UAV that never learned one
// (every blind-coverage baseline) clears it and the BS records no position.
inline constexpr uint8_t  kFlagHasFix = 0x01;
// D37: a REPORT carries UP TO kMaxFixes confirmed positions, not one.
//
// One slot was the binding constraint on the whole mission, not a detail. With
// two DATA UAVs it capped a run at two fixes however many victims were found:
// measured with the fleet kept airborne until the sweep completed, 12 of 16
// victims had a UAV deliver to them and only 8 fixes ever reached the BS, and
// every attempt to serve more candidates traded straight against reporting
// them. [type][flags][count:u8] + count x [x:i16][y:i16].
inline constexpr uint32_t kMaxFixes   = 4;
inline constexpr uint32_t kReportHdr  = 1 + 1 + 1;                  // 3
inline constexpr uint32_t kReportLen  = kReportHdr + kMaxFixes * 4; // 19
inline constexpr uint32_t kHandoffLen = 1 + 1 + 2 + 2 + 2;          // 8
inline constexpr uint32_t kRptLen     = 1 + 2 + 2 + 1 + 1 + 2 + 2;  // 11 (+self GPS)
// audit A4/A5: SHARE carries the cell aggregate (evQ8, used by the election to
// compare CELL strengths) AND the cell's strongest single reporter — its
// evidence (peakQ8) and its GPS-reported position. The two cannot share one
// byte: the aggregate is a noisy-OR union and is therefore always >= any
// member, so an aiming rule that compared it against a single node's evidence
// would pick a neighbouring cell every time. Carrying the peak is what lets a
// leader aim outside its own cell at all.
// [type][origCell:u16][evQ8:u8][peakQ8:u8][x:i16][y:i16][ttl:u8]
inline constexpr uint32_t kShareLen   = 1 + 2 + 1 + 1 + 2 + 2 + 1;  // 10
inline constexpr uint32_t kRclaimLen  = kShareLen;                  // same body
inline constexpr uint32_t kEchoLen    = 1 + 2 + 1 + 2 + 2;          // 8 (audit W4)
// CLAIM roles: 0 = taking a region, 1 = couriering the report, 2 = delivered
// there, 3 = my band is swept, 4 = I have LANDED at the base, 5 = base orders
// Phase 2 to launch. 4 and 5 exist because "the scouts have finished sweeping"
// and "the scouts are home" and "a candidate exists" are three different
// moments, and the rotary team may be told to wait for any of them.
inline constexpr uint32_t kClaimLen   = 1 + 2 + 1 + 2;              // 6 [region][role][id]

inline constexpr uint32_t kMaxPayload = 100;                    // safe app payload
inline constexpr uint32_t kChunkBytes = kMaxPayload - kChunkHdr;  // 91

}  // namespace ns3::uavsar

#endif  // UAV_SAR_TYPES_H
