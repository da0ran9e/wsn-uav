#ifndef UAV_SAR_NODE_CAPABILITY_H
#define UAV_SAR_NODE_CAPABILITY_H

// Heterogeneous ground nodes.
//
// Until now every sensor node was interchangeable: same detector, same compute,
// same radio. That made "cover the field" and "cover the nodes that matter" the
// same sentence, and it is the reason the sweep planner could treat a node as a
// point to be passed within 50 m of and nothing more.
//
// Real deployments are not uniform. A node carries three capabilities that fail
// INDEPENDENTLY, and each one gates a different stage of the screening pipeline:
//
//   observation  how far can it see?       -> gates EVIDENCE, as an effective
//                                            RANGE scale, not as a gain on the
//                                            reading. obs = 0 is no camera and
//                                            no evidence ever; obs = 0.5 reaches
//                                            half as far as obs = 1.
//   compute      can it decide?           -> gates IDENTITY. A node can measure
//                                            a clue on cue fragments and still
//                                            lack the compute to run the match
//                                            against the complete reference, so
//                                            it can raise a candidate but never
//                                            confirm or reject one.
//   radio        how much can it listen?  -> gates SEEDING RATE. Modelled as a
//                                            DUTY CYCLE, not a raw bitrate: the
//                                            cue broadcast offers ~4 kbps and
//                                            every 802.15.4 radio does 250 kbps,
//                                            so raw rate never binds and a model
//                                            built on it would be decoration.
//                                            What actually binds in a deployed
//                                            WSN is that cheap nodes sleep; a
//                                            node awake 40 % of the time misses
//                                            60 % of a single overflight. It
//                                            costs nothing against the DATA
//                                            UAV's 20 s dwell -- a duty-cycled
//                                            radio synchronises to a persistent
//                                            source -- so this gates SEEDING
//                                            only, which is Phase 1's problem.
//
// The planning consequence is the point: screening capability is now UNEVENLY
// DISTRIBUTED over the field, so a sweep that treats every square metre alike is
// spending flight time where it cannot buy evidence.

#include <cstdint>
#include <map>
#include <vector>

namespace ns3::uavsar {

// Which physical quantity a node's sensor measures. The reference dataset is
// recorded in ONE modality, and a match can only be run between like and like:
// a thermal node holding a visual reference has nothing to compare it against.
// This is what separates "can detect something is here" from "can say what it
// is", and it is the fourth capability -- independent of the three below, and
// the one that decides whether a cell is worth spending flight time on at all.
enum class Modality : uint8_t {
    NONE = 0,       // no imaging sensor; scalar only
    VISUAL = 1,
    THERMAL = 2,
    ACOUSTIC = 3,
};

// Scalar-only nodes (temperature, humidity, seismic) can raise an anomaly but
// their sample rate is far below what a match needs. They are class C.
inline bool Images(Modality m) { return m != Modality::NONE; }

struct NodeCapability {
    Modality modality = Modality::VISUAL;
    double obs = 1.0;      // [0,1]; 0 = no camera at all
    double cpu = 1.0;      // [0,1]; fraction of the reference matcher it can run
    // Fraction of broadcasts the receiver is actually awake for. The equivalent
    // sustained rate is radioDuty * 250 kbps, which is what a datasheet would
    // quote, but the duty is the quantity that does the work here.
    double radioDuty = 1.0;
    double SustainedBps() const { return radioDuty * 250000.0; }

    // What this node can contribute to SCREENING. Both factors are necessary --
    // a camera with no compute cannot decide, compute with no camera has nothing
    // to decide about -- so they multiply rather than average.
    double Screening() const { return obs * cpu; }
};

struct CapabilityConfig {
    uint32_t seed = 1;
    double cameraFraction = 0.65;   // share of nodes with any camera at all
    // Of the nodes that image at all, how the modality splits. The reference is
    // recorded in ONE of these (params::kReferenceModality), so this fraction
    // directly sets how much of the field can ever be class A.
    // TODO(param): measure or specify for the target deployment.
    double visualFraction = 0.55;   // share of imaging nodes that are VISUAL
    double thermalFraction = 0.30;  // ... THERMAL; remainder is ACOUSTIC
    double obsMin = 0.45, obsMax = 1.0;
    double cpuMin = 0.20, cpuMax = 1.0;
    double dutyMin = 0.35, dutyMax = 1.0;   // receiver awake fraction
    bool   uniform = false;         // true = every node fully capable (the old world)
};

// Deliberately ns-3-independent and drawn from its OWN rng stream, so turning
// heterogeneity on does not shift any other random decision in the run.
std::map<uint32_t, NodeCapability>
BuildCapabilities(const std::vector<uint32_t>& nodeIds, const CapabilityConfig& cfg);

// A node needs enough compute to run the full-reference matcher before it may
// claim or deny an identity. Below this it can still report a clue.
inline constexpr double kCpuConfirmMin = 0.50;

}  // namespace ns3::uavsar

#endif  // UAV_SAR_NODE_CAPABILITY_H
