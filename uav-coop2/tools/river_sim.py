"""Logic-level trial of the River scheme (L3-vi.md, Algorithms 1-7) against a direct pull.

    python3 tools/river_sim.py --deploy ../uav-coop/docs/data --data docs/data \
        --path docs/data/path-a180.csv --runs 120 --out docs/data/river

The pass: node v receives packet s with probability 1 - p(rho), rho = horizontal distance to
the UAV when s is sent, p = the PER-vs-distance curve measured from the ns-3 pass bitmaps;
independent over packets and nodes, as in that ns-3 model.

The ground, in slots of 10 ms:
  - one frame per slot on each cell's own medium (every in-cell hop of that cell), and one
    per slot on each gateway pair's own channel (the hop between two cells);
  - a hop succeeds with q = exp(-thr/mean): Rayleigh, n = 3.5 from 1 m, static log-normal
    shadowing sigma 7.8 dB per node pair; a failed hop is retried in a later slot;
  - a cell's data lives at its CL; a cell path runs CL -> gateway -> ... -> CL: inside a cell
    the least-ETX path (link qualities known from phase 0), between cells the one gateway
    link of the pair (fixed, whatever its quality);
  - a request is one control frame along the same path.
Schemes (both start with each involved cell gathering what it needs at its CL):
  river   Bank fill (Alg. 5), Circle fill (Alg. 6), critical pull (Alg. 7)
  direct  each critical cell asks every Axe cell for what it lacks of Seg(a), shortest cell path
Writes OUT-crit.csv (per run, scheme, critical cell), OUT-runs.csv (per run, scheme),
OUT-load.csv (frames per cell medium, summed over runs) and, for run 1, OUT-trace.csv
(each critical CL's holding over time) and OUT-r1.csv (per-cell holdings and transfers).
"""
import argparse, csv, heapq, math, os, sys
from collections import defaultdict, deque

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from river_plan import load, plan, cellpath  # noqa: E402

TX_DBM, SENS_DBM, FSPL1M, N_G2G, SIGMA = 10.0, -100.0, 40.05, 3.5, 7.8


class Net:
    """Node graph, cells, CLs, gateway links and in-cell shortest paths."""

    def __init__(self, geo, deploy):
        nodes = geo["nodes"]
        self.xy = np.array([[float(r["x"]), float(r["y"])] for r in nodes])
        self.cell = [(int(r["q"]), int(r["r"])) for r in nodes]
        self.cl = {self.cell[i]: i for i, r in enumerate(nodes) if r["isCL"] == "1"}
        self.members = defaultdict(list)
        for i, h in enumerate(self.cell):
            self.members[h].append(i)
        n = len(nodes)
        d2 = ((self.xy[:, None, :] - self.xy[None, :, :]) ** 2).sum(-1)
        self.adj = [set(np.flatnonzero((d2[i] <= 50.0 ** 2) & (np.arange(n) != i)).tolist()) for i in range(n)]
        for r in csv.DictReader(open(os.path.join(deploy, "deploy-bridges-s35.csv"))):
            a, b = int(r["a"]), int(r["b"])
            self.adj[a].add(b); self.adj[b].add(a)
        self.gw = {}
        for r in csv.DictReader(open(os.path.join(deploy, "deploy-gateways-s35.csv"))):
            A, B = (int(r["qA"]), int(r["rA"])), (int(r["qB"]), int(r["rB"]))
            a, b = int(r["gwA"]), int(r["gwB"])
            self.gw[(A, B)], self.gw[(B, A)] = (a, b), (b, a)
            self.adj[a].add(b); self.adj[b].add(a)
        self._ip, self.q = {}, None

    def mission(self, q):
        """Link qualities of a new mission; in-cell paths are re-planned on them."""
        self.q, self._ip = q, {}

    def inpath(self, u, v):
        """Least-ETX node path u -> v inside their (common) cell, ETX = 1/q per hop."""
        if (u, v) in self._ip:
            return self._ip[(u, v)]
        h = self.cell[u]
        assert self.cell[v] == h
        dist, prev, hp = {u: 0.0}, {u: None}, [(0.0, u)]
        while hp:
            d, x = heapq.heappop(hp)
            if x == v:
                break
            if d > dist[x]:
                continue
            for y in self.adj[x]:
                if self.cell[y] != h:
                    continue
                nd = d + 1.0 / self.q(x, y)
                if nd < dist.get(y, float("inf")):
                    dist[y], prev[y] = nd, x
                    heapq.heappush(hp, (nd, y))
        assert v in prev, (u, v, h)
        p = [v]
        while p[-1] != u:
            p.append(prev[p[-1]])
        self._ip[(u, v)] = p[::-1]
        return self._ip[(u, v)]

    def etx(self, path):
        return sum(1.0 / self.q(x, y) for x, y in zip(path, path[1:]))

    def route(self, cells, start=None):
        """Node path for a cell path: start (default the CL of cells[0]) -> ... -> CL of cells[-1]."""
        cur = self.cl[cells[0]] if start is None else start
        p = [cur]
        for x, y in zip(cells, cells[1:]):
            a, b = self.gw[(x, y)]
            p += self.inpath(cur, a)[1:] + [b]
            cur = b
        p += self.inpath(cur, self.cl[cells[-1]])[1:]
        return p


