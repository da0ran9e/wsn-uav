"""Where does River's ground time go? Per-medium load from a per-hop trace of coop2-river (--trace).

    python3 trace_media.py WORK K TRACE_PREFIX

WORK holds c<K>-nodes-s35.csv and plan<K>.txt. A hop inside a cell uses that cell's medium, a hop between two cells the
gateway pair's. Prints, per phase, the frames; the busiest cell media with their roles, their frames per phase, the span
in which they carry 90 % of their frames and their utilisation there (frames x median service time / span); and, for
every critical cell, the frames of its own medium and the time its CL received 50 % / 90 % / 100 % of its packets.
"""
import csv, sys, collections
import numpy as np
W, K, TR = sys.argv[1:4]
cell = {int(r["id"]): (int(r["q"]), int(r["r"])) for r in csv.DictReader(open(f"{W}/c{K}-nodes-s35.csv"))}
cl = {(int(r["q"]), int(r["r"])): int(r["id"]) for r in csv.DictReader(open(f"{W}/c{K}-nodes-s35.csv")) if r["isCL"] == "1"}
role = collections.defaultdict(set)
for l in open(f"{W}/plan{K}.txt"):
    p = l.split()
    if not p: continue
    if p[0] == "AXE": role[(int(p[1]), int(p[2]))].add("axe")
    if p[0] == "CRIT": role[(int(p[1]), int(p[2]))].add("CRIT")
    if p[0] == "BANK": role[(int(p[4]), int(p[5]))].add("bank")
    if p[0] == "CIRC": role[(int(p[3]), int(p[4]))].add("member")
T = collections.defaultdict(list); PH = collections.defaultdict(collections.Counter); tot = collections.Counter()
tmax = 0
for r in csv.DictReader(open(TR + "-hops.csv")):
    a, b = cell[int(r["from"])], cell[int(r["to"])]
    m = a if a == b else ("pair", min(a, b), max(a, b))
    t = float(r["t"]); T[m].append(t); PH[m][r["phase"]] += 1; tot[r["phase"]] += 1; tmax = max(tmax, t)
print("frames per phase:", dict(tot), "| last hop at", round(tmax, 1), "s")
gaps = np.concatenate([np.diff(np.sort(v)) for v in T.values() if len(v) > 50])
tau = float(np.median(gaps[gaps < 0.05])); print(f"median service time on a busy medium: {tau*1e3:.2f} ms")
cells = sorted([m for m in T if m[0] != "pair"], key=lambda m: -len(T[m]))
print("\nbusiest cell media: cell, roles, frames, by phase, span of the middle 90 % (s), utilisation in it")
for m in cells[:14]:
    t = np.sort(T[m]); lo, hi = np.percentile(t, [5, 95])
    print(f"  {m} {sorted(role[m]) or ['relay']} {len(t)} {dict(PH[m])} [{lo:.0f}, {hi:.0f}] {0.9*len(t)*tau/(hi-lo):.2f}")
pairs = sorted([m for m in T if m[0] == "pair"], key=lambda m: -len(T[m]))
print("busiest gateway pairs:", [(m[1], m[2], len(T[m])) for m in pairs[:5]])
print(f"cell media carry {sum(len(T[m]) for m in cells)} frames, gateway pairs {sum(len(T[m]) for m in pairs)}")
held = collections.defaultdict(list)
for r in csv.DictReader(open(TR + "-held.csv")):
    held[(int(r["q"]), int(r["r"]))].append(float(r["t"]))
print("\ncritical cells: frames on own medium, by phase, utilisation over [gather end, done], arrival quantiles (s)")
for k in sorted(c for c in role if "CRIT" in role[c]):
    t = np.sort(T[k]); a = np.sort([x for x in held[k] if x > 0])
    q = np.percentile(a, [10, 50, 90, 100]) if len(a) else [0] * 4
    print(f"  {k}: {len(t)} {dict(PH[k])} util {len(t)*tau/max(q[3]-q[0],1e-9):.2f}; packets by network {len(a)}; 10/50/90/100 % at {q[0]:.0f}/{q[1]:.0f}/{q[2]:.0f}/{q[3]:.0f}")
