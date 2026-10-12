"""Step-by-step figures of the ns-3 River trial (uav-coop2-river --trace), one mission.

    python3 tools/river_ns3_figures.py --deploy ../uav-coop/docs/data --path docs/data/path-a180.csv \
        --plan docs/data/river-plan.txt --bits BITS/p1-bits-r1.bin --trace "TRACE/{s}" --figs docs/figures

--trace  prefix pattern of the traces, {s} in rf (River, full Circle), ro (River, on-demand Circle), d (direct)
Draws
  ns3-setup.png      step 0: channels of the PECEE grid, gateway pairs, in-cell least-ETX routes
  ns3-pass.png       step 1: what each CL / each cell holds after the pass
  ns3-gather.png     step 2: in-cell gathering to the CL (River, full)
  ns3-flows.png      step 3: frames after gathering, per scheme (Bank fill, Circle fill, pull)
  ns3-snapshots.png  step 3: what each CL holds over time, per scheme
  ns3-timeline.png   step 4: each critical CL's holding over time, per scheme
  ns3-phases.png     frames per phase and MAC give-ups, per scheme
"""
import argparse, csv, math, os, sys
from collections import Counter, defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from river_plan import load, plan  # noqa: E402

INK, INK2, SURF, GREY, FAINT = "#0b0b0b", "#52514e", "#fcfcfb", "#e6e5e1", "#c9dcf3"
RAMP = matplotlib.colors.LinearSegmentedColormap.from_list("r", ["#f1f0eb", "#86b6ef", "#3987e5", "#0d366b"])
TIME = matplotlib.colors.LinearSegmentedColormap.from_list("t", ["#f6c3c3", "#e34948", "#8f1d1b"])
CAT = ["#0d366b", "#3987e5", "#1baf7a", "#eda100", "#e34948", "#8e5ad6", "#52514e"]
SCHEMES = [("rf", "River — Circle chuẩn bị sẵn", "#1c5cab"), ("ro", "River — Circle chỉ lấy khi được hỏi", "#1baf7a"),
           ("d", "Kéo thẳng từ Axe (so sánh)", "#eda100")]
PHASES = [("gather", "gom trong cell", "#3987e5"), ("bankfill", "Axe → Bank", "#1baf7a"),
          ("circlefill", "Bank → Circle", "#eda100"), ("pull", "→ critical cell", "#e34948"),
          ("control", "yêu cầu", "#52514e")]
EDGE_NB = [(0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1), (1, 0)]


def corners(cx, cy, R):
    return [(cx + R * math.cos(math.radians(30 + 60 * k)), cy + R * math.sin(math.radians(30 + 60 * k)))
            for k in range(6)]


def rows(f):
    return list(csv.DictReader(open(f)))


