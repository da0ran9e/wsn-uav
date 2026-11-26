#!/usr/bin/env python3
"""Figures for the J1 draft v2 (forest scenario), front part of the paper.

Usage: python3 paper/j1/analysis/fig_draft_v2.py OUTDIR
Writes, each as a text-free PNG and a -labelled PNG/PDF:
  draft2-scenario-cattien   scenario on the real Cat Tien window (trails, streams from maps-forest/cattien)
  draft2-phases             three-phase timeline of one mission (swimlanes)
  draft2-canopy-loss        Weissberger foliage loss of the slant path vs horizontal distance, h = 100 m
  draft2-density-gap        device density of real forest deployments vs the density the model assumes
Everything except the trail and stream geometry is illustrative (cell clusters, AI cells, paths, person).
"""
import json, math, os, sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, FancyBboxPatch, Circle
from matplotlib.lines import Line2D

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
HERE = os.path.dirname(os.path.abspath(__file__))
MAPS = os.path.join(HERE, "..", "maps-forest", "cattien")
rng = np.random.default_rng(7)
plt.rcParams.update({"font.size": 8, "font.family": "DejaVu Sans"})


def save(fig, name, labelled):
    base = os.path.join(OUT, name + ("-labelled" if labelled else ""))
    fig.savefig(base + ".png", dpi=200, bbox_inches="tight", pad_inches=0.02)
    if labelled:
        fig.savefig(base + ".pdf", bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def lines(path):
    out = []
    for f in json.load(open(path))["features"]:
        g = f["geometry"]
        cs = [g["coordinates"]] if g["type"] == "LineString" else g["coordinates"]
        out += [np.array(c) for c in cs]
    return out


# ---------------------------------------------------------------- 1 scenario
trails, streams = lines(f"{MAPS}/trails.geojson"), lines(f"{MAPS}/streams.geojson")
pts = np.vstack(trails)
ipp = pts[np.argmin(np.hypot(pts[:, 0] - 700, pts[:, 1] + 900))]      # last-seen point: on the central trail
bs = pts[np.argmin(np.hypot(pts[:, 0] - 2700, pts[:, 1] + 1300))]     # ranger station: on the trail near the road (SE)
R, RAD = 100.0, 2600.0
dx, dy = 1.5 * R, math.sqrt(3) * R
cells = []
for i in range(-40, 41):
    for j in range(-40, 41):
        x, y = i * dx, j * dy + (dy / 2 if i % 2 else 0)
        if math.hypot(x, y) <= RAD:
            cells.append((i, j, x + ipp[0], y + ipp[1]))
cells = np.array(cells)
xy = cells[:, 2:]
K = 12                                                               # clusters of at most ~80 cells
cen = xy[rng.choice(len(xy), K, replace=False)]
for _ in range(60):
    lab = np.argmin(((xy[:, None, :] - cen[None]) ** 2).sum(-1), 1)
    cen = np.array([xy[lab == k].mean(0) for k in range(K)])
idx = {(int(a), int(b)): n for n, (a, b) in enumerate(cells[:, :2])}
crit = np.concatenate([rng.choice(np.where(lab == k)[0], 5, replace=False) for k in range(K)])
# phase-1 tour: nearest neighbour from the base station, then Chaikin smoothing
order, left, cur = [], list(range(K)), bs
while left:
    k = min(left, key=lambda k: np.hypot(*(cen[k] - cur))); order.append(k); left.remove(k); cur = cen[k]
poly = np.vstack([bs, cen[order], bs])
for _ in range(4):
    q = 0.75 * poly[:-1] + 0.25 * poly[1:]; r = 0.25 * poly[:-1] + 0.75 * poly[1:]
    poly = np.vstack([poly[0], np.column_stack([q, r]).reshape(-1, 2), poly[-1]])
seg = np.vstack([np.linspace(poly[n], poly[n + 1], 20) for n in range(len(poly) - 1)])
dpath = np.min(np.hypot(xy[:, None, 0] - seg[None, :, 0], xy[:, None, 1] - seg[None, :, 1]), 1)
person = ipp + np.array([-1150.0, 820.0])
hit = np.argmin(np.hypot(*(xy - person).T))
sus = [crit[np.argmin(np.hypot(*(xy[crit] - person).T))], crit[3], crit[27]]
corner = [(R * math.cos(math.radians(60 * a)), R * math.sin(math.radians(60 * a))) for a in range(6)]
nbr = lambda i, j: [(i, j + 1), (i, j - 1), (i + 1, j + (i % 2)), (i + 1, j - 1 + (i % 2)), (i - 1, j + (i % 2)), (i - 1, j - 1 + (i % 2))]


def scenario(labelled):
    fig, ax = plt.subplots(figsize=(6.8, 6.8))
    ax.set_facecolor("#e8efe3")
    for s in streams: ax.plot(*s.T, color="#4f8fd0", lw=0.8, zorder=4)
    for t in trails: ax.plot(*t.T, color="#b5652b", lw=1.0, zorder=4)
    for n, (i, j, x, y) in enumerate(cells):
        fc = "#9cc3e6" if dpath[n] < 199 else "#f6f6f2"
        if n in set(crit): fc = "#d1372b"
        ax.add_patch(MPoly([(x + a, y + b) for a, b in corner], closed=True, fc=fc, ec="#c8c8c0", lw=0.15, zorder=2))
        for e, (a, b) in enumerate(nbr(int(i), int(j))):          # cluster borders
            m = idx.get((a, b))
            if m is None or lab[m] != lab[n]:
                ang = {0: 60, 1: 240, 2: 0, 3: 300, 4: 120, 5: 180}[e]
                p0 = (x + R * math.cos(math.radians(ang)), y + R * math.sin(math.radians(ang)))
                p1 = (x + R * math.cos(math.radians(ang + 60)), y + R * math.sin(math.radians(ang + 60)))
                ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color="#555555", lw=0.6, zorder=3)
    ax.plot(*seg.T, color="#1b1b1b", lw=1.4, zorder=5)
    p2 = np.vstack([bs] + [xy[s] for s in sus])
    ax.plot(*p2.T, color="#7b3fa0", lw=1.2, ls=(0, (4, 2)), zorder=5)
    ax.plot(*bs, marker="s", ms=8, color="#ffd23f", mec="k", zorder=6)
    ax.plot(*ipp, marker="o", ms=7, color="white", mec="k", mew=1.2, zorder=6)
    ax.plot(*person, marker="*", ms=13, color="#ff8c00", mec="k", zorder=6)
    for rr in (800, 1600, 2400):
        ax.add_patch(Circle(ipp, rr, fill=False, ec="#444444", lw=0.6, ls=":", zorder=4))
    ax.set_xlim(ipp[0] - 3300, ipp[0] + 3300); ax.set_ylim(ipp[1] - 3300, ipp[1] + 3300)
    ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    if labelled:
        h = [Line2D([], [], color="#b5652b", lw=1.2, label="trail (OSM)"), Line2D([], [], color="#4f8fd0", lw=1.2, label="stream (OSM)"),
             Line2D([], [], marker="h", ls="", ms=8, mfc="#f6f6f2", mec="#888", label="cell, R = 100 m"),
             Line2D([], [], color="#555", lw=1, label="cluster border"),
             Line2D([], [], marker="h", ls="", ms=8, mfc="#d1372b", mec="#888", label="critical (AI) cell"),
             Line2D([], [], marker="h", ls="", ms=8, mfc="#9cc3e6", mec="#888", label="within 200 m of the pass"),
             Line2D([], [], color="#1b1b1b", lw=1.6, label="phase 1: fixed-wing pass"),
             Line2D([], [], color="#7b3fa0", lw=1.4, ls="--", label="phase 2: rotary-wing visits"),
             Line2D([], [], marker="s", ls="", ms=7, color="#ffd23f", mec="k", label="ranger station (BS)"),
             Line2D([], [], marker="o", ls="", ms=6, color="white", mec="k", label="last-seen point"),
             Line2D([], [], color="#444", lw=0.8, ls=":", label="search rings (illustrative)"),
             Line2D([], [], marker="*", ls="", ms=10, color="#ff8c00", mec="k", label="missing person")]
        ax.legend(handles=h, loc="lower left", fontsize=6.5, framealpha=0.9)
        x0, y0 = ipp[0] + 1900, ipp[1] - 3100
        ax.plot([x0, x0 + 1000], [y0, y0], color="k", lw=2.5); ax.text(x0 + 500, y0 + 90, "1 km", ha="center")
    save(fig, "draft2-scenario-cattien", labelled)


