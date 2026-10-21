"""Mission policies over many maps and draws (CLAUDE.md §8 item 70); figures without text (item 63).

    python3 tools/mission_policy.py --works "W/k*" --draws 100 --figs docs/figures --out docs/data/mission/policy

Each work folder is a mission.py map with River (prepared) run in ns-3 per cluster. A cluster's layer-3 times
do not depend on when the UAV reaches it, so every policy below reuses them.

Report chain (new constraint, item 70): critical cell c of cluster k
  ready_c  = leave_k + done_c (ns-3) + MATCH                 matching done at c
  atCH_c   = ready_c + HOP * cells(c, CH)                     result passed to the CH (a control frame per cell)
  the CH owns the LoRa uplink: airtime AIR, duty cycle DUTY, so one message per GAP = AIR / DUTY s, at
  phase_k + n GAP (phase_k uniform in [0, GAP), drawn per draw); each message carries every result at the CH
  by then; it reaches the BS AIR s after the slot.
Suspects: one critical cell true, 2 or 3 others false (per draw). Each suspect's report carries a score:
  true U(S_TRUE), false U(S_FALSE).

Policies, all combinations:
  tour   short    team 1's shortest tour (Held-Karp over cluster segments and direction)
         l3first  the tour minimising the time all critical cells are ready, max_k (leave_k + L3hat_k), with
                  L3hat_k = max(15, -52 + 6.92 maxFar_k) s, maxFar_k = the largest cell distance from a critical
                  cell to an Axe cell (the BS knows it from the plan; fitted on the first 20 clusters, r = 0.67);
                  exact (Pareto Held-Karp over time and readiness)
  depart   wait     team 2 leaves once every critical cell has reported
           early    team 2 leaves at the first suspect report
  order    tsp      the next suspect is the first of the shortest open tour over the known unvisited suspects from
                    here and back to the BS (with wait: one fixed closed tour, shorter first leg)
           score    the next suspect maximises score / (flight + HOVER) among the known unvisited ones
  Team 2 decides at the BS and after each verification; with no known unvisited suspect it waits where it is
  for the next report. At the true suspect it verifies and flies back: the mission ends.
Writes OUT-draws.csv (map, size, draw, policy, metrics), OUT-summary.csv and figures FIGS/policy-{end,example}.png.
"""
import argparse, csv, glob, itertools, json, math, os, random, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from map_gen import strip_text
from mission_report import (AXE, BANK, FALSE, GREY, INK, INK2, SURF, TRUE, crit_marks, frame, land, load_map)
from tour_heur import order_segments

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uav-coop2/tools"))
from river_plan import hexdist  # noqa: E402

V1, V2, HOVER, MATCH, HOP = 50.0, 15.0, 30.0, 5.0, 0.1
AIR, DUTY = 0.4, 0.01
GAP = AIR / DUTY
S_TRUE, S_FALSE = (0.5, 1.0), (0.2, 0.8)
POLICIES = [(t, d, o) for t in ("short", "l3first") for d in ("wait", "early") for o in ("tsp", "score")]


def l3hat(C):
    P = C["P"]
    far = max(max(hexdist(h, a) for a in P["axe"]) for h in P["crit"])
    return max(15.0, -52.0 + 6.92 * far)


SEAM_GAP, SEAM_DEG = 1000.0, 30.0


def seams(M):
    """Seamless junctions (CLAUDE.md §8 item 116): {(k, d, k2, e): metres} for the legs on which team 1 flies
    straight on from the core of one cluster's path (its lead-out dropped) into the core of the next (its lead-in
    dropped): the cores at most SEAM_GAP apart, the exit heading, the gap and the entry heading within SEAM_DEG of
    each other. The value replaces the straight transit between the two full paths, gap - lead-out - lead-in, so
    it is negative when the cores touch (each leg's own length still counts its leads)."""
    core = {}
    for k, C in M["cl"].items():
        p, part = C["geo"]["path"], C["geo"]["part"]
        i0, i1 = int(np.argmax(part >= 1)), len(part) - 1 - int(np.argmax(part[::-1] <= 2))
        lin, lout = float(np.linalg.norm(np.diff(p[:i0 + 1], axis=0), axis=1).sum()), \
            float(np.linalg.norm(np.diff(p[i1:], axis=0), axis=1).sum())
        a, b = p[i0], p[i1]
        ha, hb = p[min(i0 + 25, i1)] - a, b - p[max(i1 - 25, i0)]
        # direction 0: enters at a heading ha, leaves at b heading hb, leads lin / lout; direction 1 reversed
        core[(k, 0)] = (a, ha, b, hb, lin, lout)
        core[(k, 1)] = (b, -hb, a, -ha, lout, lin)
    ang = lambda u, v: math.degrees(math.acos(max(-1.0, min(1.0, float(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v) + 1e-9))))))
    out = {}
    for (k, d), (_, _, x, hx, _, lo) in core.items():
        for (k2, e), (y, hy, _, _, li, _) in core.items():
            g = y - x
            gap = float(np.linalg.norm(g))
            if k2 == k or gap > SEAM_GAP or ang(hx, hy) > SEAM_DEG or (gap > 50 and (ang(hx, g) > SEAM_DEG or ang(g, hy) > SEAM_DEG)):
                continue
            out[(k, d, k2, e)] = gap - lo - li
    return out


