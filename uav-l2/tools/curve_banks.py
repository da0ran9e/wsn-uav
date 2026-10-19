"""Banks on curved Axes (CLAUDE.md §8 item 103): parallel perpendiculars vs the path's local normals.

    python3 tools/curve_banks.py --works "W/k[468]" --bin BIN --scratch CURV --angles 180,135,100,70 \
        --out docs/data/curve/banks --figs docs/figures

Each cluster of each rebuilt map (tools/regeom.py) is deployed again with uav-coop-deploy --angle=A (180 =
straight across the CH; smaller = the exit turned towards the entry, a bent Dubins path). River plans with
banks=parallel and banks=local (uav-coop2/tools/river_plan.py) are then compared on geometry only:
  band      cluster cells whose centre is within omega of the in-cluster flight path: the River a curved
            Axe should have
  coverage  |River and band| / |band|;  spill  |River - band| / |River|
  offset    mean distance from each Bank to the path, over omega (1 = on the river edge; Banks cut at the
            cluster edge are left out)
Writes OUT.csv and figures FIGS/curve-banks-*.png (no text, CLAUDE.md §8 item 63).
"""
import argparse, csv, glob, os, subprocess, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import numpy as np

from map_gen import strip_text

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uav-coop2/tools"))
from river_plan import load, plan, NB  # noqa: E402

SURF, GREY, INK, RIVER, AXE, BANK, SPILL, MISS = "#fcfcfb", "#e6e5e1", "#0b0b0b", "#c9dcf3", "#1c5cab", \
    "#1baf7a", "#eda100", "#e34948"


def deploy(bin_, work, cl, angle, out):
    os.makedirs(out, exist_ok=True)
    for margin in (300, 200, 100, 0):   # as mission.py: lower the CH margin for a cluster too thin for it
        if os.path.exists(f"{out}/deploy-path-s35.csv"):
            return True
        subprocess.run([f"{bin_}/deploy-bin", f"--regionIn={work}/c{cl}-cells.csv", f"--nodesIn={work}/c{cl}-nodesin.csv",
                        "--spacings=35", f"--angle={angle}", "--pick=0", f"--chMargin={margin}", "--out=deploy"], cwd=out,
                       env=dict(os.environ, LD_LIBRARY_PATH=f"{bin_}/lib"), capture_output=True, text=True)
    return os.path.exists(f"{out}/deploy-path-s35.csv")


def dist_to_path(pts, path):
    a, b = path[:-1], path[1:]
    ab = b - a
    t = np.clip(((pts[:, None, :] - a) * ab).sum(-1) / np.maximum((ab * ab).sum(-1), 1e-9), 0, 1)
    return np.linalg.norm(pts[:, None, :] - (a + t[..., None] * ab), axis=-1).min(axis=1)


def metrics(g, P):
    c, S = g["c"], g["S"]
    inside = np.array([g["uav"][s] for a in P["axe"] for s in P["seg"][a]])
    cells = sorted(S)
    d = dist_to_path(np.array([c[h] for h in cells]), inside)
    band = {h for h, x in zip(cells, d) if x <= P["omega"]}
    river = P["river"]
    edge = lambda h: any((h[0] + a, h[1] + b) not in S for a, b in NB)
    banks = [b for b in P["bank"].values() if not edge(b)]
    off = dist_to_path(np.array([c[b] for b in banks]), inside) / P["omega"] if banks else np.array([np.nan])
    paths = set(P["axe"]) | {h for p in P["bpath"].values() for h in p}   # what the ns-3 River routes over
    return dict(axe=len(P["axe"]), river=len(river), band=len(band), coverage=len(river & band) / max(len(band), 1),
                pathCoverage=len(paths & band) / max(len(band), 1),
                spill=len(river - band) / max(len(river), 1), offset=float(np.nanmean(off))), band


