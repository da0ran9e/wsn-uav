"""MEANDER as lanes (CLAUDE.md §8 item 146): SWATH-K's boustrophedon, but the lanes follow the terrain's own
curvilinear coordinates (meander.coords), and each cluster's stretch is bent lightly towards its critical cells.

    python3 tools/meander_lane.py --clusters 8 --seed 1 --work WORK --bin BIN [--lane 8] [--geometry]

  1  lanes: n (signed geodesic distance to the spine) cut into strips L cells wide, offset 0, 1/3 or 2/3 of a lane;
     a lane under CAPL / 4 cells joins its neighbour; each land piece (cut off by a lake or a river) its own spine
  2  lane line: per W/2 of s, the mean centre of the lane's cells nearest the strip's centre n_c (clipped into the
     lane where it is narrower); a 7-bin moving average, then smoothed (ends fixed) until its curvature is at most
     1.02 / RHO (kin_time.curvature, 3 points 10 m apart); --straight S km (item 151): its deviation from the
     chord between its ends first smoothed at scale S (straighten), inf the chord. --parallel (item 153): the
     lanes straight and parallel instead (swath.route), the bearing (5 degree steps) and offset of the shortest
     BS -> route -> BS (with --trim the shortest once trimmed, every cluster's shortfall to minAxe added)
  3  route: the lanes in order of n, alternately both ways, each joined to the next by the shortest Dubins path of
     radius RHO; the offset, the first lane's direction along s, and which end the BS starts from: the fewest clusters (step 4), then the shortest
     BS -> route -> BS (with --minAxe the shortest only: thin lanes are already merged)
  4  clusters: each lane's cells in route order cut into max(ceil(cells / CAPL), ceil(length / (span W))) equal
     consecutive runs (CAPL 190, span --span, default SPAN 14: the saturation optimum of SAT-vi.md), repaired into connected clusters
     (a run's smaller pieces join the touching cluster they share most edges with); the natural cluster count
     --minAxe (item 149): each lane cut by the length of its line over its own cells instead, every cluster at
     least minAxe km (one copy of the clue set over its own cells at a constant 50 m/s); --trim T (item 153): the
     lane's land left over cut off its two ends (each end at most RHO + T cells; the leads deliver over RHO of it)
     --chFrom DIR (item 155): the CHs given (DIR's, e.g. the existing clusters' CHs): each lane cut between its
     CHs instead, one cluster per CH; a lane without a CH is not flown, its cells join the clusters they touch;
     lanes chosen with no CH-less lane first, then the shortest once trimmed, the bends onto the CHs included
  5  deploy: uav-coop-deploy, the CH the strongest node under the cluster's stretch (swath_mission.stage_deploy);
     --chAnywhere (item 154): the strongest node of the cluster wherever it lies, the line then bent onto it (step 6)
  6  bend, one lane line at a time (so the clusters along it still join seamlessly): every critical cell
     (river_plan Algorithm 3, the local test over the real neighbourhood) farther than --reach cells (default the
     River half width OMEGA; item 151: 5) pulls the line towards itself by min(d - OMEGA, BEND) with a Gaussian bump (sigma = sqrt(2 a RHO), as
     meander_mission.through), then every CH pulls it onto itself; the bumps widened until the curvature is at
     most 1.02 / RHO (bend_lane); cut back into the clusters' stretches, straight lead-in /
     lead-out of RHO; c{k}-path-s35.csv
  7  tour (kind route: the clusters in route order, seamless where one stretch runs on into the next), pass, River
"""
import argparse, csv, json, math, os, sys

import numpy as np

from kin_time import curvature as kcurv, resample
from map_gen import W, centre
from meander import coords
from meander_mission import dense
from mission import domain_scores, stage_runs, stage_tour
from partition import pieces
from restructure import bs_point, domain, touching
from swath import RHO, cells_at, heading, route as swath_route
from swath_mission import stage_deploy
import dubins

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uav-coop2/tools"))
from river_plan import load_around, ring  # noqa: E402

