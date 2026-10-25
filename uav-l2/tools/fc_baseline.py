"""Baseline FC (CLAUDE.md §8 item 166): the clue set fountain-coded, gathered only inside each critical cell, no River.

    import fc_baseline; out, info, detail = fc_baseline.run(M, C, crits, work)   # l1_rank.py method FC-<team-2 options>

Team 1 (the same fixed wing: 50 m/s, 45 degree bank, +-2 m/s^2) carries the 400 kB clue set as its 12 files, each
fountain-coded (an ideal rateless code: file j decodes once the cell holds (1 + EPS) K_j of its coded packets, any of
them), the files' packets interleaved in proportion to their size, one every 10 ms, none ever repeated. It flies a
tour over the critical cells and serves each one without hovering:
  order   the critical cells by TSP from the BS (mission_baselines.tsp_order: nearest neighbour, 2-opt)
  plan    the BS keeps, per critical cell and file, the expected number of coded packets the cell holds (the union of
          its nodes; river_plan.hear_model for the work folder's channel, the model that matches the ns-3 pass). A
          cell is served once every file j reaches (1 + EPS) K_j + 3 sqrt((1 + EPS) K_j)
  fly     to the next critical cell not yet served (cells served on the way are skipped): Dubins, radius RHO, to its
          centre, heading for the one after; if it is still short there, at VMIN round circles of radius R_LOOP
          until it is served (a part circle at the end), then on; finally back to the BS. The circles run either
          through the centre or (coming in R_LOOP right of it instead of over it) about it: the BS plans both
          tours and flies the shorter
  times   kin_time.profile over the whole flight, VMIN on the circles (the slowing down and speeding up included)
Reception, one realisation per map and channel (seeded by both): each node hears each packet independently with
hear_model's probability, as on the ns-3 pass. File j decodes at the packet that brings the cell's union to
(1 + EPS) K_j. The cell's CL then gathers what it still lacks from its members, GATHER_A + GATHER_B x packets moved
(fitted on 351 critical cells of the ns-3 River runs, R2 0.83). The cell reports at decode + gather; a cell some file
of which never decodes reports what it has after the last packet it could hear. Then match, LoRa and team 2 as P*.
"""
import csv, hashlib, json, math, os, sys

import numpy as np

import dubins
from kin_time import G, VMAX, VMIN, profile, resample
from mission import ENV_LOSS
from mission_baselines import tsp_order

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uav-coop2/tools"))
from river_plan import hear_model  # noqa: E402

EPS = 0.05
GATHER_A, GATHER_B = 0.07, 0.00789
RHO, R_LOOP, SLOT = VMAX ** 2 / G, VMIN ** 2 / G, 0.01
HEADS = [2 * math.pi * i / 72 for i in range(72)]


def pattern(K):
    """File of each packet over one period of sum(K) packets: file j's K_j packets spread evenly."""
    return np.array([j for _, j in sorted(((i + 0.5) / k, j) for j, k in enumerate(K) for i in range(k))])


