"""Saturation of the proposed scheme against cluster shape (CLAUDE.md §8 item 120): tables and figures from the strip
sweep (sat_strip.py), and the shape's cost over a whole domain flown lane by lane.

    python3 tools/sat_report.py --strips "SAT/w*-s*" --out docs/data/sat --figs docs/figures

Writes:
  shapes.csv   per shape (width cells x length km) and River window (ch: one around the CH, crit: one per critical
               cell): strips, cells, critical cells, mean and last finish (s after the UAV leaves), frames per critical
               cell, MAC give-ups per 1000 frames, share of critical cells holding a full clue set (Q packets)
  crit.csv     per critical cell: its offsets from the CH along the flight and from the flight line, what it lacked
               and when it finished
  domain.csv   for each DY (--dy, a list), a DX x DY km rectangle flown in lanes of the shape's width along DX, the
               BS 1 km below its middle;
               lane ends joined by Dubins turns (radius 255 m); each cluster's critical cells ready at (the UAV
               leaves the cluster) + (their finish times on that shape): team 1's tour, and the mean and the last
               time a critical cell is ready
Figures (no text): sat-grid.png, sat-lateral.png, sat-domain.png, described in docs/SAT-vi.md.
"""
import argparse, csv, glob, json, math, os, statistics as st
from collections import defaultdict

import numpy as np

import dubins
from map_gen import W as CELLW, centre

Q = math.ceil(400e3 / 99)   # packets of the clue set
V1, RHO = 50.0, 50.0 ** 2 / 9.80665


def strips(pattern):
    out = []
    for w in sorted(sum((glob.glob(p) for p in pattern.split()), [])):   # several globs: space-separated
        if not os.path.exists(f"{w}/strip.json") or not os.path.exists(f"{w}/c1-bearing.json"):
            continue
        s = json.load(open(f"{w}/strip.json"))
        ch = next(r for r in csv.DictReader(open(f"{w}/c1-nodes-s35.csv")) if r["isCH"] == "1")
        path = np.array([[float(r["x"]), float(r["y"])] for r in csv.DictReader(open(f"{w}/c1-path-s35.csv"))])
        yline = float(np.median(path[:, 1]))
        for tag, win in (("rf", "ch"), ("rfc", "crit")):
            f = f"{w}/r1-{tag}-runs.csv"
            if not os.path.exists(f) or len(open(f).readlines()) < 2:
                continue
            run = next(csv.DictReader(open(f)))
            crit = []
            for c in csv.DictReader(open(f"{w}/r1-{tag}-crit.csv")):
                x, y = centre((int(c["q"]), int(c["r"])))
                crit.append(dict(along=x - float(ch["x"]), lateral=y - yline, D=int(c["D"]), lackCL=int(c["lackCL"]),
                                 lackCell=int(c["lackCell"]), done=float(c["doneS"]), missing=int(c["missing"])))
            out.append(dict(width=s["width"], length=s["length"], seed=s["seed"], cells=s["cells"], window=win,
                            hops=int(run["hops"]), macFail=int(run["macFail"]), wallS=float(run["wallS"]), crit=crit))
    return out


def shapes(rows):
    g = defaultdict(list)
    for r in rows:
        g[(r["width"], r["length"], r["window"])].append(r)
    out = []
    for (w, l, win), rs in sorted(g.items()):
        done = [[c["done"] for c in r["crit"] if c["done"] >= 0] for r in rs]
        unfinished = sum(1 for r in rs for c in r["crit"] if c["done"] < 0)
        out.append(dict(width=w, length=l, window=win, strips=len(rs), cells=st.mean(r["cells"] for r in rs),
                        crit=st.mean(len(r["crit"]) for r in rs),
                        doneMean=st.mean(st.mean(d) for d in done if d),
                        doneMax=st.mean(max(d) for d in done if d), unfinished=unfinished,
                        framesPerCrit=st.mean(r["hops"] / max(1, len(r["crit"])) for r in rs),
                        macPerK=st.mean(1000 * r["macFail"] / max(1, r["hops"]) for r in rs),
                        fullClue=st.mean(c["D"] >= Q for r in rs for c in r["crit"]),
                        wallS=st.mean(r["wallS"] for r in rs)))
    return out


