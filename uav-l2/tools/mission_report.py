"""Stage 6 of the mission (CLAUDE.md §8 item 68): matching, suspects, team 2; figures without text (item 63).

    python3 tools/mission_report.py --works W2,W4,... --figs docs/figures --out docs/data/mission

Per map (a mission.py work folder):
  River       critical cell c of cluster k holds all of D_k at  leave_k + done_c  (ns-3, per scheme)
  matching    starts then and takes MATCH s (a placeholder for layer 1)
  report      each critical cell sends a few bytes to the BS over LoRa: airtime 0.4 s plus a wait for its
              duty cycle, uniform in [0, LORA] s (drawn once per cell, the same for every scheme)
  suspects    one critical cell of the whole map is the true suspect, 2 or 3 others false ones (drawn once
              per map); all other critical cells report nothing found
  team 2      one rotary-wing UAV, V2 m/s, leaves the BS once every critical cell has reported; it visits the
              suspects along the shortest closed tour BS -> suspects -> BS (exact, no turn radius), the
              direction with the shorter first leg; HOVER s to verify each; at the true one it flies
              straight back to the BS and the mission ends
              (also given: the mission end averaged over every suspect being the true one, same tour)
Writes OUT-summary.csv (one row per map and scheme), OUT-cells.csv (per critical cell) and figures
FIGS/mission-{maps,pass,river,suspects,timeline}.png, one panel per map.
"""
import argparse, csv, itertools, json, math, os, random, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.patches import FancyArrowPatch
import numpy as np

from map_gen import W, cell_at, centre, corners, strip_text

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uav-coop2/tools"))
from river_plan import plan  # noqa: E402

MATCH, LORA, AIR, V2, HOVER = 5.0, 30.0, 0.4, 15.0, 30.0
SCHEMES = ("rf", "ad12", "d")
INK, INK2, SURF, GREY = "#0b0b0b", "#52514e", "#fcfcfb", "#e6e5e1"
RIVER, BANK, AXE, WATER = "#c9dcf3", "#9fd8bf", "#1c5cab", "#3987e5"
CAT = ["#1c5cab", "#1baf7a", "#eda100", "#8e5ad6", "#0d366b", "#52514e", "#e34948", "#86b6ef", "#b07a2a"]
TRUE, FALSE = "#e34948", "#eda100"


def load_map(w, schemes=SCHEMES):
    m = json.load(open(f"{w}/map.json"))
    tour = json.load(open(f"{w}/tour.json"))
    rows = list(csv.DictReader(open(f"{w}/domain-cells.csv")))
    water = [(int(r["q"]), int(r["r"])) for r in rows if r["type"] != "land"]
    owner = {(int(r["q"]), int(r["r"])): int(r["cluster"]) for r in csv.DictReader(open(f"{w}/clusters.csv"))}
    cl = {}
    for k in range(1, m["clusters"] + 1):
        lat = list(csv.DictReader(open(f"{w}/c{k}-lattice.csv")))
        c = {(int(x["q"]), int(x["r"])): (float(x["cx"]), float(x["cy"])) for x in lat}
        sel = sorted((int(x["q"]), int(x["r"])) for x in lat if x["selected"] == "1")
        nodes = list(csv.DictReader(open(f"{w}/c{k}-nodes-s35.csv")))
        path = np.array([[float(q["x"]), float(q["y"])] for q in csv.DictReader(open(f"{w}/c{k}-path-s35.csv"))])
        seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))]
        d = np.arange(0, seg[-1], 0.5)
        uav = np.c_[np.interp(d, seg, path[:, 0]), np.interp(d, seg, path[:, 1])]
        geo = dict(c=c, w=W, R=W / math.sqrt(3), cells=sel, S=set(sel), nodes=nodes, path=path, uav=uav)
        res = {t: {(int(r["q"]), int(r["r"])): r for r in csv.DictReader(open(f"{w}/r{k}-{t}-crit.csv"))}
               for t in schemes}
        runs = {t: next(csv.DictReader(open(f"{w}/r{k}-{t}-runs.csv"))) for t in schemes}
        P = plan(geo)
        N = len(uav)
        bits = np.unpackbits(np.fromfile(f"{w}/pass{k}-bits-r1.bin", dtype=np.uint8).reshape(len(nodes), -1),
                             axis=1, bitorder="little")[:, :N].astype(bool)
        inD = np.zeros(N, bool)
        for x in P["axe"]:
            inD[P["seg"][x][0]:P["seg"][x][-1] + 1] = bits[:, P["seg"][x][0]:P["seg"][x][-1] + 1].any(axis=0)
        cellof = [(int(n["q"]), int(n["r"])) for n in nodes]
        mem = {}
        for i, h in enumerate(cellof):
            mem.setdefault(h, []).append(i)
        held = {h: float((bits[mem[h]].any(axis=0) & inD).sum() / inD.sum()) for h in sel}
        cl[k] = dict(geo=geo, P=P, res=res, runs=runs, held=held, D=int(inD.sum()), bits=bits, inD=inD, mem=mem)
    return dict(m=m, tour=tour, water=water, owner=owner, cl=cl, bs=tuple(m["bs"]), name=os.path.basename(w))


