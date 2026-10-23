"""Team 1's tour with a speed profile and the delivery check (CLAUDE.md §8 items 144-145).

    python3 tools/kin_time.py WORK[:KIND[:smooth]] [...]

The whole flight (BS, transits, every cluster's path, back to the BS; the Dubins transits of iter_fig.flown) as one
polyline. Speed: at most VMAX, at most sqrt(g tan(PHI) / curvature) (curvature from three points 10 m apart), along-track
acceleration within +-ACC (forward and backward passes, the usual minimum-time profile). Delivery: the UAV broadcasts
one frame per 10 ms, so a cluster gets one copy of the clue set (CLUE frames: q_kb of 99 B, 4041 at 400 kB) only if it spends CLUE x 10 ms over its
own cells; a cluster short of that is fixed by slowing down over its cells (down to VMIN) and, if that is not enough,
by circling inside it at VMIN; the extra time adds to the tour. Prints per work: tour at constant 50 m/s, with the
profile, the fixes and the total, for PHI in PHIS. smooth: every cluster path is first smoothed (1-2-1 passes, ends
fixed) until its curvature is at most 1.02 / R_TURN, or 400 passes (MEANDER's bends, item 144). KIND skin / route:
where one cluster's stretch runs on into the next (mission_policy.seams), its lead-out and the next lead-in are
not flown.
"""
import math, sys

import numpy as np

from iter_fig import flown, poses
from map_gen import cell_at
from mission_policy import R_TURN, seams, tour
from mission_report import load_map

VMAX, VMIN, ACC, G = 50.0, 25.0, 2.0, 9.80665
PHIS = (45, 30, 60)                  # bank: the one that sets R_TURN, and two sensitivities (item 149)
STEP = 10.0


def resample(P, step=STEP):
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    t = np.arange(0, s[-1], step)
    return np.c_[np.interp(t, s, P[:, 0]), np.interp(t, s, P[:, 1])]


def curvature(P):
    a, b, c = P[:-2], P[1:-1], P[2:]
    ab, bc, ca = (np.linalg.norm(x, axis=1) for x in (b - a, c - b, a - c))
    cross = np.abs((b - a)[:, 0] * (c - a)[:, 1] - (b - a)[:, 1] * (c - a)[:, 0])
    k = 2 * cross / np.maximum(ab * bc * ca, 1e-9)
    return np.r_[k[0], k, k[-1]]


def profile(P, phi):
    """Seconds per STEP segment of the resampled polyline P."""
    v = np.minimum(VMAX, np.sqrt(G * math.tan(math.radians(phi)) / np.maximum(curvature(P), 1e-9)))
    ds = np.linalg.norm(np.diff(P, axis=0), axis=1)
    for i in range(1, len(v)):
        v[i] = min(v[i], math.sqrt(v[i - 1] ** 2 + 2 * ACC * ds[i - 1]))
    for i in range(len(v) - 2, -1, -1):
        v[i] = min(v[i], math.sqrt(v[i + 1] ** 2 + 2 * ACC * ds[i]))
    return ds / ((v[:-1] + v[1:]) / 2)


def smooth(P):
    Q = resample(np.asarray(P, float))
    for _ in range(400):
        if curvature(Q).max() * R_TURN <= 1.02:
            break
        Q[1:-1] = (Q[:-2] + 2 * Q[1:-1] + Q[2:]) / 4
    return Q


