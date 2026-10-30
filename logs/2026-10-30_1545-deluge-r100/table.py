"""Table "Ground transport on fixed CHORD passes" (CLAUDE.md §8 items 227-229) from results/R<seed>/.

    python3 table.py [SEEDS...]          (default: every results/R* with all four schemes) -> table.md, table.csv

Per scheme (rf River, d direct pull, t Trickle on River's cells, tp Trickle on the direct-pull path cells), over
seeds x 8 clusters of map k8-s1, channel r100:
  ready     critical cells done, and the time the last one is done (ground side; 900 s when not done)
  frames    frames sent (PHY TX starts: data, requests, adverts, ACKs, retries) and data hops delivered
  energy    radio energy (uav-l2/tools/energy.py, uav-l2/docs/ENERGY-vi.md): CC2420 always listening as simulated,
            and scheduled sleep for rf and d (a node sleeps after its last frame; Trickle keeps listening for
            adverts), CC2420 and EFR32MG21 (+10 dBm); total and the hottest node
  T*        mission completion, mean of 100 paired layer-1 draws per seed (l1-draws.csv from score.sh)
Paired: River minus the scheme, per (seed, cluster) or per (seed, draw), with River's wins.
"""
import csv, glob, math, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, f"{HERE}/../../uav-l2/tools")
from energy import node_energy
SCH = ["rf", "d", "t", "tp"]
NAME = {"rf": "River", "d": "Direct pull", "t": "Deluge (River cells)", "tp": "Deluge (path cells)"}
L1 = {"rf": "P+prog", "d": "Pd+prog", "t": "Pt+prog", "tp": "Ptp+prog"}
LIMIT = 900.0


def rows(f):
    return list(csv.DictReader(open(f))) if os.path.exists(f) else None


def cluster(d, k, s):
    crit, runs, en = rows(f"{d}/r{k}-{s}-crit.csv"), rows(f"{d}/r{k}-{s}-runs.csv"), rows(f"{d}/r{k}-{s}-energy.csv")
    if not (crit and runs and en):
        return None
    for n in en:
        n["scheme"] = s
    e_on = [node_energy(n, "cc2420", "on") for n in en]
    e_plan = [node_energy(n, "cc2420", "sched") for n in en]
    e_efr = [node_energy(n, "efr32mg21", "sched") for n in en]
    done = [float(c["doneS"]) for c in crit]
    return dict(crit=len(done), done=sum(x >= 0 for x in done), ready=max(x if x >= 0 else LIMIT for x in done),
                frames=sum(int(n["framesTx"]) for n in en), hops=int(runs[0]["hops"]), eOn=sum(e_on),
                ePlan=sum(e_plan), hotOn=max(e_on), hotPlan=max(e_plan), eEfr=sum(e_efr), hotEfr=max(e_efr))


def tstar(d):
    out = defaultdict(dict)
    for r in rows(f"{d}/l1-draws.csv") or []:
        for s, m in L1.items():
            if r["method"].split("-")[0] == m:
                out[s][int(r["draw"])] = float(r["Tstar"])
    return out


def main():
    seeds = sys.argv[1:] or sorted(os.path.basename(p)[1:] for p in glob.glob(f"{HERE}/results/R*"))
    C, T = {}, {}
    for R in seeds:
        d = f"{HERE}/results/R{R}"
        cs = {(k, s): cluster(d, k, s) for k in range(1, 9) for s in SCH}
        if all(cs.values()):
            C[R] = cs
            T[R] = tstar(d)
        else:
            print(f"R{R}: missing", [x for x, v in cs.items() if not v][:6])
    if not C:
        return
    keys = [(R, k) for R in C for k in range(1, 9)]
    agg = lambda s, f: sum(C[R][(k, s)][f] for R, k in keys)
    lines = [f"Seeds {', '.join(C)} x 8 clusters (k8-s1, r100), fixed CHORD passes; paired River - scheme, River wins "
             f"in brackets.", "", "| | " + " | ".join(NAME[s] for s in SCH) + " |", "|---" * (len(SCH) + 1) + "|"]
    out = []

    def row(label, f, fmt, per="cluster", lower=True):
        cells = []
        for s in SCH:
            if per == "cluster":
                v = agg(s, f) / (1 if f in ("done", "crit") else len(keys))
                diffs = [C[R][(k, "rf")][f] - C[R][(k, s)][f] for R, k in keys]
            else:
                tv = [T[R][s][i] for R in T for i in T[R].get(s, {})]
                if not tv:
                    cells.append("-")
                    continue
                v = sum(tv) / len(tv)
                diffs = [T[R]["rf"][i] - T[R][s][i] for R in T for i in T[R][s] if i in T[R]["rf"]]
            txt = fmt(v)
            if s != "rf" and diffs:
                m = sum(diffs) / len(diffs)
                sd = math.sqrt(sum((x - m) ** 2 for x in diffs) / max(len(diffs) - 1, 1))
                wins = sum((x < 0) if lower else (x > 0) for x in diffs)
                txt += f" (Δ {fmt(m)} ± {fmt(1.96 * sd / math.sqrt(len(diffs)))}, {wins}/{len(diffs)})"
            cells.append(txt)
            out.append(dict(metric=label, scheme=s, value=v))
        lines.append(f"| {label} | " + " | ".join(cells) + " |")

    row("critical cells done", "done", lambda v: f"{v:.0f}", lower=False)
    row("ground ready, s (last critical cell)", "ready", lambda v: f"{v:.0f}")
    row("frames sent, k", "frames", lambda v: f"{v / 1e3:.0f}")
    row("data hops, k", "hops", lambda v: f"{v / 1e3:.0f}")
    row("radio energy CC2420, always on, J", "eOn", lambda v: f"{v:.0f}")
    row("radio energy CC2420, scheduled sleep, J", "ePlan", lambda v: f"{v:.0f}")
    row("radio energy EFR32MG21, scheduled sleep, J", "eEfr", lambda v: f"{v:.0f}")
    row("hottest node CC2420, always on, J", "hotOn", lambda v: f"{v:.2f}")
    row("hottest node CC2420, scheduled sleep, J", "hotPlan", lambda v: f"{v:.2f}")
    row("hottest node EFR32MG21, scheduled sleep, J", "hotEfr", lambda v: f"{v:.2f}")
    row("mission T*, s", None, lambda v: f"{v:.0f}", per="draw")
    lines.append("")
    lines.append("Per-cluster rows are means over (seed, cluster); Δ = River minus the scheme, mean ± 95 % CI; "
                 "(n/N) = pairs where River is better. T*: 100 paired draws per seed.")
    open(f"{HERE}/table.md", "w").write("\n".join(lines) + "\n")
    with open(f"{HERE}/table.csv", "w", newline="") as f:
        w = csv.DictWriter(f, ["metric", "scheme", "value"])
        w.writeheader()
        w.writerows(out)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