def panel(ax, g, P, band):
    c, R = g["c"], g["R"]
    hexagon = lambda h: [(c[h][0] + R * np.cos(np.pi / 6 + k * np.pi / 3), c[h][1] + R * np.sin(np.pi / 6 + k * np.pi / 3))
                         for k in range(6)]
    river = P["river"]
    col = [AXE if h in P["axe"] else BANK if h in set(P["bank"].values()) else RIVER if h in river & band
           else SPILL if h in river else MISS if h in band else GREY for h in sorted(g["S"])]
    ax.add_collection(PolyCollection([hexagon(h) for h in sorted(g["S"])], facecolors=col, edgecolors=SURF, lw=.6))
    for (a, side), p in P["bpath"].items():
        ax.plot(*np.array([c[h] for h in p]).T, color=INK, lw=.7, alpha=.6)
    ax.plot(*g["path"].T, color=INK, lw=1.6)
    xs = np.array([c[h] for h in g["S"]])
    ax.set_xlim(xs[:, 0].min() - 2 * R, xs[:, 0].max() + 2 * R)
    ax.set_ylim(xs[:, 1].min() - 2 * R, xs[:, 1].max() + 2 * R)
    ax.set_aspect("equal")
    ax.axis("off")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--works", nargs="+", required=True)
    ap.add_argument("--bin", required=True)
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--angles", default="180,135,100,70")
    ap.add_argument("--out", required=True)
    ap.add_argument("--figs", required=True)
    ap.add_argument("--example", default="k4/1", help="map/cluster drawn in curve-banks-example.png")
    a = ap.parse_args()
    angles = [int(x) for x in a.angles.split(",")]
    rows, ex = [], {}
    for w in sorted(x for g in a.works for x in glob.glob(g) if os.path.isdir(x)):
        name = os.path.basename(w)
        K = len(glob.glob(f"{w}/c*-cells.csv"))
        for cl in range(1, K + 1):
            for ang in angles:
                d = os.path.join(a.scratch, f"{name}-c{cl}-a{ang}")
                if not deploy(os.path.abspath(a.bin), os.path.abspath(w), cl, ang, d):
                    rows.append(dict(map=name, cluster=cl, angle=ang, banks="", ok=0))
                    continue
                g = load(d, f"{d}/deploy-path-s35.csv")
                for b in ("parallel", "local"):
                    try:
                        P = plan(g, banks=b)
                    except AssertionError:   # the path re-enters a cell: Seg(a) is not one interval
                        rows.append(dict(map=name, cluster=cl, angle=ang, banks=b, ok=0))
                        continue
                    m, band = metrics(g, P)
                    rows.append(dict(map=name, cluster=cl, angle=ang, banks=b, ok=1, **{k: round(v, 4) for k, v in m.items()}))
                    if f"{name}/{cl}" == a.example:
                        ex[(ang, b)] = (g, P, band)
        print(f"{name}: {K} clusters", flush=True)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    keys = ["map", "cluster", "angle", "banks", "ok", "axe", "river", "band", "coverage", "pathCoverage", "spill", "offset"]
    with open(a.out + ".csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=keys)
        wr.writeheader()
        wr.writerows(rows)
    print("angle banks  n  coverage  pathCoverage  spill  offset  river/band")
    for ang in angles:
        for b in ("parallel", "local"):
            rs = [r for r in rows if r["angle"] == ang and r["banks"] == b and r["ok"]]
            if rs:
                print(f"{ang:5d} {b:8s} {len(rs):3d}  {np.mean([r['coverage'] for r in rs]):.3f}  "
                      f"{np.mean([r['pathCoverage'] for r in rs]):.3f}  "
                      f"{np.mean([r['spill'] for r in rs]):.3f}  {np.nanmean([r['offset'] for r in rs]):.3f}  "
                      f"{np.mean([r['river'] / r['band'] for r in rs]):.3f}")
        print(f"{ang:5d} failed {sum(1 for r in rows if r['angle'] == ang and not r['ok'])}")
    if ex:
        fig, axs = plt.subplots(2, len(angles), figsize=(4 * len(angles), 8), dpi=150, facecolor=SURF)
        for j, ang in enumerate(angles):
            for i, b in enumerate(("parallel", "local")):
                if (ang, b) in ex:
                    panel(axs[i, j], *ex[(ang, b)])
                else:
                    axs[i, j].axis("off")
        strip_text(fig)
        fig.savefig(os.path.join(a.figs, "curve-banks-example.png"), facecolor=SURF, bbox_inches="tight", pad_inches=.05)
        plt.close(fig)


if __name__ == "__main__":
    main()
