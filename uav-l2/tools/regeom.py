"""Rebuild the geometry of saved mission maps (docs/data/mission/{k*,camp/*}) without new ns-3 traffic runs.

    python3 tools/regeom.py --saved docs/data/mission/camp/k2-s10 --work W/k2-s10 --bin BIN

The saved folders keep only map.json, clusters.csv, tour.json, c*-bearing.json and the River results. This
regenerates the map (stage 1 of mission.py, deterministic by seed) and runs uav-coop-deploy once per cluster with
the saved bearing and CH margin, then checks that the map, the critical cells and the flight segments match.
"""
import argparse, csv, json, math, os, shutil, sys

import mission


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--saved", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--bin", required=True)
    ap.add_argument("--clusters", type=int, required=True)
    ap.add_argument("--seed", type=int, required=True)
    a = ap.parse_args()
    a.bin, S = os.path.abspath(a.bin), os.path.abspath(a.saved)
    os.makedirs(a.work, exist_ok=True)
    os.chdir(a.work)
    a.partition, a.lane = "kmedoids", 4.5
    mission.stage_map(a, os.getcwd())
    for f in ("map.json", "clusters.csv"):
        assert open(f).read().strip() == open(f"{S}/{f}").read().strip() or f == "map.json" and \
            json.load(open(f)) == json.load(open(f"{S}/{f}")), f"{f} differs from the saved map"
    K = json.load(open("map.json"))["clusters"]
    env = dict(os.environ, LD_LIBRARY_PATH=f"{a.bin}/lib")
    for k in range(1, K + 1):
        b = json.load(open(f"{S}/c{k}-bearing.json"))
        shutil.copy(f"{S}/c{k}-bearing.json", ".")
        if not os.path.exists(f"c{k}-path-s35.csv"):
            mission.sh([f"{a.bin}/deploy-bin", f"--regionIn=c{k}-cells.csv", f"--nodesIn=c{k}-nodesin.csv",
                        "--spacings=35", "--angle=180", f"--out=c{k}", f"--bearing={b['bearing']}"]
                       + ([f"--chMargin={b['chMargin']}"] if "chMargin" in b else []), f"c{k}-deploy.log", env)
    for f in os.listdir(S):
        if not os.path.exists(f):
            shutil.copy(f"{S}/{f}", ".")
    # checks: each leg's segment ends match the path ends; the critical cells match the River results
    from mission_report import load_map
    M = load_map(".", schemes=("rf",), with_bits=False)
    for l in json.load(open("tour.json"))["legs"]:
        p = M["cl"][l["cluster"]]["geo"]["path"]
        ends = [tuple(p[0]), tuple(p[-1])][::-1 if l["reversed"] else 1]
        assert math.dist(ends[0], l["start"]) < 0.01 and math.dist(ends[1], l["end"]) < 0.01, f"C{l['cluster']} path"
    for k, C in M["cl"].items():
        saved = {(int(r["q"]), int(r["r"])) for r in csv.DictReader(open(f"r{k}-rf-crit.csv"))}
        assert saved == set(C["P"]["crit"]), f"C{k} critical cells differ"
    print(f"{os.path.basename(S)}: {K} clusters rebuilt and checked")


if __name__ == "__main__":
    sys.exit(main())
