/*
 * Fragment Dissemination Application
 * Handles both UAV fragment broadcast and ground node cooperation
 */

#ifndef WSN_UAV_FRAGMENT_DISSEMINATION_APP_H
#define WSN_UAV_FRAGMENT_DISSEMINATION_APP_H

#include "ns3/application.h"
#include "ns3/event-id.h"
#include "ns3/ptr.h"
#include "ns3/packet.h"
#include "ns3/address.h"
#include "ns3/net-device.h"
#include "ns3/mac16-address.h"
#include "fragment-model.h"
#include "confidence-model.h"
#include "../common/statistics-collector.h"
#include "../common/types.h"
#include "../common/packet-header.h"
#include <cstdint>
#include <set>

namespace ns3 {
namespace wsn {
namespace uav {

// ============================================================================
// Fragment Dissemination Application
// ============================================================================

class FragmentDisseminationApp : public Application {
public:
    enum class Role { UAV_BROADCASTER, GROUND_NODE };
    
    static TypeId GetTypeId();
    
    explicit FragmentDisseminationApp();
    virtual ~FragmentDisseminationApp();
    
    // Configuration (called before StartApplication)
    void SetRole(Role role);
    void SetNodeId(uint32_t id);
    void SetFragments(const FragmentCollection& frags);
    void SetExpectedFragmentCount(uint32_t count);
    void SetDetectionNodeId(uint32_t id);  // n* (suspicious seed node)
    void SetThresholds(double cooperationThreshold, double alertThreshold);
    void SetBfsLevel(uint32_t level);  // For cooperation stagger delay
    void SetGroundNodeCount(uint32_t count);  // To identify UAV packets (srcNodeId >= count)
    void SetStatisticsCollector(Ptr<StatisticsCollector> stats);

    // Callbacks
    typedef Callback<void, uint32_t, double> DetectionCallback;  // nodeId, timeSeconds
    typedef Callback<void, uint32_t, uint32_t, uint32_t> PacketDroppedCallback;  // srcNodeId, dstNodeId, fragmentId

    void SetDetectionCallback(DetectionCallback cb);
    void SetPacketDroppedCallback(PacketDroppedCallback cb);

    // Network device (for real NetDevice packet transmission)
    void SetNetDevice(Ptr<NetDevice> device);

    // Receive packet from MAC layer
    void OnPacketReceived(Ptr<const Packet> pkt, double rssiDbm);

    // Query state
    double GetConfidence() const;
    bool IsDetected() const;
    const ConfidenceModel& GetConfidenceModel() const;

private:
    // Application lifecycle
    void StartApplication() override;
    void StopApplication() override;
    
    // UAV behavior: broadcast fragments cyclically
    void DoBroadcast();
    void SendFragment(uint32_t fragmentId);

    // Ground node behavior: receive and cooperate
    void ScheduleCooperation(CoopTrigger trigger);
    void DoCooperation();
    void SendManifest();
    void ProcessIncomingManifest(uint32_t srcNodeId, const std::set<uint32_t>& theirFragments);
    void SendMissingFragmentTo(uint32_t dstNodeId, uint32_t fragmentId);
    
    
    // State
    Role m_role = Role::GROUND_NODE;
    uint32_t m_nodeId = 0;
    uint32_t m_detectionNodeId = 0;
    uint32_t m_expectedFragmentCount = 10;
    uint32_t m_bfsLevel = 0;
    uint32_t m_groundNodeCount = 0;  // For identifying UAV: srcNodeId >= m_groundNodeCount means UAV
    
    // Confidence tracking
    ConfidenceModel m_confidenceModel{0, 10};
    FragmentCollection m_allFragments;  // UAV: all K frags; Ground: fills up
    
    // Thresholds
    double m_cooperationThreshold = 0.30;   // τ_coop
    double m_alertThreshold = 0.75;         // τ_alert
    
    // Timers and events
    EventId m_broadcastEvent;
    EventId m_cooperationEvent;
    uint32_t m_nextFragmentIndex = 0;
    bool m_coopScheduled = false;
    bool m_detected = false;
    
    // Fragment processing
    void ProcessFragment(const Fragment& frag, bool fromUav);

    // Statistics and callbacks
    Ptr<StatisticsCollector> m_stats;
    DetectionCallback m_detectionCb;
    PacketDroppedCallback m_droppedCb;

    // Network device for transmission
    Ptr<NetDevice> m_device;
};

}  // namespace uav
}  // namespace wsn
}  // namespace ns3

#endif  // WSN_UAV_FRAGMENT_DISSEMINATION_APP_H
