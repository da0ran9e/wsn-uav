"""Energy of the ground transport and of team 1's flight (CLAUDE.md §8 item 227, part 3; docs/ENERGY-vi.md).

    python3 tools/energy.py radio RESULTS PLANS [--out CSV]     RESULTS: r<k>-<scheme>-energy.csv (coop2-river),
                                                                 PLANS: plan<k>.txt (river_export.py) of the same map
    python3 tools/energy.py uav WORK [KIND]                      team 1's tour (kin_time.run), KIND default kin

Radio: E = V (I_tx txS + I_rx rxS + I_listen listenS + I_off offS) per node, from the PHY state times ns-3 traced
(BUSY_TX, BUSY_RX, RX_ON/TX_ON idle, TRX_OFF). Listening is a receiver switched on, so I_listen = I_rx. Two chips
(CHIPS), two modes: "on" as simulated (every radio on when idle); "sched" for the planned schemes (rf, d): a node
powers down (I_sleep) after its last frame began to send (lastTxS); Trickle (t, tp) has to keep listening for
advertisements, so its "sched" equals "on". Per (cluster, scheme, chip, mode): total, max node, max node of each cell
role (crit, axe, bank, circle, relay, other; from the plan), frames sent and received.

UAV: Zeng & Zhang, IEEE TWC 16(6) 2017, fixed wing with the acceleration term:
    P(v, a) = c1 v^3 + c2 / v (1 + (|a|^2 - (a.v)^2 / v^2) / g^2),   E = sum P dt + m/2 (v_end^2 - v_0^2)
over kin_time's speed profile (bank 45 deg), with the delivery fixes flown at VMIN (circling at 45 deg bank: 1 g).
"""
import argparse, csv, glob, math, os, re, sys
from collections import defaultdict

# chip: supply V, currents A (tx at the simulated +10 dBm where the chip has it)
CHIPS = {
    # TI CC2420 datasheet SWRS041c, electrical specifications: TX 17.4 mA at 0 dBm (its maximum), RX 18.8 mA,
    # idle (oscillator on, radio off) 426 uA, power down 20 uA; 3.0 V within 2.1-3.6 V
    "cc2420": dict(V=3.0, tx=17.4e-3, rx=18.8e-3, off=426e-6, sleep=20e-6),
    # Silicon Labs EFR32MG21 (A, +10 dBm PA) datasheet: TX 33.8 mA at +10 dBm, RX 9.4 mA (802.15.4, 250 kbps),
    # radio off with the core in EM2 5.0 uA (96 kB RAM, RTC on LFXO); 3.0 V
    "efr32mg21": dict(V=3.0, tx=33.8e-3, rx=9.4e-3, off=5.0e-6, sleep=5.0e-6),
}
PLANNED = ("rf", "d", "d2")   # d2: direct pull with River's repairs
ROLES = ("crit", "axe", "bank", "circle", "relay", "other")

C1, C2, M_UAV, G = 9.26e-4, 2250.0, 10.0, 9.80665   # Zeng & Zhang 2017, Sec. VI (m only enters dK)


def roles(path):
    """cell (q, r) -> its role in the River plan; the first role a cell takes in ROLES order wins."""
    got = defaultdict(set)
    cells = lambda t, i: [(int(t[j]), int(t[j + 1])) for j in range(i + 1, i + 1 + 2 * int(t[i]), 2)]
    for line in open(path):
        t = line.split()
        if not t:
            continue
        c = lambda i: (int(t[i]), int(t[i + 1]))
        k = t[0]
        if k == "CRIT":
            got[c(1)].add("crit")
        elif k == "AXE":
            got[c(1)].add("axe")
        elif k == "BANK":
            got[c(4)].add("bank"); path_ = cells(t, 6)
            for x in path_: got[x].add("relay")
        elif k in ("CIRC", "CSRC"):
            got[c(3)].add("circle")
            for x in cells(t, 9): got[x].add("relay")
        elif k == "CSET":
            got[c(4)].add("circle")                               # one member per line: CSET k n m first last
        elif k in ("DIRECT", "CLINK"):
            for x in cells(t, 5): got[x].add("relay")
    return {x: next(r for r in ROLES if r in s) for x, s in got.items()}


def node_energy(row, chip, mode):
    ch, f = CHIPS[chip], {k: float(row[k]) for k in ("txS", "rxS", "listenS", "offS", "lastTxS", "radios")}
    tx, rx, ls, off, sleep = f["txS"], f["rxS"], f["listenS"], f["offS"], 0.0
    if mode == "sched" and row["scheme"] in PLANNED:
        span = (tx + rx + ls + off) / f["radios"]                # each radio's time from the mission start
        sleep = f["radios"] * max(0.0, span - max(f["lastTxS"], 0.0))   # after its last frame: nothing more to send
        cut = min(sleep, ls); ls -= cut; rx -= min(sleep - cut, rx)   # what it would have listened to / overheard
    return ch["V"] * (ch["tx"] * tx + ch["rx"] * (rx + ls) + ch["off"] * off + ch["sleep"] * sleep)


