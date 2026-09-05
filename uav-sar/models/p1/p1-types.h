#ifndef UAV_SAR_P1_TYPES_H
#define UAV_SAR_P1_TYPES_H

// The few enumerations everything in Phase 1 shares.

#include <cstdint>

namespace ns3::uavsar::p1 {

// What a cell is for.
//
// There are only two kinds, and the reason is N3: THE CLUSTER HEAD IS THE
// MATCHING SUBJECT. It runs the match against its OWN observation, so what a
// cell needs is one node with a camera to be the head. No reference data moves
// inside the cluster, so no other member's sensor enters this phase at all.
//
// An earlier revision carried three classes (A/B/C) separating cells by SENSOR
// MODALITY -- a cell that could detect but never discriminate. That distinction
// is gone: the scope assumption (0.2.2) is that every cell holds at least one
// camera node, and a cell that does not simply has no demand and drops out of
// the routing problem. Keeping a class for a case the scope excludes would be
// modelling something the design does not claim to handle.
enum class CellClass : uint8_t {
    SERVED = 0,   // holds a camera node -> elects a head, has demand
    BARREN = 1,   // no camera at all -> theta = 0, outside the stated scope
};

inline const char* CellClassName(CellClass c) {
    return c == CellClass::SERVED ? "served" : "barren";
}

}  // namespace ns3::uavsar::p1

#endif  // UAV_SAR_P1_TYPES_H
