"""Concept sketches at cell level, no text: River, Axe, Banks, critical cells, Circle.

    python3 tools/concept_cells.py --deploy ../uav-coop/docs/data --data docs/data --figs docs/figures \
        --path docs/data/path-a180.csv --banks 0.8,0.2,0.05

Everything here is what the BS can compute before the flight:
  PER of a cell  PER at the closest approach of the track to the cell centre, from the
                 measured PER-vs-distance curve (DATA/per-distance.csv, ns-3 pass bitmaps)
  River          cells with PER <= threshold (one panel per --banks value)
  Axe            cells the track crosses; each holds the stretch of the stream sent above it
  Banks          River cells next to a non-River cell, one colour per side of the track
  critical       the CH's cell, CLs far above the rest (> mean + 2 sd), and CLs that are
                 the best within two rings and above mean + 1 sd
  Circle         the 6 neighbours of a critical cell; the Axe is cut into 6 consecutive
                 stretches, one per neighbour (further along the flight -> further along the
                 Axe); each fetches its stretch ahead and hands it over on request
"""
import argparse, csv, math, os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.patches import FancyArrowPatch, Wedge
import numpy as np

SURF, INK, GREY, FAINT = "#fcfcfb", "#0b0b0b", "#e6e5e1", "#c9dcf3"
RAMP = matplotlib.colors.LinearSegmentedColormap.from_list("r", ["#86b6ef", "#3987e5", "#0d366b"])
SEQ = matplotlib.colors.LinearSegmentedColormap.from_list("s", ["#f6c3c3", "#e34948", "#8f1d1b"])
BANK = ["#1baf7a", "#eda100"]
CRIT = "#e34948"
CAT = ["#0d366b", "#3987e5", "#1baf7a", "#eda100", "#e34948", "#8e5ad6"]
NB = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
EDGE_NB = [(0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1), (1, 0)]


def corners(cx, cy, R):
    return [(cx + R * math.cos(math.radians(30 + 60 * k)), cy + R * math.sin(math.radians(30 + 60 * k)))
            for k in range(6)]


def hex_of(x, y, R):
    """Pointy-top axial cell containing (x, y)."""
    q, r = (math.sqrt(3) / 3 * x - y / 3) / R, (2 / 3 * y) / R
    s = -q - r
    rq, rr, rs = round(q), round(r), round(s)
    dq, dr, ds = abs(rq - q), abs(rr - r), abs(rs - s)
    if dq > dr and dq > ds:
        rq = -rr - rs
    elif dr > ds:
        rr = -rq - rs
    return rq, rr