def segments(M):
    seg = {}
    for k, C in M["cl"].items():
        p = C["geo"]["path"]
        seg[k] = (tuple(p[0]), tuple(p[-1]), float(np.sum(np.linalg.norm(np.diff(p, axis=0), axis=1))))
    return seg


def tour(M, kind):
    """Team 1's legs: [(cluster, start, end, enter, leave)], return time."""
    seg, bs = segments(M), M["bs"]
    ks = sorted(seg)
    K = len(ks)
    Lh = {k: l3hat(M["cl"][k]) for k in ks}
    st = lambda k, d: seg[k][0] if d == 0 else seg[k][1]
    en = lambda k, d: seg[k][1] if d == 0 else seg[k][0]
    if kind in ("latency", "seam") or K > 12:
        # latency (CLAUDE.md §8 item 114): least sum_k n_k leave_k, n_k the critical cells of cluster k, i.e. the
        # mean time a critical cell is left behind; exact Held-Karp up to 12 segments, else tour_heur (as for short
        # and l3first beyond 12 segments). seam (item 116): latency with the seamless junctions of seams()
        n = {k: len(M["cl"][k]["P"]["crit"]) for k in ks} if kind in ("latency", "seam") else None
        link = seams(M) if kind == "seam" else {}
        order = latency_order(bs, seg, n, link) if n and K <= 12 else order_segments(bs, seg, n, link)
        legs, t, pos, prev = [], 0.0, bs, None
        for k, d in order:
            t += link.get((*prev, k, d), math.dist(pos, st(k, d))) / V1 if prev else math.dist(pos, st(k, d)) / V1
            prev = (k, d)
            t0 = t
            t += seg[k][2] / V1
            legs.append((k, st(k, d), en(k, d), t0, t))
            pos = en(k, d)
        return legs, t + math.dist(pos, bs) / V1
    # Pareto Held-Karp: (mask, i, d) -> list of (time at leaving i, readiness so far, previous state, index)
    best = {}
    for i, k in enumerate(ks):
        for d in (0, 1):
            T = (math.dist(bs, st(k, d)) + seg[k][2]) / V1
            best[(1 << i, i, d)] = [(T, T + Lh[k], None)]
    for mask in range(1, 1 << K):
        for i in range(K):
            for d in (0, 1):
                for T, R, _ in best.get((mask, i, d), []):
                    for j in range(K):
                        if mask >> j & 1:
                            continue
                        for e in (0, 1):
                            T2 = T + (math.dist(en(ks[i], d), st(ks[j], e)) + seg[ks[j]][2]) / V1
                            R2 = max(R, T2 + Lh[ks[j]])
                            key = (mask | 1 << j, j, e)
                            if kind == "short":
                                R2 = 0.0   # time only
                            L = best.setdefault(key, [])
                            if any(t <= T2 and r <= R2 for t, r, _ in L):
                                continue
                            L[:] = [x for x in L if not (T2 <= x[0] and R2 <= x[1])]
                            L.append((T2, R2, (mask, i, d, T, R)))
    full = (1 << K) - 1
    cands = [(R, T + math.dist(en(ks[i], d), bs) / V1, (full, i, d, T, R))
             for i in range(K) for d in (0, 1) for T, R, _ in best[(full, i, d)]]
    if kind == "short":
        cands = [(b, b, s) for _, b, s in cands]
    _, back, s = min(cands)
    order = []
    while s:
        mask, i, d, T, R = s
        order.append((ks[i], d))
        s = next(p for t, r, p in best[(mask, i, d)] if t == T and r == R)
    order.reverse()
    legs, t, pos = [], 0.0, bs
    for k, d in order:
        t += math.dist(pos, st(k, d)) / V1
        t0 = t
        t += seg[k][2] / V1
        legs.append((k, st(k, d), en(k, d), t0, t))
        pos = en(k, d)
    return legs, t + math.dist(pos, bs) / V1


