/*
 * cell-spread.cc -- measure T_hop(R, n_c) inside ONE cluster cell.
 *
 * Task items B4 and B5. Deliberately NOT a whole-network simulation: there is no
 * UAV, no trajectory and no air-to-ground link. Nodes in a corridor are seeded
 * with fragments at t = 0, exactly as if a UAV had just flown past, and the
 * epidemic spread among ground nodes is then run to completion over a real
 * LR-WPAN PHY/MAC with real CSMA, collisions and hidden terminals.
 *
 * Modes:
 *   spread     (default) epidemic relaying; reports T_spread and the completion
 *              fraction crossing times
 *   seedonly   B5: relaying disabled, seeding only. Tests the claim that no node
 *              collects all k from the air alone.
 *   calibrate  PER vs distance for a single pair, used once to set TX power so
 *              that the measured r_tx is ~50 m. Reported, not assumed.
 *
 * LR-WPAN traps observed (task section 2):
 *  - ONE LrWpanHelper for all nodes, and it is heap-allocated and never freed,
 *    because ~LrWpanHelper calls m_channel->Dispose() which empties the
 *    channel's PHY list; after that TX still fires but nothing is ever received.
 *  - application payload <= 100 B, never the 127 B PSDU
 *  - >= 200 ms between back-to-back Send() calls on one device
 *  - every Send() return value is checked; a silent FAIL looks like nothing
 *  - RX callbacks set once per device, before Simulator::Run()
 */
#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"
#include "ns3/lr-wpan-module.h"
#include "ns3/propagation-module.h"
#include "ns3/spectrum-module.h"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <fstream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <vector>

using namespace ns3;
using namespace ns3::lrwpan;

NS_LOG_COMPONENT_DEFINE("CellSpread");

// ---------------------------------------------------------------- parameters
namespace cfg {
double R_m = 150.0;           // hex cell circumradius
double spacing_m = 20.0;      // node lattice spacing -> varies n_c
double r_tx_m = 50.0;         // intended intra-cluster range (calibrated)
double r_bc_m = 50.0;         // corridor half-width of the UAV footprint
uint32_t k = 8;               // fragments in the signature set
bool trickle = true;          // Trickle-style suppression
double advInterval_s = 2.0;   // Trickle Imin / plain advertisement period
double advIntervalMax_s = 32.0;
uint32_t trickleK = 2;        // suppression threshold
double sendSpacing_s = 0.2;   // >= 200 ms, hard MAC requirement
uint32_t fragBytes = 64;      // <= 100 B app payload ceiling
double suppressWindow_s = 1.0; // don't re-push a fragment heard this recently
double txPower_dBm = -2.0;    // calibrated so r_tx ~ 50 m
double stopTime_s = 900.0;
uint32_t seed = 1;
std::string mode = "spread";
std::string outCsv = "";
std::string curveCsv = "";
std::string runId = "";
} // namespace cfg

// ---------------------------------------------------------------- node state
struct NodeState
{
    std::vector<bool> have;
    uint32_t nHave = 0;
    Time completedAt = Time::Max();
    // Trickle
    Time interval;
    uint32_t consistent = 0;
    // The radio is ONE serial resource capped at 1/sendSpacing packets per
    // second. Fragment pushes and advertisements compete for it, and pushes win:
    // an earlier revision used a single FIFO and the advertisement stream starved
    // the pushes, which made a SHORTER advertisement interval produce a SLOWER
    // spread (8.0 s at 0.25 s vs 1.9 s at 2.0 s) -- backwards, and a bug rather
    // than a finding.
    std::set<uint32_t> pendingFrags;
    bool pendingAdv = false;
    bool txScheduled = false;
    Time cooldownUntil = Seconds(0.0);
    // last time each fragment was heard on air, for duplicate-push suppression
    std::map<uint32_t, Time> heardFrag;
};

