#ifndef UAV_SAR_P1_TYPES_H
#define UAV_SAR_P1_TYPES_H

// The few enumerations everything in Phase 1 shares. Kept in their own header
// so the parameter block and the sensing model can each name them without one
// having to include the other.

#include <cstdint>

namespace ns3::uavsar::p1 {

// Which physical quantity a node's sensor measures.
//
// The reference dataset is recorded in ONE modality, and a match runs only
// between like and like: a thermal node holding a visual reference has nothing
// to compare it against. This is the capability that decides whether a cell can
// EVER settle an identity, as opposed to merely noticing something -- and so it
// is the capability that decides whether flying to that cell can buy anything.
enum class Modality : uint8_t {
    NONE = 0,       // scalar sensors only (temperature, humidity, seismic)
    VISUAL = 1,
    THERMAL = 2,
    ACOUSTIC = 3,
};

inline bool Images(Modality m) { return m != Modality::NONE; }

inline const char* ModalityName(Modality m) {
    switch (m) {
        case Modality::VISUAL:   return "visual";
        case Modality::THERMAL:  return "thermal";
        case Modality::ACOUSTIC: return "acoustic";
        default:                 return "none";
    }
}

// What a cell is FOR. The whole point of the label is that only class A ever
// costs the aircraft anything.
enum class CellClass : uint8_t {
    A = 0,   // can detect AND can discriminate -> worth flying to
    B = 1,   // can detect, can never discriminate -> reference here is waste
    C = 2,   // neither
};

inline const char* CellClassName(CellClass c) {
    switch (c) {
        case CellClass::A: return "A";
        case CellClass::B: return "B";
        default:           return "C";
    }
}

}  // namespace ns3::uavsar::p1

#endif  // UAV_SAR_P1_TYPES_H