class Ground:
    """The critical cells as the broadcast reaches them: nodes and CL of each, the fountain-coded clue set, the work
    folder's channel, and the BS's expected union reception E (per critical cell and file) of the packets fed so far."""

    def __init__(self, M, C, crits, work):
        self.K = np.array([math.ceil(c["kB"] * 1000 / 99) for c in C])
        self.need = np.ceil((1 + EPS) * self.K).astype(int)
        self.target = self.need + 3 * np.sqrt(self.need)
        self.pat = pattern(self.K)
        self.env = open(f"{work}/env.txt").read().strip() if os.path.exists(f"{work}/env.txt") else "open"
        self.hear = hear_model(ENV_LOSS[self.env])
        xs = np.arange(0, 3001, 5.0)
        self.cut = float(xs[np.argmax(self.hear(xs) < 1e-7)]) + 120.0   # farther from a cell centre: nothing heard
        self.cen = np.array([M["cl"][k]["geo"]["c"][h] for k, h in crits], float)
        self.nodes, self.cl = [], []
        for k, h in crits:
            rows = [n for n in M["cl"][k]["geo"]["nodes"] if (int(n["q"]), int(n["r"])) == h]
            self.nodes.append(np.array([(float(n["x"]), float(n["y"])) for n in rows]))
            self.cl.append(next(i for i, n in enumerate(rows) if n["isCL"] == "1"))
        self.E, self.g = np.zeros((len(crits), len(C))), 0

    def feed(self, pts, v):
        """Packets every v x SLOT metres along pts: add each cell's expected union reception."""
        P = np.asarray(pts, float)
        s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
        d = np.arange(0, s[-1], v * SLOT)
        U = np.c_[np.interp(d, s, P[:, 0]), np.interp(d, s, P[:, 1])]
        f = self.pat[(self.g + np.arange(len(U))) % len(self.pat)]
        for c in np.nonzero(np.linalg.norm(self.cen - U.mean(axis=0), axis=1) < self.cut + s[-1])[0]:
            near = np.linalg.norm(U - self.cen[c], axis=1) < self.cut
            if near.any():
                dd = np.linalg.norm(U[near][:, None, :] - self.nodes[c][None, :, :], axis=2)
                np.add.at(self.E[c], f[near], 1 - np.prod(1 - self.hear(dd), axis=1))
        self.g += len(U)

    def served(self, c):
        return bool((self.E[c] >= self.target).all())


def fly(segs):
    """The flight as flown from (points, speed cap) pieces: 10 m points, kin_time's speed profile at 45 degree bank.
    Returns the points and the time at each."""
    pieces = [(resample(p) if np.linalg.norm(np.diff(p, axis=0), axis=1).sum() > 10 else p, v) for p, v in segs]
    Q = np.vstack([p for p, _ in pieces])
    cap = np.concatenate([np.full(len(p), v) for p, v in pieces])
    keep = np.r_[True, np.linalg.norm(np.diff(Q, axis=0), axis=1) > 1e-6]
    Q, cap = Q[keep], cap[keep]
    return Q, np.r_[0, np.cumsum(profile(Q, 45, cap))]


def realise(gr, M, C, crits, Q, tq, tag, work, info):
    """One realisation of the reception along the flight (seeded by the method, map and channel): each critical
    cell's held mask and report time, and per cell the decode time of each file (-1 never) and the flight's track,
    for the replay. Writes <tag>-path.csv (a point a second) and <tag>-info.json."""
    ts = np.arange(0, tq[-1], SLOT)
    U = np.c_[np.interp(ts, tq, Q[:, 0]), np.interp(ts, tq, Q[:, 1])]
    f = gr.pat[np.arange(len(U)) % len(gr.pat)]
    key = f"{tag.upper()}/{M['name']}/{gr.env}"
    rng = np.random.default_rng(int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "little"))
    out, moved_all, detail = {}, [], {}
    for c, x in enumerate(crits):
        idx = np.nonzero(np.linalg.norm(U - gr.cen[c], axis=1) < gr.cut)[0]
        got = rng.random((len(idx), len(gr.nodes[c]))) < gr.hear(
            np.linalg.norm(U[idx][:, None, :] - gr.nodes[c][None, :, :], axis=2))
        cell = got.any(axis=1)
        mask, done = np.zeros(len(C), bool), np.full(len(C), np.inf)
        for j in range(len(C)):
            hit = idx[cell & (f[idx] == j)]
            if len(hit) >= gr.need[j]:
                mask[j], done[j] = True, ts[hit[gr.need[j] - 1]]
        t_c = float(done.max()) if mask.all() else (float(ts[idx[cell].max()]) if cell.any() else float(ts[-1]))
        own = got[:, gr.cl[c]] & (ts[idx] <= t_c)
        moved = int(sum(max(0, gr.need[j] - int((own & (f[idx] == j)).sum())) for j in range(len(C)) if mask[j]))
        moved_all.append(moved)
        out[x] = (mask, t_c + GATHER_A + GATHER_B * moved)
        detail[x] = dict(done=[round(float(v), 2) if np.isfinite(v) else -1 for v in done], ready=out[x][1])
    keep = np.r_[np.arange(0, len(ts), 100), len(ts) - 1]
    track = [[round(float(ts[i]), 2), round(float(U[i][0]), 1), round(float(U[i][1]), 1)] for i in keep]
    with open(f"{work}/{tag}-path.csv", "w") as fh:   # for figures: the flight, a point a second
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["t", "x", "y"])
        w.writerows(track)
    ready = [t for _, t in out.values()]
    info.update(env=gr.env, tour=float(tq[-1]), crits=len(crits), complete=int(sum(m.all() for m, _ in out.values())),
                moved=float(np.mean(moved_all)), ready=[float(np.mean(ready)), float(np.max(ready))], key=key)
    json.dump(info, open(f"{work}/{tag}-info.json", "w"))   # for fc_table.py
    with open(f"{work}/{tag}-cells.csv", "w") as fh:   # per critical cell: every clue decoded, report time
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["cluster", "q", "r", "complete", "ready"])
        w.writerows([k, h[0], h[1], int(m.all()), round(t, 2)] for (k, h), (m, t) in out.items())
    detail["track"] = track
    return out, info, detail