def latency_order(bs, seg, n, link=None):
    """Exact Held-Karp for the least sum_k n_k * (metres flown until leaving segment k): a leg adds its length
    times the weight of the segments not yet left, so the value of a state does not depend on how it was reached.
    link: transits that replace the straight one (seams)."""
    link = link or {}
    ks = sorted(seg)
    K = len(ks)
    st = lambda k, d: seg[k][0] if d == 0 else seg[k][1]
    en = lambda k, d: seg[k][1] if d == 0 else seg[k][0]
    W = sum(n.values())
    best = {}
    for i, k in enumerate(ks):
        for d in (0, 1):
            best[(1 << i, i, d)] = ((math.dist(bs, st(k, d)) + seg[k][2]) * W, None)
    for mask in range(1, 1 << K):
        left = W - sum(n[ks[j]] for j in range(K) if mask >> j & 1)
        for i in range(K):
            for d in (0, 1):
                if (mask, i, d) not in best:
                    continue
                v0 = best[(mask, i, d)][0]
                for j in range(K):
                    if mask >> j & 1:
                        continue
                    for e in (0, 1):
                        gap = link.get((ks[i], d, ks[j], e), math.dist(en(ks[i], d), st(ks[j], e)))
                        v = v0 + (gap + seg[ks[j]][2]) * left
                        key = (mask | 1 << j, j, e)
                        if key not in best or v < best[key][0]:
                            best[key] = (v, (mask, i, d))
    full = (1 << K) - 1
    s = min(((full, i, d) for i in range(K) for d in (0, 1)), key=lambda x: best[x][0])
    order = []
    while s:
        order.append((ks[s[1]], s[2]))
        s = best[s][1]
    return order[::-1]


def open_tsp_first(pos, pts, bs):
    """First stop of the shortest open tour pos -> all pts -> BS."""
    best = min(itertools.permutations(range(len(pts))),
               key=lambda o: sum(math.dist(u, v) for u, v in zip([pos] + [pts[i] for i in o], [pts[i] for i in o] + [bs])))
    return best[0]


def run(M, legs, draw, policy, match=MATCH):
    """One mission. draw: dict(true, false, score, phase). Returns metrics and the trace of team 2."""
    _, dep_kind, order = policy
    bs = M["bs"]
    leave = {k: lv for k, _, _, _, lv in legs}
    # reports: per cluster CH LoRa slots
    arrive = {}   # (k, h) -> time its result reaches the BS
    for k, C in M["cl"].items():
        ch = C["P"]["ch"]
        atch = {h: leave[k] + float(C["res"]["rf"][h]["doneS"]) + match + HOP * hexdist(h, ch) for h in C["P"]["crit"]}
        ph = draw["phase"][k]
        for h, t in atch.items():
            n = max(0, math.ceil((t - ph) / GAP))
            arrive[(k, h)] = ph + n * GAP + AIR
    sus = [draw["true"]] + draw["false"]
    pts = {x: M["cl"][x[0]]["geo"]["c"][x[1]] for x in sus}
    known_at = {x: arrive[x] for x in sus}
    all_in = max(arrive.values())
    dep = all_in if dep_kind == "wait" else min(known_at.values())
    t, pos, done, trace = dep, bs, set(), [("dep", dep, bs)]
    if dep_kind == "wait" and order == "tsp":   # the original: one closed tour, shorter first leg
        o = min(itertools.permutations(sus), key=lambda o: sum(
            math.dist(u, v) for u, v in zip([bs] + [pts[x] for x in o], [pts[x] for x in o] + [bs])))
        o = list(o) if math.dist(bs, pts[o[0]]) <= math.dist(bs, pts[o[-1]]) else list(o)[::-1]
    while True:
        known = [x for x in sus if known_at[x] <= t and x not in done]
        if not known:
            t = min(known_at[x] for x in sus if x not in done)
            trace.append(("wait", t, pos))
            continue
        if dep_kind == "wait" and order == "tsp":
            nxt = next(x for x in o if x not in done)
        elif order == "tsp":
            nxt = known[open_tsp_first(pos, [pts[x] for x in known], bs)]
        else:
            nxt = max(known, key=lambda x: (draw["score"][x] / (math.dist(pos, pts[x]) / V2 + HOVER), -math.dist(pos, pts[x])))
        t += math.dist(pos, pts[nxt]) / V2
        trace.append(("visit", t, pts[nxt], nxt))
        t += HOVER
        pos = pts[nxt]
        done.add(nxt)
        if nxt == draw["true"]:
            found = t
            t += math.dist(pos, bs) / V2
            trace.append(("back", t, bs))
            return dict(dep=dep, found=found, end=t, visits=len(done), allIn=all_in,
                        trueIn=known_at[draw["true"]]), trace


