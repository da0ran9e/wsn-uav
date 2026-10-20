"""The whole mission with the layer-1 scoring model (CLAUDE.md §8 items 110-114; paper/L1-MODEL-vi.md).

    python3 tools/l1_rank.py --set kmedoids "KF/k*" --draws 100 --methods P,B4,B1,B7 --out docs/data/l1rank/r1

Each set holds mission work folders with ns-3 pass bitmaps and River results (mission.py, meander_mission.py),
named <map> (k4-s1, ...) or k<K>. Per map and draw (paired: the same draw on the same map in every set):
  world     every critical cell's camera store and matches (l1_model), seeded by the map, the draw and the cell
            (q, r), so a cell holds the same store whatever the partition; c* = the critical cell with the highest
            verified score; phase 2 is complete when c* is verified (item 114)
  clues     one copy of the clue set, in broadcast order, laid on the Axe packets of the River window around the
            CH (river_plan window, 400 kB), copies repeated before and after it along the Axe; a clue counts only
            when every packet of one copy is held (item 34)
              river    the window copy delivered by River at leave + doneS, or any copy the cell itself heard
              direct   only the copies the cell's own nodes heard (no cooperation), at leave + gatherDoneS
  report    the cell's top score and its held-clue bitmap: matching (match_time), to the CH (0.1 s per cell),
            the CH's LoRa (one message per 40 s at a random phase, every result at the CH so far)
  BS        each report -> a normal posterior of the cell's verified score (l1_model.calib); P(cell is c*) for the
            reported cells, cells not reported yet at the prior, verified ones at their score (l1_model.p_best)
  team 2    one rotary UAV, 15 m/s, visiting every critical cell (verification = settle 5 s + 1 MB by unicast +
            matching the full reference set); it leaves at the first report (or, -wait, when every report is in)
            and decides at the BS, after each verification and, while waiting, at each new report:
              greedy   the known unvisited cell with the largest P(c*) / (flight + verification)
              pu       the same cell, but only if its P(c*) is at least P_U, the probability that c* has not
                       reported yet; otherwise it waits for the next report
              stage    while waiting it flies towards the P(c*)-weighted centre of the cells not visited yet
Methods (name = base + options):
  P         River reports;  B4  direct reports only (no cooperation);  P+prog  the direct report first, the River
            report when it comes (both through the CH's LoRa)
  options   -grouped (broadcast order by aspect), -equal (no importance: every clue weight 1), -wait, -pu, -stage,
            -short / -latency (team 1's tour; default l3first)
  B1 (no phase 1: TSP over every critical cell with the large file), B2-r (groups, multicast large file), B3-r
  (rotary multicast of the clue set to groups, then LoRa, team 2 greedy), B6 (rotary unicast of the clue set to
  each critical cell), B7 (oracle: straight to c*)
Writes OUT-draws.csv (map, set, draw, method: Tstar, Tall, rank, dep, starIn, ...), OUT-cells.csv (per critical
cell: held clue weight river/direct) and OUT-summary.csv.
"""
import argparse, csv, glob, hashlib, json, math, os, sys
from multiprocessing import Pool

import numpy as np

import l1_model as L
from l1_mission import match_time
from mission_baselines import BC_FRAME, BIG, SETTLE, UC_FRAME, frames, groups, per, tsp_order
from mission_policy import AIR, GAP, HOP, tour
from mission_report import load_map

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uav-coop2/tools"))
from river_plan import hexdist  # noqa: E402

V2, WINDOW = 15.0, math.ceil(400 * 1000 / 99)   # the River window of mission.py --windowKB 400
DEVICE, REF_IMAGES = "pi5-hailo8l", 20          # the large file: the full reference set, ~20 images in 1 MB
VERIFY = SETTLE + frames(BIG) * UC_FRAME + match_time(DEVICE, REF_IMAGES, L.M)
METHODS = "P,B4,P-grouped,B4-grouped,P-equal,P-wait,B1,B2-300,B2-500,B3-300,B3-500,B6,B7"


def complete(w):
    if not os.path.exists(f"{w}/map.json"):
        return False
    K = json.load(open(f"{w}/map.json"))["clusters"]
    return all(os.path.exists(f"{w}/r{k}-rf-crit.csv") and os.path.exists(f"{w}/pass{k}-bits-r1.bin")
               for k in range(1, K + 1))


def mapname(w):
    b = os.path.basename(os.path.normpath(w))
    return b if "-s" in b else {"k2": "k2-s3", "k4": "k4-s2", "k6": "k6-s4", "k8": "k8-s4"}.get(b, b)


