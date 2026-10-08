"""The cluster right after the UAV pass: who holds what of a K-chunk file.

    python3 tools/state_report.py --deploy ../uav-coop/docs/data --bits "BITS/*-bits-r*.bin" \
        --K 2000 --data docs/data --figs docs/figures

--deploy  uav-coop docs/data (deploy-lattice.csv, deploy-nodes-s35.csv, deploy-path-s35.csv,
          pass-nodes.csv for the distance to the path)
--bits    uav-coop-pass --bits dumps: one row per node (nodes CSV order), packet s = bit s%8
          of byte s/8; packet s carries chunk s mod K
Writes DATA/state-nodes.csv (per node over all missions), DATA/state-cells.csv (per cell and
mission), DATA/state-r1-nodes.csv (first mission), and draws state-map.png (first mission)
and state-missions.png (all missions). With --redraw the figures come from DATA alone.

A cell is
  A  at least one of its nodes holds the whole file
  B  no node does, but together the cell holds it
  C  even together the cell lacks chunks
"""
import argparse, csv, glob, math, os, re, statistics as S

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np

INK, INK2, SURF = "#0b0b0b", "#52514e", "#fcfcfb"
RAMP = LinearSegmentedColormap.from_list("ramp", ["#f1f0eb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
LACK = LinearSegmentedColormap.from_list("lack", ["#f1f0eb", "#f6c3c3", "#e34948", "#8f1d1b"])
ZONE = {"A": "#1c5cab", "B": "#86b6ef", "C": "#e34948"}
ZONE_TXT = {"A": "A: có node đủ file", "B": "B: không node nào đủ, cả cell gộp lại đủ",
            "C": "C: cả cell gộp lại vẫn thiếu"}
EDGE_NB = [(0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1), (1, 0)]


def corners(cx, cy, R):
    return [(cx + R * math.cos(math.radians(30 + 60 * k)), cy + R * math.sin(math.radians(30 + 60 * k)))
            for k in range(6)]


def chunks(path, n, K):
    """Per node, which of the K chunks it holds after one mission (n x K bool)."""
    raw = np.fromfile(path, dtype=np.uint8)
    assert raw.size % n == 0, path
    got = np.unpackbits(raw.reshape(n, -1), axis=1, bitorder="little")
    blocks = -(-got.shape[1] // K)
    pad = np.zeros((n, blocks * K), dtype=np.uint8)
    pad[:, :got.shape[1]] = got
    return pad.reshape(n, blocks, K).any(axis=1)


def collect(a):
    nodes = list(csv.DictReader(open(os.path.join(a.deploy, "deploy-nodes-s35.csv"))))
    dpath = {r["id"]: r["dPathM"] for r in csv.DictReader(open(os.path.join(a.deploy, "pass-nodes.csv")))}
    n, K = len(nodes), a.K
    cell = [(int(r["q"]), int(r["r"])) for r in nodes]
    cells = sorted(set(cell))
    members = {c: np.array([i for i in range(n) if cell[i] == c]) for c in cells}
    files = sorted(glob.glob(a.bits), key=lambda p: int(re.search(r"-r(\d+)\.bin$", p).group(1)))
    assert files, a.bits
    held = np.zeros((len(files), n), dtype=np.int32)
    rows = []
    for m, p in enumerate(files):
        run = int(re.search(r"-r(\d+)\.bin$", p).group(1))
        H = chunks(p, n, K)
        held[m] = H.sum(axis=1)
        for c in cells:
            ix = members[c]
            union = int(H[ix].any(axis=0).sum())
            full = int((held[m, ix] == K).sum())
            zone = "A" if full else ("B" if union == K else "C")
            rows.append({"run": run, "q": c[0], "r": c[1], "nodes": len(ix), "nodesFull": full,
                         "bestChunks": int(held[m, ix].max()), "unionChunks": union, "lack": K - union,
                         "zone": zone})
        if m == 0:
            with open(os.path.join(a.data, "state-r1-nodes.csv"), "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["id", "chunks"])
                for i in range(n):
                    w.writerow([nodes[i]["id"], held[m, i]])
    with open(os.path.join(a.data, "state-cells.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(a.data, "state-nodes.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "x", "y", "q", "r", "isCH", "isCL", "dPathM", "missions", "K",
                    "chunksMean", "chunksP10", "chunksP90", "pFull"])
        for i, r in enumerate(nodes):
            h = held[:, i]
            w.writerow([r["id"], r["x"], r["y"], r["q"], r["r"], r["isCH"], r["isCL"], dpath[r["id"]],
                        len(files), K, f"{h.mean():.2f}", f"{np.percentile(h, 10):.1f}",
                        f"{np.percentile(h, 90):.1f}", f"{(h == K).mean():.4f}"])


def report(a):
    nodes = list(csv.DictReader(open(os.path.join(a.data, "state-nodes.csv"))))
    cells = list(csv.DictReader(open(os.path.join(a.data, "state-cells.csv"))))
    r1 = {r["id"]: int(r["chunks"]) for r in csv.DictReader(open(os.path.join(a.data, "state-r1-nodes.csv")))}
    K, runs = int(nodes[0]["K"]), sorted({int(r["run"]) for r in cells})
    nrun, ncell = len(runs), len(cells) // len(runs)
    per = {}
    for r in cells:
        per.setdefault(int(r["run"]), []).append(r)
    zc = {z: [sum(r["zone"] == z for r in per[m]) for m in runs] for z in "ABC"}
    full = [sum(int(r["nodesFull"]) for r in per[m]) for m in runs]
    lack = [sum(int(r["lack"]) for r in per[m]) for m in runs]
    frac = [int(r["unionChunks"]) / K for r in cells]
    print(f"K = {K}, {len(nodes)} nodes, {ncell} cells, {nrun} missions")
    print(f"  nodes holding the whole file: mean {S.mean(full):.0f} ({100 * S.mean(full) / len(nodes):.1f} %), "
          f"min {min(full)}, max {max(full)}")
    m = np.array([float(r["chunksMean"]) for r in nodes]) / K
    for lo, hi in [(0, .25), (.25, .5), (.5, .75), (.75, .9), (.9, 1), (1, 1.01)]:
        print(f"  nodes holding {100 * lo:3.0f}-{100 * min(hi, 1):3.0f} % on average: {((m >= lo) & (m < hi)).sum()}")
    for z in "ABC":
        print(f"  cells in zone {z}: mean {S.mean(zc[z]):.1f}, min {min(zc[z])}, max {max(zc[z])}  ({ZONE_TXT[z]})")
    lackC = [int(r["lack"]) for r in cells if r["zone"] == "C"]
    if lackC:
        print(f"  zone C cells lack: median {S.median(lackC):.0f}, max {max(lackC)} chunks of {K}; "
              f"total per mission mean {S.mean(lack):.0f}")
    print(f"  cell union / K: min {min(frac):.3f}")
    draw(a, nodes, cells, r1, K, runs)


def draw(a, nodes, cells, r1, K, runs):
    D = a.deploy
    lat = list(csv.DictReader(open(os.path.join(D, "deploy-lattice.csv"))))
    c = {(int(x["q"]), int(x["r"])): (float(x["cx"]), float(x["cy"])) for x in lat}
    w = math.dist(c[(0, 0)], c[(1, 0)])
    R = w / math.sqrt(3)
    sel = sorted((int(x["q"]), int(x["r"])) for x in lat if x["selected"] == "1")
    segs = [[corners(*c[h], R)[k], corners(*c[h], R)[(k + 1) % 6]]
            for h in sel for k, (dq, dr) in enumerate(EDGE_NB) if (h[0] + dq, h[1] + dr) not in sel]
    path = list(csv.DictReader(open(os.path.join(D, "deploy-path-s35.csv"))))
    px, py = [float(p["x"]) for p in path], [float(p["y"]) for p in path]
    ch = next(r for r in nodes if r["isCH"] == "1")
    xs = [c[h][0] for h in sel]; ys = [c[h][1] for h in sel]
    nx, ny = np.array([float(r["x"]) for r in nodes]), np.array([float(r["y"]) for r in nodes])

    def frame(ax, title):
        ax.add_collection(LineCollection(segs, colors=INK2, linewidths=.9, zorder=2))
        ax.plot(px, py, color=INK, lw=1.1, alpha=.75, zorder=4)
        ax.annotate("", xy=(px[-1], py[-1]), xytext=(px[-25], py[-25]),
                    arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.1), zorder=4)
        ax.scatter([float(ch["x"])], [float(ch["y"])], s=110, marker="*", color="#e34948", edgecolors=INK,
                   linewidths=.6, zorder=6)
        ax.set_xlim(min(xs) - w, max(xs) + w); ax.set_ylim(min(ys) - w, max(ys) + w)
        ax.set_aspect("equal"); ax.set_facecolor(SURF); ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.set_title(title, loc="left", fontsize=10, color=INK)

    def cellfill(ax, colours):
        ax.add_collection(PolyCollection([corners(*c[h], R) for h in sel], facecolors=[colours[h] for h in sel],
                                         edgecolors="#ffffff", linewidths=.6, zorder=1))

    def bar(ax, cmap, vmax, label):
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0, vmax))
        cb = plt.colorbar(sm, ax=ax, shrink=.65, pad=.01)
        cb.ax.tick_params(labelsize=7, colors=INK2); cb.outline.set_visible(False)
        cb.set_label(label, fontsize=8, color=INK2)

    first = {(int(r["q"]), int(r["r"])): r for r in cells if int(r["run"]) == runs[0]}
    nrun = len(runs)
    # Mission 1
    fig, ax = plt.subplots(1, 3, figsize=(19, 7.4), dpi=150, facecolor=SURF)
    v = np.array([r1[r["id"]] for r in nodes])
    full = v == K
    frame(ax[0], f"Mỗi node giữ bao nhiêu mảnh (lượt bay {runs[0]})\n"
                 f"viền đen: node đủ cả {K} mảnh ({full.sum()} / {len(v)})")
    ax[0].scatter(nx[~full], ny[~full], c=v[~full], cmap=RAMP, vmin=0, vmax=K, s=7, lw=0, zorder=3)
    ax[0].scatter(nx[full], ny[full], c=v[full], cmap=RAMP, vmin=0, vmax=K, s=11, edgecolors=INK, lw=.5, zorder=3)
    bar(ax[0], RAMP, K, "mảnh khác nhau đã có")
    cellfill(ax[1], {h: ZONE[first[h]["zone"]] for h in sel})
    for h in sel:
        k = int(first[h]["nodesFull"])
        if k:
            ax[1].text(*c[h], str(k), fontsize=6, ha="center", va="center", color="#ffffff", zorder=5)
    n_z = {z: sum(first[h]["zone"] == z for h in sel) for z in "ABC"}
    frame(ax[1], "Cell sau lượt bay\nsố trong cell: số node đủ file")
    ax[1].legend(handles=[Patch(color=ZONE[z], label=f"{ZONE_TXT[z]} ({n_z[z]})") for z in "ABC"],
                 loc="upper left", bbox_to_anchor=(0, .02), fontsize=7.5, frameon=False, labelcolor=INK2)
    lk = {h: int(first[h]["lack"]) for h in sel}
    vmax = max(1, max(lk.values()))
    cellfill(ax[2], {h: LACK(lk[h] / vmax) for h in sel})
    for h in sel:
        if lk[h]:
            ax[2].text(*c[h], str(lk[h]), fontsize=6, ha="center", va="center", color=INK, zorder=5)
    frame(ax[2], f"Cả cell gộp lại còn thiếu bao nhiêu mảnh\n"
                 f"{sum(1 for h in sel if lk[h])} cell thiếu, tổng {sum(lk.values())} mảnh")
    bar(ax[2], LACK, vmax, f"mảnh thiếu (/ {K})")
    fig.suptitle(f"Ngay sau khi UAV bay qua — file K = {K} mảnh, đường bay cơ sở (nét đen, mũi tên: hướng bay; "
                 f"sao: CH)", x=.01, ha="left", fontsize=12.5, color=INK)
    fig.tight_layout(rect=(0, 0, 1, .95))
    out = os.path.join(a.figs, "state-map.png")
    fig.savefig(out, facecolor=SURF); print(f"  {out}")
    # All missions
    fig, ax = plt.subplots(1, 3, figsize=(19, 7.4), dpi=150, facecolor=SURF)
    p = np.array([float(r["pFull"]) for r in nodes])
    frame(ax[0], f"Xác suất node đủ file qua {nrun} lượt bay")
    ax[0].scatter(nx, ny, c=p, cmap=RAMP, vmin=0, vmax=1, s=7, lw=0, zorder=3)
    bar(ax[0], RAMP, 1, "tỉ lệ lượt bay node đủ")
    pz = {h: {z: 0 for z in "ABC"} for h in sel}
    lm = {h: 0.0 for h in sel}
    for r in cells:
        h = (int(r["q"]), int(r["r"]))
        pz[h][r["zone"]] += 1 / nrun
        lm[h] += int(r["lack"]) / nrun
    cellfill(ax[1], {h: ZONE[max("ABC", key=lambda z: pz[h][z])] for h in sel})
    for h in sel:
        z = max("ABC", key=lambda z: pz[h][z])
        if pz[h][z] < .995:
            ax[1].text(*c[h], f"{100 * pz[h][z]:.0f}", fontsize=6, ha="center", va="center",
                       color="#ffffff" if z != "B" else INK, zorder=5)
    frame(ax[1], f"Vùng thường gặp nhất của mỗi cell ({nrun} lượt bay)\nsố: % lượt bay ở vùng đó (bỏ trống: luôn)")
    ax[1].legend(handles=[Patch(color=ZONE[z], label=ZONE_TXT[z]) for z in "ABC"],
                 loc="upper left", bbox_to_anchor=(0, .02), fontsize=7.5, frameon=False, labelcolor=INK2)
    vmax = max(1, max(lm.values()))
    cellfill(ax[2], {h: LACK(lm[h] / vmax) for h in sel})
    for h in sel:
        if lm[h] >= .5:
            ax[2].text(*c[h], f"{lm[h]:.0f}", fontsize=6, ha="center", va="center", color=INK, zorder=5)
    frame(ax[2], f"Cả cell gộp lại còn thiếu (TB {nrun} lượt bay)")
    bar(ax[2], LACK, vmax, f"mảnh thiếu (/ {K})")
    fig.suptitle(f"Ngay sau khi UAV bay qua — {nrun} lượt bay độc lập, K = {K}", x=.01, ha="left",
                 fontsize=12.5, color=INK)
    fig.tight_layout(rect=(0, 0, 1, .95))
    out = os.path.join(a.figs, "state-missions.png")
    fig.savefig(out, facecolor=SURF); print(f"  {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deploy", required=True)
    ap.add_argument("--bits")
    ap.add_argument("--K", type=int, default=2000)
    ap.add_argument("--data", required=True)
    ap.add_argument("--figs", required=True)
    ap.add_argument("--redraw", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.data, exist_ok=True); os.makedirs(a.figs, exist_ok=True)
    if not a.redraw:
        collect(a)
    report(a)


if __name__ == "__main__":
    main()
