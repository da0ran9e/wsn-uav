"""MEANDER in the whole Phase-1 mission (CLAUDE.md §8 items 103-104): curved, terrain-following flight in ns-3.

    python3 tools/meander_mission.py --clusters 4 --seed 2 --work WORK --bin BIN [--jobs 3] [--banks local]

The map is the one of mission.py --clusters K --seed S (restructure.domain), partitioned by MEANDER
(meander.partition_meander, lanes 4.5 cells) instead of k-medoids. Options (CLAUDE.md §8 item 106):
  --span C          MEANDER clusters at most C cells long along s (a shorter Axe)
  --lane L, --frag F   lane width (cells) and fragment threshold (x 80 cells) of MEANDER (item 116)
  --partition kmedoids   mission.py's compact clusters, each flown along its own spine (meander.coords)
  --windowKB Q      each cluster's River moves only Q kB of D, around where the UAV passes the CH
Stages (resumable like mission.py):
  1 map      domain-cells.csv, clusters.csv, c{k}-cells.csv, c{k}-nodesin.csv, map.json (mission.py layout)
  2 deploy   per cluster uav-coop-deploy, only for the roles (CH, CLs), routes and gateways (CH margin
             300/200/100/0 m, entries 0-9, as mission.py); its straight path is kept as c{k}-path-deploy.csv
  3 curve    the cluster's MEANDER line (meander.flight_curve: lane centre, curvature <= 1/rho) bent through
             the CH, which uav-coop-pass requires (the CH is a critical cell and hears the UAV directly):
               v = CH - nearest curve point P(s*);  P(s) += v exp(-(s - s*)^2 / (2 sigma^2)),
               sigma = sqrt(2 |v| rho) (the bump alone turns at 1 / (2 rho) at most);
             then Laplacian smoothing with the CH and the ends pinned until the curvature is <= 1/rho (with
             the CH pinned it tends to a kink there, so where 2000 rounds are not enough the bump is widened,
             sigma x 1.5, 2, 3, 4, 6); a
             straight lead-in / lead-out of rho; vertices every <= 1.9 m with the CH one of them;
             parts 0 lead-in, 1 entry -> CH, 2 CH -> exit, 3 lead-out; written as c{k}-path-s35.csv
  4 tour, pass, river   mission.py stage_tour and stage_runs (River Banks --banks, default local; a cell the
             curve crosses twice keeps its longest visit as Seg(a), river_export.py --reentry)
"""
import argparse, csv, json, math, os

import numpy as np

from map_gen import centre
from meander import RHO, coords, curvature, flight_curve, partition_meander
import mission
from mission import sh, stage_runs, stage_tour
from partition import pieces
from restructure import CAP, domain


def stage_map_kmedoids(a, W_):
    """mission.py's map and k-medoids clusters; each cluster gets its own spine and s (meander.coords)."""
    if os.path.exists(f"{W_}/coords.csv"):
        return
    mission.stage_map(a, W_)
    owner = {(int(r["q"]), int(r["r"])): int(r["cluster"]) for r in csv.DictReader(open(f"{W_}/clusters.csv"))}
    with open(f"{W_}/coords.csv", "w") as f:
        f.write("q,r,s,n,lane\n")
        for k in sorted(set(owner.values())):
            mine = {h for h in owner if owner[h] == k}
            main, _, s, n = coords(mine)
            assert main == mine, f"cluster {k} is in pieces"
            for h in sorted(mine):
                f.write(f"{h[0]},{h[1]},{s[h]:.3f},{n[h]:.3f},0\n")


