"""CLAUDE.md §8 item 193: one cluster of kK-s1, seed 1: its cells (light), critical cells (dark) with their discs
B(v, xi) (rings), the CH (star), CHORD's pass (grey), the old DTSP-N + River pass (blue, dashed; C4/DR-old) and the fixed one
(orange, through_crit). No text (item 63).

    python3 dr_fig.py ENV K k OUT.png
"""
import csv, json, os, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Polygon

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uav-l2/tools"))
from map_gen import centre, corners  # noqa: E402

S = "/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/C4"
env, K, k, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
cp = f"{S}/CP/{env}/R1/k{K}-s1"
xi = json.load(open(f"{S}/DRT/{env}/R1/k{K}-s1/lm.json"))["xi"]
cells = [(int(x["q"]), int(x["r"])) for x in csv.DictReader(open(f"{cp}/c{k}-lattice.csv")) if x["selected"] == "1"]
crit = [(int(x["q"]), int(x["r"])) for x in csv.DictReader(open(f"{cp}/r{k}-rf-crit.csv"))]
ch = next((float(n["x"]), float(n["y"])) for n in csv.DictReader(open(f"{cp}/c{k}-nodes-s35.csv")) if n["isCH"] == "1")
path = lambda w: np.array([[float(r["x"]), float(r["y"])] for r in csv.DictReader(open(f"{w}/c{k}-path-s35.csv"))])
fig, ax = plt.subplots(figsize=(7, 7))
for h in cells:
    ax.add_patch(Polygon(corners(h), closed=True, fc="#e8edf2", ec="#ffffff", lw=0.6))
for h in crit:
    ax.add_patch(Polygon(corners(h), closed=True, fc="#5d6d7e", ec="#ffffff", lw=0.6))
    ax.add_patch(Circle(centre(h), xi, fill=False, ec="#2c3e50", lw=0.9, ls=":"))
for w, col, ls, lw in ((cp, "#7f8c8d", "-", 2.2), (f"{S}/DR-old/{env}/R1/k{K}-s1", "#2e86c1", "--", 2.0),
                       (f"{S}/DRT/{env}/R1/k{K}-s1", "#e67e22", "-", 2.4)):
    P = path(w)
    ax.plot(P[:, 0], P[:, 1], color=col, ls=ls, lw=lw)
ax.plot(*ch, marker="*", ms=16, color="#c0392b", mec="white")
C = np.array([centre(h) for h in cells])
ax.set_xlim(C[:, 0].min() - 500, C[:, 0].max() + 500)
ax.set_ylim(C[:, 1].min() - 500, C[:, 1].max() + 500)
ax.set_aspect("equal")
ax.axis("off")
fig.savefig(out, dpi=140, bbox_inches="tight")
