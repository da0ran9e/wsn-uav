"""ns-3 check of curved-Axe Banks (CLAUDE.md §8 item 103): pass + River (prepared) per curved deploy of
tools/curve_banks.py, with banks=parallel and banks=local, same pass bitmaps.

    python3 tools/curve_ns3.py --scratch CURV --bin BIN --angles 100,70 --jobs 3 --out docs/data/curve/ns3.csv
"""
import argparse, csv, glob, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np

EXPORT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uav-coop2/tools/river_export.py")


def one(d, b_):
    env = dict(os.environ, LD_LIBRARY_PATH=f"{b_}/lib")
    run = lambda cmd, log: subprocess.run(cmd, cwd=d, env=env, stdout=open(f"{d}/{log}", "w"), stderr=subprocess.STDOUT)
    if not os.path.exists(f"{d}/pass-bits-r1.bin"):
        run([f"{b_}/pass-bin", "--nodes=deploy-nodes-s35.csv", "--path=deploy-path-s35.csv", "--firstRun=1", "--runs=1",
             "--bits", "--out=pass"], "pass.log")
    out = []
    for banks in ("parallel", "local"):
        if not os.path.exists(f"{d}/r-{banks}-crit.csv"):
            if run([sys.executable, EXPORT, "--deploy=.", "--path=deploy-path-s35.csv", f"--banks={banks}",
                    f"--out=plan-{banks}.txt"], f"plan-{banks}.log").returncode:
                continue   # the path re-enters a cell
            run([f"{b_}/river-bin", "--nodes=deploy-nodes-s35.csv", "--routes=deploy-routes-s35.csv",
                 "--gateways=deploy-gateways-s35.csv", f"--plan=plan-{banks}.txt", "--bits=pass-bits", "--firstRun=1",
                 "--runs=1", "--limit=900", "--gwSelect=quality", "--colours=7", "--scheme=river", "--prep=full",
                 f"--out=r-{banks}"], f"r-{banks}.log")
        if not os.path.exists(f"{d}/r-{banks}-crit.csv"):
            continue
        cr = list(csv.DictReader(open(f"{d}/r-{banks}-crit.csv")))
        ru = next(csv.DictReader(open(f"{d}/r-{banks}-runs.csv")))
        done = np.array([float(r["doneS"]) for r in cr])
        out.append(dict(case=os.path.basename(d), banks=banks, crit=len(cr), missing=sum(int(r["missing"]) > 0 for r in cr),
                        doneMean=round(done.mean(), 2), doneMax=round(done.max(), 2), **{k: ru[k] for k in ru if k not in ("run", "scheme")}))
    print(os.path.basename(d), [(o["banks"], o["doneMean"], o["doneMax"]) for o in out], flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--bin", required=True)
    ap.add_argument("--angles", default="100,70")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    b_ = os.path.abspath(a.bin)
    cases = sorted(d for ang in a.angles.split(",") for d in glob.glob(f"{a.scratch}/*-a{ang}")
                   if os.path.exists(f"{d}/deploy-path-s35.csv"))
    with ThreadPoolExecutor(a.jobs) as ex:
        rows = [r for out in ex.map(lambda d: one(d, b_), cases) for r in out]
    keys = sorted({k for r in rows for k in r}, key=lambda k: (k not in ("case", "banks"), k))
    with open(a.out, "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=keys)
        wr.writeheader()
        wr.writerows(rows)
    pair = {}
    for r in rows:
        pair.setdefault(r["case"], {})[r["banks"]] = r
    both = [p for p in pair.values() if len(p) == 2]
    for k in ("doneMean", "doneMax"):
        d = np.array([p["local"][k] - p["parallel"][k] for p in both])
        print(f"{k}: parallel {np.mean([p['parallel'][k] for p in both]):.1f} s, local {np.mean([p['local'][k] for p in both]):.1f} s, "
              f"paired change {d.mean():+.1f} s, local better in {np.sum(d < 0)}/{len(d)}")


if __name__ == "__main__":
    main()