def stage_map(a, W_):
    if os.path.exists(f"{W_}/clusters.csv"):
        return
    g = domain(a.clusters, a.seed)
    land = set(g["domain"])
    cv = None
    if a.meanderK:   # item 118: k-medoids' cluster count; the lane width (6 first) with the most even sizes
        best = None
        for L in (6, 5.5, 6.5, 5, 7, 4.5, 7.5, 8):
            for frag in (0.25, 0.5):
                r = partition_meander(land, L, frag_share=frag, count=math.ceil(len(land) / CAP))
                sz = np.bincount(list(r[0].values()))
                whole = all(len(pieces([h for h in r[0] if r[0][h] == c])) == 1 for c in range(len(sz)))
                cvi = float(sz.std() / sz.mean()) if whole else math.inf
                if best is None or cvi < best[0]:
                    best = (cvi, L, frag, r)
            if best[0] <= 0.11:
                break
        cv, a.lane, a.frag, (owner, lane, s, n, _, _) = best
        assert cv < math.inf, "MEANDER-K: no lane width gives connected clusters"
    else:
        owner, lane, s, n, _, _ = partition_meander(land, a.lane, span=a.span, frag_share=a.frag)
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
    with open(f"{W_}/coords.csv", "w") as f:   # MEANDER's curvilinear coordinates, for flight_curve
        f.write("q,r,s,n,lane\n")
        for h in sorted(owner):
            f.write(f"{h[0]},{h[1]},{s[h]:.3f},{n[h]:.3f},{lane[h]}\n")
    for k in sorted(set(owner.values())):
        with open(f"{W_}/c{k + 1}-cells.csv", "w") as f:
            f.write("q,r\n" + "".join(f"{q},{r}\n" for (q, r), c in sorted(owner.items()) if c == k))
        with open(f"{W_}/c{k + 1}-nodesin.csv", "w") as f:
            f.write("x,y,q,r,obs,cpu,comm\n")
            for v in nodes:
                if owner[(v[3], v[4])] == k:
                    f.write(f"{v[1]:.3f},{v[2]:.3f},{v[3]},{v[4]},{v[5]:.6g},{v[6]:.6g},{v[7]:.6g}\n")
    xs, ys = [centre(h)[0] for h in land], [centre(h)[1] for h in land]
    bs = ((min(xs) + max(xs)) / 2, min(ys) - 1000.0)
    K = len(set(owner.values()))
    json.dump(dict(clusters=K, cells=len(land), nodes=len(nodes), bs=bs, over=0, partition="meander", lane=a.lane,
                   span=a.span, meanderK=int(a.meanderK), frag=a.frag, cv=cv),
              open(f"{W_}/map.json", "w"))
    print(f"map: {len(land)} land cells, {len(nodes)} nodes, {K} clusters "
          f"{[sum(1 for c in owner.values() if c == i) for i in range(K)]}, BS {bs[0]:.0f},{bs[1]:.0f}")


def stage_deploy(a, W_, K):
    env = dict(os.environ, LD_LIBRARY_PATH=f"{a.bin}/lib")
    for k in range(1, K + 1):
        if os.path.exists(f"{W_}/c{k}-path-deploy.csv"):
            continue
        base = [f"{a.bin}/deploy-bin", f"--regionIn=c{k}-cells.csv", f"--nodesIn=c{k}-nodesin.csv",
                "--spacings=35", "--angle=180", f"--out=c{k}"]
        margin, pick = next((m, p) for m in (300, 200, 100, 0) for p in range(10)
                            if sh(base + [f"--chMargin={m}", f"--pick={p}"], f"c{k}-deploy.log", env, ok=True))
        os.rename(f"c{k}-path-s35.csv", f"c{k}-path-deploy.csv")
        json.dump(dict(chMargin=margin, pick=pick), open(f"{W_}/c{k}-deploy.json", "w"))


