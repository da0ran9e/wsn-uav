"""k-medoids vs LANE vs MEANDER in the whole mission, ns-3 River (CLAUDE.md §8 item 104).

    python3 tools/meander_compare.py --set kmedoids "W/k[468]" --set lane "ML/k*" --set meander "MM/k*" \
        --draws 100 --out docs/data/meander/ns3 --figs docs/figures

Each set holds mission folders (mission.py, tools/regeom.py rebuilds, or tools/meander_mission.py) of the same
maps, named k<K>. Per map and set:
  team 1    the l3first tour of mission_policy (the policy P flies), its return time and in-cluster flight
  River     prepared River, 7 colours (ns-3): per critical cell doneS; D per cluster (packets, kB of 99 B)
  ready     max over clusters of leave_k + max doneS_k: every critical cell holds its cluster's D
  mission   policy P (l3first, early departure, score order) over DRAWS draws of the suspects (mission_policy
            draws, seed 7919 K): the end time; the sets have different critical cells, so draws are not paired
Writes OUT-summary.csv, OUT-cells.csv (per critical cell), OUT-draws.csv and figures FIGS/meander-ns3-maps.png
(rows maps, columns sets) and FIGS/meander-ns3-results.png: River done mean, ready, mission end, D (kB) per
map, and a scatter of each cluster's Axe length against its slowest critical cell (no text, CLAUDE.md §8 item 63).
Set names (item 106): kmedoids, kmedoidsCurve, lane, meander, meanderSpan, each optionally +w (River window of
--windowKB around the CH: same colour, hollow marker; column short = clusters sent less than the window).
"""
import argparse, csv, glob, json, math, os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from map_gen import strip_text
from mission_policy import draws, run, tour
from mission_report import INK, SURF, GREY, frame, land, load_map

POLICY = ("l3first", "early", "score")
# categorical slots 1-5 by partition; a set NAME+w (River window, item 106) keeps its partition's colour, hollow
COL = {"kmedoids": "#2a78d6", "lane": "#eb6834", "meander": "#1baf7a", "kmedoidsCurve": "#eda100", "meanderSpan": "#e87ba4"}
MARK = {"kmedoids": "o", "lane": "s", "meander": "^", "kmedoidsCurve": "D", "meanderSpan": "v"}
base = lambda s: s.split("+")[0]
face = lambda s: SURF if s.endswith("+w") else COL[base(s)]
SEQ = ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]               # blue ramp, light -> dark


def complete(w):
    if not os.path.exists(f"{w}/map.json"):
        return False
    K = json.load(open(f"{w}/map.json"))["clusters"]
    return all(os.path.exists(f"{w}/r{k}-rf-crit.csv") for k in range(1, K + 1))


def measure(M, n, Q=0):
    legs, back = tour(M, POLICY[0])
    leave = {k: lv for k, _, _, _, lv in legs}
    cells, ready, L3, D, sent = [], 0.0, [], [], []
    for k, C in M["cl"].items():
        sent.append(sum(len(v) for v in C["P"]["seg"].values()))   # Axe packets sent, whole D (no window)
        done = {h: float(r["doneS"]) for h, r in C["res"]["rf"].items()}
        miss = {h: int(r["missing"]) for h, r in C["res"]["rf"].items()}
        D.append(int(C["runs"]["rf"]["D"]))
        L3.append(max(done.values()))
        ready = max(ready, leave[k] + max(done.values()))
        cells += [dict(cluster=k, q=h[0], r=h[1], ch=int(h == C["P"]["ch"]), axe=len(C["P"]["axe"]), D=D[-1],
                       doneS=done[h], missing=miss[h], ready=round(leave[k] + done[h], 1)) for h in C["P"]["crit"]]
    path = sum(float(np.sum(np.linalg.norm(np.diff(C["geo"]["path"], axis=0), axis=1))) for C in M["cl"].values())
    K = int(M["name"].lstrip("k"))
    ends = [run(M, legs, d, POLICY)[0] for d in draws(M, n, 7919 * K)]
    e = np.array([r["end"] for r in ends])
    done = np.array([c["doneS"] for c in cells])
    summ = dict(clusters=len(M["cl"]), crits=len(cells), pathKm=round(path / 1000, 2), team1=round(back, 1),
                Dmean=round(float(np.mean(D)), 1), DkBmean=round(float(np.mean(D)) * 99 / 1000, 1),
                sentKBmean=round(float(np.mean(sent)) * 99 / 1000, 1), short=sum(x < Q for x in sent) if Q else "",
                doneMean=round(float(done.mean()), 2), doneP90=round(float(np.percentile(done, 90)), 2),
                doneMax=round(float(done.max()), 2), L3mean=round(float(np.mean(L3)), 2),
                missing=sum(c["missing"] > 0 for c in cells), ready=round(ready, 1),
                endMean=round(float(e.mean()), 1), endCI=round(float(1.96 * e.std(ddof=1) / math.sqrt(len(e))), 1),
                endP90=round(float(np.percentile(e, 90)), 1),
                foundMean=round(float(np.mean([r["found"] for r in ends])), 1),
                visits=round(float(np.mean([r["visits"] for r in ends])), 2))
    return summ, cells, [dict(draw=i, **{k: round(v, 1) if isinstance(v, float) else v for k, v in r.items()})
                         for i, r in enumerate(ends)], legs


