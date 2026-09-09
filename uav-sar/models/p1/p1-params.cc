#include "p1-params.h"

#include <algorithm>
#include <cmath>

namespace ns3::uavsar::p1 {

double TurnRadiusM(double speedMps) {
    return speedMps * speedMps / (kGravity * std::tan(kBankDeg * M_PI / 180.0));
}

double MaxOffsetM(double rc, double rho) {
    const double a = rc * std::sqrt(3.0);       // centre-to-centre within a row
    return a * a / (M_PI * M_PI * rho);
}

double WeaveExtraM(double offsetM, double a) {
    return a > 0 ? M_PI * M_PI * offsetM * offsetM / (4.0 * a) : 0.0;
}

double RowChangeM(double d, double rho) {
    if (rho <= 0) return d;
    if (d < 2.0 * rho) {
        // Tight: swing out and come back. NOTE this is the cited closed form,
        // not the true Dubins optimum -- the real shortest path here is a CCC
        // word and is up to 14 % cheaper. Kept because the design rule is stated
        // against this family; the harness reports both.
        const double th = std::asin(std::min(1.0, d / (2.0 * rho)));
        return std::sqrt(std::max(0.0, 4 * rho * rho - d * d)) + 2 * (M_PI - th) * rho;
    }
    return (M_PI - 2.0) * rho + d;              // quarter, straight, quarter
}

double FanoFloor() {
    return 1.0 / (kConfusers + 1.0);
}

uint32_t FilesNeeded(double information) {
    const double i = std::max(0.01, information) * kInfoPerFile;
    const double k = std::log(1.0 / std::max(1e-9, kTargetPe)) / i;
    return (uint32_t)std::max(1.0, std::ceil(k));
}

double DoseBytes(uint32_t k) {
    // Coupon collector with a deadline. Round-robin over K files with no
    // acknowledgement means a head cannot ask for what it missed; it can only
    // keep listening. The expected number of RECEPTIONS to hold k distinct of K
    // is K*(H_K - H_{K-k}), and the tail is what confidence buys.
    const uint32_t K = kFileCount;
    k = std::min(k, K);
    double h = 0.0;
    for (uint32_t i = K; i > K - k; --i) h += 1.0 / i;
    const double mean = K * h;
    // Tail allowance: the collector's variance is dominated by the last few
    // coupons, so a multiplicative margin is the honest cheap bound rather than
    // a Gaussian quantile that the distribution does not support.
    // TODO(param): replace with a real tail bound once C is pinned down.
    const double margin = 1.0 + kDeliveryConfidence;
    return mean * margin * kFileBytes;
}

}  // namespace ns3::uavsar::p1
