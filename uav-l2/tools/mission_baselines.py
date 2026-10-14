"""Baselines for the whole mission (CLAUDE.md §8 items 72-73); figures without text (item 63).

    python3 tools/mission_baselines.py --works "W/k*" --draws 100 --figs docs/figures --out docs/data/mission/base

Verification (team 2, every method): the rotary UAV hovers over the suspect's critical cell at 100 m, settles
SETTLE s, sends the large file BIG bytes by unicast over 802.15.4 to the cell's CL, the cell matches (MATCH s);
then it knows. Unicast with ACK, one sender, no contention: per 99 B frame CSMA backoff (BE 3, mean 1.12 ms),
CCA and turnaround 0.32 ms, frame 4.26 ms, ACK 0.54 ms, LIFS 0.64 ms = UC_FRAME s. At 100 m above the CL the
link has 30 dB of margin, so losses are neglected. Broadcast (multicast) sends one frame per BC_FRAME = 10 ms as
the pass does, without ACK; a group finishes when its worst receiver has the file: frames / (1 - PER_worst)
(an ideal fountain code). PER: the A2G model of item 2 (free space to 100 m, then alpha 3; +10 dBm,
sensitivity -100 dBm; Nakagami m 1.8 per frame), from the hover point to each receiving CL.
Light file = the map's mean |D| frames (what one River carries, item 72).

Methods (one rotary UAV per team, V2 = 15 m/s; same draws of suspects, scores and LoRa phases everywhere):
  P    proposed: fixed wing + River (ns-3) + LoRa at the CH + team 2 l3first/early/score (mission_policy.py)
  B1   no phase 1: one UAV visits every critical cell (TSP, nearest neighbour + 2-opt), unicasts the large file,
       waits for the match there; it returns once the true cell is matched
  B2r  no phase 1: critical cells grouped within r m of a hover point (greedy cover); the UAV multicasts the large
       file at each group, waits for the matches; returns at the group with the true cell
  B3r  phase 1 by a rotary UAV multicasting the light file over the same groups; each cell matches and reports
       through its CH's LoRa; team 2 (a second UAV) as in P
  B6   B3 with one group per critical cell and unicast (the UAV hovers over each critical cell)
  B4t  P without cooperation: a critical cell matches what its cell holds after the pass (load_map's held: the
       share of D any node of the cell received, gathered in the cell by ns-3 gatherDoneS); placeholder layer-1 model: the true cell detects only if it holds >= t of D, else the
       mission fails (team 2 visits every reported suspect and returns)
  B7   oracle: team 2 flies straight to the true cell at t = 0, verifies and returns (a lower bound)
Writes OUT-draws.csv, OUT-summary.csv and FIGS/base-end.png, FIGS/base-paths.png.
"""
import argparse, csv, glob, json, math, os, random, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from map_gen import strip_text
from mission_report import FALSE, GREY, INK, INK2, SURF, TRUE, crit_marks, frame, land, load_map
import mission_policy as MP

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uav-coop2/tools"))
from river_plan import hexdist  # noqa: E402

V2, MATCH, SETTLE, BIG = 15.0, 5.0, 5.0, 1 << 20
PAYLOAD, UC_FRAME, BC_FRAME = 99, 6.88e-3, 10e-3
H, ALPHA, PTX, SENS, M_NAK, LAMBDA = 100.0, 3.0, 10.0, -100.0, 1.8, 3e8 / 2.4e9
RADII = (300, 500)
THETAS = (0.85, 0.9, 0.95)


def gammainc(a, x):
    """Regularised lower incomplete gamma P(a, x) (series; x small enough here)."""
    if x <= 0:
        return 0.0
    term = s = 1.0 / a
    n = 0
    while abs(term) > 1e-12 * abs(s) and n < 500:
        n += 1
        term *= x / (a + n)
        s += term
    return min(1.0, s * math.exp(-x + a * math.log(x) - math.lgamma(a)))


def per(ground):
    d = math.hypot(ground, H)
    loss = 20 * math.log10(4 * math.pi * min(d, H) / LAMBDA) + (10 * ALPHA * math.log10(d / H) if d > H else 0)
    x = 10 ** ((SENS - (PTX - loss)) / 10)   # fade power below which the frame is lost (unit mean)
    return gammainc(M_NAK, M_NAK * x)


def frames(nbytes):
    return math.ceil(nbytes / PAYLOAD)


T_BIG_UC = frames(BIG) * UC_FRAME
VERIFY = SETTLE + T_BIG_UC + MATCH


