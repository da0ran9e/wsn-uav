"""Saturation of the proposed scheme (CLAUDE.md §8 item 120): one strip-shaped cluster, WIDTH cells across and
LENGTH km long, flown along its length through the CH, then the River (window of the clue set around the CH).
Sweeping WIDTH and LENGTH sweeps the cluster's size, cell count, cross-width and length.

    python3 tools/sat_strip.py --width 6 --length 2 --seed 1 --work WORK --bin BIN      # one strip
    python3 tools/sat_strip.py --summary "WORK/*" --out OUT.csv                        # one row per strip

Stages, each skipped when its outputs exist (mission.py does the deploy, the pass and the River):
  1 strip   cells whose centre lies within WIDTH x 173 m / 2 of the x axis and between 0 and LENGTH km on it;
            nodes one per 35 m x 35 m, uniform, obs, cpu ~ U[0,1), comm ~ U(0,1] (as map_gen)
  2 deploy  mission.stage_deploy: CH (300 m from the edge, less for a thin strip), CLs, critical cells, routes,
            gateways; the flight crosses the CH along the strip (bearing 0, via lane.json as for lane clusters;
            the longest bearing would cut the strip on a diagonal)
  3 runs    mission.stage_runs: uav-coop-pass, then River, prepared Circle (rf; --schemes rf,d adds the direct
            pull), the River window --windowKB (400 kB: the clue set) around the CH
"""
import argparse, csv, glob, json, math, os, random, statistics as st, sys
from types import SimpleNamespace

from map_gen import AREA, R, W, cell_at, centre
import mission


def stage_strip(a, W_):
    if os.path.exists(f"{W_}/c1-nodesin.csv"):
        return
    half, L = a.width * W / 2, a.length * 1000.0
    rows = math.ceil(half / (1.5 * R)) + 1
    cells = sorted({(q, r) for r in range(-rows, rows + 1) for q in range(-rows - 2, int(L / W) + rows + 3)
                    if abs(centre((q, r))[1]) <= half and 0 <= centre((q, r))[0] <= L})
    rng = random.Random(a.seed)
    nodes = []
    for _ in range(round(len(cells) * AREA / 35.0 ** 2)):
        h = rng.choice(cells)
        cx, cy = centre(h)
        while True:
            x, y = cx + rng.uniform(-W / 2, W / 2), cy + rng.uniform(-R, R)
            if cell_at(x, y) == h:
                break
        nodes.append((x, y, h[0], h[1], rng.random(), rng.random(), 1 - rng.random()))
    with open(f"{W_}/c1-cells.csv", "w") as f:
        f.write("q,r\n" + "".join(f"{q},{r}\n" for q, r in cells))
    with open(f"{W_}/c1-nodesin.csv", "w") as f:
        f.write("x,y,q,r,obs,cpu,comm\n")
        f.writelines(f"{x:.3f},{y:.3f},{q},{r},{o:.6g},{c:.6g},{m:.6g}\n" for x, y, q, r, o, c, m in nodes)
    json.dump(dict(width=a.width, length=a.length, seed=a.seed, cells=len(cells), nodes=len(nodes)),
              open(f"{W_}/strip.json", "w"))
    json.dump(dict(bearing=0), open(f"{W_}/lane.json", "w"))
    print(f"strip {a.width:g} cells x {a.length:g} km: {len(cells)} cells, {len(nodes)} nodes")


def summarise(W_):
    """One row: the strip, its roles and flight, and what the River did for each scheme."""
    s = json.load(open(f"{W_}/strip.json"))
    b = json.load(open(f"{W_}/c1-bearing.json"))
    pr = next(csv.DictReader(open(f"{W_}/pass1-runs.csv"))) if os.path.exists(f"{W_}/pass1-runs.csv") else {}
    row = dict(width=s["width"], length=s["length"], seed=s["seed"], cells=s["cells"], nodes=s["nodes"],
               bearing=b["bearing"], inside=b["inside"], chMargin=b["chMargin"])
    for tag in ("rf", "d"):
        f = f"{W_}/r1-{tag}-runs.csv"
        if not os.path.exists(f) or len(open(f).readlines()) < 2:
            continue
        run = next(csv.DictReader(open(f)))
        crit = list(csv.DictReader(open(f"{W_}/r1-{tag}-crit.csv")))
        done = [float(c["doneS"]) for c in crit]
        row.update({f"{tag}_crit": len(crit), f"{tag}_D": int(run["D"]),
                    f"{tag}_doneMean": round(st.mean(done), 2), f"{tag}_doneMax": round(max(done), 2),
                    f"{tag}_gatherMax": round(max(float(c["gatherDoneS"]) for c in crit), 2),
                    f"{tag}_missing": sum(int(c["missing"]) for c in crit),
                    f"{tag}_hops": int(run["hops"]), f"{tag}_macFail": int(run["macFail"]),
                    f"{tag}_wallS": float(run["wallS"])})
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--width", type=float, help="cells across (x 173 m)")
    ap.add_argument("--length", type=float, help="km along the flight")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--work")
    ap.add_argument("--bin")
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--schemes", default="rf")
    ap.add_argument("--windowKB", type=float, default=400)
    ap.add_argument("--summary", help="glob of strip work folders: write one row per folder to --out")
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.summary:
        rows = [summarise(w) for w in sorted(glob.glob(a.summary)) if os.path.exists(f"{w}/c1-bearing.json")]
        keys = list(dict.fromkeys(k for r in rows for k in r))
        with open(a.out, "w", newline="") as f:
            w = csv.DictWriter(f, keys)
            w.writeheader()
            w.writerows(rows)
        print(f"{len(rows)} strips -> {a.out}")
        return
    os.makedirs(a.work, exist_ok=True)
    W_, a.bin = os.path.abspath(a.work), os.path.abspath(a.bin)
    os.chdir(W_)
    stage_strip(a, W_)
    m = SimpleNamespace(bin=a.bin, partition="kmedoids", jobs=a.jobs, schemes=a.schemes,
                        banks="parallel", reentry=False, windowKB=a.windowKB)
    b = mission.stage_deploy(m, W_, 1)[1]
    print(f"bearing {b['bearing']} deg, {b['inside']} m inside, CH margin {b['chMargin']} m", flush=True)
    mission.stage_runs(m, W_, 1)
    print(json.dumps(summarise(W_)))


if __name__ == "__main__":
    main()
