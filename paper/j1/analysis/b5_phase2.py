"""K9 step B5: both phases on the critical-cell sets that B4 ran in ns-3, option D3 (paper/j1/PLAN-K9-DATA-vi.md).

    python3 b5_phase2.py OUT_PREFIX WORK [WORK ...] [--draws 300] [--rho 20,100,200] [--fa cell:0.1 | sys:E]

WORK: a b4_run.sh folder (OUT/<channel>/<tag>/: River run with scheme rf on the chosen set, tour.json of team 1).
Phase 1 is measured: an AI cell c holds its window at leave_k + doneS_c (ns-3); a cell not complete by River's limit
counts as 900 s. Phase 2 is the V1 model of uav-l2/tools/mission_policy.py (team 2 at 15 m/s, leaves at the first
report, visits in score order; result to the CH then LoRa slots), with the V1 verification time of CONTEXT section 17
(5 s to settle + 73 s to send R, 1 MB, to the CL) in place of the 30 s hover. Phase 2 ends when V1 confirms the true AI
cell (item 349): the column T is that time, from take-off.

Layer 1, option D3 (item 341: every camera node sends a vector per person to its AI node):
  assignment  every node to the nearest AI cell of its cluster in cell hops (paper/j1/analysis/bg_load.py)
  index       M_c = rho * W * fcam * n_c vectors at AI cell c (n_c nodes assigned; W 2 h, fcam 0.3; item 345)
  threshold   per AI cell, so that a cell holding strangers only answers YES with probability alpha:
              t_c = Phi^-1((1 - alpha)^(1 / M_c)); the larger the index, the higher the threshold. --fa sets alpha:
              cell:A  alpha = A for every AI cell (B5: 0.1, CONTEXT section 16), so the false YES grow with the set
              sys:E   alpha = E / (AI cells), so every set expects E false YES (K9 step B6, item 360)
  scores      the binormal fit of uav-l2/tools/l1_mission.py (stranger N(0, 1), target N(MU, SIGMA), MU_X when the
              view is not among the L = 3 signature images), k target vectors at the true AI cell
  true node   uniform over the nodes (each a camera with the same rho); its AI cell is the true cell
  BS          posterior with prior n_c / n (it knows the assignment), team 2 ranks by it
A mission fails when the true AI cell answers NO. Draws are paired across sets and rho of the same channel: the true
node, the LoRa phases, a stranger quantile per cell index, the target scores and views.
Also per set: rho_max at which the busiest medium stays under the 10 % budget (bg_load model), whether rho is feasible,
and the hops from the true node to its AI cell (item 348: the suspect is seen at an ordinary node).
Writes OUT_PREFIX.csv (one row per set, rho, k) and OUT_PREFIX.md.
"""
import argparse, csv, json, math, os, random, sys
from statistics import NormalDist

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, f"{HERE}/../../../uav-l2/tools", f"{HERE}/../../../uav-coop2/tools"]
import mission_policy as MP  # noqa: E402
from bg_load import TAU, Cluster  # noqa: E402
from l1_mission import MU, MU_X, SIGMA, match_time, posterior  # noqa: E402
from mission_report import load_map  # noqa: E402

ND = NormalDist()
W_H, FCAM, UMAX, D3 = 2.0, 0.3, 0.1, 528
L, LIMIT = 3, 900.0
MP.HOVER = 5.0 + 73.0   # V1: settle, then R (1 MB) to the CL (CONTEXT section 17)
POLICY = ("l3first", "early", "score")


def setup(W):
    M = load_map(W, schemes=("rf",), with_bits=False)
    for C in M["cl"].values():
        for r in C["res"]["rf"].values():
            if int(r["missing"]):
                r["doneS"] = str(LIMIT)
    legs = [(l["cluster"], tuple(l["start"]), tuple(l["end"]), l["enter"], l["leave"])
            for l in json.load(open(f"{W}/tour.json"))["legs"]]
    nodes, u_unit = [], 0.0   # nodes: (cluster, ai cell, hops)
    for k, C in M["cl"].items():
        cl = Cluster(W, k)
        S = list(C["P"]["crit"])
        fr, _, _ = cl.load(S)
        u_unit = max(u_unit, max(fr.values()) * TAU)
        for h in cl.cells:
            a = min(S, key=lambda c: (cl.d[c].get(h, 99), math.dist(cl.xy.get(h, (0, 0)), cl.xy.get(c, (0, 0)))))
            nodes += [(k, a, cl.d[a][h])] * cl.n[h]
    T1 = max(lv + float(M["cl"][k]["res"]["rf"][h]["doneS"]) for k, _, _, _, lv in legs for h in M["cl"][k]["P"]["crit"])
    return M, legs, nodes, UMAX / (u_unit * FCAM * D3) * 3600, T1


