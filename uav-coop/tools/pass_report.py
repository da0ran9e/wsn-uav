"""Step 3 report: merge uav-coop-pass missions, summarise per node, draw the figures.

    python3 tools/pass_report.py --raw "pass*-raw.csv" --geom pass1-nodes.csv \
        --strip pass1-strip.csv --track pass1-track.csv --lattice deploy-lattice.csv \
        --data docs/data --figs docs/figures

--raw     one or more -raw.csv files (missions may be split over processes)
--geom    a -nodes.csv of the same deployment (positions, CH, distance to the path)
Writes DATA/pass-nodes.csv (per node over all missions) and DATA/pass-bins.csv (per
100 m of distance from the path), copies the strip and track, and draws
pass-map.png, pass-distance.png, pass-strip.png. With --redraw the figures are drawn
from DATA alone.
"""
import argparse, csv, glob, math, os, shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
import numpy as np

INK, INK2, SURF = "#0b0b0b", "#52514e", "#fcfcfb"
C_CH, C_GOT, C_LOST = "#e34948", "#2a78d6", "#e34948"
RAMP = LinearSegmentedColormap.from_list("ramp", ["#f1f0eb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
K_C = {200: "#86b6ef", 500: "#3987e5", 1000: "#1c5cab", 2000: "#0d366b"}
KS = [50, 100, 200, 500, 1000, 2000]


def corners(cx, cy, R):
    return [(cx + R * math.cos(math.radians(30 + 60 * k)), cy + R * math.sin(math.radians(30 + 60 * k)))
            for k in range(6)]


EDGE_NB = [(0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1), (1, 0)]


def outline(lat):
    c = {(int(x["q"]), int(x["r"])): (float(x["cx"]), float(x["cy"])) for x in lat}
    w = math.dist(c[(0, 0)], c[(1, 0)])
    sel = {(int(x["q"]), int(x["r"])) for x in lat if x["selected"] == "1"}
    segs = []
    for q, r in sel:
        v = corners(*c[(q, r)], w / math.sqrt(3))
        for k, (dq, dr) in enumerate(EDGE_NB):
            if (q + dq, r + dr) not in sel:
                segs.append([v[k], v[(k + 1) % 6]])
    return segs


def style(ax):
    ax.set_facecolor(SURF)
    ax.tick_params(colors=INK2, labelsize=8)
    for s in ax.spines.values():
        s.set_visible(False)


def merge(o):
    geom = {r["id"]: r for r in csv.DictReader(open(o.geom))}
    per = {i: [] for i in geom}
    runs = set()
    for f in sorted(glob.glob(o.raw)):
        for r in csv.DictReader(open(f)):
            per[r["id"]].append(r)
            runs.add(int(r["run"]))
    n = len(runs)
    assert runs == set(range(1, n + 1)), "missions must be 1..N, each once"
    for i, rows in per.items():
        assert len(rows) == n and len({r["run"] for r in rows}) == n, i
    out = []
    for i, g in geom.items():
        rx = np.array([int(r["rx"]) for r in per[i]], float)
        mr = np.array([int(r["maxRun"]) for r in per[i]], float)
        row = {"id": i, "x": g["x"], "y": g["y"], "isCH": g["isCH"], "dPathM": g["dPathM"],
               "missions": n, "rxMean": f"{rx.mean():.2f}", "rxP10": f"{np.percentile(rx, 10):.1f}",
               "rxP50": f"{np.percentile(rx, 50):.1f}", "rxP90": f"{np.percentile(rx, 90):.1f}",
               "runMean": f"{mr.mean():.2f}", "runP10": f"{np.percentile(mr, 10):.1f}",
               "runP50": f"{np.percentile(mr, 50):.1f}"}
        for K in KS:
            cov = np.array([int(r[f"cov{K}"]) for r in per[i]], float)
            row[f"pDone{K}"] = f"{(cov == K).mean():.4f}"
            row[f"covMean{K}"] = f"{cov.mean():.2f}"
        out.append(row)
    with open(os.path.join(o.data, "pass-nodes.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    # per 100 m of distance from the path
    bins = []
    for lo in range(0, 3000, 100):
        sel = [r for r in out if lo <= float(r["dPathM"]) < lo + 100]
        if not sel:
            continue
        b = {"loM": lo, "hiM": lo + 100, "nodes": len(sel),
             "rxMean": f"{np.mean([float(r['rxMean']) for r in sel]):.1f}",
             "runMean": f"{np.mean([float(r['runMean']) for r in sel]):.1f}"}
        for K in KS:
            b[f"pDone{K}"] = f"{np.mean([float(r[f'pDone{K}']) for r in sel]):.4f}"
        bins.append(b)
    with open(os.path.join(o.data, "pass-bins.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(bins[0]))
        w.writeheader()
        w.writerows(bins)
    shutil.copy(o.strip, os.path.join(o.data, "pass-strip.csv"))
    shutil.copy(o.track, os.path.join(o.data, "pass-track.csv"))
    print(f"{n} missions, {len(out)} nodes -> {o.data}/pass-nodes.csv, pass-bins.csv")
    print(f"{'dist':>11} {'nodes':>6} {'rx':>6} {'run':>6} " + " ".join(f"{'done' + str(K):>9}" for K in KS))
    for b in bins:
        print(f"{b['loM']:>4}-{b['hiM']:>4} m {b['nodes']:>6} {float(b['rxMean']):>6.0f} {float(b['runMean']):>6.0f} "
              + " ".join(f"{100 * float(b[f'pDone{K}']):>8.1f}%" for K in KS))


def load_track(data):
    tr = list(csv.DictReader(open(os.path.join(data, "pass-track.csv"))))
    X = np.array([float(r["x"]) for r in tr]); Y = np.array([float(r["y"]) for r in tr])
    part = np.array([int(r["part"]) for r in tr])
    return X, Y, part


def fig_map(data, lat, out):
    nd = list(csv.DictReader(open(os.path.join(data, "pass-nodes.csv"))))
    X, Y, part = load_track(data)
    nPk = len(X)
    segs = outline(lat)
    x = np.array([float(r["x"]) for r in nd]); y = np.array([float(r["y"]) for r in nd])
    panels = [("rxMean", f"gói nhận được (TB {nd[0]['missions']} lượt bay), trên {nPk:,} gói phát", 0, nPk, "{:,.0f}"),
              ("pDone1000", "xác suất nhận đủ file K = 1 000 gói", 0, 1, "{:.0%}"),
              ("pDone2000", "xác suất nhận đủ file K = 2 000 gói", 0, 1, "{:.0%}")]
    fig, ax = plt.subplots(1, 3, figsize=(17, 7.2), dpi=150, facecolor=SURF)
    for a, (col, title, lo, hi, fmt) in zip(ax, panels):
        v = np.array([float(r[col]) for r in nd])
        sc = a.scatter(x, y, c=v, cmap=RAMP, vmin=lo, vmax=hi, s=7, lw=0, zorder=2)
        a.add_collection(LineCollection(segs, colors=INK2, linewidths=.9, zorder=3))
        inside = part > 0
        a.plot(X, Y, color=INK, lw=1.2, zorder=4)
        for t in range(150, nPk, 800):
            a.annotate("", (X[t + 1], Y[t + 1]), (X[t - 1], Y[t - 1]),
                       arrowprops=dict(arrowstyle="-|>", color=INK, lw=0, mutation_scale=11), zorder=5)
        ch = [r for r in nd if r["isCH"] == "1"][0]
        a.scatter([float(ch["x"])], [float(ch["y"])], s=230, marker="*", color=C_CH, edgecolors=INK,
                  linewidths=.8, zorder=6)
        a.annotate(f"CH #{ch['id']}", (float(ch["x"]), float(ch["y"])), xytext=(9, 6),
                   textcoords="offset points", fontsize=8, color=INK, zorder=7,
                   bbox=dict(boxstyle="round,pad=.15", fc=SURF, ec="none", alpha=.85))
        a.set_aspect("equal")
        a.set_title(title, loc="left", fontsize=10, color=INK)
        cb = fig.colorbar(sc, ax=a, shrink=.7, pad=.02)
        cb.ax.tick_params(labelsize=8, colors=INK2)
        cb.outline.set_visible(False)
        if hi == 1:
            cb.ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
        style(a)
    fig.suptitle("UAV bay đường vào → CH → ra ở 100 m, 50 m/s, phát 1 gói 127 B mỗi 10 ms (+10 dBm, α = 3.0, "
                 "Rician K = 2) — mỗi chấm là một node", x=.01, ha="left", fontsize=12, color=INK)
    fig.tight_layout(rect=(0, 0, 1, .95))
    fig.savefig(out, facecolor=SURF)
    print(f"  {out}")


def fig_distance(data, out):
    nd = list(csv.DictReader(open(os.path.join(data, "pass-nodes.csv"))))
    X, _, _ = load_track(data)
    nPk = len(X)
    d = np.array([float(r["dPathM"]) for r in nd])
    edges = np.arange(0, d.max() + 50, 50)
    mid = (edges[:-1] + edges[1:]) / 2
    fig, ax = plt.subplots(1, 2, figsize=(15, 5.6), dpi=150, facecolor=SURF)
    a = ax[0]
    a.scatter(d, [float(r["rxMean"]) for r in nd], s=3, color="#b9b8b2", lw=0, zorder=2,
              label="từng node (TB các lượt bay)")
    m, p10, p90 = [], [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        s = [r for r in nd if lo <= float(r["dPathM"]) < hi]
        m.append(np.mean([float(r["rxMean"]) for r in s]) if s else np.nan)
        p10.append(np.mean([float(r["rxP10"]) for r in s]) if s else np.nan)
        p90.append(np.mean([float(r["rxP90"]) for r in s]) if s else np.nan)
    a.fill_between(mid, p10, p90, color=C_GOT, alpha=.18, lw=0, zorder=1, label="P10–P90 giữa các lượt bay")
    a.plot(mid, m, color=C_GOT, lw=2.2, zorder=3, label="trung bình mỗi 50 m")
    a.axhline(nPk, color=INK2, lw=.8, ls=(0, (3, 3)))
    a.text(d.max(), nPk, f"phát {nPk:,} gói", ha="right", va="bottom", fontsize=8, color=INK2)
    a.set_xlabel("khoảng cách ngang từ node tới đường bay, m", fontsize=9, color=INK2)
    a.set_ylabel("gói nhận được", fontsize=9, color=INK2)
    a.set_title("Số gói nhận được theo khoảng cách tới đường bay", loc="left", fontsize=10.5, color=INK)
    a.legend(frameon=False, fontsize=8.5, labelcolor=INK2)
    a.grid(color="#e6e5e1", lw=.6)
    style(a)
    a = ax[1]
    for K, c in K_C.items():
        p = []
        for lo, hi in zip(edges[:-1], edges[1:]):
            s = [float(r[f"pDone{K}"]) for r in nd if lo <= float(r["dPathM"]) < hi]
            p.append(np.mean(s) if s else np.nan)
        a.plot(mid, p, color=c, lw=2.2, label=f"K = {K:,}")
    a.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    a.set_xlabel("khoảng cách ngang từ node tới đường bay, m", fontsize=9, color=INK2)
    a.set_ylabel("tỉ lệ nhận đủ file", fontsize=9, color=INK2)
    a.set_title("Xác suất nhận đủ một file K gói phát vòng (gói s mang mảnh s mod K)", loc="left",
                fontsize=10.5, color=INK)
    a.legend(frameon=False, fontsize=8.5, labelcolor=INK2)
    a.grid(color="#e6e5e1", lw=.6)
    style(a)
    fig.tight_layout()
    fig.savefig(out, facecolor=SURF)
    print(f"  {out}")


def fig_strip(data, out):
    st = list(csv.DictReader(open(os.path.join(data, "pass-strip.csv"))))
    nd = {r["id"]: r for r in csv.DictReader(open(os.path.join(data, "pass-nodes.csv")))}
    X, Y, part = load_track(data)
    nPk = int(st[0]["packets"])
    chId = [i for i, r in nd.items() if r["isCH"] == "1"][0]
    pick = [chId]
    for target in (150, 300, 450, 600, 750, 900):
        best = min((r for r in st if r["id"] not in pick), key=lambda r: abs(float(r["dPathM"]) - target))
        pick.append(best["id"])
    rows = {r["id"]: r for r in st}
    img = []
    for i in pick:
        hx = rows[i]["bitsHex"]
        bits = [(int(c, 16) >> (3 - b)) & 1 for c in hx for b in range(4)][:nPk]
        img.append(bits)
    img = np.array(img)
    fig, ax = plt.subplots(figsize=(16, 4.6), dpi=150, facecolor=SURF)
    ax.imshow(img, aspect="auto", interpolation="nearest", cmap=ListedColormap([C_LOST, C_GOT]),
              extent=(0, nPk * 0.01, len(pick) - .5, -.5))
    for k in range(1, len(pick)):
        ax.axhline(k - .5, color=SURF, lw=3)
    labels = []
    for i in pick:
        got = sum(img[pick.index(i)])
        tag = "CH " if i == chId else ""
        labels.append(f"{tag}#{i} · {float(rows[i]['dPathM']):.0f} m · {got:,} gói")
    ax.set_yticks(range(len(pick)))
    ax.set_yticklabels(labels, fontsize=8.5, color=INK)
    for p, lab in ((1, "vào cụm"), (2, "qua CH"), (3, "ra khỏi cụm")):
        t = np.argmax(part >= p) * 0.01
        ax.axvline(t, color=INK, lw=1, ls=(0, (3, 2)))
        ax.text(t, -.75, lab, ha="center", va="bottom", fontsize=8.5, color=INK)
    ax.set_xlabel("thời điểm phát, s (một ô = một gói, 10 ms)", fontsize=9, color=INK2)
    ax.set_title(f"Gói nhận được (xanh) và mất (đỏ) trong lượt bay 1, các node ở khoảng cách khác nhau tới "
                 f"đường bay", loc="left", fontsize=10.5, color=INK, pad=18)
    style(ax)
    fig.tight_layout()
    fig.savefig(out, facecolor=SURF)
    print(f"  {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw"); ap.add_argument("--geom"); ap.add_argument("--strip"); ap.add_argument("--track")
    ap.add_argument("--lattice", required=True)
    ap.add_argument("--data", required=True); ap.add_argument("--figs", required=True)
    ap.add_argument("--redraw", action="store_true")
    o = ap.parse_args()
    os.makedirs(o.data, exist_ok=True); os.makedirs(o.figs, exist_ok=True)
    if not o.redraw:
        merge(o)
    lat = list(csv.DictReader(open(o.lattice)))
    fig_map(o.data, lat, os.path.join(o.figs, "pass-map.png"))
    fig_distance(o.data, os.path.join(o.figs, "pass-distance.png"))
    fig_strip(o.data, os.path.join(o.figs, "pass-strip.png"))


if __name__ == "__main__":
    main()