def ring(h, k):
    out, q, r = [], h[0] + NB[4][0] * k, h[1] + NB[4][1] * k
    for side in range(6):
        for _ in range(k):
            out.append((q, r))
            q, r = q + NB[side][0], r + NB[side][1]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deploy", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--figs", required=True)
    ap.add_argument("--path", required=True)
    ap.add_argument("--banks", default="0.8,0.2,0.05", help="PER at the Banks, one panel each")
    a = ap.parse_args()
    ths = [float(v) for v in a.banks.split(",")]

    lat = list(csv.DictReader(open(os.path.join(a.deploy, "deploy-lattice.csv"))))
    c = {(int(x["q"]), int(x["r"])): (float(x["cx"]), float(x["cy"])) for x in lat}
    w = math.dist(c[(0, 0)], c[(1, 0)])
    R = w / math.sqrt(3)
    for h, (x, y) in c.items():
        assert hex_of(x, y, R) == h
    sel = sorted((int(x["q"]), int(x["r"])) for x in lat if x["selected"] == "1")
    S = set(sel)
    segs = [[corners(*c[h], R)[k], corners(*c[h], R)[(k + 1) % 6]]
            for h in sel for k, (dq, dr) in enumerate(EDGE_NB) if (h[0] + dq, h[1] + dr) not in S]
    nodes = list(csv.DictReader(open(os.path.join(a.deploy, "deploy-nodes-s35.csv"))))
    P = np.array([[float(q["x"]), float(q["y"])] for q in csv.DictReader(open(a.path))])
    curve = list(csv.DictReader(open(os.path.join(a.data, "per-distance.csv"))))
    cd = np.array([(float(r["dLoM"]) + float(r["dHiM"])) / 2 for r in curve])
    cp = np.array([float(r["per"]) for r in curve])

    C = np.array([c[h] for h in sel])
    dist = np.sqrt(((C[:, None, :] - P[None, :, :]) ** 2).sum(-1))
    near = dist.argmin(1)
    per = dict(zip(sel, np.interp(dist.min(1), cd, cp)))
    k = np.clip(near, 0, len(P) - 2)
    t = P[k + 1] - P[k]
    cross = t[:, 0] * (C[:, 1] - P[k, 1]) - t[:, 1] * (C[:, 0] - P[k, 0])
    side = dict(zip(sel, (cross > 0).astype(int).tolist()))
    # Axe: cells the track crosses, in the order the stream reaches them
    axe = []
    for x, y in P:
        h = hex_of(x, y, R)
        if h in S and h not in axe:
            axe.append(h)
    rank = {h: i / max(1, len(axe) - 1) for i, h in enumerate(axe)}
    # critical cells
    sc = {(int(r["q"]), int(r["r"])): float(r["score"]) for r in nodes if r["isCL"] == "1"}
    m, s = np.mean(list(sc.values())), np.std(list(sc.values()))
    chn = next(r for r in nodes if r["isCH"] == "1")
    chc = (int(chn["q"]), int(chn["r"]))
    crit = {chc} | {h for h, v in sc.items() if v > m + 2 * s}
    for h, v in sc.items():
        around = [sc[g] for g in ring(h, 1) + ring(h, 2) if g in sc]
        if v > m + s and v >= max(around):
            crit.add(h)
    clpos = {(int(r["q"]), int(r["r"])): (float(r["x"]), float(r["y"])) for r in nodes if r["isCL"] == "1"}
    xs = C[:, 0]; ys = C[:, 1]

    def frame(ax, colours, track=.8):
        ax.add_collection(PolyCollection([corners(*c[h], R) for h in sel], facecolors=[colours[h] for h in sel],
                                         edgecolors="#ffffff", linewidths=.8, zorder=0))
        ax.add_collection(LineCollection(segs, colors="#52514e", linewidths=.9, zorder=1))
        if track:
            ax.plot(P[:, 0], P[:, 1], color=INK, lw=1.2, alpha=track, zorder=6)
            ax.add_patch(FancyArrowPatch(P[-30], P[-1], arrowstyle="-|>", mutation_scale=12, color=INK,
                                         alpha=track, zorder=6))
        ax.set_xlim(xs.min() - w, xs.max() + w); ax.set_ylim(ys.min() - w, ys.max() + w)
        ax.set_aspect("equal"); ax.set_facecolor(SURF); ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)

    def save(fig, name):
        out = os.path.join(a.figs, name)
        fig.savefig(out, facecolor=SURF, bbox_inches="tight", pad_inches=.05)
        plt.close(fig)
        print(f"  {out}")

    river = {th: {h for h in sel if per[h] <= th} for th in ths}
    # 1. River: shade = PER (darker = fewer losses)
    fig, axs = plt.subplots(1, len(ths), figsize=(5.2 * len(ths), 6.6), dpi=150, facecolor=SURF)
    for ax, th in zip(np.atleast_1d(axs), ths):
        frame(ax, {h: RAMP(1 - per[h] / th) if h in river[th] else GREY for h in sel})
    save(fig, "concept-river.png")
    # 2. Axe: each cell holds the stretch of the stream sent above it (colour = order)
    fig, ax = plt.subplots(figsize=(5.2, 6.6), dpi=150, facecolor=SURF)
    frame(ax, {h: SEQ(rank[h]) if h in rank else GREY for h in sel}, .5)
    save(fig, "concept-axe.png")
    # 3. Banks
    fig, axs = plt.subplots(1, len(ths), figsize=(5.2 * len(ths), 6.6), dpi=150, facecolor=SURF)
    banks = {}
    for ax, th in zip(np.atleast_1d(axs), ths):
        rv = river[th]
        banks[th] = {h for h in rv if any((h[0] + dq, h[1] + dr) in S and (h[0] + dq, h[1] + dr) not in rv
                                          for dq, dr in NB)}
        frame(ax, {h: BANK[side[h]] if h in banks[th] else (FAINT if h in rv else GREY) for h in sel}, .5)
    save(fig, "concept-banks.png")
    # 4. critical cells, each fed from its nearest Axe cell
    fig, ax = plt.subplots(figsize=(5.2, 6.6), dpi=150, facecolor=SURF)
    frame(ax, {h: "#f6c3c3" if h in crit else (FAINT if h in rank else GREY) for h in sel}, .4)
    for h in crit:
        src = min(axe, key=lambda g: math.dist(c[g], c[h]))
        if src != h:
            ax.add_patch(FancyArrowPatch(c[src], clpos[h], arrowstyle="-|>", mutation_scale=13, color="#3987e5",
                                         lw=1.5, connectionstyle="arc3,rad=.12", zorder=5))
        ax.scatter(*clpos[h], s=90 if h == chc else 55, marker="*" if h == chc else "o", color=CRIT,
                   edgecolors=INK, lw=.6, zorder=7)
    save(fig, "concept-critical.png")
    # 5. Circle around the critical cell farthest from the Axe with all 6 neighbours inside
    cand = [h for h in crit if h not in rank and all(g in S for g in ring(h, 1))]
    if not cand:
        cand = [h for h in sel if h not in rank and all(g in S for g in ring(h, 1))]
    cc = max(cand, key=lambda h: min(math.dist(c[h], c[g]) for g in axe))
    circ = ring(cc, 1)
    # balanced: the Axe cut into 6 consecutive stretches; the neighbour further along the
    # flight direction takes the stretch further along
    u = P[-1] - P[0]
    order = sorted(range(6), key=lambda j: np.dot(np.array(c[circ[j]]), u))
    owner = {g: order[min(5, i * 6 // len(axe))] for i, g in enumerate(axe)}
    fig, ax = plt.subplots(figsize=(5.2, 6.6), dpi=150, facecolor=SURF)
    col = {h: GREY for h in sel}
    col.update({g: matplotlib.colors.to_rgba(CAT[owner[g]], .45) for g in axe})
    col.update({h: CAT[j] for j, h in enumerate(circ)})
    col[cc] = "#ffffff"
    frame(ax, col, .35)
    share = [sum(1 for g in axe if owner[g] == j) for j in range(6)]
    a0 = 90.0
    for j in range(6):
        if share[j]:
            a1 = a0 + 360 * share[j] / len(axe)
            ax.add_patch(Wedge(c[cc], R * .62, a0, a1, facecolor=CAT[j], edgecolor="#ffffff", lw=.8, zorder=4))
            a0 = a1
    for j, h in enumerate(circ):
        if not share[j]:
            continue
        g = min((g for g in axe if owner[g] == j), key=lambda g: math.dist(c[g], c[h]))
        ax.add_patch(FancyArrowPatch(c[g], c[h], arrowstyle="-|>", mutation_scale=11, color=CAT[j], lw=1.3,
                                     connectionstyle="arc3,rad=.1", zorder=5))
        v = np.array(c[cc]) - np.array(c[h])
        v /= np.linalg.norm(v)
        ax.add_patch(FancyArrowPatch(np.array(c[h]) + v * R * .3, np.array(c[cc]) - v * R * .68,
                                     arrowstyle="-|>", mutation_scale=10, color=INK, lw=1, ls="--", zorder=5))
    ax.scatter(*clpos[cc], s=60, color=CRIT, edgecolors=INK, lw=.6, zorder=7)
    save(fig, "concept-circle.png")
    print(f"cells {len(sel)}, Axe {len(axe)}, critical {sorted(crit)} (CH {chc}), circle around {cc}, "
          f"shares {share}")
    for th in ths:
        print(f"  PER <= {th}: River {len(river[th])} cells, Banks {len(banks[th])} "
              f"({sum(side[h] for h in banks[th])} / {sum(not side[h] for h in banks[th])})")


if __name__ == "__main__":
    main()
