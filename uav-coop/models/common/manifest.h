// Compact manifests: a set of chunk indices of a K-chunk file, sent in frames.
//
// Each frame describes one segment [a, b) of the file on its own, so losing a frame
// loses only that segment. The body is whichever is shortest of:
//   LIST_IN   the members, as Rice-coded gaps between successive indices
//   LIST_OUT  the non-members, likewise
//   BITMAP    one bit per chunk of the segment
// Losses after a UAV pass are scattered (fading is drawn per packet), so runs are
// short and gap coding beats range coding; a node missing almost nothing or almost
// everything costs a few bytes.
//
// Frame layout (all big-endian):
//   B0     kind:4 | enc:2 | rsv:2        kind is the caller's message type
//   B1-2   a          B3-4   b           the segment
//   B5     riceK:4 | rsv:4
//   B6-7   count      number of listed indices (LIST_IN / LIST_OUT)
//   B8..   body

#ifndef UAVCOOP_MANIFEST_H
#define UAVCOOP_MANIFEST_H

#include <cstdint>
#include <vector>

namespace ns3::uavcoop {

constexpr uint32_t kManifestHeader = 8;

enum class ManifestEnc : uint8_t { LIST_IN = 0, LIST_OUT = 1, BITMAP = 2 };

struct ManifestFrame {
    uint8_t kind = 0;
    uint32_t a = 0, b = 0;
    std::vector<uint8_t> bytes;   // the whole frame, header included
};

// One frame for the longest segment [a, b) that fits in maxBytes, b <= K.
// `in` has K entries (1 = member).
ManifestFrame EncodeManifest(uint8_t kind, const std::vector<uint8_t>& in, uint32_t a,
                             uint32_t maxBytes);

// Decode a frame: kind, segment, and membership of every chunk in [a, b).
struct ManifestView {
    uint8_t kind = 0;
    ManifestEnc enc = ManifestEnc::BITMAP;
    uint32_t a = 0, b = 0;
    std::vector<uint8_t> member;   // b - a entries
};
ManifestView DecodeManifest(const std::vector<uint8_t>& frame);

}  // namespace ns3::uavcoop

#endif