def one(M, legs, crits, n_c, d, rho, k, alpha):
    Mc = {x: max(1, round(rho * W_H * FCAM * n_c[x])) for x in crits}
    t = {x: ND.inv_cdf((1 - alpha) ** (1 / Mc[x])) for x in crits}
    best = {x: ND.inv_cdf(min(d["u"][x], 1 - 1e-16) ** (1 / Mc[x])) for x in crits}
    tru = d["true"]
    tops = [(MU if d["tv"][i] < L else MU_X) + SIGMA * d["tz"][i] for i in range(k)]
    best[tru] = max([best[tru]] + tops)
    yes = [x for x in crits if best[x] >= t[x]]
    if tru not in yes:
        return dict(ok=0, yes=len(yes), T="", visits="")
    n = sum(n_c.values())
    score = {x: posterior(best[x], Mc[x], 1.0, n_c[x] / n) for x in yes}
    r, _ = MP.run(M, legs, dict(true=tru, false=[x for x in yes if x != tru], score=score, phase=d["phase"]), POLICY,
                  match_time("pi5-hailo8l", L, max(Mc.values())))
    return dict(ok=1, yes=len(yes), T=r["found"], visits=r["visits"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out"); ap.add_argument("works", nargs="+")
    ap.add_argument("--draws", type=int, default=300)
    ap.add_argument("--rho", default="20,100,200")
    ap.add_argument("--fa", default="cell:0.1")
    A = ap.parse_args()
    rhos = [float(x) for x in A.rho.split(",")]
    fa_kind, fa_val = A.fa.split(":")
    fa_val = float(fa_val)
    rows = []
    base = {}   # per channel: the paired draws (true node index, phases, per-draw rng seeds)
    for W in A.works:
        W = W.rstrip("/")
        ch, tag = W.split("/")[-2:]
        M, legs, nodes, rho_max, T1 = setup(W)
        crits = sorted({(k, a) for k, a, _ in nodes})
        n_c = {x: sum(1 for k, a, _ in nodes if (k, a) == x) for x in crits}
        if ch not in base:
            rng = random.Random(4049)
            base[ch] = [dict(node=rng.random(), phase={kk: rng.uniform(0, MP.GAP) for kk in M["cl"]},
                             seed=rng.randrange(1 << 30), tz=[rng.gauss(0, 1) for _ in range(3)],
                             tv=[rng.randrange(3) for _ in range(3)]) for _ in range(A.draws)]
        Ds, hops = [], []
        for b in base[ch]:
            k, a, hp = nodes[int(b["node"] * len(nodes))]
            r = random.Random(b["seed"])
            Ds.append(dict(true=(k, a), phase=b["phase"], tz=b["tz"], tv=b["tv"], u={x: r.random() for x in crits}))
            hops.append(hp)
        hops = np.array(hops)
        alpha = fa_val if fa_kind == "cell" else fa_val / len(crits)
        for rho in rhos:
            for kk in (1, 3):
                res = [one(M, legs, crits, n_c, d, rho, kk, alpha) for d in Ds]
                ok = [x for x in res if x["ok"]]
                T = np.array([x["T"] for x in ok])
                rows.append(dict(channel=ch, set=tag, ai_cells=len(crits), fa=A.fa, alpha=f"{alpha:.4g}", rho=f"{rho:g}", k=kk,
                                 rho_max=f"{rho_max:.0f}", feasible=int(rho <= rho_max), T1=f"{T1:.0f}",
                                 index_max=max(1, round(rho * W_H * FCAM * max(n_c.values()))),
                                 success=f"{len(ok) / len(res):.3f}", yes=f"{np.mean([x['yes'] for x in res]):.1f}",
                                 visits=f"{np.mean([x['visits'] for x in ok]):.2f}",
                                 T_mean=f"{T.mean():.0f}", T_p90=f"{np.percentile(T, 90):.0f}",
                                 hops_mean=f"{hops.mean():.1f}", hops_max=int(hops.max())))
        print(f"{ch} {tag}: {len(crits)} AI cells, rho_max {rho_max:.0f}, T1 {T1:.0f}", flush=True)
    with open(A.out + ".csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    with open(A.out + ".md", "w") as f:
        f.write(f"# K9 B5: both phases on the B4 sets, option D3 (k8, River seed 1), false alarms {A.fa}\n\n"
                f"{A.draws} paired draws per row. T: time from take-off to V1 confirming the true AI cell, over the "
                "missions where it answers YES (success). yes: AI cells answering YES. index: vectors at the busiest AI "
                "cell. feasible: rho <= rho_max of the set (10 % budget). hops: true node to its AI cell (cells). alpha: "
                "probability that an AI cell holding strangers only answers YES.\n\n"
                "| channel | set | AI cells | alpha | T1 | rho_max | hops mean / max | rho | feasible | index | k | success "
                "| yes | visits | T mean | T p90 |\n|" + "---|" * 16 + "\n")
        for r in rows:
            f.write(f"| {r['channel']} | {r['set']} | {r['ai_cells']} | {r['alpha']} | {r['T1']} | {r['rho_max']} | "
                    f"{r['hops_mean']} / {r['hops_max']} | {r['rho']} | {'yes' if r['feasible'] else 'no'} | "
                    f"{r['index_max']} | {r['k']} | {r['success']} | {r['yes']} | {r['visits']} | {r['T_mean']} | "
                    f"{r['T_p90']} |\n")
    print(open(A.out + ".md").read())


if __name__ == "__main__":
    main()
