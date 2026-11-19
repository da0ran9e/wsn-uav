"""Place IoT nodes on a real district map and check the cell grid: connectivity and holes (J1 context, chatlog item 356).

    python3 paper/j1/analysis/urban_nodes.py MAP_DIR NAME FIG_DIR [--density 816] [--seed 1] [--wall 15]

MAP_DIR is an output folder of osm_district.py (boundary, water_all, buildings.csv.gz, roads.csv.gz, local metres).

Placement (where such devices really stand):
  building nodes  doorbells and wall cameras: points every 40 m along each building outline (at least one per building),
                  1.5 m outside the wall; a building node runs on battery with probability --battery (default 0.45),
                  and a battery node only talks to a mains node of its own cell, it does not relay (Thread rule)
  street nodes    pole cameras and vending machines: points every 30 m along streets, 5 m to alternate sides; mains
  nothing on water. If the candidates exceed DENSITY x land area they are subsampled uniformly; if fewer, all are used.
Channel: the G2G model of the simulator (params.yaml C7-C9): 10 dBm, 40.05 dB at 1 m, exponent 3.5, log-normal shadowing
7.8 dB per pair, Rayleigh: q = exp(-10^((S - mean)/10)), S = -101.04 dBm; a link is usable when q >= 0.5. Two variants:
  open    as in the simulator now (no geometry)
  walls   minus --wall dB for every building footprint the straight segment crosses (up to 3), a first step to K1c
Cells: flat-top hexagons, R = 100 m. Per variant: land cells; empty cells (no mains node); cells whose mains nodes are
split (no usable path inside the cell); adjacent pairs of non-empty cells without a usable gateway link; battery nodes
with no usable link to a mains node of their cell; components of the cell graph (cells joined by gateway links) and the
share of non-empty cells in the largest one.
Writes FIG_DIR/cells-NAME-<variant>.png (no text) and prints a Markdown table row per variant.
"""
import argparse, csv, gzip, json, math, os
import numpy as np
from scipy.spatial import cKDTree
from shapely import wkt as swkt, STRtree, prepared
from shapely.geometry import shape, Point, LineString, Polygon
from shapely.ops import unary_union

ap = argparse.ArgumentParser()
ap.add_argument("map"); ap.add_argument("name"); ap.add_argument("figs")
ap.add_argument("--density", type=float, default=816.0); ap.add_argument("--seed", type=int, default=1)
ap.add_argument("--battery", type=float, default=0.45); ap.add_argument("--wall", type=float, default=15.0)
A = ap.parse_args()
rng = np.random.default_rng(A.seed)
PT, F1, NEXP, SIG, S, R = 10.0, 40.05, 3.5, 7.8, -101.04, 100.0

bound = shape(json.load(open(f"{A.map}/boundary.geojson"))["features"][0]["geometry"])
wf = json.load(open(f"{A.map}/water_all.geojson"))["features"]
water = shape(wf[0]["geometry"]) if wf else Polygon()
land = bound.difference(water); pl = prepared.prep(land)
blds = [swkt.loads(r["wkt"]) for r in csv.DictReader(gzip.open(f"{A.map}/buildings.csv.gz", "rt"))]
blds = [b for b in blds if not b.is_empty and b.geom_type in ("Polygon", "MultiPolygon")]
roads = [swkt.loads(r["wkt"]) for r in csv.DictReader(gzip.open(f"{A.map}/roads.csv.gz", "rt"))]

# candidates
cand, kind = [], []
for b in blds:
    ring = b.buffer(1.5).exterior if b.geom_type == "Polygon" else b.buffer(1.5).convex_hull.exterior
    k = max(1, int(round(ring.length / 40)))
    for i in range(k):
        p = ring.interpolate((i + 0.5) / k, normalized=True); cand.append((p.x, p.y)); kind.append(0)