def holdings(M, C, seqs):
    """{(k, h): {order: (river mask, direct mask)}}."""
    out = {}
    for k, cl in M["cl"].items():
        P, uav, bits, inD = cl["P"], cl["geo"]["uav"], cl["bits"], cl["inD"]
        allp = np.array(sorted(s for a in P["axe"] for s in P["seg"][a]))
        chn = next(x for x in cl["geo"]["nodes"] if x["isCH"] == "1")
        c0 = int(np.argmin(np.linalg.norm(uav - [float(chn["x"]), float(chn["y"])], axis=1)))
        n = len(allp)
        i0 = min(max(int(np.searchsorted(allp, c0)) - WINDOW // 2, 0), n - WINDOW) if n > WINDOW else 0
        for h in P["crit"]:
            heard = bits[cl["mem"][h]].any(axis=0)[allp]          # the cell's own reception, per Axe packet
            got = inD[allp]                                        # D: heard by some node of the cluster
            res = {}
            for name, seq in seqs.items():
                st, en, Q = L.layout(C, seq)
                riv, dire = np.zeros(len(C), bool), np.zeros(len(C), bool)
                for j in range(len(C)):
                    riv[j] = i0 + en[j] <= n and got[i0 + st[j]:i0 + en[j]].all()
                    for kk in range(-(i0 // Q) - 1, (n - i0) // Q + 1):   # every copy along the Axe
                        a0, a1 = i0 + kk * Q + st[j], i0 + kk * Q + en[j]
                        if a0 >= 0 and a1 <= n and heard[a0:a1].all():
                            dire[j] = True
                            break
                res[name] = (riv | dire, dire)
            out[(k, h)] = res
    return out


def world(name, d, cells, C):
    """Per critical cell (k, h): the verified score U and the match matrix."""
    U, mv = {}, {}
    for x in cells:
        q, r = x[1]
        seed = int.from_bytes(hashlib.sha256(f"{name}/{d}/{q}/{r}".encode()).digest()[:8], "little")
        rng = np.random.default_rng(seed)
        a = L.stores(rng, 1)
        mv[x] = L.matches(rng, a, C)
        U[x] = float(L.verified(a, C)[0])
    return U, mv


def lora(M, ready, phase):
    out = {}
    for (k, h), t in ready.items():
        at = t + HOP * hexdist(h, M["cl"][k]["P"]["ch"])
        out[(k, h)] = phase[k] + max(0, math.ceil((at - phase[k]) / GAP)) * GAP + AIR
    return out


def team2(bs, pos, reports, U, prior, star, depart="early", rule="greedy", stage=False):
    """Team 2 visiting every cell. reports {cell: [(arrival at the BS, (mu, sd)), ...]} in time order.
    Returns Tstar, Tall, rank of c*, departure, c*'s first report at the BS."""
    cells = list(pos)
    first = {c: reports[c][0][0] for c in cells}
    events = sorted({t for c in cells for t, _ in reports[c]})
    t = min(first.values()) if depart == "early" else max(r[-1][0] for r in reports.values())
    dep, p, seen, left, Ts, rank = t, bs, [], set(cells), None, None

    def post(c):
        return [v for tt, v in reports[c] if tt <= t][-1]

    while left:
        known = sorted(c for c in left if first[c] <= t)
        n_un = len(left) - len(known)
        go = False
        if known:
            pk, pu = L.p_best([post(c) for c in known], (prior, n_un), [U[v] for v in seen])
            i = max(range(len(known)), key=lambda i: (pk[i] / (math.dist(p, pos[known[i]]) / V2 + VERIFY),
                                                     -math.dist(p, pos[known[i]])))
            go = rule == "greedy" or n_un == 0 or pk[i] >= n_un * pu
        if go:
            c = known[i]
            t += math.dist(p, pos[c]) / V2 + VERIFY
            p = pos[c]
            seen.append(c)
            left.remove(c)
            if c == star:
                Ts, rank = t, len(seen)
            continue
        nxt = min(e for e in events if e > t)
        if stage and known:
            w = {c: pk[j] for j, c in enumerate(known)} | {c: pu for c in left if c not in known}
            tot = sum(w.values())
            if tot > 0:
                goal = tuple(sum(w[c] * pos[c][a] for c in w) / tot for a in (0, 1))
                d = math.dist(p, goal)
                f = min(1.0, V2 * (nxt - t) / d) if d > 0 else 0.0
                p = (p[0] + f * (goal[0] - p[0]), p[1] + f * (goal[1] - p[1]))
        t = nxt
    return Ts, t + math.dist(p, bs) / V2, rank, dep, first[star]


def fly_all(bs, stops, cost, star_in):
    """No phase 1: TSP over stops (hover point, members), cost(stop) at each. Tstar, Tall, rank."""
    o = tsp_order(bs, [s[0] for s in stops])
    t, p, Ts, rank = 0.0, bs, None, None
    for n, i in enumerate(o):
        t += math.dist(p, stops[i][0]) / V2 + cost(stops[i])
        p = stops[i][0]
        if Ts is None and star_in(stops[i]):
            Ts, rank = t, n + 1
    return Ts, t + math.dist(p, bs) / V2, rank


def missions(M, tours, hold, d, phase, C, Cq, methods):
    """The requested methods on one draw. Returns {method: (Tstar, Tall, rank, dep, starIn)} and per-cell rows."""
    bs = M["bs"]
    crits = [(k, h) for k in sorted(M["cl"]) for h in M["cl"][k]["P"]["crit"]]
    pos = {x: tuple(M["cl"][x[0]]["geo"]["c"][x[1]]) for x in crits}
    U, mv = world(M["name"], d, crits, C)
    star = max(crits, key=lambda x: U[x])
    tm = match_time(DEVICE, len(C), L.M)
    res = M["cl"]
    prior = L.calib(C, np.ones(len(C), bool))[3]
    full = np.ones(len(C), bool)
    cache = {}

    def posts(kind, order, wC):
        key = (kind, order, id(wC))
        if key not in cache:
            out = {}
            for x in crits:
                m = full if kind == "full" else hold[x][order][0 if kind == "river" else 1]
                S = float(L.report(mv[x], wC, m)[0])
                al, be, sd, _ = L.calib(wC, m, truth=C)
                out[x] = (al + be * S, max(sd, 1e-4)) if m.any() else (al, sd)
            cache[key] = out
        return cache[key]

    def ready(kind, tk):
        leave = {l[0]: l[4] for l in tours[tk][0]}
        col = "doneS" if kind == "river" else "gatherDoneS"
        return lora(M, {x: leave[x[0]] + float(res[x[0]]["res"]["rf"][x[1]][col]) + tm for x in crits}, phase)

    out = {}
    light = sum(math.ceil(c["kB"] * 1000 / 99) for c in C)
    for meth in methods:
        base, *opts = meth.split("-")
        if base in ("P", "B4", "P+prog"):
            order = "grouped" if "grouped" in opts else "interleaved"
            wC = Cq if "equal" in opts else C
            tk = next((o for o in opts if o in ("short", "latency")), "l3first")
            if base == "P+prog":
                ad, ar = ready("direct", tk), ready("river", tk)
                pd_, pr_ = posts("direct", order, wC), posts("river", order, wC)
                reps = {x: [(t, v) for t, _, v in sorted([(ad[x], 0, pd_[x]), (ar[x], 1, pr_[x])])] for x in crits}
            else:
                kind = "river" if base == "P" else "direct"
                a_, p_ = ready(kind, tk), posts(kind, order, wC)
                reps = {x: [(a_[x], p_[x])] for x in crits}
            out[meth] = team2(bs, pos, reps, U, prior, star, "wait" if "wait" in opts else "early",
                              "pu" if "pu" in opts else "greedy", "stage" in opts)
        elif meth == "B1":
            out[meth] = fly_all(bs, [(pos[x], [x]) for x in crits], lambda s: VERIFY, lambda s: star in s[1]) + (0.0, 0.0)
        elif meth == "B7":
            out[meth] = (math.dist(bs, pos[star]) / V2 + VERIFY, float("nan"), 1, 0.0, 0.0)
        elif base in ("B2", "B3"):
            G = groups(pos, int(opts[0]))
            bc = lambda g, nfr: SETTLE + nfr * BC_FRAME / (1 - max(per(math.dist(g[0], pos[b])) for b in g[1]))
            if base == "B2":
                out[meth] = fly_all(bs, G, lambda g: bc(g, frames(BIG)) + match_time(DEVICE, REF_IMAGES, L.M),
                                    lambda g: star in g[1]) + (0.0, 0.0)
            else:
                t, p, rd = 0.0, bs, {}
                for i in tsp_order(bs, [g[0] for g in G]):
                    hp, mem = G[i]
                    t += math.dist(p, hp) / V2 + bc(G[i], light)
                    for b in mem:
                        rd[b] = t + tm
                    p = hp
                a_, p_ = lora(M, rd, phase), posts("full", "", C)
                out[meth] = team2(bs, pos, {x: [(a_[x], p_[x])] for x in crits}, U, prior, star)
        elif meth == "B6":
            t, p, rd = 0.0, bs, {}
            for i in tsp_order(bs, [pos[x] for x in crits]):
                x = crits[i]
                t += math.dist(p, pos[x]) / V2 + SETTLE + light * UC_FRAME
                rd[x] = t + tm
                p = pos[x]
            a_, p_ = lora(M, rd, phase), posts("full", "", C)
            out[meth] = team2(bs, pos, {x: [(a_[x], p_[x])] for x in crits}, U, prior, star)
        else:
            raise SystemExit(f"unknown method {meth}")
    w = np.array([c["w"] for c in C])
    rows = [dict(cluster=x[0], q=x[1][0], r=x[1][1], star=int(x == star), U=round(U[x], 4),
                 riverW=round(float(w[hold[x]["interleaved"][0]].sum() / w.sum()), 3),
                 directW=round(float(w[hold[x]["interleaved"][1]].sum() / w.sum()), 3),
                 riverAll=int(hold[x]["interleaved"][0].all()), directAll=int(hold[x]["interleaved"][1].all()))
            for x in crits]
    return out, rows, len(crits)


def one_work(job):
    """All draws on one work folder (run in a worker process)."""
    sname, w, ndraws, methods = job
    C = L.clues()
    Cq = [dict(c, w=1.0) for c in C]
    seqs = {"interleaved": L.order(C, "interleaved"), "grouped": L.order(C, "grouped")}
    M = load_map(w, schemes=("rf",))
    M["name"] = mapname(w)
    kinds = {o for m in methods for o in m.split("-") if o in ("short", "latency")} | {"l3first"}
    tours = {k: tour(M, k) for k in kinds}
    hold = holdings(M, C, seqs)
    seedm = int.from_bytes(hashlib.sha256(M["name"].encode()).digest()[:4], "little")
    prng = np.random.default_rng(seedm)
    draws, cells = [], []
    for d in range(ndraws):
        phase = {k: float(prng.uniform(0, GAP)) for k in sorted(M["cl"])}
        out, rows, nc = missions(M, tours, hold, d, phase, C, Cq, methods)
        for meth, (Ts, Ta, rank, dep, sin) in out.items():
            tk = next((o for o in meth.split("-") if o in ("short", "latency")), "l3first")
            draws.append(dict(map=M["name"], size=len(M["cl"]), set=sname, draw=d, method=meth, crits=nc,
                              team1=round(tours[tk][1], 1), Tstar=round(Ts, 1), Tall=round(Ta, 1), rank=rank,
                              dep=round(dep, 1), starIn=round(sin, 1)))
        if d == 0:
            cells += [dict(map=M["name"], set=sname, **r) for r in rows]
    print(f"{sname} {M['name']}: {len(M['cl'])} clusters, {nc} critical cells; " + ", ".join(
        f"{m} {np.mean([r['Tstar'] for r in draws if r['method'] == m]):.0f}" for m in methods[:4]) + " s", flush=True)
    return draws, cells


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", nargs=2, action="append", metavar=("NAME", "GLOBS"), required=True)
    ap.add_argument("--draws", type=int, default=100)
    ap.add_argument("--methods", default=METHODS)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    methods = a.methods.split(",")
    jobs = [(sname, w, a.draws, methods) for sname, globs in a.set
            for w in sorted(w for g in globs.split(",") for w in glob.glob(g) if complete(w))]
    with Pool(a.jobs) as pool:
        got = pool.map(one_work, jobs, chunksize=1)
    draws = [r for d, _ in got for r in d]
    cells = [r for _, c in got for r in c]
    for suffix, rows in (("draws", draws), ("cells", cells)):
        with open(f"{a.out}-{suffix}.csv", "w", newline="") as f:
            wr = csv.DictWriter(f, fieldnames=list(rows[0]))
            wr.writeheader()
            wr.writerows(rows)
    summ = []
    for sname, _ in a.set:
        for size in sorted({r["size"] for r in draws if r["set"] == sname}):
            R = [r for r in draws if r["set"] == sname and r["size"] == size]
            for meth in methods:
                X = [r for r in R if r["method"] == meth]
                ts = np.array([r["Tstar"] for r in X])
                summ.append(dict(set=sname, size=size, method=meth, maps=len({r["map"] for r in X}), n=len(X),
                                 Tstar=round(ts.mean(), 1), ci=round(1.96 * ts.std(ddof=1) / math.sqrt(len(ts)), 1),
                                 p90=round(float(np.percentile(ts, 90)), 1),
                                 Tall=round(float(np.mean([r["Tall"] for r in X])), 1) if meth != "B7" else "",
                                 rank=round(float(np.mean([r["rank"] for r in X])), 2),
                                 first=round(float(np.mean([r["rank"] == 1 for r in X])), 3)))
    with open(f"{a.out}-summary.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(summ[0]))
        wr.writeheader()
        wr.writerows(summ)


if __name__ == "__main__":
    main()