CAPL, SPAN = 190, 14
OMEGA, BEND = 3.5 / 2 * W, W


def straighten(P, scale):
    """The line's deviation from the chord between its ends, smoothed by a Gaussian of scale metres along it (odd
    reflection at the ends, which stay fixed): 0 keeps the line, larger scales flatten its bends, inf gives the
    chord (item 151)."""
    if scale <= 0 or len(P) < 3:
        return P
    t = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    chord = P[0] + np.outer(t / t[-1], P[-1] - P[0])
    if not np.isfinite(scale):
        return chord
    dev = P - chord
    step = t[-1] / (len(P) - 1)
    k = max(1, int(3 * scale / step))
    ext = np.r_[-dev[k:0:-1], dev, -dev[-2:-k - 2:-1]]   # odd reflection: the deviation stays 0 at the ends
    g = np.exp(-0.5 * (np.arange(-k, k + 1) * step / scale) ** 2)
    g /= g.sum()
    sm = np.c_[np.convolve(ext[:, 0], g, "same"), np.convolve(ext[:, 1], g, "same")][k:k + len(P)]
    return chord + sm


def lane_line(cells, s, n, nc, scale=0.0):
    pts = []
    S0, S1 = min(s[h] for h in cells), max(s[h] for h in cells)
    for a in np.arange(S0, S1 + 1e-9, W / 2):
        b = [h for h in cells if a <= s[h] < a + W / 2]
        if b:
            m = min(abs(n[h] - nc) for h in b)
            pts.append(np.mean([centre(h) for h in b if abs(n[h] - nc) <= m + W], axis=0))
    P = np.array(pts) if len(pts) > 1 else np.array([centre(cells[0]), np.array(centre(cells[0])) + (W, 0)])
    if len(P) >= 5:
        Q = np.vstack([P[:1]] * 3 + [P] + [P[-1:]] * 3)
        P = np.vstack([P[:1], np.mean([Q[i:i + len(P)] for i in range(7)], axis=0)[1:-1], P[-1:]])
    P = straighten(resample(P), scale)
    for it in range(6000):
        if len(P) < 5 or kcurv(P).max() * RHO <= 1.02:
            break
        P[1:-1] = (P[:-2] + 2 * P[1:-1] + P[2:]) / 4
        if it % 50 == 49:
            P = resample(np.r_[P, P[-1:]])
    return P


def route(land, L, off, flip=0, scale=0.0):
    s, n, lane = {}, {}, {}
    for k, part in enumerate(sorted(pieces(list(land)), key=len, reverse=True)):   # a lake or river cuts the land:
        _, _, sp, np_ = coords(set(part))                                          # each piece its own spine
        s.update(sp); n.update(np_)
        lane.update({h: (k, int(math.floor(np_[h] / (L * W) + off))) for h in part})
    while True:   # a lane under CAPL / 4 cells joins the neighbouring lane of its piece towards the spine
        size = {i: sum(1 for v in lane.values() if v == i) for i in set(lane.values())}
        thin = [i for i in sorted(size) if size[i] < CAPL / 4 and sum(x[0] == i[0] for x in size) > 1]
        if not thin:
            break
        i = thin[0]
        j = min((x for x in size if x != i and x[0] == i[0]), key=lambda x: (abs(x[1] - i[1]), abs(x[1])))
        lane = {h: j if v == i else v for h, v in lane.items()}
    ids = sorted(set(lane.values()))
    pts, pos, order, s0 = [], {}, [], 0.0
    for m, i in enumerate(ids):
        mine = [h for h in land if lane[h] == i]
        nc = float(np.clip((i[1] - off + 0.5) * L * W, min(n[h] for h in mine), max(n[h] for h in mine)))
        P = lane_line(mine, s, n, nc, scale)
        P = P if (m + flip) % 2 == 0 else P[::-1]
        if pts:   # the shortest turn from the previous lane's end into this one
            E, S = pts[-1][-1], P[0]
            turn = dubins.path((*E, heading(pts[-1], len(pts[-1]) - 1, True)), (*S, heading(P, 0)), RHO, 2.0)[0]
            T = np.array(turn[1:-1])
            if len(T):
                pts.append(T)
                s0 += float(np.linalg.norm(np.diff(np.r_[E[None], T, S[None]], axis=0), axis=1).sum())
        ls = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
        for h in mine:
            pos[h] = s0 + float(ls[int(np.argmin(np.linalg.norm(P - centre(h), axis=1)))])
        order.append((i, sorted(mine, key=lambda h: (pos[h], h)), (s0, s0 + float(ls[-1]))))
        pts.append(P)
        s0 += float(ls[-1])
    poly = np.vstack(pts)
    poly = poly[np.r_[True, np.linalg.norm(np.diff(poly, axis=0), axis=1) > 1e-9]]
    S = np.r_[0, np.cumsum(np.linalg.norm(np.diff(poly, axis=0), axis=1))]
    return dict(poly=poly, s=S, pos=pos, lanes=order, off=off)


