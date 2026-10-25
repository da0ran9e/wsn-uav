"""Step A of LM-Tour (CLAUDE.md §8 items 171-175): predict, before the flight, how long River takes to complete a
critical cell, from the path alone. Fitted on the ns-3 River runs of the FIX folders (River --repair 20, CAMP-BIN4).

    python3 tools/river_surrogate.py --works W1,W2,... --out docs/data/results/river-surrogate
    import river_surrogate as RS; m = RS.Model.load(OUT + ".csv"); m.predict(RS.features(geo, P, loss))

Label: doneS of each critical cell, seconds from team 1 leaving the cluster to its CL holding its window (the
--windowAt crit copy of the clue set). Features, each known to the BS before take-off from the path, the deployment
and the channel (the plan is river_plan.plan exactly as river_export.py wrote it for ns-3, checked line by line):
  hops      cells from the critical cell to the nearest Axe cell of its window (hex distance)
  dpath     metres from the cell centre to the path over its window
  lackCell  packets of its window the cell's nodes together are expected to miss (river_plan.hear_model of the
            channel, per node and packet, union over the cell), and lackCL the same for its CL alone
  naxe      Axe cells its window spans; ring1, ring2: cluster cells around it (Circle candidates)
  ncrit     critical cells of the cluster; share: of them, those whose window overlaps its own (shared Banks)
  shareLack the others' expected lackCell summed over the overlapping ones (the load on the shared Banks)
  cluLack   expected lackCell summed over every critical cell of the cluster (all that River has to move)
  loss      the channel's excess loss (dB)
Models (leave-one-map-out: the three maps, each with its four channels, take turns as the test set):
  mean      the training mean
  formula   doneS = a + b hops + c lackCell / 1000 + d cluLack / 1000 (least squares)
  linear    least squares on every feature
  trees     gradient-boosted regression trees (scikit-learn: depth 2, 200 trees, learning rate 0.05, at least 20
            cells a leaf; deeper trees fit the two training maps and do worse on the third)
Finding (812 critical cells, 3 maps x 4 channels): 89 % of the variance of doneS lies between clusters and follows
cluLack; the formula does as well as every feature and better than the trees on a map it has not seen.
"""
import argparse, csv, json, math, os, sys

import numpy as np

from mission import ENV_LOSS
from mission_report import load_map

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uav-coop2/tools"))
from river_plan import hear_model, hexdist, load_around, plan, ring  # noqa: E402

WINDOW = math.ceil(400 * 1000 / 99)   # packets: one copy of the 400 kB clue set
FEATS = ("hops", "dpath", "lackCell", "lackCL", "naxe", "ring1", "ring2", "ncrit", "share", "shareLack", "cluLack",
         "loss")
FORMULA = ("hops", "lackCell", "cluLack")


def mission_plan(geo, around, loss):
    """The River plan as river_export.py builds it for the mission (--windowKB 400 --windowAt crit --axeNear)."""
    return plan(geo, window=WINDOW, window_at="crit", domain_sc=around, near=True, near_loss=loss)