static std::vector<NodeState> g_state;
static NodeContainer g_nodes;
static NetDeviceContainer g_devs;
static uint64_t g_pktAdv = 0, g_pktFrag = 0, g_sendFail = 0, g_bytes = 0;
static uint32_t g_nNodes = 0;
static std::vector<std::pair<double, double>> g_curve; // (t, fraction complete)
static uint32_t g_lastComplete = 0;
static uint64_t g_rxAdv = 0, g_rxFrag = 0;
// Contention evidence, straight off the LR-WPAN MAC/PHY trace sources. If these
// are all zero the channel is not contending and the result is a bug, not a
// finding (task section 7).
static uint64_t g_macTxDrop = 0, g_macRxDrop = 0, g_phyRxDrop = 0, g_phyTxDrop = 0;
static uint64_t g_macTx = 0, g_macTxOk = 0;
static uint32_t g_tracesConnected = 0;

static void CbMacTxDrop(Ptr<const Packet>) { ++g_macTxDrop; }
static void CbMacRxDrop(Ptr<const Packet>) { ++g_macRxDrop; }
static void CbPhyRxDrop(Ptr<const Packet>) { ++g_phyRxDrop; }
static void CbPhyTxDrop(Ptr<const Packet>) { ++g_phyTxDrop; }
static void CbMacTx(Ptr<const Packet>) { ++g_macTx; }
static void CbMacTxOk(Ptr<const Packet>) { ++g_macTxOk; }
// calibrate mode
static uint32_t g_calibRx = 0;

static const uint8_t TYPE_ADV = 1;
static const uint8_t TYPE_FRAG = 2;

static uint32_t CountComplete()
{
    uint32_t c = 0;
    for (auto& s : g_state)
        if (s.nHave == cfg::k)
            ++c;
    return c;
}

static void RecordCurve()
{
    uint32_t c = CountComplete();
    if (c != g_lastComplete || g_curve.empty())
    {
        g_curve.emplace_back(Simulator::Now().GetSeconds(),
                             static_cast<double>(c) / g_nNodes);
        g_lastComplete = c;
    }
    if (c < g_nNodes)
    {
        Simulator::Schedule(Seconds(0.25), &RecordCurve);
    }
    else if (cfg::mode == "spread")
    {
        // Every node holds all k: the measurement is finished. Without this the
        // run keeps advertising for the rest of stopTime, which costs most of the
        // wall time and changes nothing. Censored runs still use the full cap.
        Simulator::Stop(MilliSeconds(1));
    }
}

// Broadcast. Every Send() return value is checked: a silent FAIL looks exactly
// like nothing happening.
static void DoSend(uint32_t id, Ptr<Packet> pkt, uint8_t type)
{
    Ptr<NetDevice> dev = g_devs.Get(id);
    bool ok = dev->Send(pkt, Mac16Address("ff:ff"), 0);
    if (!ok)
    {
        ++g_sendFail;
        return;
    }
    if (type == TYPE_ADV)
        ++g_pktAdv;
    else
        ++g_pktFrag;
    g_bytes += pkt->GetSize();
}

static void TxTick(uint32_t id);

// Wake the node's transmitter if it has something to send and its >= 200 ms
// cooldown has expired.
static void MaybeTx(uint32_t id)
{
    NodeState& st = g_state[id];
    if (st.txScheduled)
        return;
    if (st.pendingFrags.empty() && !st.pendingAdv)
        return;
    Time now = Simulator::Now();
    Time at = std::max(now, st.cooldownUntil);
    st.txScheduled = true;
    Simulator::Schedule(at - now, &TxTick, id);
}

static Ptr<Packet> MakeAdv(uint32_t id)
{
    // [type:1][id:2][bitmap: ceil(k/8)]  -- compact binary, no strings
    uint32_t nb = (cfg::k + 7) / 8;
    std::vector<uint8_t> buf(3 + nb, 0);
    buf[0] = TYPE_ADV;
    buf[1] = id & 0xff;
    buf[2] = (id >> 8) & 0xff;
    for (uint32_t f = 0; f < cfg::k; ++f)
        if (g_state[id].have[f])
            buf[3 + f / 8] |= (1u << (f % 8));
    return Create<Packet>(buf.data(), buf.size());
}

