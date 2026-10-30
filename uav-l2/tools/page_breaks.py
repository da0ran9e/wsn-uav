"""Image boundaries for the Trickle baseline's pages (uav-coop2-river --pageBreaks; reviewer: pages aligned to images).

    python3 tools/page_breaks.py WORK

Writes WORK/pages{k}.txt per cluster: the packet indices where a clue image starts. The clue set is laid on the Axe
packets as l1_rank.holdings lays it: one copy in broadcast order (interleaved) from the start of the River window
around the CH, copies repeated before and after it along the Axe. A Trickle page then never spans two images.
"""
import os, sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import l1_model as L
from l1_rank import WINDOW
from mission_report import load_map

w = sys.argv[1]
M = load_map(w, schemes=(), with_bits=False)
C = L.clues()
st, en, Q = L.layout(C, L.order(C, "interleaved"))
for k, cl in M["cl"].items():
    P, uav = cl["P"], cl["geo"]["uav"]
    allp = np.array(sorted(s for a in P["axe"] for s in P["seg"][a]))
    n = len(allp)
    ch = next(x for x in cl["geo"]["nodes"] if x["isCH"] == "1")
    c0 = int(np.argmin(np.linalg.norm(uav - [float(ch["x"]), float(ch["y"])], axis=1)))
    i0 = min(max(int(np.searchsorted(allp, c0)) - WINDOW // 2, 0), n - WINDOW) if n > WINDOW else 0
    starts = sorted({int(allp[i]) for kk in range(-(i0 // Q) - 1, (n - i0) // Q + 1) for j in range(len(C))
                     for i in [i0 + kk * Q + st[j]] if 0 <= i < n})
    with open(f"{w}/pages{k}.txt", "w") as f:
        f.write("\n".join(map(str, starts)) + "\n")
    print(f"c{k}: {len(starts)} image starts on {n} Axe packets (copy {Q} packets)")
