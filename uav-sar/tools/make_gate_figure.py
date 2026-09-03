"""PNG: what Phase 2 waited for, and why waiting alone does not work.

One row per seed. Every element is a time: each advert the ground put on the
air (a SUMMON or a re-aim), the moment the gate released the rotary team, the
moment a UAV accepted an aim, and the deliveries that followed.

The point of the figure is the gap between an advert and an acceptance. A
SUMMON is a single one-hop broadcast from a cell leader; only a UAV already
airborne within its reach at that instant hears it. So a team parked at base
misses it by construction -- and once released, catching a later re-aim is
luck. The blue ticks that carry no acceptance under them are exactly that
loss. The LoRa flag closes it by routing the aim through the base, which is
standing next to the team it is releasing.

    python3 tools/make_gate_figure.py RUNROOT OUT.png
"""
import csv, glob, os, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

INK, DIM, GRID = "#12151a", "#5b6472", "#dfe3e9"
C_AD, C_GATE, C_DEL, C_ACC = "#2f6fd0", "#c2410c", "#1f9d6b", "#e08a1e"

LABEL = {"nogate": "không cổng\n(Phase 2 chạy ngay)",
         "sweep": "chờ quét xong",
         "home": "chờ scout hạ cánh",
         "flag": "chờ cờ LoRa\n(ứng viên đầu tiên)"}


def run_times(d):
    ev = list(csv.DictReader(open(os.path.join(d, "events.csv"))))
    at = lambda *n: sorted(float(r["t"]) for r in ev if r["event"] in n)
    return dict(gate=at("gate_open"), ads=at("summon_start", "retarget"),
                acc=at("divert", "retarget_divert"), dels=at("deliver_start"))


def main():
    root, out = sys.argv[1], sys.argv[2]
    rows = []
    for a in ("nogate", "sweep", "home", "flag"):
        ds = [d for d in sorted(glob.glob(os.path.join(root, a, "s*")))
              if os.path.exists(os.path.join(d, "events.csv"))]
        if ds:
            rows.append((a, [run_times(d) for d in ds]))
    tmax = max((max(t["dels"] + t["gate"] + t["ads"] + [1])
                for _, ts in rows for t in ts), default=300) * 1.06

    n = sum(len(ts) for _, ts in rows)
    fig, ax = plt.subplots(figsize=(10.4, 0.44 * n + 2.4), dpi=170)
    y, yticks, ylabels = 0, [], []
    for arm, ts in rows:
        y0 = y
        for t in ts:
            ax.plot([0, tmax], [y, y], color=GRID, lw=0.7, zorder=0)
            g = t["gate"][0] if t["gate"] else 0.0
            for a_ in t["ads"]:
                # An advert is dim once it is on the air with nobody able to act
                # on it: the team is still parked, or it was never heard.
                heard = any(g <= x <= a_ + 6.0 for x in t["acc"]) and a_ >= g - 1.0
                ax.plot([a_, a_], [y - .30, y + .30], color=C_AD, lw=2.0,
                        alpha=0.95 if heard else 0.30, solid_capstyle="butt")
            if t["gate"]:
                ax.plot([g], [y], marker="|", color=C_GATE, ms=17, mew=2.6)
            if t["acc"]:
                ax.plot(t["acc"], [y] * len(t["acc"]), marker="^", ls="",
                        color=C_ACC, ms=5.4, mew=0)
            if t["dels"]:
                ax.plot(t["dels"], [y] * len(t["dels"]), marker="o", ls="",
                        color=C_DEL, ms=5.0, mew=0)
            y += 1
        yticks.append((y0 + y - 1) / 2.0)
        ylabels.append(LABEL.get(arm, arm))
        ax.axhline(y - 0.5, color="#b9c0cb", lw=0.9)
        y += 0.7
    ax.set_yticks(yticks); ax.set_yticklabels(ylabels, fontsize=9.5, color=INK)
    ax.set_xlim(-8, tmax); ax.set_ylim(-1, y - 0.7)
    ax.invert_yaxis()
    ax.set_xlabel("thời gian mô phỏng (s)", fontsize=9.5, color=INK)
    ax.grid(axis="x", alpha=0.25, lw=0.6)
    for s in ax.spines.values(): s.set_color(GRID)
    ax.tick_params(labelsize=9)
    ax.set_title("Phase 2 chờ cái gì — và tin đi đường nào", fontsize=12.5,
                 color=INK, pad=10)
    fig.legend(handles=[
        Line2D([], [], color=C_AD, lw=2.2, label="mặt đất rao ứng viên"),
        Line2D([], [], color=C_AD, lw=2.2, alpha=0.30, label="rao mà không ai nhận"),
        Line2D([], [], color=C_GATE, marker="|", ls="", ms=14, mew=2.6,
               label="cổng mở (Phase 2 xuất phát)"),
        Line2D([], [], color=C_ACC, marker="^", ls="", ms=7, label="UAV nhận mục tiêu"),
        Line2D([], [], color=C_DEL, marker="o", ls="", ms=6, label="giao dữ liệu")],
        loc="lower center", ncol=5, frameon=False, fontsize=8.8,
        bbox_to_anchor=(0.5, -0.005))
    fig.text(0.5, 0.052,
             "SUMMON là quảng bá một chặng, phát một lần: chỉ UAV đang bay trong tầm "
             "ngay lúc đó mới nghe được. Hai nhánh giữa mở cổng đúng lúc mặt đất VẪN "
             "đang rao (11 lần rao sau cổng trên 6 hạt) nhưng đội đỗ ở căn cứ đã lỡ "
             "lần rao đầu, và sau khi cất cánh thì bắt được lần rao sau là chuyện may — "
             "0/6 hạt bắt được. Cờ LoRa không thắng vì mở sớm hơn mà vì đưa TOẠ ĐỘ về "
             "căn cứ, nơi đang đứng cạnh chính đội cần lệnh.",
             ha="center", va="center", fontsize=8.4, color=DIM, wrap=True)
    fig.tight_layout(rect=[0, 0.145, 1, 0.965])
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    print(f"  {out}")


if __name__ == "__main__":
    main()
