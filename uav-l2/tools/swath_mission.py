"""SWATH-K in the whole Phase-1 mission (CLAUDE.md §8 items 115-118, 135): one boustrophedon cut into K clusters.

    python3 tools/swath_mission.py --clusters 8 --seed 10 --work WORK --bin BIN [--jobs 3] [--geometry]

The map is the one of mission.py --clusters K --seed S (restructure.domain); swath.py gives the route and the K
clusters (exactly k-medoids' count, at most 80 cells). Stages (resumable like mission.py):
  1 map      domain-cells.csv, clusters.csv, c{k}-cells.csv, c{k}-nodesin.csv, map.json, route.npz
  2 core     c{k}-core.npy: cluster k's stretch of the route; c{k}-chcells.csv: its cells under that stretch
  3 deploy   per cluster uav-coop-deploy for the roles, routes and gateways, the CH only from c{k}-chcells.csv
             (--chCells: the CH is the strongest node under the flight line; CH margin 300/200/100/0 m)
  4 curve    the stretch bent through the CH (meander_mission.through: curvature <= 1/RHO), straight lead-in /
             lead-out of RHO; c{k}-path-s35.csv with the CH a vertex (uav-coop-pass requires it)
  5 tour, pass, river   mission.py stage_tour and stage_runs (River Banks local; a stretch that turns at the end
             of a lane may cross a cell twice: river_export.py --reentry)
Team 1 then flies the route without transits between clusters that follow each other along a lane (the tour kind
skin in mission_policy: Dubins transits, seamless where one stretch runs on into the next).
"""
import argparse, csv, json, math, os

import numpy as np

from map_gen import cell_at, centre
from meander_mission import dense, through
from mission import sh, stage_runs, stage_tour
from restructure import domain
from swath import RHO, swath


def stage_map(a, W_):
    if os.path.exists(f"{W_}/clusters.csv"):
        return
    g = domain(a.clusters, a.seed)
    land = set(g["domain"])
    xs, ys = [centre(h)[0] for h in land], [centre(h)[1] for h in land]
    bs = ((min(xs) + max(xs)) / 2, min(ys) - 1000.0)
    owner, r, cuts, info = swath(land, bs, L=a.lane)
    gaps = {h: "lake" for h in g["lake_set"]} | {h: "river" for h in g["river"]}
    with open(f"{W_}/domain-cells.csv", "w") as f:
        f.write("q,r,cx,cy,type\n")
        for h in g["final"]:
            f.write(f"{h[0]},{h[1]},{centre(h)[0]:.3f},{centre(h)[1]:.3f},{gaps.get(h, 'land')}\n")
    nodes = [v for v in g["nodes"] if (v[3], v[4]) in owner]
    with open(f"{W_}/clusters.csv", "w") as f:
        f.write("q,r,cluster\n")
        for h in sorted(owner):
            f.write(f"{h[0]},{h[1]},{owner[h] + 1}\n")
    K = len(set(owner.values()))
    for k in range(K):
        with open(f"{W_}/c{k + 1}-cells.csv", "w") as f:
            f.write("q,r\n" + "".join(f"{q},{r_}\n" for (q, r_), c in sorted(owner.items()) if c == k))
        with open(f"{W_}/c{k + 1}-nodesin.csv", "w") as f:
            f.write("x,y,q,r,obs,cpu,comm\n")
            for v in nodes:
                if owner[(v[3], v[4])] == k:
                    f.write(f"{v[1]:.3f},{v[2]:.3f},{v[3]},{v[4]},{v[5]:.6g},{v[6]:.6g},{v[7]:.6g}\n")
    np.savez(f"{W_}/route.npz", poly=r["poly"], s=r["s"], cuts=np.array(cuts))
    sz = np.bincount(list(owner.values()))
    json.dump(dict(clusters=K, cells=len(land), nodes=len(nodes), bs=bs, over=0, partition="swath", lane=a.lane,
                   bearing=info["deg"], offset=info["off"], route=float(r["s"][-1]), lanes=len(r["lanes"]),
                   cv=float(sz.std() / sz.mean())), open(f"{W_}/map.json", "w"))
    print(f"map: {len(land)} land cells, {len(nodes)} nodes, {K} clusters {sz.tolist()}, route "
          f"{r['s'][-1] / 1000:.1f} km over {len(r['lanes'])} lanes at {info['deg']} deg, BS {bs[0]:.0f},{bs[1]:.0f}")


def stage_core(W_, K):
    R = np.load(f"{W_}/route.npz")
    poly, s, cuts = R["poly"], R["s"], R["cuts"]
    for k in range(1, K + 1):
        if os.path.exists(f"{W_}/c{k}-chcells.csv"):
            continue
        core = poly[(s >= cuts[k - 1]) & (s <= cuts[k])]
        np.save(f"{W_}/c{k}-core.npy", core)
        mine = {(int(r["q"]), int(r["r"])) for r in csv.DictReader(open(f"{W_}/c{k}-cells.csv"))}
        under = sorted({cell_at(x, y) for x, y in core[::3]} & mine) or sorted(mine)
        with open(f"{W_}/c{k}-chcells.csv", "w") as f:
            f.write("q,r\n" + "".join(f"{q},{r}\n" for q, r in under))


