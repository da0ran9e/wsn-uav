"""The River plan (L3-vi.md, Algorithms 1-4), computed the way the BS / CH / Axe cells would.

    from river_plan import load, plan
    geo = load(deploy_dir, path_csv); P = plan(geo, width=3.5, kg=2, kl=1, r=2)

Algorithm 1  Axe (cells crossed, in flight order) and Seg(a) per packet index
Algorithm 2  Bank_+-(a) and Path_+-(a): perpendiculars to the Axe's sum vector, +-omega
Algorithm 3  critical cells: the CH's cell, global outliers, local outliers
Algorithm 4  Circle: Neig(k) ordered along u, the Axe cut into consecutive groups, each
             Seg(a) of a group fetched from a's Bank on the side nearer the member
Adaptive Circle (CLAUDE.md §8 items 66-67): for every size n up to the cells of rings 1-2, the
             members (ring 1 first, spread evenly round k, then ring 2) and their groups; the
             critical cell's CL picks n at run time from its lack
"""
import csv, math, os
from collections import deque

import numpy as np

NB = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]


def hex_of(x, y, R):
    """Pointy-top axial cell containing (x, y)."""
    q, r = (math.sqrt(3) / 3 * x - y / 3) / R, (2 / 3 * y) / R
    s = -q - r
    rq, rr, rs = round(q), round(r), round(s)
    dq, dr, ds = abs(rq - q), abs(rr - r), abs(rs - s)
    if dq > dr and dq > ds:
        rq = -rr - rs
    elif dr > ds:
        rr = -rq - rs
    return rq, rr


def ring(h, k):
    out, q, r = [], h[0] + NB[4][0] * k, h[1] + NB[4][1] * k
    for side in range(6):
        for _ in range(k):
            out.append((q, r))
            q, r = q + NB[side][0], r + NB[side][1]
    return out


def hexdist(a, b):
    return (abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[0] + a[1] - b[0] - b[1])) // 2


def load(deploy, path_csv, step=0.5):
    """Lattice, cells, nodes and the flight path sampled at one point per packet."""
    lat = list(csv.DictReader(open(os.path.join(deploy, "deploy-lattice.csv"))))
    c = {(int(x["q"]), int(x["r"])): (float(x["cx"]), float(x["cy"])) for x in lat}
    h0 = next(h for h in c if (h[0] + 1, h[1]) in c)   # any two neighbours (the lattice may miss the origin)
    w = math.dist(c[h0], c[(h0[0] + 1, h0[1])])
    R = w / math.sqrt(3)
    for h, (x, y) in c.items():
        assert hex_of(x, y, R) == h
    sel = sorted((int(x["q"]), int(x["r"])) for x in lat if x["selected"] == "1")
    nodes = list(csv.DictReader(open(os.path.join(deploy, "deploy-nodes-s35.csv"))))
    path = np.array([[float(q["x"]), float(q["y"])] for q in csv.DictReader(open(path_csv))])
    # resample the flight path at one point every step metres: packet s is sent at uav[s]
    seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))]
    d = np.arange(0, seg[-1], step)
    uav = np.c_[np.interp(d, seg, path[:, 0]), np.interp(d, seg, path[:, 1])]
    return dict(c=c, w=w, R=R, cells=sel, S=set(sel), nodes=nodes, path=path, uav=uav)


def cellpath(src, dst, allowed, c):
    """Shortest cell path src -> dst through allowed cells, the straightest among equals."""
    prev, seen, dq = {}, {src}, deque([src])
    while dq:
        v = dq.popleft()
        if v == dst:
            break
        for g in sorted(((v[0] + a, v[1] + b) for a, b in NB), key=lambda g: math.dist(c.get(g, (1e9, 1e9)), c[dst])):
            if g in allowed and g not in seen:
                seen.add(g); prev[g] = v; dq.append(g)
    assert dst in seen, (src, dst)
    out = [dst]
    while out[-1] != src:
        out.append(prev[out[-1]])
    return out[::-1]