# ---------------------------------------------------------------- 2 phases
LANES = ["Base station", "Fixed-wing UAV", "Ground network", "AI nodes", "Rotary-wing UAV"]
BOX = [  # lane, t0, t1, colour, label
    (0, 0.0, 2.2, "#cfd8dc", "phase 0 (offline):\ncells, AI cells,\nflight and ground plan"),
    (0, 2.6, 3.2, "#ffe082", "LoRa\nwake-up"),
    (1, 3.4, 7.4, "#90caf9", "phase 1: one pass, broadcast query"),
    (2, 3.8, 8.4, "#a5d6a7", "planned ground transport + repair"),
    (3, 5.0, 9.0, "#ffcc80", "match, report over LoRa"),
    (0, 6.0, 9.6, "#e1bee7", "update posterior"),
    (4, 6.4, 11.4, "#ce93d8", "phase 2: visit, verify"),
]


def phases(labelled):
    fig, ax = plt.subplots(figsize=(7.0, 2.6))
    for n in range(len(LANES)):
        ax.axhline(n, color="#dddddd", lw=0.6, zorder=0)
    for lane, t0, t1, col, txt in BOX:
        ax.add_patch(FancyBboxPatch((t0, lane - 0.32), t1 - t0, 0.64, boxstyle="round,pad=0.02,rounding_size=0.12", fc=col, ec="#555", lw=0.6, zorder=2))
        if labelled: ax.text((t0 + t1) / 2, lane, txt, ha="center", va="center", fontsize=6.3, zorder=3)
    for (x0, y0, x1, y1) in [(2.2, 0, 2.6, 0), (3.2, 0, 3.4, 1), (3.6, 1, 3.8, 2), (6.0, 2, 6.0, 3), (7.0, 3, 7.0, 0), (6.4, 0, 6.4, 4)]:
        ax.annotate("", (x1, y1 + (0.32 if y1 < y0 else -0.32 if y1 > y0 else 0)), (x0, y0 + (-0.32 if y1 < y0 else 0.32 if y1 > y0 else 0)),
                    arrowprops=dict(arrowstyle="-|>", lw=0.7, color="#333"), zorder=1)
    ax.plot([11.4], [4], marker="*", ms=11, color="#ff8c00", mec="k")
    ax.axvline(2.4, color="#999", lw=0.6, ls="--")
    ax.set_xlim(-0.1, 12.2); ax.set_ylim(len(LANES) - 0.5, -0.5)
    ax.set_xticks([]); ax.set_yticks(range(len(LANES)))
    ax.set_yticklabels(LANES if labelled else [""] * len(LANES))
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    if labelled:
        ax.text(2.4, -0.62, "incident reported", ha="center", fontsize=6.5, color="#555")
        ax.text(11.65, 4.0, "$T^\\star$", ha="left", va="center", fontsize=8)
        ax.set_xlabel("time (not to scale)")
    save(fig, "draft2-phases", labelled)


