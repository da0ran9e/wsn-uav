/*
 * WSN-UAV Module: Data Types and Enums
 */

#ifndef WSN_UAV_TYPES_H
#define WSN_UAV_TYPES_H

#include "ns3/vector.h"

namespace ns3 {
namespace wsn {
namespace uav {

// ============================================================================
// Waypoint Struct (UAV trajectory point)
// ============================================================================

struct Waypoint {
    double x = 0.0;  // position (meters)
    double y = 0.0;
    double z = 0.0;
    double arrivalTimeSec = 0.0;  // absolute simulation time (seconds)
};

// ============================================================================
// Node Cell Assignment
// ============================================================================

struct NodeCell {
    uint32_t nodeId = 0;
    int32_t cellId = 0;
    bool isLeader = false;
};

// ============================================================================
// Cooperation Trigger Reasons
// ============================================================================

enum class CoopTrigger {
    CONFIDENCE_REACHED,  // confidence >= τ_coop
    CONTACT_ENDED,       // UAV contact window closed
    MANIFEST_RECEIVED    // peer sent manifest with new fragments
};

// ============================================================================
// Node Lifecycle Phases
// ============================================================================

enum class NodeLifecyclePhase {
    BOOTSTRAP,   // initializing
    DISCOVERY,   // startup phase (neighbor discovery)
    ACTIVE,      // receiving fragments + cooperating
    DEGRADED,    // isolated or low connectivity
    DEAD         // no energy or disconnected
};

}  // namespace uav
}  // namespace wsn
}  // namespace ns3

#endif  // WSN_UAV_TYPES_H
