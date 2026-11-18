"""K9 step B3: choose the critical cells (cells with an AI node) of each cluster, for option D3 (ordinary camera nodes
send 512-d INT8 vectors to their AI node; paper/j1/PLAN-K9-DATA-vi.md, chatlog items 341-342).

    python3 cc_select.py WORK OUT_DIR [--rho 20,50,100,200] [--fcam 0.3] [--umax 0.1,0.2] [--hmax 5]

Two forces, both at model level (B4 checks them in ns-3):
  River     the River surrogate (uav-l2/tools/river_surrogate.py, formula fitted on C4):
            doneS(h) = a + b hops_h + c lackCell_h / 1000 + d cluLack / 1000, cluLack the lackCell summed over the
            cluster's critical cells. Every feature but cluLack depends on the cell alone (its window is the clue-set
            copy nearest to it), so they are computed once per cluster from a plan in which every cell is critical,
            and T_k(S) = max_{h in S} (a + b hops_h + c lack_h / 1000) + d sum_{h in S} lack_h / 1000. More critical cells
            make every one of them slower.
  background each cell's nodes send to the nearest AI cell of the cluster (bg_load.py: load model of river_lb.py); the
            busiest medium must stay under the duty budget umax at rho people/h per camera, a share fcam of the nodes
            being cameras, 528 B per person; and no node farther than hmax cells from its AI cell (H limit, item 338).
            Fewer critical cells make the AI cells' own cells busier.
For each (umax, rho) and cluster: the fewest critical cells m for which a placement is feasible, the placement found by
local search (start: k-medoids; moves: swap one critical cell for another cell; while infeasible, lower the busiest
medium; once feasible, lower T_k), then m + 1 and m + 2 as well, keeping the best T_k. If even every cell being critical
is not feasible, the cameras send only a share (option a, item 342): coverage = budget / load at the best placement.
T1 = max_k (leave_k + T_k), leave_k from WORK/tour.json (team 1 leaves cluster k). Algorithm 3's set is scored the same
way for comparison. Writes OUT_DIR/cc-<map>.md and .csv, and the chosen sets as crit-<map>-u<umax>-rho<rho>.csv
(mission.py --crit). A check recomputes T_k of each chosen set from the real plan (river_plan with crit.csv).
"""
import argparse, csv, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, f"{HERE}/../../../uav-l2/tools", f"{HERE}/../../../uav-coop2/tools"]
import river_surrogate as RS  # noqa: E402
from bg_load import TAU, Cluster  # noqa: E402
from mission_report import load_map  # noqa: E402
from river_plan import hear_model, load_around  # noqa: E402

SURR = f"{HERE}/../../../uav-l2/docs/data/results/river-surrogate.csv"
SIZE = 528   # D3: 512-d INT8 vector + 16 B time and place


def cell_terms(geo, around, loss, hear, coef):
    """{cell: (own term a + b hops + c lack/1000, lack/1000)} from a plan in which every cell is critical."""
    g = dict(geo, crit_cells=set(geo["S"]))
    P = RS.mission_plan(g, around, loss)
    F = RS.features(g, P, loss, hear)
    a, b, c, _ = coef
    return {h: (a + b * F[h]["hops"] + c * F[h]["lackCell"] / 1000, F[h]["lackCell"] / 1000) for h in P["crit"]}


def t_cluster(S, terms, d):
    return max(terms[h][0] for h in S) + d * sum(terms[h][1] for h in S)


def busy(cl, S):
    fr, far, _ = cl.load(S)
    return max(fr.values()) * TAU, far


