#ifndef WSN_UAV_HEX_CELLS_REFERENCE_H
#define WSN_UAV_HEX_CELLS_REFERENCE_H

// -----------------------------------------------------------------------------
// REFERENCE-ONLY: hexagonal cell partitioning helpers.
//
// Ported verbatim from
//     src/wsn/model/routing/scenario4/helper/calc-utils.{h,cc}
// where scenario4 uses hex cells with HEX_CELL_RADIUS = 80 m (see
// src/wsn/examples/scenarios/scenario4/scenario4-params.h:81).
//
// The wsn-uav module currently uses a SQUARE grid for cell partitioning
// (see models/common/cell-layer.cc and the cellKey lambda in
// models/application/uav-app.cc::BuildMission). This header is kept as a
// self-contained reference so that a future port from square → hex only
// needs to swap the coordinate helper wherever a cell id is computed.
//
// Nothing in the current build calls into this header.
// -----------------------------------------------------------------------------

#include <cmath>
#include <cstdint>

namespace ns3::wsn::uav::hex {

struct HexCellCoord {
    int32_t q;
    int32_t r;
};

// Round fractional axial (q, r) to the nearest integer axial coord, using
// cube coordinates to preserve the constraint q + r + s == 0.
inline void HexRound(double fracQ, double fracR, int32_t& q, int32_t& r) {
    const double fracS = -fracQ - fracR;

    int32_t rq = static_cast<int32_t>(std::round(fracQ));
    int32_t rr = static_cast<int32_t>(std::round(fracR));
    int32_t rs = static_cast<int32_t>(std::round(fracS));

    const double qDiff = std::fabs(rq - fracQ);
    const double rDiff = std::fabs(rr - fracR);
    const double sDiff = std::fabs(rs - fracS);

    if (qDiff > rDiff && qDiff > sDiff) {
        rq = -rr - rs;
    } else if (rDiff > sDiff) {
        rr = -rq - rs;
    }

    q = rq;
    r = rr;
}

// World (x, y) → axial (q, r) on a flat-top hex grid of radius `cellRadius`.
inline HexCellCoord ComputeHexCellCoord(double x, double y, double cellRadius) {
    const double fracQ = (std::sqrt(3.0) / 3.0 * x - 1.0 / 3.0 * y) / cellRadius;
    const double fracR = (2.0 / 3.0 * y) / cellRadius;
    HexCellCoord coord{0, 0};
    HexRound(fracQ, fracR, coord.q, coord.r);
    return coord;
}

// Pack (q, r) into a single int32 cell id. `gridOffset` must exceed the
// possible range of q so each (q, r) maps to a unique id.
// scenario4 uses a default offset of 10000 (see calc-utils.cc:79).
inline int32_t MakeCellId(int32_t q, int32_t r, int32_t gridOffset) {
    return q + r * gridOffset;
}

// 3-coloring for interference-aware scheduling: adjacent hex cells are
// guaranteed to have different colors in a hex tiling.
inline uint32_t ComputeHexColor(int32_t q, int32_t r) {
    return static_cast<uint32_t>(((q - r) % 3 + 3) % 3);
}

// World coordinate of the center of hex cell (q, r).
inline void ComputeHexCellCenter(int32_t q, int32_t r, double cellRadius,
                                 double& outCenterX, double& outCenterY) {
    outCenterX = cellRadius * (std::sqrt(3.0) * q + std::sqrt(3.0) / 2.0 * r);
    outCenterY = cellRadius * (3.0 / 2.0 * r);
}

}  // namespace ns3::wsn::uav::hex

#endif  // WSN_UAV_HEX_CELLS_REFERENCE_H
