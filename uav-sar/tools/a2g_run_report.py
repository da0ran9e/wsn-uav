"""Longest unbroken packet run from a passing UAV: ns-3 vs the analytic model.

URBAN BRANCH ONLY -- see examples/a2g-run-test.cc.

    python3 tools/a2g_run_report.py DIR OUT.png

DIR holds the outputs of a2g-run-test:
    calib.csv                     --mode=calib
    r26.csv r30.csv r335.csv      --fading=rician   --alpha=2.6 / 3.0 / 3.35
    n30.csv                       --fading=nakagami --alpha=3.0

The analytic model is the same pass computed directly: the same geometry, the
same two-segment path loss, Rician K=2 redrawn per packet. Three receivers:
    hard     received iff faded power >= -100 dBm  (what the spec's table assumed)
    curve    ns-3's own PER curve for 127-byte frames, read from calib.csv
    curve4   the same, but four independent fades inside each packet -- airtime
             4.256 ms against a 1.06 ms coherence time. A pessimistic bound:
             real fades decorrelate gradually, not in four clean blocks.
"""
import csv, os, sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

LATERAL = (0, 300, 600, 900)          # node 4, (3,5), (2,6), (1,7)
NODES = {0: (4,), 300: (3, 5), 600: (2, 6), 900: (1, 7)}
SPEC_TABLE = {3.0: (823, 208, 40, 11), 3.35: (740, 151, 20, 4)}   # node 4..1

INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"                  # categorical 1-3
RAMP = {2.6: "#86b6ef", 3.0: "#2a78d6", 3.35: "#104281"}      # ordinal blue


def longest(ok):
    x = np.concatenate(([0], ok.astype(np.int8), [0]))
    d = np.diff(x)
    s, e = np.where(d == 1)[0], np.where(d == -1)[0]
    return int((e - s).max()) if s.size else 0


def rician(rng, n, K=2.0):
    los, sc = np.sqrt(K / (K + 1)), np.sqrt(1 / (K + 1) / 2)
    return (los + sc * rng.standard_normal(n)) ** 2 + (sc * rng.standard_normal(n)) ** 2


def analytic(alpha, rx, per127=None, passes=200, seed=7, blocks=1):
    """Mean and sd of the longest run, and mean packets received, per lateral."""
    rng = np.random.default_rng(seed)
    y = -2000 + 50 * np.arange(8001) * 0.01
    out = {}
    for lat in LATERAL:
        d = np.sqrt(y ** 2 + lat ** 2 + 100 ** 2)
        mean = 10 - (80.05 + 10 * alpha * np.log10(d / 100))
        tot, rn = [], []
        for _ in range(passes):
            if rx == "hard":
                ok = mean + 10 * np.log10(rician(rng, d.size)) >= -100
            else:
                ps = np.ones(d.size)
                for _ in range(blocks):
                    ps *= (1 - per127(mean + 10 * np.log10(rician(rng, d.size)))) ** (1 / blocks)
                ok = rng.random(d.size) < ps
            tot.append(ok.sum())
            rn.append(longest(ok))
        out[lat] = (np.mean(rn), np.std(rn), np.mean(tot))
    return out


def ns3(path):
    rows = list(csv.DictReader(open(path)))
    out = {}
    for lat in LATERAL:
        r = [x for x in rows if int(x["node"]) in NODES[lat]]
        L = np.array([float(x["longest"]) for x in r])
        out[lat] = (L.mean(), L.std(), np.percentile(L, 10), np.percentile(L, 90),
                    np.mean([float(x["received"]) for x in r]))
    return out


def style(ax):
    ax.set_facecolor(SURF)
    ax.grid(color=GRID, lw=.7, which="both")
    ax.set_axisbelow(True)
    ax.tick_params(colors=INK2, labelsize=8.5)
    for s in ax.spines.values():
        s.set_visible(False)


