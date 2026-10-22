"""Geometry only (CLAUDE.md §8 item 136): SWATH-K's shortest route vs the route with the earliest mean pass over the
cells likely to be critical (strongest node per cell: global outlier mu + 2 sd or local max over rings 1-2 with
mu + 1 sd, domain-wide), both directions, BS link included."""
import math, sys
sys.path.insert(0, "/home/user/wsn-uav/uav-l2/tools")
sys.path.insert(0, "/home/user/wsn-uav/uav-coop2/tools")
import numpy as np
import dubins
from map_gen import centre
from restructure import domain
from river_plan import ring
from swath import RHO, heading, routes

V1 = 50.0
for m in sys.argv[1:]:
    K, seed = int(m[1]), int(m.split("-s")[1])
    g = domain(K, seed)
    land = set(g["domain"])
    best = {}
    for v in g["nodes"]:
        h = (v[3], v[4])
        if h in land:
            best[h] = max(best.get(h, -1), v[5] * v[6] * v[7])
    sc = np.array(list(best.values()))
    mu, sd = sc.mean(), sc.std()
    crit = [h for h, s in best.items() if s > mu + 2 * sd or
            (s > mu + sd and s >= max([best[x] for k in (1, 2) for x in ring(h, k) if x in best] or [0]))]
    xs, ys = [centre(h)[0] for h in land], [centre(h)[1] for h in land]
    bs = ((min(xs) + max(xs)) / 2, min(ys) - 1000.0)
    R = routes(land, bs)
    rows = []
    for tot, deg, off, r in R:
        P, L = r["poly"], r["s"][-1]
        fwd = dubins.free_start(bs, (*P[0], heading(P, 0)), RHO)
        rev = dubins.free_start(bs, (*P[-1], heading(P, len(P) - 1, True) + math.pi), RHO)
        mpos = np.mean([r["pos"][h] for h in crit])
        lat = min(fwd + mpos, rev + L - mpos) / V1
        rows.append((lat, tot / V1, deg, off))
    short = rows[0]
    early = min(rows)
    print(f"{m}: {len(crit)} likely critical cells; shortest route {short[1]:.0f} s, mean critical pass {short[0]:.0f} s"
          f" | earliest: route {early[1]:.0f} s, mean pass {early[0]:.0f} s ({early[2]} deg)", flush=True)