def through(P, ch):
    """The curve P (10 m vertices, no leads) bent through ch and smoothed to curvature <= 1/RHO: the bump
    widened (sigma x 1, 1.5, 2, 3, 4, 6) until the smoothing reaches it."""
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    i = int(np.argmin(np.linalg.norm(P - ch, axis=1)))
    v = ch - P[i]

    def even(P):       # equal steps of at most 10 m (resample's short last step would fake a sharp turn)
        seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
        d = np.linspace(0, seg[-1], max(1, math.ceil(seg[-1] / 10.0)) + 1)
        return np.c_[np.interp(d, seg, P[:, 0]), np.interp(d, seg, P[:, 1])]

    def split(P, i):   # both halves resampled, the CH the vertex between them
        A, B = even(P[:i + 1]), even(P[i:])
        return np.r_[A, B[1:]], len(A) - 1

    for mult in (1, 1.5, 2, 3, 4, 6):
        sigma = max(mult * math.sqrt(2 * np.linalg.norm(v) * RHO), 20.0)
        Q = P + v * np.exp(-(s - s[i]) ** 2 / (2 * sigma ** 2))[:, None]
        Q[i] = ch
        Q, j = split(Q, i)
        for it in range(2000):
            if len(Q) < 8 or curvature(Q).max() <= 1 / RHO:
                break
            R = Q[1:-1] + 0.25 * (Q[:-2] + Q[2:] - 2 * Q[1:-1])
            if 0 < j < len(Q) - 1:
                R[j - 1] = ch
            Q[1:-1] = R
            if it % 50 == 49:
                Q, j = split(Q, j)
        kmax = float(curvature(Q).max() * RHO) if len(Q) >= 8 else 0.0
        if kmax <= 1.0 + 1e-3:
            break
    return Q, j, kmax, mult


def dense(P, step=1.9):
    """Vertices every <= step m, P's own vertices kept (the ends and the CH among them)."""
    out = [P[0]]
    for p, q in zip(P, P[1:]):
        m = max(1, math.ceil(np.linalg.norm(q - p) / step))
        out += [p + (q - p) * j / m for j in range(1, m + 1)]
    return np.array(out)


def stage_curve(a, W_, K):
    co = {(int(r["q"]), int(r["r"])): float(r["s"]) for r in csv.DictReader(open(f"{W_}/coords.csv"))}
    out = {}
    for k in range(1, K + 1):
        if os.path.exists(f"{W_}/c{k}-curve.json"):
            out[k] = json.load(open(f"{W_}/c{k}-curve.json"))
            continue
        cells = [(int(r["q"]), int(r["r"])) for r in csv.DictReader(open(f"{W_}/c{k}-cells.csv"))]
        ch = next(r for r in csv.DictReader(open(f"{W_}/c{k}-nodes-s35.csv")) if r["isCH"] == "1")
        ch = np.array([float(ch["x"]), float(ch["y"])])
        P, ok = flight_curve(cells, co)
        core = P[25:-25]                                   # flight_curve's leads: 25 vertices of RHO / 25
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
        out[k] = dict(chOffset=round(off, 1), curvature=round(kmax, 3), feasible=int(ok and kmax <= 1.0 + 1e-3),
                      length=round(L, 1), sigmaX=mult)
        json.dump(out[k], open(f"{W_}/c{k}-curve.json", "w"))
    return out


