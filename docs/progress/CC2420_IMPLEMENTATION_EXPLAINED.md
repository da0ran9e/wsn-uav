---
CC2420 Implementation in wsn-uav: Detailed Explanation
Date: 2026-05-06
---

# How CC2420 Radio is Implemented in wsn-uav

This document explains how the CC2420 radio model from the `wsn` module is integrated into `wsn-uav`.

## Overview: Two-Module Architecture

```
wsn (separate repo)
  ├── src/wsn/helper/cc2420-helper.h/.cc
  ├── src/wsn/model/radio/cc2420/
  │   ├── cc2420-phy.h/.cc          ← Physical layer (TX/RX timing)
  │   ├── cc2420-mac.h/.cc          ← MAC layer (CSMA-CA)
  │   ├── cc2420-net-device.h/.cc   ← NS-3 device interface
  │   └── cc2420-energy-model.h/.cc ← Power consumption
  └── ...

wsn-uav (separate repo)
  ├── helper/wsn-network-helper.h/.cc
  ├── models/application/fragment-dissemination-app.h/.cc
  └── ...
```

**Key Point:** wsn-uav **does NOT modify or fork CC2420**. It only uses the helper class to instantiate devices.

---

## Step-by-Step: How CC2420 is Used in wsn-uav

### Step 1: Include the Helper

In `wsn-network-helper.cc`:

```cpp
#include "ns3/cc2420-helper.h"  // From wsn module
```

This includes the Cc2420Helper class that provides high-level API for:
- Creating spectrum channels
- Installing CC2420 devices on nodes
- Configuring PHY/MAC attributes

### Step 2: Create CC2420 Helper Instance

In `WsnNetworkHelper::InstallRadios()`:

```cpp
void WsnNetworkHelper::InstallRadios() {
    wsn::Cc2420Helper cc2420;  // Create helper instance
    // ...
}
```

This creates a local instance of Cc2420Helper. Each instance has:
- A `m_channel` member to store the spectrum channel
- `m_macFactory`, `m_phyFactory` for configuring components
- Methods to create and install devices

### Step 3: Create Spectrum Channel

```cpp
auto channel = cc2420.CreateChannel();
```

This calls `Cc2420Helper::CreateChannel()`:

```cpp
// From wsn/helper/cc2420-helper.cc (lines 50-67)
Ptr<SingleModelSpectrumChannel> Cc2420Helper::CreateChannel() const
{
    Ptr<SingleModelSpectrumChannel> channel = 
        CreateObject<SingleModelSpectrumChannel>();

    // Add log-distance propagation loss model
    Ptr<LogDistancePropagationLossModel> loss = 
        CreateObject<LogDistancePropagationLossModel>();
    loss->SetAttribute("Exponent", DoubleValue(3.0));              
    loss->SetAttribute("ReferenceDistance", DoubleValue(1.0));     
    loss->SetAttribute("ReferenceLoss", DoubleValue(46.6776));     // FSPL @ 2.4GHz
    channel->AddPropagationLossModel(loss);

    // Add constant delay model
    Ptr<ConstantSpeedPropagationDelayModel> delay = 
        CreateObject<ConstantSpeedPropagationDelayModel>();
    channel->SetPropagationDelayModel(delay);

    return channel;  // ← Returns NEW object each time
}
```

**Critical Detail:** Every call to `CreateChannel()` creates a **NEW, independent** `SingleModelSpectrumChannel` object. These objects are **NOT connected to each other**.

### Step 4: Configure the Channel

```cpp
cc2420.SetChannel(channel);
```

This stores the channel in the helper's member:

```cpp
// From wsn/helper/cc2420-helper.cc (lines 44-47)
void Cc2420Helper::SetChannel(Ptr<SpectrumChannel> channel)
{
    m_channel = channel;  // ← Store for later use
}
```

Now all subsequent calls to `Install()` on this helper will use this channel.

### Step 5: Configure PHY Attributes

