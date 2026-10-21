"""Layer-2 diagnosis (CLAUDE.md §8 item 115): why the restructured partitions lose on T*. Per map and partition,
from the ns-3 mission folders already run (no new simulation):
  clusters, critical cells, land cells
  tour      team 1's latency tour (as P*) and its shortest tour: time broadcasting inside clusters (pass),
            flying between clusters and from the BS (transit), back to the BS (return)
  data      per cluster: Axe packets, D (packets heard by some node of the cluster); clusters whose Axe holds the
            whole clue set (Q packets)
  reach     per land cell of a cluster: share of the cluster's D its own nodes heard (penetration); cells that
            heard >= 50 % / >= 90 %; from its own reception (any complete copy of a clue): the clue weight it
            holds (mean, and cells with >= 50 %), cells holding every clue
  River     when the last critical cell of the map has its River data (leave + doneS, latency tour)

    python3 tools/l2_diag.py --set kmedoids "KW/k*" --set meander "MW/k*" --set subch "SW/k*" \
        --out docs/data/l2diag/diag --figs docs/figures --map k6-s4

Writes OUT-maps.csv, prints means per size; with --figs, FIGS/l2-diag.png (no text, item 63): per size and
partition, (1) team 1's latency tour as pass / transit / return, stacked, (2) the share of land cells that heard
>= 50 % of their cluster's D (full bar) and that hold every clue from their own reception (dark mark),
(3) clusters and critical cells per map; and FIGS/l2-diag-<map>.png: that map once per partition, cells shaded
by the share of D they heard (white 0 -> dark 1), flight lines black, transits dashed, the BS a black square.
"""
import argparse, csv, glob, os
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import numpy as np

import l1_model as L
import l1_rank as R
from map_gen import strip_text
from mission_policy import tour
from mission_report import GREY, INK, SURF, load_map

COL = {"kmedoids": "#1c5cab", "subch": "#8a59cf", "meander": "#2f9e6e"}


def diag(M, C, seqs, Q):
    out = dict(clusters=len(M["cl"]), crit=sum(len(cl["P"]["crit"]) for cl in M["cl"].values()),
               cells=sum(len(cl["geo"]["cells"]) for cl in M["cl"].values()))
    for kind in ("latency", "short"):
        legs, back = tour(M, kind)
        prev, transit = 0.0, 0.0
        for l in legs:
            transit += l[3] - prev
            prev = l[4]
        out[kind] = dict(back=back, pass_=sum(l[4] - l[3] for l in legs), transit=transit, ret=back - legs[-1][4])
    legs, _ = tour(M, "latency")
    leave = {l[0]: l[4] for l in legs}
    axe, D, held, allclue, clueW = [], [], [], [], []
    w = np.array([c["w"] for c in C])
    for k, cl in M["cl"].items():
        P = cl["P"]
        axe.append(len({s for x in P["axe"] for s in P["seg"][x]}))
        D.append(cl["D"])
        held += [cl["held"][h] for h in cl["geo"]["cells"] if h in cl["held"]]
        # every cell with nodes, as if it were critical: clues held from its own reception
        cells = [h for h in cl["geo"]["cells"] if h in cl["mem"]]
        one = dict(M, cl={k: dict(cl, P=dict(P, crit=cells))})
        hold = R.holdings(one, C, seqs)
        allclue += [bool(hold[(k, h)]["interleaved"][1].all()) for h in cells]
        clueW += [float(w[hold[(k, h)]["interleaved"][1]].sum() / w.sum()) for h in cells]
    held = np.array(held)
    out.update(axeMean=float(np.mean(axe)), axeFull=float(np.mean([a >= Q for a in axe])), Dmean=float(np.mean(D)),
               Dsum=float(np.sum(D)), reach=float(held.mean()), reach50=float(np.mean(held >= .5)),
               reach90=float(np.mean(held >= .9)), allDirect=float(np.mean(allclue)),
               clueW=float(np.mean(clueW)), clueW50=float(np.mean(np.array(clueW) >= .5)),
               riverAll=max(leave[k] + max(float(r["doneS"]) for r in cl["res"]["rf"].values())
                            for k, cl in M["cl"].items()))
    return out


def flat(name, sname, d):
    row = dict(map=name, size=int(name.split("-")[0][1:]), set=sname)
    for k, v in d.items():
        if isinstance(v, dict):
            row.update({f"{k}_{kk.rstrip('_')}": round(vv, 1) for kk, vv in v.items()})
        else:
            row[k] = round(v, 4) if isinstance(v, float) else v
    return row


def hexpoly(x, y, R=100, s=0.96):
    return [(x + R * s * np.cos(np.radians(30 + 60 * i)), y + R * s * np.sin(np.radians(30 + 60 * i))) for i in range(6)]


