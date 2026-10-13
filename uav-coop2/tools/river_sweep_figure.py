"""Sweeps on ns-3: colours of the cell grid, River width, number of critical cells.

    python3 tools/river_sweep_figure.py --runs PILOT --figs docs/figures [--name ns3-sweeps.png]

PILOT holds uav-coop2-river outputs c{n}-w{W}-k{K}-{full|d}[-bF]-{crit,runs}.csv; the blocks -bF of one
configuration are merged. Per configuration and mission: the mean over critical cells of the completion
time, the last critical cell's time and the frames sent (a critical cell not done counts at the limit,
900 s, and is reported). Plotted: mean over missions with its 95 % interval. Printed: the comparisons,
paired by mission (every configuration of a mission sees the same channel).
"""
import argparse, csv, glob, math, os, re, statistics as st

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

INK, INK2, SURF, GREY = "#0b0b0b", "#52514e", "#fcfcfb", "#e6e5e1"
RIVER, DIRECT = "#1c5cab", "#eda100"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--figs", required=True)
    ap.add_argument("--name", default="ns3-sweeps.png")
    a = ap.parse_args()
    per = {}   # key -> run -> dict(times, frames)
    for f in glob.glob(os.path.join(a.runs, "c*-w*-k*-*-crit.csv")):
        m = re.match(r"c(\d+)-w([\d.]+)-k(\d+)-(full|d)(-b\d+)?-crit\.csv", os.path.basename(f))
        key = (int(m[1]), float(m[2]), int(m[3]), m[4])
        d = per.setdefault(key, {})
        for r in csv.DictReader(open(f)):
            d.setdefault(int(r["run"]), dict(times=[], frames=0))["times"].append(float(r["doneS"]))
        for r in csv.DictReader(open(f.replace("-crit", "-runs"))):
            d[int(r["run"])]["frames"] = int(r["hops"]) / 1000
    unfinished = {k: sum(t < 0 for v in d.values() for t in v["times"]) for k, d in per.items()}
    metric = lambda v, what: (st.mean(900 if t < 0 else t for t in v["times"]) if what == "mean" else
                              max(900 if t < 0 else t for t in v["times"]) if what == "last" else v["frames"])

    def ci(xs):
        return st.mean(xs), (1.96 * st.stdev(xs) / math.sqrt(len(xs)) if len(xs) > 1 else 0)

    res = {k: {w: ci([metric(v, w) for v in d.values()]) for w in ("mean", "last", "frames")} | {"n": len(d)}
           for k, d in per.items()}
    nm = min(v["n"] for v in res.values())

    fig, axs = plt.subplots(2, 3, figsize=(15, 7.5), dpi=150, facecolor=SURF, sharex="col",
                            gridspec_kw=dict(hspace=.12, wspace=.22))
    sweeps = [("số màu của lưới cell", [(c, (c, 3.5, 7, "full")) for c in (3, 4, 7, 13)], False),
              ("độ rộng River, cell", [(w, (7, w, 7, "full")) for w in (2.5, 3.5, 4.5, 6.5)], False),
              ("số critical cell", [(k, (7, 3.5, k, "full")) for k in (1, 4, 7, 10, 16)], True)]
    for j, (xl, pts, withDirect) in enumerate(sweeps):
        series = [("River", RIVER, pts)]
        if withDirect:
            series.append(("kéo thẳng", DIRECT, [(x, k[:3] + ("d",)) for x, k in pts]))
        for lab, colr, ps in series:
            ps = [(x, res[k]) for x, k in ps if k in res]
            xs = [x for x, _ in ps]
            kw = dict(color=colr, mec=SURF, mew=1.5, capsize=3, elinewidth=1)
            axs[0, j].errorbar(xs, [v["mean"][0] for _, v in ps], [v["mean"][1] for _, v in ps], fmt="-o", lw=2,
                               ms=8, label=f"{lab}: trung bình các critical cell", **kw)
            axs[0, j].errorbar(xs, [v["last"][0] for _, v in ps], [v["last"][1] for _, v in ps], fmt="--^", lw=1.2,
                               ms=7, label=f"{lab}: critical cell cuối", **kw)
            axs[1, j].errorbar(xs, [v["frames"][0] for _, v in ps], [v["frames"][1] for _, v in ps], fmt="-o", lw=2,
                               ms=8, label=lab, **kw)
            for x, v in ps:
                axs[1, j].annotate(f"{v['frames'][0]:.0f}k", (x, v["frames"][0]), textcoords="offset points",
                                   xytext=(0, 8), ha="center", fontsize=7, color=INK2)
        axs[1, j].set_xlabel(xl, fontsize=9, color=INK2)
        axs[1, j].set_xticks([x for x, _ in pts])
        axs[1, j].set_xticklabels([str(x).replace(".", ",") for x, _ in pts])
        axs[0, j].legend(frameon=False, fontsize=7.5, labelcolor=INK2, loc="upper left" if withDirect else "lower right")
    axs[0, 0].set_ylabel("hoàn tất, s", fontsize=9, color=INK2)
    axs[1, 0].set_ylabel("khung truyền thành công (nghìn)", fontsize=9, color=INK2)
    for ax in axs.ravel():
        ax.grid(color=GREY, lw=.6); ax.set_facecolor(SURF); ax.tick_params(colors=INK2, labelsize=8)
        ax.set_ylim(bottom=0)
        for sp in ax.spines.values():
            sp.set_visible(False)
    for j, t in enumerate(("Lưới cell (River 3,5; 7 critical)", "Độ rộng River (7 màu; 7 critical)",
                           "Số critical cell (7 màu; River 3,5)")):
        axs[0, j].set_title(t, loc="left", fontsize=10, color=INK)
    fig.suptitle(f"Quét tham số trên ns-3 — trung bình {nm} lượt bay (vạch: khoảng tin cậy 95 %); "
                 "gateway chọn theo chất lượng liên kết",
                 x=.01, ha="left", fontsize=11, color=INK)
    out = os.path.join(a.figs, a.name)
    fig.savefig(out, facecolor=SURF, bbox_inches="tight", pad_inches=.08)
    print(f"  {out}")

    # paired comparisons, mission by mission
    def paired(ka, kb, label):
        runs_ = sorted(set(per.get(ka, {})) & set(per.get(kb, {})))
        if not runs_:
            return
        out_ = [label + f" ({len(runs_)} lượt)"]
        for w, unit in (("mean", "s"), ("last", "s"), ("frames", "k")):
            dif = [metric(per[kb][r], w) - metric(per[ka][r], w) for r in runs_]
            m_, h = ci(dif)
            out_.append(f"{w} {m_:+.1f}±{h:.1f}{unit} (B<A {sum(x < 0 for x in dif)}/{len(dif)})")
        print("  " + "; ".join(out_))

    print(f"\nmissions per configuration: {sorted({v['n'] for v in res.values()})}; "
          f"unfinished critical cells: {dict((k, v) for k, v in unfinished.items() if v) or 0}")
    print("per configuration, mean ± 95 % (mean over critical cells | last | frames):")
    for k in sorted(res):
        v = res[k]
        print(f"  c{k[0]:<2} w{k[1]} k{k[2]:<2} {k[3]:4}: {v['mean'][0]:6.1f}±{v['mean'][1]:4.1f} s | "
              f"{v['last'][0]:6.1f}±{v['last'][1]:4.1f} s | {v['frames'][0]:6.1f}±{v['frames'][1]:4.1f} k")
    print("paired differences B - A, mean ± 95 %:")
    ref = (7, 3.5, 7, "full")
    for c in (3, 4, 13):
        paired(ref, (c, 3.5, 7, "full"), f"A = 7 màu, B = {c} màu")
    for w in (2.5, 4.5, 6.5):
        paired(ref, (7, w, 7, "full"), f"A = River 3,5, B = River {w}")
    for k in (1, 4, 7, 10, 16):
        paired((7, 3.5, k, "d"), (7, 3.5, k, "full"), f"A = kéo thẳng, B = River, {k} critical")


if __name__ == "__main__":
    main()