def xlabels(ax):
    ax.set_xticks(range(4))
    ax.set_xticklabels(["0 m\nnode 4", "300 m\nnode 3, 5", "600 m\nnode 2, 6",
                        "900 m\nnode 1, 7"], fontsize=8.5, color=INK2)
    ax.set_xlabel("lệch ngang khỏi đường bay", fontsize=9, color=INK2)


def main():
    src, out = sys.argv[1], sys.argv[2]
    cal = list(csv.DictReader(open(os.path.join(src, "calib.csv"))))
    cx = np.array([float(r["prxDbm"]) for r in cal])
    cy = np.array([float(r["per"]) for r in cal])
    per127 = lambda p: np.interp(p, cx, cy, left=1.0, right=0.0)
    p50 = cx[np.argmax(cy <= 0.5)]

    sim = {a: ns3(os.path.join(src, f)) for a, f in
           ((2.6, "r26.csv"), (3.0, "r30.csv"), (3.35, "r335.csv"))}
    nak = ns3(os.path.join(src, "n30.csv"))

    print(f"ns-3, 127-byte frame, sensitivity -100 dBm: PER 50% at {p50:.2f} dBm\n")
    print(f"{'':30s}" + "".join(f"{f'{l} m':>16s}" for l in LATERAL))
    for a in (3.0, 3.35):
        hard = analytic(a, "hard")
        curve = analytic(a, "curve", per127)
        c4 = analytic(a, "curve", per127, blocks=4)
        print(f"--- alpha {a}: LONGEST RUN, mean ± sd")
        print(f"{'  spec table (hard -100)':30s}" +
              "".join(f"{v:>16d}" for v in SPEC_TABLE[a]))
        for name, r in (("analytic, hard -100", hard), ("analytic, ns-3 PER curve", curve),
                        ("ns-3 simulation", sim[a]), ("ns-3 curve, 4 fades/packet", c4)):
            print(f"{'  ' + name:30s}" + "".join(f"{f'{r[l][0]:.0f} ± {r[l][1]:.0f}':>16s}"
                                                for l in LATERAL))
        if a == 3.0:
            bracket = c4
    print("--- alpha 3.0, Nakagami m=1.8 (the spec's stand-in for Rician K=2)")
    print(f"{'  ns-3 simulation':30s}" + "".join(f"{f'{nak[l][0]:.0f} ± {nak[l][1]:.0f}':>16s}"
                                                for l in LATERAL))
    print(f"{'  ratio to Rician':30s}" + "".join(f"{nak[l][0] / sim[3.0][l][0]:>15.2f}x"
                                                for l in LATERAL))

    # ------------------------------------------------------------------ figure
    fig, ax = plt.subplots(2, 2, figsize=(12.6, 9.0), dpi=170, facecolor=SURF)
    x = np.arange(4)

    a = ax[0, 0]
    s = sim[3.0]
    m = [s[l][0] for l in LATERAL]
    lo = [s[l][0] - s[l][2] for l in LATERAL]
    hi = [s[l][3] - s[l][0] for l in LATERAL]
    a.errorbar(x - .12, m, yerr=[lo, hi], fmt="o", ms=8, color=S1, lw=2, capsize=0,
               mec=SURF, mew=2, label="ns-3, Rician K=2 (thanh = p10–p90)", zorder=3)
    a.plot(x, SPEC_TABLE[3.0], "D", ms=8, mfc="none", mec=S2, mew=2,
           label="bảng giải tích của đặc tả", zorder=3)
    a.plot(x + .12, [bracket[l][0] for l in LATERAL], "^", ms=10, color=S3, mec=SURF,
           mew=1.5, label="cận dưới: 4 fade trong mỗi gói", zorder=3)
    for i, l in enumerate(LATERAL):
        a.annotate(f"{s[l][0]:.0f}", (x[i] - .12, s[l][3]), xytext=(0, 5),
                   textcoords="offset points", ha="center", va="bottom", fontsize=8.5,
                   color=INK, fontweight="bold")
    a.set_yscale("log")
    a.set_ylabel("chuỗi gói liên tục dài nhất (gói, log)", fontsize=9, color=INK2)
    a.set_title("Kết quả chính, α = 3.0\nmột gói = 10 ms = 0.5 m đường bay",
                fontsize=10.5, color=INK, loc="left")
    a.legend(fontsize=8, frameon=False, loc="lower left", labelcolor=INK2)
    xlabels(a)

    a = ax[0, 1]
    for al in (2.6, 3.0, 3.35):
        v = [sim[al][l][0] for l in LATERAL]
        a.plot(x, v, "-o", ms=8, lw=2, color=RAMP[al], mec=SURF, mew=2)
        a.annotate(f"α = {al}", (x[-1], v[-1]), xytext=(8, 0), textcoords="offset points",
                   va="center", fontsize=8.5, color=INK2)
    a.set_yscale("log")
    a.set_xlim(-.3, 3.6)
    a.set_ylabel("chuỗi dài nhất, trung bình (gói, log)", fontsize=9, color=INK2)
    a.set_title("Độ nhạy theo số mũ suy hao α\nnode xa nhạy gấp bội node giữa",
                fontsize=10.5, color=INK, loc="left")
    xlabels(a)

    a = ax[1, 0]
    ratio = [nak[l][0] / sim[3.0][l][0] for l in LATERAL]
    a.bar(x, ratio, width=.56, color=S1, edgecolor=SURF, lw=2)
    a.axhline(1.0, color=INK2, lw=1, ls="--")
    for i, r in enumerate(ratio):
        a.annotate(f"{r:.2f}×", (x[i], r), xytext=(0, 4), textcoords="offset points",
                   ha="center", fontsize=9, color=INK, fontweight="bold")
    a.set_ylim(0, max(ratio) * 1.18)
    a.set_ylabel("chuỗi dài nhất: Nakagami ÷ Rician", fontsize=9, color=INK2)
    a.set_title("Nakagami m = 1.8 KHÔNG tương đương Rician K = 2\n"
                "khớp trung bình & phương sai, lệch đuôi fade sâu 50×",
                fontsize=10.5, color=INK, loc="left")
    xlabels(a)

    a = ax[1, 1]
    a.plot(cx, cy, "-", lw=2, color=S1, label="ns-3, khung 127 B")
    a.plot([-110, -100, -100, -90], [1, 1, 0, 0], "--", lw=1.2, color=INK2,
           label="ngưỡng cứng −100 dBm (đặc tả)")
    a.plot([p50], [.5], "o", ms=8, color=S1, mec=SURF, mew=2)
    a.annotate(f"PER 50 % tại {p50:.1f} dBm", (p50, .5), xytext=(-12, 0),
               textcoords="offset points", ha="right", va="center", fontsize=8.5, color=INK)
    a.set_xlim(-106, -94)
    a.set_xlabel("công suất thu, không fading (dBm)", fontsize=9, color=INK2)
    a.set_ylabel("tỉ lệ lỗi gói", fontsize=9, color=INK2)
    a.set_title("Máy thu ns-3 hào phóng hơn ngưỡng cứng ~1 dB\n"
                "giải thích trọn chênh lệch với bảng giải tích",
                fontsize=10.5, color=INK, loc="left")
    a.legend(fontsize=8, frameon=False, loc="upper right", labelcolor=INK2)

    for b in ax.flat:
        style(b)
    fig.suptitle("UAV 100 m, 50 m/s, gói 127 B mỗi 10 ms — chuỗi gói liên tục dài nhất "
                 "mỗi node nhận được (200 lượt bay)", fontsize=12, color=INK, x=.02,
                 ha="left", y=.995)
    fig.text(.02, .005, "NHÁNH ĐÔ THỊ — không dùng cho kịch bản rừng. TX +10 dBm, độ nhạy "
             "−100 dBm, suy hao tự do tới 100 m rồi (d/100)^−α, ăng-ten đẳng hướng, "
             "không che khuất, bỏ qua MAC.", fontsize=8, color=INK2)
    fig.tight_layout(rect=(0, .02, 1, .97))
    fig.savefig(out, facecolor=SURF)
    print(f"\n  {out}")


if __name__ == "__main__":
    main()
