#include "deploy.h"

#include <cmath>
#include <map>

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

void AssignCapabilities(std::vector<SensorNode>& nodes, CoopRng& rng) {
    for (SensorNode& n : nodes) {
        n.obs = rng.Uniform();
        n.cpu = rng.Uniform();
        n.comm = 1.0 - rng.Uniform();   // (0, 1]: never zero
    }
}

size_t AssignRoles(std::vector<SensorNode>& nodes, const std::vector<double>& edgeDist,
                   double margin) {
    auto stronger = [](const SensorNode& a, const SensorNode& b) {
        return a.Score() != b.Score() ? a.Score() > b.Score() : a.id < b.id;
    };
    std::map<Hex, size_t> best;   // cell -> strongest node so far
    size_t ch = nodes.size();
    for (size_t i = 0; i < nodes.size(); ++i) {
        nodes[i].isCH = nodes[i].isCL = false;
        auto it = best.find(nodes[i].cell);
        if (it == best.end() || stronger(nodes[i], nodes[it->second])) best[nodes[i].cell] = i;
        if (edgeDist[i] >= margin && (ch == nodes.size() || stronger(nodes[i], nodes[ch]))) ch = i;
    }
    if (ch < nodes.size()) best[nodes[ch].cell] = ch;
    for (const auto& [cell, i] : best) nodes[i].isCL = true;
    if (ch < nodes.size()) nodes[ch].isCH = true;
    return ch;
}

}  // namespace ns3::uavcoop
