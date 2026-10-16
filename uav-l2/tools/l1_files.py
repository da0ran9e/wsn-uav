"""Layer 1 seen from the pass (CLAUDE.md §8 item 85): complete query files a critical cell holds right after the
pass, before River, for file sizes from the layer-1 report (reports/Nhận dạng tại node biên lớp 1.md).

    python3 tools/l1_files.py --works "W/k*" "W/camp/k*" --out docs/data/mission/l1-files.csv

D of a cluster (the packets of its Axe segments, in broadcast order) is cut into consecutive files of F frames;
a file counts only if every frame of it is held (CLAUDE.md §8 item 34). Holders: the critical cell's best node
alone (no cooperation at all), and the cell (its nodes pooled, intra-cell gathering only: B4).
QUERIES: a query of V distinct files of F frames each, broadcast over and over along D (file j at copies j, j+V,
...); full = the holder has at least one complete copy of every distinct file.
"""
import argparse, csv, glob, os

import numpy as np

from mission_report import load_map

QUERIES = [(4, 11), (4, 50), (4, 150), (12, 150), (40, 100)]   # (distinct files, frames each)
SIZES = {1: "64 B code", 6: "int8 512-d", 11: "fp16 512-d", 21: "fp32 512-d", 50: "~5 kB crop", 150: "~15 kB crop"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--works", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rows = []
    for w in sorted(f for g in a.works for f in glob.glob(g) if os.path.isdir(f)):
        M = load_map(w, schemes=("rf",))
        for k, C in M["cl"].items():
            bits, inD = C["bits"], C["inD"]
            idx = np.flatnonzero(inD)
            for h in C["P"]["crit"]:
                mem = C["mem"][h]
                for who, got in (("node", bits[mem][:, idx]), ("cell", bits[mem][:, idx].any(axis=0, keepdims=True))):
                    for F in SIZES:
                        n = len(idx) // F
                        ok = got[:, :n * F].reshape(len(got), n, F).all(axis=2).sum(axis=1).max()
                        rows.append(dict(map=M["name"], cluster=k, q=h[0], r=h[1], who=who, F=F, files=n,
                                         complete=int(ok), frac=round(ok / n, 4), V="", full=""))
                    for V, F in QUERIES:   # a query of V distinct files of F frames, repeated along D
                        n = len(idx) // F
                        whole = got[:, :n * F].reshape(len(got), n, F).all(axis=2)   # holder x file copy
                        have = [whole[:, j::V].any(axis=1) for j in range(V)]          # holder x distinct file
                        best = max(int(sum(hv[i] for hv in have)) for i in range(len(got)))
                        rows.append(dict(map=M["name"], cluster=k, q=h[0], r=h[1], who=who, F=F, files=n,
                                         complete=best, frac=round(best / V, 4), V=V, full=int(best == V)))
    with open(a.out, "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)
    for who in ("node", "cell"):
        for V, F in QUERIES:
            rs = [r for r in rows if r["who"] == who and r["V"] == V and r["F"] == F]
            print(f"{who:4s} query {V:2d} files x {F:3d} frames ({V * F:4d} frames): every file complete in "
                  f"{np.mean([r['full'] for r in rs]):.2f} of critical cells, files held mean {np.mean([r['frac'] for r in rs]):.2f}")
    for who in ("node", "cell"):
        for F, name in SIZES.items():
            v = np.array([r["frac"] for r in rows if r["who"] == who and r["F"] == F and r["V"] == ""])
            print(f"{who:4s} F={F:3d} ({name:12s}): complete files mean {v.mean():.2f}, p10 {np.quantile(v, .1):.2f}, "
                  f"min {v.min():.2f}; cells with >= 4 files {np.mean([r['complete'] >= 4 for r in rows if r['who'] == who and r['F'] == F and r['V'] == '']):.2f}")


if __name__ == "__main__":
    main()
