"""Paired comparison of the validation sets (CLAUDE.md §8 item 136): per map, l1_rank draws and l2_metrics rows.

    python3 compare.py DRAWS.csv L2M.csv

T* of a partition = its P* (P+prog-<tour>-puq-stage-zero-redir) with its own tour kind: kmedoids the better of kin and
skin per map (both are flyable), the SWATH sets skin. Differences are paired by map (same world, same draws).
"""
import csv, sys, statistics as st
from collections import defaultdict

draws, l2m = sys.argv[1], sys.argv[2]
T = defaultdict(list)
for r in csv.DictReader(open(draws)):
    T[(r["set"], r["map"], r["method"])].append(float(r["Tstar"]))
mean = {k: st.mean(v) for k, v in T.items()}
p90 = {k: sorted(v)[int(0.9 * len(v)) - 1] for k, v in T.items()}
P = lambda tour: f"P+prog-{tour}-puq-stage-zero-redir"
sets = sorted({k[0] for k in T})
maps = sorted({k[1] for k in T}, key=lambda m: (int(m[1]), int(m.split("-s")[1])))


def tstar(s, m, q=mean):
    if s == "kmedoids":
        return min(q[(s, m, P(t))] for t in ("kin", "skin") if (s, m, P(t)) in q)
    return q[(s, m, P("skin"))]


L2 = {(r["set"], r["map"]): r for r in csv.DictReader(open(l2m))}
print("map    " + "".join(f"{s:>22}" for s in sets))
for m in maps:
    print(f"{m:7}" + "".join(f"{tstar(s, m):10.0f} (p90 {tstar(s, m, p90):5.0f})" for s in sets if (s, m, P('skin')) in T))
for s in sets:
    if s == "kmedoids":
        continue
    for size in ("k2", "k4", "k6", "k8", "all"):
        ms = [m for m in maps if (size == "all" or m.startswith(size + "-")) and (s, m, P("skin")) in T]
        d = [tstar(s, m) - tstar("kmedoids", m) for m in ms]
        d9 = [tstar(s, m, p90) - tstar("kmedoids", m, p90) for m in ms]
        dl = {f: [float(L2[(s, m)][f]) - float(L2[("kmedoids", m)][f]) for m in ms if (s, m) in L2 and ("kmedoids", m) in L2]
              for f in ("team1", "readyMean", "readyLast", "frames")}
        print(f"{s} - kmedoids, {size}: {len(ms)} maps; T* {st.mean(d):+.0f} s (better on {sum(x < 0 for x in d)}), "
              f"p90 {st.mean(d9):+.0f} s; team1 {st.mean(dl['team1']):+.0f} s, ready mean {st.mean(dl['readyMean']):+.0f} s, "
              f"ready last {st.mean(dl['readyLast']):+.0f} s, River frames {st.mean(dl['frames']) / 1000:+.0f} k")
