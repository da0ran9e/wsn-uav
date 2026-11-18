"""K9 step B1: the background flow from ordinary camera nodes to their AI nodes, and which (data option, rho, number of AI
nodes) keep every medium under a duty budget (paper/j1/PLAN-K9-DATA-vi.md; parameters paper/j1/K9-PARAMS-vi.md).

    python3 bg_load.py WORK OUT_PREFIX [--n 8,16,24,32,48,64,96,128] [--fcam 0.1,0.3,1] [--umax 0.1,0.2]

WORK: a C4 mission folder (c<k>-nodes-s35.csv, c<k>-gateways-s35.csv). Every cluster keeps its own mesh, as in River:
a node is assigned to the nearest AI cell of its own cluster in cell hops (ties: the nearer centre), its records go
along a shortest cell path over the cluster's gateway pairs.

AI sets. For each total N, every cluster gets max(1, round(N * cells_k / cells)) AI cells, placed by k-medoids on the
cell-hop metric weighted by the cell's node count (greedy start, then swaps); plus Algorithm 3's own set (the
critical cells River serves now). An AI cell is a cell with an AI node; candidates are not restricted (at 816
nodes/km^2 every cell has about 4 nodes in the top 20 % of cpu, K9-PARAMS section 5).

Load model (uav-coop2/tools/river_lb.py, fitted on a coop2-river trace, R^2 0.89): a flow of v packets of 99 B costs its
source and destination cells HE v frames, every cell in between HT v frames and every gateway pair it crosses v frames.
A medium (cell or gateway pair) is busy TAU seconds per frame. Everything is linear in the byte rate per camera, so
the script computes each medium's busy fraction per unit rate (1 B/s per camera) once per AI set, and from it the
largest rho at which the busiest medium stays under the duty budget umax:
    rho_max = umax / (u_unit * fcam * size_bytes) * 3600      (people per hour per camera)
for the record sizes of options D1 (frame, 40 KB), D2 (person crop, 10 KB), D3 (512-d INT8 vector + 16 B, 528 B).
Also: the largest assignment distance (cell hops; node hops about 2.7 per cell from the River trace) and the records per
second the busiest AI node must take in at rho = 200, fcam = 0.3.
Writes OUT_PREFIX.csv (one row per AI set) and OUT_PREFIX.md (rho_max table).
"""
import argparse, collections, csv, json, math, os

PKT, HT, HE, TAU = 99, 1.7, 1.5, 6.5e-3
SIZES = {"D1": 40_000, "D2": 10_000, "D3": 528}

ap = argparse.ArgumentParser()
ap.add_argument("work"); ap.add_argument("out")
ap.add_argument("--n", default="8,16,24,32,48,64,96,128")
ap.add_argument("--fcam", default="0.1,0.3,1")
ap.add_argument("--umax", default="0.1,0.2")
A = ap.parse_args()
W = A.work
K = json.load(open(f"{W}/map.json"))["clusters"]


def bfs(src, adj):
    d, q = {src: 0}, collections.deque([src])
    while q:
        v = q.popleft()
        for g in adj[v]:
            if g not in d:
                d[g] = d[v] + 1; q.append(g)
    return d


