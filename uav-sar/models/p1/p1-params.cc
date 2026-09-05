#include "p1-params.h"

#include <cmath>

namespace ns3::uavsar::p1 {

double ThetaFullBytes() {
    const double d = 1.0 - kConfuserSimilarity;
    return kThetaBaseBytes / (d * d);
}

double TurnRadiusM(double speedMps) {
    return speedMps * speedMps / (kGravity * std::tan(kBankDeg * M_PI / 180.0));
}

}  // namespace ns3::uavsar::p1
