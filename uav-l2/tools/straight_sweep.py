"""MEANDER lanes straightened step by step on random maps, against CHORD-T with the same cluster count, geometry only
(CLAUDE.md §8 item 151).

    python3 tools/straight_sweep.py --work DIR --bin BIN --log LOGDIR [--jobs 3]       # run (resumable)
    python3 tools/straight_sweep.py --work DIR --bin BIN --log LOGDIR --table OUT.md   # one row per pair

Maps: restructure.domain(K, seed), the compact domains of the 16-map campaign, BS south. MEANDER: lanes 8 cells,
--minAxe 2.4 (every cluster one clue-set copy over its own cells), --reach 5 (only critical cells farther than 5
cells pull the line), --straight STRAIGHT km (0: the lane centre line, inf: each lane the chord between its ends).
CHORD-T: mission.py --chordTour 0.6,0.8 with MEANDER's cluster count. Columns as l2_screen, plus the shortest Axe
(packets over a cluster's own cells, km) and the share of critical cells within 5 cells of their path.
"""
import argparse, json, os
from concurrent.futures import ThreadPoolExecutor

import numpy as np

from factor_sweep import run, seeds
from map_gen import W

K, STRAIGHT, REACH, MINAXE = 8, ("0", "0.5", "1", "2", "4", "inf"), 5, 2.4


def ml(a, s, st):
    return f"{a.work}/s{s}-st{st}/ml"


def chord(a, s, k):
    return f"{a.work}/s{s}-K{k}/chord"


def one(a, s, st):
    w = ml(a, s, st)
    if not os.path.exists(f"{w}/c1-curve.json"):
        run(["python3", "uav-l2/tools/meander_lane.py", "--clusters", str(K), "--seed", str(s), "--lane", "8",
             "--minAxe", str(MINAXE), "--reach", str(REACH), "--straight", st, "--work", w, "--bin", a.bin,
             "--geometry"], f"{a.log}/ml-s{s}-st{st}.md")
    if not os.path.exists(f"{w}/c1-curve.json"):
        return s, st, "meander failed"
    k = json.load(open(f"{w}/map.json"))["clusters"]
    c = chord(a, s, k)
    if not os.path.exists(f"{c}/tour.json"):
        run(["python3", "uav-l2/tools/mission.py", "--clusters", str(K), "--seed", str(s), "--count", str(k),
             "--work", c, "--bin", a.bin, "--windowKB", "400", "--windowAt", "crit", "--critRing", "domain",
             "--axeNear", "--chordTour", "0.6,0.8", "--geometry"], f"{a.log}/chord-s{s}-K{k}.md")
    return s, st, "ok" if os.path.exists(f"{c}/tour.json") else "chord failed"


def extra(w):
    from mission_report import load_map
    M = load_map(w, schemes=(), with_bits=False)
    axe = [sum(len(C["P"]["seg"][x]) for x in C["P"]["axe"]) * 0.5 / 1000 for C in M["cl"].values()]
    d = [np.min(np.linalg.norm(C["geo"]["path"] - np.array(C["geo"]["c"][h]), axis=1))
         for C in M["cl"].values() for h in C["P"]["crit"]]
    return min(axe), float(np.mean(np.array(d) <= REACH * W))


def table(a, S):
    from l2_screen import row
    rows = ["| seed | straight (km) | method | cụm | cell | 50 m/s | 45° | 30° | 60° | trên cụm km | dẫn km | nối km | "
            "BS km | critical | TB m | p90 m | >606 m | Axe ngắn nhất km | critical trong 5 cell |", "|---" * 19 + "|"]
    for s in S:
        for st in STRAIGHT:
            w = ml(a, s, st)
            if not os.path.exists(f"{w}/c1-curve.json"):
                continue
            c = chord(a, s, json.load(open(f"{w}/map.json"))["clusters"])
            for meth, x, kind in (("CHORD", c, "kin"), ("MEANDER", w, "route")):
                if os.path.exists(f"{x}/tour.json") or kind == "route":
                    r = row("x", x, kind).split("|")[2:-1]
                    ax, near = extra(x)
                    rows.append(f"| {s} | {st} | {meth} |" + "|".join(r) + f"| {ax:.2f} | {near:.0%} |")
    open(a.table, "w").write("\n".join(rows) + "\n")
    print("\n".join(rows))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--bin", required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--table", default="")
    a = ap.parse_args()
    a.work, a.bin, a.log = (os.path.abspath(x) for x in (a.work, a.bin, a.log))
    S = seeds(dict(K=K, spine=0.0))
    if a.table:
        return table(a, S)
    with ThreadPoolExecutor(a.jobs) as ex:   # one worker per seed: the CHORD-T folders of a seed are shared
        for res in ex.map(lambda s: [one(a, s, st) for st in STRAIGHT], S):
            for r in res:
                print(*r, flush=True)


if __name__ == "__main__":
    main()
