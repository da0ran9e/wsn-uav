"""CLAUDE.md §8 item 192: how long would a real zigzag through every critical cell be? Per cluster of kK-s1 (the
campaign4 CHORD folder, seed 1): the shortest open path through all its critical-cell centres (exact for n <= 9,
Held-Karp), less 2 xi per interior visit and xi at each end (the discs B(v, xi) let the path cut corners), as a lower
bound on the in-cluster length L of a pass that enters every disc; its time at 50 m/s against the 40.4 s that one
clue-set copy needs over the cluster anyway.

    python3 zigzag_bound.py ENV K
"""
import csv, itertools, json, math, os, sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uav-l2/tools"))
from map_gen import centre  # noqa: E402

S = "/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/C4"
env, K = sys.argv[1], int(sys.argv[2])
w = f"{S}/CP/{env}/R1/k{K}-s1"
xi = json.load(open(f"{S}/DR/{env}/R1/k{K}-s1/lm.json"))["xi"] if os.path.exists(f"{S}/DR/{env}/R1/k{K}-s1/lm.json") \
    else {"open": 255, "r500": 255, "r200": 199, "r100": 99}[env]
n = json.load(open(f"{w}/map.json"))["clusters"]
CLUE_S = 40.41


def open_tsp(P):
    m = len(P)
    if m <= 1:
        return 0.0
    D = np.linalg.norm(P[:, None] - P[None], axis=2)
    best = {}
    for j in range(m):
        best[(1 << j, j)] = 0.0
    for size in range(2, m + 1):
        for sub in itertools.combinations(range(m), size):
            mask = sum(1 << j for j in sub)
            for j in sub:
                pm = mask ^ (1 << j)
                best[(mask, j)] = min(best[(pm, i)] + D[i, j] for i in sub if i != j)
    full = (1 << m) - 1
    return min(best[(full, j)] for j in range(m))


tot_lb, tot_need = 0.0, 0.0
print(f"{env} k{K}-s1, xi = {xi:.0f} m: per cluster, critical cells, open TSP over their centres (m), lower bound on a "
      "pass entering every disc (m), its time at 50 m/s against the 40.4 s needed anyway")
print("| k | crit | TSP m | bound m | bound s at 50 m/s | in-cluster time s (max of the two) |")
print("|---|---|---|---|---|---|")
for k in range(1, n + 1):
    crit = [(int(x["q"]), int(x["r"])) for x in csv.DictReader(open(f"{w}/r{k}-rf-crit.csv"))]
    P = np.array([centre(h) for h in crit], float)
    L = open_tsp(P) if len(P) <= 9 else float("nan")
    lb = max(0.0, L - 2 * xi * max(len(P) - 2, 0) - 2 * xi)
    t = max(CLUE_S, lb / 50)
    tot_lb += t
    tot_need += CLUE_S
    print(f"| {k} | {len(P)} | {L:.0f} | {lb:.0f} | {lb / 50:.1f} | {t:.1f} |")
print(f"\nSum over clusters: at least {tot_lb:.0f} s in the clusters against {tot_need:.0f} s for the delivery alone "
      f"(+{tot_lb - tot_need:.0f} s).")