def stage_deploy(a, W_, K):
    env = dict(os.environ, LD_LIBRARY_PATH=f"{a.bin}/lib")
    for k in range(1, K + 1):
        if os.path.exists(f"{W_}/c{k}-path-deploy.csv"):
            continue
        base = [f"{a.bin}/deploy-bin", f"--regionIn=c{k}-cells.csv", f"--nodesIn=c{k}-nodesin.csv",
                "--spacings=35", "--angle=180", f"--chCells=c{k}-chcells.csv", f"--out=c{k}"]
        margin, pick = next((m, p) for m in (300, 200, 100, 0) for p in range(10)
                            if sh(base + [f"--chMargin={m}", f"--pick={p}"], f"c{k}-deploy.log", env, ok=True))
        os.rename(f"c{k}-path-s35.csv", f"c{k}-path-deploy.csv")
        json.dump(dict(chMargin=margin, pick=pick), open(f"{W_}/c{k}-deploy.json", "w"))


def stage_curve(W_, K):
    out = {}
    for k in range(1, K + 1):
        if os.path.exists(f"{W_}/c{k}-curve.json"):
            out[k] = json.load(open(f"{W_}/c{k}-curve.json"))
            continue
        ch = next(r for r in csv.DictReader(open(f"{W_}/c{k}-nodes-s35.csv")) if r["isCH"] == "1")
        ch = np.array([float(ch["x"]), float(ch["y"])])
        core = np.load(f"{W_}/c{k}-core.npy")[::5]                 # 2 m route vertices -> 10 m, as through expects
        off = float(np.min(np.linalg.norm(core - ch, axis=1)))
        C, i, kmax, mult = through(core, ch)
        t0, t1 = C[min(3, len(C) - 1)] - C[0], C[-1] - C[max(len(C) - 4, 0)]
        t0, t1 = t0 / np.linalg.norm(t0), t1 / np.linalg.norm(t1)
        parts = [np.array([C[0] - RHO * t0, C[0]]), C[:i + 1], C[i:], np.array([C[-1], C[-1] + RHO * t1])]
        with open(f"{W_}/c{k}-path-s35.csv", "w") as f:
            f.write("part,seg,x,y,thDeg\n")
            for j, Pj in enumerate(parts):
                D = dense(Pj)
                D = D if j == 3 else D[:-1]                # a part's last vertex is the next part's first
                for m, p in enumerate(D):
                    nx = D[m + 1] if m + 1 < len(D) else parts[j + 1][0] if j < 3 else p + (p - D[m - 1])
                    th = math.degrees(math.atan2(nx[1] - p[1], nx[0] - p[0]))
                    f.write(f"{j},{-1 if j in (0, 3) else 0 if m == 0 else 1},{p[0]:.3f},{p[1]:.3f},{th:.4f}\n")
        L = float(np.sum(np.linalg.norm(np.diff(C, axis=0), axis=1)))
        out[k] = dict(chOffset=round(off, 1), curvature=round(kmax, 3), feasible=int(kmax <= 1.0 + 1e-3),
                      length=round(L, 1), sigmaX=mult)
        json.dump(out[k], open(f"{W_}/c{k}-curve.json", "w"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clusters", type=int, required=True, help="map size: 80 x CLUSTERS cells grown")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--work", required=True)
    ap.add_argument("--bin", required=True)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--schemes", default="rf", help="tags of mission.SCHEMES to run")
    ap.add_argument("--lane", type=float, default=6.0, help="lane width, cells")
    ap.add_argument("--banks", default="local", choices=("parallel", "local"))
    ap.add_argument("--windowKB", type=float, default=400)
    ap.add_argument("--windowAt", default="crit", choices=("ch", "crit"))
    ap.add_argument("--critRing", default="domain", choices=("cluster", "domain"))
    ap.add_argument("--geometry", action="store_true", help="stop after stage 4 (no ns-3 pass or River)")
    a = ap.parse_args()
    a.reentry = True
    a.bin = os.path.abspath(a.bin)
    os.makedirs(a.work, exist_ok=True)
    W_ = os.path.abspath(a.work)
    os.chdir(W_)
    stage_map(a, W_)
    K = json.load(open("map.json"))["clusters"]
    stage_core(W_, K)
    stage_deploy(a, W_, K)
    cv = stage_curve(W_, K)
    print("curves: " + ", ".join(f"C{k} {v['length'] / 1000:.2f} km, CH {v['chOffset']:.0f} m off, "
                                 f"k*rho {v['curvature']:.2f}" for k, v in cv.items()))
    if a.geometry:
        return
    stage_tour(a, W_, K)
    stage_runs(a, W_, K)


if __name__ == "__main__":
    main()
