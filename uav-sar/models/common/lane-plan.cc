#include "lane-plan.h"

#include <algorithm>
#include <cmath>
#include <limits>
#include <map>

namespace ns3::uavsar {

using ns3::Vector;

namespace {

constexpr double kTwoPi = 2.0 * M_PI;

double Mod2Pi(double t) { return t - kTwoPi * std::floor(t / kTwoPi); }

struct Word { double t, p, q; bool ok; };

Word Lsl(double a, double b, double d) {
    double tmp = std::atan2(std::cos(b) - std::cos(a), d + std::sin(a) - std::sin(b));
    double ps = 2 + d * d - 2 * std::cos(a - b) + 2 * d * (std::sin(a) - std::sin(b));
    if (ps < 0) return {0, 0, 0, false};
    return {Mod2Pi(tmp - a), std::sqrt(ps), Mod2Pi(b - tmp), true};
}
Word Rsr(double a, double b, double d) {
    double tmp = std::atan2(std::cos(a) - std::cos(b), d - std::sin(a) + std::sin(b));
    double ps = 2 + d * d - 2 * std::cos(a - b) + 2 * d * (std::sin(b) - std::sin(a));
    if (ps < 0) return {0, 0, 0, false};
    return {Mod2Pi(a - tmp), std::sqrt(ps), Mod2Pi(tmp - b), true};
}
Word Lsr(double a, double b, double d) {
    double ps = -2 + d * d + 2 * std::cos(a - b) + 2 * d * (std::sin(a) + std::sin(b));
    if (ps < 0) return {0, 0, 0, false};
    double p = std::sqrt(ps);
    double tmp = std::atan2(-std::cos(a) - std::cos(b), d + std::sin(a) + std::sin(b)) -
                 std::atan2(-2.0, p);
    return {Mod2Pi(tmp - a), p, Mod2Pi(tmp - Mod2Pi(b)), true};
}
Word Rsl(double a, double b, double d) {
    double ps = -2 + d * d + 2 * std::cos(a - b) - 2 * d * (std::sin(a) + std::sin(b));
    if (ps < 0) return {0, 0, 0, false};
    double p = std::sqrt(ps);
    double tmp = std::atan2(std::cos(a) + std::cos(b), d - std::sin(a) - std::sin(b)) -
                 std::atan2(2.0, p);
    return {Mod2Pi(a - tmp), p, Mod2Pi(Mod2Pi(b) - tmp), true};
}

// CCC is built geometrically, not from a remembered closed form: the textbook
// LRL/RLR expressions are easy to transcribe with one sign wrong, and a wrong
// one still returns plausible LENGTHS. The Python twin of this file had exactly
// that bug (208 m endpoint error on LRL while the other five words were exact),
// caught only by integrating the control word back to its endpoint.
Word Ccc(double a, double b, double d, bool leftOuter) {
    const double s = leftOuter ? 1.0 : -1.0;
    const double p1x = 0.0, p1y = 0.0, p2x = d, p2y = 0.0;
    const double c1x = p1x - s * std::sin(a), c1y = p1y + s * std::cos(a);
    const double c3x = p2x - s * std::sin(b), c3y = p2y + s * std::cos(b);
    const double vx = c3x - c1x, vy = c3y - c1y;
    const double D = std::hypot(vx, vy);
    if (D > 4.0 || D < 1e-12) return {0, 0, 0, false};
    const double theta = std::atan2(vy, vx), phi = std::acos(D / 4.0);
    Word best{0, 0, 0, false};
    double bestLen = std::numeric_limits<double>::infinity();
    for (double sign : {1.0, -1.0}) {
        const double ang = theta + sign * phi;
        const double c2x = c1x + 2 * std::cos(ang), c2y = c1y + 2 * std::sin(ang);
        const double t = Mod2Pi(s * (std::atan2(c2y - c1y, c2x - c1x) -
                                     std::atan2(p1y - c1y, p1x - c1x)));
        const double p = Mod2Pi(-s * (std::atan2(c3y - c2y, c3x - c2x) -
                                      std::atan2(c1y - c2y, c1x - c2x)));
        const double q = Mod2Pi(s * (std::atan2(p2y - c3y, p2x - c3x) -
                                     std::atan2(c2y - c3y, c2x - c3x)));
        if (t + p + q < bestLen) { bestLen = t + p + q; best = {t, p, q, true}; }
    }
    return best;
}

}  // namespace

double DubinsLength(double x0, double y0, double h0,
                    double x1, double y1, double h1, double R) {
    const double dx = x1 - x0, dy = y1 - y0;
    const double D = std::hypot(dx, dy);
    const double d = D / R;
    const double th = D > 1e-12 ? Mod2Pi(std::atan2(dy, dx)) : 0.0;
    const double a = Mod2Pi(h0 - th), b = Mod2Pi(h1 - th);
    double best = std::numeric_limits<double>::infinity();
    const Word ws[6] = {Lsl(a, b, d), Rsr(a, b, d), Lsr(a, b, d),
                        Rsl(a, b, d), Ccc(a, b, d, false), Ccc(a, b, d, true)};
    for (const Word& w : ws)
        if (w.ok) best = std::min(best, w.t + w.p + w.q);
    return best * R;
}

std::vector<Lane> BuildFieldLanes(const std::vector<Vector>& sensors,
                                  double spacing, double alt) {
    std::vector<Lane> lanes;
    if (sensors.empty() || spacing <= 0) return lanes;
    double x0 = sensors[0].x, x1 = x0, y0 = sensors[0].y, y1 = y0;
    for (const Vector& s : sensors) {
        x0 = std::min(x0, s.x); x1 = std::max(x1, s.x);
        y0 = std::min(y0, s.y); y1 = std::max(y1, s.y);
    }
    const bool alongX = (x1 - x0) >= (y1 - y0);
    const double across0 = alongX ? y0 : x0, across1 = alongX ? y1 : x1;
    const double along0 = alongX ? x0 : y0, along1 = alongX ? x1 : y1;
    const int n = std::max(1, (int)std::ceil((across1 - across0) / spacing) + 1);
    for (int i = 0; i < n; ++i) {
        const double a = std::min(across0 + i * spacing, across1);
        lanes.push_back(alongX ? Lane{Vector(along0, a, alt), Vector(along1, a, alt)}
                               : Lane{Vector(a, along0, alt), Vector(a, along1, alt)});
    }
    return lanes;
}

std::vector<Lane> LanesFor(const std::vector<Lane>& all, uint32_t idx, uint32_t count) {
    if (count == 0) return {};
    const size_t n = all.size();
    const size_t lo = n * idx / count, hi = n * (idx + 1) / count;
    return std::vector<Lane>(all.begin() + lo, all.begin() + hi);
}

std::vector<Vector> OrderLanes(const std::vector<Lane>& lanes,
                               double R, Vector start) {
    const uint32_t n = (uint32_t)lanes.size();
    std::vector<Vector> out;
    if (n == 0) return out;

    auto heading = [](const Vector& from, const Vector& to) {
        return std::atan2(to.y - from.y, to.x - from.x);
    };
    // Each lane has two modes: fly a->b or b->a.
    auto entry = [&](uint32_t i, int d) { return d == 0 ? lanes[i].a : lanes[i].b; };
    auto exit_ = [&](uint32_t i, int d) { return d == 0 ? lanes[i].b : lanes[i].a; };
    auto entryH = [&](uint32_t i, int d) {
        return d == 0 ? heading(lanes[i].a, lanes[i].b) : heading(lanes[i].b, lanes[i].a);
    };

    auto emit = [&](const std::vector<std::pair<uint32_t, int>>& order) {
        for (auto [i, d] : order) { out.push_back(entry(i, d)); out.push_back(exit_(i, d)); }
    };

    if (n > kExactLaneLimit) {                       // fall back to index order
        std::vector<std::pair<uint32_t, int>> order;
        for (uint32_t i = 0; i < n; ++i) order.push_back({i, (int)(i % 2)});
        emit(order);
        return out;
    }

    auto laneLen = [&](uint32_t i) {
        return std::hypot(lanes[i].b.x - lanes[i].a.x, lanes[i].b.y - lanes[i].a.y);
    };
    auto hop = [&](uint32_t i, int di, uint32_t j, int dj) {
        const Vector e = exit_(i, di);
        return DubinsLength(e.x, e.y, entryH(i, di),
                            entry(j, dj).x, entry(j, dj).y, entryH(j, dj), R);
    };

    const uint32_t full = 1u << n;
    const double INF = std::numeric_limits<double>::infinity();
    std::vector<double> dp((size_t)full * n * 2, INF);
    std::vector<int> par((size_t)full * n * 2, -1);
    auto at = [&](uint32_t mask, uint32_t i, int d) { return ((size_t)mask * n + i) * 2 + d; };

    const double sh = heading(start, lanes[0].a);    // heading into the field
    for (uint32_t i = 0; i < n; ++i)
        for (int d = 0; d < 2; ++d)
            dp[at(1u << i, i, d)] =
                DubinsLength(start.x, start.y, sh, entry(i, d).x, entry(i, d).y,
                             entryH(i, d), R) + laneLen(i);

    for (uint32_t mask = 1; mask < full; ++mask)
        for (uint32_t i = 0; i < n; ++i) {
            if (!(mask & (1u << i))) continue;
            for (int di = 0; di < 2; ++di) {
                const double cur = dp[at(mask, i, di)];
                if (cur == INF) continue;
                for (uint32_t j = 0; j < n; ++j) {
                    if (mask & (1u << j)) continue;
                    const uint32_t nm = mask | (1u << j);
                    for (int dj = 0; dj < 2; ++dj) {
                        const double cand = cur + hop(i, di, j, dj) + laneLen(j);
                        if (cand < dp[at(nm, j, dj)] - 1e-9) {
                            dp[at(nm, j, dj)] = cand;
                            par[at(nm, j, dj)] = (int)(i * 2 + di);
                        }
                    }
                }
            }
        }

    double best = INF; uint32_t bi = 0; int bd = 0;
    for (uint32_t i = 0; i < n; ++i)
        for (int d = 0; d < 2; ++d)
            if (dp[at(full - 1, i, d)] < best) { best = dp[at(full - 1, i, d)]; bi = i; bd = d; }

    std::vector<std::pair<uint32_t, int>> order;
    uint32_t mask = full - 1, i = bi; int d = bd;
    while (true) {
        order.push_back({i, d});
        const int pr = par[at(mask, i, d)];
        if (pr < 0) break;
        mask &= ~(1u << i);
        i = (uint32_t)(pr / 2); d = pr % 2;
    }
    std::reverse(order.begin(), order.end());
    emit(order);
    return out;
}


// ---------------------------------------------------------------------------
// Cell-based coverage and the capability/effort balanced split.
// ---------------------------------------------------------------------------

namespace {

double PointToSegment(double px, double py,
                      double ax, double ay, double bx, double by) {
    const double vx = bx - ax, vy = by - ay;
    const double L2 = vx * vx + vy * vy;
    double t = L2 > 0 ? ((px - ax) * vx + (py - ay) * vy) / L2 : 0.0;
    t = std::max(0.0, std::min(1.0, t));
    return std::hypot(px - (ax + t * vx), py - (ay + t * vy));
}

}  // namespace

std::vector<LaneScore> ScoreLanes(const std::vector<Lane>& lanes,
                                  const std::vector<CapNode>& nodes, double radius) {
    std::vector<LaneScore> out(lanes.size());
    for (size_t i = 0; i < lanes.size(); ++i) {
        const Lane& l = lanes[i];
        out[i].effort = std::hypot(l.b.x - l.a.x, l.b.y - l.a.y);
        for (const CapNode& n : nodes)
            if (PointToSegment(n.x, n.y, l.a.x, l.a.y, l.b.x, l.b.y) <= radius)
                out[i].capability += n.screening;
    }
    return out;
}

std::vector<Lane> SelectLanesForCells(const std::vector<Lane>& candidates,
                                      const std::vector<CapNode>& nodes,
                                      double radius, double cellTarget) {
    // Total screening capability per cell -- the denominator each cell is
    // measured against. Cells with no capability at all (no camera anywhere) are
    // dropped from the requirement rather than made unsatisfiable: flying over
    // them cannot buy evidence, which is the whole point of scoring by
    // capability instead of by node count.
    std::map<int32_t, double> total, got;
    for (const CapNode& n : nodes)
        if (n.cellId >= 0) total[n.cellId] += n.screening;

    std::vector<char> taken(candidates.size(), 0);
    std::vector<char> seeded(nodes.size(), 0);
    std::vector<Lane> chosen;

    auto satisfied = [&]() {
        for (const auto& [cid, tot] : total) {
            if (tot <= 1e-9) continue;
            if (got[cid] < cellTarget * tot - 1e-9) return false;
        }
        return true;
    };

    while (!satisfied()) {
        // Marginal capability per metre: what this lane would ADD toward the
        // still-unmet cell targets, divided by what it costs to fly.
        double bestGain = 0; size_t best = candidates.size();
        std::vector<char> bestNew;
        for (size_t i = 0; i < candidates.size(); ++i) {
            if (taken[i]) continue;
            const Lane& l = candidates[i];
            const double len = std::hypot(l.b.x - l.a.x, l.b.y - l.a.y);
            if (len <= 0) continue;
            double add = 0;
            std::vector<char> mark(nodes.size(), 0);
            for (size_t k = 0; k < nodes.size(); ++k) {
                if (seeded[k]) continue;
                const CapNode& n = nodes[k];
                if (n.cellId < 0) continue;
                const double tot = total[n.cellId];
                if (tot <= 1e-9 || got[n.cellId] >= cellTarget * tot) continue;
                if (PointToSegment(n.x, n.y, l.a.x, l.a.y, l.b.x, l.b.y) > radius) continue;
                add += n.screening;
                mark[k] = 1;
            }
            const double gain = add / len;
            if (gain > bestGain) { bestGain = gain; best = i; bestNew = mark; }
        }
        if (best == candidates.size()) break;      // nothing left that helps
        taken[best] = 1;
        chosen.push_back(candidates[best]);
        for (size_t k = 0; k < nodes.size(); ++k)
            if (bestNew[k]) { seeded[k] = 1; got[nodes[k].cellId] += nodes[k].screening; }
    }

    // Keep across-field order: the split below is contiguous, and contiguity is
    // only meaningful if the lanes are sorted the way they lie on the ground.
    std::sort(chosen.begin(), chosen.end(), [](const Lane& p, const Lane& q) {
        return (p.a.x + p.b.x != q.a.x + q.b.x) ? (p.a.x + p.b.x < q.a.x + q.b.x)
                                                : (p.a.y + p.b.y < q.a.y + q.b.y);
    });
    return chosen;
}

std::vector<Lane> ClipLanes(const std::vector<Lane>& lanes,
                            const std::vector<NoFlyZone>& zones) {
    if (zones.empty()) return lanes;
    std::vector<Lane> out;
    for (const Lane& l : lanes) {
        const double dx = l.b.x - l.a.x, dy = l.b.y - l.a.y;
        const double L = std::hypot(dx, dy);
        if (L <= 1e-9) continue;
        // Collect the parameter intervals the lane spends inside a zone, then
        // keep the gaps between them.
        std::vector<std::pair<double, double>> blocked;
        for (const NoFlyZone& z : zones) {
            double t0, t1;
            if (!z.rect) {
                const double fx = l.a.x - z.x, fy = l.a.y - z.y;
                const double A = dx * dx + dy * dy;
                const double B = 2 * (fx * dx + fy * dy);
                const double C = fx * fx + fy * fy - z.r * z.r;
                const double disc = B * B - 4 * A * C;
                if (disc <= 0) continue;             // misses the circle
                const double sq = std::sqrt(disc);
                t0 = (-B - sq) / (2 * A); t1 = (-B + sq) / (2 * A);
            } else {
                // Liang-Barsky slab clip against the axis-aligned box.
                t0 = 0.0; t1 = 1.0;
                const double p[4] = {-dx, dx, -dy, dy};
                const double q[4] = {l.a.x - z.x0, z.x1 - l.a.x,
                                     l.a.y - z.y0, z.y1 - l.a.y};
                bool miss = false;
                for (int k = 0; k < 4 && !miss; ++k) {
                    if (std::fabs(p[k]) < 1e-12) {   // parallel to this slab
                        if (q[k] < 0) miss = true;   // and outside it
                    } else {
                        const double t = q[k] / p[k];
                        if (p[k] < 0) t0 = std::max(t0, t);
                        else          t1 = std::min(t1, t);
                    }
                }
                if (miss || t0 >= t1) continue;
            }
            t0 = std::max(0.0, t0); t1 = std::min(1.0, t1);
            if (t1 > t0) blocked.push_back({t0, t1});
        }
        if (blocked.empty()) { out.push_back(l); continue; }
        std::sort(blocked.begin(), blocked.end());
        double cur = 0.0;
        auto emit = [&](double a, double bb) {
            if ((bb - a) * L < 2.0 * kMinLanePieceM) return;   // too short to fly
            out.push_back(Lane{
                Vector(l.a.x + a * dx, l.a.y + a * dy, l.a.z),
                Vector(l.a.x + bb * dx, l.a.y + bb * dy, l.b.z)});
        };
        for (const auto& [t0, t1] : blocked) {
            if (t0 > cur) emit(cur, t0);
            cur = std::max(cur, t1);
        }
        if (cur < 1.0) emit(cur, 1.0);
    }
    return out;
}

std::vector<Vector> RouteAroundZones(const std::vector<Vector>& wps,
                                     const std::vector<NoFlyZone>& zones,
                                     double marginM) {
    if (zones.empty() || wps.size() < 2) return wps;

    // Deepest penetration of segment pq into zone z, and where it happens.
    // Sample the leg and take the deepest point inside the zone. Sampling rather
    // than a closed form because the zone may be a rectangle, and one code path
    // for both shapes is worth more here than an exact circle solution.
    auto worstHit = [&](const Vector& p, const Vector& q, const NoFlyZone& z,
                        double& depth, Vector& at) {
        depth = -1;
        for (int k = 0; k <= 40; ++k) {
            const double t = k / 40.0;
            const double cx = p.x + t * (q.x - p.x), cy = p.y + t * (q.y - p.y);
            if (!z.Contains(cx, cy)) continue;
            double ux, uy; z.Outward(cx, cy, ux, uy);
            // depth ~ how far from the boundary; approximated by how far the
            // outward ray must run to leave, which is enough to rank legs.
            double d = 0;
            while (d < 2000 && z.Contains(cx + ux * d, cy + uy * d)) d += 5.0;
            if (d > depth) { depth = d; at = Vector(cx, cy, p.z); }
        }
        return depth > 0;
    };

    std::vector<Vector> cur = wps;
    for (int pass = 0; pass < 6; ++pass) {
        std::vector<Vector> next;
        bool changed = false;
        next.push_back(cur.front());
        for (size_t i = 1; i < cur.size(); ++i) {
            const Vector& p = cur[i - 1];
            const Vector& q = cur[i];
            const NoFlyZone* worst = nullptr;
            double bestDepth = 0; Vector at;
            for (const NoFlyZone& z : zones) {
                double d; Vector a;
                if (worstHit(p, q, z, d, a) && d > bestDepth) {
                    bestDepth = d; worst = &z; at = a;
                }
            }
            if (worst) {
                // Push the closest approach radially outside the zone. If the leg
                // runs through the centre there is no radial direction to use, so
                // fall back to the leg's normal -- either side is equally good.
                double ux, uy; worst->Outward(at.x, at.y, ux, uy);
                // Walk outward until clear of the zone, then stand off further.
                double d = 0;
                while (d < 4000 && worst->Contains(at.x + ux * d, at.y + uy * d)) d += 5.0;
                next.push_back(Vector(at.x + ux * (d + marginM),
                                      at.y + uy * (d + marginM), p.z));
                changed = true;
            }
            next.push_back(q);
        }
        cur.swap(next);
        if (!changed) break;
    }
    return cur;
}

std::vector<Lane> SubdivideLanes(const std::vector<Lane>& lanes, uint32_t minPieces) {
    if (lanes.empty() || lanes.size() >= minPieces) return lanes;
    const uint32_t per = (uint32_t)std::ceil((double)minPieces / lanes.size());
    std::vector<Lane> out;
    for (const Lane& l : lanes) {
        for (uint32_t k = 0; k < per; ++k) {
            const double t0 = (double)k / per, t1 = (double)(k + 1) / per;
            out.push_back(Lane{
                Vector(l.a.x + t0 * (l.b.x - l.a.x), l.a.y + t0 * (l.b.y - l.a.y), l.a.z),
                Vector(l.a.x + t1 * (l.b.x - l.a.x), l.a.y + t1 * (l.b.y - l.a.y), l.a.z)});
        }
    }
    // Order by position along the sweep so contiguous blocks stay geometrically
    // contiguous -- otherwise a "contiguous" block is scattered over the field
    // and the whole point of contiguity (one seam) is lost.
    std::sort(out.begin(), out.end(), [](const Lane& p, const Lane& q) {
        const double pa = p.a.x + p.b.x, qa = q.a.x + q.b.x;
        if (pa != qa) return pa < qa;
        return p.a.y + p.b.y < q.a.y + q.b.y;
    });
    return out;
}

std::vector<std::vector<Lane>> BalancedSplit(const std::vector<Lane>& lanes,
                                             const std::vector<CapNode>& nodes,
                                             double radius, uint32_t count,
                                             double alpha, Vector start,
                                             double turnRadiusM) {
    const uint32_t n = (uint32_t)lanes.size();
    std::vector<std::vector<Lane>> out(count);
    if (n == 0 || count == 0) return out;
    if (count == 1) { out[0] = lanes; return out; }

    const std::vector<LaneScore> sc = ScoreLanes(lanes, nodes, radius);
    std::vector<double> pe(n + 1, 0.0), pk(n + 1, 0.0);
    for (uint32_t i = 0; i < n; ++i) {
        pe[i + 1] = pe[i] + sc[i].effort;
        pk[i + 1] = pk[i] + sc[i].capability;
    }
    const double meanK = pk[n] / count;

    // Cost of giving lanes [i, j) to one UAV: how far that block's effort and
    // capability sit from an even share. Both are normalised, so alpha is a
    // genuine trade-off dial and not a units conversion.
    // Effort is what the UAV actually FLIES, not the metres of lane it is given.
    // Scoring lane length alone was measured and it split the field badly: with
    // the base at one corner, the block furthest from it pays a long transit
    // that the objective could not see, and the flown distances came out 56 %
    // apart while the objective believed they were even.
    auto blockEffort = [&](uint32_t i, uint32_t j) {
        double e = pe[j] - pe[i];                       // lane metres
        if (j > i) {
            e += (j - i - 1) * M_PI * turnRadiusM;      // one reversal per gap
            // out to the nearest end of the block, and home from it again
            double best = -1;
            for (uint32_t k = i; k < j; ++k)
                for (const Vector& p : {lanes[k].a, lanes[k].b}) {
                    const double d = std::hypot(p.x - start.x, p.y - start.y);
                    if (best < 0 || d < best) best = d;
                }
            e += 2.0 * std::max(0.0, best);
        }
        return e;
    };
    // Mean effort has to use the same estimator as the blocks, otherwise the
    // normalisation is against a quantity nobody is being scored on.
    const double meanEff = blockEffort(0, n) / count;

    auto blockCost = [&](uint32_t i, uint32_t j) {
        const double e = meanEff > 0
                             ? std::fabs(blockEffort(i, j) - meanEff) / meanEff : 0.0;
        const double k = meanK > 0 ? std::fabs(pk[j] - pk[i] - meanK) / meanK : 0.0;
        return alpha * e + (1.0 - alpha) * k;
    };

    // Exact DP over split points, minimising the WORST block. Minimising the sum
    // would let one UAV be handed a double share as long as another was light;
    // the mission ends when the last UAV lands, so the max is the honest cost.
    const double INF = std::numeric_limits<double>::infinity();
    std::vector<std::vector<double>> dp(count + 1, std::vector<double>(n + 1, INF));
    std::vector<std::vector<uint32_t>> cut(count + 1, std::vector<uint32_t>(n + 1, 0));
    dp[0][0] = 0.0;
    for (uint32_t u = 1; u <= count; ++u)
        for (uint32_t j = u; j <= n; ++j)
            for (uint32_t i = u - 1; i < j; ++i) {
                if (dp[u - 1][i] == INF) continue;
                const double c = std::max(dp[u - 1][i], blockCost(i, j));
                if (c < dp[u][j] - 1e-12) { dp[u][j] = c; cut[u][j] = i; }
            }

    uint32_t j = n;
    for (uint32_t u = count; u >= 1; --u) {
        const uint32_t i = cut[u][j];
        out[u - 1].assign(lanes.begin() + i, lanes.begin() + j);
        j = i;
        if (u == 1) break;
    }
    return out;
}

}  // namespace ns3::uavsar
