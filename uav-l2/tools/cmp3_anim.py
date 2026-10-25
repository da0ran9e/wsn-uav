"""CHORD (P*), FC and DN on one map side by side, in each channel (CLAUDE.md §8 item 168), for the replay page
docs/anim/cmp3-<map>-replay.html (docs/anim/cmp3-head.html + cmp3-body.html).

    python3 tools/cmp3_anim.py --works open=W1,r500=W2,r200=W3,r100=W4 --l1 L1 --out docs/anim/cmp3-k8-s1.json \
        [--draw D] [--html docs/anim/cmp3-k8-s1-replay.html]

The WORKs are the mission folders of one map, one per channel; L1 the --out prefix of the l1_rank run that scored
them with the three methods (its draws file picks the draw and checks the replay). The draw shown (--draw, else
chosen) is the one whose largest relative distance from a method's median T* in a channel is smallest, among those
in which c* is not CHORD's first visit in any channel; it is the same layer-1 world in every panel. Everything is recomputed with l1_rank's own
code (missions, team2) and the baselines' (fc_baseline, dn_baseline), and each T* is checked against the draws file.
Exported per channel and method (seconds from team 1's take-off, metres rounded):
  t1      team 1's flight as flown, about one [t, x, y] a second, and its end
  fill    per critical cell, how much of the clue set its CL holds over time: CHORD [enter, leave, own share,
          River share, River done (s after leave, 900 if never)], FC / DN the decode time of each file (-1 never)
  ready   per critical cell, when its CL holds its data; reports: when each of its reports reaches the BS
  team2   moves [kind, t0, t1, from, to, critical cell]; verified: when each critical cell is verified; Tstar, Tall
  groups  DN's neighbourhoods [centre x, y, orbit radius]
"""
import argparse, csv, hashlib, json, os

import numpy as np

import dn_baseline
import fc_baseline
import kin_time
import l1_model as L
import l1_rank as R
from mission_policy import GAP, tour
from mission_report import load_map

METHODS = (("CHORD", "P+prog-kin-puq-stage-zero-redir-kt"), ("FC", "FC-puq-stage-zero-redir"),
           ("DN", "DN-puq-stage-zero-redir"))
r0 = lambda v: int(round(float(v)))
r1 = lambda v: round(float(v), 1)


def pick_draw(l1, chans):
    rows = [r for r in csv.DictReader(open(f"{l1}-draws.csv")) if r["set"] in chans]
    T = {(r["set"], r["method"], int(r["draw"])): float(r["Tstar"]) for r in rows}
    rank = {(r["set"], int(r["draw"])): int(r["rank"]) for r in rows if r["method"] == METHODS[0][1]}
    draws = sorted({d for _, _, d in T})
    med = {(c, m): np.median([T[(c, m, d)] for d in draws]) for c in chans for _, m in METHODS}
    ok = [d for d in draws if all(rank[(c, d)] >= 2 for c in chans)]
    return min(ok, key=lambda d: max(abs(T[(c, m, d)] - med[(c, m)]) / med[(c, m)] for c in chans for _, m in METHODS))