```cpp
cc2420.SetPhyAttribute("TxPower", DoubleValue(params::TX_POWER_DBM));
cc2420.SetPhyAttribute("RxSensitivity", DoubleValue(params::RX_SENSITIVITY_DBM));
cc2420.SetPhyAttribute("PerfectChannel", BooleanValue(m_config.usePerfectChannel));
cc2420.SetPhyAttribute("EnableShadowing", BooleanValue(!m_config.usePerfectChannel));
```

These configure the CC2420Phy object factory:

```cpp
// From wsn/helper/cc2420-helper.cc (lines 76-79)
void Cc2420Helper::SetPhyAttribute(const std::string& name, 
                                   const AttributeValue& value)
{
    m_phyFactory.Set(name, value);
}
```

When `Install()` is called later, the factory creates PHY objects with these attributes.

### Step 6: Install Devices on Nodes

```cpp
m_groundDevices = cc2420.Install(m_groundNodes);
```

This calls `Cc2420Helper::Install()`:

```cpp
// From wsn/helper/cc2420-helper.cc (lines 87-98)
NetDeviceContainer Cc2420Helper::Install(NodeContainer c) const
{
    NetDeviceContainer devices;
    for (NodeContainer::Iterator i = c.Begin(); i != c.End(); ++i) {
        devices.Add(Install(*i));  // ← Call single-node Install
    }
    return devices;
}
```

For each node, calls `CreateDevice()`:

```cpp
// From wsn/helper/cc2420-helper.cc (lines 106-149)
Ptr<NetDevice> Cc2420Helper::CreateDevice(Ptr<Node> node) const
{
    // Create component objects
    Ptr<Cc2420NetDevice> dev = CreateObject<Cc2420NetDevice>();
    Ptr<Cc2420Mac> mac = m_macFactory.Create<Cc2420Mac>();
    Ptr<Cc2420Phy> phy = m_phyFactory.Create<Cc2420Phy>();
    Ptr<Cc2420EnergyModel> energyModel = 
        m_energyFactory.Create<Cc2420EnergyModel>();

    // Wire them together
    dev->SetMac(mac);
    dev->SetPhy(phy);
    dev->SetChannel(m_channel);      // ← Use THIS helper's channel
    mac->SetPhy(phy);
    energyModel->SetPhy(phy);
    
    // Setup PHY with node's position
    if (node->GetObject<MobilityModel>())
    {
        phy->SetMobility(node->GetObject<MobilityModel>());
    }
    if (m_channel)
    {
        phy->SetChannel(m_channel);  // ← Register with channel
    }

    node->AddDevice(dev);
    return dev;
}
```

**Key Steps:**
1. Creates PHY, MAC, NetDevice, Energy components
2. Wires them together (dev → mac → phy)
3. Attaches device to the **THIS helper's m_channel**
4. Registers PHY with the channel

---

## The Channel Isolation Problem Illustrated

### Correct Usage (Single Helper)

```cpp
// One helper instance
wsn::Cc2420Helper cc2420;
auto channel = cc2420.CreateChannel();     // Channel A created
cc2420.SetChannel(channel);

// Both installed on SAME helper → SAME channel
m_groundDevices = cc2420.Install(m_groundNodes);    // Via Channel A
m_uavDevices = cc2420.Install(m_uavNodes);          // Via Channel A (same!)

// Result: Ground devices and UAV devices share Channel A
```

### Incorrect Usage (Separate Helpers) - Current wsn-uav Bug

```cpp
// First helper
wsn::Cc2420Helper cc2420_ground;
auto channel_A = cc2420_ground.CreateChannel();    // Channel A created
cc2420_ground.SetChannel(channel_A);
m_groundDevices = cc2420_ground.Install(m_groundNodes);  // Via Channel A

// Second helper
wsn::Cc2420Helper cc2420_uav;
auto channel_B = cc2420_uav.CreateChannel();       // Channel B created (DIFFERENT!)
cc2420_uav.SetChannel(channel_B);
m_uavDevices = cc2420_uav.Install(m_uavNodes);     // Via Channel B

// Result: Ground on Channel A, UAV on Channel B → NO COMMUNICATION
```

---

## What Happens Inside CC2420