def features(geo, P, loss, hear=None):
    """Per critical cell of the plan P on the cluster geo: dict of FEATS."""
    hear = hear or hear_model(loss)
    c, S, uav = geo["c"], geo["S"], geo["uav"]
    allp = np.array(sorted(s for a in P["axe"] for s in P["seg"][a]))
    pos = {}
    for n in geo["nodes"]:
        pos.setdefault((int(n["q"]), int(n["r"])), []).append((float(n["x"]), float(n["y"]), n["isCL"] == "1"))
    out, win = {}, {}
    for h in P["crit"]:
        lo, hi = P["need"][h] if P["need"] else (int(allp[0]), int(allp[-1]))
        ps = allp[(allp >= lo) & (allp <= hi)]
        U = uav[ps]
        nd = np.array([(x, y) for x, y, _ in pos[h]])
        p = hear(np.linalg.norm(U[:, None, :] - nd[None, :, :], axis=2))
        cl = [i for i, (_, _, z) in enumerate(pos[h]) if z][0]
        ax = [a for a in P["axe"] if P["seg"][a][-1] >= lo and P["seg"][a][0] <= hi]
        win[h] = (lo, hi)
        out[h] = dict(hops=min(hexdist(h, a) for a in ax), dpath=float(np.linalg.norm(U - c[h], axis=1).min()),
                      lackCell=float(np.prod(1 - p, axis=1).sum()), lackCL=float((1 - p[:, cl]).sum()),
                      naxe=len(ax), ring1=sum(g in S for g in ring(h, 1)), ring2=sum(g in S for g in ring(h, 2)),
                      ncrit=len(P["crit"]), loss=loss)
    for h in P["crit"]:
        lo, hi = win[h]
        oth = [g for g in P["crit"] if g != h and win[g][1] >= lo and win[g][0] <= hi]
        out[h].update(share=len(oth), shareLack=sum(out[g]["lackCell"] for g in oth),
                      cluLack=sum(out[g]["lackCell"] for g in P["crit"]))
    return out


def check_plan(w, k, P):
    """The recomputed plan is the one ns-3 ran: the AXE, CRIT and NEED lines of plan{k}.txt (to 2 packets)."""
    want = {"AXE": [], "CRIT": [], "NEED": []}
    for line in open(f"{w}/plan{k}.txt"):
        f = line.split()
        if f[0] in want:
            want[f[0]].append(tuple(int(v) for v in f[1:]))
    got = dict(AXE=[(*a, P["seg"][a][0], P["seg"][a][-1]) for a in P["axe"]], CRIT=[tuple(h) for h in P["crit"]],
               NEED=[(*h, *P["need"][h]) for h in P["crit"]] if P["need"] else [])
    for t in want:   # load_map's cell radius is W / sqrt(3), river_export's the rounded CSV spacing: a packet on a
        g, x = sorted(got[t]), sorted(want[t])   # cell boundary may fall on either side
        assert len(g) == len(x) and all(u[:2] == v[:2] and max(map(abs, np.subtract(u[2:], v[2:])), default=0) <= 2
                                        for u, v in zip(g, x)), (w, k, t)


def dataset(works):
    rows = []
    for w in works:
        env = open(f"{w}/env.txt").read().strip() if os.path.exists(f"{w}/env.txt") else "open"
        opts = json.load(open(f"{w}/plan-opts.json"))
        M = load_map(w, schemes=("rf",), with_bits=False)
        around = load_around(f"{w}/domain-cl.csv")
        hear = hear_model(opts["lossDb"])
        for k in sorted(M["cl"]):
            geo = M["cl"][k]["geo"]
            P = mission_plan(geo, around, opts["lossDb"])
            check_plan(w, k, P)
            F = features(geo, P, ENV_LOSS[env], hear)
            for h in P["crit"]:
                r = M["cl"][k]["res"]["rf"][h]
                rows.append(dict(map=os.path.basename(w), env=env, cluster=k, q=h[0], r=h[1], **F[h],
                                 doneS=float(r["doneS"]), lackCLns3=int(r["lackCL"]), lackCellns3=int(r["lackCell"]),
                                 gatherS=float(r["gatherDoneS"]), circle=int(r["circle"])))
        print(f"{w}: {sum(1 for x in rows if x['map'] == os.path.basename(w) and x['env'] == env)} critical cells",
              flush=True)
    return rows


