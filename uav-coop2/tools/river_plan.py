"""The River plan (L3-vi.md, Algorithms 1-4), computed the way the BS / CH / Axe cells would.

    from river_plan import load, plan
    geo = load(deploy_dir, path_csv); P = plan(geo, width=3.5, kg=2, kl=1, r=2)

Algorithm 1  Axe (cells crossed, in flight order) and Seg(a) per packet index
Algorithm 2  Bank_+-(a) and Path_+-(a): perpendiculars to the Axe's sum vector, +-omega
             (banks="local", CLAUDE.md §8 item 103: perpendiculars to the flight path where it crosses a,
             the inner side cut at the local radius of curvature, so curved Axes keep their Banks at omega)
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


def detour(b, m, k, S, c):
    """Cell path b -> m that avoids k; through k only when k cuts m off (k is a cut cell)."""
    try:
        return cellpath(b, m, S - {k}, c)
    except AssertionError:
        return cellpath(b, m, S, c)


def load_around(path):
    """{cell: score of its strongest node} for every cell of the domain (mission.py --critRing domain)."""
    return {(int(x["q"]), int(x["r"])): float(x["score"]) for x in csv.DictReader(open(path))}


def plan(geo, width=3.5, kg=2.0, kl=1.0, r=2, banks="parallel", reentry=False, window=0, window_at="ch", domain_sc=None,
         near=False):
    c, w, R, S, uav = geo["c"], geo["w"], geo["R"], geo["S"], geo["uav"]
    # Algorithm 1: Axe and Seg (packets sent above each Axe cell; outside the cluster: none, or with near (CLAUDE.md
    # §8 item 135) the nearest cluster cell next to where the UAV is, whose nodes hear it from a few hundred metres)
    axe, seg = [], {}
    reentry = reentry or near   # the nearest cell may change back and forth along a path that grazes the edge
    for s, (x, y) in enumerate(uav):
        h = hex_of(x, y, R)
        if h not in S and near:
            nb = [g for g in ring(h, 1) if g in S]
            h = min(nb, key=lambda g: math.dist(c[g], (x, y))) if nb else h
        if h not in S:
            continue
        if h not in seg:
            axe.append(h); seg[h] = []
        seg[h].append(s)
    for a in axe:   # straight path: one interval per Axe cell
        runs = np.split(np.array(seg[a]), np.where(np.diff(seg[a]) > 1)[0] + 1)
        assert reentry or len(runs) == 1, a
        # reentry: a curved path crosses the cell again; Seg(a) is its longest visit, the rest are left
        # unassigned like the packets sent outside the cluster
        seg[a] = [int(s) for s in max(runs, key=len)]
    axe.sort(key=lambda a: seg[a][0])
    allp = sorted(s for a in axe for s in seg[a])

    def around(x, y):   # `window` consecutive Axe packets around where the UAV passes closest to (x, y)
        c0 = int(np.argmin(np.linalg.norm(uav - [x, y], axis=1)))
        i = min(max(int(np.searchsorted(allp, c0)) - window // 2, 0), len(allp) - window)
        return allp[i], allp[i + window - 1]
    need = {}
    if window and len(allp) > window:
        if window_at == "ch":   # the cluster needs only the `window` Axe packets around where the UAV passes the CH
            chn = next(x for x in geo["nodes"] if x["isCH"] == "1")
            wins = [around(float(chn["x"]), float(chn["y"]))]
        else:   # "crit" (item 120): every critical cell needs the copy of the clue set nearest to it
            cl = {(int(x["q"]), int(x["r"])): x for x in geo["nodes"] if x["isCL"] == "1"}
            need = {h: around(*c[h]) for h in cl}   # cut down to the critical cells below
            wins = list(need.values())
        keep = lambda s: any(lo <= s <= hi for lo, hi in wins)
        seg = {a: [s for s in seg[a] if keep(s)] for a in axe}
        axe = [a for a in axe if seg[a]]
        seg = {a: seg[a] for a in axe}
    u = np.array(c[axe[-1]]) - np.array(c[axe[0]])
    u /= np.linalg.norm(u)
    nrm = np.array([-u[1], u[0]])
    omega = width / 2 * w
    # Algorithm 2: Banks along perpendiculars, cut at the cluster edge
    bank, bpath = {}, {}
    N = len(uav)
    heading = lambda i, half: uav[min(max(i, 0) + half, N - 1)] - uav[max(min(i, N - 1) - half, 0)]
    for a in axe:
        z, nz, reach = np.array(c[a]), nrm, (omega, omega)
        if banks == "local":   # from the path's midpoint over a, along the path's normal there
            m = seg[a][len(seg[a]) // 2]
            t = heading(m, 20)
            t /= np.linalg.norm(t)
            z, nz = uav[m], np.array([-t[1], t[0]])
            t0, t1 = heading(m - 200, 20), heading(m + 200, 20)   # +-100 m: heading change -> curvature
            turn = math.atan2(t0[0] * t1[1] - t0[1] * t1[0], float(np.dot(t0, t1)))
            rc = (min(m + 200, N - 1) - max(m - 200, 0)) * 0.5 / abs(turn) if abs(turn) > 1e-6 else math.inf
            # normals converge at the centre of curvature, on the side the path turns towards
            reach = (min(omega, rc), omega) if turn > 0 else (omega, min(omega, rc))
        for side, sg in ((0, 1.0), (1, -1.0)):
            p = [a]
            for t in np.arange(0, reach[side] + 1e-9, w / 20):
                h = hex_of(*(z + sg * t * nz), R)
                if h not in S:
                    break
                if h != p[-1]:
                    p.append(h)
            bank[(a, side)], bpath[(a, side)] = p[-1], p
    river = set(axe) | {h for p in bpath.values() for h in p}
    if banks == "local":   # outside a bend the normals fan out: rays every 10 m along Seg(a) fill the gaps
        for a in axe:
            for m in seg[a][::20]:
                t = heading(m, 20)
                t /= np.linalg.norm(t)
                for sg in (1.0, -1.0):
                    for x in np.arange(0, omega + 1e-9, w / 20):
                        h = hex_of(*(uav[m] + sg * x * np.array([-t[1], t[0]])), R)
                        if h not in S:
                            break
                        river.add(h)
    # Algorithm 3: critical cells
    sc = {(int(x["q"]), int(x["r"])): float(x["score"]) for x in geo["nodes"] if x["isCL"] == "1"}
    mu, sd = np.mean(list(sc.values())), np.std(list(sc.values()))
    chn = next(x for x in geo["nodes"] if x["isCH"] == "1")
    chc = (int(chn["q"]), int(chn["r"]))
    crit = {chc} | {h for h, v in sc.items() if v > mu + kg * sd}
    ref = sc if domain_sc is None else {**domain_sc, **sc}   # domain_sc: the local test over the cell's real
    for h, v in sc.items():                                  # neighbourhood, other clusters' cells too (item 135)
        near = [ref[g] for k in range(1, r + 1) for g in ring(h, k) if g in ref]
        if v > mu + kl * sd and v >= max(near):
            crit.add(h)
    crit = sorted(crit)
    need = {k: need[k] for k in crit} if need else {}
    if need:   # only the critical cells' own windows, and only the Axe cells they cover, stay in the plan
        keep = lambda s: any(lo <= s <= hi for lo, hi in need.values())
        seg = {a: [s for s in seg[a] if keep(s)] for a in axe}
        axe = [a for a in axe if seg[a]]
        seg = {a: seg[a] for a in axe}
        bank = {x: v for x, v in bank.items() if x[0] in seg}
        bpath = {x: v for x, v in bpath.items() if x[0] in seg}
    # Algorithm 4: Circles; members ordered along the Axe (sum vector, or with banks="local" the track)
    along = (lambda g: float(np.dot(np.array(c[g]), u))) if banks != "local" else \
        (lambda g: int(np.argmin(np.linalg.norm(uav - np.array(c[g]), axis=1))))
    circle = {}
    for k in crit:
        mem = sorted((g for g in ring(k, 1) if g in S), key=along)
        q = len(mem)
        groups = [[] for _ in range(q)]
        axk = [a for a in axe if not need or seg[a][-1] >= need[k][0] and seg[a][0] <= need[k][1]]
        for i, a in enumerate(axk):
            groups[min(q - 1, i * q // len(axk))].append(a)
        tasks = []
        for j, m in enumerate(mem):
            src = []
            for a in groups[j]:
                side = min((0, 1), key=lambda sd_: (hexdist(bank[(a, sd_)], m), math.dist(c[bank[(a, sd_)]], c[m])))
                b = bank[(a, side)]
                src.append((a, side, b, detour(b, m, k, S, c) if b != m else [m]))
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
            mem = sorted(mem, key=along)
            sets[n] = [(m, (i * len(axe) // n, (i + 1) * len(axe) // n - 1)) for i, m in enumerate(mem)]
        src = {}
        for m in r1 + r2:
            for a in axe:
                side = min((0, 1), key=lambda sd_: (hexdist(bank[(a, sd_)], m), math.dist(c[bank[(a, sd_)]], c[m])))
                b = bank[(a, side)]
                src[(m, a)] = (b, detour(b, m, k, S, c) if b != m else [m])
        adapt[k] = dict(sets=sets, src=src, link={m: cellpath(k, m, S, c) for m in r1 + r2})
    return dict(axe=axe, seg=seg, u=u, omega=omega, bank=bank, bpath=bpath, river=river, crit=crit, ch=chc,
                circle=circle, adapt=adapt, width=width, banks=banks, need=need)