def reverse(r):
    Ln = float(r["s"][-1])
    return dict(r, poly=r["poly"][::-1], s=Ln - r["s"][::-1], pos={h: Ln - v for h, v in r["pos"].items()},
                lanes=[(i, cs[::-1], (Ln - b, Ln - a)) for i, cs, (a, b) in r["lanes"][::-1]])


def parallel(land, th, L, off):
    """--parallel (item 153): straight parallel lanes across bearing th (swath.route), as route() returns them."""
    r = swath_route(land, th, L, off)
    return dict(r, lanes=[(i, cs, (r["pos"][cs[0]] - W / 2, r["pos"][cs[-1]] + W / 2)) for i, cs in r["lanes"]])


def best_route(land, bs, L, span=SPAN, min_axe=0.0, scale=0.0, straight_lanes=False, trim=-1.0, chs=None):
    out = []
    offs = [i / 6 for i in range(6)] if chs else (0.0, 1 / 3, 2 / 3)
    cands = ([parallel(land, math.radians(deg), L, off) for deg in range(0, 180, 5) for off in offs]
             if straight_lanes else
             [route(land, L, off, flip, scale) for off in (0.0, 1 / 3, 2 / 3) for flip in (0, 1)])
    for r in cands:
        for x in (r, reverse(r)):
            P = x["poly"]
            tot = x["s"][-1] + dubins.free_start(bs, (*P[0], heading(P, 0)), RHO) + \
                dubins.free_end((*P[-1], heading(P, len(P) - 1, True)), bs, RHO)
            if min_axe and trim >= 0:   # item 153: the shortest once trimmed, a cluster's shortfall counted as flown
                info = partition(x, span, min_axe, trim, chs)[2]   # item 155: no CH-less lane first, bends added
                key = (info["orphans"], tot - info["trimmed"] + sum(max(0.0, min_axe - g) for g in info["got"])
                       + info["bend"])
            else:
                key = (0 if min_axe else len(partition(x, span)[1]), tot)   # with min_axe by length: the shortest
            out.append((*key, tot, x))
    return min(out, key=lambda t: t[:2])[2:]


