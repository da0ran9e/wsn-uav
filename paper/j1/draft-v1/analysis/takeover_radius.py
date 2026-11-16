"""Deviation-adaptive query radius for takeover, evaluated offline on the ns-3 wind passes (experiment WND/TKO:
k8-s1, channel r100, sigma 50 m x 3 seeds, 100 m x 3, 200 m x 1; real pass bitmaps and tracks, no new simulation).

    python3 takeover_radius.py WIND_DIR OUT_PREFIX

For every SPINE cell a whose segment has packets heard by no node of a or of an adjacent cell but held elsewhere
("activated with holders"), the query must reach the farthest holder cell, h_a cell hops away (BFS over gateway links).
Rules compared:
  fixed h          flood h cell hops (the simulated takeover used h = 3)
  adaptive         h = ceil(e_hat / (sqrt(3) R)) + 1, e_hat = largest cross-track deviation among the packets that a or
                   an adjacent cell did hear within +-W packets of Seg(a) (positions are in the packet headers);
                   if they heard none, h = H_MAX
  adaptive (true e) the same rule with the true deviation of Seg(a) (upper reference)
Reported: activated cells whose farthest holder is inside the flood, and cells flooded per query.
Writes OUT_PREFIX.md.
"""
import csv, collections, math, sys
import numpy as np

W, OUT = sys.argv[1:3]
ADJ = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]
RCELL, WIN, H_MAX = 100.0, 300, 5
hop_rule = lambda e: math.ceil(e / (math.sqrt(3) * RCELL)) + 1
res = collections.defaultdict(list)
for sig, R in [(50, 1), (50, 2), (50, 3), (100, 1), (100, 2), (100, 3), (200, 1)]:
    w = f"{W}/s{sig}/R{R}/k8-s1"
    for k in range(1, 9):
        nodes = list(csv.DictReader(open(f"{w}/c{k}-nodes-s35.csv")))
        cell = [(int(n["q"]), int(n["r"])) for n in nodes]
        mem = collections.defaultdict(list)
        for i, c in enumerate(cell): mem[c].append(i)
        gw = set()
        for r in csv.DictReader(open(f"{w}/c{k}-gateways-s35.csv")):
            A, B = (int(r["qA"]), int(r["rA"])), (int(r["qB"]), int(r["rB"])); gw |= {(A, B), (B, A)}
        lines = open(f"{w}/plan{k}.txt").read().split("\n"); N = int(lines[0].split()[1])
        seg = {(int(q[1]), int(q[2])): (int(q[3]), int(q[4])) for q in (l.split() for l in lines) if q and q[0] == "AXE"}
        trk = np.array([[float(r["x"]), float(r["y"])] for r in csv.DictReader(open(f"{w}/pass{k}-track.csv"))])[:N]
        plan = np.array([[float(r["x"]), float(r["y"])] for r in csv.DictReader(open(f"{w}/c{k}-path-s35.csv"))])
        dev = np.array([np.min(np.hypot(plan[:, 0] - p[0], plan[:, 1] - p[1])) for p in trk])
        raw = np.fromfile(f"{w}/pass{k}-bits-r1.bin", dtype=np.uint8).reshape(len(nodes), -1)
        got = np.unpackbits(raw, axis=1, bitorder="little")[:, :N].astype(bool)
        cellgot = {c: got[ids].any(0) for c, ids in mem.items()}
        for a, (f, l) in seg.items():
            l = min(l, N - 1); s = np.arange(f, l + 1)
            nb = [a] + [(a[0] + d[0], a[1] + d[1]) for d in ADJ if (a, (a[0] + d[0], a[1] + d[1])) in gw]
            heard_nb = np.any([cellgot[c] for c in nb], axis=0)
            miss = s[~heard_nb[s]]
            if not len(miss): continue
            par, order = {a: 0}, [a]
            for c in order:
                for d in ADJ:
                    c2 = (c[0] + d[0], c[1] + d[1])
                    if c2 in par or c2 not in mem or (c, c2) not in gw: continue
                    par[c2] = par[c] + 1; order.append(c2)
            h = 0
            for t in miss:
                b = next((c for c in order if c not in nb and cellgot[c][t]), None)
                if b is not None: h = max(h, par[b])
            if h == 0: continue                                  # packets nobody heard: takeover cannot help
            lo, hi = max(0, f - WIN), min(N, l + WIN + 1)
            near = np.arange(lo, hi)[heard_nb[lo:hi]]
            e_hat = dev[near].max() if len(near) else None
            ball = lambda hh: sum(1 for c in order if 0 < par[c] <= hh)
            rules = {"fixed 2": 2, "fixed 3": 3, "fixed 4": 4, "fixed 5": 5,
                     "adaptive": hop_rule(e_hat) if e_hat is not None else H_MAX,
                     "adaptive (true e)": hop_rule(dev[s].max())}
            for name, hh in rules.items():
                res[(sig, name)].append((h <= hh, ball(hh), hh, e_hat is None))
out = ["| sigma (m) | rule | activated cells with holders | farthest holder inside the flood | mean hops flooded | mean cells flooded | no estimate (fallback) |",
       "|---|---|---|---|---|---|---|"]
for sig in (100, 200):
    for name in ("fixed 2", "fixed 3", "fixed 4", "fixed 5", "adaptive", "adaptive (true e)"):
        v = res[(sig, name)]
        if v: out.append(f"| {sig} | {name} | {len(v)} | {sum(x[0] for x in v)} | {np.mean([x[2] for x in v]):.2f} | {np.mean([x[1] for x in v]):.1f} | {sum(x[3] for x in v)} |")
out.append(f"\nsigma = 50 m: {len(res[(50, 'fixed 3')])} activated cells with holders.")
open(OUT + ".md", "w").write("\n".join(out) + "\n"); print("\n".join(out))