def channel(w, d, l1rows):
    M = load_map(w, schemes=("rf",))
    M["name"] = R.mapname(w)
    M["windowAt"] = "crit" if any(l.startswith("NEED") for k in M["cl"] for l in open(f"{w}/plan{k}.txt")) else "ch"
    C = L.clues()
    Cq = [dict(c, w=1.0) for c in C]
    seqs = {"interleaved": L.order(C, "interleaved"), "grouped": L.order(C, "grouped")}
    tours = {k: tour(M, k) for k in ("kin", "l3first")}
    _, o = kin_time.run(w, "kin")
    assert o[45]["fix"] < 1.0, o[45]["fix"]   # the passes fly the profile (mission.py --kinPass)
    legs = tours["kin"][0]
    tours["kin/kt"] = ([(*l[:4], o[45]["leave"][l[0]]) for l in legs], o[45]["profile"] + o[45]["fix"])
    hold = R.holdings(M, C, seqs)
    crits = [(k, h) for k in sorted(M["cl"]) for h in M["cl"][k]["P"]["crit"]]
    det = {}
    for name, mod in (("fc", fc_baseline), ("dn", dn_baseline)):
        out, info, det[name] = mod.run(M, C, crits, w)
        M[name] = (out, info)
    prng = np.random.default_rng(int.from_bytes(hashlib.sha256(M["name"].encode()).digest()[:4], "little"))
    for _ in range(d + 1):   # l1_rank's phases, draw by draw
        phase = {k: float(prng.uniform(0, GAP)) for k in sorted(M["cl"])}
    traces = {}
    res, _, _ = R.missions(M, tours, hold, d, phase, C, Cq, [m for _, m in METHODS], traces)
    U, _ = R.world(M["name"], d, crits, C)
    star = max(crits, key=lambda x: U[x])
    ci = {x: i for i, x in enumerate(crits)}
    tc, pts, tag = o[45]["track"]
    keep = np.r_[0, np.where(np.diff(np.floor(tc)) > 0)[0] + 1, len(tc) - 1]
    chord_track = [[r1(tc[i]), r0(pts[i][0]), r0(pts[i][1])] for i in keep]
    enter = {k: float(tc[int(np.argmax(tag == k))]) for k in M["cl"]}
    out = {}
    for label, meth in METHODS:
        Ts, Ta, rank, dep, _ = res[meth]
        want = next(float(r["Tstar"]) for r in l1rows if r["map"] == M["name"] and r["method"] == meth
                    and int(r["draw"]) == d and r["set"] == (open(f"{w}/env.txt").read().strip()
                                                             if os.path.exists(f"{w}/env.txt") else "open"))
        assert abs(Ts - want) < 0.2, (label, Ts, want)   # the replay is the scored draw
        mv, ver = [], {}
        for e in traces[meth]:
            if e[0] in ("fly", "stage", "back"):
                mv.append([e[0], r1(e[1]), r1(e[2]), [r0(e[3][0]), r0(e[3][1])], [r0(e[4][0]), r0(e[4][1])],
                           ci[e[5]] if e[0] == "fly" else -1])
            elif e[0] == "verify":
                mv.append(["verify", r1(e[1]), r1(e[2]), None, None, ci[e[3]]])
                ver[ci[e[3]]] = r1(e[2])
        reports = [[r1(t) for t in traces["reports"][meth][x]] for x in crits]
        if label == "CHORD":
            leave = o[45]["leave"]
            fill, ready = [], []
            for x in crits:
                v = float(M["cl"][x[0]]["res"]["rf"][x[1]]["doneS"])
                stall = v < 0
                dm, rm = hold[x]["interleaved"][1], hold[x]["interleaved"][0 if not stall else 1]
                done = R.LIMIT if stall else v
                fill.append([r1(enter[x[0]]), r1(leave[x[0]]), round(dm.mean(), 3), round(rm.mean(), 3), r1(done)])
                ready.append(r1(leave[x[0]] + done))
            t1, end = chord_track, r1(tours["kin/kt"][1])
        else:
            dd = det[label.lower()]
            fill = [dd[x]["done"] for x in crits]
            ready = [r1(dd[x]["ready"]) for x in crits]
            t1, end = [[r1(a), r0(b), r0(c)] for a, b, c in dd["track"]], r1(M[label.lower()][1]["tour"])
        out[label] = dict(t1=t1, end=end, fill=fill, ready=ready, reports=reports, team2=mv,
                          verified=[ver.get(i, -1) for i in range(len(crits))], Tstar=r1(Ts), Tall=r1(Ta), rank=rank)
    out["DN"]["groups"] = [[g["c"][0], g["c"][1], g["r"]] for g in det["dn"]["groups"]]
    out["DN"]["radius"] = M["dn"][1]["radius"]
    return M, crits, star, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--works", required=True, help="channel=WORK,...")
    ap.add_argument("--l1", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--draw", type=int, default=-1)
    ap.add_argument("--html", default="")
    ap.add_argument("--title", default="Phase-1 Designs Compared")
    a = ap.parse_args()
    works = dict(x.split("=", 1) for x in a.works.split(","))
    l1rows = list(csv.DictReader(open(f"{a.l1}-draws.csv")))
    d = a.draw if a.draw >= 0 else pick_draw(a.l1, list(works))
    chans, base = {}, None
    for ch, w in works.items():
        M, crits, star, chans[ch] = channel(w, d, l1rows)
        base = base or (w, M, crits, star)
        print(f"{ch}: " + ", ".join(f"{k} T* {v['Tstar']:.0f} s (visit {v['rank']}), team 1 {v['end']:.0f} s"
                                    for k, v in chans[ch].items()), flush=True)
    w, M, crits, star = base
    idx, cells = {}, []
    for r in csv.DictReader(open(f"{w}/domain-cells.csv")):
        h = (int(r["q"]), int(r["r"]))
        idx[h] = len(cells)
        cells.append([r0(r["cx"]), r0(r["cy"]), 0 if r["type"] == "land" else 1, M["owner"].get(h, 0)])
    data = dict(map=M["name"], draw=d, bs=[r0(v) for v in M["bs"]], cells=cells,
                crit=[[idx[h], k, int(h == M["cl"][k]["P"]["ch"])] for k, h in crits], star=crits.index(star),
                paths=[[[r0(px), r0(py)] for px, py in M["cl"][k]["geo"]["path"]] for k in sorted(M["cl"])],
                chans=chans, params=dict(R=100, v2=R.V2, verify=round(R.VERIFY, 2)))
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    json.dump(data, open(a.out, "w"), separators=(",", ":"))
    print(f"{a.out}: {os.path.getsize(a.out) / 1e6:.2f} MB, draw {d}")
    if a.html:
        anim = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../docs/anim")
        head = open(f"{anim}/cmp3-head.html").read().replace("<title>Phase-1 Designs Compared</title>",
                                                            f"<title>{a.title}</title>")
        body = open(f"{anim}/cmp3-body.html").read().replace("__DATA__", json.dumps(data, separators=(",", ":")))
        open(a.html, "w").write(head + body)


if __name__ == "__main__":
    main()
