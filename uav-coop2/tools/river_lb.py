"""Load-balanced River plan: re-route the Bank -> Circle member flows of a River plan so that no cell medium or
gateway pair carries much more than the others (J1 draft, paper/j1/draft-v1).

    python3 uav-coop2/tools/river_lb.py WORK K OUT_PLAN [--shared] [--p 6] [--passes 3]

Reads WORK/plan<K>.txt, c<K>-nodes-s35.csv, c<K>-gateways-s35.csv; writes OUT_PLAN with the same
records except CIRC, whose Bank (either Bank of the Axe cell) and cell path are chosen again. Everything else (Axe,
Banks, windows, members and their groups) is unchanged, so the plan runs on the same river binary.

Model. One frame occupies one medium (a cell, or a gateway pair) for one service time, so a medium's load is the frames
it must carry. A flow of v packets costs every cell it crosses --ht * v frames (default 1.7), its Bank and its member
--he * v (1.5) and every gateway pair on its path v. The two constants are the frames per packet measured on a per-hop
trace of coop2-river (k8, r100, seed 1, cluster 1: least squares over the cells, R^2 0.89); the planner uses nothing
finer than the cell graph. Fixed load: the hop member -> critical cell, and Axe -> Bank.
Each flow (critical cell k, member m, Axe cell a) is routed, largest first, on the path minimising
sum over its media of (load + added)^p - load^p (a soft maximum; --p), plus a small term in the frames; then
--passes rounds of removing and re-routing every flow. --shared: flows of the same segment from the same Bank share
their common hops (the --tree forwarding of coop2-river sends a packet once over a shared hop), so such a hop carries
the largest of their volumes.
Prints the largest and mean loads of the old and the new plan under this model.
"""
import argparse, csv, collections, heapq

ap = argparse.ArgumentParser()
ap.add_argument("work"); ap.add_argument("k"); ap.add_argument("out")
ap.add_argument("--shared", action="store_true"); ap.add_argument("--p", type=float, default=6.0)
ap.add_argument("--passes", type=int, default=3); ap.add_argument("--beta", type=float, default=0.02)
ap.add_argument("--ht", type=float, default=1.7); ap.add_argument("--he", type=float, default=1.5)
A = ap.parse_args()
W, K = A.work, A.k
cl = {(int(n["q"]), int(n["r"])) for n in csv.DictReader(open(f"{W}/c{K}-nodes-s35.csv")) if n["isCL"] == "1"}
adj = collections.defaultdict(list)
for r in csv.DictReader(open(f"{W}/c{K}-gateways-s35.csv")):
    a, b = (int(r["qA"]), int(r["rA"])), (int(r["qB"]), int(r["rB"]))
    if a in cl and b in cl: adj[a].append(b); adj[b].append(a)

lines = open(f"{W}/plan{K}.txt").read().split("\n")
axe, banks, need, circ, bpath = {}, collections.defaultdict(dict), {}, [], {}
for l in lines:
    p = l.split()
    if not p: continue
    v = list(map(int, p[1:])) if p[0] != "N" else []
    if p[0] == "AXE": axe[(v[0], v[1])] = (v[2], v[3])
    elif p[0] == "BANK":
        a, side, b = (v[0], v[1]), v[2], (v[3], v[4]); banks[a][side] = b
        bpath[(a, b)] = [(v[6 + 2 * i], v[7 + 2 * i]) for i in range(v[5])]
    elif p[0] == "NEED": need[(v[0], v[1])] = (v[2], v[3])
    elif p[0] == "CIRC":
        k, m, a, b = (v[0], v[1]), (v[2], v[3]), (v[4], v[5]), (v[6], v[7])
        circ.append(dict(k=k, m=m, a=a, b=b, path=[(v[9 + 2 * i], v[10 + 2 * i]) for i in range(v[8])]))


def vol(k, a):
    lo, hi = axe[a]
    if k in need: lo, hi = max(lo, need[k][0]), min(hi, need[k][1])
    return max(0, hi - lo + 1)


def hops(path):
    """[(medium, frames per packet, key)] of a cell path."""
    out = [(c, h, (c, h)) for i, c in enumerate(path) for h in [A.ht if 0 < i < len(path) - 1 else A.he]]
    return out + [(("pair",) + tuple(sorted(e)), 1, e) for e in zip(path, path[1:])]


fixed = collections.Counter()
for (a, b), P in bpath.items():                                  # Axe -> Bank
    for m, h, _ in hops(P): fixed[m] += h * (axe[a][1] - axe[a][0] + 1)
