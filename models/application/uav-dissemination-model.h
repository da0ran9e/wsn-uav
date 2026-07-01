#ifndef UAV_DISSEMINATION_MODEL_H
#define UAV_DISSEMINATION_MODEL_H

#include "../common/semantic-fragment.h"

#include "ns3/address.h"
#include "ns3/ptr.h"
#include "ns3/random-variable-stream.h"
#include "ns3/vector.h"

#include <cstdint>
#include <vector>

namespace ns3::wsn::uav {

enum class BroadcastModel : uint8_t {
    CYCLIC = 0,
    RANDOM = 1,
    UNICAST_FULL = 2,
    UTILITY_WEIGHTED = 3,
};

struct UavDisseminationConfig {
    BroadcastModel model = BroadcastModel::CYCLIC;
    std::vector<Fragment> fragments;
    uint32_t dataSubPacketsPerFragment = 0;
    std::vector<ns3::Vector> sensorPositions;
    std::vector<uint32_t> groundNodeIds;
    std::vector<ns3::Address> groundNodeAddresses;
    double radiusMeters = 0.0;
};

struct UavDisseminationPacket {
    bool valid = false;
    std::vector<uint8_t> payload;
    ns3::Address destination;
};

class UavDisseminationModel {
public:
    UavDisseminationModel();

    void Start(const UavDisseminationConfig& config);
    void Stop();

    UavDisseminationPacket NextPacket(const ns3::Vector& uavPosition);
    void NotifyTxResult(bool sent);

    const char* ModelName() const;
    bool IsActive() const { return m_active; }
    uint32_t FragmentCount() const { return static_cast<uint32_t>(m_fragments.size()); }
    uint32_t DataSubPacketsPerFragment() const { return m_dataSubPacketsPerFragment; }
    uint32_t TxSuccessCount() const { return m_txSuccessCount; }
    uint32_t TxAttemptCount() const { return m_txAttemptCount; }
    uint32_t TxFailCount() const { return m_txFailCount; }

private:
    UavDisseminationPacket BuildBroadcastPacket();
    UavDisseminationPacket BuildUnicastFullPacket(const ns3::Vector& uavPosition);
    void AdvanceUnicastAfterSuccess();
    size_t PickWeightedFragment() const;
    double FragmentWeight(const Fragment& fragment) const;

    BroadcastModel m_model = BroadcastModel::CYCLIC;
    bool m_active = false;
    std::vector<Fragment> m_fragments;
    uint32_t m_dataSubPacketsPerFragment = 0;
    std::vector<ns3::Vector> m_sensorPositions;
    std::vector<uint32_t> m_groundNodeIds;
    std::vector<ns3::Address> m_groundNodeAddresses;
    double m_radiusMeters = 0.0;

    size_t m_curFragIdx = 0;
    uint8_t m_curStep = 0;  // broadcast: 0 semantic, 1..N data

    std::vector<uint16_t> m_unicastFragIdxByNode;
    std::vector<uint8_t> m_unicastSubIdxByNode;
    std::vector<bool> m_unicastNodeComplete;
    size_t m_unicastCursor = 0;
    uint32_t m_unicastCompletedNodes = 0;
    bool m_pendingUnicast = false;
    size_t m_pendingUnicastNode = 0;

    uint32_t m_txSuccessCount = 0;
    uint32_t m_txAttemptCount = 0;
    uint32_t m_txFailCount = 0;

    ns3::Ptr<ns3::UniformRandomVariable> m_rng;
};

}  // namespace ns3::wsn::uav

#endif  // UAV_DISSEMINATION_MODEL_H
