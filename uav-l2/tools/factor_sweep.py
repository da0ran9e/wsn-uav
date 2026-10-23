"""One factor at a time: MEANDER lanes (meander_lane.py) against CHORD-T (mission.py --chordTour) with the same
number of clusters, geometry only (CLAUDE.md §8 item 149).

    python3 tools/factor_sweep.py --work DIR --bin BIN --log LOGDIR [--jobs 3]     # run every pair (resumable)
    python3 tools/factor_sweep.py --work DIR --bin BIN --log LOGDIR --table OUT.md # l2_screen rows per pair

Base: the band of item 147 (8 x 80 cells grown along a 10 km spine bent 120 degrees, width 0.7 km), BS south,
MEANDER lanes 8 cells and clusters at most SPAN 14 cells long, a 400 kB clue set, 45 degree bank. Each factor moves
alone; the other ones stay at the base. Seeds: the first SEEDS seeds whose land is one piece (partition.py's
k-medoids needs connected land).
  size    80 K cells, K 4 6 8 12 16; spine and width scaled by sqrt(K / 8) (the same shape, larger)
  aspect  spine / width 5 / 1.4, 7 / 1.0, 10 / 0.7, 14 / 0.5 km (about the same area), and the compact domain
          without a spine (restructure.domain's default, as the 16 campaign maps)
  bend    0 60 120 180 240 degrees
  bs      south, end, side, centre (restructure.bs_point)
  span    MEANDER clusters at most 10, 14, 18 cells long (CHORD-T takes the count MEANDER gets)
  q       clue set 300, 400, 500 kB: CHORD-T's 80 % rule and the delivery need (kin_time) follow it
  bank    30 45 60 degrees: the speed profile only (kin_time), on the base pairs
"""
import argparse, json, math, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

from partition import pieces
from restructure import domain

SEEDS = 3
BASE = dict(K=8, spine=10.0, width=0.7, bend=120, bs="south", span=14, q=400)
FACTORS = {
    "size": [dict(K=k, spine=round(10 * math.sqrt(k / 8), 2), width=round(0.7 * math.sqrt(k / 8), 2)) for k in (4, 6, 8, 12, 16)],
    "aspect": [dict(spine=0.0)] + [dict(spine=s, width=w) for s, w in ((5, 1.4), (7, 1.0), (10, 0.7), (14, 0.5))],
    "bend": [dict(bend=b) for b in (0, 60, 120, 180, 240)],
    "bs": [dict(bs=b) for b in ("south", "end", "side", "centre")],
    "span": [dict(span=s) for s in (10, 14, 18)],
    "q": [dict(q=q) for q in (300, 400, 500)],
}
TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(TOOLS))


def shape(c):
    return f"spine={c['spine']:g},bend={c['bend']:g},width={c['width']:g}" if c["spine"] > 0 else ""


def name(c):
    fmt = lambda v: f"{v:g}" if isinstance(v, (int, float)) else v
    return "-".join(f"{k}{fmt(c[k])}" for k in ("K", "spine", "width", "bend", "bs", "span", "q")) + f"-s{c['seed']}"


def seeds(c):
    out, s = [], 1
    while len(out) < SEEDS:
        if len(pieces(list(domain(c["K"], s, shape(c))["domain"]))) == 1:
            out.append(s)
        s += 1
    return out


def configs():
    """{(factor, level index): [config per seed]}; the configs shared between factors (the base) once each."""
    out = {}
    for f, levels in FACTORS.items():
        for i, lv in enumerate(levels):
            c = dict(BASE, **lv)
            out[(f, i)] = [dict(c, seed=s) for s in seeds(c)]
    return out


def run(cmd, log):
    return subprocess.run([sys.executable, os.path.join(ROOT, "tools/runlog.py"), log, " ".join(cmd)], cwd=ROOT,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode


def pair(a, c):
    """MEANDER first (its natural cluster count), then CHORD-T with that count; the clue set only changes CHORD-T."""
    n = name(c)
    ml = f"{a.work}/{name(dict(c, q=400))}/ml"
    ch = f"{a.work}/{n}/chord"
    sh = ["--shape", shape(c)] if shape(c) else []
    if not os.path.exists(f"{ml}/c1-curve.json"):
        run(["python3", "uav-l2/tools/meander_lane.py", "--clusters", str(c["K"]), "--seed", str(c["seed"]), *sh,
             "--bs", c["bs"], "--span", str(c["span"]), "--lane", "8", "--work", ml, "--bin", a.bin, "--geometry"],
            f"{a.log}/ml-{name(dict(c, q=400))}.md")
    if not os.path.exists(f"{ml}/c1-curve.json"):
        return n, "meander failed"
    K = json.load(open(f"{ml}/map.json"))["clusters"]
    if not os.path.exists(f"{ch}/tour.json"):
        run(["python3", "uav-l2/tools/mission.py", "--clusters", str(c["K"]), "--seed", str(c["seed"]), *sh,
             "--bs", c["bs"], "--count", str(K), "--work", ch, "--bin", a.bin, "--windowKB", str(c["q"]),
             "--windowAt", "crit", "--critRing", "domain", "--axeNear", "--chordTour", "0.6,0.8", "--geometry"],
            f"{a.log}/chord-{n}.md")
    return n, "ok" if os.path.exists(f"{ch}/tour.json") else "chord failed"


def table(a, C):
    sys.path.insert(0, TOOLS)
    import kin_time
    import numpy as np
    from l2_screen import row
    rows = ["| factor | level | seed | method | " + "|".join(
        ["cụm", "cell", "50 m/s", "45°", "30°", "60°", "trên cụm km", "dẫn km", "nối km", "BS km", "critical",
         "TB m", "p90 m", ">606 m"]) + " |", "|---" * 18 + "|"]
    done = set()
    for (f, i), cs in C.items():
        for c in cs:
            ml, ch = f"{a.work}/{name(dict(c, q=400))}/ml", f"{a.work}/{name(c)}/chord"
            if not (os.path.exists(f"{ch}/tour.json") and os.path.exists(f"{ml}/c1-curve.json")):
                continue
            for meth, w, kind in (("CHORD", ch, "kin"), ("MEANDER", ml, "route")):
                r = row("x", w, kind, c["q"]).split("|")[2:-1]
                rows.append(f"| {f} | {i} | {c['seed']} | {meth} |" + "|".join(r) + "|")
    open(a.table, "w").write("\n".join(rows) + "\n")
    print(f"{len(rows) - 2} rows -> {a.table}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--bin", required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--table", default="")
    a = ap.parse_args()
    a.work, a.bin, a.log = (os.path.abspath(x) for x in (a.work, a.bin, a.log))
    C = configs()
    if a.table:
        return table(a, C)
    todo = {name(c): c for cs in C.values() for c in cs}
    print(f"{len(todo)} pairs")
    order = sorted(todo.values(), key=lambda c: (c["K"], name(c)))   # small maps first
    by = {}
    for c in order:   # one worker per MEANDER folder: pairs sharing it (the clue-set levels) run in sequence
        by.setdefault(name(dict(c, q=400)), []).append(c)
    with ThreadPoolExecutor(a.jobs) as ex:
        for res in ex.map(lambda g: [pair(a, c) for c in g], list(by.values())):
            for n, st in res:
                print(n, st, flush=True)


if __name__ == "__main__":
    main()
