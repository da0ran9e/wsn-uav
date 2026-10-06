"""G2G multi-hop chain across one wide cluster: how long does the file take?

URBAN BRANCH ONLY -- see examples/g2g-chain-test.cc.

    python3 tools/g2g_chain_report.py select DIR          # representative chains
    python3 tools/g2g_chain_report.py report DIR OUTDIR   # tables and figures

DIR holds the campaign (TAG-runs.csv, TAG-hops.csv, TAG-arrivals.csv per
configuration) and, for the space-time figures, rep-sS-* files: the chain chosen
by `select`, re-run alone with its trace. Choice of chain, by rule: among the
chains that delivered the whole file, the one whose completion time is closest
to their median (ties: lowest run number).
"""
import csv, glob, os, re, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np

INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"
OK, FAIL = "#2a78d6", "#e34948"
SP_RAMP = {50: "#86b6ef", 75: "#3987e5", 100: "#0d366b"}     # ordinal, validated
SPACINGS = (50, 75, 100)
PER50_DBM = -101.0          # ns-3, 127-byte frame, sensitivity -100 dBm (A2G-RUN calib)
LIMIT_S = 300.0
VARIANTS = [  # tag prefix, label
    ("main-s{s}-M3", "gốc: M=3, T_c=100 ms, σ=7.8 dB, +10 dBm"),
    ("m4-s{s}", "M = 4 (giãn tái dùng khe)"),
    ("coh10-s{s}", "T_c = 10 ms (fading nhanh)"),
    ("coh1000-s{s}", "T_c = 1 s (fading chậm)"),
    ("sig4-s{s}", "σ = 4 dB (gần LoS)"),
    ("tx0-s{s}", "TX 0 dBm (lớp CC2420)"),
]


def runs_of(src, tag):
    return list(csv.DictReader(open(os.path.join(src, f"{tag}-runs.csv"))))


def hops_of(src, tag):
    return list(csv.DictReader(open(os.path.join(src, f"{tag}-hops.csv"))))


def pick(rows):
    done = [r for r in rows if r["complete"] == "1"]
    if not done:
        return None
    med = np.median([float(r["completeS"]) for r in done])
    return min(done, key=lambda r: (abs(float(r["completeS"]) - med), int(r["run"])))


def style(ax, grid=True):
    ax.set_facecolor(SURF)
    if grid:
        ax.grid(color=GRID, lw=.7)
        ax.set_axisbelow(True)
    ax.tick_params(colors=INK2, labelsize=8)
    for s in ax.spines.values():
        s.set_visible(False)


def summary(rows):
    t = np.array([float(r["completeS"]) for r in rows if r["complete"] == "1"])
    frac = len(t) / len(rows)
    q = (lambda p: np.percentile(t, p)) if len(t) else (lambda p: float("nan"))
    deliv = np.mean([int(r["delivered"]) for r in rows])
    return frac, q(50), q(10), q(90), deliv


def worst(hops):
    by = {}
    for h in hops:
        by.setdefault(h["run"], []).append(float(h["medianPrxDbm"]))
    return {k: min(v) for k, v in by.items()}


