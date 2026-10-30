"""Export one (work folder, scheme) of the Deluge-lite experiment as dl_cells / dl_runs rows (SigDrop 2 backup design).

    python3 dl_export.py WORK REGIME SEED TAG OUT      -> OUT-cells.csv, OUT-runs.csv, OUT-check.txt, OUT-raw/

Readiness of a critical cell = when team 1 leaves its cluster (kin_time 45 degree profile, as lm_tour.py score)
plus the cell's doneS in r<k>-TAG-crit.csv; not done before the run's limit -> ready=0, t_ready_s empty.
Frames per run, summed over the clusters: frames_data, frames_adv, frames_req are the MAC data frames delivered
(hops: gather + bankfill + circlefill + pull; advert; control = requests and summaries); frames_total is every PHY
transmission start on the ground (data, adverts, requests, ACKs, retries; -energy.csv), UAV broadcasts excluded.
"""
import csv, glob, hashlib, os, shutil, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uav-l2/tools"))
import kin_time

w, reg, seed, tag, out = sys.argv[1:6]
CFG = {"rf": "-", "dla": "0.5-8", "dlb": "2-60", "t": "1-64"}
SCH = "RIVER" if tag == "rf" else "DL"
leave = kin_time.run(w, "kin")[1][45]["leave"]
K = len(glob.glob(f"{w}/r*-{tag}-runs.csv"))
cells, tot, check = [], dict(frames_data=0, frames_adv=0, frames_req=0, frames_total=0, wall_s=0.0), []
os.makedirs(f"{out}-raw", exist_ok=True)
for k in range(1, K + 1):
    for x in ("crit", "runs"):
        shutil.copy(f"{w}/r{k}-{tag}-{x}.csv", f"{out}-raw/r{k}-{tag}-{x}.csv")
    run = next(csv.DictReader(open(f"{w}/r{k}-{tag}-runs.csv")))
    tot["frames_data"] += sum(int(run[p]) for p in ("gather", "bankfill", "circlefill", "pull"))
    tot["frames_adv"] += int(run.get("advert", 0))
    tot["frames_req"] += int(run["control"])
    tot["wall_s"] += float(run["wallS"])
    tot["frames_total"] += sum(int(r["framesTx"]) for r in csv.DictReader(open(f"{w}/r{k}-{tag}-energy.csv")))
    bits = hashlib.sha256(open(f"{w}/pass{k}-bits-r1.bin", "rb").read()).hexdigest()[:16]
    crit = list(csv.DictReader(open(f"{w}/r{k}-{tag}-crit.csv")))
    check.append(f"c{k}: pass bits {bits}, D <= {run['D']} (max per cell {max(int(c['D']) for c in crit)}), "
                 f"missing {sum(int(c['missing']) for c in crit)}, done {sum(float(c['doneS']) >= 0 for c in crit)}"
                 f"/{len(crit)}, sim {run['simS']} s")
    for c in crit:
        d = float(c["doneS"])
        cells.append(dict(map="k12", regime=reg, seed=seed, scheme=SCH, trickle_cfg=CFG[tag], cell_id=f"{c['q']}:{c['r']}",
                          cluster_id=k, ready=int(d >= 0), t_ready_s=round(leave[k] + d, 1) if d >= 0 else ""))
ready = [c["t_ready_s"] for c in cells if c["ready"]]
runs = [dict(map="k12", regime=reg, seed=seed, scheme=SCH, trickle_cfg=CFG[tag], n_crit=len(cells), n_ready=len(ready),
             mean_ready_s=round(sum(ready) / len(ready), 1) if ready else "", max_ready_s=max(ready, default=""),
             **{k: round(v, 1) if k == "wall_s" else v for k, v in tot.items()})]
for name, rows in (("cells", cells), ("runs", runs)):
    with open(f"{out}-{name}.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)
open(f"{out}-check.txt", "w").write("\n".join(check) + "\n")
print(f"{reg} R{seed} {tag}: {len(ready)}/{len(cells)} ready, mean {runs[0]['mean_ready_s']} s, "
      f"frames {tot['frames_total']}, wall {tot['wall_s']:.0f} s")
