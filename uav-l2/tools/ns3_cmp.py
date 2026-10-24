"""One row per map and design from ns-3 mission folders already run and their l1_rank output (CLAUDE.md §8
items 151, 156): team 1's tour, when it leaves the clusters, when River brings each critical cell its data, and T*.

    python3 tools/ns3_cmp.py OUT.md LABEL=GLOB:KIND:L1 [...]

GLOB: the mission folders (named by map, e.g. NS/chordB/k8-s*); KIND: kin (CHORD-T) or route (meander_lane);
L1: the --out prefix l1_rank.py wrote for them (L1-draws.csv, L1-cells.csv), its method
P+prog-KIND-puq-stage-zero-redir-kt. Columns: tour at 45 degree bank with the delivery fixes (kin_time), critical
cells, mean time team 1 leaves their clusters (kin_time leave, fixes included), River done (doneS of scheme rf:
mean / p90 / max), ready (leave + done, mean), the share of critical cells holding all 12 clues after River, mean T*
over the draws. Under each map: critical cells common to all designs / each design's.
"""
import csv, glob, os, sys
from collections import defaultdict

import numpy as np

import kin_time
from mission_report import load_map


def main():
    out, sets = sys.argv[1], []
    for arg in sys.argv[2:]:
        label, spec = arg.split("=", 1)
        g, kind, l1 = spec.rsplit(":", 2)
        sets.append((label, {os.path.basename(os.path.normpath(w)): w for w in sorted(glob.glob(g))}, kind, l1))
    rows = ["| bản đồ | phương án | tour 45° (s) | critical | rời cụm TB (s) | River xong TB / p90 / max (s) | "
            "sẵn sàng TB (s) | đủ 12 manh mối | T* TB (s) |", "|---" * 9 + "|"]
    for m in sorted(set.intersection(*(set(w) for _, w, _, _ in sets))):
        crit = []
        for label, works, kind, l1 in sets:
            w = works[m]
            _, o = kin_time.run(w, kind)
            M = load_map(w, schemes=("rf",), with_bits=False)
            leave = o[45]["leave"]
            cr = [(k, h, float(C["res"]["rf"][h]["doneS"])) for k, C in M["cl"].items() for h in C["P"]["crit"]]
            lv, dn = np.array([leave[k] for k, _, _ in cr]), np.array([d for _, _, d in cr])
            crit.append({h for _, h, _ in cr})
            allc = np.mean([int(r["riverAll"]) for r in csv.DictReader(open(f"{l1}-cells.csv")) if r["map"] == m])
            meth = f"P+prog-{kind}-puq-stage-zero-redir-kt"
            T = np.array([float(r["Tstar"]) for r in csv.DictReader(open(f"{l1}-draws.csv"))
                          if r["map"] == m and r["method"] == meth])
            rows.append(f"| {m} | {label} | {o[45]['profile'] + o[45]['fix']:.0f} | {len(cr)} | {lv.mean():.0f} | "
                        f"{dn.mean():.0f} / {np.percentile(dn, 90):.0f} / {dn.max():.0f} | {(lv + dn).mean():.0f} | "
                        f"{allc:.0%} | {T.mean():.0f} |")
        rows.append(f"| | critical chung | {len(set.intersection(*crit))} / " + " / ".join(str(len(c)) for c in crit)
                    + " | | | | | | |")
    open(out, "w").write("\n".join(rows) + "\n")
    print("\n".join(rows))


if __name__ == "__main__":
    main()