# ---------------------------------------------------------------- tables
def tables(src):
    print(f"Completion = all 100 packets at the tail within {LIMIT_S:.0f} s. "
          "Times are over the chains that completed.\n")
    print(f"{'configuration':44s} {'spacing':>7} {'hops':>4} | {'done':>6} {'median':>8} "
          f"{'p10':>7} {'p90':>7} | {'pkts at tail (mean)':>19}")
    for tagf, label in VARIANTS:
        for s in SPACINGS:
            tag = tagf.format(s=s)
            if not os.path.exists(os.path.join(src, f"{tag}-runs.csv")):
                continue
            rows = runs_of(src, tag)
            hops = len(hops_of(src, tag)) // len(rows)
            f, m, a, b, d = summary(rows)
            print(f"{label:44s} {s:5d} m {hops:4d} | {f:6.1%} {m:7.1f}s {a:6.1f}s {b:6.1f}s | {d:19.1f}")
        print()
    # The explanation: the worst link of each chain.
    print("Worst link (lowest median Prx over the chain's hops) vs outcome, primary runs:")
    print(f"{'worst-link Prx':>16} | " + " | ".join(f"{s} m: n  done  median" for s in SPACINGS))
    edges = [-200, -110, -106, -104, -102, -100, -95, 0]
    W = {s: worst(hops_of(src, f"main-s{s}-M3")) for s in SPACINGS}
    R = {s: {r["run"]: r for r in runs_of(src, f"main-s{s}-M3")} for s in SPACINGS}
    for lo, hi in zip(edges, edges[1:]):
        cells = []
        for s in SPACINGS:
            g = [R[s][k] for k, w in W[s].items() if lo <= w < hi]
            if not g:
                cells.append(f"{'':>19}")
                continue
            dn = [float(r["completeS"]) for r in g if r["complete"] == "1"]
            cells.append(f"{len(g):5d} {len(dn) / len(g):5.0%} "
                         f"{(np.median(dn) if dn else float('nan')):6.1f}s")
        print(f"{f'[{lo}, {hi}) dBm':>16} | " + " | ".join(cells))


