"""Upper bound on the TAKEOVER report round that the simulation idealised (oracle holder discovery).

    python3 report_bound.py   -> report-bound.md

From the existing wind runs (pass bits, plan, nodes, routes, gateways; no new simulation), for every SPINE (Axe) cell a:
  oracle pairs   the (a, b) pairs the simulated takeover used: packets of Seg(a) heard by no node of a or of an
                 adjacent cell, each assigned to the nearest cell b (BFS over gateway links) that heard it
                 (same rule as coop2-river.cc --takeover)
  naive holders  every cell b outside a and its neighbours that heard any packet of Seg(a), i.e. who would report
                 if holders reported unconditionally (holders cannot know whether a misses the packet)
Report frame: 2 B SPINE id + 4 B per packet range, 88 B payload -> 21 ranges per frame.
Radio hops of a cell path: per cell hop, the CL's hops to the next cell (routes toCells) plus the entry gateway's hops
to that cell's CL. Delay per radio hop tau = 7 ms (4.3 ms max frame + unslotted CSMA backoff + ACK; RETRY = 4 tries).
  critical path   longest report: radio hops x frames x tau
  serialised      every report radio transmission of the cluster back to back, x RETRY (no spatial reuse at all)
"""
import csv, collections, math, os
S = "/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/WIND"
H = os.path.dirname(os.path.abspath(__file__))
TAU, RETRY, PER = 0.007, 4, 21
ADJ = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]

def cluster(w, k):
    nodes = list(csv.DictReader(open(f"{w}/c{k}-nodes-s35.csv")))
    cell = [(int(n["q"]), int(n["r"])) for n in nodes]
    members, cl = collections.defaultdict(list), {}
    for i, n in enumerate(nodes):
        members[cell[i]].append(i)
        if n["isCL"] == "1": cl[cell[i]] = i
    routes = list(csv.DictReader(open(f"{w}/c{k}-routes-s35.csv")))
    hopsCL = {int(r["id"]): int(r["hopsCL"]) for r in routes}
    toh = {}
    for r in routes:
        for e in r["toCells"].split("|"):
            c, rest = e.split(">"); q, rr = map(int, c.split(":"))
            toh[(int(r["id"]), (q, rr))] = int(rest.split("/")[1])
    gw = {}
    for r in csv.DictReader(open(f"{w}/c{k}-gateways-s35.csv")):
        A, B = (int(r["qA"]), int(r["rA"])), (int(r["qB"]), int(r["rB"]))
        gw[(A, B)] = int(r["gwB"]); gw[(B, A)] = int(r["gwA"])
    lines = open(f"{w}/plan{k}.txt").read().split("\n")
    N = int(lines[0].split()[1])
    seg = {(int(p[1]), int(p[2])): (int(p[3]), int(p[4])) for p in (l.split() for l in lines) if p and p[0] == "AXE"}
    rb = (N + 7) // 8
    raw = open(f"{w}/pass{k}-bits-r1.bin", "rb").read()
    heard = collections.defaultdict(set)   # cell -> packets heard by any of its nodes
    for i in range(len(nodes)):
        row = raw[i * rb:(i + 1) * rb]
        for s in range(N):
            if row[s >> 3] >> (s & 7) & 1: heard[cell[i]].add(s)
    out = []
    for a, (f, l) in seg.items():
        nb = [a] + [(a[0] + d[0], a[1] + d[1]) for d in ADJ if (a, (a[0] + d[0], a[1] + d[1])) in gw]
        seen = set().union(*(heard[c] for c in nb))
        par, order = {a: a}, [a]
        for c in order:
            for d in ADJ:
                c2 = (c[0] + d[0], c[1] + d[1])
                if c2 in par or c2 not in cl or (c, c2) not in gw: continue
                par[c2] = c; order.append(c2)
        dist = {}
        for c in order: dist[c] = 0 if c == a else dist[par[c]] + 1
        def radio(b):   # report path b -> a
            p = [b]
            while p[-1] != a: p.append(par[p[-1]])
            return sum(toh.get((cl[p[i]], p[i + 1]), 3) + hopsCL.get(gw[(p[i], p[i + 1])], 3) for i in range(len(p) - 1))
        pkts = collections.defaultdict(list)
        for s in range(f, l + 1):
            if s in seen: continue
            b = next((c for c in order[1:] if s in heard[c]), None)
            if b: pkts[b].append(s)
        naive = [c for c in order if c not in nb and any(f <= s <= l for s in heard[c])]
        for b, xs in pkts.items():
            rng = 1 + sum(1 for i in range(1, len(xs)) if xs[i] != xs[i - 1] + 1)
            out.append(dict(kind="oracle", a=a, b=b, hops=dist[b], radio=radio(b), frames=math.ceil(rng / PER), pkts=len(xs)))
        for b in naive:
            out.append(dict(kind="naive", a=a, b=b, hops=dist[b], radio=radio(b), frames=1, pkts=0))
    return out

L = ["| σ | seed | cặp oracle | SPINE cell thiếu | hop cell max | hop radio max | frame/báo cáo max | trễ đường dài nhất | trễ tuần tự hoá ×4 (cụm xấu nhất) | báo cáo ngây thơ (mọi người giữ) |", "|---" * 10 + "|"]
for sig in (50, 100):
    for R in (1, 2, 3):
        w = f"{S}/s{sig}/R{R}/k8-s1"
        rows = {k: cluster(w, k) for k in range(1, 9)}
        o = [x for k in rows for x in rows[k] if x["kind"] == "oracle"]
        nv = [x for k in rows for x in rows[k] if x["kind"] == "naive"]
        crit = max((x["radio"] * x["frames"] * TAU for x in o), default=0)
        ser = max((sum(x["radio"] * x["frames"] for x in rows[k] if x["kind"] == "oracle") * TAU * RETRY for k in rows), default=0)
        L.append(f"| {sig} | {R} | {len(o)} | {len({(x['a']) for x in o})} | {max((x['hops'] for x in o), default=0)} | "
                 f"{max((x['radio'] for x in o), default=0)} | {max((x['frames'] for x in o), default=0)} | {crit:.2f} s | {ser:.2f} s | "
                 f"{len(nv)} báo cáo, hop cell max {max((x['hops'] for x in nv), default=0)} |")
open(f"{H}/report-bound.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
