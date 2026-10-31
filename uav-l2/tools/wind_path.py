"""A flown path off the planned one (wind; CLAUDE.md §8 item 241): the River plan keeps the planned path, the pass
flies this one.

    python3 tools/wind_path.py IN.csv OUT.csv SIGMA SEED

Cross-track and along-track offsets are white noise smoothed by a Gaussian kernel (10 s), scaled to standard
deviation SIGMA m (cross) and SIGMA/2 m (along). The time column t is kept, so packet s still leaves at s x 10 ms
and the packet count matches the plan; only where it leaves from changes. Vertices are re-split to <= 1.9 m.
"""
import csv, math, sys

import numpy as np

src, dst, sigma, seed = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4])
R = list(csv.DictReader(open(src)))
x, y, t = (np.array([float(r[c]) for r in R]) for c in ("x", "y", "t"))
rng = np.random.default_rng(seed)


def smooth(scale):
    """Gaussian-smoothed white noise sampled at the path times, standard deviation scale."""
    g = np.arange(0.0, t[-1] + 1.0, 0.5)
    k = np.exp(-0.5 * (np.arange(-60, 61) * 0.5 / 10.0) ** 2)
    v = np.convolve(rng.standard_normal(len(g) + 120), k, "valid")[: len(g)]
    return np.interp(t, g, v / v.std() * scale)


tx, ty = np.gradient(x), np.gradient(y)
n = np.hypot(tx, ty)
tx, ty = tx / n, ty / n
cross, along = smooth(sigma), smooth(sigma / 2)
X, Y = x + along * tx - cross * ty, y + along * ty + cross * tx
rows = []
for i, r in enumerate(R):
    if i:
        d = math.hypot(X[i] - X[i - 1], Y[i] - Y[i - 1])
        for j in range(1, int(math.ceil(d / 1.9))):   # keep vertices <= 2 m apart (the pass checks it)
            f = j / math.ceil(d / 1.9)
            rows.append(dict(r, x=f"{X[i-1] + f * (X[i] - X[i-1]):.3f}", y=f"{Y[i-1] + f * (Y[i] - Y[i-1]):.3f}",
                             t=f"{t[i-1] + f * (t[i] - t[i-1]):.7f}", part=R[i - 1]["part"], seg=R[i - 1]["seg"]))
    rows.append(dict(r, x=f"{X[i]:.3f}", y=f"{Y[i]:.3f}"))
with open(dst, "w", newline="") as f:
    w = csv.DictWriter(f, list(R[0]), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
print(f"{dst}: cross-track sd {cross.std():.1f} m (max {abs(cross).max():.0f}), along sd {along.std():.1f} m")
