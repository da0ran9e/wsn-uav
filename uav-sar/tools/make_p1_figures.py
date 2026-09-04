"""PNG panels for one Phase-1 plan: what the cells are for, what tier 1 saw,
what the aircraft flew, and what the refinement loop did.

    python3 tools/make_p1_figures.py RUNDIR OUT.png [TITLE]
"""
import csv, math, os, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from matplotlib.patches import RegularPolygon

INK, DIM, GRID = "#12151a", "#5b6472", "#dfe3e9"
CLS = {"A": "#2f6fd0", "B": "#e08a1e", "C": "#b9c0cb"}
MOD = {"visual": "#2f6fd0", "thermal": "#c2410c", "acoustic": "#7c3aed", "none": "#cbd2dc"}


def rows(d, n):
    p = os.path.join(d, n)
    return list(csv.DictReader(open(p))) if os.path.exists(p) else []


def cfg(d):
    return {r["key"]: r["value"] for r in rows(d, "config.csv")}


def hexes(ax, cells, colour, alpha=0.30, rc=100.0):
    for c in cells:
        ax.add_patch(RegularPolygon((float(c["cx"]), float(c["cy"])), 6, radius=rc,
                                    orientation=0.0, facecolor=colour(c),
                                    edgecolor="#ffffff", lw=0.8, alpha=alpha, zorder=1))


def frame(ax, side, title):
    ax.set_title(title, fontsize=10.5, color=INK, pad=7)
    ax.set_xlim(-90, side + 90)
    ax.set_ylim(-90, side + 90)
    ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color(GRID)


