"""Animated replay of LANE (restructure.py) on one map, every step, without text (CLAUDE.md §8 items 63, 86).

    python3 tools/restructure_anim.py --clusters 8 --seed 4 --out docs/anim/lane-replay.html

Exports the stages of restructure.run_map (domain, direction scan, lanes, pieces and fragments, chunks, final
clusters in visit order, CH proxies and flight lines, the boustrophedon tour) and the k-medoids partition with
its Held-Karp tour for comparison, and fills docs/anim/lane-head.html + lane-body.html with them.
Coordinates in metres (rounded); tour times in seconds at 50 m/s.
"""
import argparse, json, math, os

from map_gen import centre
from restructure import OMEGA, V1, W, run_map

HERE = os.path.dirname(os.path.abspath(__file__))
ANIM = os.path.join(HERE, "../docs/anim")


def flight(rows, ev):
    """Per cluster: CH, line, bearing; the tour as timed legs (inside or transit)."""
    pts, legs, t = ev["pts"], [], 0.0
    for i, (p, q) in enumerate(zip(pts, pts[1:])):
        d = math.dist(p, q) / V1
        legs.append([[round(p[0]), round(p[1])], [round(q[0]), round(q[1])], round(t, 2), round(t + d, 2),
                     1 if i % 2 == 1 and i < len(pts) - 2 else 0])
        t += d
    rank = {k: i for i, (k, d) in enumerate(ev["order"])}
    cl = {r["k"]: dict(ch=[round(c) for c in centre(r["ch"])], th=round(math.radians(r["bearing"]), 5),
                       seg=[[round(v) for v in ev["seg"][r["k"]][0]], [round(v) for v in ev["seg"][r["k"]][1]]],
                       rank=rank[r["k"]]) for r in rows}
    return dict(cl=cl, legs=legs, end=round(t, 2))


def covered(owner, cl, h):
    c = cl[owner[h]]
    x, y = centre(h)
    return int(abs(-(x - c["ch"][0]) * math.sin(c["th"]) + (y - c["ch"][1]) * math.cos(c["th"])) <= OMEGA)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clusters", type=int, default=8)
    ap.add_argument("--seed", type=int, default=4)
    ap.add_argument("--lane", type=float, default=4.5)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    R = run_map(a.clusters, a.seed, a.lane, "short")
    g, land, lo, km, st = R["g"], R["land"], R["lo"], R["km"], R["st"]
    th = R["th"]
    u = (math.cos(th), math.sin(th))
    lane_f = flight(*R["lane_"])
    km_f = flight(*R["base"])
    cost = {}
    for c, nl, b, off in st["scan"]:
        cost[b] = min(cost.get(b, 1e9), c + nl / 100)
    cut_ids = {c: i for i, c in enumerate(sorted(set(st["cut"].values())))}
    cells = []
    for h in g["final"]:
        x, y = centre(h)
        if h not in land:
            cells.append([round(x), round(y), 1])
            continue
        cells.append([round(x), round(y), 0, R["lane"][h], cut_ids[st["cut"][h]], int(h in st["frag"]), lo[h],
                      km[h], round(x * u[0] + y * u[1]), covered(lo, lane_f["cl"], h), covered(km, km_f["cl"], h)])
    out = dict(cells=cells, nodes=[[round(v[1]), round(v[2])] for v in R["nodes"]], bs=[round(v) for v in R["bs"]],
               th=round(th, 5), scan=[[b, round(cost[b], 3)] for b in sorted(cost)], lane=lane_f, km=km_f,
               params=dict(R=100, omega=round(OMEGA, 1), W=round(W, 3), v=V1, L=round(a.lane * W, 1)))
    head = open(os.path.join(ANIM, "lane-head.html")).read()
    body = open(os.path.join(ANIM, "lane-body.html")).read().replace("__DATA__", json.dumps(out, separators=(",", ":")))
    with open(a.out, "w") as f:
        f.write(head + body)
    print(f"{a.out}: {os.path.getsize(a.out) / 1e6:.2f} MB; {len(cells)} cells, {len(set(lo.values()))} lane clusters, "
          f"{len(set(km.values()))} k-medoids clusters; tours {lane_f['end']:.0f} s / {km_f['end']:.0f} s")


if __name__ == "__main__":
    main()
