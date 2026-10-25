"""Baseline DN (CLAUDE.md §8 item 168): nearby critical cells grouped into small neighbourhoods, team 1's tour over
them by DTSP-N (the Dubins travelling salesman problem with neighbourhoods), no River; phase 2 as P*.

    import dn_baseline; out, info, detail = dn_baseline.run(M, C, crits, work)   # l1_rank.py method DN-<team-2 options>

Data, channel, reception, in-cell gather and the report as baseline FC (fc_baseline.py: the fountain-coded 400 kB
clue set, one coded packet every 10 ms, never repeated). What differs is the tour:
  groups    the critical cells (the CHs' cells among them) grouped bottom up: the two groups with the closest
            centroids merge as long as every member of the merged group lies within a radius of its centroid; the
            BS plans the whole tour (below) with each radius of R_GROUPS and flies the shortest
  orbit     each group is served from a circle about its centroid, radius the farthest member's distance clipped to
            [R_LOOP, RHO], flown at the speed of a 45 degree bank on it (sqrt(g r): 25 m/s on R_LOOP, 50 on RHO);
            the neighbourhood of the group is that circle: team 1 enters it on a tangent, either way round
  laps      the BS gives each group the laps that bring every member to the FC target in expectation, from the
            orbit alone (river_plan.hear_model of the work folder's channel)
  DTSP-N    sampling-based, sequence first: the groups in the order of a Euclidean TSP of their centroids from the
            BS (mission_baselines.tsp_order), then on that order a shortest path over N_ANGLE entry angles x 2
            directions per group (dynamic programming over the samples; each sample's exit is its entry turned by
            the group's laps; Dubins, radius RHO, between an exit and the next entry; free headings at the BS)
  fly       the chosen tour, leaving each orbit as soon as every member is served in expectation counting what it
            heard on the way, and skipping a group already served before team 1 sets off for it (Dubins from where
            it is to the next entry), back to the BS; kin_time's speed profile over the whole flight
"""
import math

import numpy as np

import dubins
from fc_baseline import G, HEADS, R_LOOP, RHO, VMAX, Ground, fly, realise
from mission_baselines import tsp_order

R_GROUPS = (200.0, 300.0, 400.0)   # m: group radii the BS tries (critical cells: median nearest neighbour 458 m)
N_ANGLE = 12      # entry angles sampled per group and direction
ARC = 16          # an orbit is flown a sixteenth of a lap at a time


def groups(cen, rg):
    """Bottom-up grouping of points: merge the closest pair of centroids while every member stays within rg."""
    Gs = [[i] for i in range(len(cen))]
    while True:
        m = np.array([cen[g].mean(axis=0) for g in Gs])
        best = None
        for a in range(len(Gs)):
            for b in range(a + 1, len(Gs)):
                d = float(np.linalg.norm(m[a] - m[b]))
                if d > 2 * rg or (best is not None and d >= best[0]):
                    continue
                u = Gs[a] + Gs[b]
                if np.linalg.norm(cen[u] - cen[u].mean(axis=0), axis=1).max() <= rg:
                    best = (d, a, b)
        if best is None:
            return Gs
        _, a, b = best
        Gs[a] += Gs.pop(b)


def arc(o, r, th, dirn, f0, f1, n=None):
    """Points of the orbit about o, radius r, from angle th + dirn 2 pi f0 to th + dirn 2 pi f1."""
    a = th + dirn * 2 * math.pi * np.linspace(f0, f1, n or max(2, int(abs(f1 - f0) * 2 * math.pi * r / 2) + 2))
    return o + r * np.c_[np.cos(a), np.sin(a)]


def pose_on(o, r, th, dirn):
    return (o[0] + r * math.cos(th), o[1] + r * math.sin(th), th + dirn * math.pi / 2)