def tsp(bs, pts):
    """Shortest closed tour BS -> pts -> BS (exact), oriented with the shorter first leg."""
    best = min(itertools.permutations(range(len(pts))),
               key=lambda o: sum(math.dist(u, v) for u, v in zip([bs] + [pts[i] for i in o], [pts[i] for i in o] + [bs])))
    o = list(best)
    return o if math.dist(bs, pts[o[0]]) <= math.dist(bs, pts[o[-1]]) else o[::-1]


def simulate(M, seed):
    rng = random.Random(seed)
    crits = [(k, h) for k in sorted(M["cl"]) for h in M["cl"][k]["P"]["crit"]]
    wait = {x: AIR + rng.uniform(0, LORA) for x in crits}
    true = rng.choice(crits)
    false = rng.sample([x for x in crits if x != true], rng.choice((2, 3)))
    sus = [true] + false
    pts = [M["cl"][k]["geo"]["c"][h] for k, h in sus]
    order = tsp(M["bs"], pts)
    leave = {l["cluster"]: l["leave"] for l in M["tour"]["legs"]}
    out = {}
    for t in SCHEMES:
        done = {(k, h): leave[k] + float(M["cl"][k]["res"][t][h]["doneS"]) for k, h in crits}
        match = {x: done[x] + MATCH for x in crits}
        rep = {x: match[x] + wait[x] for x in crits}
        dep = max(rep.values())
        tt, pos, visits = dep, M["bs"], []
        for i in order:
            tt += math.dist(pos, pts[i]) / V2
            visits.append((sus[i], tt))
            tt += HOVER
            pos = pts[i]
            if sus[i] == true:
                break
        end = tt + math.dist(pos, M["bs"]) / V2
        ends = []   # the mission end had each suspect been the true one (same tour)
        for j in range(len(sus)):
            tj, pj = dep, M["bs"]
            for i in order:
                tj += math.dist(pj, pts[i]) / V2 + HOVER
                pj = pts[i]
                if i == j:
                    break
            ends.append(tj + math.dist(pj, M["bs"]) / V2)
        out[t] = dict(done=done, match=match, rep=rep, dep=dep, visits=visits, end=end, found=visits[-1][1],
                      endMean=sum(ends) / len(ends))
    return dict(crits=crits, true=true, false=false, sus=sus, pts=pts, order=order, wait=wait, by=out)


def panel_axes(n):
    fig, axs = plt.subplots(1, n, figsize=(5.2 * n, 6.4), dpi=150, facecolor=SURF)
    return fig, np.atleast_1d(axs)


def frame(ax, M):
    allc = list(M["owner"]) + M["water"]
    xs = [centre(h)[0] for h in allc] + [M["bs"][0]]
    ys = [centre(h)[1] for h in allc] + [M["bs"][1]]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    half = max(max(xs) - min(xs), max(ys) - min(ys)) / 2 + W
    ax.set_xlim(cx - half, cx + half); ax.set_ylim(cy - half, cy + half)
    ax.set_aspect("equal"); ax.set_facecolor(SURF); ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.plot([cx + half - W - 1000, cx + half - W], [cy - half + .4 * W] * 2, color=INK, lw=2)   # 1 km


