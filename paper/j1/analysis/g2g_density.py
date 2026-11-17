"""How node spacing affects the G2G cell grid (J1 context, chatlog item 333). Monte Carlo, no ns-3.

    python3 paper/j1/analysis/g2g_density.py [--trials 300] [--seed 1]

Geometry: hexagonal cells of circumradius R = 100 m; a centre cell and its 6 neighbours; nodes uniform at density
1/s^2 (s = node spacing, as in uav-coop deploy: nodes = area / s^2). G2G channel of the simulator (params.yaml C7-C9):
P_tx 10 dBm, 40.05 dB at 1 m, exponent 3.5, static log-normal shadowing sigma 7.8 dB per pair, Rayleigh fading;
a frame gets through with q = exp(-10^((S - mean)/10)), S = -101.04 dBm. A link is usable when q >= Q (default 0.5,
the simulator's "weak gateway pair" line); a good link has q >= 0.9.
Per spacing: nodes per cell; share of empty cells; share of cells whose usable-link graph is connected (every node
reaches the CL, here any node of the cell); share of adjacent cell pairs with at least one usable (good) node pair, the
gateway the BS would pick; q of the best pair; and the median hop length and ETX per 100 m of the in-cell shortest
paths (ETX = sum of 1/q) from every node to the cell's most central node.
"""
import argparse, heapq, math
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--trials", type=int, default=300); ap.add_argument("--seed", type=int, default=1)
ap.add_argument("--Q", type=float, default=0.5)
A = ap.parse_args()
R, PT, F1, N_EXP, SIG, S = 100.0, 10.0, 40.05, 3.5, 7.8, -101.04
rng = np.random.default_rng(A.seed)
centres = [(0.0, 0.0)] + [(math.sqrt(3) * R * math.cos(math.pi / 6 + k * math.pi / 3),
                            math.sqrt(3) * R * math.sin(math.pi / 6 + k * math.pi / 3)) for k in range(6)]
AREA = 1.5 * math.sqrt(3) * R * R


def in_hex(x, y):                    # flat-top hexagon (vertices at 0°, 60°, ...): neighbours lie at 30° + k·60°
    x, y = abs(x), abs(y)
    return y <= math.sqrt(3) / 2 * R and math.sqrt(3) * x + y <= math.sqrt(3) * R


def drop(cx, cy, n):
    pts = []
    while len(pts) < n:
        x, y = rng.uniform(-R, R, 2)
        if in_hex(x, y): pts.append((cx + x, cy + y))
    return np.array(pts).reshape(-1, 2)


def q_of(d, shadow):
    mean = PT - F1 - 10 * N_EXP * np.log10(np.maximum(d, 1.0)) - shadow
    return np.exp(-10 ** ((S - mean) / 10))


print("| s (m) | node/km² | node/cell | empty cells | cells connected (q≥%.1f) | adjacent pairs with a usable / good gateway | best gateway q, median | in-cell hop, median (m) | ETX per 100 m |" % A.Q)
print("|---|---|---|---|---|---|---|---|---|")
for s in (20, 35, 50, 60, 70, 85, 100):
    lam = 1 / s ** 2; mean_n = lam * AREA
    empty = conn = pairs_ok = pairs_good = 0; ncell = npair = 0; bestq, hopl, etx100 = [], [], []
    for _ in range(A.trials):
        cells = [drop(cx, cy, rng.poisson(mean_n)) for cx, cy in centres]
        # centre cell: connectivity and paths
        P = cells[0]; ncell += 1
        if len(P) == 0: empty += 1
        else:
            d = np.hypot(*(P[:, None, :] - P[None, :, :]).transpose(2, 0, 1))
            sh = rng.normal(0, SIG, d.shape); sh = np.triu(sh, 1); sh = sh + sh.T
            q = q_of(d, sh); np.fill_diagonal(q, 0)
            ok = q >= A.Q
            root = int(np.argmin(np.hypot(P[:, 0], P[:, 1])))
            dist = np.full(len(P), np.inf); dist[root] = 0; prev = np.full(len(P), -1); pq = [(0.0, root)]
            while pq:
                du, u = heapq.heappop(pq)
                if du > dist[u]: continue
                for v in np.nonzero(ok[u])[0]:
                    nd = du + 1 / q[u, v]
                    if nd < dist[v]: dist[v] = nd; prev[v] = u; heapq.heappush(pq, (nd, v))
            conn += np.all(np.isfinite(dist))
            for v in range(len(P)):
                if v == root or not np.isfinite(dist[v]): continue
                hopl.append(d[v, prev[v]])
                L = math.hypot(*(P[v] - P[root]))
                if L > 50: etx100.append(dist[v] / L * 100)
        # gateways centre <-> each neighbour
        for k in range(1, 7):
            npair += 1
            B = cells[k]
            if len(P) == 0 or len(B) == 0: continue
            d = np.hypot(*(P[:, None, :] - B[None, :, :]).transpose(2, 0, 1))
            qq = q_of(d, rng.normal(0, SIG, d.shape)).max()
            bestq.append(qq); pairs_ok += qq >= A.Q; pairs_good += qq >= 0.9
    print(f"| {s} | {1e6 * lam:.0f} | {mean_n:.1f} | {empty / ncell * 100:.1f} % | {conn / ncell * 100:.1f} % | "
          f"{pairs_ok / npair * 100:.1f} % / {pairs_good / npair * 100:.1f} % | {np.median(bestq):.3f} | "
          f"{np.median(hopl) if hopl else float('nan'):.0f} | {np.median(etx100) if etx100 else float('nan'):.2f} |")
