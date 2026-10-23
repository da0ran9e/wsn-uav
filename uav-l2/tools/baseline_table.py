"""One quick comparison table of the proposal, its ablations and the baselines (CLAUDE.md §8 item 139).

    python3 tools/baseline_table.py OUT.md ROW [ROW ...]      ROW = label=DRAWS.csv:SET:METHOD[:FOLDERS:TAG]

The first row is the reference (P*). Per row: mean T* over every map and draw, its p90, the mean T* per map size,
the paired difference to the reference (per map, then averaged; on how many maps the reference is faster) and,
when FOLDERS (a glob of work folders named by map) and TAG (a River scheme: rf, d, t) are given, the ground MAC
frames per map (hops of every cluster's r<k>-<TAG>-runs.csv). METHOD may list tour kinds as kin|skin: the better
per map (as for k-medoids in PROPOSE-ITER-vi.md).
"""
import csv, glob, os, statistics as st, sys
from collections import defaultdict

import numpy as np


def load(path, sname, method):
    T = defaultdict(list)
    meths = [method.replace("kin|skin", t) for t in ("kin", "skin")] if "kin|skin" in method else [method]
    for r in csv.DictReader(open(path)):
        if r["set"] == sname and r["method"] in meths:
            T[(r["map"], r["method"])].append(float(r["Tstar"]))
    out = {}
    for m in {k[0] for k in T}:
        out[m] = min((T[(m, x)] for x in meths if (m, x) in T), key=st.mean)
    return out


def frames(folders, tag):
    out = {}
    for w in glob.glob(folders):
        runs = sorted(glob.glob(f"{w}/r*-{tag}-runs.csv"))
        if runs:
            out[os.path.basename(os.path.normpath(w))] = sum(int(next(csv.DictReader(open(f)))["hops"]) for f in runs)
    return out


def main():
    out, rows = sys.argv[1], sys.argv[2:]
    data = []
    for row in rows:
        label, spec = row.split("=", 1)
        parts = spec.split(":")
        T = load(parts[0], parts[1], parts[2])
        F = frames(parts[3], parts[4]) if len(parts) > 4 else {}
        data.append((label, T, F))
    ref = data[0][1]
    sizes = ("k2", "k4", "k6", "k8")
    lines = ["| Phương án | T\\* TB | p90 | " + " | ".join(sizes) + " | ΔT\\* so với P\\* (P\\* nhanh hơn) | khung mặt đất / bản đồ |",
             "|---|" + "---|" * (len(sizes) + 4)]
    for label, T, F in data:
        maps = sorted(T)
        allT = [t for m in maps for t in T[m]]
        per = [" %.0f" % np.mean([t for m in maps if m.startswith(z + "-") for t in T[m]])
               if any(m.startswith(z + "-") for m in maps) else " –" for z in sizes]
        common = [m for m in maps if m in ref]
        d = [st.mean(T[m]) - st.mean(ref[m]) for m in common]
        delta = "–" if T is ref else "%+.0f s (%d/%d)" % (np.mean(d), sum(x > 0 for x in d), len(d))
        fr = "%.0f k" % (np.mean([F[m] for m in maps if m in F]) / 1000) if F else "–"
        lines.append(f"| {label} | {np.mean(allT):.0f} | {np.percentile(allT, 90):.0f} |" + " |".join(per)
                     + f" | {delta} | {fr} |")
    open(out, "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
