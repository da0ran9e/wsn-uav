#include "phase1-params.h"

#include <cmath>

namespace ns3::uavsar::p1 {

double TurnRadiusM(double speedMps) {
    return speedMps * speedMps / (kGravity * std::tan(kBankDeg * M_PI / 180.0));
}

}  // namespace ns3::uavsar::p1
