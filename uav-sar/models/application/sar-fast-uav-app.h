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
#include "ns3/random-variable-stream.h"

#include <cstdint>
#include <memory>
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
    void SetBs(ns3::Vector pos, ns3::Address addr) { m_bsPos = pos; m_bsAddr = addr; }
    // audit F2: symmetric completion — every UAV flies home and reports, so the
    // mission clock is not stopped by a single courier while peers stay airborne.
    void SetAllHome(bool v) { m_allHome = v; }
    // audit W4: home on the strongest DIRECT echo instead of a ground SUMMON.
    void SetEchoRelay(bool v) { m_echoRelay = v; }

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

    enum class State { IDLE, CLIMB, CRUISE, RELAY_HOLD, RETURN_BS, DONE };

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
    double m_relayUntilS = 0;   // audit A10: bounded post-sweep relay hold
    // audit W4: closed-loop baseline -- the best DIRECT echo this UAV heard.
    bool m_echoRelay = false;
    double m_bestEchoEv = 0, m_bestEchoX = 0, m_bestEchoY = 0;
    void RelayBestEcho();
    ns3::EventId m_echoSettle;
    bool m_hasFix = false;      // audit B3: victim fix to carry home in the REPORT
    double m_fixX = 0, m_fixY = 0;
    double m_alt = 20.0, m_speed = 25.0, m_radius = 50.0;
    State m_state = State::IDLE;
    ns3::Vector m_bsPos{0, 0, 0};
    ns3::Address m_bsAddr;
    ns3::Ptr<ns3::UniformRandomVariable> m_rng;
    bool m_courier = false;
    bool m_yieldedCourier = false;
    bool m_allHome = true;
    ns3::EventId m_courierEvent;
    uint32_t m_reportsSent = 0;
    void SendReport();
    void ClaimCourier();          // won the radio CLAIM -> race the report home
    void SendClaim(uint8_t role); // broadcast a role claim (mutual exclusion)
    ns3::EventId m_ctrl, m_dis, m_traj;
    FlightController m_fc;
};

}  // namespace ns3::uavsar

#endif  // UAV_SAR_FAST_UAV_APP_H
