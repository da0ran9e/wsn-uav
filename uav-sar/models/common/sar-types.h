#ifndef UAV_SAR_TYPES_H
#define UAV_SAR_TYPES_H

// Wire message types + layout constants for the packet-level plane (radio).
// byte[0]=MsgType, byte[1]=dst (0xFF broadcast). Little-endian; coords in dm.
// The control plane (clue report / cross-cell share / region election) is
// handled event-level by RegionCoordinator; only these cross the radio.

#include <cstdint>

namespace ns3::uavsar {

enum class Msg : uint8_t {
    CUE      = 1,   // FAST -> ground: chunk of a cue fragment (same layout as FULL)
    SUMMON   = 2,   // region-leader -> sky: come to me          [regionId:u16][cx:i16][cy:i16]
    A2A      = 3,   // FAST -> DATA relay of a SUMMON            (SUMMON body)
    FULL     = 4,   // DATA -> ground: full-data chunk           [id:u16][seq:u16][total:u16][layer:u8]
    CONFIRM  = 5,   // ground -> DATA: full dataset received/confirmed [regionId:u16][nodeId:u8]
    REPORT   = 6,   // UAV -> BS: mission report (small)          [regionId:u16][resultQ8:u8]
    HANDOFF  = 7,   // DATA -> FAST: carry the report home (fast) [regionId:u16]
};

inline constexpr uint8_t kBroadcast = 0xFF;

// CUE and FULL share the chunk layout so a fragment is byte-honest whichever
// path delivered it: [type][dst][fragId:u16][seq:u16][total:u16][layer:u8]+payload.
inline constexpr uint32_t kChunkHdr   = 1 + 1 + 2 + 2 + 2 + 1;  // 9, payload follows
inline constexpr uint32_t kSummonLen  = 1 + 1 + 2 + 2 + 2;      // 8
inline constexpr uint32_t kA2ALen     = 1 + 1 + 2 + 2 + 2;      // 8 (same body)
inline constexpr uint32_t kConfirmLen = 1 + 1 + 2 + 1;          // 5
inline constexpr uint32_t kReportLen  = 1 + 1 + 2 + 1;          // 5
inline constexpr uint32_t kHandoffLen = 1 + 1 + 2;              // 4

inline constexpr uint32_t kMaxPayload = 100;                    // safe app payload
inline constexpr uint32_t kChunkBytes = kMaxPayload - kChunkHdr;  // 91

}  // namespace ns3::uavsar

#endif  // UAV_SAR_TYPES_H
