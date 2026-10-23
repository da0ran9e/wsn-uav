"""MEANDER as lanes (CLAUDE.md §8 item 146): SWATH-K's boustrophedon, but the lanes follow the terrain's own
curvilinear coordinates (meander.coords), and each cluster's stretch is bent lightly towards its critical cells.

    python3 tools/meander_lane.py --clusters 8 --seed 1 --work WORK --bin BIN [--lane 8] [--geometry]

  1  lanes: n (signed geodesic distance to the spine) cut into strips L cells wide, offset 0, 1/3 or 2/3 of a lane;
     a lane under CAPL / 4 cells joins its neighbour
  2  lane line: per W/2 of s, the mean centre of the lane's cells nearest the strip's centre n_c (clipped into the
     lane where it is narrower); a 7-bin moving average, then smoothed (ends fixed) until its curvature is at most
     1.02 / RHO (kin_time.curvature, 3 points 10 m apart)
  3  route: the lanes in order of n, alternately both ways, each joined to the next by the shortest Dubins path of
     radius RHO; the offset, and which end the BS starts from: the fewest clusters (step 4), then the shortest
     BS -> route -> BS
  4  clusters: each lane's cells in route order cut into max(ceil(cells / CAPL), ceil(length / (SPAN W))) equal
     consecutive runs (CAPL 190, SPAN 14: the saturation optimum of SAT-vi.md), repaired into connected clusters
     (a run's smaller pieces join the touching cluster they share most edges with); the natural cluster count
  5  deploy: uav-coop-deploy, the CH the strongest node under the cluster's stretch (swath_mission.stage_deploy)
  6  bend, one lane line at a time (so the clusters along it still join seamlessly): every critical cell
     (river_plan Algorithm 3, the local test over the real neighbourhood) farther than the River half width
     OMEGA pulls the line towards itself by min(d - OMEGA, BEND) with a Gaussian bump (sigma = sqrt(2 a RHO), as
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
from restructure import domain, touching
from swath import RHO, cells_at, heading
from swath_mission import stage_deploy
import dubins

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uav-coop2/tools"))
from river_plan import load_around, ring  # noqa: E402

CAPL, SPAN = 190, 14
OMEGA, BEND = 3.5 / 2 * W, W


def lane_line(cells, s, n, nc):
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
    P = resample(P)
    for it in range(6000):
        if len(P) < 5 or kcurv(P).max() * RHO <= 1.02:
            break
        P[1:-1] = (P[:-2] + 2 * P[1:-1] + P[2:]) / 4
        if it % 50 == 49:
            P = resample(np.r_[P, P[-1:]])
    return P


def route(land, L, off):
    _, _, s, n = coords(land)
    lane = {h: int(math.floor(n[h] / (L * W) + off)) for h in land}
    while True:   # a lane under CAPL / 4 cells joins the neighbouring lane towards the spine
        size = {i: sum(1 for v in lane.values() if v == i) for i in set(lane.values())}
        thin = [i for i in sorted(size) if size[i] < CAPL / 4 and len(size) > 1]
        if not thin:
            break
        i = thin[0]
        j = min((x for x in size if x != i), key=lambda x: (abs(x - i), abs(x)))
        lane = {h: j if v == i else v for h, v in lane.items()}
    ids = sorted(set(lane.values()))
    pts, pos, order, s0 = [], {}, [], 0.0
    for m, i in enumerate(ids):
        mine = [h for h in land if lane[h] == i]
        nc = float(np.clip((i - off + 0.5) * L * W, min(n[h] for h in mine), max(n[h] for h in mine)))
        P = lane_line(mine, s, n, nc)
        P = P if m % 2 == 0 else P[::-1]
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


def best_route(land, bs, L):
    out = []
    for off in (0.0, 1 / 3, 2 / 3):
        r = route(land, L, off)
        for x in (r, reverse(r)):
            P = x["poly"]
            tot = x["s"][-1] + dubins.free_start(bs, (*P[0], heading(P, 0)), RHO) + \
                dubins.free_end((*P[-1], heading(P, len(P) - 1, True)), bs, RHO)
            out.append((len(partition(x)[1]), tot, x))
    return min(out, key=lambda t: t[:2])[1:]


def partition(r):
    """Step 4: owner {cell: cluster}, and each cluster's stretch (route coordinates) before the repair."""
    owner, span, k = {}, [], 0
    for _, cs, (a, b) in r["lanes"]:
        p = r["pos"]
        m = max(math.ceil(len(cs) / CAPL), math.ceil((p[cs[-1]] - p[cs[0]]) / (SPAN * W)), 1)
        for j in range(m):
            run = cs[j * len(cs) // m:(j + 1) * len(cs) // m]
            for h in run:
                owner[h] = k + j
            lo = a if j == 0 else (p[cs[j * len(cs) // m - 1]] + p[run[0]]) / 2
            hi = b if j == m - 1 else (p[run[-1]] + p[cs[(j + 1) * len(cs) // m]]) / 2
            span.append((lo, hi))
        k += m
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
    return owner, span


def stage_map(a, W_):
    if os.path.exists(f"{W_}/clusters.csv"):
        return
    g = domain(a.clusters, a.seed)
    land = set(g["domain"])
    xs, ys = [centre(h)[0] for h in land], [centre(h)[1] for h in land]
    bs = ((min(xs) + max(xs)) / 2, min(ys) - 1000.0)
    tot, r = best_route(land, bs, a.lane)
    owner, span = partition(r)
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
                   lane=a.lane, offset=r["off"], route=float(r["s"][-1]), lanes=len(r["lanes"]), total=float(tot),
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


def bend_lane(P, pins, pulls):
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
            if d[i] > OMEGA:
                Q = bump(Q, c, min(d[i] - OMEGA, BEND), i, mult)
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


def stage_curve(W_, K):
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
        Q, idx, kmax = bend_lane(P, [ch[k] for k in ks], pulls)
        for k, i in zip(ks, idx):
            lo, hi = (int(np.searchsorted(d, span[k - 1][0])), int(np.searchsorted(d, span[k - 1][1])))
            lo, hi = min(lo, i), max(hi, i)
            C, i = Q[lo:hi + 1], i - lo
            before = [float(np.min(np.linalg.norm(P[lo:hi + 1] - c, axis=1))) for c in crit[k]]
            after = [float(np.min(np.linalg.norm(C - c, axis=1))) for c in crit[k]]
            t0, t1 = C[min(3, len(C) - 1)] - C[0], C[-1] - C[max(len(C) - 4, 0)]
            t0, t1 = t0 / np.linalg.norm(t0), t1 / np.linalg.norm(t1)
            parts = [np.array([C[0] - RHO * t0, C[0]]), C[:i + 1], C[i:], np.array([C[-1], C[-1] + RHO * t1])]
            with open(f"{W_}/c{k}-path-s35.csv", "w") as f:
                f.write("part,seg,x,y,thDeg\n")
                for j, Pj in enumerate(parts):
                    D = dense(Pj)
                    D = D if j == 3 else D[:-1]
                    for m, p in enumerate(D):
                        nx = D[m + 1] if m + 1 < len(D) else parts[j + 1][0] if j < 3 else p + (p - D[m - 1])
                        th = math.degrees(math.atan2(nx[1] - p[1], nx[0] - p[0]))
                        f.write(f"{j},{-1 if j in (0, 3) else 0 if m == 0 else 1},{p[0]:.3f},{p[1]:.3f},{th:.4f}\n")
            out[k] = dict(crit=len(crit[k]), far_before=sum(x > OMEGA for x in before),
                          far_after=sum(x > OMEGA for x in after), mean_before=round(float(np.mean(before)), 1),
                          mean_after=round(float(np.mean(after)), 1), curvature=round(float(kmax), 3),
                          shift=round(float(np.max(np.linalg.norm(Q[lo:hi + 1] - P[lo:hi + 1], axis=1))), 1),
                          length=round(float(np.linalg.norm(np.diff(C, axis=0), axis=1).sum()), 1))
            json.dump(out[k], open(f"{W_}/c{k}-curve.json", "w"))
    return dict(sorted(out.items()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clusters", type=int, required=True, help="map size: 80 x CLUSTERS cells grown")
    ap.add_argument("--seed", type=int, default=1)
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
    os.makedirs(a.work, exist_ok=True)
    W_ = os.path.abspath(a.work)
    os.chdir(W_)
    stage_map(a, W_)
    K = json.load(open("map.json"))["clusters"]
    stage_core(W_, K)
    stage_deploy(a, W_, K)
    for k, v in stage_curve(W_, K).items():
        print(f"C{k}: {v['length'] / 1000:.2f} km, {v['crit']} critical, beyond the River half width "
              f"{v['far_before']} -> {v['far_after']}, mean distance {v['mean_before']:.0f} -> {v['mean_after']:.0f} m, "
              f"shift <= {v['shift']:.0f} m, k*rho {v['curvature']:.2f}")
    if a.geometry:
        return
    stage_tour(a, W_, K)
    stage_runs(a, W_, K)


if __name__ == "__main__":
    main()
