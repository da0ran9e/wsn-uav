#!/usr/bin/env python3.10
"""B4 + B5: measure T_spread, and hence T_hop(R, n_c), in ns-3.

Drives ns3/cell-spread.cc over the sweep in config/cluster-radius.yaml. Each
worker owns one CSV so appends are never interleaved; the shards are merged at
the end.

The sweep is REDUCED from the full 7x3x3x2 factorial to 45 configurations. N=120
seeds per configuration is a hard rule (AGENT-BRIEF 8) and is NOT reduced; the
factorial is. What is kept: the full R x k grid (the mechanism is T_hop ~ k/lambda,
so k matters), the spacing axis at three R (n_c independent of R), Trickle on/off
at every R, and an advertisement-interval sensitivity axis. See STATUS.md.
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import yaml  # noqa: E402
import provenance  # noqa: E402

NS3 = Path(os.environ.get("NS3_DIR", Path.home() / "ns3-dev"))
BIN = NS3 / "build" / "scratch" / "ns3.46-cell-spread-default"
OUT = ROOT / "results" / "B4"


def jobs(cfg: dict) -> list[dict]:
    g, r, pr, sw, st = (cfg["geometry"], cfg["radio"], cfg["protocol"],
                        cfg["sweep"], cfg["stats"])
    base = dict(rtx=g["r_tx_m"], rbc=g["r_bc_m"], txPower=r["tx_power_dBm"],
                fragBytes=r["frag_bytes"], advIntervalMax=pr["adv_interval_max_s"],
                trickleK=pr["trickle_k"], suppressWindow=pr["suppress_window_s"],
                stopTime=pr["stop_time_s"])
    seeds = [st["seed_report_base"] + i for i in range(st["seeds_report"])]
    out: list[dict] = []

    def add(arm, **kw):
        for s in seeds:
            j = dict(base)
            j.update(kw)
            j["seed"] = s
            j["arm"] = arm
            j["runId"] = (f"{arm}|R{kw['R']}|sp{kw['spacing']}|k{kw['k']}|"
                          f"tr{kw['trickle']}|ai{kw.get('advInterval', pr['adv_interval_s'])}|"
                          f"{kw.get('mode','spread')}|s{s}")
            out.append(j)

    # 1. the primary R x k grid
    for R, k in itertools.product(g["R_grid_m"], sw["k_values"]):
        add("main", R=R, spacing=sw["spacing_reference_m"], k=k, trickle=1,
            advInterval=pr["adv_interval_s"], mode="spread")
    # 2. n_c varied independently of R
    for R in sw["spacing_sweep_R_m"]:
        for sp in sw["spacing_values_m"]:
            if sp == sw["spacing_reference_m"]:
                continue
            add("spacing", R=R, spacing=sp, k=8, trickle=1,
                advInterval=pr["adv_interval_s"], mode="spread")
    # 3. Trickle suppression off
    for R in g["R_grid_m"]:
        add("trickle_off", R=R, spacing=sw["spacing_reference_m"], k=8, trickle=0,
            advInterval=pr["adv_interval_s"], mode="spread")
    # 4. advertisement-interval sensitivity
    for ai in pr["adv_interval_sweep_s"]:
        add("advint", R=150, spacing=sw["spacing_reference_m"], k=8, trickle=1,
            advInterval=ai, mode="spread")
    # 5. B5: seeding only, no relaying
    for R in g["R_grid_m"]:
        add("seedonly", R=R, spacing=sw["spacing_reference_m"], k=8, trickle=1,
            advInterval=pr["adv_interval_s"], mode="seedonly",
            stopTime=pr["stop_time_seedonly_s"])
    return out


def run_shard(args) -> tuple[int, int, float]:
    shard, job_list, want_curves = args
    csv_path = OUT / f"shard-{shard:02d}.csv"
    curve_path = OUT / f"curve-{shard:02d}.csv"
    ok = fail = 0
    t0 = time.time()
    for j in job_list:
        cmd = [str(BIN)]
        for key in ("R", "spacing", "k", "trickle", "rtx", "rbc", "txPower",
                    "fragBytes", "advInterval", "advIntervalMax", "trickleK",
                    "suppressWindow", "stopTime", "seed", "mode"):
            if key in j:
                cmd.append(f"--{key}={j[key]}")
        cmd.append(f"--outCsv={csv_path}")
        cmd.append(f"--runId={j['arm']}~{j['runId']}")
        if want_curves and j["seed"] < 1003:
            cmd.append(f"--curveCsv={curve_path}")
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            ok += 1 if p.returncode == 0 else 0
            fail += 0 if p.returncode == 0 else 1
        except subprocess.TimeoutExpired:
            fail += 1
    return ok, fail, time.time() - t0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--limit", type=int, default=0, help="smoke test: first N jobs")
    a = ap.parse_args()

    cfg_path = ROOT / "config" / "cluster-radius.yaml"
    cfg = yaml.safe_load(cfg_path.read_text())
    if not BIN.exists():
        print(f"FATAL: ns-3 binary missing: {BIN}")
        return 2

    OUT.mkdir(parents=True, exist_ok=True)
    for old in list(OUT.glob("shard-*.csv")) + list(OUT.glob("curve-*.csv")):
        old.unlink()
    provenance.write_config_txt(OUT / "config.txt", cfg, cfg_path)
    provenance.write_env_txt(OUT / "env.txt")

    jl = jobs(cfg)
    if a.limit:
        jl = jl[: a.limit]
    shards = [[] for _ in range(a.workers)]
    for i, j in enumerate(jl):
        shards[i % a.workers].append(j)
    print(f"B4/B5: {len(jl)} runs over {len(set(j['runId'].rsplit('|s',1)[0] for j in jl))} "
          f"configurations, {a.workers} workers")
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        res = list(ex.map(run_shard, [(i, s, True) for i, s in enumerate(shards)]))
    ok = sum(r[0] for r in res)
    fail = sum(r[1] for r in res)
    print(f"done: ok={ok} fail={fail} wall={time.time()-t0:.0f}s")

    # merge shards
    rows, header = [], None
    for sh in sorted(OUT.glob("shard-*.csv")):
        with open(sh, newline="") as fh:
            rd = csv.reader(fh)
            h = next(rd)
            header = header or h
            assert h == header, f"shard header mismatch in {sh}"
            rows.extend(rd)
    stamp = provenance.stamp(cfg_path)
    with open(OUT / "runs.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header + ["schema_version", "prov_id"])
        for r in rows:
            w.writerow(r + [stamp["schema_version"], stamp["prov_id"]])
    crows, cheader = [], None
    for sh in sorted(OUT.glob("curve-*.csv")):
        with open(sh, newline="") as fh:
            rd = csv.reader(fh)
            h = next(rd)
            cheader = cheader or h
            crows.extend(rd)
    if crows:
        with open(OUT / "curves.csv", "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(cheader)
            w.writerows(crows)
    print(f"merged {len(rows)} rows -> {OUT/'runs.csv'}; {len(crows)} curve points")
    (OUT / "meta.json").write_text(json.dumps(
        {"n_runs": len(rows), "ok": ok, "fail": fail,
         "wall_s": round(time.time() - t0, 1), "provenance": stamp}, indent=2) + "\n")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
