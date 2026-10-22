"""The whole Phase-1 mission on one generated map (CLAUDE.md §8 item 68), with the layer-3 River at its core.

    python3 tools/mission.py --clusters 4 --seed 4 --work WORK --bin BIN [--jobs 3]

Stages (each writes into WORK; a stage whose outputs exist is skipped, so a run can be resumed):
  1 map       map_gen domain with lakes, grown to 80 x CLUSTERS cells, nodes one per 35 m x 35 m;
              partition.py into clusters of at most 80 cells (or, --partition=lane, restructure.py lanes
              --lane cells wide; each cluster then flies along the lanes first); the BS 1 km below the
              domain's lowest cell
  2 deploy    per cluster: uav-coop-deploy (given region and nodes) picks the CH and CLs (the CH at least
              300 m from the cluster's edge; 200, 100, 0 m for a cluster too thin for that); the bearing
              through the CH with the longest in-cluster flight (0-178 deg, step 2) is chosen and the
              cluster deployed again flying straight across the CH along it (routes, gateways, path);
              where the Dubins lead-in/out cannot stay outside the cluster, the next-longest bearing
  3 tour      team 1 (one fixed-wing UAV, 50 m/s): BS -> every cluster's straight segment, either way
              round -> BS, the shortest such tour (Held-Karp over segments x direction); transits
              straight (no turn radius). Each cluster's pass starts when the UAV reaches its entry
  4 pass      uav-coop-pass, mission 1, per cluster (only that cluster's nodes listen)
  5 river     river_export.py plan, then uav-coop2-river per cluster for SCHEMES (River prepared,
              River adaptive Circle of 12, direct pull); the cluster starts when the UAV leaves it
  6 analyse   (mission_report.py) matching, suspects, team 2
BIN holds deploy-bin, pass-bin (+ pass-lib/), river-bin (+ lib/).
"""
import argparse, csv, json, math, os, random, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

from map_gen import add_args, cell_at, centre, generate
from partition import partition
from restructure import lane_partition
from subch import subch_partition
from tour_heur import order_segments

HERE = os.path.dirname(os.path.abspath(__file__))
COOP2 = os.path.join(HERE, "../../uav-coop2/tools")
V1 = 50.0   # team 1 speed, m/s (the pass: one packet per 0.5 m every 10 ms)
SCHEMES = {"rf": ["--scheme=river", "--prep=full"],
           "ad12": ["--scheme=river", "--prep=adaptive", "--circleMin=12", "--circleMax=12"],
           "d": ["--scheme=direct"]}


def sh(cmd, log, env=None, ok=False):
    with open(log, "w") as f:
        r = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, env=env)
    if r.returncode and not ok:
        sys.exit(f"failed ({r.returncode}): {' '.join(cmd)}; see {log}")
    return r.returncode == 0


def stage_map(a, W_):
    if os.path.exists(f"{W_}/clusters.csv"):
        return
    p = argparse.ArgumentParser()
    add_args(p)
    g_args = p.parse_args([])
    g_args.seed, g_args.cells, g_args.lakes, g_args.lakeCells = a.seed, 80 * a.clusters, a.clusters, 10
    g = generate(g_args, random.Random(a.seed))
    gaps = {h: "lake" for h in g["lake_set"]} | {h: "river" for h in g["river"]}
    land = set(g["domain"])
    with open(f"{W_}/domain-cells.csv", "w") as f:
        f.write("q,r,cx,cy,type\n")
        for h in g["final"]:
            f.write(f"{h[0]},{h[1]},{centre(h)[0]:.3f},{centre(h)[1]:.3f},{gaps.get(h, 'land')}\n")
    if a.partition == "lane":
        owner, th, _, st = lane_partition(land, 80, a.lane)
        med, over = sorted(set(owner.values())), 0
        json.dump(dict(bearing=round(math.degrees(th)), lane=a.lane), open(f"{W_}/lane.json", "w"))
    elif a.partition == "subch":   # baseline (item 114): the k-medoids clusters of --src split around critical cells
        owner, seeds = subch_partition(a.src, a.dmin, a.minsize, pairs=getattr(a, "pairs", False))
        assert set(owner) == land, "the subCH partition must cover the same land cells"
        med, over = sorted(set(owner.values())), 0
        json.dump(dict(src=a.src, dmin=a.dmin, minsize=a.minsize,
                       seeds={k: v for k, v in seeds.items()}), open(f"{W_}/subch.json", "w"))
    else:
        count = getattr(a, "count", 0)   # subCH-K's source (item 118): exactly COUNT clusters, the cap raised to fit
        owner, med, it, over = partition(land, math.ceil(len(land) / count) if count else 80, random.Random(a.seed))
        assert not count or len(med) == count, f"k-medoids gave {len(med)} clusters, not {count}"
    nodes = [v for v in g["nodes"] if (v[3], v[4]) in owner]
    with open(f"{W_}/clusters.csv", "w") as f:
        f.write("q,r,cluster\n")
        for h in sorted(owner):
            f.write(f"{h[0]},{h[1]},{owner[h] + 1}\n")
    for k in sorted(set(owner.values())):
        with open(f"{W_}/c{k + 1}-cells.csv", "w") as f:
            f.write("q,r\n" + "".join(f"{q},{r}\n" for (q, r), c in sorted(owner.items()) if c == k))
        with open(f"{W_}/c{k + 1}-nodesin.csv", "w") as f:
            f.write("x,y,q,r,obs,cpu,comm\n")
            for v in nodes:
                if owner[(v[3], v[4])] == k:
                    f.write(f"{v[1]:.3f},{v[2]:.3f},{v[3]},{v[4]},{v[5]:.6g},{v[6]:.6g},{v[7]:.6g}\n")
    ys = [centre(h)[1] for h in land]
    xs = [centre(h)[0] for h in land]
    bs = ((min(xs) + max(xs)) / 2, min(ys) - 1000.0)
    json.dump(dict(clusters=len(med), cells=len(land), nodes=len(nodes), bs=bs, over=over),
              open(f"{W_}/map.json", "w"))
    print(f"map: {len(land)} land cells, {len(nodes)} nodes, {len(med)} clusters "
          f"{[sum(1 for c in owner.values() if c == i) for i in range(len(med))]}, BS {bs[0]:.0f},{bs[1]:.0f}")