def radio(a):
    out = []
    for fn in sorted(glob.glob(os.path.join(a.results, "r*-*-energy.csv"))):
        k, scheme = re.match(r"r(\d+)-(\w+)-energy\.csv", os.path.basename(fn)).groups()
        role = roles(os.path.join(a.plans, f"plan{k}.txt"))
        rows = list(csv.DictReader(open(fn)))
        for run in sorted({r["run"] for r in rows}):
            rr = [r for r in rows if r["run"] == run]
            for chip in CHIPS:
                for mode in ("on", "sched"):
                    e = [(node_energy(r, chip, mode), role.get((int(r["q"]), int(r["r"])), "other")) for r in rr]
                    rec = dict(cluster=int(k), scheme=scheme, run=run, chip=chip, mode=mode, nodes=len(rr),
                               totalJ=sum(x for x, _ in e), maxJ=max(x for x, _ in e),
                               framesTx=sum(int(r["framesTx"]) for r in rr),
                               framesRx=sum(int(r["framesRx"]) for r in rr))
                    for ro in ROLES:
                        rec[f"max_{ro}J"] = max([x for x, o in e if o == ro], default=0.0)
                    out.append(rec)
    if a.out:
        with open(a.out, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    # summary over the clusters: sum of totals and frames, max of the per-node maxima
    agg = defaultdict(lambda: defaultdict(float))
    for r in out:
        g = agg[(r["scheme"], r["chip"], r["mode"])]
        for x in ("totalJ", "framesTx", "framesRx"): g[x] += r[x]
        for x in ["maxJ"] + [f"max_{ro}J" for ro in ROLES]: g[x] = max(g[x], r[x])
        g["clusters"] += 1
    print("scheme chip      mode  clusters totalJ  maxJ  " + " ".join(f"{ro:>6}" for ro in ROLES) + "  framesTx framesRx")
    for (s, c, m), g in sorted(agg.items()):
        print(f"{s:6} {c:9} {m:5} {g['clusters']:8.0f} {g['totalJ']:7.1f} {g['maxJ']:5.2f} "
              + " ".join(f"{g[f'max_{ro}J']:6.2f}" for ro in ROLES) + f"  {g['framesTx']:8.0f} {g['framesRx']:8.0f}")


def p_uav(v, a_par, a_perp):
    """Zeng & Zhang's power for speed v, along-track a_par and normal a_perp: |a|^2 - (a.v)^2/v^2 = a_perp^2."""
    return C1 * v ** 3 + C2 / v * (1 + a_perp ** 2 / G ** 2)


def uav(a):
    import numpy as np
    from kin_time import VMIN, curvature, run
    _, o = run(a.work, a.kind)
    r = o[45]
    tc, P, _ = r["track"]
    dt = np.diff(tc)
    ds = np.linalg.norm(np.diff(P, axis=0), axis=1)
    v = ds / dt                                                   # each STEP segment's mean speed
    vm = np.r_[v[0], (v[:-1] + v[1:]) / 2, v[-1]]                 # at the points
    a_par = np.gradient(vm, np.r_[0, np.cumsum(dt)])[:-1]
    kap = (curvature(P)[:-1] + curvature(P)[1:]) / 2
    a_perp = v ** 2 * kap
    e_acc = float(np.sum(p_uav(v, a_par, a_perp) * dt))
    e_lvl = float(np.sum(p_uav(v, 0, 0) * dt))                    # same profile, the level steady-flight power only
    e_fix = 0.0                                                   # delivery fixes: extra seconds at VMIN
    for k, how in r["how"].items():
        need = math.ceil(400 * 1000 / 99) * 0.01
        extra = max(0.0, need - r["over"].get(k, 0.0))
        e_fix += extra * p_uav(VMIN, 0, G if how == "circle" else 0)   # circling at VMIN, 45 deg bank: 1 g
    dk = M_UAV / 2 * (vm[-1] ** 2 - vm[0] ** 2)
    print(f"{a.work}:{a.kind}  bank 45: {tc[-1]:.0f} s + fixes {r['fix']:.0f} s, {ds.sum() / 1000:.1f} km")
    print(f"  energy {(e_acc + e_fix + dk) / 1e3:.1f} kJ (level-flight power only {e_lvl / 1e3:.1f} kJ, "
          f"acceleration term +{(e_acc - e_lvl) / 1e3:.1f} kJ, fixes {e_fix / 1e3:.1f} kJ, dK {dk / 1e3:.2f} kJ)")
    print(f"  P(50 m/s) {p_uav(50, 0, 0):.0f} W, P(25) {p_uav(25, 0, 0):.0f} W, P(25, 1 g turn) "
          f"{p_uav(25, 0, G):.0f} W; max normal acceleration {a_perp.max() / G:.2f} g; "
          f"25 m/s on 63.7 m: {25 ** 2 / 63.7 / G:.2f} g")


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    r = sp.add_parser("radio"); r.add_argument("results"); r.add_argument("plans"); r.add_argument("--out", default="")
    u = sp.add_parser("uav"); u.add_argument("work"); u.add_argument("kind", nargs="?", default="kin")
    a = ap.parse_args()
    radio(a) if a.cmd == "radio" else uav(a)


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
