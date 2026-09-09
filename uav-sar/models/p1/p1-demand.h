#ifndef UAV_SAR_P1_DEMAND_H
#define UAV_SAR_P1_DEMAND_H

// T0: turn each head's information demand into seconds of flight time.
//
//   T0.1  G(b), the dose one straight pass at offset b delivers per unit of
//         inverse speed. Depends only on geometry and p(d), so it is tabulated.
//   T0.2  the offset is delta_n, ALREADY KNOWN from P0.5.
//   T0.3  v_n = lambda G(delta_n) / theta_n, the fastest a single pass can be
//   T0.4  c_n, the service cost in seconds
//
// ---------------------------------------------------------------------------
// THE CIRCULARITY IS GONE, AND THAT IS THE POINT OF PA1
// ---------------------------------------------------------------------------
// Before, c_n depended on the offset, the offset depended on the route, and the
// route needed c_n -- so T0 had to guess, and T4 had to iterate until the guess
// stopped moving. It oscillated, and stopping it needed a self-consistency test
// and a halving step.
//
// Now the flight path is the ROW LINE, which Phase 0 fixed before any routing
// happened. delta_n is a property of the elected head, not of a plan. c_n is
// computed once and is final. T4 stops being a correctness requirement and
// becomes an optional improvement.
//
// ---------------------------------------------------------------------------
// ONE INCONSISTENCY IN T0.4, FLAGGED RATHER THAN SILENTLY RESOLVED
// ---------------------------------------------------------------------------
// T0.4 charges the weave -- pi^2 delta^2 / (4a) of extra path to reach the head
// -- AND evaluates the dose at G(delta_n), the standoff of a straight pass. Those
// are two different flights. If the aircraft weaves out to the head it arrives
// overhead and the dose is nearer G(0); if it flies the row straight it pays no
// extra length. Charging both is conservative in both directions at once.
//
// Implemented as written, because it is the spec. DoseAtHead() is the single
// place to change if the intended reading is the other one.

#include "p1-cells.h"
#include "p1-params.h"
#include "p1-sensing.h"
#include "p1-types.h"

#include <cstdint>
#include <map>
#include <vector>

namespace ns3::uavsar::p1 {

class DoseModel {
  public:
    DoseModel();
    double Prx(double distanceM) const;
    double G(double offsetM) const;             // metres
  private:
    std::vector<double> m_g;
};

struct Demand {
    int32_t   cellId = -1;
    CellClass cls = CellClass::BARREN;
    int32_t   row = 0;
    double    x = 0, y = 0;          // cell centre, world frame
    double    offsetM = 0.0;         // delta_n, from P0.5
    uint32_t  files = 0;             // k_n
    double    theta = 0.0;           // bytes; 0 = never serve
    // Written by ServiceCost().
    double    weaveS = 0.0;          // time cost of following the head
    double    doseS = 0.0;           // time cost of delivering theta
    uint32_t  orbits = 0;            // >0 when one pass can never be enough
    double    serveMps = 0.0;        // speed to hold over the head; 0 = orbit
    double    CostS() const { return weaveS + doseS; }
    bool      feasible = true;       // F3: G(delta_n) > 0
};

std::map<int32_t, Demand> BuildDemands(const CellPlan& plan,
                                       const std::vector<Node>& nodes);

// The offset the dose is evaluated at. See the note above.
inline double DoseAtHead(const Demand& d) { return d.offsetM; }

// T0.4. `passM` is the along-row length over which the aircraft can hold the
// reduced speed -- one cell pitch.
double ServiceCost(Demand& d, const DoseModel& dose, double cellPitchM,
                   double turnRadiusM);

}  // namespace ns3::uavsar::p1

#endif  // UAV_SAR_P1_DEMAND_H
