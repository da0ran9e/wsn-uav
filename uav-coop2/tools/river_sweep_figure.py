"""Sweeps on ns-3: colours of the cell grid, River width, number of critical cells.

    python3 tools/river_sweep_figure.py --runs PILOT --figs docs/figures [--name ns3-sweeps.png]

PILOT holds uav-coop2-river outputs c{n}-w{W}-k{K}-{full|d}-{crit,runs}.csv (all missions in each file).
Per configuration: mean over missions of (mean over critical cells of the completion time), of the last
critical cell's time, and of the frames sent.
"""
import argparse, csv, glob, os, re, statistics as st

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
    res = {}
    for f in glob.glob(os.path.join(a.runs, "c*-w*-k*-*-crit.csv")):
        m = re.match(r"c(\d+)-w([\d.]+)-k(\d+)-(full|d)-crit\.csv", os.path.basename(f))
        key = (int(m[1]), float(m[2]), int(m[3]), m[4])
        crit, runs = list(csv.DictReader(open(f))), list(csv.DictReader(open(f.replace("-crit", "-runs"))))
        per = {}
        for r in crit:
            per.setdefault(r["run"], []).append(float(r["doneS"]) if float(r["doneS"]) >= 0 else float("nan"))
        res[key] = dict(mean=st.mean(st.mean(v) for v in per.values()), last=st.mean(max(v) for v in per.values()),
                        frames=st.mean(int(r["hops"]) for r in runs) / 1000, n=len(per))
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
            axs[0, j].plot(xs, [v["mean"] for _, v in ps], "-o", color=colr, lw=2, ms=8, mec=SURF, mew=1.5,
                           label=f"{lab}: trung bình các critical cell")
            axs[0, j].plot(xs, [v["last"] for _, v in ps], "--^", color=colr, lw=1.2, ms=7, mec=SURF, mew=1.5,
                           label=f"{lab}: critical cell cuối")
            axs[1, j].plot(xs, [v["frames"] for _, v in ps], "-o", color=colr, lw=2, ms=8, mec=SURF, mew=1.5,
                           label=lab)
            for x, v in ps:
                axs[1, j].annotate(f"{v['frames']:.0f}k", (x, v["frames"]), textcoords="offset points",
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
    fig.suptitle(f"Quét tham số trên ns-3 — trung bình {nm} lượt bay; gateway chọn theo chất lượng liên kết",
                 x=.01, ha="left", fontsize=11, color=INK)
    out = os.path.join(a.figs, a.name)
    fig.savefig(out, facecolor=SURF, bbox_inches="tight", pad_inches=.08)
    print(f"  {out}")


if __name__ == "__main__":
    main()