for r in roads:
    n = int(r.length // 30)
    for i in range(n):
        d = (i + 0.5) * 30; p = r.interpolate(d); q = r.interpolate(min(d + 1, r.length))
        dx, dy = q.x - p.x, q.y - p.y; L = math.hypot(dx, dy) or 1; side = 5 if i % 2 else -5
        cand.append((p.x - dy / L * side, p.y + dx / L * side)); kind.append(1)
cand = np.array(cand); kind = np.array(kind)
inside = np.array([pl.contains(Point(x, y)) for x, y in cand])
cand, kind = cand[inside], kind[inside]
target = int(A.density * land.area / 1e6)
if len(cand) > target:
    sel = rng.choice(len(cand), target, replace=False); cand, kind = cand[sel], kind[sel]
battery = (kind == 0) & (rng.random(len(cand)) < A.battery)
N = len(cand)

# cells (flat-top axial)
def hexcell(x, y):
    q = (2 / 3 * x) / R; r = (-x / 3 + math.sqrt(3) / 3 * y) / R
    xq, zq = q, r; yq = -xq - zq
    rx, ry, rz = round(xq), round(yq), round(zq)
    dx, dy, dz = abs(rx - xq), abs(ry - yq), abs(rz - zq)
    if dx > dy and dx > dz: rx = -ry - rz
    elif dy > dz: ry = -rx - rz
    else: rz = -rx - ry
    return (rx, rz)
cell = [hexcell(x, y) for x, y in cand]
centre = lambda c: (1.5 * R * c[0], math.sqrt(3) * R * (c[1] + c[0] / 2))
hexpoly = lambda c: Polygon([(centre(c)[0] + R * math.cos(math.pi / 3 * k), centre(c)[1] + R * math.sin(math.pi / 3 * k)) for k in range(6)])
# land cells: centre inside the district, at least half land
x0, y0, x1, y1 = bound.bounds
land_cells = set()
for qq in range(int(x0 / (1.5 * R)) - 2, int(x1 / (1.5 * R)) + 3):
    for rr in range(int(y0 / (math.sqrt(3) * R) - qq / 2) - 3, int(y1 / (math.sqrt(3) * R) - qq / 2) + 4):
        c = (qq, rr)
        if bound.contains(Point(centre(c))):
            h = hexpoly(c)
            if land.intersection(h).area >= 0.5 * h.area: land_cells.add(c)
water_cells = sum(1 for qq in range(int(x0 / (1.5 * R)) - 2, int(x1 / (1.5 * R)) + 3)
                  for rr in range(int(y0 / (math.sqrt(3) * R) - qq / 2) - 3, int(y1 / (math.sqrt(3) * R) - qq / 2) + 4)
                  if bound.contains(Point(centre((qq, rr)))) and (qq, rr) not in land_cells)

# links
tree = cKDTree(cand)
pairs = np.array(sorted(tree.query_pairs(280.0)))
d = np.hypot(*(cand[pairs[:, 0]] - cand[pairs[:, 1]]).T)
sh = rng.normal(0, SIG, len(pairs))
mean = PT - F1 - 10 * NEXP * np.log10(np.maximum(d, 1)) - sh
qopen = np.exp(-10 ** ((S - mean) / 10))
walls = np.zeros(len(pairs))
cands = np.nonzero(qopen >= 0.5)[0]
if len(cands) and blds:
    bt = STRtree(blds)
    segs = [LineString([cand[pairs[i, 0]], cand[pairs[i, 1]]]) for i in cands]
    hit = bt.query(segs, predicate="intersects")
    np.add.at(walls, cands[hit[0]], 1)
qwall = np.exp(-10 ** ((S - (mean - A.wall * np.minimum(walls, 3))) / 10))


def analyse(qv):
    ok = qv >= 0.5
    P = pairs[ok]
    mains = ~battery
    same = np.array([cell[a] == cell[b] for a, b in P]) if len(P) else np.array([], bool)
    # in-cell union-find over mains nodes
    par = list(range(N))
    def f(x):
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    gw = set(); orphan_ok = np.zeros(N, bool)
    for (a, b), sm in zip(P, same):
        if sm:
            if mains[a] and mains[b]: par[f(a)] = f(b)
            elif mains[a] or mains[b]: orphan_ok[b if mains[a] else a] = True
        elif mains[a] and mains[b]:
            gw.add(tuple(sorted((cell[a], cell[b]))))
    comps = {}
    for i in range(N):
        if mains[i]: comps.setdefault(cell[i], set()).add(f(i))
    nonempty = [c for c in comps if c in land_cells]
    split = sum(1 for c in nonempty if len(comps[c]) > 1)
    empty = len(land_cells) - len(nonempty)
    nb = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]
    adj = [(c, (c[0] + a, c[1] + b)) for c in nonempty for a, b in nb if (c[0] + a, c[1] + b) in comps and (c[0] + a, c[1] + b) > c]
    nogw = sum(1 for e in adj if tuple(sorted(e)) not in gw)
    # cell graph components
    cp = {c: c for c in comps}
    def g(x):
        while cp[x] != x: cp[x] = cp[cp[x]]; x = cp[x]
        return x
    for a, b in gw:
        if a in cp and b in cp: cp[g(a)] = g(b)
    sizes = {}
    for c in nonempty: sizes[g(c)] = sizes.get(g(c), 0) + 1
    giant = max(sizes.values()) if sizes else 0
    orph = int(np.sum(battery & ~orphan_ok))
    return dict(empty=empty, split=split, nogw=nogw, adj=len(adj), comps=len(sizes), giant=giant, nonempty=len(nonempty),
                orph=orph, gw=gw, comps_map=comps, root={c: g(c) for c in nonempty}, sizes=sizes)


