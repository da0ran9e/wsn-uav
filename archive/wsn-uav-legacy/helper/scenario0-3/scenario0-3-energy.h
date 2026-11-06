#ifndef SCENARIO0_3_ENERGY_H
#define SCENARIO0_3_ENERGY_H

#include <cstdint>
#include <map>

namespace ns3::wsn::uav {

// Energy consumption states
enum class EnergyState {
    IDLE = 0,           // Idle mode (minimal power)
    RX = 1,             // Receiving
    TX = 2,             // Transmitting
    SLEEP = 3           // Sleep mode
};

// Simple battery model (standalone, no NS-3 inheritance)
class SimpleBattery {
public:
    SimpleBattery() = default;
    ~SimpleBattery() = default;

    // Battery parameters
    void SetInitialEnergy(double joules) {
        m_initialEnergy = joules;
        m_remainingEnergy = joules;
    }

    double GetInitialEnergy() const { return m_initialEnergy; }
    double GetRemainingEnergy() const { return std::max(0.0, m_remainingEnergy); }
    double GetEnergyFraction() const {
        if (m_initialEnergy <= 0.0) return 0.0;
        return GetRemainingEnergy() / m_initialEnergy;
    }

    bool IsEnergyAvailable() const { return GetRemainingEnergy() > 0.0; }
    double GetTotalEnergyConsumed() const { return m_totalEnergyConsumed; }

    // Update energy (called by device energy models)
    void UpdateEnergy(double energyJ) {
        m_remainingEnergy -= energyJ;
        m_totalEnergyConsumed += energyJ;
    }

private:
    double m_initialEnergy = 3600.0;       // 3600 Joules (~1 Wh)
    double m_remainingEnergy = 3600.0;
    double m_totalEnergyConsumed = 0.0;
};

// LR-WPAN device energy model (standalone, no NS-3 inheritance)
class DeviceEnergyModel {
public:
    DeviceEnergyModel() = default;
    ~DeviceEnergyModel() = default;

    void SetEnergySource(SimpleBattery* source) { m_energySource = source; }

    // Power consumption settings (milliwatts)
    void SetTxPower(double mw) { m_txPowerMw = mw; }
    void SetRxPower(double mw) { m_rxPowerMw = mw; }
    void SetIdlePower(double mw) { m_idlePowerMw = mw; }
    void SetSleepPower(double mw) { m_sleepPowerMw = mw; }

    double GetTxPower() const { return m_txPowerMw; }
    double GetRxPower() const { return m_rxPowerMw; }
    double GetIdlePower() const { return m_idlePowerMw; }
    double GetSleepPower() const { return m_sleepPowerMw; }

    // State transitions
    void TransitionToTx();
    void TransitionToRx();
    void TransitionToIdle();
    void TransitionToSleep();

    EnergyState GetCurrentState() const { return m_currentState; }

    // Energy tracking
    double GetEnergyConsumedInState(EnergyState state) const;
    double GetTimeInState(EnergyState state) const;

private:
    SimpleBattery* m_energySource = nullptr;

    EnergyState m_currentState = EnergyState::IDLE;
    double m_lastStateChangeTimeS = 0.0;

    // Power consumption (mW) - typical for CC2420-compatible LR-WPAN radio
    double m_txPowerMw = 52.0;    // TX: ~52mW
    double m_rxPowerMw = 62.0;    // RX: ~62mW
    double m_idlePowerMw = 0.02;  // Idle: ~0.02mW
    double m_sleepPowerMw = 0.001; // Sleep: ~0.001mW

    // Energy tracking per state
    std::map<EnergyState, double> m_energyInState;  // Joules per state
    std::map<EnergyState, double> m_timeInState;    // seconds per state

    void UpdateEnergyConsumption();
};

}  // namespace ns3::wsn::uav

#endif  // SCENARIO0_3_ENERGY_H