def bearings(W_, k):
    """Bearings through the CH, the longest in-cluster flight first."""
    cells = {(int(r["q"]), int(r["r"])) for r in csv.DictReader(open(f"{W_}/c{k}-cells.csv"))}
    ch = next(r for r in csv.DictReader(open(f"{W_}/c{k}-nodes-s35.csv")) if r["isCH"] == "1")
    cx, cy = float(ch["x"]), float(ch["y"])
    out = []
    for b in range(0, 180, 2):
        th = math.radians(b)
        far = [max([s for s in range(0, 8000, 5)
                    if cell_at(cx + sg * s * math.cos(th), cy + sg * s * math.sin(th)) in cells] or [0])
               for sg in (1, -1)]
        inside = sum(5 for s in range(-far[1], far[0], 5)
                     if cell_at(cx + s * math.cos(th), cy + s * math.sin(th)) in cells)
        out.append((b, inside))
    return sorted(out, key=lambda t: -t[1])


def stage_deploy(a, W_, K):
    out = {}
    for k in range(1, K + 1):
        if not os.path.exists(f"{W_}/c{k}-path-s35.csv"):
            base = [f"{a.bin}/deploy-bin", f"--regionIn=c{k}-cells.csv", f"--nodesIn=c{k}-nodesin.csv",
                    "--spacings=35", "--angle=180", f"--out=c{k}"]
            env = dict(os.environ, LD_LIBRARY_PATH=f"{a.bin}/lib")
            # a random entry only to get the roles: try other entries if a path from it is infeasible
            margins = (0, 100, 200, 300) if a.partition == "subch" else (300, 200, 100, 0)   # subCH: the strongest node
            margin = next(m for m in margins for p in range(10)
                          if sh(base + [f"--chMargin={m}", f"--pick={p}"], f"c{k}-deploy0.log", env, ok=True))
            base.append(f"--chMargin={margin}")
            scan = bearings(W_, k)
            if os.path.exists(f"{W_}/lane.json"):   # lane clusters: fly along the lanes first
                th = json.load(open(f"{W_}/lane.json"))["bearing"]
                scan = sorted(scan, key=lambda t: t[0] != th)
            b, inside = next((b, i) for b, i in scan
                             if sh(base + [f"--bearing={b}"], f"c{k}-deploy.log", env, ok=True))
            json.dump(dict(bearing=b, inside=inside, chMargin=margin), open(f"{W_}/c{k}-bearing.json", "w"))
        out[k] = json.load(open(f"{W_}/c{k}-bearing.json"))
    return out