import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, PathPatch
from matplotlib.path import Path as MPath
print(f"| Bản đồ | Biến thể | Node (node/km² đất) | Chạy pin | Cell đất | Cell nước | Cell rỗng | Cell đứt bên trong | Cặp kề không có gateway | "
      f"Thành phần | Cell trong thành phần lớn nhất | Node pin không với tới node điện |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|")
for name, qv in (("open", qopen), ("walls", qwall)):
    r = analyse(qv)
    print(f"| {A.name} | {name} | {N} ({N / (land.area / 1e6):.0f}) | {battery.mean() * 100:.0f} % | {len(land_cells)} | {water_cells} | "
          f"{r['empty']} ({r['empty'] / max(len(land_cells), 1) * 100:.0f} %) | {r['split']} ({r['split'] / max(r['nonempty'], 1) * 100:.0f} %) | "
          f"{r['nogw']} / {r['adj']} ({r['nogw'] / max(r['adj'], 1) * 100:.0f} %) | {r['comps']} | "
          f"{r['giant'] / max(r['nonempty'], 1) * 100:.1f} % | {r['orph']} ({r['orph'] / max(battery.sum(), 1) * 100:.0f} %) |", flush=True)
    W_, H_ = x1 - x0, y1 - y0
    fig = plt.figure(figsize=(8, 8 * H_ / W_)); ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(x0 - 50, x1 + 50); ax.set_ylim(y0 - 50, y1 + 50); ax.set_aspect("equal"); ax.axis("off")
    for g in getattr(water, "geoms", [water]):
        if g.geom_type == "Polygon": ax.add_patch(MPoly(np.array(g.exterior.coords), facecolor="#7fb3e0", edgecolor="none"))
    big = max(r["sizes"], key=r["sizes"].get) if r["sizes"] else None
    for c in land_cells:
        h = np.array(hexpoly(c).exterior.coords)
        if c not in r["comps_map"]: col = "#ffffff"                       # empty
        elif r["root"].get(c) != big: col = "#d62728"                    # cut off from the main grid
        elif len(r["comps_map"][c]) > 1: col = "#ff9f40"                 # split inside
        else: col = "#a6d39a"                                            # fine
        ax.add_patch(MPoly(h, facecolor=col, edgecolor="#777777", lw=0.2))
    ax.plot(*np.array(bound.exterior.coords).T, c="#222222", lw=1)
    sub = rng.choice(N, min(N, 6000), replace=False)
    ax.scatter(cand[sub, 0], cand[sub, 1], s=0.3, c=np.where(battery[sub], "#7f7f7f", "#222222"), lw=0)
    os.makedirs(A.figs, exist_ok=True); fig.savefig(f"{A.figs}/cells-{A.name}-{name}.png", dpi=140); plt.close(fig)
