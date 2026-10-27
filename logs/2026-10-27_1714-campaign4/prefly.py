"""Copy of logs/2026-10-27_1800-lm-dtspn/prefly.py for this campaign: repo-relative tools path, mission index with
the simulation seed of runseed.txt (mission.py --runSeed; item 188), the clusters counted from map.json.

DTSP-N + River does not fly over the CH, which pass-bin requires (coop-pass.cc: CHECK dPath(CH) < 1 m; the CH
is used for nothing else in the pass). For each such cluster of WORK: a nodes file with one extra receive-only node
at the point of the path nearest the CH, flagged as the CH (the real CH unflagged), the pass flown with it as
mission.py would, and the extra node's row (the last) cut from the bitmap. mission.py then finds the bitmap and
skips the pass; River reads it with the real nodes file.

    python3 prefly.py WORK ENV K SEED BIN
"""
import csv, json, math, os, subprocess, sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uav-l2/tools"))
from mission import ENV_LOSS, runseed  # noqa: E402

w, env, K, seed, BIN = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
for k in range(1, json.load(open(f"{w}/map.json"))["clusters"] + 1):   # K is the target count (k16: 15)
    if os.path.exists(f"{w}/pass{k}-bits-r1.bin"):
        continue
    nodes = list(csv.DictReader(open(f"{w}/c{k}-nodes-s35.csv")))
    ch = next(n for n in nodes if n["isCH"] == "1")
    P = np.array([[float(r["x"]), float(r["y"])] for r in csv.DictReader(open(f"{w}/c{k}-path-s35.csv"))])
    d = np.linalg.norm(P - [float(ch["x"]), float(ch["y"])], axis=1)
    if d.min() < 1.0:
        continue   # flies over the CH: mission.py runs the pass itself
    p = P[int(np.argmin(d))]
    extra = dict(ch, id=str(max(int(n["id"]) for n in nodes) + 1), x=f"{p[0]:.3f}", y=f"{p[1]:.3f}", isCH="1")
    with open(f"{w}/c{k}-nodes-pass.csv", "w") as f:
        wr = csv.DictWriter(f, fieldnames=list(nodes[0]), lineterminator="\n")
        wr.writeheader()
        wr.writerows([dict(n, isCH="0") for n in nodes] + [extra])
    run = 100000 * K + 100 * seed + k + 10000000 * (runseed(w) - 1)   # as mission.py --mapRuns --runSeed
    cmd = [f"{BIN}/pass-bin", f"--nodes=c{k}-nodes-pass.csv", f"--path=c{k}-path-s35.csv", f"--firstRun={run}",
           "--runs=1", "--bits", f"--out=pass{k}", *([f"--lossDb={ENV_LOSS[env]:g}"] if ENV_LOSS[env] else [])]
    with open(f"{w}/pass{k}.log", "w") as log:
        subprocess.run(cmd, cwd=w, stdout=log, stderr=subprocess.STDOUT, check=True,
                       env=dict(os.environ, LD_LIBRARY_PATH=f"{BIN}/pass-lib"))
    b = np.fromfile(f"{w}/pass{k}-bits-r{run}.bin", dtype=np.uint8).reshape(len(nodes) + 1, -1)
    b[:-1].tofile(f"{w}/pass{k}-bits-r{run}.bin")
    os.symlink(f"pass{k}-bits-r{run}.bin", f"{w}/pass{k}-bits-r1.bin")
    print(f"C{k}: CH {d.min():.0f} m off the path, flown with an extra node there", flush=True)
