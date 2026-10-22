"""MEANDER-K partition only (no deploy): cluster count, CV and lane width on the 40 campaign maps."""
import math, sys, time
sys.path.insert(0, "/home/user/wsn-uav/uav-l2/tools")
import numpy as np
from meander import partition_meander
from partition import pieces
from restructure import CAP, domain

MAPS = ("k2-s10 k2-s11 k2-s20 k2-s23 k2-s25 k2-s3 k2-s4 k2-s5 k2-s8 k2-s9 k4-s1 k4-s11 k4-s12 k4-s13 k4-s16 k4-s2 "
        "k4-s20 k4-s21 k4-s5 k4-s9 k6-s11 k6-s12 k6-s13 k6-s15 k6-s16 k6-s17 k6-s2 k6-s20 k6-s4 k6-s9 k8-s1 k8-s10 "
        "k8-s11 k8-s2 k8-s4 k8-s5 k8-s6 k8-s7 k8-s8 k8-s9").split()
print("map,cells,K,lane,frag,cv,min,max")
for m in MAPS:
    K, seed = int(m[1]), int(m.split("-s")[1])
    land = set(domain(K, seed)["domain"])
    best = None
    for L in (6, 5.5, 6.5, 5, 7, 4.5, 7.5, 8):
        for frag in (0.25, 0.5):
            r = partition_meander(land, L, frag_share=frag, count=math.ceil(len(land) / CAP))
            sz = np.bincount(list(r[0].values()))
            whole = all(len(pieces([h for h in r[0] if r[0][h] == c])) == 1 for c in range(len(sz)))
            cv = float(sz.std() / sz.mean()) if whole else math.inf
            if best is None or cv < best[0]:
                best = (cv, L, frag, sz)
        if best[0] <= 0.11:
            break
    cv, L, frag, sz = best
    print(f"{m},{len(land)},{len(sz)},{L},{frag},{cv:.3f},{sz.min()},{sz.max()}", flush=True)
