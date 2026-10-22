"""Layer-2 delivery metrics per map (CLAUDE.md §8 item 136): when the critical cells hold the clue set.

    python3 tools/l2_metrics.py --set kmedoids "KD/*" kin --set swath "SW/*" skin --out OUT.csv

Per work folder (mission.py, swath_mission.py) and team 1's tour of the given kind (mission_policy.tour):
  team1      team 1 back at the BS (s)
  readyMean  mean over the critical cells of leave + River doneS: the cell holds its window of the clue set (s)
  readyLast  the last critical cell to hold it: phase 1 delivered (s)
  frames     River MAC frames of the whole map (hops of every cluster's run)
"""
import argparse, csv, glob, os

import numpy as np

from mission_policy import tour
from mission_report import load_map


def metrics(w, kind):
    M = load_map(w, schemes=("rf",), with_bits=False)
    legs, back = tour(M, kind)
    leave = {l[0]: l[4] for l in legs}
    ready = [leave[k] + float(r["doneS"]) for k, C in M["cl"].items() for r in C["res"]["rf"].values()]
    frames = sum(int(C["runs"]["rf"]["hops"]) for C in M["cl"].values())
    return dict(map=os.path.basename(os.path.normpath(w)), team1=round(back, 1), readyMean=round(float(np.mean(ready)), 1),
                readyLast=round(max(ready), 1), crits=len(ready), frames=frames)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", nargs=3, action="append", metavar=("NAME", "GLOB", "KIND"), required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rows = [dict(set=n, kind=k, **metrics(w, k)) for n, g, k in a.set for w in sorted(glob.glob(g))
            if os.path.exists(f"{w}/r1-rf-crit.csv")]
    with open(a.out, "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)


if __name__ == "__main__":
    main()
