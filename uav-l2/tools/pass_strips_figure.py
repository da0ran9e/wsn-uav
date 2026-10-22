"""What one node, and its whole cell, received in the pass, at several distances from the flight line
(CLAUDE.md §8 item 122): the reason the ground has to cooperate.

    python3 tools/pass_strips_figure.py --strip SAT/w10-l4-s1 --out docs/figures/river-pass-strips.png

From the ns-3 pass bitmap of one strip run (sat_strip.py). For each target offset (--offsets, m from the flight
line) the node nearest to it near the middle of the strip; two rows per offset, over --span packets centred on
where the UAV passes that node: the node alone, then the union of every node of its cell. Received packets
light, lost packets red; no text (§8 item 63). Prints, per row, the packets received and the longest run.
"""
import argparse, csv

import numpy as np


def longest(b):
    best = run = 0
    for x in b:
        run = run + 1 if x else 0
        best = max(best, run)
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strip", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--offsets", default="0,200,400,600,800")
    ap.add_argument("--span", type=int, default=2000, help="packets shown (0.5 m each)")
    a = ap.parse_args()
    w = a.strip
    nodes = list(csv.DictReader(open(f"{w}/c1-nodes-s35.csv")))
    track = np.array([[float(r["x"]), float(r["y"])] for r in csv.DictReader(open(f"{w}/pass1-track.csv"))])
    N = len(track)
    row = (N + 7) // 8
    raw = np.fromfile(f"{w}/pass1-bits-r1.bin", dtype=np.uint8).reshape(len(nodes), row)
    bits = np.unpackbits(raw, axis=1, bitorder="little")[:, :N].astype(bool)
    xy = np.array([[float(r["x"]), float(r["y"])] for r in nodes])
    cell = [(int(r["q"]), int(r["r"])) for r in nodes]
    yline = float(np.median(track[:, 1]))
    xmid = float(np.median(xy[:, 0]))
    rows, info = [], []
    for off in (float(o) for o in a.offsets.split(",")):
        cand = [i for i in range(len(nodes)) if abs(xy[i, 0] - xmid) < 300]
        i = min(cand, key=lambda i: abs(abs(xy[i, 1] - yline) - off))
        c0 = int(np.argmin(np.linalg.norm(track - xy[i], axis=1)))
        lo = min(max(c0 - a.span // 2, 0), N - a.span)
        one = bits[i, lo:lo + a.span]
        union = np.any(bits[[j for j in range(len(nodes)) if cell[j] == cell[i]], lo:lo + a.span], axis=0)
        rows += [one, union]
        info.append(f"{abs(xy[i, 1] - yline):.0f} m: node {one.sum()}/{a.span} (run {longest(one)}), "
                    f"cell {union.sum()}/{a.span} (run {longest(union)})")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    cmap = ListedColormap(["#d64541", "#e9eef1"])
    fig, ax = plt.subplots(figsize=(12, 0.42 * len(rows) + 0.6))
    gap = 0.5
    for k, r in enumerate(rows):
        y = -(k + (k // 2) * gap)
        ax.imshow(r[None, :].astype(int), cmap=cmap, vmin=0, vmax=1, aspect="auto", interpolation="nearest",
                  extent=(0, a.span, y - (0.85 if k % 2 == 0 else 0.6), y))
    ax.set_xlim(0, a.span)
    ax.set_ylim(-(len(rows) + (len(rows) // 2) * gap) - 0.2, 0.2)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(a.out, dpi=150)
    print("\n".join(info))


if __name__ == "__main__":
    main()