def main():
    d, out = sys.argv[1], sys.argv[2]
    title = sys.argv[3] if len(sys.argv) > 3 else os.path.basename(d)
    C = cfg(d)
    side, rc = float(C["side"]), float(C["cellRadius"])
    cells, nodes = rows(d, "cells.csv"), rows(d, "nodes.csv")
    objs, path, hist = rows(d, "objects.csv"), rows(d, "path.csv"), rows(d, "history.csv")

    fig = plt.figure(figsize=(16.4, 4.8), dpi=170)
    gs = fig.add_gridspec(1, 4, width_ratios=[1, 1, 1, 0.9], wspace=0.22)

    # --- 1. Phase 0: what each cell is FOR -------------------------------
    ax = fig.add_subplot(gs[0, 0])
    hexes(ax, cells, lambda c: CLS[c["class"]], 0.28, rc)
    for n in nodes:
        ax.plot(float(n["x"]), float(n["y"]), ".", ms=1.9,
                color=MOD.get(n["modality"], "#ccc"), zorder=2)
    lead = {c["leader"] for c in cells if c["class"] == "A"}
    for n in nodes:
        if n["id"] in lead:
            ax.plot(float(n["x"]), float(n["y"]), "o", ms=5.2, mfc="none",
                    mec="#12151a", mew=1.3, zorder=4)
    nA = sum(1 for c in cells if c["class"] == "A")
    nB = sum(1 for c in cells if c["class"] == "B")
    nC = sum(1 for c in cells if c["class"] == "C")
    frame(ax, side, f"Pha 0 — lớp ô  A={nA} B={nB} C={nC}")
    ax.legend(handles=[
        Line2D([], [], marker="s", ls="", ms=8, color=CLS["A"], alpha=.5,
               label="A: phân biệt được → cần tham chiếu"),
        Line2D([], [], marker="s", ls="", ms=8, color=CLS["B"], alpha=.5,
               label="B: chỉ phát hiện → không gửi"),
        Line2D([], [], marker="s", ls="", ms=8, color=CLS["C"], alpha=.5, label="C: vô hướng"),
        Line2D([], [], marker="o", ls="", ms=6, mfc="none", mec=INK, label="cụm trưởng (bầu theo năng lực)"),
        Line2D([], [], marker=".", ls="", ms=9, color=MOD["visual"], label="nút visual (= tham chiếu)"),
        Line2D([], [], marker=".", ls="", ms=9, color=MOD["thermal"], label="nút thermal"),
        Line2D([], [], marker=".", ls="", ms=9, color=MOD["acoustic"], label="nút acoustic")],
        loc="upper center", bbox_to_anchor=(0.5, -0.02), frameon=False, fontsize=6.4, ncol=2)

    # --- 2. Tier 1 -------------------------------------------------------
    ax = fig.add_subplot(gs[0, 1])
    smax = max((float(c["score"]) for c in cells), default=1.0) or 1.0
    hexes(ax, cells, lambda c: plt.cm.YlOrRd(0.15 + 0.85 * float(c["score"]) / smax), 0.85, rc)
    for c in cells:
        if c["suspect"] == "1":
            ax.add_patch(RegularPolygon((float(c["cx"]), float(c["cy"])), 6, radius=rc,
                                        orientation=0.0, facecolor="none",
                                        edgecolor="#12151a", lw=1.8, zorder=3))
    for o in objs:
        real = o["real"] == "1"
        ax.plot(float(o["x"]), float(o["y"]), "*" if real else "x",
                ms=15 if real else 9, mew=2.0,
                color="#1f9d6b" if real else "#c2410c", zorder=6)
    nd = sum(1 for c in cells if c["suspect"] == "1")
    frame(ax, side, f"Tầng 1 — điểm $a_n$, |D|={nd}")
    ax.legend(handles=[
        Line2D([], [], marker="*", ls="", ms=12, color="#1f9d6b", label="nạn nhân thật"),
        Line2D([], [], marker="x", ls="", ms=8, mew=2, color="#c2410c", label="vật gây nhầm"),
        Line2D([], [], marker="h", ls="", ms=9, mfc="none", mec=INK, label="ô nghi vấn (∈ D)")],
        loc="upper center", bbox_to_anchor=(0.5, -0.02), frameon=False, fontsize=6.8)

    # --- 3. what was flown, coloured by the speed the LP chose -----------
    ax = fig.add_subplot(gs[0, 2])
    hexes(ax, cells, lambda c: "#eef1f5" if float(c["theta"]) <= 0 else "#cfe0f7", 0.9, rc)
    vmin, vmax = float(C["vmin"]), float(C["vmax"])
    VEH = ["#12151a", "#7c3aed", "#0e7490", "#a16207", "#be123c"]
    segs, cols = [], []
    for vi, v in enumerate(sorted({p["vehicle"] for p in path}, key=int)):
        pts = [(float(p["x"]), float(p["y"]), float(p["speedMps"]))
               for p in path if p["vehicle"] == v]
        # a wide, pale underlay says WHICH aircraft; the thin line on top says
        # how fast. Two questions, two channels.
        ax.plot([q[0] for q in pts], [q[1] for q in pts], "-",
                color=VEH[vi % len(VEH)], lw=4.6, alpha=0.22, zorder=4,
                solid_capstyle="round")
        for i in range(len(pts) - 1):
            segs.append([(pts[i][0], pts[i][1]), (pts[i + 1][0], pts[i + 1][1])])
            cols.append(pts[i][2])
    if segs:
        lc = LineCollection(segs, cmap="viridis_r", lw=2.0, zorder=5)
        lc.set_array(__import__("numpy").array(cols))
        lc.set_clim(vmin, vmax)
        ax.add_collection(lc)
        cb = fig.colorbar(lc, ax=ax, orientation="horizontal",
                          fraction=0.045, pad=0.035, aspect=34)
        cb.set_label("tốc độ (m/s) — chậm = giao nhiều liều", fontsize=7)
        cb.ax.tick_params(labelsize=6.5)
    ax.plot(0, 0, "s", ms=8, color="#12151a", zorder=7)
    ax.annotate("căn cứ", (0, 0), textcoords="offset points", xytext=(9, 6),
                fontsize=7, color=INK)
    for o in objs:
        ax.plot(float(o["x"]), float(o["y"]), "*" if o["real"] == "1" else "x",
                ms=13 if o["real"] == "1" else 8, mew=1.8,
                color="#1f9d6b" if o["real"] == "1" else "#c2410c", zorder=8)
    frame(ax, side, f"T2+T3 — {C['vehicles']} máy bay, makespan {float(C['makespan']):.0f}s")
    ax.legend(handles=[Line2D([], [], color=VEH[i % len(VEH)], lw=4, alpha=.35,
                              label=f"máy bay {i+1}")
                       for i in range(int(C["vehicles"]))],
              loc="upper center", bbox_to_anchor=(0.5, -0.30), frameon=False,
              fontsize=6.8, ncol=min(3, int(C["vehicles"])))

    # --- 4. the refinement loop -----------------------------------------
    ax = fig.add_subplot(gs[0, 3])
    it = [int(h["iteration"]) for h in hist]
    mk = [float(h["makespanS"]) for h in hist]
    ok = [h["valid"] == "1" for h in hist]
    nc = [int(h.get("planCells", 0)) for h in hist]
    ax.plot(it, mk, "-", color=DIM, lw=1.4, zorder=1)
    for i, (m, k) in enumerate(zip(mk, nc)):
        ax.annotate(f"{k}", (i, m), textcoords="offset points", xytext=(0, 9),
                    ha="center", fontsize=6.6, color=DIM)
    ax.plot([i for i, o in zip(it, ok) if not o], [m for m, o in zip(mk, ok) if not o],
            "o", ms=7, mfc="white", mec="#c2410c", mew=1.8, zorder=3, label="không tự nhất quán")
    ax.plot([i for i, o in zip(it, ok) if o], [m for m, o in zip(mk, ok) if o],
            "o", ms=7, color="#1f9d6b", zorder=4, label="hợp lệ")
    if C.get("feasible") == "1":
        ax.axhline(float(C["makespan"]), color="#1f9d6b", ls=":", lw=1.2)
    ax.set_xlabel("vòng lặp T4", fontsize=8.5, color=INK)
    ax.set_ylabel("makespan (s)", fontsize=8.5, color=INK)
    ax.set_title("T4 — bước rút NỬA lại khi kế hoạch\nkhông tự nhất quán (số = ô đã thăm)",
                 fontsize=10.5, color=INK, pad=7)
    ax.grid(alpha=0.25, lw=0.6)
    ax.tick_params(labelsize=7.5)
    for s in ax.spines.values():
        s.set_color(GRID)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), frameon=False, fontsize=7)

    fig.suptitle(title, fontsize=12.5, color=INK, y=1.005)
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    print(f"  {out}")


if __name__ == "__main__":
    main()
