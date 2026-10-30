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
  4 pass      uav-coop-pass, mission 1 (--mapRuns: one per map and cluster), per cluster (only that cluster's
              nodes listen)
  5 river     river_export.py plan, then uav-coop2-river per cluster for SCHEMES (River prepared,
              River adaptive Circle of 12, direct pull); the cluster starts when the UAV leaves it
  6 analyse   (mission_report.py) matching, suspects, team 2
BIN holds deploy-bin, pass-bin (+ pass-lib/), river-bin (+ lib/).
"""
import argparse, csv, json, math, os, random, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

from map_gen import cell_at, centre
from partition import partition
from restructure import bs_point, domain, lane_partition
from subch import subch_partition
from river_plan import hexdist, load, load_around, plan  # noqa: E402 (subch puts uav-coop2/tools on the path)
from tour_heur import order_segments
from chord_tour import choose

HERE = os.path.dirname(os.path.abspath(__file__))
COOP2 = os.path.join(HERE, "../../uav-coop2/tools")
V1 = 50.0   # team 1 speed, m/s (the pass: one packet per 0.5 m every 10 ms)
# Item 163: the pass's excess A2G loss per environment, dB, and so its R50 (where a packet gets through with
# probability 1/2) measured on the ns-3 pass (tools/a2g_env.py): 1015 / 498 / 199 / 99 m.
ENV_LOSS = {"open": 0.0, "r500": 9.03, "r200": 19.77, "r100": 25.74}
SCHEMES = {"rf": ["--scheme=river", "--prep=full"],
           "ad12": ["--scheme=river", "--prep=adaptive", "--circleMin=12", "--circleMax=12"],
           "d": ["--scheme=direct"],
           "t": ["--scheme=trickle"],   # baseline (item 139); needs a river-bin built with it
           "tp": ["--scheme=trickle", "--tScope=paths"]}   # Trickle on the direct-pull path cells only (reviewer)


def runseed(w):
    """The work folder's simulation seed (--runSeed; item 188): 1 unless runseed.txt says otherwise."""
    return int(open(f"{w}/runseed.txt").read()) if os.path.exists(f"{w}/runseed.txt") else 1


def sh(cmd, log, env=None, ok=False):
    with open(log, "w") as f:
        r = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, env=env)
    if r.returncode and not ok:
        sys.exit(f"failed ({r.returncode}): {' '.join(cmd)}; see {log}")
    return r.returncode == 0


def stage_map(a, W_):
    if os.path.exists(f"{W_}/clusters.csv"):
        return
    g = domain(a.clusters, a.seed, getattr(a, "shape", ""))
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
    bs = bs_point(land, getattr(a, "bs", "south"))
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
            margins = (0, 100, 200, 300) if a.partition == "subch" or getattr(a, "chAnywhere", False) \
                else (300, 200, 100, 0)   # subCH, --chAnywhere (item 154): the strongest node wherever it is
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


def fit_path(rows, S, crit, target, need):
    """--chordFit (item 159): a straight path (rows of its CSV) cut to the shortest stretch through the CH that flies
    target metres over the cluster's own cells S, the closest to the critical cells (points crit) among the
    shortest (within 20 m of it), with straight leads of RHO beyond its ends; the whole line when it is shorter.
    Returns dict(C core vertices, i the CH's index, L metres with the leads, own metres over S, poses both ways,
    fix seconds the delivery still lacks at 50 m/s for need metres, axe the own cells under the core)."""
    import numpy as np
    from swath import RHO, cells_at
    core = [r for r in rows if r["part"] in ("1", "2")]
    xy = [(float(r["x"]), float(r["y"])) for r in core]
    keep = [i for i in range(len(xy)) if i == 0 or xy[i] != xy[i - 1]]
    X = np.array([xy[i] for i in keep])
    ich = next(j for j, i in enumerate(keep) if core[i]["part"] == "2")   # part 2 starts at the CH
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(X, axis=0), axis=1))]
    on = np.array([tuple(h) in S for h in cells_at(X)])
    own = np.r_[0, np.cumsum(np.diff(s) * on[1:])]
    i0, i1 = 0, len(X) - 1
    if own[-1] > target:
        wins = []
        for i in range(ich + 1):
            j = int(np.searchsorted(own, own[i] + target))
            if j < len(X):
                wins.append((s[max(j, ich)] - s[i], i, max(j, ich)))
        best = min(w[0] for w in wins)
        cp = np.array(crit) if len(crit) else np.empty((0, 2))
        dist = lambda i, j: float(np.mean([np.min(np.linalg.norm(X[i:j + 1] - c, axis=1)) for c in cp])) if len(cp) else 0.0
        _, i0, i1 = min((dist(i, j), i, j) for L, i, j in wins if L <= best + 20)
    C = X[i0:i1 + 1]
    t0, t1 = C[min(3, len(C) - 1)] - C[0], C[-1] - C[max(len(C) - 4, 0)]
    t0, t1 = t0 / np.linalg.norm(t0), t1 / np.linalg.norm(t1)
    a0, a1 = C[0] - RHO * t0, C[-1] + RHO * t1
    h0, h1 = math.atan2(t0[1], t0[0]), math.atan2(t1[1], t1[0])
    got = float(own[i1] - own[i0])
    return dict(C=C, i=ich - i0, L=float(s[i1] - s[i0]) + 2 * RHO, own=got, fix=max(0.0, (need - got) / V1),
                poses=[((*a0, h0), (*a1, h1)), ((*a1, h1 + math.pi), (*a0, h0 + math.pi))],
                axe={tuple(h) for h in cells_at(C)} & S)