def run(M, C, crits, work):
    gr = Ground(M, C, crits, work)
    bs = np.array(M["bs"], float)

    def plan(radius):
        Gs = groups(gr.cen, radius)
        cg = np.array([gr.cen[g].mean(axis=0) for g in Gs])
        rg = np.array([min(max(np.linalg.norm(gr.cen[g] - c, axis=1).max(), R_LOOP), RHO) for g, c in zip(Gs, cg)])
        vg = np.sqrt(G * rg)
        # laps from the orbit alone, in expectation
        laps = []
        for g, c, r, v in zip(Gs, cg, rg, vg):
            gr.E[:], gr.g = 0, 0
            gr.feed(arc(c, r, 0.0, 1, 0, 1), v)
            laps.append(max(1 / ARC, float(max((gr.target / np.maximum(gr.E[i], 1e-9)).max() for i in g))))
        # DTSP-N: the sequence by the centroids' TSP, then the entry samples by dynamic programming
        order = tsp_order(tuple(bs), [tuple(p) for p in cg])
        samp = [(th, d) for th in np.arange(N_ANGLE) * 2 * math.pi / N_ANGLE for d in (1, -1)]
        ent = lambda i, s: pose_on(cg[i], rg[i], s[0], s[1])
        ext = lambda i, s: pose_on(cg[i], rg[i], s[0] + s[1] * 2 * math.pi * laps[i], s[1])
        cost = [dubins.free_start(tuple(bs), ent(order[0], s), RHO) for s in samp]
        back = []
        for a, b in zip(order, order[1:]):
            step = [[cost[j] + dubins.length(ext(a, samp[j]), ent(b, s), RHO) for j in range(len(samp))] for s in samp]
            back.append([int(np.argmin(r)) for r in step])
            cost = [min(r) for r in step]
        j = int(np.argmin([cost[j] + dubins.free_end(ext(order[-1], samp[j]), tuple(bs), RHO)
                           for j in range(len(samp))]))
        pick = {order[-1]: samp[j]}
        for t in range(len(order) - 1, 0, -1):
            j = back[t - 1][j]
            pick[order[t - 1]] = samp[j]
        # fly it, leaving each orbit once its members are served
        gr.E[:], gr.g = 0, 0
        segs, pose, visits, flown = [], None, 0, 0.0
        for i in order:
            if all(gr.served(c) for c in Gs[i]):
                continue
            th, dirn = pick[i]
            goal = ent(i, (th, dirn))
            if pose is None:
                pts = dubins.path((*bs, min(HEADS, key=lambda h: dubins.length((*bs, h), goal, RHO))), goal, RHO)[0]
            else:
                pts = dubins.path(pose, goal, RHO)[0]
            gr.feed(pts, VMAX)
            segs.append((np.array(pts), VMAX))
            visits, pose, k = visits + 1, goal, 0
            while not all(gr.served(c) for c in Gs[i]) and k < ARC * 100:
                pts = arc(cg[i], rg[i], th, dirn, k / ARC, (k + 1) / ARC)
                gr.feed(pts, vg[i])
                segs.append((pts, vg[i]))
                k += 1
            flown += k / ARC
            if k:
                pose = pose_on(cg[i], rg[i], th + dirn * 2 * math.pi * k / ARC, dirn)
        end = dubins.path(pose, (*bs, min(HEADS, key=lambda h: dubins.length(pose, (*bs, h), RHO))), RHO)[0]
        segs.append((np.array(end), VMAX))
        Q, tq = fly(segs)
        info = dict(radius=radius, groups=len(Gs), size=round(len(crits) / len(Gs), 2), visits=visits,
                    loops=round(flown, 2))
        gd = [dict(c=[round(float(v)) for v in c], r=round(float(r)), members=g) for g, c, r in zip(Gs, cg, rg)]
        return Q, tq, info, gd

    Q, tq, info, gd = min((plan(r) for r in R_GROUPS), key=lambda p: p[1][-1])
    out, info, detail = realise(gr, M, C, crits, Q, tq, "dn", work, info)
    detail["groups"] = gd
    return out, info, detail
