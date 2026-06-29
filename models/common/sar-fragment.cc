#include "sar-fragment.h"

#include <algorithm>
#include <cmath>

namespace ns3::wsn::uav::sar {

std::vector<Fragment> FragmentSet::Generate(uint32_t k,
                                            uint32_t minBytes,
                                            uint32_t maxBytes,
                                            double recognitionFrac) {
    std::vector<Fragment> frags;
    if (k == 0) return frags;
    frags.reserve(k);

    uint32_t recCount = std::max<uint32_t>(1, static_cast<uint32_t>(k * recognitionFrac));
    recCount = std::min(recCount, k);
    uint32_t dataCount = k - recCount;

    // Recognition fragments: small, near minBytes, spread up to ~10% of range.
    uint32_t recHi = minBytes + (maxBytes - minBytes) / 10;
    for (uint32_t i = 0; i < recCount; i++) {
        uint32_t sz = (recCount == 1)
                          ? minBytes
                          : minBytes + (recHi - minBytes) * i / (recCount - 1);
        Fragment f;
        f.id = static_cast<uint16_t>(i);
        f.sizeBytes = sz;
        f.cls = FragClass::RECOGNITION;
        f.numChunks = static_cast<uint16_t>((sz + CHUNK_PAYLOAD - 1) / CHUNK_PAYLOAD);
        frags.push_back(f);
    }

    // Data fragments: large, spread across [recHi, maxBytes].
    for (uint32_t j = 0; j < dataCount; j++) {
        uint32_t sz = (dataCount == 1)
                          ? maxBytes
                          : recHi + (maxBytes - recHi) * j / (dataCount - 1);
        Fragment f;
        f.id = static_cast<uint16_t>(recCount + j);
        f.sizeBytes = sz;
        f.cls = FragClass::DATA;
        f.numChunks = static_cast<uint16_t>((sz + CHUNK_PAYLOAD - 1) / CHUNK_PAYLOAD);
        frags.push_back(f);
    }

    // Priority: smaller fragment => higher priority. Rank by size ascending.
    std::vector<uint32_t> order(frags.size());
    for (uint32_t i = 0; i < order.size(); i++) order[i] = i;
    std::sort(order.begin(), order.end(),
              [&](uint32_t a, uint32_t b) { return frags[a].sizeBytes < frags[b].sizeBytes; });
    uint8_t rank = static_cast<uint8_t>(frags.size());
    for (uint32_t idx : order) {
        frags[idx].priority = rank;  // first (smallest) gets highest number
        if (rank > 0) rank--;
    }

    return frags;
}

uint32_t FragmentSet::TotalBytes(const std::vector<Fragment>& frags) {
    uint32_t t = 0;
    for (const auto& f : frags) t += f.sizeBytes;
    return t;
}

uint32_t FragmentSet::TotalChunks(const std::vector<Fragment>& frags) {
    uint32_t t = 0;
    for (const auto& f : frags) t += f.numChunks;
    return t;
}

}  // namespace ns3::wsn::uav::sar
