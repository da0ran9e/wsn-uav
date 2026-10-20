"""Tables and figures of l1_rank.py runs (CLAUDE.md §8 item 114); figures without text (item 63).

    python3 tools/l1_compare.py --draws docs/data/l1rank/e1-draws.csv --ref kmedoids:P* \
        --row "kmedoids:P*" --row "kmedoids:B4*" ... --out docs/data/l1rank/e1 --figs docs/figures --tag l1-e1

Each --row is SET:METHOD (an alias NAME=SET:METHOD prints NAME). The independent unit is the map (10 per size):
per row and size, the mean over maps of each map's mean over draws, with a 95 % t interval over maps; p90 over
every draw; the mean rank of c* in team 2's visits and the share of draws where c* was visited first; the paired
change against --ref (same map, same draw) and how many maps it beats --ref on.
Writes OUT-table.csv and FIGS/TAG-tstar.png: one group per size (k2, k4, k6, k8), one marker per row in the
order given (mean and interval over maps); colours from --colour NAME=#hex (default grey), markers from
--marker NAME=o; with --breakdown also FIGS/TAG-breakdown.png (see --help).
"""
import argparse, csv, math, os
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from map_gen import strip_text
from mission_report import GREY, INK, SURF

T975 = {1: 12.71, 2: 4.30, 3: 3.18, 4: 2.78, 5: 2.57, 6: 2.45, 7: 2.36, 8: 2.31, 9: 2.26, 10: 2.23, 11: 2.20}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", nargs="+", required=True)
    ap.add_argument("--row", action="append", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--colour", action="append", default=[])
    ap.add_argument("--marker", action="append", default=[])
    ap.add_argument("--out", required=True)
    ap.add_argument("--figs", default="")
    ap.add_argument("--tag", default="l1")
    ap.add_argument("--log", action="store_true", help="log scale for the figure")
    ap.add_argument("--breakdown", action="store_true",
                    help="also FIGS/TAG-breakdown.png: per row and size, c*'s first report at the BS (light) and the "
                         "time from it to c*'s verification (full colour), stacked")
    a = ap.parse_args()
    D = defaultdict(dict)          # (set, method) -> {(map, draw): row}
    for f in a.draws:
        for r in csv.DictReader(open(f)):
            D[(r["set"], r["method"])][(r["map"], int(r["draw"]))] = r
    rows = []
    for spec in a.row:
        name, _, key = spec.rpartition("=")
        s, m = key.split(":")
        rows.append((name or key, (s, m)))
    ref = tuple(a.ref.split(":"))
    col = dict(c.split("=") for c in a.colour)
    mk = dict(c.split("=") for c in a.marker)
    sizes = ("k2", "k4", "k6", "k8")
    table = []
    for name, key in rows:
        X = D[key]
        for sz in sizes:
            maps = sorted({k[0] for k in X if k[0].startswith(sz + "-")})
            if not maps:
                continue
            per = {mp: [float(X[k]["Tstar"]) for k in X if k[0] == mp] for mp in maps}
            mm = np.array([np.mean(v) for v in per.values()])
            ci = T975.get(len(maps) - 1, 1.96) * mm.std(ddof=1) / math.sqrt(len(maps)) if len(maps) > 1 else float("nan")
            alld = np.concatenate(list(per.values()))
            Y = [X[k] for k in X if k[0].startswith(sz + "-")]
            dref = [np.mean([float(X[k]["Tstar"]) - float(D[ref][k]["Tstar"]) for k in X if k[0] == mp and k in D[ref]])
                    for mp in maps] if key != ref else [0.0] * len(maps)
            table.append(dict(row=name, set=key[0], method=key[1], size=sz, maps=len(maps), draws=len(alld),
                              Tstar=round(float(mm.mean()), 1), ci=round(float(ci), 1),
                              p90=round(float(np.percentile(alld, 90)), 1),
                              rank=round(float(np.mean([float(r["rank"]) for r in Y])), 2),
                              first=round(float(np.mean([r["rank"] == "1" for r in Y])), 3),
                              starIn=round(float(np.mean([float(r["starIn"]) for r in Y])), 1),
                              team1=round(float(np.mean([float(r["team1"]) for r in Y])), 1),
                              crits=round(float(np.mean([float(r["crits"]) for r in Y])), 1),
                              clusters=round(float(np.mean([float(r["size"]) for r in Y])), 1),
                              Tall=round(float(np.nanmean([float(r["Tall"]) for r in Y])), 1),
                              dRef=round(float(np.mean(dref)), 1), betterMaps=int(sum(d < -1e-9 for d in dref))))
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out + "-table.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(table[0]))
        w.writeheader()
        w.writerows(table)
    print(f"{'row':34s} " + "  ".join(f"{sz:>22s}" for sz in sizes))
    for name, key in rows:
        cells = []
        for sz in sizes:
            t = next((t for t in table if t["row"] == name and t["size"] == sz), None)
            cells.append(f"{t['Tstar']:6.0f}±{t['ci']:3.0f} {t['dRef']:+5.0f} {t['betterMaps']:2d}/{t['maps']}" if t else " " * 22)
        print(f"{name:34s} " + "  ".join(cells))
    if not a.figs:
        return
    fig, ax = plt.subplots(figsize=(12, 5), dpi=150, facecolor=SURF)
    n = len(rows)
    for i, (name, key) in enumerate(rows):
        for j, sz in enumerate(sizes):
            t = next((t for t in table if t["row"] == name and t["size"] == sz), None)
            if t is None:
                continue
            x = j + (i - (n - 1) / 2) * min(0.08, 0.8 / n)
            ax.errorbar(x, t["Tstar"], yerr=t["ci"], fmt=mk.get(name, "o"), ms=6, capsize=2, lw=1.2,
                        color=col.get(name, "#52514e"), mec=col.get(name, "#52514e"))
    if a.log:
        ax.set_yscale("log")
        ax.tick_params(which="both", labelleft=False)
    else:
        ax.set_ylim(0, None)
    ax.set_xticks(range(len(sizes)))
    ax.set_xlim(-.6, len(sizes) - .4)
    ax.grid(axis="y", color=GREY, lw=.6, which="both")
    ax.set_axisbelow(True)
    ax.set_facecolor(SURF)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    strip_text(fig)
    fig.savefig(os.path.join(a.figs, f"{a.tag}-tstar.png"), facecolor=SURF, bbox_inches="tight", pad_inches=.06)
    plt.close(fig)
    if not a.breakdown:
        return
    # where the time goes: c*'s first report at the BS (light) and the rest until c* is verified (row colour)
    fig, ax = plt.subplots(figsize=(12, 4.5), dpi=150, facecolor=SURF)
    bw = min(0.8 / n, 0.12)
    for i, (name, key) in enumerate(rows):
        for j, sz in enumerate(sizes):
            t = next((t for t in table if t["row"] == name and t["size"] == sz), None)
            if t is None:
                continue
            x = j + (i - (n - 1) / 2) * bw
            c = col.get(name, "#52514e")
            ax.bar(x, t["starIn"], width=bw * .9, color=matplotlib.colors.to_rgba(c, .3), edgecolor="none")
            ax.bar(x, t["Tstar"] - t["starIn"], bottom=t["starIn"], width=bw * .9, color=c, edgecolor="none")
    ax.set_xticks(range(len(sizes)))
    ax.set_ylim(0, None)
    ax.grid(axis="y", color=GREY, lw=.6)
    ax.set_axisbelow(True)
    ax.set_facecolor(SURF)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    strip_text(fig)
    fig.savefig(os.path.join(a.figs, f"{a.tag}-breakdown.png"), facecolor=SURF, bbox_inches="tight", pad_inches=.06)
    plt.close(fig)


if __name__ == "__main__":
    main()
