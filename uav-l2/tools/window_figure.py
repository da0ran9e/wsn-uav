"""The River window on one strip (CLAUDE.md §8 item 122): one window of the clue set around the CH for every
critical cell, against one window per critical cell (the copy nearest to it), and what each did to the finish times.

    python3 tools/window_figure.py --strip SAT/w6-l4-s1 --out docs/figures/river-window.png

Three rows sharing the x axis (metres along the flight), no text (§8 item 63):
  1 the strip: cells, Axe, flight line, the CH (star) and the other critical cells (dots), each joined to the
    point where the UAV passes closest to it; colour = position along the flight
  2 the Axe's packet stream: all Axe packets (grey), the window around the CH (dark), then one bar per critical
    cell for its own window, in the same colours
  3 finish time of each critical cell (s after the UAV leaves): open = CH window, filled = own window
"""
import argparse, csv

import numpy as np

from map_gen import corners


def read(w):
    lat = {(int(r["q"]), int(r["r"])): (float(r["cx"]), float(r["cy"])) for r in csv.DictReader(open(f"{w}/c1-lattice.csv"))
           if r["selected"] == "1"}
    plan = [l.split() for l in open(f"{w}/plan1-crit.txt")]
    axe_ch = [(int(p[1]), int(p[2]), int(p[3]), int(p[4])) for p in (l.split() for l in open(f"{w}/plan1.txt")) if p[0] == "AXE"]
    axe_all = [(int(p[1]), int(p[2]), int(p[3]), int(p[4])) for p in plan if p[0] == "AXE"]
    need = {(int(p[1]), int(p[2])): (int(p[3]), int(p[4])) for p in plan if p[0] == "NEED"}
    track = np.array([[float(r["x"]), float(r["y"])] for r in csv.DictReader(open(f"{w}/pass1-track.csv"))])
    ch = next(r for r in csv.DictReader(open(f"{w}/c1-nodes-s35.csv")) if r["isCH"] == "1")
    done = {}
    for tag in ("rf", "rfc"):
        for r in csv.DictReader(open(f"{w}/r1-{tag}-crit.csv")):
            done.setdefault((int(r["q"]), int(r["r"])), {})[tag] = float(r["doneS"])
    return lat, axe_ch, axe_all, need, track, (int(ch["q"]), int(ch["r"])), done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strip", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    lat, axe_ch, axe_all, need, track, ch, done = read(a.strip)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon
    INK, SOFT, GREY, AXE = "#1b2a33", "#d6e0e5", "#e4e4e1", "#1f5aa6"
    crit = sorted(need, key=lambda h: lat[h][0])
    near = {h: int(np.argmin(np.linalg.norm(track - lat[h], axis=1))) for h in crit}
    cmap = plt.cm.viridis
    xs = [lat[h][0] for h in crit]
    col = {h: cmap(0.08 + 0.84 * (lat[h][0] - min(xs)) / max(1.0, max(xs) - min(xs))) for h in crit}
    axe_cells = {(q, r) for q, r, _, _ in axe_all}
    px = track[:, 0]
    x0, x1 = min(x for x, _ in lat.values()) - 120, max(x for x, _ in lat.values()) + 120

    fig, ax = plt.subplots(3, 1, figsize=(12, 7.8), sharex=True, gridspec_kw=dict(height_ratios=[2.8, 1.6, 1.4]))
    m = ax[0]
    for h, (cx, cy) in lat.items():
        m.add_patch(Polygon(corners(h), closed=True, fc=AXE if h in axe_cells else GREY, ec="white", lw=.8))
    m.plot(track[:, 0], track[:, 1], color="#8a8f93", lw=1.2)
    for h in crit:
        p = track[near[h]]
        m.plot([lat[h][0], p[0]], [lat[h][1], p[1]], color=col[h], lw=1.4, ls=(0, (2, 2)))
        if h == ch:
            m.scatter(*lat[h], marker="*", s=380, color=col[h], edgecolor=INK, lw=.9, zorder=5)
        else:
            m.scatter(*lat[h], s=110, color=col[h], edgecolor=INK, lw=.9, zorder=5)
    m.set_aspect("equal", adjustable="datalim")
    m.axis("off")

    b = ax[1]
    lo, hi = min(s for *_, s, _ in axe_ch), max(e for *_, e in axe_ch)
    rows = len(crit) + 2
    bar = lambda y, s, e, c, h=.62: b.add_patch(plt.Rectangle((px[s], y - h / 2), px[e] - px[s], h, fc=c, ec="none"))
    # all packets sent above the cluster, then the CH window
    s_all = min(s for *_, s, _ in axe_all)
    e_all = max(e for *_, e in axe_all)
    bar(rows - 1, s_all, e_all, GREY)
    bar(rows - 2, lo, hi, INK)
    for i, h in enumerate(crit):
        s, e = need[h]
        bar(rows - 3 - i, s, e, col[h])
        b.scatter(px[near[h]], rows - 3 - i, s=16, color="white", edgecolor=INK, lw=.6, zorder=4)
    b.set_ylim(-.8, rows - .2)
    b.set_yticks([])
    b.tick_params(length=0)
    for sp in b.spines.values():
        sp.set_visible(False)

    t = ax[2]
    for h in crit:
        x = lat[h][0]
        f, c_ = done[h].get("rf"), done[h].get("rfc")
        t.plot([x, x], [c_, f], color=col[h], lw=1.6)
        t.scatter(x, f, s=70, facecolor="white", edgecolor=col[h], lw=1.8, zorder=4, marker="*" if h == ch else "o")
        t.scatter(x, c_, s=70, color=col[h], edgecolor=INK, lw=.6, zorder=5, marker="*" if h == ch else "o")
    t.set_ylim(0, max(max(v.values()) for v in done.values()) * 1.08)
    t.set_yticks(range(0, int(t.get_ylim()[1]) + 1, 20))
    t.set_yticklabels([])
    t.set_xticks(np.arange(0, x1, 500))
    t.set_xticklabels([])
    t.grid(color=SOFT, lw=.6)
    for sp in ("top", "right"):
        t.spines[sp].set_visible(False)
    t.set_xlim(x0, x1)
    fig.tight_layout()
    fig.savefig(a.out, dpi=130)
    print(f"{len(crit)} critical cells; CH window {lo}-{hi}; " +
          "; ".join(f"{h}: {need[h][0]}-{need[h][1]} ch {done[h].get('rf')} s own {done[h].get('rfc')} s" for h in crit))


if __name__ == "__main__":
    main()
