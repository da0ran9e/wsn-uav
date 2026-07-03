#ifndef UAV_SAR_FAST_UAV_APP_H
#define UAV_SAR_FAST_UAV_APP_H

// FAST-team UAV: sweeps the area (GMC coverage), broadcasts small identity cues
// (L0/L1) to the ground, listens for the region SUMMON and relays it to the
// DATA team over A2A (DATA does not listen directly).

#include "flight-controller.h"
#include "../common/target-profile.h"

#include "ns3/application.h"
#include "ns3/net-device.h"
#include "ns3/event-id.h"
#include "ns3/vector.h"
#include "ns3/ptr.h"
#include "ns3/address.h"

#include <cstdint>
#include <vector>

namespace ns3::uavsar {

class SarMetrics;

class SarFastUavApp : public ns3::Application {
public:
    static ns3::TypeId GetTypeId();
    SarFastUavApp();
    ~SarFastUavApp() override;

    void SetNodeId(uint32_t id) { m_nodeId = id; }
    void SetDevice(ns3::Ptr<ns3::NetDevice> d) { m_dev = d; }
    void SetMetrics(SarMetrics* m) { m_metrics = m; }
    void SetSensorPositions(const std::vector<ns3::Vector>& p) { m_sensors = p; }
    void SetCues(const std::vector<Fragment>& c) { m_cues = c; }
    void SetCruise(double alt, double speed) { m_alt = alt; m_speed = speed; }

    bool OnReceive(ns3::Ptr<ns3::NetDevice> dev, ns3::Ptr<const ns3::Packet> pkt,
                   uint16_t proto, const ns3::Address& from);

private:
    void StartApplication() override;
    void StopApplication() override;
    void TakeOff();
    void BuildMission();
    void ControlTick();
    void DisseminateTick();
    void TrajTick();

    enum class State { IDLE, CLIMB, CRUISE, DONE };

    uint32_t m_nodeId = 0;
    ns3::Ptr<ns3::NetDevice> m_dev;
    SarMetrics* m_metrics = nullptr;
    std::vector<ns3::Vector> m_sensors;
    std::vector<Fragment> m_cues;
    std::vector<ns3::Vector> m_targets;
    size_t m_ti = 0;
    size_t m_cueIdx = 0;      // fragment index in m_cues
    uint16_t m_cueSeq = 0;    // chunk seq within the current cue fragment
    uint32_t m_cueTxCount = 0;  // for decimated viz markers
    bool m_summonSeen = false;  // once a summon is relayed, stop spreading cues
    double m_alt = 20.0, m_speed = 25.0, m_radius = 50.0;
    State m_state = State::IDLE;
    ns3::EventId m_ctrl, m_dis, m_traj;
    FlightController m_fc;
};

}  // namespace ns3::uavsar

#endif  // UAV_SAR_FAST_UAV_APP_H
