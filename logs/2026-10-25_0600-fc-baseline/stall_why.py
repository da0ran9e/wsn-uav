"""Which packet each stalled critical cell lacks at River's deadline, which nodes and cells hold it, and its place on
the Axe (item 168 scoring; the River trace of stall-trace.sh).
    python3 stall_why.py WORK K [K ...]
"""
import csv, sys
from collections import defaultdict

sys.path.insert(0, "/home/user/wsn-uav/uav-l2/tools")
import numpy as np
from mission_report import load_map

w, ks = sys.argv[1], [int(k) for k in sys.argv[2:]]
M = load_map(w, schemes=("rf",))
for k in ks:
    cl = M["cl"][k]
    bits, mem = cl["bits"], cl["mem"]
    inD = bits.any(axis=0)
    need = {}
    axe = {}
    for l in open(f"{w}/plan{k}.txt"):
        f = l.split()
        if f[0] == "NEED":
            need[(int(f[1]), int(f[2]))] = (int(f[3]), int(f[4]))
        if f[0] == "AXE":
            axe[(int(f[1]), int(f[2]))] = (int(f[3]), int(f[4]))
    held = defaultdict(dict)
    for r in csv.DictReader(open(f"{w}/tr/t{k}-held.csv")):
        held[(int(r["q"]), int(r["r"]))][int(r["s"])] = float(r["t"])
    cellof = {v: h for h, ms in mem.items() for v in ms}
    for h in cl["P"]["crit"]:
        if float(cl["res"]["rf"][h]["doneS"]) >= 0:
            continue
        lo, hi = need[h]
        segs = [range(x, y + 1) for x, y in axe.values()]   # River's D: the Axe segments' packets someone holds
        miss = [s for s in range(lo, hi + 1) if inD[s] and any(s in g for g in segs) and s not in held[h]]
        for s in miss:
            hold_nodes = np.nonzero(bits[:, s])[0]
            seg = [a for a, (x, y) in axe.items() if x <= s <= y]
            print(f"C{k} crit {h}: lacks packet {s} (window {lo}-{hi}); Axe segment {seg}; held by "
                  f"{len(hold_nodes)} node(s) in cells {sorted({cellof.get(v) for v in hold_nodes})}; "
                  f"last packet it got at {max(held[h].values()):.1f} s")
