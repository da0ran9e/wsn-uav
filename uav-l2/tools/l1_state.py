"""What team 2 is doing when c*'s first report reaches the BS (CLAUDE.md §8 item 114, round 2): waiting (at the
BS or staging), flying to another cell, or verifying another cell; then how long until it starts towards c*, and
how many other cells it verifies after c*'s report is in. Shows what a policy that redirects team 2 could gain.

    python3 tools/l1_state.py --work "KW/k*" --method P+prog-latency-puq-stage-zero --draws 100 --out docs/data/l1rank/state

Same maps, draws and seeds as l1_rank.py. Writes OUT.csv (one row per map and draw) and prints a summary per size.
"""
import argparse, csv, glob, hashlib
from collections import defaultdict

import numpy as np

import l1_model as L
import l1_rank as R
from mission_policy import GAP, tour
from mission_report import load_map


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--method", default="P+prog-latency-puq-stage-zero")
    ap.add_argument("--draws", type=int, default=100)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    C = L.clues()
    Cq = [dict(c, w=1.0) for c in C]
    seqs = {"interleaved": L.order(C, "interleaved"), "grouped": L.order(C, "grouped")}
    rows = []
    for w in sorted(w for w in glob.glob(a.work) if R.complete(w)):
        M = load_map(w, schemes=("rf",))
        M["name"] = R.mapname(w)
        tk = next((o for o in a.method.split("-") if o in ("short", "latency", "seam")), "l3first")
        tours = {tk: tour(M, tk), "l3first": tour(M, "l3first")}
        hold = R.holdings(M, C, seqs)
        prng = np.random.default_rng(int.from_bytes(hashlib.sha256(M["name"].encode()).digest()[:4], "little"))
        for d in range(a.draws):
            phase = {k: float(prng.uniform(0, GAP)) for k in sorted(M["cl"])}
            tr = {}
            out, _, _ = R.missions(M, tours, hold, d, phase, C, Cq, [a.method], tr)
            Ts, _, rank, _, sin = out[a.method]
            moves = [e for e in tr[a.method] if e[0] in ("fly", "verify", "stage")]
            star = next(e[5] for e in moves if e[0] == "fly" and e[1] < Ts and e[2] + R.VERIFY >= Ts - 1e-6)
            now = next((e for e in moves if e[1] < sin < e[2]), None)   # what it was doing just before
            state = "wait" if now is None or now[0] == "stage" else ("fly" if now[0] == "fly" else "verify")
            if now is not None and now[0] != "stage" and (now[5] if now[0] == "fly" else now[3]) == star:
                state = "toStar"
            go = next(e[1] for e in moves if e[0] == "fly" and e[5] == star)
            wrong_after = sum(1 for e in moves if e[0] == "verify" and e[3] != star and e[1] >= sin and e[1] < Ts)
            rows.append(dict(map=M["name"], size=len(M["cl"]), draw=d, Tstar=round(Ts, 1), starIn=round(sin, 1),
                             rank=rank, state=state, toStar=round(go, 1), busy=round(max(0.0, go - sin), 1),
                             wrongAfter=wrong_after))
        print(M["name"], "done", flush=True)
    with open(a.out + ".csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)
    by = defaultdict(list)
    for r in rows:
        by[r["size"]].append(r)
    for k in sorted(by):
        rs = by[k]
        share = {s: np.mean([r["state"] == s for r in rs]) for s in ("wait", "fly", "verify", "toStar")}
        print(f"k{k}: {len(rs)} draws; at c*'s report team 2 is waiting {share['wait']:.2f}, flying elsewhere "
              f"{share['fly']:.2f}, verifying elsewhere {share['verify']:.2f}, already heading to c* {share['toStar']:.2f}; "
              f"until it heads to c*: mean {np.mean([r['busy'] for r in rs]):.0f} s; other cells verified after "
              f"c*'s report: mean {np.mean([r['wrongAfter'] for r in rs]):.2f}; Tstar {np.mean([r['Tstar'] for r in rs]):.0f} s")


if __name__ == "__main__":
    main()