def land(ax, M, colours=None, alpha=1.0):
    cells = list(M["owner"])
    ax.add_collection(PolyCollection([corners(h) for h in cells], alpha=alpha, edgecolors=SURF, linewidths=.3,
                                     facecolors=[(colours or {}).get(h, GREY) for h in cells], zorder=0))
    ax.add_collection(PolyCollection([corners(h) for h in M["water"]], facecolors="#dbe9f8", edgecolors=WATER,
                                     hatch="////", linewidths=0, zorder=0))
    segs = []
    for h in cells:
        v = corners(h)
        cx, cy = centre(h)
        for j in range(6):
            p, q = v[j], v[(j + 1) % 6]
            n = cell_at(p[0] + q[0] - cx, p[1] + q[1] - cy)
            if M["owner"].get(n) != M["owner"][h]:
                segs.append((p, q))
    ax.add_collection(LineCollection(segs, colors=INK, linewidths=1.2, zorder=3))
    ax.scatter(*M["bs"], s=110, marker="s", color=INK, zorder=8)


def crit_marks(ax, M, face="#ffffff"):
    for k, C in M["cl"].items():
        for h in C["P"]["crit"]:
            star = h == C["P"]["ch"]
            ax.scatter(*C["geo"]["c"][h], s=150 if star else 60, marker="*" if star else "o", color=face,
                       edgecolors=INK, lw=.9, zorder=7)