class Cluster:
    def __init__(s, k):
        nodes = list(csv.DictReader(open(f"{W}/c{k}-nodes-s35.csv")))
        s.n = collections.Counter((int(x["q"]), int(x["r"])) for x in nodes)
        s.cells = sorted(s.n)
        s.xy = {}
        for x in nodes:
            if x["isCL"] == "1":
                s.xy[(int(x["q"]), int(x["r"]))] = (float(x["x"]), float(x["y"]))
        s.adj = collections.defaultdict(list)
        for r in csv.DictReader(open(f"{W}/c{k}-gateways-s35.csv")):
            a, b = (int(r["qA"]), int(r["rA"])), (int(r["qB"]), int(r["rB"]))
            if a in s.n and b in s.n:
                s.adj[a].append(b); s.adj[b].append(a)
        s.d = {h: bfs(h, s.adj) for h in s.cells}
        s.alg3 = None

    def medoids(s, m):
        cost = lambda S: sum(s.n[h] * min(s.d[h].get(c, 99) for c in S) for h in s.cells)
        S = []
        for _ in range(m):   # greedy start
            S.append(min((c for c in s.cells if c not in S), key=lambda c: cost(S + [c])))
        best, better = cost(S), True
        while better:   # swaps
            better = False
            for i in range(len(S)):
                for c in s.cells:
                    if c in S:
                        continue
                    T = S[:i] + [c] + S[i + 1:]
                    v = cost(T)
                    if v < best - 1e-9:
                        S, best, better = T, v, True
        return sorted(S)

    def path(s, a, b):   # a shortest cell path a -> b, the straightest among equals
        p = [a]
        while p[-1] != b:
            v = p[-1]
            nxt = [g for g in s.adj[v] if s.d[b].get(g, 99) == s.d[b][v] - 1]
            p.append(min(nxt, key=lambda g: math.dist(s.xy.get(g, (0, 0)), s.xy.get(b, (0, 0)))))
        return p

    def load(s, S):
        """Per unit rate (1 B/s per node): frames/s per medium, the assignment, and the bytes/s into each AI cell."""
        fr = collections.Counter()
        into = collections.Counter()
        far = 0
        for h in s.cells:
            a = min(S, key=lambda c: (s.d[c].get(h, 99), math.dist(s.xy.get(h, (0, 0)), s.xy.get(c, (0, 0)))))
            far = max(far, s.d[a][h])
            v = s.n[h] / PKT   # packets/s per unit rate
            into[a] += s.n[h]
            p = s.path(h, a)
            for i, c in enumerate(p):
                fr[c] += v * (HE if i in (0, len(p) - 1) else HT)
            for x, y in zip(p, p[1:]):
                fr[tuple(sorted((x, y)))] += v
        return fr, far, into


cls = {k: Cluster(k) for k in range(1, K + 1)}
import sys
sys.path[:0] = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../uav-l2/tools"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../uav-coop2/tools")]
from mission_report import load_map  # noqa: E402
M = load_map(W, schemes=())
alg3 = {k: list(M["cl"][k]["P"]["crit"]) for k in cls}
total = sum(len(c.cells) for c in cls.values())
sets = []
for N in map(int, A.n.split(",")):
    sets.append((f"N{N}", {k: c.medoids(max(1, round(N * len(c.cells) / total))) for k, c in cls.items()}))
sets.append(("alg3", alg3))

rows = []
for name, S in sets:
    u_max, far, into_max = 0.0, 0, 0.0
    for k, c in cls.items():
        fr, f, into = c.load(S[k])
        u_max = max(u_max, max(fr.values()) * TAU)
        far = max(far, f)
        into_max = max(into_max, max(into.values()))
    row = dict(set=name, ai=sum(map(len, S.values())), u_unit=u_max, far_cells=far, nodes_max=into_max)
    rows.append(row)

fc = [float(x) for x in A.fcam.split(",")]
um = [float(x) for x in A.umax.split(",")]
with open(A.out + ".csv", "w") as f:
    w = csv.writer(f)
    w.writerow(["set", "ai_cells", "u_per_Bps_per_node", "far_cells", "nodes_into_busiest_ai"] +
               [f"rho_max_{d}_f{x:g}_u{u:g}" for d in SIZES for x in fc for u in um])
    for r in rows:
        w.writerow([r["set"], r["ai"], f"{r['u_unit']:.6g}", r["far_cells"], r["nodes_max"]] +
                   [f"{u / (r['u_unit'] * x * SIZES[d]) * 3600:.4g}" for d in SIZES for x in fc for u in um])
with open(A.out + ".md", "w") as f:
    f.write(f"# Background flow to AI nodes: largest rho (people/h per camera) under the duty budget\n\n"
            f"Map {os.path.basename(W.rstrip('/'))}, {total} cells, {sum(sum(c.n.values()) for c in cls.values())} nodes. "
            f"Budget umax, camera share fcam. far: largest assignment distance in cells.\n\n")
    for u in um:
        for x in fc:
            f.write(f"\n## umax {u:g}, fcam {x:g}\n\n| set | AI cells | far (cells) | nodes into busiest AI | "
                    + " | ".join(f"rho_max {d}" for d in SIZES) + " |\n|" + "---|" * (4 + len(SIZES)) + "\n")
            for r in rows:
                f.write(f"| {r['set']} | {r['ai']} | {r['far_cells']} | {r['nodes_max']} | "
                        + " | ".join(f"{u / (r['u_unit'] * x * SIZES[d]) * 3600:.3g}" for d in SIZES) + " |\n")
print(open(A.out + ".md").read())