def tsp_order(start, pts):
    """Closed tour start -> pts -> start: nearest neighbour then 2-opt; returns the order of pts."""
    n = len(pts)
    left, o, pos = set(range(n)), [], start
    while left:
        j = min(left, key=lambda i: math.dist(pos, pts[i]))
        o.append(j)
        left.remove(j)
        pos = pts[j]
    P = [start] + [pts[i] for i in o] + [start]
    better = True
    while better:
        better = False
        for i in range(1, len(P) - 2):
            for j in range(i + 1, len(P) - 1):
                if math.dist(P[i - 1], P[j]) + math.dist(P[i], P[j + 1]) < math.dist(P[i - 1], P[i]) + math.dist(P[j], P[j + 1]) - 1e-9:
                    P[i:j + 1] = P[i:j + 1][::-1]
                    o[i - 1:j] = o[i - 1:j][::-1]
                    better = True
    return o if math.dist(start, pts[o[0]]) <= math.dist(start, pts[o[-1]]) else o[::-1]


def groups(cl, r):
    """Greedy cover of the critical CLs by disks of radius r centred on a critical CL; hover point = centroid."""
    left, out = set(cl), []
    while left:
        c = max(sorted(left), key=lambda a: sum(math.dist(cl[a], cl[b]) <= r for b in left))
        mem = [b for b in left if math.dist(cl[c], cl[b]) <= r]
        hp = tuple(np.mean([cl[b] for b in mem], axis=0))
        if any(math.dist(hp, cl[b]) > r for b in mem):
            hp = cl[c]
        out.append((hp, mem))
        left -= set(mem)
    return out


def tour_visits(bs, stops, cost, stop_when):
    """Fly bs -> stops in TSP order, spending cost(stop) at each; return (time found, end, visits, path)."""
    o = tsp_order(bs, [s[0] for s in stops])
    t, pos, path = 0.0, bs, [bs]
    for n, i in enumerate(o):
        t += math.dist(pos, stops[i][0]) / V2 + cost(stops[i])
        pos = stops[i][0]
        path.append(pos)
        if stop_when(stops[i]):
            path.append(bs)
            return t, t + math.dist(pos, bs) / V2, n + 1, path
    raise AssertionError("true cell not on the tour")


def lora_arrival(M, draw, ready):
    """ready: {(k, h): time the result is at the critical cell} -> {(k, h): time at the BS} via the CH's LoRa."""
    out = {}
    for (k, h), t in ready.items():
        ch = M["cl"][k]["P"]["ch"]
        at = t + MP.HOP * hexdist(h, ch)
        ph = draw["phase"][k]
        out[(k, h)] = ph + max(0, math.ceil((at - ph) / MP.GAP)) * MP.GAP + MP.AIR
    return out


def team2(M, draw, known_at, verify):
    """Team 2 as in P (early, score), from given report arrival times at the BS."""
    bs = M["bs"]
    sus = [draw["true"]] + draw["false"]
    pts = {x: M["cl"][x[0]]["geo"]["c"][x[1]] for x in sus}
    t = min(known_at[x] for x in sus)
    dep, pos, done = t, bs, set()
    while True:
        known = [x for x in sus if known_at[x] <= t and x not in done]
        if not known:
            t = min(known_at[x] for x in sus if x not in done)
            continue
        nxt = max(known, key=lambda x: (draw["score"][x] / (math.dist(pos, pts[x]) / V2 + verify), -math.dist(pos, pts[x])))
        t += math.dist(pos, pts[nxt]) / V2 + verify
        pos = pts[nxt]
        done.add(nxt)
        if nxt == draw["true"]:
            return dep, t, t + math.dist(pos, bs) / V2, len(done)