def search(cl, terms, d, m, cap, hmax):
    """Local search from the k-medoids placement of m cells: (feasible, T, busy per unit rate, far, S)."""
    S = cl.medoids(m)

    def score(S):
        u, far = busy(cl, S)
        ok = u <= cap and far <= hmax
        return (0 if ok else 1, t_cluster(S, terms, d) if ok else u + far * 1e-3, u, far)
    best = score(S)
    better = True
    while better:
        better = False
        for i in range(len(S)):
            for c in cl.cells:
                if c in S:
                    continue
                T = sorted(S[:i] + [c] + S[i + 1:])
                v = score(T)
                if v[:2] < best[:2]:
                    S, best, better = T, v, True
                    break
            if better:
                break
    return best[0] == 0, t_cluster(S, terms, d), best[2], best[3], S


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("work"); ap.add_argument("out")
    ap.add_argument("--rho", default="20,50,100,200")
    ap.add_argument("--fcam", type=float, default=0.3)
    ap.add_argument("--umax", default="0.1,0.2")
    ap.add_argument("--hmax", type=int, default=5)
    A = ap.parse_args()
    W = A.work.rstrip("/")
    name = "-".join(W.split("/")[-3:])
    os.makedirs(A.out, exist_ok=True)
    M = load_map(W, schemes=())
    loss = json.load(open(f"{W}/plan-opts.json"))["lossDb"]
    around, hear = load_around(f"{W}/domain-cl.csv"), hear_model(loss)
    model = RS.Model.load(SURR, "formula")
    coef = model.c
    d = coef[3]
    leave = {l["cluster"]: l["leave"] for l in json.load(open(f"{W}/tour.json"))["legs"]}
    K = len(M["cl"])
    cls = {k: Cluster(W, k) for k in M["cl"]}
    terms = {k: cell_terms(M["cl"][k]["geo"], around, loss, hear, coef) for k in M["cl"]}
    alg3 = {k: list(M["cl"][k]["P"]["crit"]) for k in M["cl"]}
    rows = []
    a3 = {k: (t_cluster(alg3[k], terms[k], d), *busy(cls[k], alg3[k])) for k in cls}
    for u in map(float, A.umax.split(",")):
        for rho in map(float, A.rho.split(",")):
            cap = u / (A.fcam * rho / 3600 * SIZE)   # largest busy fraction per unit rate (1 B/s per node)
            res = {}
            for k, cl in cls.items():
                n = len(cl.cells)
                memo = {}
                run = lambda m: memo.setdefault(m, search(cl, terms[k], d, m, cap, A.hmax))
                hi = 1
                while hi < n and not run(hi)[0]:   # doubling, then bisection: feasibility grows with m
                    hi = min(n, 2 * hi)
                found = None
                if run(hi)[0]:
                    lo = hi // 2 if hi > 1 else 0
                    while hi - lo > 1:
                        mid = (lo + hi) // 2
                        if run(mid)[0]:
                            hi = mid
                        else:
                            lo = mid
                    for m in (hi, hi + 1, hi + 2):   # a little more room may place them better
                        if m <= n and run(m)[0] and (found is None or run(m)[1] < found[0]):
                            found = (run(m)[1], run(m)[2], run(m)[3], run(m)[4], 1.0)
                if found is None:   # option a: cameras send only a share; the least loaded placement tried
                    ok, T, ub, far, S = min((memo[m] for m in memo), key=lambda r: r[2])
                    found = (T, ub, far, S, min(1.0, cap / ub))
                res[k] = found
            T1 = max(leave[k] + res[k][0] for k in cls)
            T1a = max(leave[k] + a3[k][0] for k in cls)
            cov_a3 = min(min(1.0, cap / a3[k][1]) if a3[k][2] <= A.hmax else 0.0 for k in cls)
            rows.append(dict(umax=u, rho=rho, cc=sum(len(r[3]) for r in res.values()), T1=T1,
                             cov=min(r[4] for r in res.values()), far=max(r[2] for r in res.values()),
                             cc_a3=sum(map(len, alg3.values())), T1_a3=T1a, cov_a3=cov_a3, per=res))
            with open(f"{A.out}/crit-{name}-u{u:g}-rho{rho:g}.csv", "w") as f:
                f.write("q,r\n" + "".join(f"{q},{r}\n" for k in res for q, r in sorted(res[k][3])))
    # check: T_k of the chosen sets from the real plan (river_plan with these cells as crit.csv)
    worst = 0.0
    r0 = rows[0]
    for k in cls:
        S = set(r0["per"][k][3])
        g = dict(M["cl"][k]["geo"], crit_cells=S)
        P = RS.mission_plan(g, around, loss)
        F = RS.features(g, P, loss, hear)
        real = max(model.predict([F[h] for h in P["crit"]]))
        worst = max(worst, abs(real - r0["per"][k][0]))
    with open(f"{A.out}/cc-{name}.csv", "w") as f:
        w = csv.writer(f)
        w.writerow(["umax", "rho", "cluster", "m", "T_k", "busy_per_unit", "far", "coverage", "leave"])
        for r in rows:
            for k, v in r["per"].items():
                w.writerow([r["umax"], r["rho"], k, len(v[3]), f"{v[0]:.1f}", f"{v[1]:.6g}", v[2], f"{v[4]:.3f}",
                            f"{leave[k]:.0f}"])
    with open(f"{A.out}/cc-{name}.md", "w") as f:
        f.write(f"# Critical cells chosen for D3 on {name}\n\nfcam {A.fcam:g}, hmax {A.hmax} cells, River surrogate "
                f"(formula). T1: last critical cell done, seconds from take-off (model). Algorithm 3: "
                f"{r0['cc_a3']} critical cells. Check against the real plan: largest |T_k| difference "
                f"{worst:.2f} s.\n\n| umax | rho (people/h) | critical cells | T1 (s) | coverage | farthest (cells) | "
                f"Alg. 3 T1 (s) | Alg. 3 coverage |\n|---|---|---|---|---|---|---|---|\n")
        for r in rows:
            f.write(f"| {r['umax']:g} | {r['rho']:g} | {r['cc']} | {r['T1']:.0f} | {r['cov']:.2f} | {r['far']} | "
                    f"{r['T1_a3']:.0f} | {r['cov_a3']:.2f} |\n")
    print(open(f"{A.out}/cc-{name}.md").read())


if __name__ == "__main__":
    main()
