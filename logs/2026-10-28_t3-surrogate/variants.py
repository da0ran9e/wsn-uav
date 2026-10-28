"""Tier 3 check (LightGBM-style surrogate vs the step-A formula): passes to fly in ns-3. Per cluster of k8-s1 and
channel, from LM-Tour's DTSP-N leg (the bearing of runs/LMD lm.json, the CH pinned): v0 the leg unbent, v1-v5
the leg bent into the disc B(c, xi) of one critical cell farther than xi (random order, seed k), then of two
when single ones run out; every pass crosses the cluster once. Variant j of every cluster goes into one folder
runs/T3v{j}/ENV/k8-s1 (a cluster without a j-th variant flies v0 again).

    python3 variants.py ENV
"""
import itertools, json, os, sys

import numpy as np

sys.path.insert(0, "/Users/mophan/Github/ns-3-dev-git-ns-3.46/src/wsn-uav/uav-l2/tools")
import lm_tour as LT  # noqa: E402
from mission_policy import R_TURN  # noqa: E402
from mission_report import load_map  # noqa: E402
from river_surrogate import Model  # noqa: E402

sys.path.insert(0, "/Users/mophan/Github/ns-3-dev-git-ns-3.46/src/wsn-uav/uav-coop2/tools")
from river_plan import hear_model  # noqa: E402

RUN = "/Users/mophan/Github/ns3-uav-build/runs"
NV = 6
env = sys.argv[1]
w = f"{RUN}/CP/{env}/k8-s1"
_, loss, around = LT.context(w)
xi = min(LT.OMEGA, R_TURN, LT.R50[env])
bearing = {int(k): b for k, b in json.load(open(f"{RUN}/LMD/{env}/k8-s1/lm.json"))["bearing"].items()}
M = load_map(w, schemes=(), with_bits=False)
model, hear = Model.load(LT.SURROGATE, "formula"), hear_model(loss)
var, log = {}, {}
for k in sorted(M["cl"]):
    c = LT.Cluster(w, M, k, model, hear, loss, around)
    ln = c.chord(bearing[k])
    base = c.rows([], xi, ln, pin=True)
    Q = np.array([[float(r["x"]), float(r["y"])] for r in base])
    cand = [h for h in M["cl"][k]["P"]["crit"] if np.linalg.norm(Q - c.geo["c"][h], axis=1).min() > xi]
    rng = np.random.default_rng(k)
    pulls = [[cand[i]] for i in rng.permutation(len(cand))]
    pulls += [list(p) for p in (itertools.combinations(cand, 2)) if len(cand) > 2]
    var[k], log[k] = [base], [[]]
    for p in pulls:
        if len(var[k]) == NV:
            break
        r = c.rows(p, xi, ln, pin=True)
        if c.once(r):
            var[k].append(r)
            log[k].append([list(h) for h in p])
    print(f"C{k}: bearing {bearing[k]}, {len(cand)} candidates beyond {xi:.0f} m, {len(var[k])} passes", flush=True)
for j in range(NV):
    LT.build(w, f"{RUN}/T3v{j}/{env}/k8-s1", {k: v[j] if j < len(v) else v[0] for k, v in var.items()})
os.makedirs(env, exist_ok=True)
json.dump(dict(xi=xi, bearing=bearing, pulls={k: v for k, v in log.items()}), open(f"{env}/variants.json", "w"),
          indent=1)