### PHY Layer: Transmission

When a node calls `device->Send(packet, destination)`:

1. **NetDevice** (cc2420-net-device.cc)
   - Receives from application
   - Passes to MAC layer

2. **MAC Layer** (cc2420-mac.cc)
   - CSMA-CA backoff
   - Waits for clear channel (CCA)
   - Passes to PHY layer

3. **PHY Layer** (cc2420-phy.cc)
   - Calculates transmission time: `txTime = packetSize * 8 / dataRate`
   - Broadcasts to channel: `channel->StartTx(device, packet)`
   - All attached devices receive this notification

### Channel: Signal Propagation

When `channel->StartTx()` is called:

```
// From NS-3 SpectrumChannel (not CC2420-specific)
// But this is where isolation happens!

For each device attached to THIS channel:
  1. Calculate path loss (distance-based)
  2. Calculate signal strength at receiver
  3. If signal strength >= RxSensitivity:
     Call device's PHY->StartRx(packet)
  Else:
     Packet lost (not received)
```

**Key:** The channel is a **central arbiter**. Only devices attached to the **same** channel object can hear each other.

### RX Layer: Reception

When device's PHY receives notification:

1. Calculates reception time
2. Models collision detection
3. Passes to MAC layer
4. MAC delivers to device
5. Device delivers to application

---

## Attributes and Configuration

All CC2420 parameters are in `parameters.h`:

```cpp
namespace ns3::wsn::uav::params {
    constexpr double TX_POWER_DBM             = -10;      // dBm
    constexpr double RX_SENSITIVITY_DBM       = -95;      // dBm
    constexpr uint32_t DATA_RATE_BPS          = 250000;   // 250 kbps
    constexpr double GRID_SPACING             = 20.0;     // 20m nodes
    constexpr double UAV_BROADCAST_RADIUS     = 50.0;     // 50m
}
```

These match IEEE 802.15.4 CC2420 specifications.

---

## Trace Points for Debugging

You can monitor CC2420 events:

```cpp
Config::ConnectWithoutContext(
    "/NodeList/*/DeviceList/*/Phy/PhyTxBegin",
    MakeCallback(&OnPhyTxBegin));

Config::ConnectWithoutContext(
    "/NodeList/*/DeviceList/*/Phy/PhyRxBegin",
    MakeCallback(&OnPhyRxBegin));
```

This is what Scenario 0 radio test uses to observe packet flow.

---

## Summary: How CC2420 Works in wsn-uav

| Component | Location | Role |
|-----------|----------|------|
| **Cc2420Helper** | wsn/helper/ | High-level API for creating/installing devices |
| **Cc2420NetDevice** | wsn/model/radio/cc2420/ | NS-3 device interface |
| **Cc2420Mac** | wsn/model/radio/cc2420/ | CSMA-CA MAC protocol |
| **Cc2420Phy** | wsn/model/radio/cc2420/ | TX/RX timing, collisions |
| **SpectrumChannel** | NS-3 core | Central medium for signal propagation |
| **LogDistancePropagationLossModel** | NS-3 core | Path loss calculation |

**Communication Flow:**
```
Application
    ↓
NetDevice.Send()
    ↓
MAC layer (backoff, CCA)
    ↓
PHY.SendPacket()
    ↓
Channel.StartTx(packet)   ← Central arbiter
    ↓
All attached devices' PHY.ReceiveNotification()
    ↓
MAC → NetDevice → Application
```

**The Problem:** If ground devices and UAV devices are on **different** channel objects, the "All attached devices" step only includes devices on that specific channel.

---

## How to Test This

Run Scenario 0 radio test to observe:

```bash
# Shows channels are shared (packets flow)
python3.10 ./ns3 run "scenario-0-radio-test --testMode=shared"

# Shows channels are isolated (no packets flow)
python3.10 ./ns3 run "scenario-0-radio-test --testMode=broken"
```

Look for:
- `Node X TX` events (PHY transmission)
- `Node Y RX` events (PHY reception)
- If TX exists but RX doesn't → channel isolation confirmed