def map_figure(Ms, path):
    fig, axs = plt.subplots(1, len(Ms), figsize=(6.2 * len(Ms), 6.2), dpi=140, facecolor=SURF)
    blues = matplotlib.colormaps["Blues"]
    for ax, (sname, M) in zip(np.atleast_1d(axs), Ms):
        polys, cols = [], []
        for k, cl in M["cl"].items():
            for h in cl["geo"]["cells"]:
                polys.append(hexpoly(*cl["geo"]["c"][h]))
                cols.append(blues(0.08 + 0.92 * cl["held"].get(h, 0.0)))
        ax.add_collection(PolyCollection(polys, facecolors=cols, edgecolors=SURF, linewidths=.3, zorder=0))
        legs, back = tour(M, "latency")
        pos = M["bs"]
        for l in legs:
            ax.plot([pos[0], l[1][0]], [pos[1], l[1][1]], color=INK, lw=.9, ls=(0, (3, 2)), zorder=3)
            p = M["cl"][l[0]]["geo"]["path"]
            ax.plot(p[:, 0], p[:, 1], color=INK, lw=1.6, zorder=4)
            pos = l[2]
        ax.plot([pos[0], M["bs"][0]], [pos[1], M["bs"][1]], color=INK, lw=.9, ls=(0, (3, 2)), zorder=3)
        ax.scatter(*M["bs"], s=70, marker="s", color=INK, zorder=6)
        for k, cl in M["cl"].items():
            for h in cl["P"]["crit"]:
                ax.scatter(*cl["geo"]["c"][h], s=28, facecolor=SURF, edgecolor=INK, lw=.9, zorder=5)
        ax.set_aspect("equal")
        ax.autoscale_view()
        ax.axis("off")
    strip_text(fig)
    fig.savefig(path, facecolor=SURF, bbox_inches="tight", pad_inches=.05)
    plt.close(fig)


def summary_figure(rows, sets, path):
    sizes = sorted({r["size"] for r in rows})
    fig, axs = plt.subplots(1, 3, figsize=(17, 4.6), dpi=150, facecolor=SURF, gridspec_kw=dict(width_ratios=[1.3, 1, 1]))
    n = len(sets)
    bw = 0.8 / n
    for j, sz in enumerate(sizes):
        for i, s in enumerate(sets):
            rs = [r for r in rows if r["size"] == sz and r["set"] == s]
            if not rs:
                continue
            x = j + (i - (n - 1) / 2) * bw
            c = COL.get(s, "#52514e")
            m = lambda key: np.mean([r[key] for r in rs])
            b = 0.0
            for key, a in (("latency_pass", 1.0), ("latency_transit", .55), ("latency_ret", .25)):
                axs[0].bar(x, m(key), bottom=b, width=bw * .9, color=matplotlib.colors.to_rgba(c, a), edgecolor="none")
                b += m(key)
            axs[1].bar(x, m("reach50"), width=bw * .9, color=matplotlib.colors.to_rgba(c, .35), edgecolor="none")
            axs[1].bar(x, m("allDirect"), width=bw * .9, color=c, edgecolor="none")
            axs[2].bar(x, m("crit"), width=bw * .9, color=matplotlib.colors.to_rgba(c, .35), edgecolor="none")
            axs[2].bar(x, m("clusters"), width=bw * .9, color=c, edgecolor="none")
    for ax in axs:
        ax.set_xticks(range(len(sizes)))
        ax.set_ylim(0, None)
        ax.grid(axis="y", color=GREY, lw=.6)
        ax.set_axisbelow(True)
        ax.set_facecolor(SURF)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    axs[1].set_ylim(0, 1)
    strip_text(fig)
    fig.savefig(path, facecolor=SURF, bbox_inches="tight", pad_inches=.06)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", nargs=2, action="append", metavar=("NAME", "GLOB"), required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--figs", default="")
    ap.add_argument("--map", default="", help="also draw this map once per partition")
    a = ap.parse_args()
    C = L.clues()
    seqs = {"interleaved": L.order(C, "interleaved")}
    Q = L.layout(C, seqs["interleaved"])[2]
    rows, keep = [], []
    for sname, g in a.set:
        for w in sorted(w for w in glob.glob(g) if R.complete(w)):
            M = load_map(w, schemes=("rf",))
            name = R.mapname(w)
            rows.append(flat(name, sname, diag(M, C, seqs, Q)))
            if name == a.map:
                keep.append((sname, M))
            print(sname, name, flush=True)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out + "-maps.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    sets = [s for s, _ in a.set]
    keys = [k for k in rows[0] if k not in ("map", "size", "set")]
    by = defaultdict(list)
    for r in rows:
        by[(r["set"], r["size"])].append(r)
    for k in keys:
        print(f"{k:18s}" + "  ".join(f"{s}: " + " / ".join(f"{np.mean([r[k] for r in by[(s, z)]]):.3g}"
                                                          for z in sorted({r['size'] for r in rows}))
                                      for s in sets))
    if a.figs:
        summary_figure(rows, sets, f"{a.figs}/l2-diag.png")
        if keep:
            map_figure(keep, f"{a.figs}/l2-diag-{a.map}.png")


if __name__ == "__main__":
    main()
