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
                       reported yet (-puh: P_U / 2, -puq: P_U / 4); otherwise it waits for the next report
              put      as pu, but P_U counts only the cells whose first report reaches the BS while team 2 would be
                       busy flying to and verifying this one (the BS knows when each cluster reports from the plan)
              stage    while waiting it flies towards the P(c*)-weighted centre of the cells not visited yet
Methods (name = base + options):
  P         River reports;  B4  direct reports only (no cooperation);  P+prog  the direct report first, the River
            report when it comes (both through the CH's LoRa); Pd, Pd+prog / Pt, Pt+prog  the same with the
            direct-pull (r*-d) / Trickle (r*-t, CLAUDE.md §8 item 139) ns-3 runs in place of River's
  options   -grouped (broadcast order by aspect), -equal (no importance: every clue weight 1), -wait, -zero (team 2
            leaves with team 1, at t = 0, and stages towards the critical cells' centre until reports come), -pu,
            -puh, -puq, -put, -stage, -short / -latency / -seam (team 1's tour; default l3first; seam = latency
            with seamless junctions, mission_policy.seams;
            kin = latency with Dubins transits, mission_policy.kin_links)
            -redir (team 2 may change its target in flight when a report comes; P, B4, P+prog)
            P+prog only: -allclues (upper bound: the River report holds all 12 clues, as if every Axe were long
            enough for the clue set)
  B1 (no phase 1: TSP over every critical cell with the large file), B2-r (groups, multicast large file), B3-r
  (rotary multicast of the clue set to groups, then LoRa, team 2), B6 (rotary unicast of the clue set to each
  critical cell, then LoRa, team 2), B7 (oracle: straight to c*); B3 and B6 take the team-2 options (-pu..., -stage,
  -zero, -redir)
  B8-r      (CLAUDE.md §8 item 134) the fixed wing of team 1 serves the same groups as B3-r itself, no River: it
            flies to each group's hover point (straight, V1) and circles it at R_TURN, multicasting the clue set
            until the group's worst receiver has it (ideal fountain code at the mean PER over the circle, as B3);
            then LoRa and team 2 (team-2 options as B3)
  B5        (item 134) the fixed wing sweeps the whole land on SWATH's serpentine (swath.route, the shortest
            BS -> route -> BS; Dubins turns), broadcasting the clue set over and over, one frame per 0.5 m; no River.
            Reception as the pass: a cell holds a frame when one of its nodes does (each node loses it with the
            A2G PER, independently), a clue when it holds every frame of one copy (one realisation per map, seeded
            by its name). Lanes: the widest of LANES cells with every critical cell holding all clues (else the
            narrowest). A cell reports when it holds every clue, else after the last frame within 1.5 km, plus its
            in-cell gather (gatherDoneS) and the match; then LoRa and team 2 (team-2 options as B3)
Writes OUT-draws.csv (map, set, draw, method: Tstar, Tall, rank, dep, starIn, ...), OUT-cells.csv (per critical
cell: held clue weight river/direct) and OUT-summary.csv.
"""
import argparse, csv, glob, hashlib, json, math, os, sys
from multiprocessing import Pool

import numpy as np

import l1_model as L
from l1_mission import match_time
from mission_baselines import BC_FRAME, BIG, SETTLE, UC_FRAME, frames, groups, per, tsp_order
from mission_policy import AIR, GAP, HOP, R_TURN, V1, tour
import swath
from mission_report import load_map

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uav-coop2/tools"))
from river_plan import hexdist  # noqa: E402

V2, WINDOW = 15.0, math.ceil(400 * 1000 / 99)   # the River window of mission.py --windowKB 400
DEVICE, REF_IMAGES = "pi5-hailo8l", 20          # the large file: the full reference set, ~20 images in 1 MB
VERIFY = SETTLE + frames(BIG) * UC_FRAME + match_time(DEVICE, REF_IMAGES, L.M)
METHODS = "P,B4,P-grouped,B4-grouped,P-equal,P-wait,B1,B2-300,B2-500,B3-300,B3-500,B6,B7"
BETA = {"pu": 1.0, "puh": 0.5, "puq": 0.25}      # -pu: go at P >= P_U; -puh / -puq: at P >= P_U / 2, P_U / 4


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
        n = len(allp)

        def start(x, y):   # river_plan.plan's window: WINDOW Axe packets around where the UAV passes closest to (x, y)
            c0 = int(np.argmin(np.linalg.norm(uav - [x, y], axis=1)))
            return min(max(int(np.searchsorted(allp, c0)) - WINDOW // 2, 0), n - WINDOW) if n > WINDOW else 0
        i0 = start(float(chn["x"]), float(chn["y"]))
        for h in P["crit"]:
            if M.get("windowAt") == "crit":   # mission.py --windowAt crit (item 120): each cell its own window
                i0 = start(*cl["geo"]["c"][h])
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


LANES = (12, 11, 10, 9, 8, 7, 6, 5, 4, 3)   # B5 lane widths tried, cells, widest first


def orbit_per(c, x, n=72):
    """Mean A2G PER at ground point x from a UAV circling c at R_TURN."""
    return float(np.mean([per(math.dist(x, (c[0] + R_TURN * math.cos(2 * math.pi * i / n),
                                             c[1] + R_TURN * math.sin(2 * math.pi * i / n)))) for i in range(n)]))


def dubins_free(bs, P, back):
    """Shortest Dubins path from the BS (any heading) into the polyline's start, or (back) from its end to the BS."""
    if back:
        v = P[-1] - P[-6]
        return swath.dubins.free_end((*P[-1], math.atan2(v[1], v[0])), bs, swath.RHO)
    v = P[5] - P[0]
    return swath.dubins.free_start(bs, (*P[0], math.atan2(v[1], v[0])), swath.RHO)


def b5_sweep(M, C, seq, crits, res):
    """B5 (item 134): ({(k, h): (held clue mask, time the cell reports at its CL)}, lane width, route metres)."""
    st, en, Q = L.layout(C, seq)
    land = {h for cl in M["cl"].values() for h in cl["geo"]["cells"]}
    nodes = {x: np.array([(float(n["x"]), float(n["y"])) for n in M["cl"][x[0]]["geo"]["nodes"]
                          if (int(n["q"]), int(n["r"])) == x[1]]) for x in crits}
    grid = np.arange(0, 3001.0)
    pt = np.array([per(g) for g in grid])
    rng = np.random.default_rng(int.from_bytes(hashlib.sha256(f"B5/{M['name']}".encode()).digest()[:8], "little"))
    for lane in LANES:
        _, _, _, r = swath.routes(land, M["bs"], lane)[0]
        P, sv = r["poly"], r["s"]
        if dubins_free(M["bs"], P[::-1], False) + dubins_free(M["bs"], P, True) < \
                dubins_free(M["bs"], P, False) + dubins_free(M["bs"], P[::-1], True):
            P, sv = P[::-1], sv[-1] - sv[::-1]
        t0 = dubins_free(M["bs"], P, False) / V1
        nf = int(sv[-1] / 0.5)
        F = np.array([np.interp(np.arange(nf) * 0.5, sv, P[:, a]) for a in (0, 1)]).T   # frame positions
        out = {}
        for x in crits:
            d = np.linalg.norm(F[:, None, :] - nodes[x][None, :, :], axis=2)                # frames x nodes
            near = d.min(axis=1) < 1500
            lose = np.where(near[:, None], np.interp(d, grid, pt, right=1.0), 1.0).prod(axis=1)
            got = rng.random(nf) >= lose
            held, when = np.zeros(len(C), bool), np.full(len(C), np.inf)
            for j in range(len(C)):
                for kk in range(nf // Q + 1):
                    a0, a1 = kk * Q + st[j], kk * Q + en[j]
                    if a1 <= nf and got[a0:a1].all():
                        held[j], when[j] = True, t0 + a1 * 0.5 / V1
                        break
            last = t0 + (np.nonzero(near)[0].max() + 1) * 0.5 / V1 if near.any() else t0
            gat = float(res[x[0]]["res"]["rf"][x[1]]["gatherDoneS"])
            out[x] = (held, (float(when.max()) if held.all() else last) + max(gat, 0.0))
        if all(h.all() for h, _ in out.values()) or lane == LANES[-1]:
            return out, lane, float(sv[-1])


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


def policy(opts):
    """Team 2's options from a method's parts: (departure, waiting rule, staging, beta)."""
    rule = "put" if "put" in opts else "pu" if any(o in BETA for o in opts) else "greedy"
    return (next((o for o in opts if o in ("wait", "zero")), "early"), rule, "stage" in opts,
            next((BETA[o] for o in opts if o in BETA), 1.0))


def team2(bs, pos, reports, U, prior, star, depart="early", rule="greedy", stage=False, trace=None, beta=1.0,
          redirect=False):
    """Team 2 visiting every cell. reports {cell: [(arrival at the BS, (mu, sd)), ...]} in time order.
    Returns Tstar, Tall, rank of c*, departure, c*'s first report at the BS. trace (a list), when given, gets
    ("p", t, {cell: P(c*)}) at every decision and the moves ("fly", t0, t1, a, b, cell), ("verify", t0, t1, cell),
    ("stage", t0, t1, a, b), ("back", t0, t1, a, b). redirect: a flight is cut at each report that reaches the BS
    before team 2 arrives, and team 2 decides again from where it is (it may keep its target or change it)."""
    cells = list(pos)
    first = {c: reports[c][0][0] for c in cells}
    events = sorted({t for c in cells for t, _ in reports[c]})
    t = {"early": min(first.values()), "zero": 0.0}.get(depart, max(r[-1][0] for r in reports.values()))
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
            if rule == "put":   # only the cells whose first report comes while team 2 would be busy with this one
                busy = t + math.dist(p, pos[known[i]]) / V2 + VERIFY
                n_win = sum(1 for c in left if t < first[c] <= busy)
                go = pk[i] >= n_win * pu
            else:
                go = rule == "greedy" or n_un == 0 or pk[i] >= beta * n_un * pu
            if trace is not None:
                trace.append(("p", t, {c: pk[j] for j, c in enumerate(known)} | {"unreported": pu}))
        if go:
            c = known[i]
            t1 = t + math.dist(p, pos[c]) / V2
            nxt = min((e for e in events if e > t), default=math.inf)
            if redirect and nxt < t1:                 # a report comes in flight: fly until then, decide again
                f = (nxt - t) / (t1 - t)
                q = (p[0] + f * (pos[c][0] - p[0]), p[1] + f * (pos[c][1] - p[1]))
                if trace is not None:
                    trace.append(("fly", t, nxt, p, q, c))
                p, t = q, nxt
                continue
            if trace is not None:
                trace += [("fly", t, t1, p, pos[c], c), ("verify", t1, t1 + VERIFY, c)]
            t += math.dist(p, pos[c]) / V2 + VERIFY
            p = pos[c]
            seen.append(c)
            left.remove(c)
            if c == star:
                Ts, rank = t, len(seen)
            continue
        nxt = min(e for e in events if e > t)
        if stage:
            w = ({c: pk[j] for j, c in enumerate(known)} | {c: pu for c in left if c not in known}) if known else \
                {c: 1.0 for c in left}
            tot = sum(w.values())
            if tot > 0:
                goal = tuple(sum(w[c] * pos[c][a] for c in w) / tot for a in (0, 1))
                d = math.dist(p, goal)
                f = min(1.0, V2 * (nxt - t) / d) if d > 0 else 0.0
                q = (p[0] + f * (goal[0] - p[0]), p[1] + f * (goal[1] - p[1]))
                if trace is not None:
                    trace.append(("stage", t, t + f * d / V2, p, q))
                p = q
        t = nxt
    if trace is not None:
        trace.append(("back", t, t + math.dist(p, bs) / V2, p, bs))
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


def missions(M, tours, hold, d, phase, C, Cq, methods, traces=None):
    """The requested methods on one draw. Returns {method: (Tstar, Tall, rank, dep, starIn)} and per-cell rows.
    traces (a dict), when given, gets team 2's trace (see team2) of each P / B4 / P+prog method."""
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

    def ready(kind, tk, scheme="rf"):
        leave = {l[0]: l[4] for l in tours[tk][0]}
        col = "doneS" if kind == "river" else "gatherDoneS"
        return lora(M, {x: leave[x[0]] + float(res[x[0]]["res"][scheme][x[1]][col]) + tm for x in crits}, phase)

    out = {}
    light = sum(math.ceil(c["kB"] * 1000 / 99) for c in C)
    for meth in methods:
        base, *opts = meth.split("-")
        if base in ("P", "B4", "P+prog", "Pd", "Pd+prog", "Pt", "Pt+prog"):
            sch = "d" if base.startswith("Pd") else "t" if base.startswith("Pt") else "rf"
            base = base.replace("Pd", "P").replace("Pt", "P")
            order = "grouped" if "grouped" in opts else "interleaved"
            wC = Cq if "equal" in opts else C
            tk = next((o for o in opts if o in ("short", "latency", "seam", "kin", "skin")), "l3first")
            if base == "P+prog":
                ad, ar = ready("direct", tk), ready("river", tk, sch)
                pd_, pr_ = posts("direct", order, wC), posts("full" if "allclues" in opts else "river", order, wC)
                reps = {x: [(t, v) for t, _, v in sorted([(ad[x], 0, pd_[x]), (ar[x], 1, pr_[x])])] for x in crits}
            else:
                kind = "river" if base == "P" else "direct"
                a_, p_ = ready(kind, tk, sch), posts(kind, order, wC)
                reps = {x: [(a_[x], p_[x])] for x in crits}
            dep, rule, stg, beta = policy(opts)
            tr = None if traces is None else traces.setdefault(meth, [])
            out[meth] = team2(bs, pos, reps, U, prior, star, dep, rule, stg, tr, beta, "redir" in opts)
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
                dep, rule, stg, beta = policy(opts)
                out[meth] = team2(bs, pos, {x: [(a_[x], p_[x])] for x in crits}, U, prior, star, dep, rule, stg,
                                  beta=beta, redirect="redir" in opts)
        elif base == "B8":
            t, p, rd = 0.0, bs, {}
            G = groups(pos, int(opts[0]))
            for i in tsp_order(bs, [g[0] for g in G]):
                hp, mem = G[i]
                t += math.dist(p, hp) / V1 + light * BC_FRAME / (1 - max(orbit_per(hp, pos[b]) for b in mem))
                for b in mem:
                    rd[b] = t + tm
                p = hp
            a_, p_ = lora(M, rd, phase), posts("full", "", C)
            dep, rule, stg, beta = policy(opts)
            out[meth] = team2(bs, pos, {x: [(a_[x], p_[x])] for x in crits}, U, prior, star, dep, rule, stg,
                              beta=beta, redirect="redir" in opts)
        elif base == "B5":
            sweep = M["b5"][0]
            a_ = lora(M, {x: sweep[x][1] + tm for x in crits}, phase)
            p_ = {}
            for x in crits:
                m = sweep[x][0]
                al, be, sd, _ = L.calib(C, m, truth=C)
                p_[x] = (al + be * float(L.report(mv[x], C, m)[0]), max(sd, 1e-4)) if m.any() else (al, sd)
            dep, rule, stg, beta = policy(opts)
            out[meth] = team2(bs, pos, {x: [(a_[x], p_[x])] for x in crits}, U, prior, star, dep, rule, stg,
                              beta=beta, redirect="redir" in opts)
        elif base == "B6":
            t, p, rd = 0.0, bs, {}
            for i in tsp_order(bs, [pos[x] for x in crits]):
                x = crits[i]
                t += math.dist(p, pos[x]) / V2 + SETTLE + light * UC_FRAME
                rd[x] = t + tm
                p = pos[x]
            a_, p_ = lora(M, rd, phase), posts("full", "", C)
            dep, rule, stg, beta = policy(opts)
            out[meth] = team2(bs, pos, {x: [(a_[x], p_[x])] for x in crits}, U, prior, star, dep, rule, stg, beta=beta,
                              redirect="redir" in opts)
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
    sname, w, ndraws, methods, par = job
    L.DIM, L.RHO, L.M = par["dim"], par["rho"], par["m"]
    C = L.clues()
    Cq = [dict(c, w=1.0) for c in C]
    seqs = {"interleaved": L.order(C, "interleaved"), "grouped": L.order(C, "grouped")}
    K = json.load(open(f"{w}/map.json"))["clusters"]
    for tag in ("d", "t"):   # no direct-pull (d) or Trickle (t) run on this work folder
        if not all(os.path.exists(f"{w}/r{k}-{tag}-crit.csv") for k in range(1, K + 1)):
            methods = [m for m in methods if not m.startswith("P" + tag)]
    M = load_map(w, schemes=("rf",) + tuple(t for t in ("d", "t") if any(m.startswith("P" + t) for m in methods)))
    M["name"] = mapname(w)
    M["windowAt"] = "crit" if any(l.startswith("NEED") for k in range(1, K + 1) for l in open(f"{w}/plan{k}.txt")) \
        else "ch"
    kinds = {o for m in methods for o in m.split("-") if o in ("short", "latency", "seam", "kin", "skin")} | {"l3first"}
    tours = {k: tour(M, k) for k in kinds}
    hold = holdings(M, C, seqs)
    if any(m.split("-")[0] == "B5" for m in methods):
        crits = [(k, h) for k in sorted(M["cl"]) for h in M["cl"][k]["P"]["crit"]]
        M["b5"] = b5_sweep(M, C, seqs["interleaved"], crits, M["cl"])
        print(f"{sname} {M['name']}: B5 lanes {M['b5'][1]} cells, route {M['b5'][2] / 1000:.1f} km, "
              f"{sum(h.all() for h, _ in M['b5'][0].values())}/{len(crits)} critical cells hold every clue", flush=True)
    seedm = int.from_bytes(hashlib.sha256(M["name"].encode()).digest()[:4], "little")
    prng = np.random.default_rng(seedm)
    draws, cells = [], []
    for d in range(ndraws):
        phase = {k: float(prng.uniform(0, GAP)) for k in sorted(M["cl"])}
        out, rows, nc = missions(M, tours, hold, d, phase, C, Cq, methods)
        for meth, (Ts, Ta, rank, dep, sin) in out.items():
            tk = next((o for o in meth.split("-") if o in ("short", "latency", "seam", "kin", "skin")), "l3first")
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
    ap.add_argument("--dim", type=int, default=L.DIM, help="layer 1: effective embedding dimension")
    ap.add_argument("--rho", type=float, default=L.RHO, help="layer 1: share of look-alike crops")
    ap.add_argument("--m", type=int, default=L.M, help="layer 1: crops per store")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    methods = a.methods.split(",")
    par = dict(dim=a.dim, rho=a.rho, m=a.m)
    jobs = [(sname, w, a.draws, methods, par) for sname, globs in a.set
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
                if not X:   # a Pd method on a set without direct-pull runs
                    continue
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
