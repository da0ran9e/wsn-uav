"""One cluster, step by step through the River scheme (CLAUDE.md §8 item 65). Figures carry no text
(item 63); every number is printed for the doc.

    python3 tools/cluster_steps.py --data DATA --k 3 --bits PASS-bits-r1.bin --trace "TRACE/{s}" \
        --figs docs/figures --name c3

DATA: ck-{lattice,nodes-s35,path-s35}.csv (uav-coop-deploy). TRACE: uav-coop2-river --trace outputs for
s in rf (River, Circle prepared), ro (River, on demand), d (direct pull). Writes FIGS/NAME-step*.png:
  step0  roles and routes: CL (dots), CH (star), in-cell least-ETX trees, gateway pairs
  step1  after the pass: share of D held by each cell (all its nodes), and by its CL alone
  step2  Algorithm 1: Axe cells, darker = later on the track, and the flight path
  step3  Algorithm 2: River (light blue), Banks (green), Axe -> Bank cell paths
  step4  Algorithm 3: CL strength (light -> dark), critical cells (rings), CH (star)
  step5  Algorithm 4: each critical cell's Circle (outlined in its colour) and Bank -> member paths
  step6  in-cell gathering to the CLs (River, prepared): links, width ~ frames
  step7  after gathering, frames per link: River prepared | River on demand | direct
  step8  each critical CL's share of D over time: River prepared | on demand | direct (one colour per cell)
"""
import argparse, csv, math, os, statistics as st, sys
from collections import Counter, defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection
import numpy as np

from map_gen import corners, strip_text
from cluster_river_figure import load_geo

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uav-coop2/tools"))
from river_plan import plan, ring  # noqa: E402

INK, INK2, SURF, GREY = "#0b0b0b", "#52514e", "#fcfcfb", "#e6e5e1"
RIVER, BANK, AXE = "#c9dcf3", "#9fd8bf", "#1c5cab"
RAMP = matplotlib.colors.LinearSegmentedColormap.from_list("r", ["#f1f0eb", "#86b6ef", "#3987e5", "#0d366b"])
CAT = ["#1c5cab", "#1baf7a", "#eda100", "#e34948", "#8e5ad6", "#0d366b", "#52514e"]
PH = {"gather": "#3987e5", "bankfill": "#1baf7a", "circlefill": "#eda100", "pull": "#e34948", "control": "#52514e"}