def run(M, C, crits, work):
    gr = Ground(M, C, crits, work)
    order = tsp_order(tuple(M["bs"]), [tuple(p) for p in gr.cen])
    bs = np.array(M["bs"], float)
    cen = gr.cen

    def plan(about):
        """The tour, about: when a pass over a cell's centre is not enough, circle about the centre (else through it)."""
        gr.E[:], gr.g = 0, 0
        segs, pose, loops, visits = [], None, 0, 0
        while True:
            rem = [c for c in order if not gr.served(c)]
            if not rem:
                break
            c = rem[0]
            nxt = cen[rem[1]] if len(rem) > 1 else bs
            head = math.atan2(nxt[1] - cen[c][1], nxt[0] - cen[c][0])
            left = np.array([-math.sin(head), math.cos(head)])

            def leg(goal):
                if pose is None:
                    return dubins.path((*bs, min(HEADS, key=lambda h: dubins.length((*bs, h), goal, RHO))), goal,
                                       RHO)[0]
                return dubins.path(pose, goal, RHO)[0]
            saved = gr.E.copy(), gr.g
            goal = (*cen[c], head)
            pts = leg(goal)
            gr.feed(pts, VMAX)
            if about and not gr.served(c):   # come in R_LOOP right of the centre instead, to circle about it
                gr.E[:], gr.g = saved
                goal = (*(cen[c] - R_LOOP * left), head)
                pts = leg(goal)
                gr.feed(pts, VMAX)
            segs.append((np.array(pts), VMAX))
            pose, visits = goal, visits + 1
            if not gr.served(c):   # circles, turning left, an eighth at a time
                o = cen[c] if about else cen[c] + R_LOOP * left
                a0, arcs = head - math.pi / 2, 0
                while not gr.served(c) and arcs < 8 * 100:
                    a = a0 + 2 * math.pi / 8 * np.linspace(arcs, arcs + 1, 26)
                    pts = o + R_LOOP * np.c_[np.cos(a), np.sin(a)]
                    gr.feed(pts, VMIN)
                    segs.append((pts, VMIN))
                    arcs += 1
                loops += arcs / 8
                pose = (*pts[-1], a[-1] + math.pi / 2)
        back = dubins.path(pose, (*bs, min(HEADS, key=lambda h: dubins.length(pose, (*bs, h), RHO))), RHO)[0]
        segs.append((np.array(back), VMAX))
        Q, tq = fly(segs)
        return Q, tq, visits, loops

    # the BS plans both and flies the shorter
    Q, tq, visits, loops = min((plan(about) for about in (False, True)), key=lambda r: r[1][-1])
    return realise(gr, M, C, crits, Q, tq, "fc", work, dict(visits=visits, loops=round(loops, 2)))
