#include "scenario0-3-energy.h"
#include "ns3/simulator.h"

namespace ns3::wsn::uav {

void
DeviceEnergyModel::TransitionToTx()
{
    UpdateEnergyConsumption();
    m_currentState = EnergyState::TX;
    m_lastStateChangeTimeS = ns3::Simulator::Now().GetSeconds();
}

void
DeviceEnergyModel::TransitionToRx()
{
    UpdateEnergyConsumption();
    m_currentState = EnergyState::RX;
    m_lastStateChangeTimeS = ns3::Simulator::Now().GetSeconds();
}

void
DeviceEnergyModel::TransitionToIdle()
{
    UpdateEnergyConsumption();
    m_currentState = EnergyState::IDLE;
    m_lastStateChangeTimeS = ns3::Simulator::Now().GetSeconds();
}

void
DeviceEnergyModel::TransitionToSleep()
{
    UpdateEnergyConsumption();
    m_currentState = EnergyState::SLEEP;
    m_lastStateChangeTimeS = ns3::Simulator::Now().GetSeconds();
}

void
DeviceEnergyModel::UpdateEnergyConsumption()
{
    double now = ns3::Simulator::Now().GetSeconds();
    double timeDelta = now - m_lastStateChangeTimeS;

    if (timeDelta <= 0.0 || !m_energySource) {
        return;
    }

    double powerMw = 0.0;
    switch (m_currentState) {
    case EnergyState::TX:
        powerMw = m_txPowerMw;
        break;
    case EnergyState::RX:
        powerMw = m_rxPowerMw;
        break;
    case EnergyState::IDLE:
        powerMw = m_idlePowerMw;
        break;
    case EnergyState::SLEEP:
        powerMw = m_sleepPowerMw;
        break;
    }

    // Convert mW to W, then multiply by time to get energy in Joules
    double energyJ = (powerMw / 1000.0) * timeDelta;
    m_energyInState[m_currentState] += energyJ;
    m_timeInState[m_currentState] += timeDelta;

    m_energySource->UpdateEnergy(energyJ);
}

double
DeviceEnergyModel::GetEnergyConsumedInState(EnergyState state) const
{
    auto it = m_energyInState.find(state);
    if (it != m_energyInState.end()) {
        return it->second;
    }
    return 0.0;
}

double
DeviceEnergyModel::GetTimeInState(EnergyState state) const
{
    auto it = m_timeInState.find(state);
    if (it != m_timeInState.end()) {
        return it->second;
    }
    return 0.0;
}

}  // namespace ns3::wsn::uav