def partition(r, cells_long=SPAN, min_axe=0.0, trim=-1.0, chs=None):
    """Step 4: owner {cell: cluster}, and each cluster's stretch (route coordinates) before the repair. min_axe > 0
    (item 149): each lane cut instead into floor(L / min_axe) runs of equal L, L the length of the lane's line over
    its own cells, so that every cluster's Axe carries at least min_axe metres of packets (one copy of the clue set
    at 2.02 km for 400 kB); the ns-3 pass flies at a constant 50 m/s, so no slowing down makes up a short one.
    trim >= 0 (metres, item 153): the lane's land left over by the m runs, half off each end, plus RHO (the lead-in
    and lead-out, along the same straight line, still deliver over it), at most RHO + trim per end; the cells
    there stay with the end clusters, unflown. Also returns, with min_axe, each cluster's metres over its own cells
    (the leads at trimmed lane ends included) and the route metres trimmed off.
    chs [(cell, (x, y))] (item 155, with min_axe): each lane cut between the CHs in it, one cluster per CH (each
    cut at the equal share of the land, kept a cell W from the CHs; the ends trimmed short of the first and last
    CH); a lane without one is not flown and its cells join the clusters they touch. info then also counts those
    lanes and the metres the bends onto the CHs add (a Gaussian bump of a with sigma sqrt(2 a RHO), as bend_lane:
    a^1.5 sqrt(pi) / (4 sqrt(2 RHO)))."""
    owner, span, k, info = {}, [], 0, dict(got=[], trimmed=0.0, orphans=0, bend=0.0)
    left = []
    for _, cs, (a, b) in r["lanes"]:
        p = r["pos"]
        if min_axe:
            d = np.arange(a, b, 2.0)
            P = np.c_[np.interp(d, r["s"], r["poly"][:, 0]), np.interp(d, r["s"], r["poly"][:, 1])]
            mine = set(cs)
            land = np.cumsum([2.0 * (tuple(h) in mine) for h in cells_at(P)])
            at = lambda x: float(d[min(int(np.searchsorted(land, x)), len(d) - 1)])
            if chs is not None:
                here = [np.asarray(xy) for h, xy in chs if h in mine]
                if not here:
                    info["orphans"] += 1
                    left += list(cs)
                    continue
                ix = sorted(int(np.argmin(np.linalg.norm(P - c, axis=1))) for c in here)
                info["bend"] += sum(float(np.min(np.linalg.norm(P - c, axis=1))) ** 1.5 for c in here) \
                    * math.sqrt(math.pi) / (4 * math.sqrt(2 * RHO))
                lc = [float(land[i]) for i in ix]
                m = len(here)
                t0 = t1 = 0.0
                if trim >= 0:   # each end on its own, short of its CH; what one end cannot take the other may
                    cap0, cap1 = (max(0.0, min(RHO + trim, land[-1] / 4, x - W)) for x in (lc[0], land[-1] - lc[-1]))
                    want = max(land[-1] - m * min_axe, 0.0) + 2 * RHO
                    t0 = min(cap0, max(want / 2, want - cap1))
                    t1 = min(cap1, want - t0)
                inner = [float(np.clip(t0 + (land[-1] - t0 - t1) * j / m, lc[j - 1] + W, lc[j] - W))
                         if lc[j] - lc[j - 1] > 2 * W else (lc[j - 1] + lc[j]) / 2 for j in range(1, m)]
                cut = [at(t0) if t0 else a] + [at(x) for x in inner] + [at(land[-1] - t1) if t1 else b]
            else:
                m = max(1, int(land[-1] // min_axe), math.ceil(len(cs) / CAPL))
                t = min(max(land[-1] - m * min_axe, 0.0) / 2 + RHO, RHO + trim, land[-1] / 4) if trim >= 0 else 0.0
                cut = [at(t) if t else a] + [at(t + (land[-1] - 2 * t) * j / m) for j in range(1, m)] + \
                      [at(land[-1] - t) if t else b]
            for h in cs:
                owner[h] = k + min(m - 1, max(0, int(np.searchsorted(cut, p[h], side="right")) - 1))
            span += list(zip(cut[:-1], cut[1:]))
            on = lambda x: float(np.interp(x, d, land))
            ext = [cut[0] - RHO if cut[0] > a else cut[0]] + cut[1:-1] + [cut[-1] + RHO if cut[-1] < b else cut[-1]]
            info["got"] += [on(y) - on(x) for x, y in zip(ext[:-1], ext[1:])]
            info["trimmed"] += cut[0] - a + b - cut[-1]
            k += m
            continue
        m = max(math.ceil(len(cs) / CAPL), math.ceil((p[cs[-1]] - p[cs[0]]) / (cells_long * W)), 1)
        for j in range(m):
            run = cs[j * len(cs) // m:(j + 1) * len(cs) // m]
            for h in run:
                owner[h] = k + j
            lo = a if j == 0 else (p[cs[j * len(cs) // m - 1]] + p[run[0]]) / 2
            hi = b if j == m - 1 else (p[run[-1]] + p[cs[(j + 1) * len(cs) // m]]) / 2
            span.append((lo, hi))
        k += m
    while left:   # item 155: a CH-less lane's cells, piece by piece, to the cluster they touch most (else the nearest CH)
        part = pieces(left)[0]
        nb = {}
        for g in (g for h in part for g in ring(h, 1) if g in owner):
            nb[owner[g]] = nb.get(owner[g], 0) + 1
        if nb:
            j = max(nb, key=lambda j: (nb[j], -j))
        else:
            c = np.mean([centre(h) for h in part], axis=0)
            j = owner[min((h for h, _ in chs), key=lambda h: np.linalg.norm(np.asarray(centre(h)) - c))]
        for h in part:
            owner[h] = j
        left = [h for h in left if h not in owner]
    while True:
        moved = False
        for c in range(k):
            for part in pieces([h for h in owner if owner[h] == c])[1:]:
                nb = touching(owner, part)
                if nb:
                    j = max(nb, key=lambda j: (nb[j], -j))
                    for h in part:
                        owner[h] = j
                    moved = True
        if not moved:
            break
    return owner, span, info


def stage_map(a, W_):
    if os.path.exists(f"{W_}/clusters.csv"):
        return
    g = domain(a.clusters, a.seed, a.shape)
    land = set(g["domain"])
    bs = bs_point(land, a.bs)
    trim = a.trim * W if a.trim >= 0 else -1.0
    chs = None
    if a.chFrom:   # item 155: the CHs given, (cell, position) each
        chs = [((int(x["q"]), int(x["r"])), (float(x["x"]), float(x["y"])))
               for f in sorted(os.listdir(a.chFrom)) if f.startswith("c") and f.endswith("-nodes-s35.csv") and f[1:f.index("-")].isdigit()
               for x in csv.DictReader(open(f"{a.chFrom}/{f}")) if x["isCH"] == "1"]
        json.dump([[*h, *xy] for h, xy in chs], open(f"{W_}/chs.json", "w"))
    tot, r = best_route(land, bs, a.lane, a.span, a.minAxe * 1000, a.straight * 1000, a.parallel, trim, chs)
    owner, span, info = partition(r, a.span, a.minAxe * 1000, trim, chs)
    if chs:   # every cluster exactly one CH
        assert sorted(owner[h] for h, _ in chs) == list(range(len(span))), [owner[h] for h, _ in chs]
    gaps = {h: "lake" for h in g["lake_set"]} | {h: "river" for h in g["river"]}
    with open(f"{W_}/domain-cells.csv", "w") as f:
        f.write("q,r,cx,cy,type\n")
        for h in g["final"]:
            f.write(f"{h[0]},{h[1]},{centre(h)[0]:.3f},{centre(h)[1]:.3f},{gaps.get(h, 'land')}\n")
    with open(f"{W_}/clusters.csv", "w") as f:
        f.write("q,r,cluster\n" + "".join(f"{h[0]},{h[1]},{owner[h] + 1}\n" for h in sorted(owner)))
    K = len(span)
    nodes = [v for v in g["nodes"] if (v[3], v[4]) in owner]
    for k in range(K):
        with open(f"{W_}/c{k + 1}-cells.csv", "w") as f:
            f.write("q,r\n" + "".join(f"{q},{r_}\n" for (q, r_), c in sorted(owner.items()) if c == k))
        with open(f"{W_}/c{k + 1}-nodesin.csv", "w") as f:
            f.write("x,y,q,r,obs,cpu,comm\n")
            for v in nodes:
                if owner[(v[3], v[4])] == k:
                    f.write(f"{v[1]:.3f},{v[2]:.3f},{v[3]},{v[4]},{v[5]:.6g},{v[6]:.6g},{v[7]:.6g}\n")
    np.savez(f"{W_}/route.npz", poly=r["poly"], s=r["s"], span=np.array(span),
             lanes=np.array([iv for _, _, iv in r["lanes"]]))
    sz = np.bincount(list(owner.values()))
    json.dump(dict(clusters=K, cells=len(land), nodes=len(nodes), bs=bs, over=0, partition="meander-lane",
                   lane=a.lane, span=a.span, minAxe=a.minAxe, straight=a.straight, reach=a.reach,
                   parallel=a.parallel, bearing=round(math.degrees(r["th"])) if "th" in r else None,
                   trim=a.trim, chAnywhere=a.chAnywhere, chFrom=a.chFrom, orphans=info["orphans"], bs_at=a.bs, shape=a.shape, offset=r["off"], route=float(r["s"][-1]), lanes=len(r["lanes"]), total=float(tot),
                   cv=float(sz.std() / sz.mean())), open(f"{W_}/map.json", "w"))
    print(f"map: {len(land)} land cells, {K} clusters {sz.tolist()}, {len(r['lanes'])} lanes, route "
          f"{r['s'][-1] / 1000:.1f} km, with BS {tot / 1000:.1f} km")


def stage_core(W_, K):
    R = np.load(f"{W_}/route.npz")
    poly, s, span = R["poly"], R["s"], R["span"]
    for k in range(1, K + 1):
        if os.path.exists(f"{W_}/c{k}-chcells.csv"):
            continue
        lo, hi = span[k - 1]
        core = poly[(s >= lo) & (s <= hi)]
        np.save(f"{W_}/c{k}-core.npy", core)
        mine = {(int(r["q"]), int(r["r"])) for r in csv.DictReader(open(f"{W_}/c{k}-cells.csv"))}
        under = sorted({tuple(h) for h in cells_at(core)} & mine) or sorted(mine)
        if os.path.exists(f"{W_}/chs.json"):   # item 155: the given CH's cell
            under = [h for h in ((q, r) for q, r, *_ in json.load(open(f"{W_}/chs.json"))) if h in mine]
        with open(f"{W_}/c{k}-chcells.csv", "w") as f:
            f.write("q,r\n" + "".join(f"{q},{r}\n" for q, r in under))


def critical(nodes, around, kg=2.0, kl=1.0, r=2):
    """river_plan.plan's Algorithm 3 (critical cells do not depend on the path)."""
    sc = {(int(x["q"]), int(x["r"])): float(x["score"]) for x in nodes if x["isCL"] == "1"}
    mu, sd = np.mean(list(sc.values())), np.std(list(sc.values()))
    chn = next(x for x in nodes if x["isCH"] == "1")
    crit = {(int(chn["q"]), int(chn["r"]))} | {h for h, v in sc.items() if v > mu + kg * sd}
    ref = {**around, **sc}
    for h, v in sc.items():
        near = [ref[g] for k in range(1, r + 1) for g in ring(h, k) if g in ref]
        if v > mu + kl * sd and v >= max(near):
            crit.add(h)
    return sorted(crit)


def bend_lane(P, pins, pulls, reach=OMEGA):
    """Step 6 on one lane line P (10 m vertices): each pull (a critical cell farther than OMEGA) a Gaussian bump of
    min(d - OMEGA, BEND) towards it, then each pin (a CH) a bump onto it (three rounds, so a later bump does not
    move an earlier pin; then exact), each measured from the line so far. A bump of a with sigma = sqrt(2 a RHO)
    turns at 1 / (2 RHO) at most; while the line turns sharper than 1.02 / RHO all bumps are widened (sigma x 1.5
    ... 6). No smoothing afterwards: with the CHs pinned it would tend to straight pieces kinked at the CHs.
    Returns the line, the pins' vertex indices and the largest curvature x RHO."""
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]

    def bump(Q, c, amp, i, mult):
        sigma = max(mult * math.sqrt(2 * amp * RHO), 20.0)
        d = max(float(np.linalg.norm(c - Q[i])), 1e-9)
        return Q + ((c - Q[i]) / d * amp) * np.exp(-(s - s[i]) ** 2 / (2 * sigma ** 2))[:, None]

    for mult in (1, 1.5, 2, 3, 4, 6):
        Q = P.copy()
        for c in pulls:
            d = np.linalg.norm(Q - c, axis=1)
            i = int(np.argmin(d))
            if d[i] > reach:
                Q = bump(Q, c, min(d[i] - reach, BEND), i, mult)
        idx = [int(np.argmin(np.linalg.norm(Q - c, axis=1))) for c in pins]
        for _ in range(3):
            for c, i in zip(pins, idx):
                amp = float(np.linalg.norm(c - Q[i]))
                if amp > 1e-6:
                    Q = bump(Q, c, amp, i, mult)
        for c, i in zip(pins, idx):
            Q[i] = c
        kmax = float(kcurv(Q).max() * RHO)
        if kmax <= 1.02:
            break
    return Q, idx, kmax


def write_path(fn, C, i):
    """C (10 m vertices) as a deploy path file: a straight lead-in and lead-out of RHO along its end tangents, the
    CH at vertex i between parts 1 and 2."""
    t0, t1 = C[min(3, len(C) - 1)] - C[0], C[-1] - C[max(len(C) - 4, 0)]
    t0, t1 = t0 / np.linalg.norm(t0), t1 / np.linalg.norm(t1)
    parts = [np.array([C[0] - RHO * t0, C[0]]), C[:i + 1], C[i:], np.array([C[-1], C[-1] + RHO * t1])]
    with open(fn, "w") as f:
        f.write("part,seg,x,y,thDeg\n")
        for j, Pj in enumerate(parts):
            D = dense(Pj)
            D = D if j == 3 else D[:-1]
            for m, p in enumerate(D):
                nx = D[m + 1] if m + 1 < len(D) else parts[j + 1][0] if j < 3 else p + (p - D[m - 1])
                th = math.degrees(math.atan2(nx[1] - p[1], nx[0] - p[0]))
                f.write(f"{j},{-1 if j in (0, 3) else 0 if m == 0 else 1},{p[0]:.3f},{p[1]:.3f},{th:.4f}\n")


def stage_curve(W_, K, reach=OMEGA):
    if not os.path.exists(f"{W_}/domain-cl.csv"):
        domain_scores(W_, K)
    around = load_around(f"{W_}/domain-cl.csv")
    if all(os.path.exists(f"{W_}/c{k}-curve.json") for k in range(1, K + 1)):
        return {k: json.load(open(f"{W_}/c{k}-curve.json")) for k in range(1, K + 1)}
    R = np.load(f"{W_}/route.npz")
    poly, rs, span, lanes = R["poly"], R["s"], R["span"], R["lanes"]
    ch, crit = {}, {}
    for k in range(1, K + 1):
        nodes = list(csv.DictReader(open(f"{W_}/c{k}-nodes-s35.csv")))
        x = next(r for r in nodes if r["isCH"] == "1")
        ch[k] = np.array([float(x["x"]), float(x["y"])])
        lat = {(int(x["q"]), int(x["r"])): np.array([float(x["cx"]), float(x["cy"])])
               for x in csv.DictReader(open(f"{W_}/c{k}-lattice.csv"))}
        crit[k] = [lat[h] for h in critical(nodes, around)]
    out = {}
    for a, b in lanes:
        ks = [k for k in range(1, K + 1) if a - 1e-6 <= span[k - 1][0] and span[k - 1][1] <= b + 1e-6]
        d = np.r_[np.arange(a, b, 10.0), b]
        P = np.c_[np.interp(d, rs, poly[:, 0]), np.interp(d, rs, poly[:, 1])]
        pulls = [c for k in ks for c in crit[k] if not np.allclose(c, ch[k], atol=W)]
        Q, idx, kmax = bend_lane(P, [ch[k] for k in ks], pulls, reach)
        for k, i in zip(ks, idx):
            lo, hi = (int(np.searchsorted(d, span[k - 1][0])), int(np.searchsorted(d, span[k - 1][1])))
            lo, hi = min(lo, i), max(hi, i)
            C, i = Q[lo:hi + 1], i - lo
            before = [float(np.min(np.linalg.norm(P[lo:hi + 1] - c, axis=1))) for c in crit[k]]
            after = [float(np.min(np.linalg.norm(C - c, axis=1))) for c in crit[k]]
            write_path(f"{W_}/c{k}-path-s35.csv", C, i)
            out[k] = dict(crit=len(crit[k]), far_before=sum(x > reach for x in before),
                          far_after=sum(x > reach for x in after), mean_before=round(float(np.mean(before)), 1),
                          mean_after=round(float(np.mean(after)), 1), curvature=round(float(kmax), 3),
                          shift=round(float(np.max(np.linalg.norm(Q[lo:hi + 1] - P[lo:hi + 1], axis=1))), 1),
                          length=round(float(np.linalg.norm(np.diff(C, axis=0), axis=1).sum()), 1))
            json.dump(out[k], open(f"{W_}/c{k}-curve.json", "w"))
    return dict(sorted(out.items()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clusters", type=int, required=True, help="map size: 80 x CLUSTERS cells grown")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--bs", default="south", choices=("south", "end", "side", "centre"))
    ap.add_argument("--span", type=float, default=SPAN, help="clusters at most SPAN cells long along the route")
    ap.add_argument("--minAxe", type=float, default=0.0,
                    help="km: cut each lane by length so every cluster flies at least this much over its own cells")
    ap.add_argument("--shape", default="", help="map_gen options for the domain (restructure.domain)")
    ap.add_argument("--straight", type=float, default=0.0,
                    help="km: straighten each lane line at this scale (0 none, inf the chord; item 151)")
    ap.add_argument("--parallel", action="store_true",
                    help="straight parallel lanes (swath.route) at the bearing of the shortest route (item 153)")
    ap.add_argument("--trim", type=float, default=-1.0,
                    help="cells: with --minAxe, cut each lane's leftover off its ends, at most RHO + TRIM cells (item 153)")
    ap.add_argument("--chAnywhere", action="store_true",
                    help="the CH the strongest node of the cluster wherever it lies, not under the line (item 154)")
    ap.add_argument("--chFrom", default="",
                    help="work folder whose CHs (c*-nodes-s35.csv) MEANDER's clusters are cut around (item 155)")
    ap.add_argument("--reach", type=float, default=OMEGA / W,
                    help="cells: only critical cells farther than this from the line pull it (item 151: 5)")
    ap.add_argument("--work", required=True)
    ap.add_argument("--bin", required=True)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--schemes", default="rf")
    ap.add_argument("--lane", type=float, default=8.0, help="lane width, cells")
    ap.add_argument("--banks", default="local", choices=("parallel", "local"))
    ap.add_argument("--windowKB", type=float, default=400)
    ap.add_argument("--windowAt", default="crit", choices=("ch", "crit"))
    ap.add_argument("--critRing", default="domain", choices=("cluster", "domain"))
    ap.add_argument("--axeNear", action="store_true")
    ap.add_argument("--geometry", action="store_true", help="stop after the bend (no ns-3 pass or River)")
    a = ap.parse_args()
    a.reentry, a.tourKind = True, "route"
    a.bin = os.path.abspath(a.bin)
    a.chFrom = os.path.abspath(a.chFrom) if a.chFrom else ""
    os.makedirs(a.work, exist_ok=True)
    W_ = os.path.abspath(a.work)
    os.chdir(W_)
    stage_map(a, W_)
    K = json.load(open("map.json"))["clusters"]
    stage_core(W_, K)
    stage_deploy(a, W_, K)
    for k, v in stage_curve(W_, K, a.reach * W).items():
        print(f"C{k}: {v['length'] / 1000:.2f} km, {v['crit']} critical, beyond reach "
              f"{v['far_before']} -> {v['far_after']}, mean distance {v['mean_before']:.0f} -> {v['mean_after']:.0f} m, "
              f"shift <= {v['shift']:.0f} m, k*rho {v['curvature']:.2f}")
    if a.geometry:
        return
    stage_tour(a, W_, K)
    stage_runs(a, W_, K)


if __name__ == "__main__":
    main()
