"""PNG: what several UAV antennas would have to beat.

    python3 tools/make_antenna_figure.py OUT.png CSV [CSV ...]
"""
import csv, statistics as st, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

INK, DIM, GRID = "#12151a", "#5b6472", "#dfe3e9"
C_ONE, C_MANY, C_REF = "#2f6fd0", "#1f9d6b", "#c2410c"


def main():
    out, csvs = sys.argv[1], sys.argv[2:]
    by = {}
    for fp in csvs:
        for r in csv.DictReader(open(fp)):
            by.setdefault(float(r["Rc"]), []).append(r)
    rc = sorted(by)
    agg = lambda k, f=st.mean: [f([float(r[k]) for r in by[x]]) for x in rc]

    mean_in, max_in = agg("meanInRange"), agg("maxInRange", max)
    inLo, inHi = agg("meanInRange", min), agg("meanInRange", max)
    frac2 = agg("frac2")
    seedPass, seedSnap = agg("seedPass"), agg("seedSnap")
    sHead, sPass, sSnap = agg("slotsHead"), agg("slotsPass"), agg("slotsSnap")
    wholeSnap = agg("wholeSnap")

    alt = {}
    for fp in csvs:
        try:
            for r in csv.DictReader(open(fp + ".alt.csv")):
                alt.setdefault(float(r["z"]), []).append(float(r["meanInRange"]))
        except OSError:
            pass

    fig, ax = plt.subplots(1, 4, figsize=(19.5, 4.5), dpi=170)

    # --- 1. how many heads one broadcast already covers ---------------------
    a = ax[0]
    a.fill_between(rc, inLo, inHi, color=C_ONE, alpha=.18, lw=0)
    a.plot(rc, mean_in, "-o", ms=3.4, color=C_ONE, lw=1.9,
           label="trung bình CL trong tầm")
    a.plot(rc, max_in, "s--", ms=3.0, color=C_MANY, lw=1.4,
           label="nhiều nhất cùng lúc")
    a.axhline(1.0, color=C_REF, ls=":", lw=1.3)
    a.annotate("1 = một búp sóng là đủ", (rc[len(rc) // 2], 1.0),
               textcoords="offset points", xytext=(0, 7), ha="center",
               fontsize=8, color=C_REF)
    a.set_xlabel("$R_c$ (m)", fontsize=9.5, color=INK)
    a.set_ylabel("số cụm trưởng", fontsize=9.5, color=INK)
    a.set_title("MỘT lần quảng bá phục vụ bao nhiêu CL\n"
                "(anten thứ hai phải vượt con số này)",
                fontsize=10.5, color=INK, pad=7)
    a.legend(fontsize=8, frameon=False)
    a.grid(alpha=.25, lw=.6)

    # --- 2. the free seeding ------------------------------------------------
    a = ax[1]
    a.plot(rc, [100 * x for x in seedSnap], "-o", ms=3.4, color=C_ONE, lw=1.9,
           label="% nút nhận từ MỘT gói (một thời điểm)")
    a.plot(rc, [100 * x for x in seedPass], color=C_ONE, lw=1.2, ls="-.",
           label="% nút nhận trong CẢ lượt bay")
    a.plot(rc, [100 * x for x in wholeSnap], "s--", ms=3.0, color=C_MANY, lw=1.4,
           label="% ô phủ TRỌN bằng một gói")
    a.plot(rc, [100 * x for x in frac2], color=DIM, lw=1.2, ls=":",
           label="% thời gian bay có ≥2 CL trong tầm")
    a.set_ylim(-3, 103)
    a.set_xlabel("$R_c$ (m)", fontsize=9.5, color=INK)
    a.set_ylabel("%", fontsize=9.5, color=INK)
    a.set_title("Một lượt bay GIEO SẴN bao nhiêu\nquảng bá tới mọi nút trong tầm",
                fontsize=10.5, color=INK, pad=7)
    a.legend(fontsize=7.5, frameon=False, loc="center left")
    a.grid(alpha=.25, lw=.6)

    # --- 3. what is left for the ground mesh --------------------------------
    a = ax[2]
    a.plot(rc, sHead, "-o", ms=3.4, color=C_REF, lw=1.9,
           label="lan từ MỘT cụm trưởng")
    a.plot(rc, sSnap, "-o", ms=3.4, color=C_MANY, lw=1.9,
           label="lan từ tập nút MỘT gói đã gieo")
    a.plot(rc, sPass, color=C_MANY, lw=1.2, ls="-.",
           label="lan từ tập cả lượt bay")
    a.set_xlabel("$R_c$ (m)", fontsize=9.5, color=INK)
    a.set_ylabel("khe MAC còn phải dùng", fontsize=9.5, color=INK)
    a.set_title("Phần việc còn lại của mạng mặt đất\n"
                "quảng bá đã xoá gần hết", fontsize=10.5, color=INK, pad=7)
    a.legend(fontsize=8, frameon=False)
    a.grid(alpha=.25, lw=.6)

    # --- 4. the caveat: this all rests on an unmeasured p(d) and on z -------
    a = ax[3]
    if alt:
        z = sorted(alt)
        m = [st.mean(alt[x]) for x in z]
        a.plot(z, m, "-o", ms=3.4, color=C_REF, lw=1.9)
        a.axhline(1.0, color=DIM, ls=":", lw=1.3)
        a.annotate("1 CL", (z[-1], 1.0), textcoords="offset points",
                   xytext=(-12, 7), ha="right", fontsize=8, color=DIM)
        a.set_xlabel("độ cao bay $z$ (m)", fontsize=9.5, color=INK)
        a.set_ylabel("số CL trong tầm", fontsize=9.5, color=INK)
    a.set_title("CẢNH BÁO: kết luận phụ thuộc $z$\n"
                "$z$ chưa phải tham số của p1", fontsize=10.5, color=C_REF, pad=7)
    a.grid(alpha=.25, lw=.6)

    for b in ax:
        b.tick_params(labelsize=8.5)
        for s in b.spines.values():
            s.set_color(GRID)
    fig.suptitle("Nhiều anten trên UAV có đổi được kết quả không?",
                 fontsize=12.5, color=INK, y=1.01)
    fig.text(0.5, -0.03,
             "Quảng bá một chiều, không báo nhận (I4): mọi nút trong p(d) nhận "
             "CÙNG nội dung CÙNG lúc. Anten thêm chỉ có ích khi các nút cần nội "
             "dung KHÁC nhau — điều mà I4 cố tình loại bỏ. "
             "Vùng mờ = trải 6 hạt giống. "
             "TẤT CẢ phụ thuộc p(d) với d50 = 190 m, vẫn là TODO(param) chưa đo, "
             "và vào độ cao bay (bảng phải).",
             ha="center", va="top", fontsize=8.3, color=DIM, wrap=True)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    print(f"  {out}")


if __name__ == "__main__":
    main()