class Model:
    """kind: mean, formula, linear or trees; fitted on rows (dicts with FEATS and doneS)."""

    def __init__(self, kind, rows):
        from sklearn.ensemble import GradientBoostingRegressor
        self.kind = kind
        y = np.array([r["doneS"] for r in rows])
        self.cols = {"formula": FORMULA, "linear": FEATS, "trees": FEATS}.get(kind, ())
        X = self.X(rows)
        if kind == "mean":
            self.c = float(y.mean())
        elif kind in ("formula", "linear"):
            self.c = np.linalg.lstsq(np.c_[np.ones(len(X)), X], y, rcond=None)[0]
        else:
            self.f = GradientBoostingRegressor(max_depth=2, n_estimators=200, learning_rate=0.05, min_samples_leaf=20,
                                               random_state=0).fit(X, y)

    def X(self, rows):
        return np.array([[float(r[c]) / (1000 if "Lack" in c or c.startswith("lack") else 1) for c in self.cols]
                         for r in rows]).reshape(len(rows), len(self.cols))

    def predict(self, rows):
        X = self.X(rows)
        if self.kind == "mean":
            return np.full(len(rows), self.c)
        if self.kind in ("formula", "linear"):
            return np.c_[np.ones(len(X)), X] @ self.c
        return self.f.predict(X)

    @staticmethod
    def load(path, kind="trees"):
        rows = [{k: (v if k in ("map", "env") else float(v)) for k, v in r.items()} for r in csv.DictReader(open(path))]
        return Model(kind, rows)


def score(y, p):
    e = p - y
    return dict(mae=float(np.abs(e).mean()), rmse=float(np.sqrt((e ** 2).mean())),
                r2=float(1 - (e ** 2).sum() / ((y - y.mean()) ** 2).sum()), bias=float(e.mean()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--works", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rows = dataset(a.works.split(","))
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(f"{a.out}.csv", "w") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        wr.writeheader()
        wr.writerows(rows)
    y = np.array([r["doneS"] for r in rows])
    print(f"{len(rows)} critical cells, doneS mean {y.mean():.1f} s, sd {y.std():.1f}, "
          f"min {y.min():.1f}, max {y.max():.1f}; stalled {int((y < 0).sum())}")
    lack = np.array([[r["lackCell"], r["lackCellns3"], r["lackCL"], r["lackCLns3"]] for r in rows])
    print(f"expected vs ns-3 lack: cell r {np.corrcoef(lack[:, 0], lack[:, 1])[0, 1]:.3f} "
          f"(mean {lack[:, 0].mean():.0f} vs {lack[:, 1].mean():.0f}), "
          f"CL r {np.corrcoef(lack[:, 2], lack[:, 3])[0, 1]:.3f} (mean {lack[:, 2].mean():.0f} vs {lack[:, 3].mean():.0f})")
    out = []
    for split in ("map", "env"):
        groups = sorted({r[split] for r in rows})
        for kind in ("mean", "formula", "linear", "trees"):
            P = np.zeros(len(rows))
            for g in groups:
                te = [i for i, r in enumerate(rows) if r[split] == g]
                tr = [r for r in rows if r[split] != g]
                P[te] = Model(kind, tr).predict([rows[i] for i in te])
            s = score(y, P)
            out.append(dict(split=f"leave-one-{split}-out", model=kind, **{k: round(v, 3) for k, v in s.items()}))
            print(f"  {out[-1]['split']:<20} {kind:<8} MAE {s['mae']:6.1f} s  RMSE {s['rmse']:6.1f}  "
                  f"R2 {s['r2']:6.3f}  bias {s['bias']:+5.1f}", flush=True)
    full = {k: Model(k, rows) for k in ("formula", "linear", "trees")}
    print("formula on all: doneS = %.2f + %.2f hops + %.2f lackCell/1000 + %.2f cluLack/1000" % tuple(full["formula"].c))
    imp = dict(zip(FEATS, full["trees"].f.feature_importances_))
    print("tree importances: " + ", ".join(f"{k} {v:.2f}" for k, v in sorted(imp.items(), key=lambda x: -x[1])))
    with open(f"{a.out}-scores.csv", "w") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(out[0]), lineterminator="\n")
        wr.writeheader()
        wr.writerows(out)
    json.dump(dict(formula=list(full["formula"].c), linear=dict(zip(("const",) + FEATS, full["linear"].c)),
                   importances=imp), open(f"{a.out}-fit.json", "w"), indent=1)


if __name__ == "__main__":
    main()