def stage_tour(a, W_, K):
    if os.path.exists(f"{W_}/tour.json"):
        return json.load(open(f"{W_}/tour.json"))
    bs = tuple(json.load(open(f"{W_}/map.json"))["bs"])
    seg = {}
    for k in range(1, K + 1):
        p = [(float(r["x"]), float(r["y"])) for r in csv.DictReader(open(f"{W_}/c{k}-path-s35.csv"))]
        L = sum(math.dist(u, v) for u, v in zip(p, p[1:]))
        seg[k] = (p[0], p[-1], L)
    ks = list(range(1, K + 1))
    end = lambda k, d: seg[k][1] if d == 0 else seg[k][0]     # d = 0: fly entry -> exit
    start = lambda k, d: seg[k][0] if d == 0 else seg[k][1]
    if K > 13:   # too many segments for Held-Karp (tour_heur)
        return write_tour(W_, bs, seg, order_segments(bs, seg))
    best = {}   # Held-Karp: (visited mask, last cluster, its direction) -> (transit metres, previous state)
    for i, k in enumerate(ks):
        for d in (0, 1):
            best[(1 << i, i, d)] = (math.dist(bs, start(k, d)), None)
    for mask in range(1, 1 << K):
        for i in range(K):
            for d in (0, 1):
                if (mask, i, d) not in best:
                    continue
                c0 = best[(mask, i, d)][0]
                for j in range(K):
                    if mask >> j & 1:
                        continue
                    for e in (0, 1):
                        c = c0 + math.dist(end(ks[i], d), start(ks[j], e))
                        key = (mask | 1 << j, j, e)
                        if key not in best or c < best[key][0]:
                            best[key] = (c, (mask, i, d))
    full = (1 << K) - 1
    last = min(((full, i, d) for i in range(K) for d in (0, 1)),
               key=lambda s: best[s][0] + math.dist(end(ks[s[1]], s[2]), bs))
    order, s = [], last
    while s:
        order.append((ks[s[1]], s[2]))
        s = best[s][1]
    order.reverse()
    return write_tour(W_, bs, seg, order)


def write_tour(W_, bs, seg, order):
    end = lambda k, d: seg[k][1] if d == 0 else seg[k][0]
    start = lambda k, d: seg[k][0] if d == 0 else seg[k][1]
    t, pos, legs = 0.0, bs, []
    for k, d in order:
        t += math.dist(pos, start(k, d)) / V1
        t0 = t
        t += seg[k][2] / V1
        legs.append(dict(cluster=k, reversed=d, enter=t0, leave=t, start=start(k, d), end=end(k, d)))
        pos = end(k, d)
    t += math.dist(pos, bs) / V1
    tour = dict(legs=legs, back=t, length=t * V1, inside=sum(v[2] for v in seg.values()))
    json.dump(tour, open(f"{W_}/tour.json", "w"), indent=1)
    print(f"tour: {tour['length'] / 1000:.1f} km, {t:.0f} s, order {[(l['cluster'], l['reversed']) for l in legs]}")
    return tour


def deploy_links(W_, k):
    """d{k}/ in the layout river_export.py and river_plan.load expect."""
    os.makedirs(f"{W_}/d{k}", exist_ok=True)
    for src, dst in ((f"c{k}-lattice.csv", "deploy-lattice.csv"), (f"c{k}-nodes-s35.csv", "deploy-nodes-s35.csv")):
        if not os.path.exists(f"{W_}/d{k}/{dst}"):
            os.symlink(f"../{src}", f"{W_}/d{k}/{dst}")


def domain_scores(W_, K):
    """domain-cl.csv: every cell's strongest node over all clusters (river_plan.load_around; item 135)."""
    best = {}
    for k in range(1, K + 1):
        for x in csv.DictReader(open(f"{W_}/c{k}-nodes-s35.csv")):
            h = (int(x["q"]), int(x["r"]))
            best[h] = max(best.get(h, -1.0), float(x["score"]))
    with open(f"{W_}/domain-cl.csv", "w") as f:
        f.write("q,r,score\n" + "".join(f"{q},{r},{v:.6g}\n" for (q, r), v in sorted(best.items())))


