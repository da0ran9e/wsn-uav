"""Each cluster's ns-3 pass flown with team 1's speed profile instead of a constant 50 m/s (CLAUDE.md §8 item 157).

    python3 tools/pass_speed.py WORK [--q KB]       # after the tour, before the pass (mission.py --kinPass)

Per cluster k, its path c{k}-path-s35.csv as the pass flies it (lead-in to lead-out), at 45 degree bank:
  speed   kin_time.profile on the path (10 m points): at most VMAX, the curvature limit, +-ACC
  need    one copy of the clue set sent over its own cells: CLUE = ceil(q 1000 / 99) packets, one per 10 ms
          (4041 at 400 kB, 40.41 s), counted on the packets themselves (river_plan.packets)
  cap     a cluster short of that slows down over its own cells: the highest cap there in [VMIN, VMAX] that gives
          CLUE packets (bisection)
  loops   if VMIN is not enough: n full circles of radius VMIN^2 / (g tan 45) (63.7 m) tangent to the path at the
          CH, on the side with more of its own cells, n the fewest that give CLUE packets (kin_time's "circle")
Writes the path back with column t (seconds from the start of the lead-in), the original kept as
c{k}-path-const.csv, and c{k}-speed.json {cap, loops, packets, clue}. kin_time.run applies the same caps on the
tour, so the tour, the leave times and the pass agree.
"""
import argparse, csv, json, math, os, sys

import numpy as np

from kin_time import G, VMAX, VMIN, profile, resample
from map_gen import cell_at

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uav-coop2/tools"))
from river_plan import packets  # noqa: E402

R_LOOP = VMIN ** 2 / G            # the tightest circle at VMIN, 45 degree bank


def timed(rows, own, cap):
    """rows with column t: the profile with speed cap over own cells (a function of a point)."""
    X = np.array([[float(r["x"]), float(r["y"])] for r in rows])
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(X, axis=0), axis=1))]
    Q = np.vstack([resample(X), X[-1:]])
    sq = np.r_[0, np.cumsum(np.linalg.norm(np.diff(Q, axis=0), axis=1))]
    c = np.array([cap if own(p) else VMAX for p in Q])
    tq = np.r_[0, np.cumsum(profile(Q, 45, c))]
    t = np.interp(s * sq[-1] / s[-1], sq, tq)   # the 10 m chords are a little shorter than the 2 m ones
    return [dict(r, t=f"{x:.7f}") for r, x in zip(rows, t)]


def with_loops(rows, ich, n, side):
    """n full circles of radius R_LOOP tangent to the path at vertex ich, turning left (side 1) or right (-1)."""
    X = np.array([[float(r["x"]), float(r["y"])] for r in rows])
    v = X[min(ich + 1, len(X) - 1)] - X[max(ich - 1, 0)]
    th = math.atan2(v[1], v[0])
    c = X[ich] + side * R_LOOP * np.array([-math.sin(th), math.cos(th)])
    a0 = math.atan2(*(X[ich] - c)[::-1])
    m = math.ceil(2 * math.pi * n * R_LOOP / 1.5)
    loop = []
    for j in range(1, m + 1):
        a = a0 + side * 2 * math.pi * n * j / m
        p = c + R_LOOP * np.array([math.cos(a), math.sin(a)])
        h = math.degrees(a + side * math.pi / 2)
        loop.append(dict(rows[ich], seg="1", x=f"{p[0]:.3f}", y=f"{p[1]:.3f}", thDeg=f"{h:.4f}"))
    return rows[:ich + 1] + loop + rows[ich + 1:]


def fit(rows, S, ch, clue):
    """The pass rows (no column t) flown so that CLUE packets are sent over the cells S: (rows with t, cap, loops)."""
    own = lambda p: cell_at(*p) in S
    got = lambda rs: sum(own(p) for p in packets(rs))
    ich = int(np.argmin([math.dist((float(r["x"]), float(r["y"])), ch) for r in rows]))
    loops, base = 0, rows
    if got(timed(rows, own, VMIN)) < clue:   # not even at VMIN: circle at the CH
        side = max((1, -1), key=lambda sd: sum(own((float(r["x"]), float(r["y"]))) for r in with_loops(rows, ich, 1, sd)))
        if got(timed(with_loops(rows, ich, 1, side), own, VMIN)) <= got(timed(rows, own, VMIN)):
            # a pass off the CH (DTSP-N + River, item 188) whose vertex nearest the CH has none of S around it:
            # circle at the vertex over S nearest the CH instead (else the loops never add a packet)
            ich = min((i for i, r in enumerate(rows) if own((float(r["x"]), float(r["y"])))),
                      key=lambda i: math.dist((float(rows[i]["x"]), float(rows[i]["y"])), ch))
            side = max((1, -1), key=lambda sd: sum(own((float(r["x"]), float(r["y"]))) for r in with_loops(rows, ich, 1, sd)))
        while got(timed(base, own, VMIN)) < clue:
            loops += 1
            base = with_loops(rows, ich, loops, side)
    lo, hi = VMIN, VMAX
    if got(timed(base, own, VMAX)) >= clue:
        lo = VMAX
    else:
        for _ in range(30):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if got(timed(base, own, mid)) >= clue else (lo, mid)
    return timed(base, own, lo), lo, loops


def run(W_, K, q_kb=400):
    clue = math.ceil(q_kb * 1000 / 99)
    out = {}
    for k in range(1, K + 1):
        if not os.path.exists(f"{W_}/c{k}-path-const.csv"):
            os.rename(f"{W_}/c{k}-path-s35.csv", f"{W_}/c{k}-path-const.csv")
        rows = list(csv.DictReader(open(f"{W_}/c{k}-path-const.csv")))
        S = {(int(x["q"]), int(x["r"])) for x in csv.DictReader(open(f"{W_}/c{k}-lattice.csv")) if x["selected"] == "1"}
        own = lambda p: cell_at(*p) in S
        got = lambda rs: sum(own(p) for p in packets(rs))
        ch = next(np.array([float(x["x"]), float(x["y"])]) for x in csv.DictReader(open(f"{W_}/c{k}-nodes-s35.csv"))
                  if x["isCH"] == "1")
        new, lo, loops = fit(rows, S, ch, clue)
        with open(f"{W_}/c{k}-path-s35.csv", "w") as f:
            w = csv.DictWriter(f, fieldnames=list(new[0].keys()), lineterminator="\n")
            w.writeheader()
            w.writerows(new)
        out[k] = dict(cap=lo, loops=loops, packets=got(new), clue=clue, seconds=float(new[-1]["t"]))
        json.dump(out[k], open(f"{W_}/c{k}-speed.json", "w"))
        print(f"C{k}: cap {lo:.1f} m/s, {loops} loops, {out[k]['packets']} packets over its cells (need {clue}), "
              f"pass {out[k]['seconds']:.1f} s")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("work")
    ap.add_argument("--q", type=float, default=400)
    a = ap.parse_args()
    run(os.path.abspath(a.work), json.load(open(f"{a.work}/map.json"))["clusters"], a.q)


if __name__ == "__main__":
    main()
