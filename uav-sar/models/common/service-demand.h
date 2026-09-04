#ifndef UAV_SAR_SERVICE_DEMAND_H
#define UAV_SAR_SERVICE_DEMAND_H

// T0: turn an information demand into a routing cost.
//
// Three steps, and the third is the one that changes the problem class:
//
//   T0.1  theta_n -- how many reference bytes this cell needs. Tiered: a cell
//         that flagged needs a full answer; a class-A cell that did not flag
//         gets a hedge against a Tier-1 miss; a cell that can never
//         discriminate gets nothing, because sending to it is pure waste.
//
//   T0.2  G(b) -- what ONE straight pass at offset b delivers, per unit of
//         inverse speed. Depends only on geometry and on p(d), so it is
//         computed once into a table.
//
//         The fact underneath everything: DOSE IS INVERSELY PROPORTIONAL TO
//         SPEED. An aircraft that cannot hover has exactly one control for
//         "give this place more" -- fly slower over it.
//
//   T0.3  c_n -- the demand as SECONDS of flight time. Once a cell is a
//         weighted node in a graph, a continuous delivery problem has become a
//         combinatorial routing problem, and the rest of the pipeline is
//         standard machinery instead of new mathematics.
//
// CIRCULARITY, handled explicitly: c_n depends on the offset b, b depends on
// the route, and the route needs c_n. The first pass assumes b = 0 and T4
// re-enters with the offsets the route actually produced.

#include "cell-class.h"
#include "cell-grid.h"
#include "node-capability.h"
#include "tier1-detect.h"

#include <cstdint>
#include <map>
#include <vector>

namespace ns3::uavsar {

// One pass at offset b delivers  lambda_tx * G(b) / v  bytes.  G has units of
// metres: it is the equivalent length of the pass at peak reception.
class DosePerPass {
  public:
    DosePerPass();
    double G(double offsetM) const;         // metres
    // Equivalent interaction length at offset b: G(b) / p(b). The length over
    // which the aircraft has to hold the reduced speed for the dose to be real.
    double InteractionLength(double offsetM) const;
    double Prx(double distanceM) const;
  private:
    std::vector<double> m_g;                // sampled 0..kGmaxOffsetM
};

struct CellDemand {
    int32_t  cellId = -1;
    CellClass cls = CellClass::C;
    double   theta = 0.0;        // bytes of reference needed; 0 = do not serve
    double   weight = 0.0;       // w_n from Tier 1; 0 outside D
    bool     suspect = false;
    double   x = 0, y = 0;       // cell centre -- the point to route to
    // Filled by ServiceCost().
    double   servePenaltyS = 0.0;   // seconds ADDED over flying past at cruise
    double   serveSpeedMps = 0.0;   // speed to hold over the cell; 0 = loiter
    uint32_t loiterLoops = 0;       // >0 when one pass can never be enough
};

// T0.1: demand per cell.
std::map<int32_t, CellDemand>
BuildDemands(const CellGridPlan& grid, const CellRolePlan& roles,
             const Tier1Result& tier1,
             const std::map<uint32_t, NodeCapability>& caps);

// T0.3: cost in seconds of serving this cell from a pass at offset `offsetM`.
// Writes servePenaltyS / serveSpeedMps / loiterLoops into `d` and returns the
// penalty. A cell with theta = 0 costs nothing and is left untouched.
double ServiceCost(CellDemand& d, double offsetM, const DosePerPass& dose);

}  // namespace ns3::uavsar

#endif  // UAV_SAR_SERVICE_DEMAND_H
