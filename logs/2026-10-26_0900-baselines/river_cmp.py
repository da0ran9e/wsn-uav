"""River (rf) vs direct pull (d) on ns-3, per channel and map: critical-cell completion and transmissions.

    python3 river_cmp.py FIX
"""
import csv, glob, os, sys

import numpy as np

fix = sys.argv[1]
print("| kênh | bản đồ | cell | xong TB rf / d (s) | xong max rf / d (s) | kẹt rf / d | cell d nhanh hơn | "
      "lượt truyền rf / d (nghìn) | MAC lỗi rf / d (nghìn) |")
print("|---|---|---|---|---|---|---|---|---|")
for e in ("open", "r500", "r200", "r100"):
    for m in ("k8-s1", "k12-s1", "k16-s1"):
        w = f"{fix}/{e}/{m}"
        crit, runs = {}, {}
        for s in ("rf", "d"):
            crit[s] = {(r["run"], r["q"], r["r"]): r for f in sorted(glob.glob(f"{w}/r*-{s}-crit.csv"))
                       for r in csv.DictReader(open(f))}
            runs[s] = [r for f in sorted(glob.glob(f"{w}/r*-{s}-runs.csv")) for r in csv.DictReader(open(f))]
        keys = sorted(crit["rf"])
        assert keys == sorted(crit["d"]), w
        stall = {s: sum(float(crit[s][k]["doneS"]) < 0 or int(crit[s][k]["missing"]) > 0 for k in keys) for s in crit}
        done = {s: np.array([float(crit[s][k]["doneS"]) for k in keys]) for s in crit}
        ok = (done["rf"] >= 0) & (done["d"] >= 0)
        faster = int(((done["d"] < done["rf"]) & ok).sum())
        tx = {s: sum(int(r["hops"]) for r in runs[s]) / 1000 for s in runs}
        mf = {s: sum(int(r["macFail"]) for r in runs[s]) / 1000 for s in runs}
        print(f"| {e} | {m} | {len(keys)} | {done['rf'][ok].mean():.0f} / {done['d'][ok].mean():.0f} | "
              f"{done['rf'][ok].max():.0f} / {done['d'][ok].max():.0f} | {stall['rf']} / {stall['d']} | "
              f"{faster}/{int(ok.sum())} | {tx['rf']:.0f} / {tx['d']:.0f} | {mf['rf']:.0f} / {mf['d']:.0f} |")
