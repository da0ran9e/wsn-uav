/*
 * WSN-UAV Module: Simulation Parameters
 * 
 * Paper: "Joint Fragment Dissemination and Edge Fusion for Fast Target 
 *        Detection in UAV-Assisted Urban IoT"
 */

#ifndef WSN_UAV_PARAMETERS_H
#define WSN_UAV_PARAMETERS_H

namespace ns3 {
namespace wsn {
namespace uav {
namespace params {

// ============================================================================
// Network Topology Parameters
// ============================================================================

// Grid spacing per paper specification
constexpr double GRID_SPACING = 20.0;  // meters
constexpr double HEX_CELL_RADIUS = 80.0;  // meters
constexpr double NEIGHBOR_DISCOVERY_RADIUS = 80.0;  // meters

// ============================================================================
// UAV Parameters
// ============================================================================

constexpr double UAV_ALTITUDE = 20.0;  // meters (h)
constexpr double UAV_SPEED = 20.0;  // m/s (v)
constexpr double UAV_BROADCAST_RADIUS = 50.0;  // meters (Rb)

// ============================================================================
// Fragment and Recognition Parameters
// ============================================================================

constexpr uint32_t DEFAULT_NUM_FRAGMENTS = 10;  // K
constexpr double MASTER_FILE_CONFIDENCE = 0.90;  // C_master
constexpr uint32_t IMAGE_WIDTH_PIXELS = 416;
constexpr uint32_t IMAGE_HEIGHT_PIXELS = 416;
constexpr uint32_t BYTES_PER_PIXEL = 3;  // RGB

// ============================================================================
// Confidence Thresholds (from paper Section III.C)
// ============================================================================

constexpr double COOPERATION_THRESHOLD = 0.30;  // τ_coop
constexpr double ALERT_THRESHOLD = 0.75;  // τ_alert
constexpr double SUSPICIOUS_COVERAGE_PERCENT = 0.30;  // ρ
constexpr double CELL_COVERAGE_THRESHOLD = 0.30;  // β (GMC algorithm)

// ============================================================================
// Timing Parameters
// ============================================================================

constexpr double STARTUP_DURATION = 5.0;  // seconds
constexpr double UAV_PLANNING_DELAY = 0.2;  // seconds (after startup)
constexpr double FRAGMENT_BROADCAST_INTERVAL = 0.2;  // seconds
constexpr double COOPERATION_STAGGER_STEP = 0.02;  // seconds/BFS_level
constexpr double COOPERATION_JITTER_MAX = 0.015;  // seconds

// ============================================================================
// Radio / PHY Parameters (CC2420 / IEEE 802.15.4)
// ============================================================================

constexpr double TX_POWER_DBM = -10.0;  // dBm (balanced for realistic channel with some drops)
constexpr double RX_SENSITIVITY_DBM = -95.0;  // dBm
constexpr double NOISE_FLOOR_DBM = -101.0;  // dBm (CC2420 spec)
constexpr uint32_t PACKET_SIZE_BYTES = 100;
constexpr double DATA_RATE_BPS = 250000.0;  // 250 kbps (IEEE 802.15.4)

// ============================================================================
// Trajectory Planning (GMC Algorithm)
// ============================================================================

constexpr double GMC_ALPHA = 0.2;  // coverage/cost tradeoff factor
constexpr bool USE_CELL_AWARE_EXPANSION = true;
constexpr bool USE_KMEANS_CENTROIDS = true;
constexpr uint32_t MAX_KMEANS_CENTROIDS = 8;

}  // namespace params
}  // namespace uav
}  // namespace wsn
}  // namespace ns3

#endif  // WSN_UAV_PARAMETERS_H
