"""How many nodes hold a whole file, when only consecutive packets make one.

    python3 tools/runs_report.py --deploy ../uav-coop/docs/data --data docs/data --figs docs/figures \
        "LABEL|RAW_GLOB|PATH.csv" ...

Each path gives the -raw.csv files of uav-coop-pass (maxRun = the longest run of consecutive
packets a node received in one mission) and the flight path it was flown on. A node holds a
file of K packets in a mission only if maxRun >= K: scattered packets do not add up.
Writes DATA/runs-paths.csv (per path) and DATA/runs-nodes.csv (per path and node), and draws
runs-maps.png and runs-summary.png. With --redraw the figures come from DATA alone.
"""
import argparse, csv, glob, math, os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

INK, INK2, SURF, GRIDC = "#0b0b0b", "#52514e", "#fcfcfb", "#e6e5e1"
RAMP = LinearSegmentedColormap.from_list("ramp", ["#f1f0eb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
SERIES = ["#0d366b", "#3987e5", "#1baf7a", "#eda100", "#e34948", "#8f1d1b"]
KS = [1000, 2000]
EDGE_NB = [(0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1), (1, 0)]


def corners(cx, cy, R):
    return [(cx + R * math.cos(math.radians(30 + 60 * k)), cy + R * math.sin(math.radians(30 + 60 * k)))
            for k in range(6)]


def collect(a, nodes):
    n = len(nodes)
    xy = np.array([[float(r["x"]), float(r["y"])] for r in nodes])
    paths, per = [], []
    for spec in a.paths:
        label, raw, path = spec.split("|")
        rows = [r for f in sorted(glob.glob(raw)) for r in csv.DictReader(open(f))]
        runs = sorted({int(r["run"]) for r in rows})
        idx = {v: i for i, v in enumerate(runs)}
        M = np.full((len(runs), n), -1, dtype=np.int64)
        for r in rows:
            M[idx[int(r["run"])], int(r["id"])] = int(r["maxRun"])
        assert (M >= 0).all(), f"{label}: missing node rows"
        assert len(runs) == len(set(runs)) and len(rows) == len(runs) * n, label
        P = np.array([[float(p["x"]), float(p["y"])] for p in csv.DictReader(open(path))])
        d = np.sqrt(((xy[:, None, :] - P[None, :, :]) ** 2).sum(-1)).min(1)
        row = {"path": label, "missions": len(runs), "pathCsv": os.path.basename(path),
               "maxRunMedian": float(np.median(M)), "maxRunMax": int(M.max())}
        for K in KS:
            c = (M >= K).sum(1)
            row.update({f"full{K}Mean": c.mean(), f"full{K}Min": int(c.min()), f"full{K}Max": int(c.max()),
                        f"full{K}Ever": int((M >= K).any(0).sum()),
                        f"full{K}P95": int(((M >= K).mean(0) >= .95).sum())})
        paths.append(row)
        for i in range(n):
            per.append({"path": label, "id": nodes[i]["id"], "dPathM": f"{d[i]:.1f}",
                        "maxRunMean": f"{M[:, i].mean():.1f}", "maxRunMax": int(M[:, i].max()),
                        **{f"p{K}": f"{(M[:, i] >= K).mean():.4f}" for K in KS}})
    for name, rows in [("runs-paths.csv", paths), ("runs-nodes.csv", per)]:
        with open(os.path.join(a.data, name), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows({k: (f"{v:.2f}" if isinstance(v, float) else v) for k, v in r.items()} for r in rows)


def report(a, nodes):
    paths = list(csv.DictReader(open(os.path.join(a.data, "runs-paths.csv"))))
    per = list(csv.DictReader(open(os.path.join(a.data, "runs-nodes.csv"))))
    n = len(nodes)
    print(f"{'path':24}{'missions':>9}{'maxRun p50':>11}{'max':>6}" +
          "".join(f"{'full' + str(K) + ' mean (min-max)':>26}{'ever':>6}{'>=95%':>6}" for K in KS))
    for p in paths:
        print(f"{p['path']:24}{p['missions']:>9}{float(p['maxRunMedian']):>11.0f}{p['maxRunMax']:>6}" +
              "".join(f"{float(p[f'full{K}Mean']):>14.1f} ({p[f'full{K}Min']:>4}-{p[f'full{K}Max']:>4})"
                      f"{p[f'full{K}Ever']:>6}{p[f'full{K}P95']:>6}" for K in KS))
    lat = list(csv.DictReader(open(os.path.join(a.deploy, "deploy-lattice.csv"))))
    c = {(int(x["q"]), int(x["r"])): (float(x["cx"]), float(x["cy"])) for x in lat}
    w = math.dist(c[(0, 0)], c[(1, 0)])
    R = w / math.sqrt(3)
    sel = sorted((int(x["q"]), int(x["r"])) for x in lat if x["selected"] == "1")
    segs = [[corners(*c[h], R)[k], corners(*c[h], R)[(k + 1) % 6]]
            for h in sel for k, (dq, dr) in enumerate(EDGE_NB) if (h[0] + dq, h[1] + dr) not in sel]
    xs = [c[h][0] for h in sel]; ys = [c[h][1] for h in sel]
    nx, ny = np.array([float(r["x"]) for r in nodes]), np.array([float(r["y"]) for r in nodes])
    ch = next(r for r in nodes if r["isCH"] == "1")
    by = {p["path"]: [r for r in per if r["path"] == p["path"]] for p in paths}
    m = len(paths)
    fig, ax = plt.subplots(1, m, figsize=(4.3 * m, 6.4), dpi=150, facecolor=SURF)
    ax = np.atleast_1d(ax)
    for j, p in enumerate(paths):
        A = ax[j]
        v = np.array([float(r["p1000"]) for r in by[p["path"]]])
        A.add_collection(LineCollection(segs, colors=INK2, linewidths=.9, zorder=2))
        A.scatter(nx, ny, c=v, cmap=RAMP, vmin=0, vmax=1, s=4, lw=0, zorder=3)
        P = list(csv.DictReader(open(os.path.join(a.data, p["pathCsv"]))))
        px, py = [float(q["x"]) for q in P], [float(q["y"]) for q in P]
        A.plot(px, py, color=INK, lw=1, alpha=.8, zorder=4)
        A.annotate("", xy=(px[-1], py[-1]), xytext=(px[-25], py[-25]),
                   arrowprops=dict(arrowstyle="-|>", color=INK, lw=1), zorder=4)
        A.scatter([float(ch["x"])], [float(ch["y"])], s=80, marker="*", color="#e34948", edgecolors=INK,
                  linewidths=.5, zorder=5)
        A.set_xlim(min(xs) - w, max(xs) + w); A.set_ylim(min(ys) - w, max(ys) + w)
        A.set_aspect("equal"); A.set_facecolor(SURF); A.set_xticks([]); A.set_yticks([])
        for sp in A.spines.values():
            sp.set_visible(False)
        A.set_title(f"{p['path']}\nđủ file 1000: {float(p['full1000Mean']):.0f} node / lượt\n"
                    f"đủ file 2000: {float(p['full2000Mean']):.1f} node / lượt", loc="left", fontsize=9, color=INK)
    sm = plt.cm.ScalarMappable(cmap=RAMP, norm=plt.Normalize(0, 1))
    cb = fig.colorbar(sm, ax=list(ax), shrink=.6, pad=.01)
    cb.ax.tick_params(labelsize=7, colors=INK2); cb.outline.set_visible(False)
    cb.set_label("tỉ lệ lượt bay node nhận ≥ 1000 gói liền nhau", fontsize=8, color=INK2)
    fig.suptitle(f"Nhận đủ file khi chỉ tính các gói liền nhau — mỗi đường bay {paths[0]['missions']} lượt "
                 f"(sao: CH; mũi tên: hướng bay)", x=.01, ha="left", fontsize=12, color=INK)
    out = os.path.join(a.figs, "runs-maps.png")
    fig.savefig(out, facecolor=SURF, bbox_inches="tight"); print(f"  {out}")

    fig, ax = plt.subplots(1, 3, figsize=(17, 5), dpi=150, facecolor=SURF)
    x = np.arange(m)
    labs = [p["path"] for p in paths]
    for k, K in enumerate(KS):
        A = ax[k]
        mean = [float(p[f"full{K}Mean"]) for p in paths]
        lo = [mean[i] - int(p[f"full{K}Min"]) for i, p in enumerate(paths)]
        hi = [int(p[f"full{K}Max"]) - mean[i] for i, p in enumerate(paths)]
        A.bar(x, mean, .55, color=SERIES[k * 2], yerr=[lo, hi], ecolor=INK2, capsize=3)
        for i, v in enumerate(mean):
            A.text(i + .3, v, f"{v:.1f}", va="center", fontsize=8, color=INK)
        A.set_ylim(0, max(1, max(m_ + h_ for m_, h_ in zip(mean, hi)) * 1.1))
        A.set_title(f"Node nhận ≥ {K} gói liền nhau, mỗi lượt (/ {n})\nthanh: TB; vạch: min–max qua các lượt",
                    loc="left", fontsize=10, color=INK)
        A.set_xticks(x); A.set_xticklabels(labs, fontsize=7.5, color=INK, rotation=15)
    A = ax[2]
    bins = np.arange(0, 1300, 100)
    for j, p in enumerate(paths):
        d = np.array([float(r["dPathM"]) for r in by[p["path"]]])
        v = np.array([float(r["p1000"]) for r in by[p["path"]]])
        mid, val = [], []
        for b0 in bins[:-1]:
            s = (d >= b0) & (d < b0 + 100)
            if s.sum() >= 5:
                mid.append(b0 + 50); val.append(v[s].mean())
        A.plot(mid, val, marker="o", ms=3, lw=1.4, color=SERIES[j % len(SERIES)], label=p["path"])
    A.set_xlabel("khoảng cách ngang tới đường bay, m", fontsize=8.5, color=INK2)
    A.set_ylim(0, 1)
    A.set_title("Tỉ lệ node nhận ≥ 1000 gói liền nhau\ntheo khoảng cách tới đường bay", loc="left",
                fontsize=10, color=INK)
    A.legend(frameon=False, fontsize=7.5, labelcolor=INK2)
    for A in ax:
        A.grid(axis="y", color=GRIDC, lw=.6); A.set_facecolor(SURF)
        A.tick_params(colors=INK2, labelsize=8)
        for sp in A.spines.values():
            sp.set_visible(False)
    fig.tight_layout()
    out = os.path.join(a.figs, "runs-summary.png")
    fig.savefig(out, facecolor=SURF, bbox_inches="tight"); print(f"  {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deploy", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--figs", required=True)
    ap.add_argument("--redraw", action="store_true")
    ap.add_argument("paths", nargs="*")
    a = ap.parse_args()
    os.makedirs(a.data, exist_ok=True); os.makedirs(a.figs, exist_ok=True)
    nodes = list(csv.DictReader(open(os.path.join(a.deploy, "deploy-nodes-s35.csv"))))
    if not a.redraw:
        collect(a, nodes)
    report(a, nodes)


if __name__ == "__main__":
    main()