def stage_chord(a, W_, K):
    """--chordTour FRAC,CLUE (CHORD-T, item 136; CLUE of the --windowKB clue set, item 149): the bearings of all
    clusters re-chosen jointly with team 1's tour
    (chord_tour.choose); every candidate deployed for real (its Dubins lead-in / lead-out must be feasible) into
    cand/, the chosen ones copied over the cluster's deploy files."""
    if os.path.exists(f"{W_}/chord.json"):
        return
    frac, clue = (float(x) for x in a.chordTour.split(","))
    env = dict(os.environ, LD_LIBRARY_PATH=f"{a.bin}/lib")
    os.makedirs(f"{W_}/cand", exist_ok=True)
    if getattr(a, "critRing", "cluster") == "domain" and not os.path.exists(f"{W_}/domain-cl.csv"):
        domain_scores(W_, K)
    around = load_around(f"{W_}/domain-cl.csv") if os.path.exists(f"{W_}/domain-cl.csv") else None
    cands, n, files, fits = {}, {}, {}, {}
    need = math.ceil((a.windowKB or 400) * 1000 / 99) * 0.5   # one copy of the clue set at 50 m/s, metres
    for k in range(1, K + 1):
        deploy_links(W_, k)
        geo = load(f"{W_}/d{k}", f"{W_}/c{k}-path-s35.csv")
        crit = plan(geo, reentry=True, domain_sc=around)["crit"]
        n[k] = len(crit)
        bj = json.load(open(f"{W_}/c{k}-bearing.json"))
        scan = bearings(W_, k)
        top = scan[0][1]
        pick = [(bj["bearing"], bj["inside"])]
        for b, ins in scan:
            if ins >= frac * top and ins >= clue * math.ceil((a.windowKB or 400) * 1000 / 99) * 0.5 and \
                    all(min(abs(b - p), 180 - abs(b - p)) >= 10 for p, _ in pick) and len(pick) < 6:
                pick.append((b, ins))
        cands[k], files[k] = [], []
        for b, ins in pick:
            pre = f"c{k}" if b == bj["bearing"] else f"cand/c{k}b{b}"
            if pre != f"c{k}" and not sh([f"{a.bin}/deploy-bin", f"--regionIn=c{k}-cells.csv", f"--nodesIn=c{k}-nodesin.csv",
                                          "--spacings=35", "--angle=180", f"--chMargin={bj['chMargin']}", f"--bearing={b}",
                                          f"--out={pre}"], f"{pre}-deploy.log", env, ok=True):
                continue
            p = list(csv.DictReader(open(f"{W_}/{pre}-path-s35.csv")))
            if getattr(a, "chordFit", 0):   # item 159: the line cut to just enough, its delivery shortfall in its time
                f = fit_path(p, geo["S"], [geo["c"][h] for h in crit], a.chordFit * need, need)
                tail = max(0.0, -12.0 + 0.101 * len(geo["S"]) + 5.7 * max(
                    [min(hexdist(h, x) for x in f["axe"]) for h in crit] or [0])) if f["axe"] else 0.0
                cands[k].append(dict(L=f["L"], fix=f["fix"], tail=tail, poses=f["poses"]))
                fits[(k, pre)] = f
                files[k].append((b, ins, pre))
                continue
            xy = [(float(r["x"]), float(r["y"])) for r in p]
            h0, h1 = math.radians(float(p[0]["thDeg"])), math.radians(float(p[-1]["thDeg"]))
            cands[k].append(dict(L=sum(math.dist(u, v) for u, v in zip(xy, xy[1:])),
                                 poses=[((*xy[0], h0), (*xy[-1], h1)), ((*xy[-1], h1 + math.pi), (*xy[0], h0 + math.pi))]))
            files[k].append((b, ins, pre))
    picks, order = choose(tuple(json.load(open(f"{W_}/map.json"))["bs"]), cands, n, getattr(a, "riverTour", 0.0))
    for k, c in picks.items():
        b, ins, pre = files[k][c]
        if fits:   # the chosen line cut to just enough (meander_lane.write_path), the whole one kept
            from meander_lane import write_path
            f = fits[(k, pre)]
            write_path(f"{W_}/{pre}-path-fit.csv", f["C"], f["i"])
            os.replace(f"{W_}/{pre}-path-s35.csv", f"{W_}/{pre}-path-full.csv")
            os.replace(f"{W_}/{pre}-path-fit.csv", f"{W_}/{pre}-path-s35.csv")
        if pre != f"c{k}":
            for f in os.listdir(W_):   # the old line's pass, plan and River results must not be reused
                if f.startswith((f"pass{k}-", f"plan{k}.", f"r{k}-")):
                    os.remove(f"{W_}/{f}")
            for f in os.listdir(f"{W_}/cand"):
                if f.startswith(f"c{k}b{b}-") and f.endswith(".csv"):
                    os.replace(f"{W_}/cand/{f}", f"{W_}/c{k}-{f[len(f'c{k}b{b}-'):]}")
            bj = json.load(open(f"{W_}/c{k}-bearing.json"))
            json.dump(dict(bj, bearing=b, inside=ins, longest=bj["bearing"]), open(f"{W_}/c{k}-bearing.json", "w"))
    if os.path.exists(f"{W_}/tour.json"):
        os.remove(f"{W_}/tour.json")
    json.dump(dict(frac=frac, clue=clue, fit=getattr(a, "chordFit", 0), riverTour=getattr(a, "riverTour", 0.0),
                   own={k: round(fits[(k, files[k][c][2])]["own"], 1) for k, c in picks.items()} if fits else {},
                   picks={k: files[k][c][0] for k, c in picks.items()},
                   candidates={k: [f[0] for f in files[k]] for k in files}), open(f"{W_}/chord.json", "w"))
    print("chord-t: " + ", ".join(f"C{k} {files[k][c][0]} deg" for k, c in sorted(picks.items())))


