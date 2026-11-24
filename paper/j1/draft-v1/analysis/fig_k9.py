"""K9 figures for the J1 draft: the River surrogate against ns-3 on the chosen critical-cell sets (B4), and the time to
confirm the target versus the number of AI cells under the two false-alarm rules (B5, B6).

    python3 fig_k9.py K9_DATA FIGS PLAIN

K9_DATA: logs/2026-11-18_1036-k9/data. FIGS: labelled PDF and PNG for the paper. PLAIN: the same plots without text
(CLAUDE.md item 63), for paper/j1/figures/.
"""
import csv, os, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA, FIGS, PLAIN = sys.argv[1:4]
SETS = [("rho20", "24 AI cells", "#1f6fb8", "o"), ("alg3", "Algorithm 3 (45)", "#e9a03b", "s"),
        ("rho100", "69 AI cells", "#2a9d8f", "^"), ("rho200", "161 AI cells", "#b5403a", "D")]
INK, GRID, LIMIT = "#333333", "#dddddd", 900.0
plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK, "axes.labelcolor": INK, "xtick.color": INK,
                     "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False})


def save(fig, ax, name):
    fig.savefig(f"{FIGS}/{name}.pdf", bbox_inches="tight"); fig.savefig(f"{FIGS}/{name}.png", dpi=200, bbox_inches="tight")
    for a in ax:
        a.set_xlabel(""); a.set_ylabel(""); a.set_title("")
        a.set_xticklabels([]); a.set_yticklabels([])
        if a.get_legend(): a.get_legend().remove()
        for t in list(a.texts): t.remove()
    for l in list(fig.legends): l.remove()
    fig.savefig(f"{PLAIN}/{name}.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


# 1. surrogate vs ns-3, per critical cell, both channels
rows = list(csv.DictReader(open(f"{DATA}/b4-seed1.csv")))
fig, ax = plt.subplots(figsize=(3.4, 3.0))
ax.plot([0, LIMIT], [0, LIMIT], color=GRID, lw=1, zorder=0)
for tag, name, col, mk in SETS:
    r = [x for x in rows if x["set"] == tag]
    done = [x for x in r if x["missing"] == "0"]
    ax.scatter([float(x["doneS_pred"]) for x in done], [float(x["doneS_ns3"]) for x in done], s=10, marker=mk,
               facecolor=col, edgecolor="white", linewidth=0.4, label=name)
    inc = [x for x in r if x["missing"] != "0"]
    if inc:
        ax.scatter([float(x["doneS_pred"]) for x in inc], [LIMIT] * len(inc), s=22, marker=mk, facecolor="none",
                   edgecolor=col, linewidth=1)
ax.set_xlim(0, 400); ax.set_ylim(0, LIMIT + 30)
ax.set_xlabel("Surrogate prediction (s)"); ax.set_ylabel("ns-3, River seed 1 (s)")
ax.text(248, LIMIT, "not complete at 900 s", ha="right", va="center", color=INK, fontsize=7)
ax.legend(frameon=False, loc="center left", bbox_to_anchor=(0, 0.62), fontsize=7, handletextpad=0.2)
save(fig, [ax], "k9-surrogate-vs-ns3")

# 2. time to confirm vs AI cells at rho = 20, two false-alarm rules (r100)
def load(f):
    return {(r["channel"], r["set"], r["rho"], r["k"]): r for r in csv.DictReader(open(f))}


cell, sys_ = load(f"{DATA}/b6-fa-cell-0-1.csv"), load(f"{DATA}/b6-fa-sys-2-4.csv")
fig, axs = plt.subplots(1, 2, figsize=(3.5, 2.7), sharey=True)
for ax, k in zip(axs, ("1", "3")):
    xs = [int(cell[("r100", t, "20", k)]["ai_cells"]) for t, _, _, _ in SETS]
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    X = [xs[i] for i in order]
    T1 = [float(cell[("r100", SETS[i][0], "20", k)]["T1"]) for i in order]
    Tc = [float(cell[("r100", SETS[i][0], "20", k)]["T_mean"]) for i in order]
    Ts = [float(sys_[("r100", SETS[i][0], "20", k)]["T_mean"]) for i in order]
    ax.plot(X, T1, color="#888888", lw=2, marker="o", ms=4, label="Phase 1 done (ns-3)")
    ax.plot(X[-1:], T1[-1:], ls="none", marker="o", ms=6, mfc="white", mec="#888888", mew=1.2)   # lower bound
    ax.plot(X, Tc, color="#1f6fb8", lw=2, marker="s", ms=4, label="Confirmed, alarm 0.1 per AI cell")
    ax.plot(X, Ts, color="#b5403a", lw=2, marker="^", ms=4, label="Confirmed, 2.4 alarms system-wide")
    ax.set_xlabel("AI cells"); ax.set_xticks([25, 75, 125]); ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True)
    ax.set_title(f"k = {k} target vector{'s' if k == '3' else ''}", fontsize=8, color=INK)
axs[0].set_ylabel("Time from take-off (s)")
fig.legend(*axs[0].get_legend_handles_labels(), frameon=False, fontsize=6.5, loc="lower center", ncol=1,
           bbox_to_anchor=(0.5, 1.0))
save(fig, list(axs), "k9-time-vs-ai-cells")
print("written")