def plan(geo, width=3.5, kg=2.0, kl=1.0, r=2):
    c, w, R, S, uav = geo["c"], geo["w"], geo["R"], geo["S"], geo["uav"]
    # Algorithm 1: Axe and Seg (packets sent above each Axe cell; outside the cluster: none)
    axe, seg = [], {}
    for s, (x, y) in enumerate(uav):
        h = hex_of(x, y, R)
        if h not in S:
            continue
        if h not in seg:
            axe.append(h); seg[h] = []
        seg[h].append(s)
    for a in axe:   # straight path: one interval per Axe cell
        assert seg[a][-1] - seg[a][0] + 1 == len(seg[a]), a
    u = np.array(c[axe[-1]]) - np.array(c[axe[0]])
    u /= np.linalg.norm(u)
    nrm = np.array([-u[1], u[0]])
    omega = width / 2 * w
    # Algorithm 2: Banks along parallel perpendiculars, cut at the cluster edge
    bank, bpath = {}, {}
    for a in axe:
        z = np.array(c[a])
        for side, sg in ((0, 1.0), (1, -1.0)):
            p = [a]
            for t in np.arange(0, omega + 1e-9, w / 20):
                h = hex_of(*(z + sg * t * nrm), R)
                if h not in S:
                    break
                if h != p[-1]:
                    p.append(h)
            bank[(a, side)], bpath[(a, side)] = p[-1], p
    river = set(axe) | {h for p in bpath.values() for h in p}
    # Algorithm 3: critical cells
    sc = {(int(x["q"]), int(x["r"])): float(x["score"]) for x in geo["nodes"] if x["isCL"] == "1"}
    mu, sd = np.mean(list(sc.values())), np.std(list(sc.values()))
    chn = next(x for x in geo["nodes"] if x["isCH"] == "1")
    chc = (int(chn["q"]), int(chn["r"]))
    crit = {chc} | {h for h, v in sc.items() if v > mu + kg * sd}
    for h, v in sc.items():
        around = [sc[g] for k in range(1, r + 1) for g in ring(h, k) if g in sc]
        if v > mu + kl * sd and v >= max(around):
            crit.add(h)
    crit = sorted(crit)
    # Algorithm 4: Circles
    circle = {}
    for k in crit:
        mem = sorted((g for g in ring(k, 1) if g in S), key=lambda g: float(np.dot(np.array(c[g]), u)))
        q = len(mem)
        groups = [[] for _ in range(q)]
        for i, a in enumerate(axe):
            groups[min(q - 1, i * q // len(axe))].append(a)
        tasks = []
        for j, m in enumerate(mem):
            src = []
            for a in groups[j]:
                side = min((0, 1), key=lambda sd_: (hexdist(bank[(a, sd_)], m), math.dist(c[bank[(a, sd_)]], c[m])))
                b = bank[(a, side)]
                src.append((a, side, b, cellpath(b, m, S - {k}, c) if b != m else [m]))
            tasks.append((m, groups[j], src))
        circle[k] = tasks
    # Adaptive Circle: candidates in rings 1-2, members for each size n, Banks for every candidate
    adapt = {}
    for k in crit:
        r1 = [g for g in ring(k, 1) if g in S]
        r2 = [g for g in ring(k, 2) if g in S]
        spread = lambda rg, n: [rg[i * len(rg) // n] for i in range(n)]
        sets = {}
        for n in range(1, len(r1) + len(r2) + 1):
            mem = spread(r1, n) if n <= len(r1) else r1 + spread(r2, n - len(r1))
            mem = sorted(mem, key=lambda g: float(np.dot(np.array(c[g]), u)))
            sets[n] = [(m, (i * len(axe) // n, (i + 1) * len(axe) // n - 1)) for i, m in enumerate(mem)]
        src = {}
        for m in r1 + r2:
            for a in axe:
                side = min((0, 1), key=lambda sd_: (hexdist(bank[(a, sd_)], m), math.dist(c[bank[(a, sd_)]], c[m])))
                b = bank[(a, side)]
                src[(m, a)] = (b, cellpath(b, m, S - {k}, c) if b != m else [m])
        adapt[k] = dict(sets=sets, src=src, link={m: cellpath(k, m, S, c) for m in r1 + r2})
    return dict(axe=axe, seg=seg, u=u, omega=omega, bank=bank, bpath=bpath, river=river, crit=crit, ch=chc,
                circle=circle, adapt=adapt, width=width)