def stage_bend(a, W_, K):
    """--bendCrit CELLS (item 156): each cluster's chord bent lightly towards its critical cells that lie farther than
    the River half width OMEGA from it but within CELLS cells, by min(d - OMEGA, W) each, the CH pinned
    (meander_lane.bend_lane); the straight path kept as c{k}-path-chord.csv."""
    import numpy as np
    from map_gen import W
    from meander_lane import bend_lane, critical, write_path
    if not os.path.exists(f"{W_}/domain-cl.csv"):
        domain_scores(W_, K)
    around = load_around(f"{W_}/domain-cl.csv")
    for k in range(1, K + 1):
        if os.path.exists(f"{W_}/c{k}-path-chord.csv"):
            continue
        xy = [(float(r["x"]), float(r["y"])) for r in csv.DictReader(open(f"{W_}/c{k}-path-s35.csv"))
              if r["part"] in ("1", "2")]
        core = np.array([p for i, p in enumerate(xy) if i == 0 or p != xy[i - 1]])
        s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(core, axis=0), axis=1))]
        d = np.r_[np.arange(0, s[-1], 10.0), s[-1]]
        P = np.c_[np.interp(d, s, core[:, 0]), np.interp(d, s, core[:, 1])]
        nodes = list(csv.DictReader(open(f"{W_}/c{k}-nodes-s35.csv")))
        x = next(r for r in nodes if r["isCH"] == "1")
        ch = np.array([float(x["x"]), float(x["y"])])
        lat = {(int(r["q"]), int(r["r"])): np.array([float(r["cx"]), float(r["cy"])])
               for r in csv.DictReader(open(f"{W_}/c{k}-lattice.csv"))}
        pulls = [lat[h] for h in critical(nodes, around) if not np.allclose(lat[h], ch, atol=W)
                 and np.min(np.linalg.norm(P - lat[h], axis=1)) <= a.bendCrit * W]
        if getattr(a, "bendShort", False) and getattr(a, "chordFit", 0) and \
                json.load(open(f"{W_}/chord.json"))["own"].get(str(k), 0) >= math.ceil((a.windowKB or 400) * 1000 / 99) * 0.5:
            continue   # item 159: only a cluster short of one clue-set copy bends towards its critical cells
        Q, idx, _ = bend_lane(P, [ch], pulls)
        os.rename(f"{W_}/c{k}-path-s35.csv", f"{W_}/c{k}-path-chord.csv")
        write_path(f"{W_}/c{k}-path-s35.csv", Q, idx[0])
        print(f"C{k}: bent towards {len(pulls)} critical cells, shift <= {np.max(np.linalg.norm(Q - P, axis=1)):.0f} m")


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
    if getattr(a, "kinPass", False):   # item 157: every pass flies team 1's speed profile (pass_speed.py)
        import pass_speed
        if not all(os.path.exists(f"{W_}/c{k}-speed.json") for k in range(1, K + 1)):
            pass_speed.run(W_, K, getattr(a, "windowKB", 0) or 400)
    if getattr(a, "critRing", "cluster") == "domain" and not os.path.exists(f"{W_}/domain-cl.csv"):
        domain_scores(W_, K)
    env = getattr(a, "env", "open")
    if os.path.exists(f"{W_}/env.txt") and open(f"{W_}/env.txt").read().strip() != env:
        sys.exit(f"{W_} was flown with --env {open(f'{W_}/env.txt').read().strip()}, not {env}")
    if not os.path.exists(f"{W_}/env.txt"):   # written once: LM-Tour and DTSP-N + River runs read it via symlinks
        open(f"{W_}/env.txt", "w").write(env + "\n")
    rs = getattr(a, "runSeed", 1)
    ran = os.path.exists(f"{W_}/runseed.txt") or os.path.exists(f"{W_}/pass1-bits-r1.bin")   # flown before
    if ran and runseed(W_) != rs:
        sys.exit(f"{W_} was run with --runSeed {runseed(W_)}, not {rs}")
    if rs != 1 and not ran:
        open(f"{W_}/runseed.txt", "w").write(f"{rs}\n")
    po = dict(axeNear=True, lossDb=ENV_LOSS[env])
    if getattr(a, "axeNear", False) and (not os.path.exists(f"{W_}/plan-opts.json")
                                        or json.load(open(f"{W_}/plan-opts.json")) != po):
        json.dump(po, open(f"{W_}/plan-opts.json", "w"))   # read back by mission_report.load_map (River's plan)
    opts = json.load(open(f"{W_}/plan-opts.json")) if os.path.exists(f"{W_}/plan-opts.json") else {}
    passenv = dict(os.environ, LD_LIBRARY_PATH=f"{a.bin}/pass-lib")
    rivenv = dict(os.environ, LD_LIBRARY_PATH=f"{a.bin}/lib")

    def mission(k):   # item 161: the ns-3 mission index (pass fading, G2G shadowing and fades, MAC draws)
        return 100000 * a.clusters + 100 * a.seed + k + 10000000 * (rs - 1) if getattr(a, "mapRuns", False) else 1

    def one(k):
        if not os.path.exists(f"{W_}/pass{k}-bits-r1.bin"):
            sh([f"{a.bin}/pass-bin", f"--nodes=c{k}-nodes-s35.csv", f"--path=c{k}-path-s35.csv",
                f"--firstRun={mission(k)}", "--runs=1", "--bits", f"--out=pass{k}",
                *([f"--lossDb={ENV_LOSS[env]:g}"] if ENV_LOSS[env] else [])], f"pass{k}.log", passenv)
            if mission(k) != 1:   # the readers all take pass{k}-bits-r1.bin
                os.symlink(f"pass{k}-bits-r{mission(k)}.bin", f"{W_}/pass{k}-bits-r1.bin")
        if not os.path.exists(f"{W_}/plan{k}.txt"):
            deploy_links(W_, k)
            sh([sys.executable, f"{COOP2}/river_export.py", f"--deploy=d{k}", f"--path=c{k}-path-s35.csv",
                f"--banks={getattr(a, 'banks', 'parallel')}", *(["--reentry"] if getattr(a, "reentry", False) else []),
                *([f"--windowKB={a.windowKB:g}"] if getattr(a, "windowKB", 0) else []),
                *([f"--windowAt={a.windowAt}"] if getattr(a, "windowAt", "ch") != "ch" else []),
                *(["--around=domain-cl.csv"] if os.path.exists(f"{W_}/domain-cl.csv") else []),
                *(["--axeNear"] if opts.get("axeNear") else []),
                *([f"--lossDb={opts['lossDb']:g}"] if "lossDb" in opts else []),
                f"--out=plan{k}.txt"], f"plan{k}.log")
        return k

    def river(job):
        k, tag = job
        if not os.path.exists(f"{W_}/r{k}-{tag}-runs.csv") or len(open(f"{W_}/r{k}-{tag}-runs.csv").readlines()) < 2:
            sh([f"{a.bin}/river-bin", f"--nodes=c{k}-nodes-s35.csv", f"--routes=c{k}-routes-s35.csv",
                f"--gateways=c{k}-gateways-s35.csv", f"--plan=plan{k}.txt", f"--bits=pass{k}-bits",
                f"--firstRun={mission(k)}", "--runs=1", "--limit=900", "--gwSelect=quality", "--colours=7", *SCHEMES[tag], f"--out=r{k}-{tag}",
                *([f"--repair={a.riverRepair:g}"] if getattr(a, "riverRepair", 0) and tag == "rf" else []),
                *([f"--pageBreaks=pages{k}.txt"] if tag.startswith("t") and os.path.exists(f"{W_}/pages{k}.txt")
                  else [])],   # page_breaks.py: Trickle pages aligned to the clue images
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
    ap.add_argument("--bs", default="south", choices=("south", "end", "side", "centre"),
                    help="where the BS is (restructure.bs_point, item 149)")
    ap.add_argument("--shape", default="", help="map_gen options for the domain, e.g. spine=8.8,bend=220 (item 147)")
    ap.add_argument("--work", required=True)
    ap.add_argument("--bin", required=True)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--schemes", default="rf,ad12,d", help="tags of SCHEMES to run")
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
    ap.add_argument("--chordFit", type=float, default=0,
                    help="with --chordTour: cut each line to F copies of the clue set over its own cells (item 159)")
    ap.add_argument("--riverTour", type=float, default=0.0,
                    help="with --chordFit: weight of the latest estimated River end in the tour (item 159)")
    ap.add_argument("--bendShort", action="store_true",
                    help="with --bendCrit and --chordFit: bend only the clusters short of one copy (item 159)")
    ap.add_argument("--env", default="open", choices=tuple(ENV_LOSS),
                    help="A2G environment of the pass: R50 1015 m (open), 500, 200 or 100 m, by an excess loss "
                         "(ENV_LOSS; needs a pass-bin with --lossDb; item 163)")
    ap.add_argument("--mapRuns", action="store_true",
                    help="each cluster's ns-3 pass and River run as mission 100000 CLUSTERS + 100 SEED + k instead of 1: "
                         "draws independent across clusters and maps, shared by every design of one map (item 161)")
    ap.add_argument("--runSeed", type=int, default=1,
                    help="with --mapRuns: simulation seed R, mission index + 10^7 (R - 1); also the reception "
                         "realisations and layer-1 draws of the scoring tools (runseed.txt; item 188)")
    ap.add_argument("--riverRepair", type=float, default=0,
                    help="River (rf) with --repair=S: Axe cells complete their Seg from adjacent cells, a critical cell "
                         "idle S seconds asks again (needs a river-bin built with it; item 169)")
    ap.add_argument("--kinPass", action="store_true",
                    help="the ns-3 pass flies team 1's speed profile: slower, or circling, where a cluster is short (item 157)")
    ap.add_argument("--bendCrit", type=float, default=0,
                    help="cells: bend each chord lightly towards its critical cells within this distance (item 156)")
    ap.add_argument("--chAnywhere", action="store_true",
                    help="the CH the strongest node wherever it lies (no 300 m edge margin; item 154)")
    ap.add_argument("--chordTour", default="", metavar="FRAC,CLUE",
                    help="CHORD-T (item 136): bearings with at least FRAC of the longest in-cluster flight and CLUE of "
                         "one clue set, chosen jointly with team 1's tour (chord_tour.py)")
    ap.add_argument("--lane", type=float, default=4.5, help="--partition=lane: lane width, cells")
    ap.add_argument("--banks", default="parallel", choices=("parallel", "local"),
                    help="River Banks: the sum vector's normal, or the path's local normal (CLAUDE.md §8 item 103)")
    ap.add_argument("--windowKB", type=float, default=0,
                    help="each cluster needs only this much of D, around the CH (river_export.py; item 106)")
    ap.add_argument("--axeNear", action="store_true", help="River's Axe also takes packets sent next to the cluster "
                    "(river_export.py --axeNear; item 135)")
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
    if a.chordTour:
        stage_chord(a, W_, K)
    if a.bendCrit:
        stage_bend(a, W_, K)
    stage_tour(a, W_, K)
    if a.geometry:
        for k in range(1, K + 1):
            deploy_links(W_, k)
        return
    stage_runs(a, W_, K)


if __name__ == "__main__":
    main()