class Trial:
    """One mission, one scheme: a slot-by-slot event simulation."""

    def __init__(self, net, P, rx, D, q, rng, gather_crit=True):
        self.net, self.P, self.rx, self.D, self.q, self.rng = net, P, rx, D, q, rng
        self.N = rx.shape[1]
        self.gather_crit = gather_crit
        self.have, self.at = {}, {}
        self.res = defaultdict(list)       # resource -> heap of (ready, seq, job)
        self.active = set()
        self.seq = 0
        self.waiters = defaultdict(list)
        self.frames = defaultdict(int)     # by phase
        self.load = defaultdict(int)       # frames by cell medium / gateway pair
        self.gather_left, self.on_gathered = {}, defaultdict(list)
        self.now = 0

    def hold(self, c):
        if c not in self.have:
            cl = self.net.cl[c]
            self.have[c] = self.rx[cl].copy()
            self.at[c] = np.where(self.have[c], 0.0, np.inf)
        return self.have[c]

    def hops(self, path):
        out = []
        for u, v in zip(path, path[1:]):
            cu, cv = self.net.cell[u], self.net.cell[v]
            r = ("c", cu) if cu == cv else ("p",) + tuple(sorted((cu, cv)))
            out.append((r, self.q(u, v)))
        return out

    def send(self, path, s, phase, cb=None):
        """Queue a frame (packet s, or a control frame when s < 0) along a node path, now."""
        dst = self.net.cell[path[-1]]
        if len(path) == 1:
            self.arrive(dst, s, self.now, cb)
            return
        job = [self.hops(path), 0, s, dst, phase, cb]
        self.push(job, self.now)

    def push(self, job, ready):
        r = job[0][job[1]][0]
        self.seq += 1
        heapq.heappush(self.res[r], (ready, self.seq, job))
        self.active.add(r)

    def arrive(self, c, s, t, cb):
        if s >= 0:
            h = self.hold(c)
            if not h[s]:
                h[s] = True
                self.at[c][s] = t
                for fn in self.waiters.pop((c, s), []):
                    fn()
        if cb:
            cb()

    def when(self, c, s, fn):
        """Run fn once cell c holds packet s (now, if it already does)."""
        if self.hold(c)[s]:
            fn()
        else:
            self.waiters[(c, s)].append(fn)

    def run(self, limit):
        t = 0
        while self.active and t < limit:
            self.now = t
            for r in list(self.active):
                hp = self.res[r]
                if not hp or hp[0][0] > t:
                    if not hp:
                        self.active.discard(r)
                    continue
                _, _, job = heapq.heappop(hp)
                hl, i = job[0], job[1]
                self.frames[job[4]] += 1
                self.load[r] += 1
                if self.rng.random() < hl[i][1]:
                    job[1] += 1
                    if job[1] == len(hl):
                        self.now = t + 1
                        self.arrive(job[3], job[2], t + 1, job[5])
                        self.now = t
                    else:
                        self.push(job, t + 1)
                else:
                    self.push(job, t + 1)
                if not hp:
                    self.active.discard(r)
            t += 1
        return t

    # convention 1: gather what a cell needs at its CL, from its own nodes
    def gather(self, c, need):
        net, h = self.net, self.hold(c)
        cl = net.cl[c]
        mem = [v for v in net.members[c] if v != cl]
        dist = {v: net.etx(net.inpath(v, cl)) for v in mem}
        todo = [s for s in np.flatnonzero(need & ~h)]
        n = 0
        for s in todo:
            src = [v for v in mem if self.rx[v, s]]
            if not src:
                continue
            v = min(src, key=dist.get)
            n += 1
            self.send(net.inpath(v, cl), int(s), "gather", lambda c=c: self.gathered_one(c))
        self.gather_left[c] = n
        if n == 0:
            self.gathered(c)

    def gathered_one(self, c):
        self.gather_left[c] -= 1
        if self.gather_left[c] == 0:
            self.gathered(c)

    def gathered(self, c):
        for fn in self.on_gathered.pop(c, []):
            fn()

    def after_gather(self, c, fn):
        if self.gather_left.get(c, 1) == 0 and c not in self.on_gathered:
            fn()
        else:
            self.on_gathered[c].append(fn)


def mask(N, idx):
    m = np.zeros(N, dtype=bool)
    m[list(idx)] = True
    return m


