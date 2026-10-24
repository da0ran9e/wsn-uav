"""MEANDER with fully straight lanes, each cluster flown just long enough, on random maps, against CHORD-T with the
same cluster count, geometry only (CLAUDE.md §8 item 153).

    python3 tools/trim_sweep.py --work DIR --bin BIN --log LOGDIR [--jobs 3]       # run (resumable)
    python3 tools/trim_sweep.py --work DIR --bin BIN --log LOGDIR --table OUT.md   # one row per pair

Maps as straight_sweep (restructure.domain(8, seed), BS south). MEANDER: lanes 8 cells, straight and parallel
(--parallel), cut so every cluster has --minAxe 2.1 km over its own cells (one copy of the clue set, 2.02 km, and a
small margin), no pull towards critical cells (--reach 1000: the line only bends onto each CH, which the ns-3 pass
needs); VARIANTS: without (par) and with (par-trim5) the lanes' leftover cut off their ends (--trim 5). CHORD-T:
mission.py --chordTour 0.6,0.8 with MEANDER's cluster count. Columns as straight_sweep. --chAnywhere (item 154):
both take the CH the strongest node of the cluster wherever it lies (a random position: the node scores are random).
par-trim5-chord (item 155): MEANDER cut around the CHs CHORD-T's clusters already have (CHORD-T with par-trim5's
count), so both serve the same CHs.
"""
import argparse, json, os
from concurrent.futures import ThreadPoolExecutor

from factor_sweep import run, seeds
from straight_sweep import K, extra

VARIANTS = {"par": ["--parallel"], "par-trim5": ["--parallel", "--trim", "5"],
            "par-trim5-chord": ["--parallel", "--trim", "5"]}
MINAXE = 2.1


def ml(a, s, v):
    return f"{a.work}/s{s}-{v}/ml"


def chord(a, s, k):
    return f"{a.work}/s{s}-K{k}/chord"


def one(a, s, v):
    w = ml(a, s, v)
    ch = a.ch
    if v.endswith("-chord"):   # after par-trim5 and its CHORD-T (VARIANTS' order)
        ch = ["--chFrom", chord(a, s, json.load(open(f"{ml(a, s, 'par-trim5')}/map.json"))["clusters"])]
    if not os.path.exists(f"{w}/c1-curve.json"):
        run(["python3", "uav-l2/tools/meander_lane.py", "--clusters", str(K), "--seed", str(s), "--lane", "8",
             "--minAxe", str(MINAXE), "--reach", "1000", *VARIANTS[v], *ch, "--work", w, "--bin", a.bin,
             "--geometry"],
            f"{a.log}/ml-s{s}-{v}.md")
    if not os.path.exists(f"{w}/c1-curve.json"):
        return s, v, "meander failed"
    k = json.load(open(f"{w}/map.json"))["clusters"]
    c = chord(a, s, k)
    if not os.path.exists(f"{c}/tour.json"):
        run(["python3", "uav-l2/tools/mission.py", "--clusters", str(K), "--seed", str(s), "--count", str(k),
             "--work", c, "--bin", a.bin, "--windowKB", "400", "--windowAt", "crit", "--critRing", "domain",
             "--axeNear", "--chordTour", "0.6,0.8", *a.ch, "--geometry"], f"{a.log}/chord-s{s}-K{k}.md")
    return s, v, "ok" if os.path.exists(f"{c}/tour.json") else "chord failed"


def table(a, S):
    from l2_screen import row
    rows = ["| seed | variant | method | cụm | cell | 50 m/s | 45° | 30° | 60° | trên cụm km | dẫn km | nối km | BS km | "
            "critical | TB m | p90 m | >606 m | Axe ngắn nhất km | critical trong 5 cell |", "|---" * 19 + "|"]
    for s in S:
        for v in VARIANTS:
            w = ml(a, s, v)
            if not os.path.exists(f"{w}/c1-curve.json"):
                continue
            c = chord(a, s, json.load(open(f"{w}/map.json"))["clusters"])
            for meth, x, kind in (("CHORD", c, "kin"), ("MEANDER", w, "route")):
                if os.path.exists(f"{x}/tour.json") or kind == "route":
                    r = row("x", x, kind).split("|")[2:-1]
                    ax, near = extra(x)
                    rows.append(f"| {s} | {v} | {meth} |" + "|".join(r) + f"| {ax:.2f} | {near:.0%} |")
    open(a.table, "w").write("\n".join(rows) + "\n")
    print("\n".join(rows))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--bin", required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--table", default="")
    ap.add_argument("--chAnywhere", action="store_true")
    a = ap.parse_args()
    a.ch = ["--chAnywhere"] if a.chAnywhere else []
    a.work, a.bin, a.log = (os.path.abspath(x) for x in (a.work, a.bin, a.log))
    S = seeds(dict(K=K, spine=0.0))
    if a.table:
        return table(a, S)
    with ThreadPoolExecutor(a.jobs) as ex:   # one worker per seed: the CHORD-T folders of a seed are shared
        for res in ex.map(lambda s: [one(a, s, v) for v in VARIANTS], S):
            for r in res:
                print(*r, flush=True)


if __name__ == "__main__":
    main()