def run(w, kind, smoothed=False, q_kb=400):
    M = load_map(w, schemes=(), with_bits=False)
    legs, t_const = tour(M, kind)
    trs = flown(M, legs, kind)
    seam = seams(M) if kind in ("skin", "route") else {}
    dirs = [0 if math.dist(l[1], M["cl"][l[0]]["geo"]["path"][0]) < 1e-6 else 1 for l in legs]
    key = lambda i, j: (legs[i][0], dirs[i], legs[j][0], dirs[j])
    parts, owner, kinds = [], [], []
    for i, l in enumerate(legs):
        seamless = i > 0 and key(i - 1, i) in seam   # flown on from core to core: no transit, no leads there
        parts.append(np.empty((0, 2)) if seamless else trs[i]); owner.append(None)
        kinds.append("bs" if i == 0 else "transit")
        g = M["cl"][l[0]]["geo"]
        p, part = (g["path"], g["part"]) if dirs[i] == 0 else (g["path"][::-1], g["part"][::-1])
        keep = np.ones(len(p), bool)   # a seamless junction flies on from core to core: the leads there are dropped
        if i > 0 and key(i - 1, i) in seam:
            keep &= ~((part == 0) | (part == 3)) | (np.arange(len(p)) > len(p) // 2)
        if i + 1 < len(legs) and key(i, i + 1) in seam:
            keep &= ~((part == 0) | (part == 3)) | (np.arange(len(p)) < len(p) // 2)
        lead = ((part == 0) | (part == 3))[keep]
        p = p[keep]
        p = smooth(p) if smoothed else p
        if not smoothed:   # the leads and the core apart (length split below)
            parts.append(p); owner.append(l[0]); kinds.append(("core", lead))
        else:
            parts.append(p); owner.append(l[0]); kinds.append(("core", None))
    parts.append(trs[-1]); owner.append(None); kinds.append("bs")
    seq = [(resample(np.asarray(q, float)), k) for q, k in zip(parts, owner) if len(q) > 1]
    P = np.vstack([q for q, _ in seq])
    tag = np.concatenate([[k if k is not None else -1] * len(q) for q, k in seq])
    out = dict(const=sum(np.linalg.norm(np.diff(P, axis=0), axis=1)) / VMAX)
    L = dict(bs=0.0, transit=0.0, lead=0.0, core=0.0)   # metres of each kind
    for q, kd in zip(parts, kinds):
        if len(q) < 2:
            continue
        seg = np.linalg.norm(np.diff(np.asarray(q, float), axis=0), axis=1)
        if isinstance(kd, tuple):
            ld = kd[1] if kd[1] is not None else np.zeros(len(q), bool)
            L["lead"] += float(seg[ld[1:] & ld[:-1]].sum())
            L["core"] += float(seg[~(ld[1:] & ld[:-1])].sum())
        else:
            L[kd] += float(seg.sum())
    out["parts"] = L
    for phi in PHIS:
        dt = profile(P, phi)
        over = {}
        for i in range(len(dt)):
            k = tag[i]
            if k >= 0 and cell_at(*P[i]) in M["cl"][k]["geo"]["S"]:
                over.setdefault(k, [0.0, 0.0])
                over[k][0] += dt[i]
                over[k][1] += np.linalg.norm(P[i + 1] - P[i])
        need = math.ceil(q_kb * 1000 / 99) * 0.01   # one copy of a q_kb clue set, 99 B frames
        fix, how = 0.0, {}
        for k in sorted(M["cl"]):
            t, L = over.get(k, (0.0, 0.0))
            if t >= need:
                continue
            fix += need - t
            how[k] = "slow" if L / VMIN >= need else "circle"
        out[phi] = dict(profile=float(dt.sum()), fix=fix, how=how, over={k: round(v[0], 1) for k, v in over.items()})
    return M, out


def main():
    for arg in sys.argv[1:]:
        w, _, rest = arg.partition(":")
        kind, _, sm = rest.partition(":")
        _, o = run(w, kind or "kin", sm == "smooth")
        print(arg, f"constant 50 m/s {o['const']:.0f} s")
        for phi in PHIS:
            r = o[phi]
            print(f"  bank {phi}: profile {r['profile']:.0f} s, delivery fixes +{r['fix']:.0f} s {r['how']}, "
                  f"total {r['profile'] + r['fix']:.0f} s; time over own cells {r['over']}")


if __name__ == "__main__":
    main()