group = collections.Counter()
for t in circ: group[(t["k"], t["m"])] += vol(t["k"], t["a"])
for (k, m), v in group.items():                                  # member -> critical cell
    for med, h, _ in hops([m, k]): fixed[med] += h * v


def loads(tasks, shared):
    L = collections.Counter(fixed); seen = collections.defaultdict(list)
    for t in tasks: add(t, L, seen, 1, shared)
    return L


def route(t, L, seen):
    """Cheapest Bank and path for task t given the loads L (Dijkstra over (cell, previous cell))."""
    v = vol(t["k"], t["a"]); p, beta = A.p, A.beta
    scale = max(max(L.values(), default=1), v, 1)
    phi = lambda x: (x / scale) ** p

    def cost(med, h, key, b):
        dv = max(0, v - max(seen.get((t["a"], b, key), ()), default=0)) if A.shared else v
        return phi(L[med] + h * dv) - phi(L[med]) + beta * h * dv / scale
    best = None
    for b in sorted(set(banks[t["a"]].values()) | {t["b"]}):
        if b == t["m"]: return b, [b]
        dist, prev = {b: cost(b, A.he, (b, A.he), b)}, {}
        pq = [(dist[b], b)]
        while pq:
            d, c = heapq.heappop(pq)
            if d > dist[c] or (best and d >= best[0]): continue
            if c == t["m"]:
                path = [c]
                while path[-1] in prev: path.append(prev[path[-1]])
                best = (d, b, path[::-1]); break
            for q in adj[c]:
                hq = A.he if q == t["m"] else A.ht
                nd = d + cost(("pair",) + tuple(sorted((c, q))), 1, (c, q), b) + cost(q, hq, (q, hq), b)
                if nd < dist.get(q, 1e99): dist[q] = nd; prev[q] = c; heapq.heappush(pq, (nd, q))
    return (best[1], best[2]) if best else (t["b"], t["path"])     # no route: keep the plan's


def add(t, L, seen, sign=1, shared=None):
    """Add (or remove) flow t; a shared hop carries the largest volume of the flows of its segment and Bank."""
    v = vol(t["k"], t["a"])
    for med, h, key in hops(t["path"]):
        dv = v
        if A.shared if shared is None else shared:
            vs = seen[(t["a"], t["b"], key)]; before = max(vs, default=0)
            vs.append(v) if sign > 0 else vs.remove(v)
            dv = sign * (max(vs, default=0) - before)
        L[med] += sign * h * dv


old = loads(circ, A.shared)
new = [dict(t) for t in circ]
L, seen = collections.Counter(fixed), collections.defaultdict(list)
order = sorted(range(len(new)), key=lambda i: -vol(new[i]["k"], new[i]["a"]))
for i in order:
    new[i]["b"], new[i]["path"] = route(new[i], L, seen); add(new[i], L, seen)
for _ in range(A.passes):
    for i in order:
        add(new[i], L, seen, -1)
        new[i]["b"], new[i]["path"] = route(new[i], L, seen); add(new[i], L, seen)
chk = loads(new, A.shared)
assert all(abs(chk[m] - L[m]) < 1e-6 for m in set(chk) | set(L)), "incremental loads drifted"
it = iter(new)
with open(A.out, "w") as f:
    for l in lines:
        if l.startswith("CIRC "):
            t = next(it)
            f.write(f"CIRC {t['k'][0]} {t['k'][1]} {t['m'][0]} {t['m'][1]} {t['a'][0]} {t['a'][1]} {t['b'][0]} {t['b'][1]} "
                    f"{len(t['path'])} " + " ".join(f"{c[0]} {c[1]}" for c in t["path"]) + "\n")
        elif l: f.write(l + "\n")
top = lambda L: ", ".join(f"{m if m[0] != 'pair' else m[1:]}: {int(x)}" for m, x in sorted(L.items(), key=lambda e: -e[1])[:4])
print(f"cluster {K}: {len(circ)} flows; frames {int(sum(old.values()))} -> {int(sum(chk.values()))}; "
      f"largest medium load {int(max(old.values()))} -> {int(max(chk.values()))}; changed Bank {sum(a['b'] != b['b'] for a, b in zip(circ, new))}, "
      f"changed path {sum(a['path'] != b['path'] for a, b in zip(circ, new))}")
print("  old top:", top(old)); print("  new top:", top(chk))
