#ifndef WSN_UAV_SAR_TYPES_H
#define WSN_UAV_SAR_TYPES_H

// Shared contract for the SAR (Search-and-Rescue) experiment, Câu chuyện 1.
// Header-only: enums, packet layout constants, small structs. No ns-3 deps so
// it can be included from both model and helper layers.
//
// Wire format rule (LR-WPAN PSDU = 127B; safe app payload <= 100B):
//   byte[0] = MsgType
//   byte[1] = destId  (0xFF = broadcast)
// Everything else is little-endian packed. Coordinates are decimetres (i16).

#include <cstdint>

namespace ns3::wsn::uav::sar {

// ---- message types --------------------------------------------------------
enum class MsgType : uint8_t {
    SAR_DATA_FRAG    = 10,  // UAV -> ground: a (chunk of a) search-data fragment
    CONFIRM_REQ      = 11,  // ground -> neighbour: please corroborate my clue
    CONFIRM_ACK      = 12,  // neighbour -> ground: corroborated
    EMERGENCY_BEACON = 13,  // ground -> UAV (broadcast): summon a DATA UAV
    FULLDATA_FRAG    = 14,  // DATA UAV -> target: full dataset delivery chunk
    CUSTODY_ACK      = 15,  // receiver -> sender: chunk received (provenance)
    A2A_BEACON_RELAY = 16,  // UAV -> UAV: relay an emergency beacon
};

inline constexpr uint8_t BROADCAST_ID = 0xFF;

// ---- fragment classes -----------------------------------------------------
enum class FragClass : uint8_t {
    RECOGNITION = 0,  // small, high recognition value (color/clothes/shape)
    DATA        = 1,  // larger forensic data
    FULL        = 2,  // full dataset delivered after confirmation
};

// ---- UAV roles ------------------------------------------------------------
enum class UavRole : uint8_t {
    FAST = 0,  // carries RECOGNITION frags, flies fast, listens for beacons
    DATA = 1,  // carries DATA frags, flies slower, delivers FULL on summon
};

// ---- comparison schemes (baselines) --------------------------------------
enum class Scheme : uint8_t {
    PROPOSED = 0,  // multi-UAV + role split + emergency beacon + A2A relay
    SINGLE   = 1,  // one UAV, sequential coverage, no cooperation
    NOCOOP   = 2,  // multi-UAV broadcast but no beacon/confirm/divert
};

// ---- packet header sizes (bytes) -----------------------------------------
// SAR_DATA_FRAG / FULLDATA_FRAG header, payload follows:
//   [type:u8][dst:u8][fragId:u16][seq:u16][total:u16][cls:u8]  = 9B
inline constexpr uint32_t DATA_FRAG_HDR   = 1 + 1 + 2 + 2 + 2 + 1;
// CONFIRM_REQ / CONFIRM_ACK: [type:u8][dst:u8][evtId:u16][nodeId:u8] = 5B
inline constexpr uint32_t CONFIRM_HDR     = 1 + 1 + 2 + 1;
// EMERGENCY_BEACON: [type:u8][0xFF][evtId:u16][cellId:u8][x:i16][y:i16][aoiMs:u16][prio:u8] = 12B
inline constexpr uint32_t BEACON_LEN      = 1 + 1 + 2 + 1 + 2 + 2 + 2 + 1;
// CUSTODY_ACK: [type:u8][dst:u8][fragId:u16][holderId:u8] = 5B
inline constexpr uint32_t CUSTODY_HDR     = 1 + 1 + 2 + 1;
// A2A_BEACON_RELAY wraps a beacon: [type:u8][dst:u8] + BEACON body (10B) = 12B
inline constexpr uint32_t A2A_RELAY_HDR   = 1 + 1;

// Max app payload per LR-WPAN packet (conservative). Chunk size for fragments.
inline constexpr uint32_t MAX_APP_PAYLOAD = 100;
inline constexpr uint32_t CHUNK_PAYLOAD   = MAX_APP_PAYLOAD - DATA_FRAG_HDR;  // 91B

// Back-to-back Send() stagger to avoid MAC queue overflow (verified >=200ms).
inline constexpr double SEND_STAGGER_S = 0.2;

}  // namespace ns3::wsn::uav::sar

#endif  // WSN_UAV_SAR_TYPES_H