def river(T):
    """Algorithms 5-7 over the plan, after each cell's gathering."""
    P, net, N = T.P, T.net, T.N
    seg = {a: mask(N, P["seg"][a]) for a in P["axe"]}
    need = defaultdict(lambda: np.zeros(N, dtype=bool))
    banks = defaultdict(list)                             # bank cell -> [(a, side)]
    for (a, side), b in P["bank"].items():
        need[a] |= seg[a]
        if b != a:
            need[b] |= seg[a]
            banks[b].append((a, side))
    for k in P["crit"]:
        if T.gather_crit:
            need[k] |= T.D
        for m, G, src in P["circle"][k]:
            for a in G:
                need[m] |= seg[a]
    # Algorithm 5: each Bank tells its Axe cell what it has; the Axe sends the rest
    for b, lst in banks.items():
        for a, side in lst:
            path = P["bpath"][(a, side)]

            def bank_ready(a=a, b=b, path=path):
                lack = np.flatnonzero(seg[a] & ~T.hold(b))
                def at_axe():
                    for s in lack:
                        T.when(a, int(s), lambda s=int(s): T.send(net.route(path), s, "bankfill"))
                T.send(net.route(path[::-1]), -1, "control", at_axe)
            T.after_gather(b, bank_ready)
    # Algorithm 6: each Circle member fetches Seg(a) of its group from a's Bank
    for k in P["crit"]:
        for m, G, src in P["circle"][k]:
            for a, side, b, path in src:
                def member_ready(a=a, b=b, m=m, path=path):
                    lack = np.flatnonzero(seg[a] & ~T.hold(m))
                    def at_bank():
                        for s in lack:
                            T.when(b, int(s), lambda s=int(s): T.send(net.route(path), s, "circlefill"))
                    T.send(net.route(path[::-1]), -1, "control", at_bank)
                T.after_gather(m, member_ready)
    # Algorithm 7: each critical cell asks its members for what it lacks of their groups
    for k in P["crit"]:
        def crit_ready(k=k):
            lack = T.D & ~T.hold(k)
            for m, G, src in P["circle"][k]:
                part = np.flatnonzero(lack & np.any([seg[a] for a in G], axis=0))
                def at_member(m=m, part=part):
                    for s in part:
                        T.when(m, int(s), lambda s=int(s), m=m: T.send(net.route([m, k]), s, "pull"))
                T.send(net.route([k, m]), -1, "control", at_member)
        T.after_gather(k, crit_ready)
    for c, nd in list(need.items()):
        T.gather(c, nd)


