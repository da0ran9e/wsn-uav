#include "deploy.h"

#include <cmath>

namespace ns3::uavcoop {

uint32_t NodeCount(const HexGrid& g, const Region& reg, double spacingM) {
    return (uint32_t)std::lround(reg.cells.size() * g.CellArea() / (spacingM * spacingM));
}

std::vector<SensorNode> DeployNodes(const HexGrid& g, const Region& reg, double spacingM,
                                    CoopRng& rng) {
    const uint32_t n = NodeCount(g, reg, spacingM);
    std::vector<SensorNode> out;
    out.reserve(n);
    const double hw = g.Width() / 2.0, R = g.Radius();
    for (uint32_t i = 0; i < n; ++i) {
        const Hex cell = reg.cells[rng.Below(reg.cells.size())];
        const Point c = g.Centre(cell);
        Point p;
        do {
            p = {c.x + rng.Uniform(-hw, hw), c.y + rng.Uniform(-R, R)};
        } while (!g.Contains(cell, p));
        out.push_back({i, p, cell});
    }
    return out;
}

}  // namespace ns3::uavcoop