def draws(M, n, seed):
    rng = random.Random(seed)
    crits = [(k, h) for k in sorted(M["cl"]) for h in M["cl"][k]["P"]["crit"]]
    out = []
    for _ in range(n):
        true = rng.choice(crits)
        false = rng.sample([x for x in crits if x != true], rng.choice((2, 3)))
        score = {true: rng.uniform(*S_TRUE)} | {x: rng.uniform(*S_FALSE) for x in false}
        phase = {k: rng.uniform(0, GAP) for k in M["cl"]}
        out.append(dict(true=true, false=false, score=score, phase=phase))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--works", required=True, help="glob of mission.py work folders")
    ap.add_argument("--draws", type=int, default=100)
    ap.add_argument("--figs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--example", default="", help="work folder drawn in policy-example.png")
    a = ap.parse_args()
    complete = lambda w: os.path.exists(f"{w}/map.json") and all(
        os.path.exists(f"{w}/r{k}-rf-crit.csv") for k in range(1, json.load(open(f"{w}/map.json"))["clusters"] + 1))
    works = sorted(w for g in a.works.split(",") for w in glob.glob(g) if complete(w))
    rows = []
    for wi, w in enumerate(works):
        M = load_map(w, schemes=("rf",))
        size = len(M["cl"])
        tours = {t: tour(M, t) for t in ("short", "l3first")}
        Ds = draws(M, a.draws, 7919 * (wi + 1))
        for di, D in enumerate(Ds):
            for pol in POLICIES:
                r, _ = run(M, tours[pol[0]][0], D, pol)
                rows.append(dict(map=os.path.basename(w), size=size, draw=di, tour=pol[0], depart=pol[1], order=pol[2],
                                 team1=f"{tours[pol[0]][1]:.1f}", **{k: f"{v:.1f}" if isinstance(v, float) else v
                                                                      for k, v in r.items()}))
        print(f"{os.path.basename(w)}: {size} clusters; team 1 short {tours['short'][1]:.0f} s, l3first "
              f"{tours['l3first'][1]:.0f} s", flush=True)
    with open(a.out + "-draws.csv", "w", newline="") as f:
        w_ = csv.DictWriter(f, fieldnames=list(rows[0]))
        w_.writeheader()
        w_.writerows(rows)
    # ---- summary: per size and policy, mean and 95 % CI of the mission end; paired change against the baseline
    base = ("short", "wait", "tsp")
    key = lambda r: (r["map"], r["draw"])
    end = {(r["size"], (r["tour"], r["depart"], r["order"]), key(r)): float(r["end"]) for r in rows}
    sizes = sorted({r["size"] for r in rows})
    summ = []
    print("\nmission end, s: mean [95 % CI]; paired change against short/wait/tsp; share of draws better")
    for s_ in sizes:
        maps = sorted({r["map"] for r in rows if r["size"] == s_})
        ids = sorted({key(r) for r in rows if r["size"] == s_})
        b = np.array([end[(s_, base, i)] for i in ids])
        for pol in POLICIES:
            x = np.array([end[(s_, pol, i)] for i in ids])
            d = x - b
            ci = 1.96 * x.std(ddof=1) / math.sqrt(len(x))
            dci = 1.96 * d.std(ddof=1) / math.sqrt(len(d))
            # map-level: the mean change per map, then across maps (maps are the independent ns-3 samples)
            per_map = [np.mean([end[(s_, pol, i)] - end[(s_, base, i)] for i in ids if i[0] == m]) for m in maps]
            summ.append(dict(size=s_, maps=len(maps), n=len(x), tour=pol[0], depart=pol[1], order=pol[2],
                             mean=f"{x.mean():.1f}", ci=f"{ci:.1f}", p50=f"{np.median(x):.1f}",
                             p90=f"{np.percentile(x, 90):.1f}", dmean=f"{d.mean():.1f}", dci=f"{dci:.1f}",
                             better=f"{np.mean(d < -1e-9):.3f}", worse=f"{np.mean(d > 1e-9):.3f}",
                             mapsBetter=sum(v < 0 for v in per_map)))
            print(f"  {s_} clusters ({len(maps)} maps, {len(x)} draws) {'/'.join(pol):22s} {x.mean():7.1f} [±{ci:5.1f}]"
                  f"  p90 {np.percentile(x, 90):7.1f}  change {d.mean():+7.1f} [±{dci:4.1f}]  better {np.mean(d < -1e-9):.0%}"
                  f"  maps better {sum(v < 0 for v in per_map)}/{len(maps)}")
    with open(a.out + "-summary.csv", "w", newline="") as f:
        w_ = csv.DictWriter(f, fieldnames=list(summ[0]))
        w_.writeheader()
        w_.writerows(summ)
    # ---- figure: mission end per size, one marker per policy (mean, 95 % CI)
    cols = ["#52514e", "#86b6ef", "#1baf7a", "#eda100", "#8e5ad6", "#3987e5", "#0d366b", "#e34948"]
    fig, ax = plt.subplots(figsize=(10, 5), dpi=150, facecolor=SURF)
    for i, pol in enumerate(POLICIES):
        for j, s_ in enumerate(sizes):
            r = next(x for x in summ if x["size"] == s_ and (x["tour"], x["depart"], x["order"]) == pol)
            xpos = j + (i - 3.5) * 0.09
            ax.errorbar(xpos, float(r["mean"]), yerr=float(r["ci"]), fmt="o", color=cols[i], ms=6, capsize=2, lw=1.2)
    ax.set_xticks(range(len(sizes)))
    ax.set_xlim(-.6, len(sizes) - .4)
    ax.set_ylim(0, None)
    ax.grid(axis="y", color=GREY, lw=.6)
    ax.set_yticks(np.arange(0, ax.get_ylim()[1], 300))
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.set_facecolor(SURF)
    strip_text(fig)
    fig.savefig(os.path.join(a.figs, "policy-end.png"), facecolor=SURF, bbox_inches="tight", pad_inches=.06)
    plt.close(fig)
    # ---- figure: one map, one draw, baseline (left) vs short/early/score... (right): team 2 paths and timelines
    if a.example:
        M = load_map(a.example, schemes=("rf",))
        D = draws(M, 1, 12345)[0]
        fig, axs = plt.subplots(1, 2, figsize=(11, 6.4), dpi=150, facecolor=SURF)
        for ax, pol in zip(axs, (base, ("l3first", "early", "score"))):
            legs = tour(M, pol[0])[0]
            r, tr = run(M, legs, D, pol)
            land(ax, M)
            crit_marks(ax, M)
            for x in [D["true"]] + D["false"]:
                ax.scatter(*M["cl"][x[0]]["geo"]["c"][x[1]], s=120 + 400 * D["score"][x], marker="o",
                           color=TRUE if x == D["true"] else FALSE, edgecolors=INK, lw=1, zorder=9)
            P = [M["bs"]] + [e[2] for e in tr if e[0] in ("visit", "back")]
            ax.plot(*np.array(P).T, color=TRUE, lw=2, zorder=10)
            frame(ax, M)
            print(f"example {os.path.basename(a.example)} {'/'.join(pol)}: departs {r['dep']:.0f} s, true found "
                  f"{r['found']:.0f} s after {r['visits']} visit(s), ends {r['end']:.0f} s; all reports in "
                  f"{r['allIn']:.0f} s, true report in {r['trueIn']:.0f} s")
        strip_text(fig)
        fig.savefig(os.path.join(a.figs, "policy-example.png"), facecolor=SURF, bbox_inches="tight", pad_inches=.06)
        plt.close(fig)


if __name__ == "__main__":
    main()
