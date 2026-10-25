"""Draft Table I (CLAUDE.md §8 item 170): critical cells holding the whole query after the pass, on CHORD's own
flight, with the fountain-coded broadcast and in-cell gathering only (chordfc-cells.csv of l1_rank -fcd) against
River (r*-rf-crit.csv), for the twelve FIX/ missions.
    python3 table1_samepath.py FIXDIR
"""
import csv, glob, sys

import numpy as np

for e in ("open", "r500", "r200", "r100"):
    for m in ("k8", "k12", "k16"):
        w = f"{sys.argv[1]}/{e}/{m}-s1"
        own = [r["complete"] == "1" for r in csv.DictReader(open(f"{w}/chordfc-cells.csv"))]
        riv = [float(r["doneS"]) for f in glob.glob(f"{w}/r*-rf-crit.csv") for r in csv.DictReader(open(f))]
        print(f"{e:5} {m:4}: fountain + gather only {np.mean(own) * 100:5.1f} % | River "
              f"{np.mean([v >= 0 for v in riv]) * 100:.0f} %, done {np.mean(riv):.0f} s after team 1 leaves (mean)")