def main():
    ap = argparse.ArgumentParser()
    for k in ("deploy", "path", "plan", "bits", "trace", "figs"):
        ap.add_argument("--" + k, required=True)
    a = ap.parse_args()

    geo = load(a.deploy, a.path)
    P = plan(geo)
    c, w, R, sel = geo["c"], geo["w"], geo["R"], geo["cells"]
    S_ = set(sel)
    nodes = geo["nodes"]
    xy = np.array([[float(n["x"]), float(n["y"])] for n in nodes])
    cell = [(int(n["q"]), int(n["r"])) for n in nodes]
    cl = {cell[i]: i for i, n in enumerate(nodes) if n["isCL"] == "1"}
    members = defaultdict(list)
    for i, h in enumerate(cell):
        members[h].append(i)
    segs = [[corners(*c[h], R)[k], corners(*c[h], R)[(k + 1) % 6]]
            for h in sel for k, (dq, dr) in enumerate(EDGE_NB) if (h[0] + dq, h[1] + dr) not in S_]
    xs = [c[h][0] for h in sel]; ys = [c[h][1] for h in sel]
    path = geo["path"]
    crits = P["crit"]
    cname = {k: f"({k[0]},{k[1]})" + (" CH" if k == P["ch"] else "") for k in crits}
    ccol = {k: CAT[i % len(CAT)] for i, k in enumerate(crits)}

    # the plan and the pass
    axe = []
    N = 0
    for line in open(a.plan):
        t = line.split()
        if t[0] == "N":
            N = int(t[1])
        elif t[0] == "AXE":
            axe.append(((int(t[1]), int(t[2])), int(t[3]), int(t[4])))
    bits = np.unpackbits(np.fromfile(a.bits, dtype=np.uint8).reshape(len(nodes), -1), axis=1,
                         bitorder="little")[:, :N].astype(bool)
    inD = np.zeros(N, bool)
    for _, f, l in axe:
        inD[f:l + 1] = bits[:, f:l + 1].any(axis=0)
    Dn = int(inD.sum())
    clHeld0 = {h: int((bits[cl[h]] & inD).sum()) for h in sel}
    cellHeld0 = {h: int((bits[members[h]].any(axis=0) & inD).sum()) for h in sel}

    tr = {}
    for s, _, _ in SCHEMES:
        p = a.trace.format(s=s)
        tr[s] = dict(hops=rows(p + "-hops.csv"), held=rows(p + "-held.csv"), crit=rows(p + "-crit.csv"),
                     runs=rows(p + "-runs.csv")[0], routes=rows(p + "-routes.csv"), pairs=rows(p + "-pairs.csv"))
    used = {cell[int(r["node"])] for r in tr["rf"]["routes"]}

    def frame(ax, col, title, track=.6, lim=None):
        ax.add_collection(PolyCollection([corners(*c[h], R) for h in sel], facecolors=[col[h] for h in sel],
                                         edgecolors="#ffffff", linewidths=.7, zorder=0))
        ax.add_collection(LineCollection(segs, colors=INK2, linewidths=.9, zorder=1))
        if track:
            ax.plot(path[:, 0], path[:, 1], color=INK, lw=1, alpha=track, zorder=6)
        if lim:
            ax.set_xlim(lim[0], lim[1]); ax.set_ylim(lim[2], lim[3])
        else:
            ax.set_xlim(min(xs) - w, max(xs) + w); ax.set_ylim(min(ys) - w, max(ys) + w)
        ax.set_aspect("equal"); ax.set_facecolor(SURF); ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.set_title(title, loc="left", fontsize=9.5, color=INK)

    def marks(ax, color="#ffffff", s=90):
        for k in crits:
            ax.scatter(*c[k], s=s, marker="*" if k == P["ch"] else "o", color=color, edgecolors=INK, lw=1, zorder=8)

    def bar(ax, cmap, lo, hi, label):
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(lo, hi))
        cb = plt.colorbar(sm, ax=ax, shrink=.6, pad=.01)
        cb.ax.tick_params(labelsize=7, colors=INK2); cb.outline.set_visible(False)
        cb.set_label(label, fontsize=8, color=INK2)

    def save(fig, name):
        out = os.path.join(a.figs, name)
        fig.savefig(out, facecolor=SURF, bbox_inches="tight", pad_inches=.08)
        plt.close(fig)
        print(f"  {out}")

    def links(hops, lw_max=3.0, hi=None):
        cnt = Counter((int(r["from"]), int(r["to"])) for r in hops)
        if not cnt:
            return [], []
        hi = hi or max(cnt.values())
        lines = [[xy[u], xy[v]] for (u, v) in cnt]
        widths = [.3 + lw_max * math.sqrt(n / hi) for n in cnt.values()]
        return lines, widths

    # step 0: channels, gateway pairs, routes
    pairs = tr["rf"]["pairs"]
    fig, axs = plt.subplots(1, 2, figsize=(13, 7), dpi=150, facecolor=SURF,
                            gridspec_kw=dict(width_ratios=[1, 1.05]))
    chcol = {h: (matplotlib.colors.to_rgba(CAT[(h[0] + 3 * h[1]) % 7], .30) if h in used else GREY) for h in sel}
    frame(axs[0], chcol, "Bước 0 — mạng mô phỏng: kênh theo lưới cell PECEE\n"
                         "số trong cell = kênh 802.15.4 của cell (11–17, cùng kênh chỉ khi cách 3 cell); "
                         "xám = cell không mô phỏng\nđoạn đen = cặp gateway (kênh riêng 18–26), đỏ = cặp yếu (q < 0,5)")
    for h in sel:
        if h in used:
            axs[0].text(*c[h], str(11 + (h[0] + 3 * h[1]) % 7), ha="center", va="center", fontsize=6, color=INK2,
                        zorder=3)
    gl = [[xy[int(p["a"])], xy[int(p["b"])]] for p in pairs]
    weak = [float(p["q"]) < .5 for p in pairs]
    axs[0].add_collection(LineCollection(gl, colors=["#e34948" if x else INK for x in weak],
                                         linewidths=[2.2 if x else 1.2 for x in weak], zorder=5))
    marks(axs[0])
    # zoom on the CH and its neighbourhood
    ch = P["ch"]
    zx, zy = c[ch]
    L = 2.3 * w
    lim = (zx - L, zx + L, zy - L, zy + L)
    frame(axs[1], {h: (FAINT if h in used else GREY) for h in sel},
          f"… phóng to quanh cell CH {ch}: đường trong cell theo ETX nhỏ nhất trên kênh của lượt bay\n"
          "chấm = node, chấm lớn = CL, đường xám = hop kế tiếp về CL; đoạn đen/đỏ = cặp gateway",
          track=.35, lim=lim)
    rl = [[xy[int(r["node"])], xy[int(r["next"])]] for r in tr["rf"]["routes"] if int(r["next"]) >= 0]
    axs[1].add_collection(LineCollection(rl, colors=INK2, linewidths=.6, alpha=.8, zorder=3))
    inz = [i for i in range(len(nodes)) if abs(xy[i, 0] - zx) < L and abs(xy[i, 1] - zy) < L]
    axs[1].scatter(xy[inz, 0], xy[inz, 1], s=5, color=INK2, zorder=4)
    cls = [cl[h] for h in sel if abs(c[h][0] - zx) < L and abs(c[h][1] - zy) < L]
    axs[1].scatter(xy[cls, 0], xy[cls, 1], s=45, color="#ffffff", edgecolors=INK, lw=1.2, zorder=6)
    axs[1].add_collection(LineCollection(gl, colors=["#e34948" if x else INK for x in weak],
                                         linewidths=[2.6 if x else 1.8 for x in weak], zorder=5))
    for h in sel:
        if abs(c[h][0] - zx) < L - w / 3 and abs(c[h][1] - zy) < L - w / 3:
            axs[1].text(c[h][0], c[h][1] - .42 * w, f"kênh {11 + (h[0] + 3 * h[1]) % 7}", ha="center", fontsize=6.5,
                        color=INK2, zorder=7)
    axs[1].scatter(*c[ch], s=200, marker="*", color="#ffffff", edgecolors=INK, lw=1, zorder=8)
    save(fig, "ns3-setup.png")

    # step 1: after the pass
    fig, axs = plt.subplots(1, 2, figsize=(12, 7), dpi=150, facecolor=SURF)
    frame(axs[0], {h: RAMP(clHeld0[h] / Dn) for h in sel},
          f"Bước 1 — ngay sau lượt bay (pass ns-3, lượt 1)\nphần của D (|D| = {Dn} gói) mà CL tự nhận được")
    bar(axs[0], RAMP, 0, 1, "tỉ lệ của D")
    frame(axs[1], {h: RAMP(cellHeld0[h] / Dn) for h in sel},
          "… mà cả cell nhận được (gộp mọi node)\n= phần CL có sau khi gom trong cell xong")
    bar(axs[1], RAMP, 0, 1, "tỉ lệ của D")
    for ax in axs:
        marks(ax)
    save(fig, "ns3-pass.png")

    # step 2: in-cell gathering (River, full)
    g = [r for r in tr["rf"]["hops"] if r["phase"] == "gather"]
    gdone = {}
    for r in g:
        h = cell[int(r["to"])]
        gdone[h] = max(gdone.get(h, 0), float(r["t"]))
    hi = max(gdone.values())
    fig, axs = plt.subplots(1, 2, figsize=(13, 7), dpi=150, facecolor=SURF)
    frame(axs[0], {h: (FAINT if h in used else GREY) for h in sel},
          f"Bước 2 — gom trong cell về CL (River, Circle chuẩn bị sẵn)\n{len(g)} khung; nét đậm = liên kết "
          "mang nhiều khung", track=.3)
    lines, widths = links(g)
    axs[0].add_collection(LineCollection(lines, colors=PHASES[0][2], linewidths=widths, alpha=.85, zorder=3))
    marks(axs[0])
    frame(axs[1], {h: (TIME(gdone[h] / hi) if h in gdone else (FAINT if h in used else GREY)) for h in sel},
          "… thời điểm cell gom xong (khung gom cuối cùng tới CL)\nxanh nhạt = cell không cần gom", track=.3)
    bar(axs[1], TIME, 0, hi, "s sau khi UAV rời cụm")
    marks(axs[1])
    save(fig, "ns3-gather.png")

    # step 3: flows after gathering, per scheme
    fig, axs = plt.subplots(1, 3, figsize=(18, 7), dpi=150, facecolor=SURF)
    for ax, (s, t, _) in zip(axs, SCHEMES):
        frame(ax, {h: (FAINT if h in used else GREY) for h in sel}, "", track=.3)
        n = {}
        data = [r for r in tr[s]["hops"] if r["phase"] in ("bankfill", "circlefill", "pull")]
        hi = max(Counter((r["phase"], r["from"], r["to"]) for r in data).values())
        for ph, lab, colr in PHASES[1:]:
            hh = [r for r in tr[s]["hops"] if r["phase"] == ph]
            n[ph] = len(hh)
            if ph == "control":   # requests: thin, underneath
                lines, _ = links(hh)
                ax.add_collection(LineCollection(lines, colors=colr, linewidths=.4, alpha=.5, zorder=2))
                continue
            lines, widths = links(hh, 4.0, hi)
            ax.add_collection(LineCollection(lines, colors=colr, linewidths=widths, alpha=.85,
                                             zorder=4 if ph == "pull" else 3))
        marks(ax)
        ax.set_title(f"Bước 3 — {t}\nAxe→Bank {n['bankfill']}, Bank→Circle {n['circlefill']}, "
                     f"→critical {n['pull']}, yêu cầu {n['control']} khung", loc="left", fontsize=9.5, color=INK)
    axs[0].legend(handles=[Line2D([], [], color=colr, lw=.6 if ph == "control" else 3, label=lab)
                           for ph, lab, colr in PHASES[1:]],
                  loc="lower left", fontsize=8, frameon=False, labelcolor=INK2)
    save(fig, "ns3-flows.png")

    # step 3: snapshots of what each CL holds
    arr = {}
    for s, _, _ in SCHEMES:
        d = defaultdict(list)
        for r in tr[s]["held"]:
            d[(int(r["q"]), int(r["r"]))].append(float(r["t"]))
        arr[s] = {h: np.sort(v) for h, v in d.items()}
    end = max(float(tr[s]["runs"]["simS"]) for s, _, _ in SCHEMES)
    times = [0, 5, 10, 20, end]
    fig, axs = plt.subplots(3, 5, figsize=(20, 12.5), dpi=120, facecolor=SURF)
    for i, (s, t, _) in enumerate(SCHEMES):
        for j, tt in enumerate(times):
            col = {h: RAMP((np.searchsorted(arr[s][h], tt, side="right") if h in arr[s] else clHeld0[h]) / Dn)
                   for h in sel}
            frame(axs[i, j], col, (f"{t}\n" if j == 0 else "\n") + f"t = {tt:.0f} s", track=.3)
            marks(axs[i, j], s=50)
    fig.suptitle("Bước 3 — phần D mà CL của mỗi cell có theo thời gian (lượt 1); "
                 "★ CH, ● critical cell", x=.01, ha="left", fontsize=11, color=INK)
    sm = plt.cm.ScalarMappable(cmap=RAMP, norm=plt.Normalize(0, 1))
    cb = fig.colorbar(sm, ax=list(axs.ravel()), shrink=.4, pad=.01)
    cb.ax.tick_params(labelsize=8, colors=INK2); cb.outline.set_visible(False)
    cb.set_label("tỉ lệ của D", fontsize=9, color=INK2)
    save(fig, "ns3-snapshots.png")

    # step 4: critical CLs over time
    fig, axs = plt.subplots(1, 3, figsize=(18, 4.8), dpi=150, facecolor=SURF, sharey=True)
    axs[0].set_ylim(.4, 1.02)
    for ax, (s, t, _) in zip(axs, SCHEMES):
        cr = {(int(r["q"]), int(r["r"])): r for r in tr[s]["crit"]}
        for k in crits:
            v = arr[s].get(k, np.zeros(0))
            n0 = int(np.searchsorted(v, 0, side="right"))
            ax.step(np.r_[0, v[n0:], end], np.r_[n0, np.arange(n0 + 1, len(v) + 1), len(v)] / Dn,
                    where="post", color=ccol[k], lw=1.5, label=cname[k])
            gd = float(cr[k]["gatherDoneS"])
            ax.plot([gd], [np.searchsorted(v, gd, side="right") / Dn], marker="|", ms=9, color=ccol[k])
        ax.set_title(f"Bước 4 — phần D mà CL của critical cell có\n{t}; vạch | = xong gom trong cell",
                     loc="left", fontsize=9.5, color=INK)
        ax.set_xlabel("thời gian sau khi UAV rời cụm, s", fontsize=8.5, color=INK2)
        ax.grid(color=GREY, lw=.6); ax.set_facecolor(SURF); ax.tick_params(colors=INK2, labelsize=8)
        for sp in ax.spines.values():
            sp.set_visible(False)
    axs[0].set_ylabel("tỉ lệ của D", fontsize=8.5, color=INK2)
    axs[2].legend(frameon=False, fontsize=7.5, labelcolor=INK2, loc="lower right")
    save(fig, "ns3-timeline.png")

    # frames per phase
    fig, axs = plt.subplots(1, 2, figsize=(13, 3.2), dpi=150, facecolor=SURF, gridspec_kw=dict(width_ratios=[3, 1]))
    ax = axs[0]
    for i, (s, t, _) in enumerate(SCHEMES):
        left = 0
        for ph, lab, colr in PHASES:
            v = int(tr[s]["runs"][ph]) / 1000
            ax.barh(i, v, left=left, color=colr, height=.6, edgecolor=SURF, lw=2, label=lab if i == 0 else None)
            if v > 4:
                ax.text(left + v / 2, i, f"{v:.0f}k", ha="center", va="center", fontsize=7.5, color="#ffffff")
            left += v
        ax.text(left + 1, i, f"{left:.0f}k", va="center", fontsize=8, color=INK)
    ax.set_yticks(range(3)); ax.set_yticklabels([t for _, t, _ in SCHEMES], fontsize=8, color=INK)
    ax.invert_yaxis()
    ax.set_xlabel("khung truyền thành công (nghìn), lượt 1", fontsize=8.5, color=INK2)
    ax.legend(frameon=False, fontsize=7.5, labelcolor=INK2, ncol=5, loc="upper center", bbox_to_anchor=(.5, 1.25))
    ax2 = axs[1]
    ax2.barh(range(3), [int(tr[s]["runs"]["macFail"]) / 1000 for s, _, _ in SCHEMES],
             color=[colr for _, _, colr in SCHEMES], height=.6)
    ax2.set_yticks([]); ax2.invert_yaxis()
    ax2.set_xlabel("MAC bỏ cuộc (nghìn khung)", fontsize=8.5, color=INK2)
    for x in (ax, ax2):
        x.grid(axis="x", color=GREY, lw=.6); x.set_facecolor(SURF); x.tick_params(colors=INK2, labelsize=8)
        for sp in x.spines.values():
            sp.set_visible(False)
    save(fig, "ns3-phases.png")


if __name__ == "__main__":
    main()