def main():
    ap = argparse.ArgumentParser()
    for k in ("data", "bits", "trace", "figs", "name"):
        ap.add_argument("--" + k, required=True)
    ap.add_argument("--k", type=int, required=True)
    a = ap.parse_args()
    geo = load_geo(a.data, a.k)
    P = plan(geo)
    c, sel, path = geo["c"], geo["cells"], geo["path"]
    nodes = geo["nodes"]
    xy = np.array([[float(n["x"]), float(n["y"])] for n in nodes])
    cellof = [(int(n["q"]), int(n["r"])) for n in nodes]
    cl = {cellof[i]: i for i, n in enumerate(nodes) if n["isCL"] == "1"}
    ch = next(i for i, n in enumerate(nodes) if n["isCH"] == "1")
    members = defaultdict(list)
    for i, h in enumerate(cellof):
        members[h].append(i)
    crits = P["crit"]
    ccol = {k: CAT[i % len(CAT)] for i, k in enumerate(crits)}
    N = len(geo["uav"])
    tr = {s: a.trace.format(s=s) for s in ("rf", "ro", "d")}
    rows = lambda f: list(csv.DictReader(open(f)))

    xs = [c[h][0] for h in sel]; ys = [c[h][1] for h in sel]
    W = geo["w"]
    lim = (min(xs) - 1.5 * W, max(xs) + 1.5 * W, min(ys) - 1.5 * W, max(ys) + 1.5 * W)

    def base(ax, col):
        ax.add_collection(PolyCollection([corners(h) for h in sel], facecolors=[col.get(h, GREY) for h in sel],
                                         edgecolors=SURF, linewidths=.5, zorder=0))
        ax.set_xlim(lim[0], lim[1]); ax.set_ylim(lim[2], lim[3])
        ax.set_aspect("equal"); ax.set_facecolor(SURF); ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)

    def marks(ax, ring_only=False):
        for k in crits:
            star = k == P["ch"]
            ax.scatter(*c[k], s=260 if star else 130, marker="*" if star else "o", color="#ffffff",
                       edgecolors=ccol[k] if ring_only else INK, lw=1.6 if ring_only else 1.1, zorder=7)

    def track(ax, alpha=.8):
        ax.plot(*path.T, color=INK, lw=1.1, alpha=alpha, zorder=6)

    def save(fig, n):
        strip_text(fig)
        out = os.path.join(a.figs, f"{a.name}-step{n}.png")
        fig.savefig(out, facecolor=SURF, bbox_inches="tight", pad_inches=.06)
        plt.close(fig)

    def links(hops, hi=None, lw=3.5):
        cnt = Counter((int(r["from"]), int(r["to"])) for r in hops)
        if not cnt:
            return [], []
        hi = hi or max(cnt.values())
        return [[xy[u], xy[v]] for u, v in cnt], [.3 + lw * math.sqrt(n / hi) for n in cnt.values()]

    # ---------------- step 0: roles and routes
    routes = rows(tr["rf"] + "-routes.csv")
    pairs = rows(tr["rf"] + "-pairs.csv")
    fig, ax = plt.subplots(figsize=(7, 8), dpi=150, facecolor=SURF)
    base(ax, {})
    ax.add_collection(LineCollection([[xy[int(r["node"])], xy[int(r["next"])]] for r in routes if int(r["next"]) >= 0],
                                     colors=INK2, linewidths=.35, alpha=.7, zorder=2))
    ax.scatter(xy[:, 0], xy[:, 1], s=1.2, color=INK2, zorder=3)
    ax.add_collection(LineCollection([[xy[int(p["a"])], xy[int(p["b"])]] for p in pairs], colors=INK, linewidths=2.2,
                                     zorder=4))
    cls = [i for i in cl.values() if i != ch]
    ax.scatter(xy[cls, 0], xy[cls, 1], s=22, color="#ffffff", edgecolors=INK, lw=.9, zorder=5)
    ax.scatter(*xy[ch], s=260, marker="*", color="#ffffff", edgecolors=INK, lw=1.1, zorder=7)
    track(ax, .4)
    save(fig, 0)
    direct = sum(1 for r in routes if r["next"] != "-1" and int(r["next"]) in cl.values())
    print(f"step0: {len(sel)} cells, {len(nodes)} nodes, CH #{ch} in cell {cellof[ch]}, {len(cl)} CLs, "
          f"{len(pairs)} gateway pairs (min q {min(float(p['q']) for p in pairs):.2f}), "
          f"{100 * direct / len(routes):.0f} % of nodes one hop from their CL")

    # ---------------- step 1: after the pass
    bits = np.unpackbits(np.fromfile(a.bits, dtype=np.uint8).reshape(len(nodes), -1), axis=1, bitorder="little")[:, :N].astype(bool)
    inD = np.zeros(N, bool)
    for x in P["axe"]:
        s0, s1 = P["seg"][x][0], P["seg"][x][-1]
        inD[s0:s1 + 1] = bits[:, s0:s1 + 1].any(axis=0)
    Dn = int(inD.sum())
    cellHeld = {h: (bits[members[h]].any(axis=0) & inD).sum() / Dn for h in sel}
    clHeld = {h: (bits[cl[h]] & inD).sum() / Dn for h in sel}
    fig, axs = plt.subplots(1, 2, figsize=(12, 8), dpi=150, facecolor=SURF)
    base(axs[0], {h: RAMP(cellHeld[h]) for h in sel}); track(axs[0]); marks(axs[0])
    base(axs[1], {h: RAMP(clHeld[h]) for h in sel}); track(axs[1]); marks(axs[1])
    save(fig, 1)
    sent_in = sum(len(v) for v in P["seg"].values())
    print(f"step1: {N} packets sent along the whole path, {sent_in} over the cluster (Axe), D = {Dn} received by "
          f"someone; share of D per cell (all nodes): median {st.median(cellHeld.values()):.2f}, "
          f"min {min(cellHeld.values()):.2f}, max {max(cellHeld.values()):.2f}; per CL alone: median "
          f"{st.median(clHeld.values()):.2f}, min {min(clHeld.values()):.2f}, max {max(clHeld.values()):.2f}")
    print(f"        critical cells, share of D: " + ", ".join(
        f"{k} cell {cellHeld[k]:.2f} / CL {clHeld[k]:.2f}" for k in crits))

    # ---------------- step 2: Algorithm 1, Axe and Seg
    na = len(P["axe"])
    fig, ax = plt.subplots(figsize=(7, 8), dpi=150, facecolor=SURF)
    base(ax, {h: RAMP(.25 + .75 * i / max(1, na - 1)) for i, h in enumerate(P["axe"])}); track(ax)
    save(fig, 2)
    seglen = [len(P["seg"][h]) for h in P["axe"]]
    print(f"step2 (Alg. 1): {na} Axe cells in flight order; Seg sizes (packets) {seglen}; "
          f"mean {st.mean(seglen):.0f}, i.e. {st.mean(seglen) * 0.01:.2f} s of broadcast per Axe cell")

    # ---------------- step 3: Algorithm 2, River and Banks
    banks = {b for (x, s_), b in P["bank"].items() if b != x}
    col = {h: RIVER for h in P["river"]}
    col.update({b: BANK for b in banks}); col.update({h: AXE for h in P["axe"]})
    fig, ax = plt.subplots(figsize=(7, 8), dpi=150, facecolor=SURF)
    base(ax, col)
    ax.add_collection(LineCollection([[c[p_[i]] for i in range(len(p_))] for p_ in P["bpath"].values() if len(p_) > 1],
                                     colors=INK, linewidths=1, zorder=3))
    track(ax, .5)
    save(fig, 3)
    blen = [len(p_) - 1 for p_ in P["bpath"].values()]
    edge_banks = sum(1 for (x, s_), p_ in P["bpath"].items() if len(p_) - 1 < round(P["omega"] / W))
    print(f"step3 (Alg. 2): River {len(P['river'])} of {len(sel)} cells; {len(banks)} distinct Banks; Axe -> Bank "
          f"paths {Counter(blen)} cells long; {edge_banks} of {len(blen)} Banks cut short by the cluster edge "
          f"(omega = {P['omega'] / W:.2f} cell widths)")

    # ---------------- step 4: Algorithm 3, critical cells
    sc = {(int(x["q"]), int(x["r"])): float(x["score"]) for x in nodes if x["isCL"] == "1"}
    mu, sd = np.mean(list(sc.values())), np.std(list(sc.values()))
    hi = max(sc.values())
    fig, ax = plt.subplots(figsize=(7, 8), dpi=150, facecolor=SURF)
    base(ax, {h: RAMP(sc[h] / hi) for h in sel}); track(ax, .4); marks(ax, ring_only=True)
    save(fig, 4)
    why = []
    for k in crits:
        r_ = ("CH" if k == P["ch"] else "global" if sc[k] > mu + 2 * sd else "local")
        why.append(f"{k} score {sc[k]:.3f} (z {(sc[k] - mu) / sd:+.1f}, {r_})")
    print(f"step4 (Alg. 3): CL scores mean {mu:.3f}, sd {sd:.3f}; global > {mu + 2 * sd:.3f}, local > {mu + sd:.3f} "
          f"and the best within 2 rings; critical: " + "; ".join(why))

    # ---------------- step 5: Algorithm 4, Circles
    fig, ax = plt.subplots(figsize=(7, 8), dpi=150, facecolor=SURF)
    base(ax, {h: RIVER for h in P["river"]} | {b: BANK for b in banks} | {h: AXE for h in P["axe"]})
    plines, pcols = [], []
    for k in crits:
        for m, G, src in P["circle"][k]:
            ax.add_patch(plt.Polygon(corners(m) if False else [(c[m][0] + .8 * (x - c[m][0]), c[m][1] + .8 * (y - c[m][1]))
                                                            for x, y in corners(m)], fill=False, ec=ccol[k], lw=1.8, zorder=5))
            for (ax_, side, b, p_) in src:
                if len(p_) > 1:
                    plines.append([c[h] for h in p_]); pcols.append(ccol[k])
    ax.add_collection(LineCollection(plines, colors=pcols, linewidths=1, alpha=.8, zorder=4))
    marks(ax, ring_only=True); track(ax, .4)
    save(fig, 5)
    for k in crits:
        t = P["circle"][k]
        L = [len(p_) - 1 for m, G, src in t for (_, _, _, p_) in src]
        print(f"step5 (Alg. 4): {k}: {len(t)} members, {sum(len(G) for m, G, src in t)} Seg tasks, Bank -> member "
              f"paths mean {st.mean(L):.1f} cells (max {max(L)}); members {', '.join(str(m) for m, G, s in t)}")

    # ---------------- ns-3: hops, phases, completion
    hops = {s: rows(tr[s] + "-hops.csv") for s in tr}
    crit = {s: {(int(r["q"]), int(r["r"])): r for r in rows(tr[s] + "-crit.csv")} for s in tr}
    runs = {s: rows(tr[s] + "-runs.csv")[0] for s in tr}
    # step 6: gathering
    g = [r for r in hops["rf"] if r["phase"] == "gather"]
    fig, ax = plt.subplots(figsize=(7, 8), dpi=150, facecolor=SURF)
    base(ax, {})
    L_, Wd = links(g)
    ax.add_collection(LineCollection(L_, colors=PH["gather"], linewidths=Wd, alpha=.85, zorder=3))
    marks(ax); track(ax, .3)
    save(fig, 6)
    gdone = defaultdict(float)
    for r in g:
        h = cellof[int(r["to"])]
        gdone[h] = max(gdone[h], float(r["t"]))
    print(f"step6 (gather, River prepared): {len(g)} frames into {len(gdone)} CLs; last gather frame at "
          f"{max(gdone.values()):.1f} s; critical cells gather done at " +
          ", ".join(f"{k} {float(crit['rf'][k]['gatherDoneS']):.1f} s" for k in crits))
    # step 7: flows after gathering, three schemes
    fig, axs = plt.subplots(1, 3, figsize=(18, 8), dpi=150, facecolor=SURF)
    for ax, s in zip(axs, ("rf", "ro", "d")):
        base(ax, {h: RIVER for h in P["river"]} | {h: AXE for h in P["axe"]} if s != "d" else {h: AXE for h in P["axe"]})
        data = [r for r in hops[s] if r["phase"] in ("bankfill", "circlefill", "pull")]
        hi = max(Counter((r["phase"], r["from"], r["to"]) for r in data).values())
        for ph in ("control", "bankfill", "circlefill", "pull"):
            hh = [r for r in hops[s] if r["phase"] == ph]
            if ph == "control":
                L_, _ = links(hh)
                ax.add_collection(LineCollection(L_, colors=PH[ph], linewidths=.4, alpha=.5, zorder=2))
            else:
                L_, Wd = links(hh, hi, 4)
                ax.add_collection(LineCollection(L_, colors=PH[ph], linewidths=Wd, alpha=.85, zorder=4 if ph == "pull" else 3))
        marks(ax); track(ax, .3)
    save(fig, 7)
    for s, lab in (("rf", "River, prepared"), ("ro", "River, on demand"), ("d", "direct")):
        u = runs[s]
        print(f"step7 ({lab}): frames {u['hops']} = gather {u['gather']} + Axe->Bank {u['bankfill']} + Bank->Circle "
              f"{u['circlefill']} + pull {u['pull']} + requests {u['control']}; MAC give-ups {u['macFail']}")
    # step 8: completion
    fig, axs = plt.subplots(1, 3, figsize=(18, 5), dpi=150, facecolor=SURF, sharey=True)
    end = max(float(runs[s]["simS"]) for s in runs)
    for ax, s in zip(axs, ("rf", "ro", "d")):
        held = defaultdict(list)
        for r in rows(tr[s] + "-held.csv"):
            held[(int(r["q"]), int(r["r"]))].append(float(r["t"]))
        for k in crits:
            v = np.sort(held[k])
            n0 = int(np.searchsorted(v, 0, side="right"))
            ax.step(np.r_[0, v[n0:], end], np.r_[n0, np.arange(n0 + 1, len(v) + 1), len(v)] / Dn, where="post",
                    color=ccol[k], lw=1.8)
            gd = float(crit[s][k]["gatherDoneS"])
            ax.plot([gd], [np.searchsorted(v, gd, side="right") / Dn], marker="|", ms=10, color=ccol[k])
        ax.set_ylim(0, 1.02); ax.set_xlim(0, end)
        ax.grid(color=GREY, lw=.6); ax.set_facecolor(SURF); ax.tick_params(colors=INK2, labelsize=8)
        for sp in ax.spines.values():
            sp.set_visible(False)
    save(fig, 8)
    for k in crits:
        r = crit["rf"][k]
        print(f"step8: {k}: lacks {r['lackCL']} at its CL, {r['lackCell']} in the whole cell; done at " +
              ", ".join(f"{lab} {float(crit[s][k]['doneS']):.1f} s" for s, lab in (("rf", "prepared"), ("ro", "on demand"), ("d", "direct"))))


if __name__ == "__main__":
    main()
