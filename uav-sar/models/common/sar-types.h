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
};

inline constexpr uint8_t kBroadcast = 0xFF;

// CUE and FULL share the chunk layout so a fragment is byte-honest whichever
// path delivered it: [type][dst][fragId:u16][seq:u16][total:u16][layer:u8]+payload.
inline constexpr uint32_t kChunkHdr   = 1 + 1 + 2 + 2 + 2 + 1;      // 9, payload follows
inline constexpr uint32_t kSummonLen  = 1 + 1 + 2 + 2 + 2;          // 8
inline constexpr uint32_t kA2ALen     = 1 + 1 + 2 + 2 + 2;          // 8 (same body)
inline constexpr uint32_t kConfirmLen = 1 + 1 + 2 + 1;              // 5
// audit B3: REPORT and HANDOFF carry the victim fix (decimetres, i16) so the
// estimate physically travels to the BS over the radio instead of being read out
// of simulator state. flags bit0 = "a fix follows"; a UAV that never learned one
// (every blind-coverage baseline) clears it and the BS records no position.
inline constexpr uint8_t  kFlagHasFix = 0x01;
inline constexpr uint32_t kReportLen  = 1 + 1 + 2 + 1 + 2 + 2;      // 9
inline constexpr uint32_t kHandoffLen = 1 + 1 + 2 + 2 + 2;          // 8
inline constexpr uint32_t kRptLen     = 1 + 2 + 2 + 1 + 1 + 2 + 2;  // 11 (+self GPS)
inline constexpr uint32_t kShareLen   = 1 + 2 + 1 + 2 + 2 + 1;      // 9
inline constexpr uint32_t kClaimLen   = 1 + 2 + 1 + 2;              // 6 [region][role][id]

inline constexpr uint32_t kMaxPayload = 100;                    // safe app payload
inline constexpr uint32_t kChunkBytes = kMaxPayload - kChunkHdr;  // 91

}  // namespace ns3::uavsar

#endif  // UAV_SAR_TYPES_H
