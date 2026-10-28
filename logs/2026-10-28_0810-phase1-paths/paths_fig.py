"""CLAUDE.md §8 item 202: team 1's phase-1 flight of each scheme of the campaign (logs/2026-10-27_1714-campaign4) on
seed 1, every map and channel. No text in the images (item 63).

Per map one grid: rows the channels (open, r500, r200, r100), columns the schemes (CHORD + River, LM-Tour + River,
DTSP-N + River, FC + DTSP-N); and every panel on its own. Drawn: the domain's land cells (light grey), its water cells
(pale blue), each cluster's cells (its own pale tint, never grey), the critical cells (dark grey), each CH (red star), the BS
(black square), and the whole flight BS -> clusters -> BS as flown (white halo, a few arrowheads for the direction):
kin_time's track of the folder for the River schemes (the one lm_tour.py score flies), dn-path.csv of the CHORD folder
for FC + DTSP-N (written by l1_rank's DN run). The same view box for the 16 panels of a map.
Prints per panel the flight's length and team 1's time (River schemes: kin_time profile + delivery fixes, as scored;
FC + DTSP-N: dn-info.json tour).

    python3 paths_fig.py OUTDIR
"""
import csv, json, os, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PolyCollection

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uav-l2/tools"))
import kin_time  # noqa: E402
from map_gen import centre, corners  # noqa: E402
from mission_report import load_map  # noqa: E402

C4 = "/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/C4"
ENVS = ("open", "r500", "r200", "r100")
SCHEMES = (("chord", "CP", "#1a5276"), ("lmtour", "LMD", "#d35400"), ("dtspn-river", "DR", "#7d3c98"),
           ("fc-dtspn", "DN", "#117a65"))
TINT = ("#aec7e8", "#ffbb78", "#98df8a", "#ff9896", "#c5b0d5", "#c49c94", "#f7b6d2", "#dbdb8d", "#9edae5",
        "#fdd0a2", "#c7e9c0", "#dadaeb", "#fcbba1", "#c6dbef", "#e7cb94")   # pale, no grey: one per cluster


def flight(sch, env, K):
    cp = f"{C4}/CP/{env}/R1/k{K}-s1"
    if sch == "DN":
        P = np.array([[float(r["x"]), float(r["y"])] for r in csv.DictReader(open(f"{cp}/dn-path.csv"))])
        return cp, P, json.load(open(f"{cp}/dn-info.json"))["tour"]
    w = f"{C4}/{sch}/{env}/R1/k{K}-s1"
    _, o = kin_time.run(w, "kin")
    return w, o[45]["track"][1], o[45]["profile"] + o[45]["fix"]


def draw(ax, w, P, col, lw):
    M = load_map(w, schemes=(), with_bits=False)
    dom = list(csv.DictReader(open(f"{w}/domain-cells.csv")))
    land = [(int(d["q"]), int(d["r"])) for d in dom if d["type"] == "land"]
    water = [(int(d["q"]), int(d["r"])) for d in dom if d["type"] != "land"] + list(M["water"] or [])
    polys = lambda hs: [corners(h) for h in hs]
    ax.add_collection(PolyCollection(polys(land), fc="#eef0f2", ec="white", lw=0.3))
    ax.add_collection(PolyCollection(polys(set(water)), fc="#d6eaf8", ec="white", lw=0.3))
    for i, k in enumerate(sorted(M["cl"])):
        g, Pk = M["cl"][k]["geo"], M["cl"][k]["P"]
        ax.add_collection(PolyCollection(polys(g["c"]), fc=TINT[i % len(TINT)], ec="white", lw=0.3))
        ax.add_collection(PolyCollection(polys(Pk["crit"]), fc="#4d5656", ec="white", lw=0.3))
    for k in sorted(M["cl"]):
        ch = next((float(n["x"]), float(n["y"])) for n in csv.DictReader(open(f"{w}/c{k}-nodes-s35.csv"))
                  if n["isCH"] == "1")
        ax.plot(*ch, marker="*", ms=7 * lw / 1.4, color="#c0392b", mec="white", mew=0.5, zorder=5)
    halo = [pe.Stroke(linewidth=lw + 1.6, foreground="white"), pe.Normal()]
    ax.plot(P[:, 0], P[:, 1], color=col, lw=lw, solid_capstyle="round", path_effects=halo, zorder=4)
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    for f in (0.1, 0.3, 0.5, 0.7, 0.9):   # the direction of flight
        i = int(np.searchsorted(s, f * s[-1]))
        j = min(i + max(1, int(len(P) * 0.004)), len(P) - 1)
        ax.annotate("", xy=P[j], xytext=P[i], zorder=6,
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=0, mutation_scale=9 * lw / 1.4))
    ax.plot(*M["bs"], marker="s", ms=6 * lw / 1.4, color="#17202a", mec="white", mew=0.6, zorder=6)
    ax.set_aspect("equal")
    ax.axis("off")
    return M, s[-1]


def box(ws, Ps):
    pts = [np.array([centre((int(d["q"]), int(d["r"]))) for d in csv.DictReader(open(f"{w}/domain-cells.csv"))])
           for w in ws[:1]] + list(Ps)
    A = np.vstack(pts)
    return A.min(axis=0) - 150, A.max(axis=0) + 150


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    print("| map | channel | scheme | flight (km) | team 1 (s) |\n|---|---|---|---|---|")
    for K in (8, 12, 16):
        runs = {(e, s): flight(s, e, K) for e in ENVS for _, s, _ in SCHEMES}
        lo, hi = box([runs[("open", "CP")][0]], [r[1] for r in runs.values()])
        asp = (hi[1] - lo[1]) / (hi[0] - lo[0])
        fig, axs = plt.subplots(4, 4, figsize=(16, 16 * asp), gridspec_kw=dict(wspace=0.02, hspace=0.02))
        for a, e in enumerate(ENVS):
            for b, (name, s, col) in enumerate(SCHEMES):
                w, P, T = runs[(e, s)]
                _, L = draw(axs[a, b], w, P, col, 1.1)
                axs[a, b].set_xlim(lo[0], hi[0]); axs[a, b].set_ylim(lo[1], hi[1])
                print(f"| k{K}-s1 | {e} | {name} | {L / 1000:.1f} | {T:.0f} |")
                f1, a1 = plt.subplots(figsize=(8, 8 * asp))
                draw(a1, w, P, col, 1.8)
                a1.set_xlim(lo[0], hi[0]); a1.set_ylim(lo[1], hi[1])
                f1.savefig(f"{out}/c4-phase1-k{K}-s1-{e}-{name}.png", dpi=130, bbox_inches="tight", pad_inches=0.02)
                plt.close(f1)
        fig.savefig(f"{out}/c4-phase1-k{K}-s1-grid.png", dpi=110, bbox_inches="tight", pad_inches=0.05)
        plt.close(fig)


if __name__ == "__main__":
    main()
