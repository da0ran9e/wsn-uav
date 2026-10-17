"""One mission draw replayed by every method side by side: proposed P, its policy and layer-3 ablations, and the
baselines (CLAUDE.md §8 item 87); text-free map (item 63).

    python3 tools/compare_anim.py --work W/k4 --out docs/anim/compare-replay.html

WORK is a mission.py folder with River runs rf, ad12 and d. The draw is the one mission_anim.py shows (the first
needing two team-2 visits under l3first / early / score). Every method uses mission_baselines.py's verification
(VERIFY s per visit) and its models; times are mission seconds. Per method the page gets the UAV moves
(fixed wing team 1, rotary UAVs), when each critical cell is ready (data complete + matched) and when its result
reaches the BS, and the end. Fills docs/anim/compare-head.html + compare-body.html.
"""
import argparse, copy, csv, json, math, os

import numpy as np

from mission_report import load_map
import mission_policy as MP
import mission_baselines as MB

HERE = os.path.dirname(os.path.abspath(__file__))
ANIM = os.path.join(HERE, "../docs/anim")
V2 = MB.V2
R2 = lambda p: [round(p[0]), round(p[1])]


def legs_of(legs, back, bs):
    """Team 1 (fixed wing): moves from the legs of MP.tour."""
    out, pos, t = [], bs, 0.0
    for k, s, e, t0, t1 in legs:
        out += [dict(u=0, t0=t, t1=t0, a=R2(pos), b=R2(s)), dict(u=0, t0=t0, t1=t1, a=R2(s), b=R2(e), tx=1)]
        pos, t = e, t1
    out.append(dict(u=0, t0=t, t1=back, a=R2(pos), b=R2(bs)))
    return out


def team2_moves(M, D, known_at, verify, u=1):
    """mission_baselines.team2 (early, score), with its moves."""
    bs, sus = M["bs"], [D["true"]] + D["false"]
    pts = {x: M["cl"][x[0]]["geo"]["c"][x[1]] for x in sus}
    t = min(known_at[x] for x in sus)
    pos, done, mv = bs, set(), []
    while True:
        known = [x for x in sus if known_at[x] <= t and x not in done]
        if not known:
            t1 = min(known_at[x] for x in sus if x not in done)
            mv.append(dict(u=u, t0=t, t1=t1, a=R2(pos), b=R2(pos)))
            t = t1
            continue
        nxt = max(known, key=lambda x: (D["score"][x] / (math.dist(pos, pts[x]) / V2 + verify), -math.dist(pos, pts[x])))
        ta = t + math.dist(pos, pts[nxt]) / V2
        mv += [dict(u=u, t0=t, t1=ta, a=R2(pos), b=R2(pts[nxt])), dict(u=u, t0=ta, t1=ta + verify, a=R2(pts[nxt]),
                                                                        b=R2(pts[nxt]), hover=1)]
        t, pos = ta + verify, pts[nxt]
        done.add(nxt)
        if nxt == D["true"]:
            end = t + math.dist(pos, bs) / V2
            mv.append(dict(u=u, t0=t, t1=end, a=R2(pos), b=R2(bs)))
            return t, end, mv


