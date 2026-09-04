#ifndef UAV_SAR_P1_SENSING_H
#define UAV_SAR_P1_SENSING_H

// What a ground node can do, and where each capability binds in Phase 1.
//
// Four capabilities that fail INDEPENDENTLY. Each one gates a different thing,
// and the point of listing them is that they gate DIFFERENT STAGES -- a node can
// be excellent at one and useless at the next:
//
//   modality  what it measures      -> decides CLASS. A node of the wrong
//                                     modality can notice something and can
//                                     never say what it is. Reference bytes
//                                     spent on its cell buy nothing at any
//                                     price, so the cell is dropped from the
//                                     routing problem entirely. This is the
//                                     capability that removes work.
//
//   obs       how far it sees       -> sets Tier-1 detection RANGE, and sets
//                                     the Fisher information I_n, hence how
//                                     much reference the node needs (theta ~
//                                     1/I_n). A better sensor asks for LESS.
//                                     This is where "the network is
//                                     heterogeneous" stops being an adjective
//                                     and becomes a term in the objective.
//
//   cpu       can it decide         -> gates whether it can run the matcher at
//                                     all. Below kCpuMatchMin it can raise a
//                                     candidate and never settle one, so its
//                                     cell cannot be class A.
//
//   rxBps     how fast it listens   -> the reference is a bulk download, not a
//                                     trickle, and the aircraft is overhead for
//                                     seconds. Sustained receive rate therefore
//                                     binds here, and it sets how long the cell
//                                     takes to spread the reference internally.
//
// obs SCALES RANGE, NOT GAIN. That distinction was measured on the old system
// and getting it wrong collapsed detection completely: as a gain multiplier, a
// weak sensor standing on top of the target still reported nothing. A weak
// sensor sees the same thing -- it just has to be closer.

#include "p1-params.h"
#include "p1-types.h"

#include <cstdint>
#include <map>
#include <vector>

namespace ns3::uavsar::p1 {

struct Node {
    uint32_t id = 0;
    double   x = 0, y = 0;
    Modality modality = Modality::NONE;
    double   obs = 0.0;        // [0,1]; 0 = no imager
    double   cpu = 0.0;        // [0,1]; fraction of the matcher it can run
    double   rxBps = 0.0;      // sustained receive rate

    bool Images() const { return p1::Images(modality) && obs > 0.0; }
    // Can this node settle an identity, given the reference it would receive?
    bool CanMatch() const {
        return Images() && modality == kReferenceModality && cpu >= kCpuMatchMin;
    }
    // Fisher information proxy: what makes theta_n heterogeneous.
    // TODO(param): obs stands in for I_n until the Chernoff derivation lands.
    double Information() const { return obs > 0.05 ? obs : 0.05; }
    // Score used by the capability-weighted election.
    double ElectScore() const {
        return kElectWCompute * cpu +
               kElectWRadio   * (rxBps / kRxBpsMax) +
               kElectWEnergy  * 1.0;
    }
};

// Deterministic given the seed. Positions come from the caller; capabilities are
// drawn here.
std::vector<Node> BuildNodes(const std::vector<std::pair<double, double>>& xy,
                             uint32_t seed);

// Every node identical and fully capable -- the homogeneous world, for the
// ablation that shows what heterogeneity actually costs.
std::vector<Node> BuildUniformNodes(const std::vector<std::pair<double, double>>& xy);

}  // namespace ns3::uavsar::p1

#endif  // UAV_SAR_P1_SENSING_H