def domain(shape_rows, dx, dy):
    """Team 1 flies lanes of the shape's width along x across a dx x dy km rectangle, boustrophedon; every lane is cut
    into clusters of the shape's length. A cluster's critical cells are ready at (UAV leaves it) + their finish times."""
    out = []
    for s in shape_rows:
        wm = s["width"] * CELLW
        lanes = math.ceil(dy * 1000 / wm)
        per = max(1, round(dx / s["length"]))
        bs = (dx * 500.0, -1000.0)
        t, legs = 0.0, []
        for i in range(lanes):
            y = (i + 0.5) * wm
            x0, x1, hd = (0.0, dx * 1000, 0.0) if i % 2 == 0 else (dx * 1000, 0.0, math.pi)
            if i == 0:
                t += dubins.free_start(bs, (x0, y, hd), RHO) / V1
            else:
                t += dubins.length(prev, (x0, y, hd), RHO) / V1
            for j in range(per):
                t += dx * 1000 / per / V1
                legs.append(t)
            prev = (x1, y, hd)
        back = t + dubins.free_end(prev, bs, RHO) / V1
        # finish times of this shape's critical cells, pooled over its strips
        out.append(dict(dy=dy, width=s["width"], length=s["length"], window=s["window"], lanes=lanes, clusters=len(legs),
                        tour=round(back, 1), lastLeave=round(legs[-1], 1),
                        readyMean=round(st.mean(legs) + s["doneMean"], 1), readyLast=round(legs[-1] + s["doneMax"], 1),
                        critTotal=round(len(legs) * s["crit"] * (dx * 1000 / per) / (s["length"] * 1000), 1)))
    return out


def figures(shape_rows, rows, dom, figs):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    INK, SOFT = "#1b2a33", "#d6e0e5"
    Ws = sorted({s["width"] for s in shape_rows})
    Ls = sorted({s["length"] for s in shape_rows})
    pick = lambda win, key: np.array([[next((s[key] for s in shape_rows if s["width"] == w and s["length"] == l
                                             and s["window"] == win), np.nan) for l in Ls] for w in Ws])
    fig, ax = plt.subplots(1, 4, figsize=(16, 4))
    for a, (win, key, cmap) in zip(ax, [("crit", "doneMax", "Blues"), ("crit", "framesPerCrit", "Purples"),
                                         ("crit", "fullClue", "Greens"), ("ch", "doneMax", "Oranges")]):
        a.imshow(pick(win, key), origin="lower", cmap=cmap, aspect="auto")
        a.set_xticks(range(len(Ls)))
        a.set_yticks(range(len(Ws)))
        a.set_xticklabels([])
        a.set_yticklabels([])
        for sp in a.spines.values():
            sp.set_color(SOFT)
    fig.tight_layout()
    fig.savefig(f"{figs}/sat-grid.png", dpi=130)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    cols = plt.cm.viridis(np.linspace(0.1, 0.9, len(Ws)))
    for w, col in zip(Ws, cols):
        pts = [(abs(c["lateral"]), c["done"]) for r in rows if r["window"] == "crit" and r["width"] == w
               for c in r["crit"] if c["done"] >= 0]
        if pts:
            ax.scatter(*zip(*pts), s=10, color=col, alpha=.7)
    ax.set_xticks(range(0, 1601, 200))
    ax.set_yticks(range(0, 61, 10))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid(color=SOFT, lw=.6)
    fig.tight_layout()
    fig.savefig(f"{figs}/sat-lateral.png", dpi=130)
    plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.2))
    cl = plt.cm.cividis(np.linspace(0.1, 0.9, len(Ls)))
    for l, col in zip(Ls, cl):
        d = sorted((x for x in dom if x["window"] == "crit" and x["length"] == l and x["dy"] == dom[0]["dy"]),
                   key=lambda x: x["width"])
        ax[0].plot([x["width"] for x in d], [x["readyMean"] for x in d], "-o", color=col, ms=4)
        ax[1].plot([x["width"] for x in d], [x["readyLast"] for x in d], "-o", color=col, ms=4)
    for a in ax:
        a.set_xticklabels([])
        a.set_yticklabels([])
        a.grid(color=SOFT, lw=.6)
    fig.tight_layout()
    fig.savefig(f"{figs}/sat-domain.png", dpi=130)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strips", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--figs")
    ap.add_argument("--dx", type=float, default=6.0, help="domain km along the lanes")
    ap.add_argument("--dy", default="4", help="domain km across the lanes; a comma-separated list for several")
    a = ap.parse_args()
    rows = strips(a.strips)
    sh = shapes(rows)
    dom = [d for dy in a.dy.split(",") for d in domain(sh, a.dx, float(dy))]
    os.makedirs(a.out, exist_ok=True)
    for name, data in (("shapes", sh), ("domain", dom)):
        with open(f"{a.out}/{name}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, list(data[0]))
            w.writeheader()
            w.writerows({k: round(v, 3) if isinstance(v, float) else v for k, v in d.items()} for d in data)
    with open(f"{a.out}/crit.csv", "w", newline="") as f:
        f.write("width,length,seed,window,along,lateral,D,lackCL,lackCell,done,missing\n")
        for r in rows:
            for c in r["crit"]:
                f.write(f"{r['width']},{r['length']},{r['seed']},{r['window']},{c['along']:.0f},{c['lateral']:.0f},"
                        f"{c['D']},{c['lackCL']},{c['lackCell']},{c['done']},{c['missing']}\n")
    if a.figs:
        figures(sh, rows, dom, a.figs)
    print(f"{len(rows)} strip runs, {len(sh)} shape x window rows -> {a.out}")


if __name__ == "__main__":
    main()
