"""The proposed mission (P: l3first tour, team 2 leaves early, score order) with a layer-1 matching model in place
of the fixed suspects (CLAUDE.md §8 items 92-94; paper/L1-STATEMENT-vi.md §6-7).

    python3 tools/l1_mission.py --works "W/k*" "W/camp/k*" --draws 30 --out docs/data/mission/l1m

The works are mission.py folders (or tools/regeom.py rebuilds of the saved ones). The layer-3 times are the ns-3
River results already there: a critical cell holds all of D at leave + doneS, so it holds every file of the query
that fits in D. Nothing new runs in ns-3.

Layer 1, per critical cell (a camera with an index of M person crops, all strangers except at the true cell):
  scores    binormal ROC fitted to Li et al., ECCV 2018 (arXiv:1807.10482), Table 4, Market-1501, Individual
            Verification, ResNet-50 multi-shot: stranger ~ N(0, 1), target ~ N(MU, SIGMA). A target crop whose
            view (front, back, side, uniform) is not among the signature images held scores ~ N(MU_X, SIGMA):
            1 point at FTR 1 % costs 25 points of TTR (the "only matching view missing" end of the layer-1 report)
  signature L images of F kB, views in the order front, back, side, front, ...; the cell holds the first
            min(L, floor(D / frames per file)) of them
  node      threshold t with FTR f per crop: YES if its best crop scores >= t; it reports that best score s
  true cell k target crops (view and score drawn per crop) among the M
  BS        posterior that a YES cell is the true one: prior 1 / (critical cells), likelihood ratio of its best
            score under "one target crop among M" vs "M strangers"; team 2 ranks by it (score order of P)
A mission fails when the true cell answers NO (team 2 then never verifies the target).
Draws are shared by every configuration (paired): the true cell, the LoRa phases, each cell's best stranger
quantile and the k target crops.
Writes OUT-draws.csv and OUT-summary.csv.
"""
import argparse, csv, glob, math, os, random
from statistics import NormalDist

import numpy as np

from mission_policy import GAP, run, tour
from mission_report import load_map

ND = NormalDist()
MU, SIGMA = 4.429, 1.299                                   # fit to TTR 82.26/95.86/98.54/99.38/99.58 % at FTR 0.1-20 %
MU_X = ND.inv_cdf(0.99) + SIGMA * ND.inv_cdf(0.9586 - 0.25)  # cross-view: TTR at FTR 1 % down by 25 points
PAYLOAD = 99
GRID = dict(f=(0.001, 0.01, 0.05, 0.10), M=(100, 1000, 10000), k=(1, 3), L=(1, 2, 3, 4, 8), F=(15, 50))
KMAX = max(GRID["k"])


def Phi(x):
    return 0.5 * math.erfc(-x / math.sqrt(2))


def phi(x):
    return math.exp(-x * x / 2) / math.sqrt(2 * math.pi)


def target_cdf_pdf(s, q):
    """A target crop's score: view held with probability q."""
    a, b = (s - MU) / SIGMA, (s - MU_X) / SIGMA
    return q * Phi(a) + (1 - q) * Phi(b), (q * phi(a) + (1 - q) * phi(b)) / SIGMA


def posterior(s, M, q, prior):
    """P(true | best score s): best of M strangers + 1 target vs best of M strangers."""
    F, f = target_cdf_pdf(s, q)
    lr = F + Phi(s) * f / (M * phi(s))
    return prior * lr / (prior * lr + 1 - prior)


def draws(M, n, seed):
    rng = random.Random(seed)
    crits = [(k, h) for k in sorted(M["cl"]) for h in M["cl"][k]["P"]["crit"]]
    out = []
    for _ in range(n):
        out.append(dict(true=rng.choice(crits), phase={k: rng.uniform(0, GAP) for k in M["cl"]},
                        u={x: rng.random() for x in crits},
                        tz=[rng.gauss(0, 1) for _ in range(KMAX)], tv=[rng.randrange(3) for _ in range(KMAX)]))
    return crits, out


def one(M, legs, crits, d, f, Mc, k, L, F):
    t = ND.inv_cdf(1 - f)
    frames = math.ceil(F * 1000 / PAYLOAD)
    held = {x: min(L, int(M["cl"][x[0]]["res"]["rf"][x[1]]["D"]) // frames) for x in crits}
    best = {x: ND.inv_cdf(d["u"][x] ** (1 / Mc)) for x in crits}   # best of Mc strangers
    hx = held[d["true"]]
    tops = [(MU if d["tv"][i] < min(hx, 3) else MU_X) + SIGMA * d["tz"][i] for i in range(k)]
    best[d["true"]] = max([best[d["true"]]] + tops)
    yes = [x for x in crits if best[x] >= t]
    nfalse = len(yes) - (d["true"] in yes)
    if d["true"] not in yes:
        return dict(ok=0, yes=len(yes), falseYes=nfalse, held=hx, end="", found="", visits="")
    score = {x: posterior(best[x], Mc, min(held[x], 3) / 3, 1 / len(crits)) for x in yes}
    r, _ = run(M, legs, dict(true=d["true"], false=[x for x in yes if x != d["true"]], score=score,
                             phase=d["phase"]), ("l3first", "early", "score"))
    return dict(ok=1, yes=len(yes), falseYes=nfalse, held=hx, end=f"{r['end']:.1f}", found=f"{r['found']:.1f}",
                visits=r["visits"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--works", nargs="+", required=True)
    ap.add_argument("--draws", type=int, default=30)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    works = sorted(w for g in a.works for w in glob.glob(g) if os.path.exists(f"{w}/c1-path-s35.csv"))
    configs = [dict(f=f, M=m, k=k, L=L, F=F) for f in GRID["f"] for m in GRID["M"] for k in GRID["k"]
               for L in GRID["L"] for F in GRID["F"]]
    rows = []
    for wi, w in enumerate(works):
        M = load_map(w, schemes=("rf",), with_bits=False)
        legs = tour(M, "l3first")[0]
        crits, Ds = draws(M, a.draws, 7919 * (wi + 1))
        for c in configs:
            for di, d in enumerate(Ds):
                rows.append(dict(map=os.path.basename(w), size=len(M["cl"]), crits=len(crits), draw=di, **c,
                                 **one(M, legs, crits, d, c["f"], c["M"], c["k"], c["L"], c["F"])))
        print(f"{os.path.basename(w)}: {len(M['cl'])} clusters, {len(crits)} critical cells", flush=True)
    with open(a.out + "-draws.csv", "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)
    summ = []
    for c in configs:
        rs = [r for r in rows if all(r[q] == v for q, v in c.items())]
        ok = [r for r in rs if r["ok"]]
        e = np.array([float(r["end"]) for r in ok])
        summ.append(dict(**c, n=len(rs), success=f"{len(ok) / len(rs):.4f}",
                         falseYes=f"{np.mean([r['falseYes'] for r in rs]):.2f}",
                         crits=f"{np.mean([r['crits'] for r in rs]):.1f}",
                         visits=f"{np.mean([r['visits'] for r in ok]):.2f}" if ok else "",
                         end=f"{e.mean():.1f}" if ok else "", p90=f"{np.percentile(e, 90):.1f}" if ok else ""))
    with open(a.out + "-summary.csv", "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(summ[0]))
        wr.writeheader()
        wr.writerows(summ)
    print(f"MU {MU} SIGMA {SIGMA} MU_X {MU_X:.3f}; {len(rows)} missions")


if __name__ == "__main__":
    main()
