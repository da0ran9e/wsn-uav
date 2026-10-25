"""Excess A2G loss for the three environments of CLAUDE.md §8 item 163, calibrated on the ns-3 pass.

    python3 tools/a2g_env.py BIN WORK [--targets 500,200,100]

WORK holds one cluster's c1-nodes-s35.csv and c1-path-s35.csv. For an excess loss L the pass (BIN/pass-bin
--lossDb=L, mission 1) is flown once; every (node, packet) pair is binned by the horizontal distance r from the
UAV to the node when the packet was sent (10 m bins), and p(r) is the share of those packets received. R50 is
where p(r) falls to 1/2, R10 to 1/10 (linear between bins). With the two-segment path loss, an excess loss L
scales the slant distance of a given received power by 10^(-L / 30); the search starts there and then corrects
on the measured R50 (secant in L against log slant R50) until it is within 2 % of the target.
"""
import argparse, csv, math, os, subprocess

import numpy as np

H, BIN_M = 100.0, 10.0


def fly(b, w, loss):
    out = f"env{loss:.2f}"
    if not os.path.exists(f"{w}/{out}-bits-r1.bin"):
        subprocess.run([f"{b}/pass-bin", "--nodes=c1-nodes-s35.csv", "--path=c1-path-s35.csv", "--firstRun=1",
                        "--runs=1", "--bits", f"--lossDb={loss:.2f}", f"--out={out}"], cwd=w, check=True,
                       stdout=subprocess.DEVNULL, env=dict(os.environ, LD_LIBRARY_PATH=f"{b}/pass-lib"))
    nodes = np.array([[float(r["x"]), float(r["y"])] for r in csv.DictReader(open(f"{w}/c1-nodes-s35.csv"))])
    uav = np.array([[float(r["x"]), float(r["y"])] for r in csv.DictReader(open(f"{w}/{out}-track.csv"))])
    got = np.unpackbits(np.fromfile(f"{w}/{out}-bits-r1.bin", dtype=np.uint8).reshape(len(nodes), -1),
                        axis=1)[:, :len(uav)]
    r = np.hypot(nodes[:, None, 0] - uav[None, :, 0], nodes[:, None, 1] - uav[None, :, 1])
    k = (r / BIN_M).astype(int).ravel()
    n, g = np.bincount(k), np.bincount(k, weights=got.ravel())
    keep = n >= 200
    return (np.arange(len(n)) * BIN_M + BIN_M / 2)[keep], (g / np.maximum(n, 1))[keep]


def radius(rr, p, level):
    i = int(np.argmax(p < level))
    return float(np.interp(level, [p[i], p[i - 1]], [rr[i], rr[i - 1]])) if i else 0.0


def slant(x):
    return math.hypot(x, H)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bin")
    ap.add_argument("work")
    ap.add_argument("--targets", default="500,200,100")
    a = ap.parse_args()
    b, w = os.path.abspath(a.bin), os.path.abspath(a.work)
    rows = []

    def measure(loss):
        rr, p = fly(b, w, loss)
        rows.append((loss, radius(rr, p, 0.5), radius(rr, p, 0.1),
                     *(float(np.interp(x, rr, p)) for x in (0, 100, 200, 500))))
        print(f"loss {loss:5.2f} dB: R50 {rows[-1][1]:5.0f} m, R10 {rows[-1][2]:5.0f} m", flush=True)
        return rows[-1][1]

    r0 = measure(0.0)
    found = {}
    for t in map(float, a.targets.split(",")):
        l1 = 30 * math.log10(slant(r0) / slant(t))
        r1 = measure(round(l1, 2))
        l0, s0 = 0.0, slant(r0)
        while abs(r1 - t) > 0.02 * t:
            l2 = l1 + (l1 - l0) * (math.log10(slant(t)) - math.log10(slant(r1))) / (
                math.log10(slant(r1)) - math.log10(s0))
            l0, s0, l1 = l1, slant(r1), round(l2, 2)
            r1 = measure(l1)
        found[t] = (l1, r1)
    print("\n| excess loss (dB) | R50 (m) | R10 (m) | p(0) | p(100 m) | p(200 m) | p(500 m) |\n|---|---|---|---|---|---|---|")
    for row in sorted(set(rows)):
        print("| {:.2f} | {:.0f} | {:.0f} | {:.3f} | {:.3f} | {:.3f} | {:.3f} |".format(*row))
    print("\n" + ", ".join(f"R50 {t:.0f} m: {l:.2f} dB (measured {r:.0f} m)" for t, (l, r) in found.items()))


if __name__ == "__main__":
    main()