def bend_figure(works, path):
    """One panel per (work, cluster): the cluster's cells, its MEANDER line (dashed), the line bent through the
    CH (solid, leads included) and the CH (star). No text (CLAUDE.md §8 item 63)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    from map_gen import corners, strip_text
    from restructure import INK, INK2, LAND, SURF
    fig, axs = plt.subplots(1, len(works), figsize=(5 * len(works), 5), dpi=150, facecolor=SURF)
    for ax, (W_, k) in zip(np.atleast_1d(axs), works):
        own = {(int(r["q"]), int(r["r"])): int(r["cluster"]) for r in csv.DictReader(open(f"{W_}/clusters.csv"))}
        co = {(int(r["q"]), int(r["r"])): float(r["s"]) for r in csv.DictReader(open(f"{W_}/coords.csv"))}
        cl = [h for h in own if own[h] == k]
        P0, _ = flight_curve(cl, co)
        P = np.array([[float(r["x"]), float(r["y"])] for r in csv.DictReader(open(f"{W_}/c{k}-path-s35.csv"))])
        ch = next(r for r in csv.DictReader(open(f"{W_}/c{k}-nodes-s35.csv")) if r["isCH"] == "1")
        box = np.r_[P0, P]
        near = [h for h in own if box[:, 0].min() - 300 < centre(h)[0] < box[:, 0].max() + 300
                and box[:, 1].min() - 300 < centre(h)[1] < box[:, 1].max() + 300]
        ax.add_collection(PolyCollection([corners(h) for h in near], edgecolors=SURF, linewidths=.4,
                                         facecolors=["#c9dcf3" if own[h] == k else LAND for h in near]))
        ax.plot(*P0[25:-25].T, color=INK2, lw=1.4, ls=(0, (4, 2)))
        ax.plot(*P.T, color=INK, lw=2)
        ax.scatter(float(ch["x"]), float(ch["y"]), s=260, marker="*", color="#ffffff", edgecolors=INK, lw=1, zorder=5)
        ax.set_xlim(box[:, 0].min() - 250, box[:, 0].max() + 250)
        ax.set_ylim(box[:, 1].min() - 250, box[:, 1].max() + 250)
        ax.set_aspect("equal"); ax.axis("off")
    strip_text(fig)
    fig.savefig(path, facecolor=SURF, bbox_inches="tight", pad_inches=.05)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clusters", type=int, required=True, help="map size: 80 x CLUSTERS cells grown")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--work", required=True)
    ap.add_argument("--bin", required=True)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--schemes", default="rf", help="tags of mission.SCHEMES to run")
    ap.add_argument("--lane", type=float, default=4.5, help="MEANDER lane width, cells")
    ap.add_argument("--frag", type=float, default=0.25, help="MEANDER: pieces under FRAG x 80 cells are merged (item 116)")
    ap.add_argument("--banks", default="local", choices=("parallel", "local"))
    ap.add_argument("--partition", default="meander", choices=("meander", "kmedoids"),
                    help="kmedoids: mission.py's compact clusters, each flown along its own spine (item 106)")
    ap.add_argument("--span", type=float, default=0, help="MEANDER: clusters at most this many cells long along s")
    ap.add_argument("--windowKB", type=float, default=0,
                    help="each cluster needs only this much of D, around the CH (river_export.py)")
    ap.add_argument("--critRing", default="cluster", choices=("cluster", "domain"),
                    help="critical cells' local test over the cluster's cells, or the real neighbourhood (item 135)")
    ap.add_argument("--windowAt", default="ch", choices=("ch", "crit"),
                    help="the window around the CH, or one around each critical cell (river_export.py; item 120)")
    ap.add_argument("--meanderK", action="store_true",
                    help="MEANDER-K (item 118): exactly ceil(cells / 80) clusters, as k-medoids; lane width searched")
    ap.add_argument("--geometry", action="store_true", help="stop after stage 3 (no ns-3 pass or River)")
    ap.add_argument("--bendFig", nargs=2, metavar=("PNG", "WORK:K,..."),
                    help="only draw bend_figure for clusters K of finished works")
    a = ap.parse_args()
    if a.bendFig:
        bend_figure([(w, int(k)) for w, k in (x.rsplit(":", 1) for x in a.bendFig[1].split(","))], a.bendFig[0])
        return
    a.reentry = True   # a curved line may cross a cell twice (river_plan: Seg(a) is the longest visit)
    a.bin = os.path.abspath(a.bin)
    os.makedirs(a.work, exist_ok=True)
    W_ = os.path.abspath(a.work)
    os.chdir(W_)
    (stage_map_kmedoids if a.partition == "kmedoids" else stage_map)(a, W_)
    K = json.load(open("map.json"))["clusters"]
    stage_deploy(a, W_, K)
    cv = stage_curve(a, W_, K)
    print("curves: " + ", ".join(f"C{k} {v['length'] / 1000:.2f} km, CH {v['chOffset']:.0f} m off, "
                                 f"k*rho {v['curvature']:.2f}" for k, v in cv.items()))
    if a.geometry:
        return
    stage_tour(a, W_, K)
    stage_runs(a, W_, K)


if __name__ == "__main__":
    main()
