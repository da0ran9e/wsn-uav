#include "manifest.h"

#include <algorithm>
#include <cstdint>

namespace ns3::uavcoop {

namespace {

class BitWriter {
  public:
    void Put(uint32_t v, uint32_t n) {   // n low bits of v, MSB first
        for (uint32_t i = n; i-- > 0;) Bit((v >> i) & 1);
    }
    void Bit(uint32_t x) {
        if (m_n % 8 == 0) m_b.push_back(0);
        if (x) m_b.back() |= (uint8_t)(0x80 >> (m_n % 8));
        ++m_n;
    }
    std::vector<uint8_t> m_b;
    uint32_t m_n = 0;
};

class BitReader {
  public:
    BitReader(const std::vector<uint8_t>& b, size_t from) : m_b(b), m_pos(from * 8) {}
    uint32_t Bit() {
        const uint32_t x = (m_b.at(m_pos / 8) >> (7 - m_pos % 8)) & 1;
        ++m_pos;
        return x;
    }
    uint32_t Get(uint32_t n) {
        uint32_t v = 0;
        for (uint32_t i = 0; i < n; ++i) v = v << 1 | Bit();
        return v;
    }
  private:
    const std::vector<uint8_t>& m_b;
    size_t m_pos;
};

// The listed indices of [a, b): members (want = 1) or non-members (want = 0).
std::vector<uint32_t> Listed(const std::vector<uint8_t>& in, uint32_t a, uint32_t b, uint8_t want) {
    std::vector<uint32_t> v;
    for (uint32_t j = a; j < b; ++j)
        if ((in[j] != 0) == (want != 0)) v.push_back(j);
    return v;
}

// Rice parameter and size in bits for the gaps of `idx` from a.
std::pair<uint32_t, uint32_t> RiceBest(const std::vector<uint32_t>& idx, uint32_t a) {
    uint32_t bestK = 0, bestBits = UINT32_MAX;
    for (uint32_t k = 0; k < 16; ++k) {
        uint64_t bits = 0;
        uint32_t prev = a;
        for (uint32_t x : idx) {
            const uint32_t g = x - prev;
            bits += (g >> k) + 1 + k;
            prev = x + 1;
        }
        if (bits < bestBits) { bestBits = (uint32_t)std::min<uint64_t>(bits, UINT32_MAX - 1); bestK = k; }
    }
    return {bestK, bestBits};
}

struct Choice {
    ManifestEnc enc;
    uint32_t k, bodyBytes;
};

Choice Best(const std::vector<uint8_t>& in, uint32_t a, uint32_t b) {
    const auto inL = Listed(in, a, b, 1), outL = Listed(in, a, b, 0);
    const auto [kIn, bIn] = RiceBest(inL, a);
    const auto [kOut, bOut] = RiceBest(outL, a);
    Choice c{ManifestEnc::BITMAP, 0, (b - a + 7) / 8};
    if ((bIn + 7) / 8 < c.bodyBytes && inL.size() < 65536) c = {ManifestEnc::LIST_IN, kIn, (bIn + 7) / 8};
    if ((bOut + 7) / 8 < c.bodyBytes && outL.size() < 65536) c = {ManifestEnc::LIST_OUT, kOut, (bOut + 7) / 8};
    return c;
}

}  // namespace

ManifestFrame EncodeManifest(uint8_t kind, const std::vector<uint8_t>& in, uint32_t a,
                             uint32_t maxBytes) {
    const uint32_t K = (uint32_t)in.size();
    // The longest segment that fits, growing b one chunk at a time and keeping the
    // Rice sizes of both lists for every parameter up to date (O(16) per chunk).
    uint64_t bits[2][16] = {};
    uint32_t prev[2] = {a, a};
    uint32_t b = a;
    while (b < K) {
        const int l = in[b] != 0 ? 0 : 1;   // 0: a member, 1: a non-member
        uint64_t next[16];
        uint64_t bestOther = UINT64_MAX, bestThis = UINT64_MAX;
        for (uint32_t k = 0; k < 16; ++k) {
            next[k] = bits[l][k] + ((b - prev[l]) >> k) + 1 + k;
            bestThis = std::min(bestThis, next[k]);
            bestOther = std::min(bestOther, bits[1 - l][k]);
        }
        const uint64_t body = std::min({(uint64_t)(b + 1 - a), bestThis, bestOther});
        if (b > a && kManifestHeader + (body + 7) / 8 > maxBytes) break;
        std::copy(next, next + 16, bits[l]);
        prev[l] = b + 1;
        ++b;
    }
    const Choice c = Best(in, a, b);
    ManifestFrame f;
    f.kind = kind;
    f.a = a;
    f.b = b;
    std::vector<uint8_t>& o = f.bytes;
    o.push_back((uint8_t)(kind << 4 | (uint8_t)c.enc << 2));
    o.push_back(a >> 8); o.push_back(a & 0xff);
    o.push_back(b >> 8); o.push_back(b & 0xff);
    o.push_back((uint8_t)(c.k << 4));
    BitWriter w;
    uint32_t count = 0;
    if (c.enc == ManifestEnc::BITMAP) {
        for (uint32_t j = a; j < b; ++j) w.Bit(in[j] != 0);
    } else {
        const auto idx = Listed(in, a, b, c.enc == ManifestEnc::LIST_IN ? 1 : 0);
        count = (uint32_t)idx.size();
        uint32_t prev = a;
        for (uint32_t x : idx) {
            const uint32_t g = x - prev;
            for (uint32_t q = g >> c.k; q > 0; --q) w.Bit(1);
            w.Bit(0);
            w.Put(g & ((1u << c.k) - 1), c.k);
            prev = x + 1;
        }
    }
    o.push_back(count >> 8); o.push_back(count & 0xff);
    o.insert(o.end(), w.m_b.begin(), w.m_b.end());
    return f;
}

ManifestView DecodeManifest(const std::vector<uint8_t>& f) {
    ManifestView v;
    v.kind = f.at(0) >> 4;
    v.enc = (ManifestEnc)((f[0] >> 2) & 3);
    v.a = (uint32_t)f.at(1) << 8 | f.at(2);
    v.b = (uint32_t)f.at(3) << 8 | f.at(4);
    const uint32_t k = f.at(5) >> 4;
    const uint32_t count = (uint32_t)f.at(6) << 8 | f.at(7);
    BitReader r(f, kManifestHeader);
    if (v.enc == ManifestEnc::BITMAP) {
        for (uint32_t j = v.a; j < v.b; ++j) v.member.push_back((uint8_t)r.Bit());
        return v;
    }
    const uint8_t listed = v.enc == ManifestEnc::LIST_IN ? 1 : 0;
    v.member.assign(v.b - v.a, (uint8_t)(1 - listed));
    uint32_t prev = v.a;
    for (uint32_t i = 0; i < count; ++i) {
        uint32_t q = 0;
        while (r.Bit()) ++q;
        const uint32_t x = prev + (q << k | r.Get(k));
        v.member.at(x - v.a) = listed;
        prev = x + 1;
    }
    return v;
}

}  // namespace ns3::uavcoop