def map_panel(ax, M, legs, vmax):
    land(ax, M)
    pos = M["bs"]
    for k, st, en, _, _ in legs:   # transits dashed, then the cluster's own (curved or straight) line
        ax.plot([pos[0], st[0]], [pos[1], st[1]], color=INK, lw=.9, ls=(0, (3, 2)), zorder=5)
        p = M["cl"][k]["geo"]["path"]
        p = p if math.dist(tuple(p[0]), st) < 1e-6 else p[::-1]
        ax.plot(*p.T, color=INK, lw=1.8, zorder=6)
        pos = en
    ax.plot([pos[0], M["bs"][0]], [pos[1], M["bs"][1]], color=INK, lw=.9, ls=(0, (3, 2)), zorder=5)
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("seq", SEQ)
    for k, C in M["cl"].items():
        for h in C["P"]["crit"]:
            star = h == C["P"]["ch"]
            ax.scatter(*C["geo"]["c"][h], s=170 if star else 70, marker="*" if star else "o", zorder=7,
                       color=cmap(min(float(C["res"]["rf"][h]["doneS"]) / vmax, 1)), edgecolors=INK, lw=.9)
    frame(ax, M)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", nargs=2, action="append", metavar=("NAME", "GLOB"), required=True)
    ap.add_argument("--draws", type=int, default=100)
    ap.add_argument("--out", required=True)
    ap.add_argument("--figs", required=True)
    ap.add_argument("--tag", default="meander-ns3", help="figure names FIGS/TAG-{maps,results}.png")
    ap.add_argument("--windowKB", type=float, default=0, help="count the clusters sent less than this (column short)")
    a = ap.parse_args()
    sets = [s for s, _ in a.set]
    works = {s: {os.path.basename(w): w for w in sorted(glob.glob(g)) if complete(w)} for s, g in a.set}
    maps = sorted(set.intersection(*[set(v) for v in works.values()]), key=lambda m: int(m.lstrip("k")))
    summ, cells, dr, got = [], [], [], {}
    for m in maps:
        for s in sets:
            M = load_map(works[s][m], schemes=("rf",), with_bits=False)
            sm, cs, ds, legs = measure(M, a.draws, math.ceil(a.windowKB * 1000 / 99))
            summ.append(dict(map=m, set=s, **sm))
            cells += [dict(map=m, set=s, **c) for c in cs]
            dr += [dict(map=m, set=s, **d) for d in ds]
            got[(m, s)] = (M, legs)
            print(f"{m} {s:9s} " + " ".join(f"{k} {v}" for k, v in sm.items()), flush=True)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    for suffix, rows in (("summary", summ), ("cells", cells), ("draws", dr)):
        with open(f"{a.out}-{suffix}.csv", "w", newline="") as f:
            wr = csv.DictWriter(f, fieldnames=list(rows[0]))
            wr.writeheader()
            wr.writerows(rows)
    # ---- maps: rows maps, columns sets (whole D only); critical cells coloured by doneS (one scale), CH a star
    whole = [s for s in sets if not s.endswith("+w")]
    vmax = max(c["doneS"] for c in cells if c["set"] in whole)
    fig, axs = plt.subplots(len(maps), len(whole), figsize=(5.2 * len(whole), 5.6 * len(maps)), dpi=130,
                            facecolor=SURF, squeeze=False)
    for i, m in enumerate(maps):
        for j, s in enumerate(whole):
            map_panel(axs[i, j], *got[(m, s)], vmax)
    strip_text(fig)
    fig.savefig(os.path.join(a.figs, f"{a.tag}-maps.png"), facecolor=SURF, bbox_inches="tight", pad_inches=.05)
    plt.close(fig)
    # ---- results: one panel per measure (no shared axis), maps along x, one marker per set
    keys = [("doneMean", None), ("ready", None), ("endMean", "endCI"), ("DkBmean", None)]
    fig, axs = plt.subplots(1, len(keys) + 1, figsize=(4.2 * (len(keys) + 1), 3.8), dpi=150, facecolor=SURF)
    ax = axs[-1]   # per cluster: Axe length (cells) against its slowest critical cell (s)
    for s in sets:
        cl = {}
        for c in cells:
            if c["set"] == s:
                key = (c["map"], c["cluster"])
                cl[key] = (c["axe"], max(cl.get(key, (0, 0))[1], c["doneS"]))
        x, y = np.array(list(cl.values())).T
        ax.scatter(x, y, s=34, marker=MARK[base(s)], facecolors=face(s), edgecolors=COL[base(s)], lw=1.1, alpha=.9)
    ax.set_xlim(0, None); ax.set_ylim(0, None)
    ax.grid(color=GREY, lw=.6); ax.set_axisbelow(True); ax.set_facecolor(SURF)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for ax, (k, ci) in zip(axs, keys):
        for j, s in enumerate(sets):
            rs = [next(r for r in summ if r["map"] == m and r["set"] == s) for m in maps]
            x = np.arange(len(maps)) + (j - (len(sets) - 1) / 2) * min(0.22, 0.8 / len(sets))
            ax.errorbar(x, [r[k] for r in rs], yerr=[r[ci] for r in rs] if ci else None, fmt=MARK[base(s)],
                        color=COL[base(s)], mfc=face(s), ms=8, capsize=2, lw=1.2, mec=COL[base(s)], mew=1.2)
        ax.set_xticks(range(len(maps)))
        ax.set_xlim(-.6, len(maps) - .4)
        ax.set_ylim(0, None)
        ax.grid(axis="y", color=GREY, lw=.6)
        ax.set_axisbelow(True)
        ax.set_facecolor(SURF)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    strip_text(fig)
    fig.savefig(os.path.join(a.figs, f"{a.tag}-results.png"), facecolor=SURF, bbox_inches="tight", pad_inches=.05)
    plt.close(fig)


if __name__ == "__main__":
    main()