static Ptr<Packet> MakeFrag(uint32_t id, uint32_t f)
{
    std::vector<uint8_t> buf(cfg::fragBytes, 0);
    buf[0] = TYPE_FRAG;
    buf[1] = id & 0xff;
    buf[2] = (id >> 8) & 0xff;
    buf[3] = f & 0xff;
    return Create<Packet>(buf.data(), buf.size());
}

static Ptr<UniformRandomVariable> g_rand;

// Fragment pushes take priority over advertisements; one packet per cooldown.
static void TxTick(uint32_t id)
{
    NodeState& st = g_state[id];
    st.txScheduled = false;
    Time now = Simulator::Now();

    // drop queued pushes for fragments somebody else has since broadcast
    for (auto it = st.pendingFrags.begin(); it != st.pendingFrags.end();)
    {
        auto h = st.heardFrag.find(*it);
        if (h != st.heardFrag.end() && now - h->second < Seconds(cfg::suppressWindow_s))
            it = st.pendingFrags.erase(it);
        else
            ++it;
    }

    if (!st.pendingFrags.empty())
    {
        uint32_t f = *st.pendingFrags.begin();
        st.pendingFrags.erase(st.pendingFrags.begin());
        DoSend(id, MakeFrag(id, f), TYPE_FRAG);
        st.heardFrag[f] = now;
    }
    else if (st.pendingAdv)
    {
        st.pendingAdv = false;
        DoSend(id, MakeAdv(id), TYPE_ADV);
    }
    else
    {
        return;
    }
    st.cooldownUntil = Simulator::Now() + Seconds(cfg::sendSpacing_s);
    MaybeTx(id);
}

static void Advertise(uint32_t id)
{
    NodeState& st = g_state[id];
    bool suppress = cfg::trickle && (st.consistent >= cfg::trickleK);
    if (!suppress)
    {
        st.pendingAdv = true;
        MaybeTx(id);
    }
    if (cfg::trickle)
    {
        st.consistent = 0;
        st.interval = std::min(st.interval * 2, Seconds(cfg::advIntervalMax_s));
    }
    Simulator::Schedule(st.interval * g_rand->GetValue(0.5, 1.0), &Advertise, id);
}

static bool OnRx(Ptr<NetDevice> dev, Ptr<const Packet> pkt, uint16_t, const Address&)
{
    uint32_t me = dev->GetNode()->GetId();
    uint32_t n = pkt->GetSize();
    std::vector<uint8_t> buf(n);
    pkt->CopyData(buf.data(), n);
    if (n < 4)
        return true;

    if (cfg::mode == "calibrate")
    {
        ++g_calibRx;
        return true;
    }

    NodeState& st = g_state[me];
    if (buf[0] == TYPE_ADV)
    {
        ++g_rxAdv;
        uint32_t nb = (cfg::k + 7) / 8;
        if (n < 3 + nb)
            return true;
        // fragments the advertiser lacks that I hold
        std::vector<uint32_t> canGive;
        bool theyHaveSomethingNew = false;
        for (uint32_t f = 0; f < cfg::k; ++f)
        {
            bool they = (buf[3 + f / 8] >> (f % 8)) & 1u;
            if (st.have[f] && !they)
                canGive.push_back(f);
            if (they && !st.have[f])
                theyHaveSomethingNew = true;
        }
        if (cfg::trickle)
        {
            if (canGive.empty() && !theyHaveSomethingNew)
            {
                ++st.consistent; // identical state heard -> suppress
            }
            else
            {
                // new information: reset the Trickle interval
                st.consistent = 0;
                st.interval = Seconds(cfg::advInterval_s);
            }
        }
        if (!canGive.empty() && cfg::mode == "spread")
        {
            uint32_t pick = canGive[g_rand->GetInteger(0, canGive.size() - 1)];
            auto h = st.heardFrag.find(pick);
            bool recentlyOnAir = (h != st.heardFrag.end()) &&
                (Simulator::Now() - h->second < Seconds(cfg::suppressWindow_s));
            if (!recentlyOnAir)
            {
                st.pendingFrags.insert(pick);
                MaybeTx(me);
            }
        }
    }
    else if (buf[0] == TYPE_FRAG)
    {
        ++g_rxFrag;
        uint32_t f = buf[3];
        if (f < cfg::k)
        {
            // somebody else served this fragment: cancel our own queued push
            st.heardFrag[f] = Simulator::Now();
            st.pendingFrags.erase(f);
        }
        if (f < cfg::k && !st.have[f])
        {
            st.have[f] = true;
            ++st.nHave;
            if (cfg::trickle)
            {
                st.consistent = 0;
                st.interval = Seconds(cfg::advInterval_s);
            }
            if (st.nHave == cfg::k)
                st.completedAt = Simulator::Now();
        }
    }
    return true;
}

