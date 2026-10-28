"""Tier 3 check: does a learned River surrogate (gradient-boosted trees, monotone, LightGBM's settings of the
guide) choose a cluster's pass better than the step-A formula (Tier 2)?

Test: k8-s1, per channel and cluster, the passes of runs/T3v0-5 (variants.py) and of CP, LM, LMD, DR, each with
ns-3 River's doneS of every critical cell. A cluster's River cost of a pass is S = sum of doneS over its critical
cells (the part of J_k a surrogate predicts). Models fitted on the other maps (k12-s1, k16-s1 of
river-surrogate.csv; setting A) or on those plus the test passes of k8's other clusters (setting B,
leave-one-cluster-out). Per (channel, cluster): Spearman of predicted and true S over its passes, and the regret
of the pass the model picks (true S of the pick minus the best true S). Cell level: MAE of doneS.

    python3 t3.py > table.md
"""
import csv, hashlib, os, sys

import numpy as np
from scipy.stats import spearmanr
from sklearn.ensemble import HistGradientBoostingRegressor

sys.path.insert(0, "/Users/mophan/Github/ns-3-dev-git-ns-3.46/src/wsn-uav/uav-l2/tools")
import river_surrogate as RS  # noqa: E402

RUN = "/Users/mophan/Github/ns3-uav-build/runs"
HERE = os.path.dirname(os.path.abspath(__file__))
ENVS = ("open", "r500", "r200", "r100")
SETS = [f"T3v{j}" for j in range(6)] + ["CP", "LM", "LMD", "DR"]
MONO = dict(hops=1, dpath=1, lackCell=1, lackCL=1, shareLack=1, cluLack=1)


class HGB:
    """Tier 3: boosted trees as the guide's LightGBM (400 trees, learning rate 0.05), monotone in the distance
    and the expected losses."""

    def __init__(self, rows):
        self.cols = RS.FEATS
        self.f = HistGradientBoostingRegressor(max_iter=400, learning_rate=0.05, min_samples_leaf=20, random_state=0,
                                               monotonic_cst=[MONO.get(c, 0) for c in self.cols])
        self.f.fit(self.X(rows), [r["doneS"] for r in rows])

    def X(self, rows):
        return np.array([[float(r[c]) for c in self.cols] for r in rows])

    def predict(self, rows):
        return self.f.predict(self.X(rows))


MODELS = dict(formula=lambda r: RS.Model("formula", r), linear=lambda r: RS.Model("linear", r),
              trees=lambda r: RS.Model("trees", r), hgb=HGB)


def test_rows():
    """Cells of every test pass, with the pass's identity; identical passes of a cluster kept once."""
    out, seen = [], set()
    for env in ENVS:
        for s in SETS:
            w = f"{RUN}/{s}/{env}/k8-s1"
            if not os.path.exists(f"{w}/plan1.txt"):
                continue
            try:
                rows = RS.dataset([w])
            except Exception as e:   # noqa: BLE001
                print(f"<!-- {s} {env}: skipped ({e!r}) -->")
                continue
            for k in sorted({r["cluster"] for r in rows}):
                key = (env, k, hashlib.md5(open(f"{w}/c{k}-path-s35.csv", "rb").read()).hexdigest())
                if key in seen:
                    continue
                seen.add(key)
                out += [dict(r, path=s) for r in rows if r["cluster"] == k]
    return out


def main():
    old = [{k: (v if k in ("map", "env") else float(v)) for k, v in r.items()}
           for r in csv.DictReader(open(os.path.join(os.path.dirname(RS.__file__),
                                                     "../docs/data/results/river-surrogate.csv")))]
    train = [r for r in old if r["map"] != "k8-s1"]
    test = test_rows()
    with open(f"{HERE}/cells.csv", "w") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(test[0]), lineterminator="\n")
        wr.writeheader()
        wr.writerows(test)
    groups = sorted({(r["env"], r["cluster"]) for r in test})
    npaths = [len({r["path"] for r in test if (r["env"], r["cluster"]) == g}) for g in groups]
    print(f"# Tier 3 check, k8-s1\n\n{len(test)} cell results, {len(groups)} (channel, cluster) groups, "
          f"{sum(npaths)} passes ({min(npaths)}-{max(npaths)} a group); training {len(train)} cells of k12, k16.\n")
    y = np.array([r["doneS"] for r in test])
    pred = {}
    for name, mk in MODELS.items():
        pred[("A", name)] = mk(train).predict(test)
        P = np.zeros(len(test))
        for k in sorted({r["cluster"] for r in test}):
            te = [i for i, r in enumerate(test) if r["cluster"] == k]
            P[te] = mk(train + [r for r in test if r["cluster"] != k]).predict([test[i] for i in te])
        pred[("B", name)] = P
    print("| setting | model | MAE doneS (s) | mean Spearman of S | regret (s, mean ± 95 %) | best pass picked |")
    print("|---|---|---|---|---|---|")
    reg = {}
    for key, p in pred.items():
        rho, rg, hit = [], [], []
        for g in groups:
            ix = [i for i, r in enumerate(test) if (r["env"], r["cluster"]) == g]
            paths = sorted({test[i]["path"] for i in ix})
            S = np.array([sum(y[i] for i in ix if test[i]["path"] == q) for q in paths])
            Sh = np.array([sum(p[i] for i in ix if test[i]["path"] == q) for q in paths])
            if len(paths) > 2 and S.std() > 0:
                rho.append(spearmanr(S, Sh)[0])
            rg.append(S[int(np.argmin(Sh))] - S.min())
            hit.append(int(np.argmin(Sh)) == int(np.argmin(S)))
        reg[key] = np.array(rg)
        print(f"| {key[0]} | {key[1]} | {np.abs(p - y).mean():.1f} | {np.nanmean(rho):.2f} | "
              f"{np.mean(rg):.1f} ± {1.96 * np.std(rg) / np.sqrt(len(rg)):.1f} | {np.mean(hit) * 100:.0f} % |")
    rnd = []
    for g in groups:
        ix = [i for i, r in enumerate(test) if (r["env"], r["cluster"]) == g]
        S = np.array([sum(y[i] for i in ix if test[i]["path"] == q) for q in sorted({test[i]["path"] for i in ix})])
        rnd.append(S.mean() - S.min())
    print(f"| - | random pass | - | 0 | {np.mean(rnd):.1f} | - |\n")
    for s in ("A", "B"):
        d = reg[(s, "hgb")] - reg[(s, "formula")]
        print(f"- {s}: regret hgb − formula {d.mean():+.1f} ± {1.96 * d.std() / np.sqrt(len(d)):.1f} s a cluster "
              f"(hgb better in {(d < 0).sum()}, worse in {(d > 0).sum()} of {len(d)} groups)")


if __name__ == "__main__":
    main()