def stage_runs(a, W_, K):
    if getattr(a, "critRing", "cluster") == "domain" and not os.path.exists(f"{W_}/domain-cl.csv"):
        domain_scores(W_, K)
    passenv = dict(os.environ, LD_LIBRARY_PATH=f"{a.bin}/pass-lib")
    rivenv = dict(os.environ, LD_LIBRARY_PATH=f"{a.bin}/lib")

    def one(k):
        if not os.path.exists(f"{W_}/pass{k}-bits-r1.bin"):
            sh([f"{a.bin}/pass-bin", f"--nodes=c{k}-nodes-s35.csv", f"--path=c{k}-path-s35.csv", "--firstRun=1",
                "--runs=1", "--bits", f"--out=pass{k}"], f"pass{k}.log", passenv)
        if not os.path.exists(f"{W_}/plan{k}.txt"):
            deploy_links(W_, k)
            sh([sys.executable, f"{COOP2}/river_export.py", f"--deploy=d{k}", f"--path=c{k}-path-s35.csv",
                f"--banks={getattr(a, 'banks', 'parallel')}", *(["--reentry"] if getattr(a, "reentry", False) else []),
                *([f"--windowKB={a.windowKB:g}"] if getattr(a, "windowKB", 0) else []),
                *([f"--windowAt={a.windowAt}"] if getattr(a, "windowAt", "ch") != "ch" else []),
                *(["--around=domain-cl.csv"] if os.path.exists(f"{W_}/domain-cl.csv") else []),
                f"--out=plan{k}.txt"], f"plan{k}.log")
        return k

    def river(job):
        k, tag = job
        if not os.path.exists(f"{W_}/r{k}-{tag}-runs.csv") or len(open(f"{W_}/r{k}-{tag}-runs.csv").readlines()) < 2:
            sh([f"{a.bin}/river-bin", f"--nodes=c{k}-nodes-s35.csv", f"--routes=c{k}-routes-s35.csv",
                f"--gateways=c{k}-gateways-s35.csv", f"--plan=plan{k}.txt", f"--bits=pass{k}-bits", "--firstRun=1",
                "--runs=1", "--limit=900", "--gwSelect=quality", "--colours=7", *SCHEMES[tag], f"--out=r{k}-{tag}"],
               f"r{k}-{tag}.log", rivenv)
        print("  " + open(f"r{k}-{tag}.log").read().strip().splitlines()[-1] if os.path.exists(f"r{k}-{tag}.log")
              else f"  r{k}-{tag} done before", flush=True)

    with ThreadPoolExecutor(a.jobs) as ex:
        list(ex.map(one, range(1, K + 1)))
        list(ex.map(river, [(k, t) for k in range(1, K + 1) for t in a.schemes.split(",")]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clusters", type=int, required=True, help="map size: 80 x CLUSTERS cells grown")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--work", required=True)
    ap.add_argument("--bin", required=True)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--schemes", default=",".join(SCHEMES), help="tags of SCHEMES to run")
    ap.add_argument("--partition", default="kmedoids", choices=("kmedoids", "lane", "subch"),
                    help="phase 0: partition.py k-medoids, or restructure.py lanes (CLAUDE.md §8 item 84), or the "
                         "k-medoids clusters of --src split around critical cells far apart (subch.py, item 114)")
    ap.add_argument("--src", default="", help="--partition=subch: the k-medoids work folder of the same map")
    ap.add_argument("--dmin", type=float, default=6, help="--partition=subch: seeds at least this many cells apart")
    ap.add_argument("--minsize", type=int, default=20, help="--partition=subch: smaller sub-clusters are merged")
    ap.add_argument("--pairs", action="store_true", help="--partition=subch: subCH-K (item 118), every --src cluster "
                    "split into exactly two of equal size around its two critical cells farthest apart")
    ap.add_argument("--count", type=int, default=0, help="k-medoids: exactly this many clusters (subCH-K's source)")
    ap.add_argument("--geometry", action="store_true", help="stop after the tour (no ns-3 pass or River)")
    ap.add_argument("--lane", type=float, default=4.5, help="--partition=lane: lane width, cells")
    ap.add_argument("--banks", default="parallel", choices=("parallel", "local"),
                    help="River Banks: the sum vector's normal, or the path's local normal (CLAUDE.md §8 item 103)")
    ap.add_argument("--windowKB", type=float, default=0,
                    help="each cluster needs only this much of D, around the CH (river_export.py; item 106)")
    ap.add_argument("--critRing", default="cluster", choices=("cluster", "domain"),
                    help="critical cells' local test over the cluster's cells, or the real neighbourhood (item 135)")
    ap.add_argument("--windowAt", default="ch", choices=("ch", "crit"),
                    help="the window around the CH, or one around each critical cell (river_export.py; item 120)")
    a = ap.parse_args()
    a.bin = os.path.abspath(a.bin)
    a.src = os.path.abspath(a.src) if a.src else ""
    os.makedirs(a.work, exist_ok=True)
    W_ = os.path.abspath(a.work)
    os.chdir(W_)
    stage_map(a, W_)
    K = json.load(open("map.json"))["clusters"]
    b = stage_deploy(a, W_, K)
    print("bearings: " + ", ".join(f"C{k} {v['bearing']} deg ({v['inside']} m inside)" for k, v in b.items()))
    stage_tour(a, W_, K)
    if a.geometry:
        for k in range(1, K + 1):
            deploy_links(W_, k)
        return
    stage_runs(a, W_, K)


if __name__ == "__main__":
    main()