def methods(M, legs, D, light):
    """Every method on one draw: {name: (end, found, ok, visits)}."""
    bs = M["bs"]
    crits = [(k, h) for k in sorted(M["cl"]) for h in M["cl"][k]["P"]["crit"]]
    cl = {}
    for k, C in M["cl"].items():
        for n in C["geo"]["nodes"]:
            x = (k, (int(n["q"]), int(n["r"])))
            if n["isCL"] == "1" and x in crits:
                cl[x] = (float(n["x"]), float(n["y"]))
    out = {}
    # P
    MP.HOVER = VERIFY
    r, _ = MP.run(M, legs, D, ("l3first", "early", "score"))
    out["P"] = (r["end"], r["found"], 1, r["visits"])
    # B7 oracle
    d = math.dist(bs, cl[D["true"]])
    out["B7"] = (2 * d / V2 + VERIFY, d / V2 + VERIFY, 1, 1)
    # B1
    f, e, n, _ = tour_visits(bs, [(cl[x], x) for x in crits], lambda s: VERIFY, lambda s: s[1] == D["true"])
    out["B1"] = (e, f, 1, n)
    for rr in RADII:
        G = groups(cl, rr)
        cost_big = lambda g: SETTLE + frames(BIG) * BC_FRAME / (1 - max(per(math.dist(g[0], cl[b])) for b in g[1])) + MATCH
        f, e, n, _ = tour_visits(bs, G, cost_big, lambda g: D["true"] in g[1])
        out[f"B2-{rr}"] = (e, f, 1, n)
        # B3: light file over the same groups, then LoRa and team 2
        t, pos, ready = 0.0, bs, {}
        for i in tsp_order(bs, [g[0] for g in G]):
            hp, mem = G[i]
            t += math.dist(pos, hp) / V2 + SETTLE + frames(light) * BC_FRAME / (1 - max(per(math.dist(hp, cl[b])) for b in mem))
            for b in mem:
                ready[b] = t + MATCH
            pos = hp
        dep, found, end, nv = team2(M, D, lora_arrival(M, D, ready), VERIFY)
        out[f"B3-{rr}"] = (end, found, 1, nv)
    # B6: unicast light file per critical cell
    t, pos, ready = 0.0, bs, {}
    for i in tsp_order(bs, [cl[x] for x in crits]):
        x = crits[i]
        t += math.dist(pos, cl[x]) / V2 + SETTLE + frames(light) * UC_FRAME
        ready[x] = t + MATCH
        pos = cl[x]
    dep, found, end, nv = team2(M, D, lora_arrival(M, D, ready), VERIFY)
    out["B6"] = (end, found, 1, nv)
    # B4: no cooperation
    leave = {l[0]: l[4] for l in legs}
    ready = {(k, h): leave[k] + float(M["cl"][k]["res"]["rf"][h]["gatherDoneS"]) + MATCH for k, h in crits}
    arr = lora_arrival(M, D, ready)
    for th in THETAS:
        ok = M["cl"][D["true"][0]]["held"][D["true"][1]] >= th
        if ok:
            dep, found, end, nv = team2(M, D, arr, VERIFY)
            out[f"B4-{th}"] = (end, found, 1, nv)
        else:   # the true cell reports nothing: team 2 checks every false suspect and gives up
            fs = D["false"]
            pts = [M["cl"][x[0]]["geo"]["c"][x[1]] for x in fs]
            t = min(arr[x] for x in fs)
            o = tsp_order(bs, pts)
            P_ = [bs] + [pts[i] for i in o] + [bs]
            end = max(t, max(arr[x] for x in fs)) + sum(math.dist(a, b) for a, b in zip(P_, P_[1:])) / V2 + len(fs) * VERIFY
            out[f"B4-{th}"] = (end, float("nan"), 0, len(fs))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--works", required=True)
    ap.add_argument("--draws", type=int, default=100)
    ap.add_argument("--figs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--example", default="")
    a = ap.parse_args()
    complete = lambda w: os.path.exists(f"{w}/map.json") and all(
        os.path.exists(f"{w}/r{k}-rf-crit.csv") for k in range(1, json.load(open(f"{w}/map.json"))["clusters"] + 1))
    works = sorted(w for g in a.works.split(",") for w in glob.glob(g) if complete(w))
    print(f"large file {BIG / 1e6:.2f} MB: unicast {T_BIG_UC:.0f} s, broadcast {frames(BIG) * BC_FRAME:.0f} s; "
          f"verification {VERIFY:.0f} s; PER at 0/300/500/800 m: " +
          " / ".join(f"{per(g):.3f}" for g in (0, 300, 500, 800)))
    rows = []
    for wi, w in enumerate(works):
        M = load_map(w, schemes=("rf",))
        light = round(np.mean([C["D"] for C in M["cl"].values()])) * PAYLOAD
        legs = MP.tour(M, "l3first")[0]
        for di, D in enumerate(MP.draws(M, a.draws, 7919 * (wi + 1))):   # the same draws as mission_policy.py
            for name, (end, found, ok, nv) in methods(M, legs, D, light).items():
                rows.append(dict(map=os.path.basename(w), size=len(M["cl"]), draw=di, method=name, end=round(end, 1),
                                 found=round(found, 1) if ok else "", ok=ok, visits=nv))
        print(f"{os.path.basename(w)}: {len(M['cl'])} clusters, light file {light / 1e6:.2f} MB", flush=True)
    with open(a.out + "-draws.csv", "w", newline="") as f:
        w_ = csv.DictWriter(f, fieldnames=list(rows[0]))
        w_.writeheader()
        w_.writerows(rows)
    names = list(dict.fromkeys(r["method"] for r in rows))
    sizes = sorted({r["size"] for r in rows})
    summ = []
    print("\nmission end, s: mean [95 % CI] over draws whose true cell was found; success rate; change against P")
    for s_ in sizes:
        R = [r for r in rows if r["size"] == s_]
        P = {(r["map"], r["draw"]): r["end"] for r in R if r["method"] == "P"}
        maps = sorted({r["map"] for r in R})
        for m in names:
            X = [r for r in R if r["method"] == m]
            okx = np.array([r["end"] for r in X if r["ok"]])
            d = np.array([r["end"] - P[(r["map"], r["draw"])] for r in X if r["ok"]])
            per_map = [np.mean([r["end"] - P[(r["map"], r["draw"])] for r in X if r["map"] == mp and r["ok"]] or [0]) for mp in maps]
            summ.append(dict(size=s_, method=m, n=len(X), success=round(np.mean([r["ok"] for r in X]), 3),
                             mean=round(okx.mean(), 1), ci=round(1.96 * okx.std(ddof=1) / math.sqrt(len(okx)), 1),
                             p90=round(np.percentile(okx, 90), 1), dP=round(d.mean(), 1),
                             visits=round(np.mean([r["visits"] for r in X]), 2), mapsWorseThanP=sum(v > 0 for v in per_map)))
            print(f"  {s_} clusters  {m:8s} {okx.mean():7.1f} [±{summ[-1]['ci']:5.1f}]  success {summ[-1]['success']:.0%}"
                  f"  vs P {d.mean():+8.1f}  visits {summ[-1]['visits']:.2f}  maps slower than P {summ[-1]['mapsWorseThanP']}/{len(maps)}")
    with open(a.out + "-summary.csv", "w", newline="") as f:
        w_ = csv.DictWriter(f, fieldnames=list(summ[0]))
        w_.writeheader()
        w_.writerows(summ)
    # ---- figure: mission end per size and method (mean, 95 % CI), methods in a fixed colour order
    cols = {"P": "#e34948", "B7": "#0b0b0b", "B1": "#52514e", "B2-300": "#86b6ef", "B2-500": "#3987e5",
            "B3-300": "#9fd8bf", "B3-500": "#1baf7a", "B6": "#eda100", "B4-0.85": "#c9b3ef", "B4-0.9": "#8e5ad6",
            "B4-0.95": "#5b2fa3"}
    fig, ax = plt.subplots(figsize=(12, 5), dpi=150, facecolor=SURF)
    for i, m in enumerate(names):
        for j, s_ in enumerate(sizes):
            r = next(x for x in summ if x["size"] == s_ and x["method"] == m)
            ax.errorbar(j + (i - (len(names) - 1) / 2) * 0.075, r["mean"], yerr=r["ci"], fmt="o", ms=5, capsize=2,
                        color=cols.get(m, INK2), lw=1.2)
    ax.set_yscale("log")
    ax.set_xticks(range(len(sizes)))
    ax.grid(axis="y", color=GREY, lw=.6, which="both")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.set_facecolor(SURF)
    ax.tick_params(which="both", labelleft=False, labelbottom=False)   # log axes label minor ticks too
    strip_text(fig)
    fig.savefig(os.path.join(a.figs, "base-end.png"), facecolor=SURF, bbox_inches="tight", pad_inches=.06)
    plt.close(fig)
    # ---- figure: one map, the UAV paths of B1, B2-500, B3-500 + team 2, P
    if a.example:
        M = load_map(a.example, schemes=("rf",))
        D = MP.draws(M, 1, 12345)[0]
        crits = [(k, h) for k in sorted(M["cl"]) for h in M["cl"][k]["P"]["crit"]]
        cl = {(k, (int(n["q"]), int(n["r"]))): (float(n["x"]), float(n["y"])) for k, C in M["cl"].items()
              for n in C["geo"]["nodes"] if n["isCL"] == "1"}
        cl = {x: cl[x] for x in crits}
        fig, axs = plt.subplots(1, 3, figsize=(16, 6.4), dpi=150, facecolor=SURF)
        G = groups(cl, 500)
        paths = [tour_visits(M["bs"], [(cl[x], x) for x in crits], lambda s: 0, lambda s: s[1] == D["true"])[3],
                 tour_visits(M["bs"], G, lambda g: 0, lambda g: D["true"] in g[1])[3],
                 [M["bs"]] + [G[i][0] for i in tsp_order(M["bs"], [g[0] for g in G])] + [M["bs"]]]
        for i, (ax, path) in enumerate(zip(axs, paths)):
            land(ax, M)
            crit_marks(ax, M)
            if i > 0:
                for hp, mem in G:
                    ax.add_patch(plt.Circle(hp, 500, facecolor="#3987e5", alpha=.12, edgecolor="#3987e5", lw=.8, zorder=4))
            ax.scatter(*cl[D["true"]], s=220, color=TRUE, edgecolors=INK, zorder=9)
            ax.plot(*np.array(path).T, color=INK, lw=1.8, zorder=10)
            frame(ax, M)
        strip_text(fig)
        fig.savefig(os.path.join(a.figs, "base-paths.png"), facecolor=SURF, bbox_inches="tight", pad_inches=.06)
        plt.close(fig)


if __name__ == "__main__":
    main()
