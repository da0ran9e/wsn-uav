"""MEANDER lane width against k-medoids, geometry only (CLAUDE.md §8 item 115): on the campaign maps
(restructure.domain(K, seed), as mission.py and meander_mission.py), for each lane width L (cells):
clusters, km flown over the cluster's own cells, km flown elsewhere (transit, lead-in / lead-out, BS legs),
share of cells within the River half-width of their cluster's flight line (cover), farthest cell (cells).
k-medoids: straight line through the CH proxy, Held-Karp tour (restructure.run_map); MEANDER: lane centre
curves, boustrophedon tour (meander.curve_eval). No ns-3.

    python3 tools/l2_lanes.py --maps "KW/k*" --lanes 4.5 6 7.5 9 [--frags 0.25 0.5] --out docs/data/l2diag/lanes [--figs DIR]
    python3 tools/l2_lanes.py --plot docs/data/l2diag/lanes.csv --figs docs/figures

--figs: DIR/l2-lanes.png (no text, item 63), one panel per size (2, 4, 6, 8 clusters): x the cover, y the km
flown (inside + transit), means over maps; k-medoids a blue dot, MEANDER a green line through its lane widths
(widest lane at the left, lowest cover).
"""
import argparse, csv, glob, os
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import meander
from map_gen import strip_text
from mission_report import GREY, SURF
from restructure import domain


def figure(rows, path):
    fig, axs = plt.subplots(1, 4, figsize=(16, 3.8), dpi=150, facecolor=SURF)
    for ax, z in zip(axs, (2, 4, 6, 8)):
        m = lambda p, key: np.mean([r[key] for r in rows if r["part"] == p and r["size"] == z])
        mp = sorted({r["part"] for r in rows if r["part"].startswith("meander") and "f" not in r["part"]},
                    key=lambda p: float(p[7:]))
        ax.plot([m(p, "cover") for p in mp], [m(p, "inside") + m(p, "transit") for p in mp], "-o", color="#2f9e6e",
                ms=5, lw=1.4)
        ax.plot(m("kmedoids", "cover"), m("kmedoids", "inside") + m("kmedoids", "transit"), "o", color="#1c5cab", ms=8)
        ax.set_ylim(0, None)
        ax.grid(color=GREY, lw=.6)
        ax.set_axisbelow(True)
        ax.set_facecolor(SURF)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    strip_text(fig)
    fig.savefig(path, facecolor=SURF, bbox_inches="tight", pad_inches=.06)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--maps", default="", help="mission folders named k<K>-s<seed> (only the names are used)")
    ap.add_argument("--plot", default="", help="only draw the figure from this csv")
    ap.add_argument("--figs", default="")
    ap.add_argument("--lanes", nargs="+", type=float, default=[4.5, 6, 7.5, 9])
    ap.add_argument("--frags", nargs="+", type=float, default=[0.25], help="MEANDER fragment threshold (x cap)")
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    if a.plot:
        rows = [{k: (v if k in ("map", "part") else float(v)) for k, v in r.items()} for r in csv.DictReader(open(a.plot))]
        figure(rows, f"{a.figs}/l2-lanes.png")
        return
    rows = []
    for w in sorted(glob.glob(a.maps)):
        name = os.path.basename(w)
        K, seed = int(name.split("-")[0][1:]), int(name.split("-s")[1])
        g = domain(K, seed)
        for L, fr in [(L, fr) for fr in a.frags for L in a.lanes]:
            M = meander.run(K, seed, 0, L, g=g, frag_share=fr)
            S = meander.summarise(M)
            tag = f"meander{L:g}" + (f"f{fr:g}" if fr != 0.25 else "")
            for part in (["kmedoids"] if (L, fr) == (a.lanes[0], a.frags[0]) else []) + ["meander"]:
                s = S[part]
                rows.append(dict(map=name, size=K, part=part if part == "kmedoids" else tag, L=L,
                                 clusters=s["clusters"], minCells=s["minCells"], inside=round(s["inside"], 2),
                                 transit=round(s["transit"], 2), cover=round(s["cover"], 3),
                                 farthest=round(s["farthest"], 2), covered=round(s["covered"], 3)))
        print(name, flush=True)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out + ".csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)
    by = defaultdict(list)
    for r in rows:
        by[(r["part"], r["size"])].append(r)
    parts = list(dict.fromkeys(r["part"] for r in rows))
    for r in rows:
        r["total"] = round(r["inside"] + r["transit"], 2)
        r["withLeads"] = round(r["total"] + 2 * meander.RHO / 1000 * r["clusters"], 2)   # each path's lead-in / -out
    for key in ("clusters", "inside", "transit", "total", "withLeads", "cover", "farthest"):
        print(f"{key:9s}" + "  ".join(f"{p}: " + " / ".join(f"{np.mean([r[key] for r in by[(p, z)]]):.3g}"
                                                         for z in (2, 4, 6, 8)) for p in parts))
    if a.figs:
        figure(rows, f"{a.figs}/l2-lanes.png")


if __name__ == "__main__":
    main()
