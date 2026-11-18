"""K9 step B2 regression: a mission folder's crit.csv holding exactly Algorithm 3's set must leave everything unchanged.

    python3 crit_regress.py SCRATCH WORK [WORK ...]

For each WORK (a C4 mission folder): its files are linked into SCRATCH/<name>/ without crit.csv, then with a crit.csv of
Algorithm 3's own cells, and checked:
  plan    river_export.py --out plan{k}.txt with the campaign's flags, byte for byte: without crit.csv, with it, and
          against the plan the campaign flew
  report  mission_report.load_map(...)["cl"][k]["P"]["crit"] (what lm_tour and river_surrogate read)
  bend    meander_lane.critical (mission.py --bendCrit, the meander lanes)
Then a different set (Algorithm 3's minus one cell per cluster, plus one cell that was not critical) must show up in the
plan's CRIT lines exactly. Prints one line per folder and exits 1 on any mismatch.
"""
import csv, filecmp, json, os, shutil, subprocess, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path[:0] = [f"{REPO}/uav-l2/tools", f"{REPO}/uav-coop2/tools"]
from meander_lane import critical  # noqa: E402
from mission_report import load_map  # noqa: E402
from river_plan import load_around, load_crit  # noqa: E402


def link(src, dst):
    shutil.rmtree(dst, ignore_errors=True)
    os.makedirs(dst)
    for f in os.listdir(src):
        if f != "crit.csv" and not (f.startswith("plan") and f.endswith((".txt", ".log"))):
            os.symlink(f"{src}/{f}", f"{dst}/{f}")


def export(w, k, out):
    opts = json.load(open(f"{w}/plan-opts.json"))
    cmd = [sys.executable, f"{REPO}/uav-coop2/tools/river_export.py", f"--deploy=d{k}", f"--path=c{k}-path-s35.csv",
           "--banks=parallel", "--windowKB=400", "--windowAt=crit", "--around=domain-cl.csv", "--axeNear",
           f"--lossDb={opts['lossDb']:g}", f"--out={out}"]
    subprocess.run(cmd, cwd=w, check=True, stdout=subprocess.DEVNULL)


def crits(w):
    M = load_map(w, schemes=())
    return {k: list(c["P"]["crit"]) for k, c in M["cl"].items()}


def write_crit(w, cells):
    with open(f"{w}/crit.csv", "w") as f:
        f.write("q,r\n" + "".join(f"{q},{r}\n" for q, r in sorted(cells)))


def main():
    scratch, works = sys.argv[1], sys.argv[2:]
    bad = 0
    for src in works:
        name = "-".join(src.rstrip("/").split("/")[-3:])
        w = os.path.join(scratch, name)
        link(src, w)
        K = json.load(open(f"{w}/map.json"))["clusters"]
        base = crits(w)
        for k in range(1, K + 1):
            export(w, k, f"plan{k}.txt")
            os.rename(f"{w}/plan{k}.txt", f"{w}/plan{k}-alg3.txt")
        write_crit(w, {h for k in base for h in base[k]})
        same = crits(w) == base
        around = load_around(f"{w}/domain-cl.csv")
        bend = all(critical(list(csv.DictReader(open(f"{w}/c{k}-nodes-s35.csv"))), around) ==
                   critical(list(csv.DictReader(open(f"{w}/c{k}-nodes-s35.csv"))), around, crit_cells=load_crit(w))
                   for k in range(1, K + 1))
        plan_same, plan_flown = True, True
        for k in range(1, K + 1):
            export(w, k, f"plan{k}-file.txt")
            plan_same &= filecmp.cmp(f"{w}/plan{k}-alg3.txt", f"{w}/plan{k}-file.txt", shallow=False)
            plan_flown &= filecmp.cmp(f"{w}/plan{k}-alg3.txt", f"{src}/plan{k}.txt", shallow=False)
        # a different set: drop each cluster's last critical cell (never the only one), add one non-critical CL cell
        want = {}
        for k in range(1, K + 1):
            cl = sorted((int(x["q"]), int(x["r"])) for x in csv.DictReader(open(f"{w}/c{k}-nodes-s35.csv"))
                        if x["isCL"] == "1")
            s = list(base[k][:-1] if len(base[k]) > 1 else base[k]) + [next(h for h in cl if h not in base[k])]
            want[k] = sorted(s)
        write_crit(w, {h for k in want for h in want[k]})
        moved = crits(w) == want
        for k in range(1, K + 1):
            export(w, k, f"plan{k}-moved.txt")
            got = sorted(tuple(map(int, l.split()[1:3])) for l in open(f"{w}/plan{k}-moved.txt") if l.startswith("CRIT "))
            moved &= got == want[k]
        ok = same and bend and plan_same and moved
        bad += not ok
        print(f"{name}: {K} clusters, {sum(map(len, base.values()))} critical cells; report {same}, bend {bend}, "
              f"plan byte-equal {plan_same}, equal to the flown plan {plan_flown}, other set followed {moved}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
