"""Layer 1 from per-image cosine scores instead of published match rates (CLAUDE.md §8 item 110).

    python3 tools/l1_vector.py --draws 2000 --out docs/data/l1/vector

Every image gets its cosine to the target's reference (the reference itself: 1). Here the scores are drawn in
standardized units (stranger crops: mean 0, sd 1), so the scenario is set by a few separations, not by one paper:
  stranger      z ~ N(0, 1)
  look-alike    z ~ N(MU_L, 1), each crop with probability rho (dressed like the target)
  target        z ~ N(d', 1), k crops at the true camera only
A camera's device and scene map them to cosines s = a_c z + b_c, a_c ~ U(0.8, 1.2), b_c ~ N(0, tau): the same
crop scores differently on two devices (item 88). Each critical cell ranks its M crops and reports its top one,
either raw (s_(1)) or against its own crowd, z_c = (s_(1) - median) / (1.4826 MAD), which a_c and b_c cancel,
or the mean of its top 3 against its crowd (norm3: k target crops lift it, one look-alike does not).
The BS ranks the cells by the report; the rank of the true cell is how many cells team 2 visits to find it.
Writes OUT.csv (one row per configuration).
"""
import argparse, csv, os

import numpy as np

CELLS, M, MU_L = 32, 223, 2.5   # critical cells per map (mean 32.6); crops in the query window; look-alike mean
GRID = dict(d=(3.0, 4.0, 5.0), k=(1, 3), rho=(0.0, 0.02), tau=(0.0, 0.5))


def ranks(rng, n, d, k, rho, tau):
    """Rank of the true cell (cell 0) among CELLS by raw top score, normalized top score and normalized top-3
    mean, n draws each."""
    z = rng.standard_normal((n, CELLS, M)).astype(np.float32)
    z += MU_L * (rng.random((n, CELLS, M)) < rho)
    z[:, 0, :k] = d + rng.standard_normal((n, k))
    s = rng.uniform(0.8, 1.2, (n, CELLS, 1)) * z + rng.normal(0, tau, (n, CELLS, 1)) if tau else z
    top = s.max(axis=2)
    top3 = np.sort(s, axis=2)[..., -3:].mean(axis=2)
    med = np.median(s, axis=2)
    mad = 1.4826 * np.median(np.abs(s - med[..., None]), axis=2)
    return [1 + (x[:, 1:] > x[:, :1]).sum(axis=1) for x in (top, (top - med) / mad, (top3 - med) / mad)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=2000)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rng = np.random.default_rng(110)
    rows = []
    for tau in GRID["tau"]:
        for rho in GRID["rho"]:
            for k in GRID["k"]:
                for d in GRID["d"]:
                    out = [[], [], []]
                    for _ in range(a.draws // 250):   # chunks of 250 draws keep memory small
                        for o, r in zip(out, ranks(rng, 250, d, k, rho, tau)):
                            o.append(r)
                    for stat, r in zip(("raw", "norm", "norm3"), map(np.concatenate, out)):
                        rows.append(dict(tau=tau, rho=rho, k=k, d=d, stat=stat, top1=round(float(np.mean(r == 1)), 3),
                                         top3=round(float(np.mean(r <= 3)), 3), meanRank=round(float(r.mean()), 2)))
                        print(" ".join(f"{q} {v}" for q, v in rows[-1].items()), flush=True)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out + ".csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
