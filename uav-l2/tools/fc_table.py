"""CHORD (P*) against FC, one row per map, channel and design, with the keys that run it again (CLAUDE.md §8
items 166-167).

    python3 tools/fc_table.py OUT L1 WORK [WORK ...]

L1: the --out prefix of the l1_rank run that scored the WORKs with the methods P+prog-kin-puq-stage-zero-redir-kt
(CHORD) and FC-puq-stage-zero-redir, its sets named by channel; WORK: a mission folder (mission.py --mapRuns), named
by its map (k8-s1, ...), its channel in env.txt (none: open). Writes OUT.md (the results table and the seeds table)
and OUT.csv. Columns:
  team1    team 1's flight, BS to BS (CHORD: kin_time at 45 degree bank with the delivery fixes; FC: fc_baseline)
  ready    when a critical cell holds its data at its CL, mean / max over the critical cells (CHORD: leave + River's
           doneS, a run not done by its deadline counted at leave + 900 s; FC: decode + in-cell gather)
  clues    critical cells holding all 12 clues (CHORD: River's mask, d = 0 of the cells file; FC: decoded)
  Tstar    when team 2 has verified c*: mean, 95 % half-width, median, p90 over the draws; rank: c*'s place in
           team 2's visits; Tall: team 2 back at the BS after every critical cell
Seeds: map (mission.py --seed; map_gen, partition), ns-3 mission index 100000 K + 100 seed + k of cluster k (pass:
A2G fading; River: G2G shadowing, fades, MAC), FC's reception (numpy default_rng, the first 8 bytes of
sha256("FC/<map>/<channel>"), little-endian), layer-1 draws d = 0..n-1 (each critical cell's store: sha256
("<map>/<d>/<q>/<r>"); the CHs' LoRa phases: sha256("<map>"), first 4 bytes).
"""
import csv, json, os, sys

import numpy as np

import kin_time
from mission import ENV_LOSS
from mission_report import load_map

CH, FC = "P+prog-kin-puq-stage-zero-redir-kt", "FC-puq-stage-zero-redir"


def main():
    out, l1, works = sys.argv[1], sys.argv[2], sys.argv[3:]
    draws = list(csv.DictReader(open(f"{l1}-draws.csv")))
    cells = list(csv.DictReader(open(f"{l1}-cells.csv")))
    rows, seeds = [], []
    for w in works:
        name = os.path.basename(os.path.normpath(w))
        env = open(f"{w}/env.txt").read().strip() if os.path.exists(f"{w}/env.txt") else "open"
        K, seed = (int(v) for v in name[1:].split("-s"))
        M = load_map(w, schemes=("rf",), with_bits=False)
        n = len(M["cl"])
        crits = [(k, h) for k in sorted(M["cl"]) for h in M["cl"][k]["P"]["crit"]]
        _, o = kin_time.run(w, "kin")
        done = {x: float(M["cl"][x[0]]["res"]["rf"][x[1]]["doneS"]) for x in crits}
        ready = [o[45]["leave"][x[0]] + (900.0 if done[x] < 0 else done[x]) for x in crits]
        fc = json.load(open(f"{w}/fc-info.json"))
        for meth, label in ((CH, "CHORD"), (FC, "FC")):
            X = [r for r in draws if r["map"] == name and r["set"] == env and r["method"] == meth]
            ts = np.array([float(r["Tstar"]) for r in X])
            r = dict(map=name, channel=env, clusters=n, crits=len(crits), design=label, draws=len(X),
                     team1=round(float(X[0]["team1"]), 1), Tstar=round(ts.mean(), 1),
                     ci=round(1.96 * ts.std(ddof=1) / np.sqrt(len(ts)), 1), median=round(float(np.median(ts)), 1),
                     p90=round(float(np.percentile(ts, 90)), 1),
                     rank=round(float(np.mean([float(r["rank"]) for r in X])), 2),
                     Tall=round(float(np.mean([float(r["Tall"]) for r in X])), 1))
            if label == "CHORD":
                C = [c for c in cells if c["map"] == name and c["set"] == env]
                r.update(ready_mean=round(float(np.mean(ready)), 1), ready_max=round(float(np.max(ready)), 1),
                         clues=sum(int(c["riverAll"]) for c in C), stalls=sum(v < 0 for v in done.values()),
                         visits="", loops="")
            else:
                r.update(ready_mean=round(fc["ready"][0], 1), ready_max=round(fc["ready"][1], 1),
                         clues=fc["complete"], stalls="", visits=fc["visits"], loops=fc["loops"])
            rows.append(r)
        seeds.append(dict(map=name, channel=env, lossDb=ENV_LOSS[env], K=K, seed=seed, clusters=n,
                          mission=f"{100000 * K + 100 * seed + 1}-{100000 * K + 100 * seed + n}",
                          fc_key=f"FC/{name}/{env}", draws=len({r["draw"] for r in draws if r["map"] == name})))
    with open(f"{out}.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)
    md = ["| bản đồ | kênh | cụm | critical cell | phương án | đội 1 bay (s) | sẵn sàng TB / max (s) | đủ 12 manh mối | "
          "ghé / vòng lượn | T\\* TB ± 95 % (s) | T\\* trung vị / p90 (s) | hạng c\\* | Tall (s) |",
          "|---" * 13 + "|"]
    for r in rows:
        gl = f"{r['visits']} / {r['loops']:g}" if r["design"] == "FC" else (f"River kẹt {r['stalls']}" if r["stalls"]
                                                                              else "")
        md.append(f"| {r['map']} | {r['channel']} | {r['clusters']} | {r['crits']} | {r['design']} | {r['team1']:.0f} | "
                  f"{r['ready_mean']:.0f} / {r['ready_max']:.0f} | {r['clues']}/{r['crits']} | {gl} | "
                  f"{r['Tstar']:.0f} ± {r['ci']:.0f} | {r['median']:.0f} / {r['p90']:.0f} | {r['rank']:.2f} | "
                  f"{r['Tall']:.0f} |")
    md += ["", "| bản đồ | kênh | suy hao thêm (dB) | --clusters | --seed | cụm | mission index ns-3 | khoá FC | "
           "lượt bốc lớp 1 |", "|---" * 9 + "|"]
    md += [f"| {s['map']} | {s['channel']} | {s['lossDb']:g} | {s['K']} | {s['seed']} | {s['clusters']} | "
           f"{s['mission']} | `{s['fc_key']}` | 0–{s['draws'] - 1} |" for s in seeds]
    open(f"{out}.md", "w").write("\n".join(md) + "\n")


if __name__ == "__main__":
    main()