// ------------------------------------------------------------------ geometry
static bool InsideHex(double x, double y, double R)
{
    // regular hexagon, circumradius R, one vertex at angle 0
    double ax = std::fabs(x), ay = std::fabs(y);
    if (ax > R || ay > R * std::sqrt(3.0) / 2.0)
        return false;
    return (R * std::sqrt(3.0) / 2.0 * ax + 0.5 * R * ay) <= R * R * std::sqrt(3.0) / 2.0;
}

int main(int argc, char* argv[])
{
    CommandLine cmd(__FILE__);
    cmd.AddValue("R", "cell circumradius (m)", cfg::R_m);
    cmd.AddValue("spacing", "node lattice spacing (m)", cfg::spacing_m);
    cmd.AddValue("rtx", "intended intra-cluster range (m)", cfg::r_tx_m);
    cmd.AddValue("rbc", "corridor half width (m)", cfg::r_bc_m);
    cmd.AddValue("k", "number of fragments", cfg::k);
    cmd.AddValue("trickle", "Trickle suppression on/off", cfg::trickle);
    cmd.AddValue("advInterval", "advertisement interval / Trickle Imin (s)", cfg::advInterval_s);
    cmd.AddValue("advIntervalMax", "Trickle Imax (s)", cfg::advIntervalMax_s);
    cmd.AddValue("trickleK", "Trickle suppression threshold", cfg::trickleK);
    cmd.AddValue("fragBytes", "fragment payload bytes (<=100)", cfg::fragBytes);
    cmd.AddValue("suppressWindow", "duplicate-push suppression window (s)",
                 cfg::suppressWindow_s);
    cmd.AddValue("txPower", "TX power (dBm)", cfg::txPower_dBm);
    cmd.AddValue("stopTime", "simulation cap (s)", cfg::stopTime_s);
    cmd.AddValue("seed", "RNG run number", cfg::seed);
    cmd.AddValue("mode", "spread | seedonly | calibrate", cfg::mode);
    cmd.AddValue("outCsv", "append one summary row here", cfg::outCsv);
    cmd.AddValue("curveCsv", "write the completion curve here", cfg::curveCsv);
    cmd.AddValue("runId", "identifier for the row", cfg::runId);
    cmd.Parse(argc, argv);

    NS_ABORT_MSG_IF(cfg::fragBytes > 100,
                    "app payload ceiling is 100 B, not the 127 B PSDU");
    NS_ABORT_MSG_IF(cfg::sendSpacing_s < 0.2, "Send() spacing must be >= 200 ms");

    RngSeedManager::SetSeed(12345);
    RngSeedManager::SetRun(cfg::seed);
    g_rand = CreateObject<UniformRandomVariable>();

    // ------------------------------------------------------------- positions
    std::vector<Vector> pos;
    if (cfg::mode == "calibrate")
    {
        // two nodes at a controlled separation; r_tx swept by the caller
        pos.push_back(Vector(0, 0, 0));
        pos.push_back(Vector(cfg::r_tx_m, 0, 0));
    }
    else
    {
        double s = cfg::spacing_m;
        int n = static_cast<int>(std::ceil(cfg::R_m / s)) + 2;
        for (int i = -n; i <= n; ++i)
            for (int j = -n; j <= n; ++j)
            {
                double x = i * s, y = j * s;
                if (InsideHex(x, y, cfg::R_m))
                    pos.push_back(Vector(x, y, 0));
            }
    }
    g_nNodes = pos.size();
    NS_ABORT_MSG_IF(g_nNodes < 2, "need at least 2 nodes");

    g_nodes.Create(g_nNodes);
    Ptr<ListPositionAllocator> alloc = CreateObject<ListPositionAllocator>();
    for (auto& p : pos)
        alloc->Add(p);
    MobilityHelper mob;
    mob.SetPositionAllocator(alloc);
    mob.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    mob.Install(g_nodes);

    // --------------------------------------------------------------- radio
    // ONE helper, heap-allocated and intentionally never deleted: its destructor
    // disposes the channel and silently kills all reception.
    static LrWpanHelper* lr = new LrWpanHelper(false);
    Ptr<SingleModelSpectrumChannel> ch = CreateObject<SingleModelSpectrumChannel>();
    Ptr<LogDistancePropagationLossModel> loss =
        CreateObject<LogDistancePropagationLossModel>();
    loss->SetAttribute("Exponent", DoubleValue(3.0));
    ch->AddPropagationLossModel(loss);
    Ptr<ConstantSpeedPropagationDelayModel> delay =
        CreateObject<ConstantSpeedPropagationDelayModel>();
    ch->SetPropagationDelayModel(delay);
    lr->SetChannel(ch);

    g_devs = lr->Install(g_nodes);
    lr->SetExtendedAddresses(g_devs);
    for (uint32_t i = 0; i < g_devs.GetN(); ++i)
    {
        Ptr<LrWpanNetDevice> d = DynamicCast<LrWpanNetDevice>(g_devs.Get(i));
        d->GetMac()->SetPanId(7);
        d->GetMac()->SetShortAddress(Mac16Address::Allocate());
        LrWpanSpectrumValueHelper svh;
        Ptr<SpectrumValue> psd = svh.CreateTxPowerSpectralDensity(cfg::txPower_dBm, 11);
        d->GetPhy()->SetTxPowerSpectralDensity(psd);
        // RX callback: once per device, before Simulator::Run()
        d->SetReceiveCallback(MakeCallback(&OnRx));
    }
    // Contention instrumentation. FailSafe so a renamed source degrades to
    // "not connected" (reported) rather than aborting the run.
    struct TraceHook { const char* path; void (*cb)(Ptr<const Packet>); };
    const TraceHook hooks[] = {
        {"/NodeList/*/DeviceList/*/$ns3::lrwpan::LrWpanNetDevice/Mac/MacTxDrop", &CbMacTxDrop},
        {"/NodeList/*/DeviceList/*/$ns3::lrwpan::LrWpanNetDevice/Mac/MacRxDrop", &CbMacRxDrop},
        {"/NodeList/*/DeviceList/*/$ns3::lrwpan::LrWpanNetDevice/Mac/MacTx", &CbMacTx},
        {"/NodeList/*/DeviceList/*/$ns3::lrwpan::LrWpanNetDevice/Mac/MacTxOk", &CbMacTxOk},
        {"/NodeList/*/DeviceList/*/$ns3::lrwpan::LrWpanNetDevice/Phy/PhyRxDrop", &CbPhyRxDrop},
        {"/NodeList/*/DeviceList/*/$ns3::lrwpan::LrWpanNetDevice/Phy/PhyTxDrop", &CbPhyTxDrop},
    };
    for (const auto& h : hooks)
        if (Config::ConnectWithoutContextFailSafe(h.path, MakeCallback(h.cb)))
            ++g_tracesConnected;

    // the trap check from the task: if this is 0 the helper died
    uint32_t nDevOnChannel = g_devs.Get(0)->GetChannel()->GetNDevices();
    NS_ABORT_MSG_IF(nDevOnChannel == 0,
                    "channel has no devices: the LrWpanHelper was destroyed");

    // --------------------------------------------------------------- seeding
    g_state.resize(g_nNodes);
    for (auto& st : g_state)
    {
        st.have.assign(cfg::k, false);
        st.interval = Seconds(cfg::advInterval_s);
    }

    uint32_t nSeeded = 0;
    if (cfg::mode != "calibrate")
    {
        // a straight corridor through the cell centre at a random orientation
        double th = g_rand->GetValue(0.0, M_PI);
        double nx = -std::sin(th), ny = std::cos(th); // unit normal
        std::vector<uint32_t> corridor;
        for (uint32_t i = 0; i < g_nNodes; ++i)
        {
            double d = std::fabs(pos[i].x * nx + pos[i].y * ny);
            if (d <= cfg::r_bc_m)
                corridor.push_back(i);
        }
        NS_ABORT_MSG_IF(corridor.empty(), "empty corridor");
        // each corridor node gets a random subset; then repair so the corridor
        // collectively holds all k
        for (uint32_t i : corridor)
        {
            for (uint32_t f = 0; f < cfg::k; ++f)
                if (g_rand->GetValue(0.0, 1.0) < 0.5)
                {
                    g_state[i].have[f] = true;
                    ++g_state[i].nHave;
                }
        }
        for (uint32_t f = 0; f < cfg::k; ++f)
        {
            bool any = false;
            for (uint32_t i : corridor)
                any = any || g_state[i].have[f];
            if (!any)
            {
                uint32_t i = corridor[g_rand->GetInteger(0, corridor.size() - 1)];
                g_state[i].have[f] = true;
                ++g_state[i].nHave;
            }
        }
        for (uint32_t i : corridor)
            if (g_state[i].nHave > 0)
                ++nSeeded;
        for (uint32_t i = 0; i < g_nNodes; ++i)
            if (g_state[i].nHave == cfg::k)
                g_state[i].completedAt = Seconds(0.0);
    }

    // ------------------------------------------------------------ scheduling
    if (cfg::mode == "calibrate")
    {
        // 200 back-to-back broadcasts from node 0, >= 200 ms apart
        for (uint32_t i = 0; i < 200; ++i)
        {
            std::vector<uint8_t> b(cfg::fragBytes, 0);
            b[0] = TYPE_FRAG;
            Simulator::Schedule(Seconds(1.0 + 0.25 * i), &DoSend, 0u,
                                Create<Packet>(b.data(), b.size()), TYPE_FRAG);
        }
        Simulator::Stop(Seconds(1.0 + 0.25 * 205));
    }
    else
    {
        for (uint32_t i = 0; i < g_nNodes; ++i)
            Simulator::Schedule(Seconds(g_rand->GetValue(0.0, cfg::advInterval_s)),
                                &Advertise, i);
        Simulator::Schedule(Seconds(0.0), &RecordCurve);
        Simulator::Stop(Seconds(cfg::stopTime_s));
    }

    Simulator::Run();

    // ----------------------------------------------------------------- report
    uint32_t nComplete = CountComplete();
    double frac = static_cast<double>(nComplete) / g_nNodes;
    // crossing times so a partial-completion criterion can be applied later
    std::vector<double> times;
    for (auto& st : g_state)
        if (st.completedAt != Time::Max())
            times.push_back(st.completedAt.GetSeconds());
    std::sort(times.begin(), times.end());
    auto quantileTime = [&](double q) -> double {
        uint32_t need = static_cast<uint32_t>(std::ceil(q * g_nNodes));
        if (need == 0)
            need = 1;
        if (times.size() < need)
            return -1.0; // censored: never reached within stopTime
        return times[need - 1];
    };
    double t50 = quantileTime(0.50), t90 = quantileTime(0.90),
           t95 = quantileTime(0.95), t99 = quantileTime(0.99),
           t100 = quantileTime(1.0);

    if (cfg::mode == "calibrate")
    {
        std::printf("CALIB d=%.1f sent=%llu rx=%u per=%.4f\n", cfg::r_tx_m,
                    (unsigned long long)g_pktFrag, g_calibRx,
                    g_pktFrag ? 1.0 - double(g_calibRx) / double(g_pktFrag) : 1.0);
    }

    if (!cfg::outCsv.empty())
    {
        bool newFile = !std::ifstream(cfg::outCsv).good();
        std::ofstream f(cfg::outCsv, std::ios::app);
        if (newFile)
            f << "run_id,mode,R_m,spacing_m,k,trickle,r_tx_m,r_bc_m,seed,"
                 "n_nodes,n_seeded,n_complete,frac_complete,censored,"
                 "T_spread_s,t50_s,t90_s,t95_s,t99_s,"
                 "pkt_adv,pkt_frag,pkt_total,send_fail,bytes_total,"
                 "rx_adv,rx_frag,mac_tx,mac_tx_ok,mac_tx_drop,mac_rx_drop,"
                 "phy_rx_drop,phy_tx_drop,traces_connected,"
                 "adv_interval_s,suppress_window_s,stop_time_s,tx_power_dBm\n";
        f << cfg::runId << ',' << cfg::mode << ',' << cfg::R_m << ','
          << cfg::spacing_m << ',' << cfg::k << ',' << (cfg::trickle ? 1 : 0) << ','
          << cfg::r_tx_m << ',' << cfg::r_bc_m << ',' << cfg::seed << ','
          << g_nNodes << ',' << nSeeded << ',' << nComplete << ',' << frac << ','
          << (t100 < 0 ? 1 : 0) << ',' << t100 << ',' << t50 << ',' << t90 << ','
          << t95 << ',' << t99 << ',' << g_pktAdv << ',' << g_pktFrag << ','
          << (g_pktAdv + g_pktFrag) << ',' << g_sendFail << ',' << g_bytes << ','
          << g_rxAdv << ',' << g_rxFrag << ',' << g_macTx << ',' << g_macTxOk << ','
          << g_macTxDrop << ',' << g_macRxDrop << ',' << g_phyRxDrop << ','
          << g_phyTxDrop << ',' << g_tracesConnected << ',' << cfg::advInterval_s
          << ',' << cfg::suppressWindow_s << ',' << cfg::stopTime_s << ','
          << cfg::txPower_dBm << '\n';
    }
    if (!cfg::curveCsv.empty())
    {
        bool newFile = !std::ifstream(cfg::curveCsv).good();
        std::ofstream f(cfg::curveCsv, std::ios::app);
        if (newFile)
            f << "run_id,t_s,frac_complete\n";
        for (auto& p : g_curve)
            f << cfg::runId << ',' << p.first << ',' << p.second << '\n';
    }
    std::printf("RESULT n=%u seeded=%u complete=%u frac=%.4f T_spread=%.3f "
                "pkts=%llu fail=%llu macTxDrop=%llu phyRxDrop=%llu traces=%u\n",
                g_nNodes, nSeeded, nComplete, frac, t100,
                (unsigned long long)(g_pktAdv + g_pktFrag),
                (unsigned long long)g_sendFail,
                (unsigned long long)g_macTxDrop,
                (unsigned long long)g_phyRxDrop, g_tracesConnected);
    Simulator::Destroy();
    return 0;
}
