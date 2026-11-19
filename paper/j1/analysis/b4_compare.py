"""K9 step B4: River measured in ns-3 against the surrogate cc_select.py optimised, on the critical-cell sets it chose.

    python3 b4_compare.py OUT_PREFIX WORK [WORK ...]

WORK: a b4_run.sh folder (OUT/<channel>/<tag>/, River run with scheme rf). Per critical cell: doneS measured (seconds
from the UAV leaving the cluster to the cell's CL holding its window; missing > 0 means not complete by the limit) and
predicted (river_surrogate formula, the model cc_select.py uses). Per cluster: T_k = the largest doneS. Per folder:
T1 = max_k (leave_k + T_k), measured and predicted. A cell not complete by River's limit (LIMIT s, mission.py) counts
as LIMIT, so its T_k and T1 are lower bounds (marked >=). Writes OUT_PREFIX.md and OUT_PREFIX.csv (one row per cell).
"""
import csv, json, os, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, f"{HERE}/../../../uav-l2/tools", f"{HERE}/../../../uav-coop2/tools"]
import river_surrogate as RS  # noqa: E402
from cc_select import SURR  # noqa: E402
from mission_report import load_map  # noqa: E402
from river_plan import hear_model, load_around  # noqa: E402

out, works = sys.argv[1], sys.argv[2:]
LIMIT = 900.0   # mission.py runs River with --limit=900
model = RS.Model.load(SURR, "formula")
rows, summ = [], []
for W in works:
    W = W.rstrip("/")
    ch, tag = W.split("/")[-2:]
    M = load_map(W, schemes=())
    loss = json.load(open(f"{W}/plan-opts.json"))["lossDb"]
    around, hear = load_around(f"{W}/domain-cl.csv"), hear_model(loss)
    leave = {l["cluster"]: l["leave"] for l in json.load(open(f"{W}/tour.json"))["legs"]}
    Tm, Tp, err, incomplete, n = {}, {}, [], 0, 0
    for k, c in M["cl"].items():
        P = RS.mission_plan(c["geo"], around, loss)
        F = RS.features(c["geo"], P, loss, hear)
        pred = dict(zip(P["crit"], model.predict([F[h] for h in P["crit"]])))
        meas = {(int(r["q"]), int(r["r"])): r for r in csv.DictReader(open(f"{W}/r{k}-rf-crit.csv"))}
        assert set(meas) == set(pred), (W, k)
        for h, r in meas.items():
            miss = int(r["missing"])
            incomplete += miss > 0
            n += 1
            d = float(r["doneS"])
            rows.append([ch, tag, k, h[0], h[1], f"{pred[h]:.1f}", f"{d:.1f}", miss])
            if miss == 0:
                err.append(pred[h] - d)
        Tm[k] = max(LIMIT if int(r["missing"]) else float(r["doneS"]) for r in meas.values())
        Tp[k] = max(pred.values())
    e = np.array(err)
    tk = np.array([Tp[k] - Tm[k] for k in Tm])
    summ.append(dict(ch=ch, tag=tag, n=n, inc=incomplete, mae=np.abs(e).mean(), bias=e.mean(),
                     tk_mae=np.abs(tk).mean(), tk_bias=tk.mean(),
                     T1m=max(leave[k] + Tm[k] for k in Tm), T1p=max(leave[k] + Tp[k] for k in Tp), Tm=Tm, Tp=Tp))
with open(out + ".csv", "w") as f:
    w = csv.writer(f)
    w.writerow(["channel", "set", "cluster", "q", "r", "doneS_pred", "doneS_ns3", "missing"])
    w.writerows(rows)
with open(out + ".md", "w") as f:
    f.write("# K9 B4: River in ns-3 against the surrogate, on the chosen critical-cell sets (k8, seed 1)\n\n"
            "Error = predicted minus measured, seconds, over the cells complete by the limit. T_k: last critical cell of "
            "the cluster (from leaving it). T1: last critical cell of the mission, from take-off. A cell not complete by the "
            f"limit counts as {LIMIT:.0f} s, so its T_k and T1 are lower bounds (>=).\n\n"
            "| channel | set | critical cells | not complete | cell MAE | cell bias | T_k MAE | T_k bias | T1 ns-3 | "
            "T1 model |\n|---|---|---|---|---|---|---|---|---|---|\n")
    for s in summ:
        f.write(f"| {s['ch']} | {s['tag']} | {s['n']} | {s['inc']} | {s['mae']:.1f} | {s['bias']:+.1f} | "
                f"{s['tk_mae']:.1f} | {s['tk_bias']:+.1f} | {'>=' if s['inc'] else ''}{s['T1m']:.0f} | {s['T1p']:.0f} |\n")
    ks = sorted(summ[0]["Tm"])
    f.write("\nT_k per cluster, model / ns-3 (seconds; >= not complete by the limit)\n\n| channel | set | "
            + " | ".join(f"c{k}" for k in ks) + " |\n|---|---|" + "---|" * len(ks) + "\n")
    for s in summ:
        f.write(f"| {s['ch']} | {s['tag']} | " + " | ".join(
            f"{s['Tp'][k]:.0f} / {'>=' if s['Tm'][k] >= LIMIT else ''}{s['Tm'][k]:.0f}" for k in ks) + " |\n")
print(open(out + ".md").read())
