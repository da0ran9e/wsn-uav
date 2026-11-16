"""Shared loaders and the A2G reception model for the J1 draft analyses (paper/j1/draft-v1/analysis)."""
import csv, glob, json, os
import numpy as np
from scipy.stats import ncx2

ENVS = {"open": 0.00, "r500": 9.03, "r200": 19.77, "r100": 25.74}      # excess loss L_obs (dB)
R50 = {"open": 1016, "r500": 498, "r200": 199, "r100": 99}             # horizontal 50 % range (m), measured on the ns-3 pass
MAPS = {"k8-s1": 8, "k12-s1": 12, "k16-s1": 15}                        # map -> number of clusters
S_EFF, PTX, FSPL1, DREF, ALPHA, K, H = -101.04, 10.0, 40.05, 100.0, 3.0, 2.0, 100.0
TP, Q, VMAX = 0.01, 4041, 50.0


def p_node(d, L):
    """Probability that one node at horizontal distance d (m) receives one packet; channel fitted on the ns-3 passes."""
    sl = np.hypot(d, H)
    pl = np.where(sl <= DREF, FSPL1 + 20 * np.log10(sl), FSPL1 + 20 * np.log10(DREF) + 10 * ALPHA * np.log10(sl / DREF))
    return ncx2.sf(2 * (K + 1) * 10 ** ((S_EFF - (PTX - pl - L)) / 10), 2, 2 * K)


_TAB = {}


def p_fast(d, L):
    """p_node by linear interpolation on a 1 m table (error below 1e-4), zero beyond 6 km."""
    if L not in _TAB: _TAB[L] = p_node(np.arange(0, 6001, 1.0), L)
    return np.interp(d, np.arange(0, 6001, 1.0), _TAB[L], right=0.0)


def p_cell(x, nodes, L):
    """Cell-level reception at UAV positions x (n,2): at least one node of the cell hears the packet."""
    q = np.ones(len(x))
    for u in nodes:
        q *= 1 - p_fast(np.hypot(x[:, 0] - u[0], x[:, 1] - u[1]), L)
    return 1 - q


def critical_cells(work):
    """[(cluster, (q, r), node positions (m,2))] of every critical cell of the mission folder `work`."""
    out = []
    for f in sorted(glob.glob(f"{work}/plan*.txt"), key=lambda s: int(s.split("plan")[-1][:-4])):
        k = int(f.split("plan")[-1][:-4])
        crit = {(int(a), int(b)) for _, a, b in (l.split()[:3] for l in open(f) if l.startswith("CRIT "))}
        rows = list(csv.DictReader(open(f"{work}/c{k}-nodes-s35.csv")))
        for c in sorted(crit):
            pts = np.array([(float(r["x"]), float(r["y"])) for r in rows if (int(r["q"]), int(r["r"])) == c])
            out.append((k, c, pts))
    return out


def base_station(work):
    return np.array(json.load(open(f"{work}/map.json"))["bs"], float)
