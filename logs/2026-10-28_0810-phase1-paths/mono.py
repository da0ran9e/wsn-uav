"""CLAUDE.md §8 item 204: the four phase-1 flights of one map and channel (default k8-s1, r500) as four separate
images, every flight in one bright colour, the cluster tints of paths_fig.py mixed further toward white. Same view
box for the four, no text.

    python3 mono.py OUTDIR [K ENV]
"""
import os, sys

import matplotlib.colors as mc
import matplotlib.pyplot as plt
import numpy as np

import paths_fig as F

COL = "#e6007e"   # one bright magenta for every flight: none of the pale tints, not the CH's red
LIGHT = 0.4       # share of white mixed into each cluster tint
F.TINT = tuple(mc.to_hex((1 - LIGHT) * np.array(mc.to_rgb(c)) + LIGHT) for c in F.TINT)


def main():
    out = sys.argv[1]
    K, env = (int(sys.argv[2]), sys.argv[3]) if len(sys.argv) > 3 else (8, "r500")
    os.makedirs(out, exist_ok=True)
    runs = {s: F.flight(s, env, K) for _, s, _ in F.SCHEMES}
    lo, hi = F.box([runs["CP"][0]], [r[1] for r in runs.values()])
    asp = (hi[1] - lo[1]) / (hi[0] - lo[0])
    for name, s, _ in F.SCHEMES:
        w, P, T = runs[s]
        fig, ax = plt.subplots(figsize=(8, 8 * asp))
        _, L = F.draw(ax, w, P, COL, 1.8)
        ax.set_xlim(lo[0], hi[0]); ax.set_ylim(lo[1], hi[1])
        fig.savefig(f"{out}/c4-phase1-k{K}-s1-{env}-{name}-mono.png", dpi=150, bbox_inches="tight", pad_inches=0.02)
        plt.close(fig)
        print(f"k{K}-s1 {env} {name}: {L / 1000:.1f} km, team 1 {T:.0f} s")


if __name__ == "__main__":
    main()
