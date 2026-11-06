#ifndef WSN_UAV_SAR_FRAGMENT_H
#define WSN_UAV_SAR_FRAGMENT_H

// Search-data fragment model for the SAR scenario.
// The BS splits its search dataset (image/video) into K fragments of varying
// size. Small fragments carry high-recognition cues (color/clothes/shape) and
// get higher priority; large fragments carry forensic data. Sizes span
// 100B..20KB. Detection/CV is NOT simulated — only the networking matters, so
// payloads are opaque byte counts.

#include "sar-types.h"

#include <cstdint>
#include <vector>

namespace ns3::wsn::uav::sar {

struct Fragment {
    uint16_t  id;
    uint32_t  sizeBytes;
    FragClass cls;
    uint8_t   priority;   // higher = sent first (smaller frags rank higher)
    uint16_t  numChunks;  // ceil(sizeBytes / CHUNK_PAYLOAD)
};

class FragmentSet {
public:
    // Build K fragments. The first `recognitionFrac*K` (>=1) are RECOGNITION
    // class with small sizes; the rest are DATA class with large sizes. Sizes
    // are spread deterministically across [minB,maxB] so runs are reproducible.
    static std::vector<Fragment> Generate(uint32_t k,
                                          uint32_t minBytes = 100,
                                          uint32_t maxBytes = 20000,
                                          double recognitionFrac = 0.34);

    // Total bytes across all fragments.
    static uint32_t TotalBytes(const std::vector<Fragment>& frags);
    // Total chunks (LR-WPAN packets) needed to deliver all fragments.
    static uint32_t TotalChunks(const std::vector<Fragment>& frags);
};

}  // namespace ns3::wsn::uav::sar

#endif  // WSN_UAV_SAR_FRAGMENT_H