# ---------------------------------------------------------------- 3 canopy loss
def weiss(d, f=2.4):
    d = np.asarray(d, float)
    return np.where(d <= 14, 0.45 * f ** 0.284 * d, 1.33 * f ** 0.284 * np.minimum(d, 400) ** 0.588)


def canopy(labelled):
    H = 100.0
    x = np.linspace(1, 1200, 600)
    th = np.arctan2(H, x)
    fig, ax = plt.subplots(figsize=(3.5, 2.5))
    for hc, ls in ((5, ":"), (10, "-"), (20, "--")):
        ax.plot(x, weiss(hc / np.sin(th)), color="#2e7d32", ls=ls, lw=1.3, label=f"canopy depth {hc} m")
    for eta in (9.0, 19.8, 25.7):
        ax.axhline(eta, color="#888", lw=0.7)
    ax.set_xlim(0, 1200); ax.set_ylim(0, 45)
    if labelled:
        ax.set_xlabel("horizontal distance UAV to node (m), UAV at 100 m")
        ax.set_ylabel("foliage loss on slant path (dB)")
        for eta in (9.0, 19.8, 25.7): ax.text(1190, eta + 0.6, f"{eta:g} dB regime", ha="right", fontsize=6, color="#555")
        ax.legend(fontsize=6, loc="upper left", framealpha=0.9)
        top = ax.secondary_xaxis("top", functions=(lambda d: np.degrees(np.arctan2(H, np.maximum(d, 1e-3))), lambda a: H / np.tan(np.radians(np.clip(a, 1e-3, 89.9)))))
        top.set_xticks([60, 30, 15, 10, 6]); top.set_xlabel("elevation angle (deg)", fontsize=7)
    else:
        ax.set_xticklabels([]); ax.set_yticklabels([])
    save(fig, "draft2-canopy-loss", labelled)


# ---------------------------------------------------------------- 4 density gap
DEP = [  # label, devices per km2, source tag (CONTEXT-vi.md section 5)
    ("Dryad pilot, Lebanon (78 ha)", 117), ("Dryad, Marsden Moor UK", 2.0), ("4G camera traps, NL [Kissling 2024]", 1.9),
    ("camera traps, Pu Mat NP", 0.17), ("camera traps, Pu Hoat NR", 0.13), ("fire cameras, California", 1 / 330),
]


def density(labelled):
    fig, ax = plt.subplots(figsize=(3.5, 2.2))
    y = np.arange(len(DEP))[::-1]
    ax.barh(y, [d for _, d in DEP], color="#78909c", height=0.6)
    ax.set_xscale("log"); ax.set_xlim(1e-3, 3e3)
    ax.axvline(300, color="#c62828", lw=1, ls="--"); ax.axvline(820, color="#1565c0", lw=1.2)
    ax.set_yticks(y)
    if labelled:
        ax.set_yticklabels([l for l, _ in DEP], fontsize=6)
        ax.set_xlabel("devices per km$^2$")
        ax.text(280, -0.45, "connected\ngrid (est.)", color="#c62828", fontsize=5.5, ha="right", va="bottom")
        ax.text(900, -0.45, "model", color="#1565c0", fontsize=5.5, ha="left", va="bottom")
    else:
        ax.set_yticklabels([""] * len(DEP)); ax.set_xticklabels([])
    save(fig, "draft2-density-gap", labelled)


for lab_ in (False, True):
    scenario(lab_); phases(lab_); canopy(lab_); density(lab_)
print("ipp", ipp.round(), "bs", bs.round(), "cells", len(cells), "clusters", K, "max cluster size", np.bincount(lab).max(),
      "critical", len(crit), "cells within 199 m of pass", int((dpath < 199).sum()))
print("weissberger h_c=10 m at 45/11/6 deg:", [round(float(weiss(10 / math.sin(math.radians(a)))), 1) for a in (45, 11, 6)])