def visits(bs, stops, cost, stop_when, u=1, disk=0):
    """mission_baselines.tour_visits with its moves; stops: (point, payload)."""
    t, pos, mv = 0.0, bs, []
    for i in MB.tsp_order(bs, [s[0] for s in stops]):
        p, c = stops[i][0], cost(stops[i])
        ta = t + math.dist(pos, p) / V2
        mv += [dict(u=u, t0=t, t1=ta, a=R2(pos), b=R2(p)), dict(u=u, t0=ta, t1=ta + c, a=R2(p), b=R2(p), hover=1, disk=disk)]
        t, pos = ta + c, p
        yield stops[i], t, mv
        if stop_when(stops[i]):
            end = t + math.dist(pos, bs) / V2
            mv.append(dict(u=u, t0=t, t1=end, a=R2(pos), b=R2(bs)))
            return


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    M = load_map(a.work, schemes=("rf", "ad12", "d"))
    bs = M["bs"]
    MP.HOVER = MB.VERIFY
    legsL, backL = MP.tour(M, "l3first")
    legsS, backS = MP.tour(M, "short")
    D = None
    for sd in range(1, 400):   # the draw mission_anim.py shows
        D = MP.draws(M, 1, sd)[0]
        if MP.run(M, legsL, D, ("l3first", "early", "score"))[0]["visits"] >= 2:
            break
    light = round(np.mean([C["D"] for C in M["cl"].values()])) * MB.PAYLOAD
    crits = [(k, h) for k in sorted(M["cl"]) for h in M["cl"][k]["P"]["crit"]]
    cl = {}
    for k, C in M["cl"].items():
        for n in C["geo"]["nodes"]:
            x = (k, (int(n["q"]), int(n["r"])))
            if n["isCL"] == "1" and x in crits:
                cl[x] = (float(n["x"]), float(n["y"]))
    ci = {x: i for i, x in enumerate(crits)}
    sus = [D["true"]] + D["false"]
    meth = {}

    def proposed(name, legs, back, policy, scheme="rf", grp=0):
        MM = M
        if scheme != "rf":
            MM = copy.copy(M)
            MM["cl"] = {k: dict(C, res=dict(C["res"], rf=C["res"][scheme])) for k, C in M["cl"].items()}
        r, tr = MP.run(MM, legs, D, policy)
        leave = {l[0]: l[4] for l in legs}
        ready = {x: leave[x[0]] + float(MM["cl"][x[0]]["res"]["rf"][x[1]]["doneS"]) + MP.MATCH for x in crits}
        rep = MB.lora_arrival(MM, D, ready)
        mv, pos, t = legs_of(legs, back, bs), bs, None
        for e in tr:   # team 2 from the trace of MP.run
            if e[0] == "dep":
                t = e[1]
            elif e[0] == "wait":
                mv.append(dict(u=1, t0=t, t1=e[1], a=R2(pos), b=R2(pos)))
                t = e[1]
            else:
                mv.append(dict(u=1, t0=t, t1=e[1], a=R2(pos), b=R2(e[2])))
                pos, t = e[2], e[1]
                if e[0] == "visit":
                    mv.append(dict(u=1, t0=t, t1=t + MP.HOVER, a=R2(pos), b=R2(pos), hover=1))
                    t += MP.HOVER
        meth[name] = dict(grp=grp, mv=mv, ready={ci[x]: round(v, 1) for x, v in ready.items()},
                          rep={ci[x]: round(v, 1) for x, v in rep.items()}, found=round(r["found"], 1),
                          end=round(r["end"], 1), ok=1, fw=1)

    proposed("P", legsL, backL, ("l3first", "early", "score"))
    proposed("P·short", legsS, backS, ("short", "early", "score"), grp=1)
    proposed("P·wait", legsL, backL, ("l3first", "wait", "score"), grp=1)
    proposed("P·tsp", legsL, backL, ("l3first", "early", "tsp"), grp=1)
    proposed("L3·direct", legsL, backL, ("l3first", "early", "score"), "d", grp=2)
    proposed("L3·circle12", legsL, backL, ("l3first", "early", "score"), "ad12", grp=2)
    # B4-0.9: no River; the cell matches what it gathered
    th = 0.9
    leave = {l[0]: l[4] for l in legsL}
    ready = {x: leave[x[0]] + float(M["cl"][x[0]]["res"]["rf"][x[1]]["gatherDoneS"]) + MP.MATCH for x in crits}
    rep = MB.lora_arrival(M, D, ready)
    ok = M["cl"][D["true"][0]]["held"][D["true"][1]] >= th
    mv = legs_of(legsL, backL, bs)
    if ok:
        found, end, m2 = team2_moves(M, D, rep, MB.VERIFY)
    else:   # the true cell reports nothing: team 2 checks the false suspects and gives up
        fs = D["false"]
        pts = [M["cl"][x[0]]["geo"]["c"][x[1]] for x in fs]
        t, pos, m2 = max(rep[x] for x in fs), bs, []
        for i in MB.tsp_order(bs, pts):
            ta = t + math.dist(pos, pts[i]) / V2
            m2 += [dict(u=1, t0=t, t1=ta, a=R2(pos), b=R2(pts[i])), dict(u=1, t0=ta, t1=ta + MB.VERIFY, a=R2(pts[i]), b=R2(pts[i]), hover=1)]
            t, pos = ta + MB.VERIFY, pts[i]
        end, found = t + math.dist(pos, bs) / V2, float("nan")
        m2.append(dict(u=1, t0=t, t1=end, a=R2(pos), b=R2(bs)))
    meth["B4·0.9"] = dict(grp=3, mv=mv + m2, ready={ci[x]: round(v, 1) for x, v in ready.items()},
                          rep={ci[x]: round(v, 1) for x, v in rep.items()}, found=round(found, 1) if ok else -1,
                          end=round(end, 1), ok=int(ok), fw=1, miss=ci[D["true"]] if not ok else -1)
    # B1: one rotary UAV, every critical cell, the large file by unicast, waits for the match
    rd, mv = {}, None
    for (p, x), t, mv in visits(bs, [(cl[x], x) for x in crits], lambda s: MB.VERIFY, lambda s: s[1] == D["true"]):
        rd[ci[x]] = round(t, 1)
    meth["B1"] = dict(grp=3, mv=mv, ready=rd, rep=dict(rd), found=rd[ci[D["true"]]], end=mv[-1]["t1"], ok=1, fw=0)
    for rr in MB.RADII:
        G = MB.groups(cl, rr)
        cost_big = lambda g: MB.SETTLE + MB.frames(MB.BIG) * MB.BC_FRAME / (1 - max(MB.per(math.dist(g[0], cl[b])) for b in g[1])) + MB.MATCH
        rd = {}
        for (hp, mem), t, mv in visits(bs, G, cost_big, lambda g: D["true"] in g[1], disk=rr):
            for b in mem:
                rd[ci[b]] = round(t, 1)
        meth[f"B2·{rr}"] = dict(grp=3, mv=mv, ready=rd, rep=dict(rd), found=rd[ci[D["true"]]], end=mv[-1]["t1"], ok=1, fw=0)
        # B3: the light file over the same groups by a rotary UAV, then LoRa and team 2
        t, pos, ready, m1 = 0.0, bs, {}, []
        for i in MB.tsp_order(bs, [g[0] for g in G]):
            hp, mem = G[i]
            ta = t + math.dist(pos, hp) / V2
            c = MB.SETTLE + MB.frames(light) * MB.BC_FRAME / (1 - max(MB.per(math.dist(hp, cl[b])) for b in mem))
            m1 += [dict(u=0, t0=t, t1=ta, a=R2(pos), b=R2(hp)), dict(u=0, t0=ta, t1=ta + c, a=R2(hp), b=R2(hp), hover=1, disk=rr)]
            t, pos = ta + c, hp
            for b in mem:
                ready[b] = t + MB.MATCH
        m1.append(dict(u=0, t0=t, t1=t + math.dist(pos, bs) / V2, a=R2(pos), b=R2(bs)))
        rep = MB.lora_arrival(M, D, ready)
        found, end, m2 = team2_moves(M, D, rep, MB.VERIFY)
        meth[f"B3·{rr}"] = dict(grp=3, mv=m1 + m2, ready={ci[x]: round(v, 1) for x, v in ready.items()},
                                rep={ci[x]: round(v, 1) for x, v in rep.items()}, found=round(found, 1), end=round(end, 1), ok=1, fw=0)
    # B6: the light file by unicast at every critical cell, then LoRa and team 2
    t, pos, ready, m1 = 0.0, bs, {}, []
    for i in MB.tsp_order(bs, [cl[x] for x in crits]):
        x = crits[i]
        ta = t + math.dist(pos, cl[x]) / V2
        c = MB.SETTLE + MB.frames(light) * MB.UC_FRAME
        m1 += [dict(u=0, t0=t, t1=ta, a=R2(pos), b=R2(cl[x])), dict(u=0, t0=ta, t1=ta + c, a=R2(cl[x]), b=R2(cl[x]), hover=1)]
        t, pos = ta + c, cl[x]
        ready[x] = t + MB.MATCH
    m1.append(dict(u=0, t0=t, t1=t + math.dist(pos, bs) / V2, a=R2(pos), b=R2(bs)))
    rep = MB.lora_arrival(M, D, ready)
    found, end, m2 = team2_moves(M, D, rep, MB.VERIFY)
    meth["B6"] = dict(grp=3, mv=m1 + m2, ready={ci[x]: round(v, 1) for x, v in ready.items()},
                      rep={ci[x]: round(v, 1) for x, v in rep.items()}, found=round(found, 1), end=round(end, 1), ok=1, fw=0)
    # B7: oracle
    p = cl[D["true"]]
    d = math.dist(bs, p) / V2
    meth["B7"] = dict(grp=3, mv=[dict(u=1, t0=0, t1=d, a=R2(bs), b=R2(p)), dict(u=1, t0=d, t1=d + MB.VERIFY, a=R2(p), b=R2(p), hover=1),
                                 dict(u=1, t0=d + MB.VERIFY, t1=2 * d + MB.VERIFY, a=R2(p), b=R2(bs))],
                      ready={ci[D["true"]]: round(d + MB.VERIFY, 1)}, rep={}, found=round(d + MB.VERIFY, 1),
                      end=round(2 * d + MB.VERIFY, 1), ok=1, fw=0)
    for m in meth.values():
        for e in m["mv"]:
            e["t0"], e["t1"] = round(e["t0"], 2), round(e["t1"], 2)
    # map
    cells = []
    for r in csv.DictReader(open(f"{a.work}/domain-cells.csv")):
        h = (int(r["q"]), int(r["r"]))
        cells.append([round(float(r["cx"])), round(float(r["cy"])), 1 if r["type"] != "land" else 0, M["owner"].get(h, 0)])
    out = dict(cells=cells, bs=R2(bs), crit=[R2(M["cl"][k]["geo"]["c"][h]) for k, h in crits],
               sus=[[ci[x], int(x == D["true"])] for x in sus], methods=meth, params=dict(R=100, verify=round(MB.VERIFY, 1)))
    head = open(os.path.join(ANIM, "compare-head.html")).read()
    body = open(os.path.join(ANIM, "compare-body.html")).read().replace("__DATA__", json.dumps(out, separators=(",", ":")))
    with open(a.out, "w") as f:
        f.write(head + body)
    print(f"{a.out}: {os.path.getsize(a.out) / 1e6:.2f} MB; {len(crits)} critical cells; light {light / 1e6:.2f} MB")
    for n, m in meth.items():
        print(f"  {n:12s} end {m['end']:7.1f} s  found {m['found']:7.1f}  ok {m['ok']}")


if __name__ == "__main__":
    main()
