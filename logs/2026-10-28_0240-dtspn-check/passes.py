"""CLAUDE.md §8 item 192: does the DTSP-N + River pass (zigzag through every critical cell's disc) fly slower than
CHORD's? Per cluster, from the campaign4 work folders (seed 1): the pass as flown (c{k}-path-s35.csv, column t from
pass_speed.fit), its length and time over the cluster's own cells, speed, turning, cap and loops (c{k}-speed.json).

    python3 passes.py ENV K
"""
import csv, json, math, os, sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uav-l2/tools"))
from map_gen import cell_at, centre  # noqa: E402

S = "/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/C4"
env, K = sys.argv[1], int(sys.argv[2])
rows = []
for s in ("CP", "LMD", "DR"):
    w = f"{S}/{s}/{env}/R1/k{K}-s1"
    n = json.load(open(f"{w}/map.json"))["clusters"]
    for k in range(1, n + 1):
        P = list(csv.DictReader(open(f"{w}/c{k}-path-s35.csv")))
        X = np.array([[float(r["x"]), float(r["y"])] for r in P])
        t = np.array([float(r["t"]) for r in P])
        keep = np.r_[True, np.linalg.norm(np.diff(X, axis=0), axis=1) > 0.5]   # repeated points: no heading
        X, t = X[keep], t[keep]
        own = {(int(x["q"]), int(x["r"])) for x in csv.DictReader(open(f"{w}/c{k}-lattice.csv")) if x["selected"] == "1"}
        d = np.linalg.norm(np.diff(X, axis=0), axis=1)
        mid = (X[1:] + X[:-1]) / 2
        inside = np.array([cell_at(*p) in own for p in mid])
        dt = np.diff(t)
        v = np.where(dt > 0, d / np.maximum(dt, 1e-9), np.nan)
        h = np.unwrap(np.arctan2(np.diff(X[:, 1]), np.diff(X[:, 0])))
        turn = np.abs(np.diff(h))
        sp = json.load(open(f"{w}/c{k}-speed.json"))
        xi = json.load(open(f"{S}/DR/{env}/R1/k{K}-s1/lm.json"))["xi"]
        crit = [(int(x["q"]), int(x["r"])) for x in csv.DictReader(open(f"{w}/r{k}-rf-crit.csv"))]
        near = sum(np.linalg.norm(X - centre(h), axis=1).min() <= xi + 1 for h in crit)
        rows.append(dict(scheme=s, k=k, L_in=d[inside].sum(), T_in=dt[inside].sum(), L=d.sum(), T=t[-1],
                         v_in=d[inside].sum() / max(dt[inside].sum(), 1e-9), vmin=np.nanmin(v[inside]) if inside.any() else np.nan,
                         turn_in=math.degrees(turn[inside[1:]].sum()), cap=sp["cap"], loops=sp["loops"],
                         crit=len(crit), near=near))
print(f"{env} k{K}-s1: per scheme, mean over clusters (and sum where marked)")
print("| scheme | in-cluster length m | in-cluster time s | mean speed in cluster m/s | slowest m/s | turning in cluster deg "
      "| cap m/s | loops (sum) | pass time s (sum) | critical cells within xi of the path |")
print("|---|---|---|---|---|---|---|---|---|---|")
for s in ("CP", "LMD", "DR"):
    R = [r for r in rows if r["scheme"] == s]
    m = lambda f: np.nanmean([r[f] for r in R])
    print(f"| {s} | {m('L_in'):.0f} | {m('T_in'):.1f} | {m('v_in'):.1f} | {np.nanmin([r['vmin'] for r in R]):.1f} | "
          f"{m('turn_in'):.0f} | {m('cap'):.1f} | {sum(r['loops'] for r in R)} | {sum(r['T'] for r in R):.0f} | "
          f"{sum(r['near'] for r in R)}/{sum(r['crit'] for r in R)} |")
print()
print("| k | CP L_in / T_in / cap | DR L_in / T_in / cap / turn / near |")
print("|---|---|---|")
for k in sorted({r["k"] for r in rows}):
    a = next(r for r in rows if r["scheme"] == "CP" and r["k"] == k)
    b = next(r for r in rows if r["scheme"] == "DR" and r["k"] == k)
    print(f"| {k} | {a['L_in']:.0f} / {a['T_in']:.1f} / {a['cap']:.1f} | {b['L_in']:.0f} / {b['T_in']:.1f} / {b['cap']:.1f} / {b['turn_in']:.0f} / {b['near']}/{b['crit']} |")