def tour_lines(ax, M, alpha=1.0):
    pos = M["bs"]
    for l in M["tour"]["legs"]:
        ax.plot([pos[0], l["start"][0]], [pos[1], l["start"][1]], color=INK, lw=1, ls=(0, (3, 2)), alpha=alpha, zorder=5)
        ax.add_patch(FancyArrowPatch(l["start"], l["end"], arrowstyle="-|>", color=INK, lw=2, alpha=alpha,
                                     mutation_scale=14, zorder=6))
        pos = l["end"]
    ax.plot([pos[0], M["bs"][0]], [pos[1], M["bs"][1]], color=INK, lw=1, ls=(0, (3, 2)), alpha=alpha, zorder=5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--works", required=True)
    ap.add_argument("--figs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    maps = [load_map(w) for w in a.works.split(",")]
    sims = [simulate(M, a.seed * 1000 + len(M["cl"])) for M in maps]
    n = len(maps)
    # ---- numbers
    with open(a.out + "-summary.csv", "w", newline="") as f, open(a.out + "-cells.csv", "w", newline="") as g:
        w, w2 = csv.writer(f), csv.writer(g)
        w.writerow(["map", "clusters", "cells", "nodes", "crit", "tour_km", "team1_back_s", "scheme", "last_done_s",
                    "team2_departs_s", "true_found_s", "mission_end_s", "mission_end_mean_s", "visits", "frames"])
        w2.writerow(["map", "cluster", "q", "r", "role", "leave_s", "lackCell", "scheme", "doneS", "done_s",
                     "report_s"])
        for M, X in zip(maps, sims):
            for t in SCHEMES:
                Y = X["by"][t]
                frames = sum(int(C["runs"][t]["hops"]) for C in M["cl"].values())
                w.writerow([M["name"], len(M["cl"]), M["m"]["cells"], M["m"]["nodes"], len(X["crits"]),
                            f"{M['tour']['length'] / 1000:.2f}", f"{M['tour']['back']:.1f}", t,
                            f"{max(Y['done'].values()):.1f}", f"{Y['dep']:.1f}", f"{Y['found']:.1f}", f"{Y['end']:.1f}",
                            f"{Y['endMean']:.1f}", len(Y["visits"]), frames])
                for k, h in X["crits"]:
                    role = "true" if (k, h) == X["true"] else "false" if (k, h) in X["false"] else ""
                    role += ("+CH" if h == M["cl"][k]["P"]["ch"] else "")
                    leave = next(l["leave"] for l in M["tour"]["legs"] if l["cluster"] == k)
                    r = M["cl"][k]["res"][t][h]
                    w2.writerow([M["name"], k, h[0], h[1], role, f"{leave:.1f}", r["lackCell"], t, r["doneS"],
                                 f"{Y['done'][(k, h)]:.1f}", f"{Y['rep'][(k, h)]:.1f}"])
    for M, X in zip(maps, sims):
        print(f"{M['name']}: {len(M['cl'])} clusters, {M['m']['cells']} cells, {M['m']['nodes']} nodes, "
              f"{len(X['crits'])} critical cells; tour {M['tour']['length'] / 1000:.1f} km, team 1 back at "
              f"{M['tour']['back']:.0f} s; true {X['true']}, false {X['false']}")
        for l in M["tour"]["legs"]:
            k = l["cluster"]
            C = M["cl"][k]
            last = {t: max(float(r["doneS"]) for r in C["res"][t].values()) for t in SCHEMES}
            print(f"   C{k}: {len(C['geo']['cells'])} cells, {len(C['geo']['nodes'])} nodes, Axe {len(C['P']['axe'])}, "
                  f"|D| {C['D']}, {len(C['P']['crit'])} critical; pass {l['enter']:.0f}-{l['leave']:.0f} s; "
                  f"last critical done after leaving: " + ", ".join(f"{t} {last[t]:.1f} s" for t in SCHEMES)
                  + "; frames: " + ", ".join(f"{t} {int(C['runs'][t]['hops'])}" for t in SCHEMES))
        for t in SCHEMES:
            Y = X["by"][t]
            print(f"   {t:5s} last critical done {max(Y['done'].values()):6.1f} s, team 2 leaves {Y['dep']:6.1f} s, "
                  f"true found {Y['found']:6.1f} s after {len(Y['visits'])} visit(s), mission ends {Y['end']:6.1f} s "
                  f"(any suspect true: {Y['endMean']:6.1f} s)")
    # ---- figure 1: map, clusters, team 1
    fig, axs = panel_axes(n)
    for ax, M in zip(axs, maps):
        land(ax, M, {h: CAT[(k - 1) % len(CAT)] for h, k in M["owner"].items()}, alpha=.35)
        tour_lines(ax, M)
        crit_marks(ax, M)
        frame(ax, M)
    strip_text(fig)
    fig.savefig(os.path.join(a.figs, "mission-maps.png"), facecolor=SURF, bbox_inches="tight", pad_inches=.06)
    plt.close(fig)
    # ---- figure 1b: after the pass, share of its cluster's D held by each cell
    ramp = matplotlib.colors.LinearSegmentedColormap.from_list("r", ["#f1f0eb", "#86b6ef", "#3987e5", "#0d366b"])
    fig, axs = panel_axes(n)
    for ax, M in zip(axs, maps):
        land(ax, M, {h: ramp(C["held"][h]) for C in M["cl"].values() for h in C["held"]})
        for C in M["cl"].values():
            ax.plot(*C["geo"]["path"].T, color=INK, lw=.9, zorder=4)
        crit_marks(ax, M)
        frame(ax, M)
        cr = [C["held"][h] for C in M["cl"].values() for h in C["P"]["crit"]]
        al = [v for C in M["cl"].values() for v in C["held"].values()]
        print(f"{M['name']} after the pass: cells hold {np.mean(al):.2f} of D on average (min {min(al):.2f}); "
              f"critical cells {np.mean(cr):.2f} (min {min(cr):.2f}); |D| per cluster "
              f"{[C['D'] for k, C in sorted(M['cl'].items())]}")
    strip_text(fig)
    fig.savefig(os.path.join(a.figs, "mission-pass.png"), facecolor=SURF, bbox_inches="tight", pad_inches=.06)
    plt.close(fig)
    # ---- figure 2: River of every cluster
    fig, axs = panel_axes(n)
    for ax, M in zip(axs, maps):
        col = {}
        for C in M["cl"].values():
            P = C["P"]
            col.update({h: RIVER for h in P["river"]})
            col.update({b: BANK for (x, s_), b in P["bank"].items() if b != x})
            col.update({h: AXE for h in P["axe"]})
        land(ax, M, col)
        for C in M["cl"].values():
            ax.plot(*C["geo"]["path"].T, color=INK, lw=.9, zorder=4)
        crit_marks(ax, M)
        frame(ax, M)
    strip_text(fig)
    fig.savefig(os.path.join(a.figs, "mission-river.png"), facecolor=SURF, bbox_inches="tight", pad_inches=.06)
    plt.close(fig)
    # ---- figure 3: suspects and team 2 (River prepared)
    fig, axs = panel_axes(n)
    for ax, M, X in zip(axs, maps, sims):
        land(ax, M)
        crit_marks(ax, M)
        for (k, h), p in zip(X["sus"], X["pts"]):
            ax.scatter(*p, s=260, marker="o", color=TRUE if (k, h) == X["true"] else FALSE, edgecolors=INK, lw=1,
                       zorder=9)
        Y = X["by"]["rf"]
        pos = M["bs"]
        for (x, _) in Y["visits"]:
            p = X["pts"][X["sus"].index(x)]
            ax.add_patch(FancyArrowPatch(pos, p, arrowstyle="-|>", color=TRUE, lw=2, mutation_scale=14, shrinkA=6,
                                         shrinkB=9, zorder=10))
            pos = p
        ax.plot([pos[0], M["bs"][0]], [pos[1], M["bs"][1]], color=TRUE, lw=1.4, ls=(0, (4, 3)), zorder=10)
        rest = [X["pts"][i] for i in X["order"][len(Y["visits"]):]]
        if rest:   # the part of the tour team 2 did not need
            ax.plot(*np.array([pos] + rest + [M["bs"]]).T, color=INK2, lw=.8, ls=(0, (1, 2)), zorder=9)
        frame(ax, M)
    strip_text(fig)
    fig.savefig(os.path.join(a.figs, "mission-suspects.png"), facecolor=SURF, bbox_inches="tight", pad_inches=.06)
    plt.close(fig)
    # ---- figure 4: timelines (River prepared); one row per cluster in tour order, then team 2
    T = max(X["by"]["rf"]["end"] for X in sims)
    fig, axs = plt.subplots(n, 1, figsize=(12, 1.2 + 0.42 * sum(len(M["cl"]) + 1 for M in maps)), dpi=150,
                            facecolor=SURF, gridspec_kw=dict(height_ratios=[len(M["cl"]) + 1 for M in maps]))
    for ax, M, X in zip(np.atleast_1d(axs), maps, sims):
        Y = X["by"]["rf"]
        for i, l in enumerate(M["tour"]["legs"]):
            y = -i
            k = l["cluster"]
            ax.barh(y, l["leave"] - l["enter"], left=l["enter"], height=.5, color=AXE, zorder=2)
            ds = [Y["done"][(kk, h)] for kk, h in X["crits"] if kk == k]
            ax.barh(y, max(ds) - l["leave"], left=l["leave"], height=.5, color=BANK, zorder=2)
            for kk, h in X["crits"]:
                if kk != k:
                    continue
                d, r = Y["done"][(kk, h)], Y["rep"][(kk, h)]
                ax.barh(y, MATCH, left=d, height=.5, color="#8e5ad6", zorder=3)
                ax.plot([d + MATCH, r], [y, y], color=INK2, lw=.8, zorder=3)
                c = TRUE if (kk, h) == X["true"] else FALSE if (kk, h) in X["false"] else "#ffffff"
                ax.scatter(r, y, s=36, color=c, edgecolors=INK, lw=.7, zorder=4)
        y = -len(M["tour"]["legs"])
        ax.barh(y, Y["found"] - Y["dep"], left=Y["dep"], height=.5, color=TRUE, zorder=2)
        for (x, tv) in Y["visits"]:
            ax.barh(y, HOVER, left=tv, height=.5, color="#ffffff", edgecolor=INK, lw=.6, zorder=3)
        ax.barh(y, Y["end"] - Y["found"] - HOVER, left=Y["found"] + HOVER, height=.5, color="#f3b9b9", zorder=2)
        ax.axvline(M["tour"]["back"], color=INK, lw=.8, ls=(0, (3, 2)))
        ax.set_xlim(0, T * 1.02)
        ax.set_ylim(y - .7, .7)
        ax.set_xticks(np.arange(0, T, 60))
        ax.grid(axis="x", color=GREY, lw=.6, zorder=0)
        ax.set_yticks([])
        ax.set_facecolor(SURF)
        for sp in ("top", "right", "left"):
            ax.spines[sp].set_visible(False)
    strip_text(fig)
    fig.savefig(os.path.join(a.figs, "mission-timeline.png"), facecolor=SURF, bbox_inches="tight", pad_inches=.06)
    plt.close(fig)
    print("figures written")


if __name__ == "__main__":
    main()