# ---------------------------------------------------------------- figure: space-time
def fig_spacetime(src, out):
    fig = plt.figure(figsize=(14, 11.5), dpi=180, facecolor=SURF)
    gs = fig.add_gridspec(3, 2, width_ratios=[5.2, 1], hspace=.55, wspace=.04,
                          left=.07, right=.98, top=.9, bottom=.05)
    for row, s in enumerate(SPACINGS):
        rep = f"rep-s{s}"
        tr_path = os.path.join(src, f"{rep}-trace.csv")
        if not os.path.exists(tr_path):
            continue
        tr = list(csv.DictReader(open(tr_path)))
        hops = list(csv.DictReader(open(os.path.join(src, f"{rep}-hops.csv"))))
        run = list(csv.DictReader(open(os.path.join(src, f"{rep}-runs.csv"))))[0]
        prim = runs_of(src, f"main-s{s}-M3")
        frac = np.mean([r["complete"] == "1" for r in prim])
        H = len(hops)
        a = fig.add_subplot(gs[row, 0])
        t = np.array([float(x["t"]) for x in tr])
        nd = np.array([int(x["node"]) for x in tr])
        ok = np.array([x["ok"] == "1" for x in tr])
        for mask, col, lw, z in ((~ok, FAIL, .5, 2), (ok, OK, .7, 3)):
            segs = [[(ti, ni), (ti, ni + 1)] for ti, ni in zip(t[mask], nd[mask])]
            a.add_collection(LineCollection(segs, colors=col, linewidths=lw, zorder=z))
        # a few packets followed hop by hop
        seq = np.array([int(x["seq"]) for x in tr])
        for k in (0, 49, 99):
            m = ok & (seq == k)
            if not m.any():
                continue
            o = np.argsort(nd[m])
            xs = np.concatenate(([t[m][o][0]], t[m][o] + .0045))
            ys = np.concatenate(([0], nd[m][o] + 1))
            a.plot(xs, ys, color=INK, lw=1.3, zorder=4)
            a.annotate(f"gói {k + 1}", (xs[-1], ys[-1]), xytext=(4, -2), textcoords="offset points",
                       fontsize=7.5, color=INK, va="top")
        T = float(run["completeS"])
        a.set_xlim(0, T * 1.06)
        a.set_ylim(H + .4, -.4)
        a.set_yticks(range(0, H + 1, max(1, H // 10)))
        a.set_yticklabels([f"{i * s} m" for i in range(0, H + 1, max(1, H // 10))])
        a.set_ylabel("vị trí trên dải (đầu → cuối)", fontsize=8.5, color=INK2)
        a.set_xlabel("thời gian (s)", fontsize=8.5, color=INK2)
        att = sum(int(h["attempts"]) for h in hops)
        a.set_title(f"Cách {s} m · {H} hop · chuỗi đại diện (lượt {run['run']}): 100 gói tới cuối "
                    f"sau {T:.1f} s, {att} lần phát dữ liệu · {frac:.0%} chuỗi xong trong "
                    f"{LIMIT_S:.0f} s", loc="left", fontsize=10, color=INK)
        style(a)
        # link quality, aligned hop by hop
        b = fig.add_subplot(gs[row, 1], sharey=a)
        prx = np.array([float(h["medianPrxDbm"]) for h in hops])
        w = int(np.argmin(prx))
        b.barh(np.arange(H) + .5, prx + 120, left=-120, height=.72,
               color=[FAIL if i == w else "#c3c2b7" for i in range(H)])
        b.axvline(PER50_DBM, color=INK2, lw=1, ls="--")
        b.text(PER50_DBM + 1, -.3, "PER 50 %", fontsize=7, color=INK2, va="top")
        b.set_xlim(-120, -75)
        b.set_xlabel("Prx trung vị (dBm)", fontsize=8, color=INK2)
        b.tick_params(labelleft=False)
        b.annotate(f"hop yếu nhất\n{prx[w]:.1f} dBm", (prx[w], w + .5), xytext=(6, 0),
                   textcoords="offset points", fontsize=7.5, color=FAIL, va="center")
        style(b)
    fig.suptitle("Đường đi của gói tin qua dải: mỗi vạch là một lần phát dữ liệu từ node này "
                 "sang node kế — xanh = có ACK, đỏ = mất", x=.07, ha="left", fontsize=12.5,
                 color=INK, y=.985)
    fig.text(.07, .945, "Dữ liệu trực tiếp từ ns-3. Đường đen: hành trình của gói 1, 50, 100. "
             "Cột phải: công suất thu trung vị từng hop (đường truyền + che khuất tĩnh), hop yếu "
             "nhất tô đỏ. TDMA M = 3, khe 10 ms, Rayleigh T_c = 100 ms, σ = 7.8 dB. NHÁNH ĐÔ THỊ.",
             fontsize=8.3, color=INK2, ha="left")
    fig.savefig(out, facecolor=SURF)
    print(f"  {out}")


# ---------------------------------------------------------------- figure: the schedule, zoomed
def fig_zoom(src, out, s=50, until=0.6):
    tr_path = os.path.join(src, f"rep-s{s}-trace.csv")
    if not os.path.exists(tr_path):
        return
    tr = [x for x in csv.DictReader(open(tr_path)) if float(x["t"]) <= until]
    H = len(list(csv.DictReader(open(os.path.join(src, f"rep-s{s}-hops.csv")))))
    fig, a = plt.subplots(figsize=(14, 5.6), dpi=180, facecolor=SURF)
    for k in range(int(until / .01) + 1):
        if k % 3 == 0:
            a.axvspan(k * .01, k * .01 + .01, color="#f0efec", lw=0, zorder=0)
    for x in tr:
        t, n = float(x["t"]), int(x["node"])
        col = OK if x["ok"] == "1" else FAIL
        a.add_patch(plt.Rectangle((t, n + .12), .00445, .76, fc=col, ec="none", zorder=3))
        if int(x["seq"]) < 3 or x["ok"] != "1":
            a.text(t + .0022, n + .5, x["seq"], ha="center", va="center", fontsize=5.5,
                   color=SURF, zorder=4)
    a.set_xlim(0, until)
    a.set_ylim(H + .2, -.2)
    a.set_yticks(np.arange(H) + .5)
    a.set_yticklabels([f"{i}→{i + 1}" for i in range(H)], fontsize=6.5)
    a.set_ylabel("hop", fontsize=8.5, color=INK2)
    a.set_xlabel("thời gian (s) — dải nền xám: khe của node 0, 3, 6, … (M = 3, khe 10 ms)",
                 fontsize=8.5, color=INK2)
    style(a, grid=False)
    fig.suptitle(f"Lịch TDMA nhìn gần: {until:.1f} s đầu, dải cách {s} m — mỗi khối là một gói "
                 "dữ liệu 4.26 ms (số = thứ tự gói); xanh = có ACK, đỏ = mất", x=.07, ha="left",
                 fontsize=11.5, color=INK, y=.98)
    fig.text(.07, .915, "Gói đi chéo xuống từng hop một khe (sóng truyền), nhiều node cách nhau "
             "3 hop phát cùng khe. Một hop đỏ liên tiếp làm cả hàng sau phải chờ. Chuỗi đại diện, "
             "dữ liệu trực tiếp từ ns-3.", fontsize=8.3, color=INK2, ha="left")
    fig.subplots_adjust(left=.07, right=.98, top=.86, bottom=.11)
    fig.savefig(out, facecolor=SURF)
    print(f"  {out}")


# ---------------------------------------------------------------- figure: ECDF + worst link
def fig_outcomes(src, out):
    fig, ax = plt.subplots(1, 2, figsize=(14, 5.2), dpi=170, facecolor=SURF,
                           gridspec_kw=dict(width_ratios=[1, 1.15]))
    a = ax[0]
    for s in SPACINGS:
        rows = runs_of(src, f"main-s{s}-M3")
        t = np.sort([float(r["completeS"]) for r in rows if r["complete"] == "1"])
        y = np.arange(1, len(t) + 1) / len(rows)
        a.step(np.concatenate(([.5], t, [LIMIT_S])), np.concatenate(([0], y, [y[-1] if len(y) else 0])),
               where="post", lw=2, color=SP_RAMP[s])
        a.annotate(f"cách {s} m: {len(t) / len(rows):.0%}", (LIMIT_S, y[-1] if len(y) else 0),
                   xytext=(4, 0), textcoords="offset points", va="center", fontsize=8.5, color=INK2)
    a.axvline(1.0, color=INK2, lw=1, ls=":")
    a.text(1.05, .97, "UAV phát 100 gói\n= 1 s", fontsize=7.5, color=INK2, va="top")
    a.axvline(3.16, color=INK2, lw=1, ls="--")
    a.text(3.3, .80, "TDMA không mất gói\n≈ 3.1 s", fontsize=7.5, color=INK2, va="top")
    a.set_xscale("log")
    a.set_xlim(.8, LIMIT_S * 1.9)
    a.set_ylim(0, 1.0)
    a.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    a.set_xlabel("thời gian để cả 100 gói tới cuối dải (s, log)", fontsize=8.5, color=INK2)
    a.set_ylabel("tỉ lệ chuỗi đã xong", fontsize=8.5, color=INK2)
    a.set_title(f"Phân bố thời gian hoàn thành (200 chuỗi mỗi khoảng cách)\nphần không chạm "
                f"100 %: chuỗi chưa xong sau {LIMIT_S:.0f} s", loc="left", fontsize=10.5, color=INK)
    style(a)

    a = ax[1]
    for s in SPACINGS:
        W = worst(hops_of(src, f"main-s{s}-M3"))
        rows = runs_of(src, f"main-s{s}-M3")
        x = np.array([W[r["run"]] for r in rows])
        done = np.array([r["complete"] == "1" for r in rows])
        y = np.array([float(r["completeS"]) if d else LIMIT_S * 1.45 for r, d in zip(rows, done)])
        a.scatter(x[done], y[done], s=16, color=SP_RAMP[s], ec=SURF, lw=.4, zorder=3,
                  label=f"cách {s} m")
        a.scatter(x[~done], y[~done] * np.exp(np.random.default_rng(s).normal(0, .06, (~done).sum())),
                  s=16, marker="x", color=SP_RAMP[s], lw=1, zorder=3)
    a.axhline(LIMIT_S, color=INK2, lw=.8)
    a.text(-121, LIMIT_S * 1.45, "chưa xong\nsau 300 s", fontsize=7.5, color=INK2, va="center")
    a.axvline(PER50_DBM, color=INK2, lw=1, ls="--")
    a.text(PER50_DBM + .3, 1.1, "PER 50 %", fontsize=7.5, color=INK2)
    a.set_yscale("log")
    a.set_ylim(1, LIMIT_S * 2.4)
    a.set_xlim(-122, -86)
    a.set_xlabel("công suất thu trung vị của hop YẾU NHẤT trong chuỗi (dBm)", fontsize=8.5, color=INK2)
    a.set_ylabel("thời gian hoàn thành (s, log)", fontsize=8.5, color=INK2)
    a.set_title("Hop yếu nhất quyết định tất cả\nmỗi điểm một chuỗi; × = không xong",
                loc="left", fontsize=10.5, color=INK)
    a.legend(fontsize=8, frameon=False, loc="upper right", labelcolor=INK2)
    style(a)
    fig.suptitle("Dải G2G ~1 km, 100 gói unicast từ đầu tới cuối — TDMA M = 3, Rayleigh "
                 "T_c = 100 ms, che khuất tĩnh σ = 7.8 dB, +10 dBm. NHÁNH ĐÔ THỊ.", x=.01,
                 ha="left", fontsize=11.5, color=INK, y=1.0)
    fig.tight_layout(rect=(0, 0, 1, .95))
    fig.savefig(out, facecolor=SURF)
    print(f"  {out}")


# ---------------------------------------------------------------- figure: sensitivities
def fig_sens(src, out):
    fig, ax = plt.subplots(1, 2, figsize=(14, 4.9), dpi=170, facecolor=SURF)
    labels = [l for _, l in VARIANTS]
    y = np.arange(len(VARIANTS))
    for c, (key, title, fmt) in enumerate(((0, "tỉ lệ chuỗi xong trong 300 s", "{:.0%}"),
                                           (1, "thời gian trung vị của chuỗi đã xong (s)", "{:.0f}"))):
        a = ax[c]
        for s, dy in zip(SPACINGS, (-.22, 0, .22)):
            vals = []
            for tagf, _ in VARIANTS:
                rows = runs_of(src, tagf.format(s=s))
                f, m, *_ = summary(rows)
                vals.append(f if key == 0 else m)
            a.scatter(vals, y + dy, s=42, color=SP_RAMP[s], ec=SURF, lw=1, zorder=3,
                      label=f"cách {s} m")
            for v, yy in zip(vals, y + dy):
                if not np.isnan(v):
                    a.annotate(fmt.format(v), (v, yy), xytext=(6, 0), textcoords="offset points",
                               va="center", fontsize=7, color=INK2)
        a.set_yticks(y)
        a.set_yticklabels(labels if c == 0 else [""] * len(y), fontsize=8.5, color=INK)
        a.set_ylim(len(y) - .5, -.5)
        if key == 0:
            a.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
            a.set_xlim(-.03, 1.12)
        else:
            a.set_xscale("log")
            a.set_xlim(2, 600)
        a.set_title(title, loc="left", fontsize=10.5, color=INK)
        style(a)
    ax[0].legend(fontsize=8, frameon=False, loc="lower right", labelcolor=INK2)
    fig.suptitle("Độ nhạy: mỗi dòng đổi MỘT tham số so với cấu hình gốc", x=.01, ha="left",
                 fontsize=12, color=INK, y=.99)
    fig.tight_layout(rect=(0, 0, 1, .94))
    fig.savefig(out, facecolor=SURF)
    print(f"  {out}")


def main():
    mode, src = sys.argv[1], sys.argv[2]
    if mode == "select":
        for s in SPACINGS:
            p = pick(runs_of(src, f"main-s{s}-M3"))
            print(s, p["run"] if p else "none")
        return
    outdir = sys.argv[3]
    os.makedirs(outdir, exist_ok=True)
    tables(src)
    fig_spacetime(src, os.path.join(outdir, "g2g-chain-spacetime.png"))
    fig_zoom(src, os.path.join(outdir, "g2g-chain-schedule.png"))
    fig_outcomes(src, os.path.join(outdir, "g2g-chain-outcomes.png"))
    fig_sens(src, os.path.join(outdir, "g2g-chain-sensitivity.png"))


if __name__ == "__main__":
    main()
