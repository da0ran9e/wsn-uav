#ifndef UAV_SAR_DATA_UAV_APP_H
#define UAV_SAR_DATA_UAV_APP_H

// DATA-team UAV: climbs and loiters at a staging point (does not listen to the
// ground directly). On a relayed SUMMON (A2A) it claims the event over the radio
// (a broadcast CLAIM with suppression, so exactly one responds — no shared-memory
// token), diverts to the victim region, delivers the FULL dataset, and on CONFIRM
// flies back to the BS and sends a small report.

#include "flight-controller.h"
#include "../common/target-profile.h"

#include "ns3/application.h"
#include "ns3/net-device.h"
#include "ns3/event-id.h"
#include "ns3/vector.h"
#include "ns3/address.h"
#include "ns3/ptr.h"
#include "ns3/random-variable-stream.h"

#include <cstdint>
#include <memory>
#include <vector>

namespace ns3::uavsar {

class SarMetrics;

class SarDataUavApp : public ns3::Application {
public:
    static ns3::TypeId GetTypeId();
    SarDataUavApp();
    ~SarDataUavApp() override;

    void SetNodeId(uint32_t id) { m_nodeId = id; }
    void SetDevice(ns3::Ptr<ns3::NetDevice> d) { m_dev = d; }
    void SetMetrics(SarMetrics* m) { m_metrics = m; }
    void SetFullDataset(const std::vector<Fragment>& f) { m_full = f; }
    void SetCruise(double alt, double speed) { m_alt = alt; m_speed = speed; }
    void SetLoiter(ns3::Vector c) { m_loiter = c; }
    void SetBs(ns3::Vector pos, ns3::Address addr) { m_bsPos = pos; m_bsAddr = addr; }

    // Baseline behaviour: instead of loiter+summon, sweep the grid and dwell-dump
    // the full dataset at every visited cell (no ground cooperation).
    enum class Mode { SUMMONED, SWEEP_DUMP };
    void SetMode(Mode m) { m_mode = m; }
    void SetSensorPositions(const std::vector<ns3::Vector>& p) { m_sensors = p; }

    bool OnReceive(ns3::Ptr<ns3::NetDevice> dev, ns3::Ptr<const ns3::Packet> pkt,
                   uint16_t proto, const ns3::Address& from);

private:
    void StartApplication() override;
    void StopApplication() override;
    void TakeOff();
    void ControlTick();
    void TrajTick();
    void SendFullChunk(size_t fi, uint16_t seq);
    void SendReport();
    void ClaimDivert();                 // won the radio CLAIM -> divert+deliver
    void SendClaim(uint8_t role);       // broadcast a role claim (mutual exclusion)
    void TryClaimDivert(double x, double y);

    enum class State { IDLE, CLIMB, GOTO_CENTER, LOITER, DIVERT, DELIVER, SWEEP, RETURN, DONE };

    uint32_t m_nodeId = 0;
    ns3::Ptr<ns3::NetDevice> m_dev;
    SarMetrics* m_metrics = nullptr;
    Mode m_mode = Mode::SUMMONED;
    std::vector<Fragment> m_full;
    std::vector<ns3::Vector> m_sensors;   // for SWEEP_DUMP GMC
    std::vector<ns3::Vector> m_targets;
    size_t m_ti = 0;
    double m_radius = 50.0;
    double m_alt = 20.0, m_speed = 15.0;
    ns3::Vector m_loiter{0, 0, 0};
    ns3::Vector m_divert{0, 0, 0};
    ns3::Vector m_bsPos{0, 0, 0};
    ns3::Address m_bsAddr;
    ns3::Ptr<ns3::UniformRandomVariable> m_rng;
    bool m_claimed = false;
    bool m_yieldedDivert = false;   // heard another UAV's CLAIM first -> stand down
    double m_pendX = 0, m_pendY = 0;
    ns3::EventId m_claimEvent;
    bool m_pendingDivert = false;   // claimed before airborne; divert after climb
    bool m_confirmed = false;
    double m_divertStartDist = 0;
    double m_dwellUntil = 0;        // SWEEP_DUMP: cycle chunks until this time
    uint32_t m_reportsSent = 0;     // REPORT retransmissions (bounded)
    uint32_t m_handoffsSent = 0;    // HANDOFF broadcasts to the FAST team
    double m_deliverUntil = 0;      // keep delivering (coverage dwell) until this
    void SendHandoff();
    void BeginReturn();             // stop delivering, head home + hand off
    uint32_t m_fullTxCount = 0;     // for decimated viz markers

    State m_state = State::IDLE;
    ns3::EventId m_ctrl, m_traj;
    FlightController m_fc;
};

}  // namespace ns3::uavsar

#endif  // UAV_SAR_DATA_UAV_APP_H