def direct(T):
    """Baseline: each critical cell asks every Axe cell directly, shortest cell path."""
    P, net, N = T.P, T.net, T.N
    seg = {a: mask(N, P["seg"][a]) for a in P["axe"]}
    S = set(P["cells"])
    need = defaultdict(lambda: np.zeros(N, dtype=bool))
    for a in P["axe"]:
        need[a] |= seg[a]
    for k in P["crit"]:
        if T.gather_crit:
            need[k] |= T.D
        def crit_ready(k=k):
            lack = T.D & ~T.hold(k)
            for a in P["axe"]:
                if a == k:
                    continue
                part = np.flatnonzero(lack & seg[a])
                cp = cellpath(k, a, S, P["c"])
                def at_axe(a=a, part=part, cp=cp):
                    for s in part:
                        T.when(a, int(s), lambda s=int(s): T.send(net.route(cp[::-1]), s, "pull"))
                T.send(net.route(cp), -1, "control", at_axe)
        T.after_gather(k, crit_ready)
    for c, nd in list(need.items()):
        T.gather(c, nd)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deploy", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--path", required=True)
    ap.add_argument("--width", type=float, default=3.5)
    ap.add_argument("--runs", type=int, default=120)
    ap.add_argument("--first", type=int, default=1)
    ap.add_argument("--limit", type=int, default=360000, help="slots")
    ap.add_argument("--gather-crit", type=int, default=1, help="critical cells gather their own nodes' packets")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    geo = load(a.deploy, a.path)
    P = plan(geo, width=a.width)
    P["cells"], P["c"] = geo["cells"], geo["c"]
    net = Net(geo, a.deploy)
    curve = list(csv.DictReader(open(os.path.join(a.data, "per-distance.csv"))))
    cd = np.array([(float(r["dLoM"]) + float(r["dHiM"])) / 2 for r in curve])
    cp = np.array([float(r["per"]) for r in curve])
    uav = geo["uav"]
    N = len(uav)
    Dfull = mask(N, [s for a in P["axe"] for s in P["seg"][a]])
    dist = np.sqrt(((net.xy[:, None, :] - uav[None, :, :]) ** 2).sum(-1))
    per = np.interp(dist, cd, cp)
    del dist
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    fc = open(a.out + "-crit.csv", "w", newline="")
    wc = csv.writer(fc)
    wc.writerow(["run", "scheme", "q", "r", "inRiver", "D", "lackCL", "lackCell", "lackAfterGather",
                 "gatherDoneS", "doneS", "missing", "fromOwnCell", "fromOutside"])
    fr = open(a.out + "-runs.csv", "w", newline="")
    wr = csv.writer(fr)
    wr.writerow(["run", "scheme", "D", "Davail", "slots", "frames", "gather", "bankfill", "circlefill", "pull",
                 "control", "lastCritS"])
    loads = defaultdict(int)
    for run in range(a.first, a.first + a.runs):
        rng = np.random.default_rng(1000 + run)
        rx = rng.random(per.shape) >= per
        D = Dfull & rx.any(axis=0)                     # packets someone in the cluster received
        shadow = {}

        def q(u, v):
            key = (u, v) if u < v else (v, u)
            if key not in shadow:
                shadow[key] = SIGMA * rng.standard_normal()
            d = max(1.0, float(np.linalg.norm(net.xy[u] - net.xy[v])))
            margin = TX_DBM - FSPL1M - 10 * N_G2G * math.log10(d) - shadow[key] - SENS_DBM
            return max(0.02, math.exp(-10 ** (-margin / 10)))

        net.mission(q)

        for scheme, fn in (("river", river), ("direct", direct)):
            T = Trial(net, P, rx, D, q, np.random.default_rng(5000 + run), bool(a.gather_crit))
            for k in P["crit"]:
                T.hold(k)
            lackCL = {k: int((D & ~T.have[k]).sum()) for k in P["crit"]}
            lackCell = {k: int((D & ~rx[net.members[k]].any(axis=0)).sum()) for k in P["crit"]}
            gat = {}
            for k in P["crit"]:
                T.on_gathered[k].append(lambda k=k, T=T: gat.__setitem__(k, T.now))
            fn(T)
            slots = T.run(a.limit)
            last = 0
            for k in P["crit"]:
                got = T.at[k][D]
                missing = int(np.isinf(got).sum())
                done = float(np.max(got[np.isfinite(got)])) * 0.01 if missing == 0 else float("nan")
                last = max(last, done if missing == 0 else 0)
                own = int(((T.at[k] > 0) & np.isfinite(T.at[k]) & D & rx[net.members[k]].any(axis=0)).sum())
                outside = int((np.isfinite(T.at[k]) & (T.at[k] > 0) & D).sum()) - own
                wc.writerow([run, scheme, k[0], k[1], int(k in P["river"]), int(D.sum()), lackCL[k], lackCell[k],
                             int((D & ~np.isfinite(T.at[k])).sum()) if k not in gat else lackCL[k] - own,
                             f"{gat.get(k, float('nan')) * 0.01:.2f}", f"{done:.2f}", missing, own, outside])
            fs = T.frames
            wr.writerow([run, scheme, int(Dfull.sum()), int(D.sum()), slots, sum(fs.values()), fs["gather"],
                         fs["bankfill"], fs["circlefill"], fs["pull"], fs["control"], f"{last:.2f}"])
            for r_, v in T.load.items():
                loads[(scheme,) + r_] += v
            if run == a.first:
                with open(a.out + f"-trace-{scheme}.csv", "w", newline="") as f:
                    w = csv.writer(f)
                    w.writerow(["q", "r", "t", "held"])
                    for k in P["crit"]:
                        tt = np.sort(T.at[k][D])
                        tt = tt[np.isfinite(tt)]
                        for t in np.r_[0, np.unique(np.round(tt, -1))]:
                            w.writerow([k[0], k[1], f"{t * 0.01:.2f}", int((tt <= t).sum())])
                with open(a.out + f"-r1-{scheme}.csv", "w", newline="") as f:
                    w = csv.writer(f)
                    w.writerow(["q", "r", "clHeld0", "cellHeld", "clHeldEnd"])
                    for c in geo["cells"]:
                        cl = net.cl[c]
                        end = T.have[c] if c in T.have else rx[cl]
                        w.writerow([c[0], c[1], int((rx[cl] & D).sum()), int((rx[net.members[c]].any(axis=0) & D).sum()),
                                    int((end & D).sum())])
        fc.flush(); fr.flush()
        print(f"run {run}: D {int(D.sum())}/{int(Dfull.sum())}", flush=True)
    with open(a.out + "-load.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["scheme", "kind", "a_q", "a_r", "b_q", "b_r", "frames"])
        for key, v in sorted(loads.items(), key=str):
            if key[1] == "c":
                w.writerow([key[0], "cell", key[2][0], key[2][1], "", "", v])
            else:
                w.writerow([key[0], "pair", key[2][0], key[2][1], key[3][0], key[3][1], v])


if __name__ == "__main__":
    main()
