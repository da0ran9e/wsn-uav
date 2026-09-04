#ifndef UAV_SAR_P1_DEMAND_H
#define UAV_SAR_P1_DEMAND_H

// T0: turn an information demand into a routing cost.
//
// Three steps, and the third changes the problem class:
//
//   T0.1  theta_n -- reference bytes this cell needs. Class A asks; class B and
//         C ask for nothing, because they can never discriminate and reference
//         spent on them buys nothing at any price.
//
//         NOTHING HAS BEEN DETECTED YET. T0 runs before the aircraft has flown,
//         so no node holds the reference and no node can say what is there. The
//         suspect set is an OUTPUT of Phase 1, not an input to it, and the
//         planner must not be handed one.
//
//         theta ~ 1 / I_n : a better sensor asks for LESS. That is the only
//         source of heterogeneity in demand, and it is where the network's
//         unevenness stops being an adjective and becomes a term in the
//         objective -- still what separates this from a plain weighted min-max
//         mTSP, since the weights are DERIVED from the deployment rather than
//         given.
//
//   T0.2  G(b) -- what ONE straight pass at offset b delivers, per unit of
//         inverse speed. It depends only on geometry and p(d), so it is
//         computed once into a table.
//
//         DOSE IS INVERSELY PROPORTIONAL TO SPEED. An aircraft that cannot
//         hover has exactly one control for "give this place more": fly slower
//         over it. That single fact is why T3 is a linear program.
//
//   T0.3  c_n -- the demand in SECONDS of flight time. Once a cell is a
//         weighted node in a graph, a continuous delivery problem has become a
//         combinatorial routing problem and the rest of the pipeline is
//         standard machinery rather than new mathematics.
//
// CIRCULARITY, handled rather than hidden: c_n depends on the offset b, b
// depends on the route, and the route needs c_n. The first pass assumes b = 0
// and T4 re-enters with the offsets the route actually produced.

#include "p1-cells.h"
#include "p1-params.h"
#include "p1-sensing.h"
#include "p1-types.h"

#include <cstdint>
#include <map>
#include <vector>

namespace ns3::uavsar::p1 {

// One pass at offset b delivers lambda_tx * G(b) / v bytes. G has units of
// metres: it is the equivalent length of the pass at peak reception.
class DoseModel {
  public:
    DoseModel();
    double Prx(double distanceM) const;
    double G(double offsetM) const;
    // Equivalent interaction length at offset b: G(b) / p(b). The distance over
    // which the aircraft has to actually hold the reduced speed.
    double InteractionLength(double offsetM) const;
  private:
    std::vector<double> m_g;
};

struct Demand {
    int32_t   cellId = -1;
    CellClass cls = CellClass::C;
    double    x = 0, y = 0;         // cell centre: the point to route to
    double    theta = 0.0;          // bytes needed; 0 = never serve
    // Written by ServiceCost().
    double    penaltyS = 0.0;       // seconds ADDED over flying past at cruise
    double    serveMps = 0.0;       // speed to hold over the cell; 0 = orbit
    uint32_t  orbits = 0;           // >0 when one pass can never be enough
};

std::map<int32_t, Demand> BuildDemands(const CellPlan& plan,
                                       const std::vector<Node>& nodes);

// Seconds of service for this cell from a pass at `offsetM`. Fills the three
// output fields and returns the penalty. A cell with theta = 0 costs nothing.
double ServiceCost(Demand& d, double offsetM, const DoseModel& dose);

// The speed at which one pass at `offsetM` exactly delivers theta. Below the
// airframe's minimum, no single pass can ever be enough -- which is the whole
// reason orbits exist in the cost model.
double OnePassSpeed(double theta, double offsetM, const DoseModel& dose);

}  // namespace ns3::uavsar::p1

#endif  // UAV_SAR_P1_DEMAND_H
