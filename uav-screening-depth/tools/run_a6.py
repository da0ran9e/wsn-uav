#!/usr/bin/env python3.10
"""A6: the flight side. T_1(R) by BHH estimate and by an actual Dubins tour.

Pure Python, no ns-3. Two arms:
  bhh     every R in the flight grid, every eta, N=120 scenarios  (closed form)
  dubins  heading sampling -> GTSP -> Noon-Bean -> ATSP -> LKH, at 5 R values
          (the task asks for at least four) plus eta at three R values

Curvature is asserted on every realised tour: |kappa| <= 1/rho, measured
numerically from the sampled path, not inferred from the segment labels.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

import yaml  # noqa: E402
import provenance  # noqa: E402
from screening import model as M  # noqa: E402
from screening import scenario as SC  # noqa: E402
from screening import tour as T  # noqa: E402

OUT = ROOT / "results" / "A6"


def _bhh_one(args):
    cfg, eta, R, seed = args
    g, v, t, sc_cfg = cfg["geometry"], cfg["vehicle"], cfg["tour"], cfg["scenario"]
    sc = SC.generate(seed, n_nodes=sc_cfg["n_nodes"], side_m=g["side_m"], eta=eta)
    chs, counts = SC.cluster_heads(sc, float(R))
    C = len(chs)
    ell = T.bhh_tour_length_m(C, g["area_m2"], t["beta_bhh"])
    C_asym = M.clusters_from_area(g["area_m2"], float(R), g["hex_packing_coeff"])
    return dict(arm="bhh", eta=eta, R_m=R, seed=seed, C_realised=C,
                C_asymptotic=round(C_asym, 4),
                n_cells_total=len(SC.hex_centres(g["side_m"], float(R))),
                tour_len_m=round(ell, 3), T1_s=round(ell / v["v_mps"], 4),
                max_kappa_rho="", solver="bhh", words="", wall_s="",
                mean_members=round(sum(counts) / max(C, 1), 3))


def _dubins_one(args):
    cfg, eta, R, seed = args
    g, v, t, sc_cfg = cfg["geometry"], cfg["vehicle"], cfg["tour"], cfg["scenario"]
    sc = SC.generate(seed, n_nodes=sc_cfg["n_nodes"], side_m=g["side_m"], eta=eta)
    chs, counts = SC.cluster_heads(sc, float(R))
    t0 = time.time()
    res = T.dubins_tour(chs, rho=v["rho_m"], n_headings=t["n_headings"],
                        ds_m=t["curvature_sample_m"], seed=1)
    # Hard acceptance check: a tour violating the curvature bound is not a result.
    if res.max_kappa_rho > 1.0 + 1e-6:
        raise AssertionError(
            f"curvature violated: |kappa|*rho = {res.max_kappa_rho} at "
            f"R={R} eta={eta} seed={seed}")
    C_asym = M.clusters_from_area(g["area_m2"], float(R), g["hex_packing_coeff"])
    return dict(arm="dubins", eta=eta, R_m=R, seed=seed, C_realised=res.n_clusters,
                C_asymptotic=round(C_asym, 4),
                n_cells_total=len(SC.hex_centres(g["side_m"], float(R))),
                tour_len_m=round(res.length_m, 3),
                T1_s=round(res.length_m / v["v_mps"], 4),
                max_kappa_rho=round(res.max_kappa_rho, 9), solver=res.solver,
                words=json.dumps(res.words, sort_keys=True),
                wall_s=round(time.time() - t0, 3),
                mean_members=round(sum(counts) / max(res.n_clusters, 1), 3))


COLS = ["arm", "eta", "R_m", "seed", "C_realised", "C_asymptotic", "n_cells_total",
        "mean_members", "tour_len_m", "T1_s", "max_kappa_rho", "solver", "words",
        "wall_s", "schema_version", "prov_id"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--arms", default="bhh,dubins")
    a = ap.parse_args()

    cfg_path = ROOT / "config" / "cluster-radius.yaml"
    cfg = yaml.safe_load(cfg_path.read_text())
    g, st, sc_cfg = cfg["geometry"], cfg["stats"], cfg["scenario"]
    seeds = [st["seed_report_base"] + i for i in range(st["seeds_report"])]
    stamp = provenance.stamp(cfg_path)
    prov = {"schema_version": stamp["schema_version"], "prov_id": stamp["prov_id"]}
    OUT.mkdir(parents=True, exist_ok=True)
    provenance.write_config_txt(OUT / "config.txt", cfg, cfg_path)
    provenance.write_env_txt(OUT / "env.txt")

    arms = a.arms.split(",")
    t0 = time.time()

    if "bhh" in arms:
        work = [(cfg, eta, R, s) for eta in sc_cfg["eta_values"]
                for R in g["R_grid_flight_m"] for s in seeds]
        print(f"A6 bhh: {len(work)} scenarios", flush=True)
        with ProcessPoolExecutor(max_workers=a.workers) as ex:
            rows = list(ex.map(_bhh_one, work, chunksize=32))
        with open(OUT / "t1_bhh.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, COLS)
            w.writeheader()
            for r in rows:
                w.writerow({**r, **prov})
        print(f"  -> t1_bhh.csv ({len(rows)} rows, {time.time()-t0:.0f}s)", flush=True)

    if "dubins" in arms:
        work = [(cfg, sc_cfg["eta_reference"], R, s)
                for R in g["R_grid_dubins_m"] for s in seeds]
        work += [(cfg, eta, R, s) for eta in sc_cfg["eta_values"]
                 if eta != sc_cfg["eta_reference"]
                 for R in sc_cfg["eta_dubins_R_m"] for s in seeds]
        print(f"A6 dubins: {len(work)} tours (LKH)", flush=True)
        t1 = time.time()
        # Write incrementally. These tours take tens of seconds each at the
        # largest C, and buffering them all until the end meant one interrupted
        # run threw away every completed tour.
        rows = []
        with open(OUT / "t1_dubins.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, COLS)
            w.writeheader()
            with ProcessPoolExecutor(max_workers=a.workers) as ex:
                for i, r in enumerate(ex.map(_dubins_one, work, chunksize=1), 1):
                    rows.append(r)
                    w.writerow({**r, **prov})
                    fh.flush()
                    if i % 60 == 0:
                        print(f"    {i}/{len(work)} tours, {time.time()-t1:.0f}s",
                              flush=True)
        worst = max(float(r["max_kappa_rho"]) for r in rows)
        print(f"  -> t1_dubins.csv ({len(rows)} rows, {time.time()-t1:.0f}s); "
              f"worst |kappa|*rho over every realised tour = {worst:.9f}", flush=True)

    print(f"A6 total wall {time.time()-t0:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
