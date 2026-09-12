#!/usr/bin/env python3.10
"""Analysis for the cluster-radius probe: B4, B5, A6 and the composition.

Every number the report quotes is computed here and written to a CSV. The report
plots CSVs; it never computes.

Analysis decisions were fixed in docs/PREREGISTRATION-cluster-radius.md before
the sweeps were read -- in particular R = 60 m is excluded from every exponent fit
because h_max(60) = 0.2 makes T_hop = 5 x T_spread there.
"""
from __future__ import annotations

import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "src"))
import yaml  # noqa: E402
import campaign_stats as S  # noqa: E402
import provenance  # noqa: E402

RES = ROOT / "results"
OUT = RES / "cluster-radius"


def read(p: Path) -> list[dict]:
    with open(p, newline="") as fh:
        return list(csv.DictReader(fh))


def h_max(R: float, r_bc: float, r_tx: float) -> float:
    return max(0.0, (R - r_bc) / r_tx)


def main() -> int:
    cfg_path = ROOT / "config" / "cluster-radius.yaml"
    cfg = yaml.safe_load(cfg_path.read_text())
    g, v, t = cfg["geometry"], cfg["vehicle"], cfg["tour"]
    r_bc, r_tx = g["r_bc_m"], g["r_tx_m"]
    stamp = provenance.stamp(cfg_path)
    prov = {"schema_version": stamp["schema_version"], "prov_id": stamp["prov_id"]}
    OUT.mkdir(parents=True, exist_ok=True)
    FIT_EXCLUDE_R = 60.0          # pre-registered
    out: dict = {"provenance": stamp, "fit_excludes_R_m": FIT_EXCLUDE_R}

    # =================================================== B4 / B5 per-config
    runs = read(RES / "B4" / "runs.csv")
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for r in runs:
        arm = r["run_id"].split("~", 1)[0]
        key = (arm, r["mode"], float(r["R_m"]), float(r["spacing_m"]), int(r["k"]),
               int(r["trickle"]), float(r["adv_interval_s"]))
        groups[key].append(r)

    # A stale or half-written runs.csv once fed this script 12 rows from an old
    # smoke test and it produced a complete-looking summary. Every configuration
    # must carry exactly the declared number of seeds, or the run is refused.
    want = cfg["stats"]["seeds_report"]
    short = {f"{k[0]}|R{k[2]:g}|sp{k[3]:g}|k{k[4]}|tr{k[5]}|ai{k[6]:g}|{k[1]}": len(v)
             for k, v in groups.items() if len(v) != want}
    if short and "--allow-partial" not in sys.argv:
        print(f"REFUSING TO ANALYSE: {len(short)} of {len(groups)} configurations do "
              f"not have exactly {want} seeds. Pass --allow-partial to override.")
        for name, n in sorted(short.items())[:12]:
            print(f"  {name}: {n}")
        if len(short) > 12:
            print(f"  ... and {len(short)-12} more")
        return 2
    out["incomplete_configs"] = short
    out["n_runs"] = len(runs)
    out["n_configs"] = len(groups)

    b4_rows = []
    for key, rs in sorted(groups.items()):
        arm, mode, R, sp, k, tr, ai = key
        n = len(rs)
        cens = sum(int(x["censored"]) for x in rs)
        done = [x for x in rs if int(x["censored"]) == 0]
        ts = [float(x["T_spread_s"]) for x in done]
        hm = h_max(R, r_bc, r_tx)
        # intention-to-treat: censored runs are reported, never dropped
        ci_ts = S.bootstrap_ci(ts, resamples=cfg["stats"]["bootstrap_resamples"]) if ts \
            else S.CI(float("nan"), float("nan"), float("nan"))
        th = [x / hm for x in ts] if hm > 0 else []
        ci_th = S.bootstrap_ci(th, resamples=cfg["stats"]["bootstrap_resamples"]) if th \
            else S.CI(float("nan"), float("nan"), float("nan"))
        pkts = [float(x["pkt_total"]) for x in rs]
        fracs = [float(x["frac_complete"]) for x in rs]
        mac_tx = sum(float(x["mac_tx"]) for x in rs)
        mac_drop = sum(float(x["mac_tx_drop"]) for x in rs)
        cens_ci = S.wilson(cens, n)
        b4_rows.append({
            "arm": arm, "mode": mode, "R_m": R, "spacing_m": sp, "k": k,
            "trickle": tr, "adv_interval_s": ai, "n_seeds": n,
            "n_nodes": float(rs[0]["n_nodes"]),
            "n_c": float(rs[0]["n_nodes"]),
            "seeded_frac": round(S.mean([float(x["n_seeded"]) / float(x["n_nodes"])
                                         for x in rs]), 5),
            "h_max": round(hm, 4),
            "censored": cens, "censored_rate": round(cens_ci.point, 5),
            "censored_lo": round(cens_ci.lo, 5), "censored_hi": round(cens_ci.hi, 5),
            "frac_complete_mean": round(S.mean(fracs), 6),
            "T_spread_med": round(ci_ts.point, 4), "T_spread_lo": round(ci_ts.lo, 4),
            "T_spread_hi": round(ci_ts.hi, 4),
            "T_hop_med": round(ci_th.point, 4) if th else "",
            "T_hop_lo": round(ci_th.lo, 4) if th else "",
            "T_hop_hi": round(ci_th.hi, 4) if th else "",
            "pkts_med": round(S.median(pkts), 1),
            "pkts_per_node_med": round(S.median([p / float(rs[0]["n_nodes"])
                                                 for p in pkts]), 3),
            "mac_tx_total": mac_tx, "mac_tx_drop_total": mac_drop,
            "mac_drop_rate": round(mac_drop / mac_tx, 6) if mac_tx else "",
            "send_fail_total": sum(float(x["send_fail"]) for x in rs),
            **prov})
    with open(OUT / "b4_by_config.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, list(b4_rows[0]))
        w.writeheader()
        w.writerows(b4_rows)

    def pick(**kw) -> list[dict]:
        # Reject unknown column names loudly. Calling this with R= instead of
        # R_m= silently selected nothing and quietly dropped whole fits.
        unknown = set(kw) - set(b4_rows[0])
        if unknown:
            raise KeyError(f"no such column(s) in b4_by_config: {sorted(unknown)}")
        return [r for r in b4_rows
                if all(abs(r[a] - b) < 1e-9 if isinstance(b, float) else r[a] == b
                       for a, b in kw.items())]

    # ------------------------------------------------- exponent fits
    fits = {}

    def fit(name, rows, xkey, ykey, note=""):
        rows = [r for r in rows if r[ykey] != "" and r[xkey] > 0]
        xs = [r[xkey] for r in rows]
        ys = [float(r[ykey]) for r in rows]
        if len(xs) < 3:
            fits[name] = {"exponent": None, "note": "too few points " + note}
            return
        b, a, r2 = S.loglog_slope(xs, ys)
        ci = S.bootstrap_slope_ci(xs, ys, resamples=2000)
        fits[name] = {"exponent": round(b, 4), "ci_lo": round(ci.lo, 4),
                      "ci_hi": round(ci.hi, 4), "r2": round(r2, 4),
                      "prefactor": round(math.exp(a), 6), "n_points": len(xs),
                      "x": xkey, "y": ykey, "note": note}

    main_k8 = [r for r in pick(arm="main", k=8) if r["R_m"] != FIT_EXCLUDE_R]
    fit("T_hop_vs_R_k8", main_k8, "R_m", "T_hop_med",
        "R=60 excluded (pre-registered: h_max=0.2 there)")
    fit("T_spread_vs_R_k8", main_k8, "R_m", "T_spread_med", "R=60 excluded")
    for R in (150.0, 250.0):
        fit(f"T_hop_vs_k_R{int(R)}", pick(arm="main", R_m=R), "k", "T_hop_med",
            "exponent in k; k/lambda floor predicts ~1")
    # n_c axis: combine the spacing arm with the matching main config
    for R in cfg["sweep"]["spacing_sweep_R_m"]:
        rows = [r for r in b4_rows
                if r["R_m"] == float(R) and r["k"] == 8 and r["trickle"] == 1
                and r["mode"] == "spread" and r["arm"] in ("main", "spacing")]
        fit(f"T_spread_vs_nc_R{R}", rows, "n_c", "T_spread_med",
            "spatial reuse vs R^2 traffic growth")
    fit("T_hop_vs_advint_R150",
        pick(arm="advint", R_m=150.0) + pick(arm="main", R_m=150.0, k=8),
        "adv_interval_s", "T_hop_med", "protocol sensitivity, not a channel property")
    # --- separate the fixed startup latency from the marginal per-hop cost ---
    # T_spread = a + b * h_max. The ratio T_spread/h_max conflates the two and
    # blows up as h_max -> 0, which is the whole reason R=60 (h_max = 0.2) had to
    # be excluded from the exponent fits. b is the quantity the closed form for R*
    # actually wants.
    hop_fit = {}
    for k in cfg["sweep"]["k_values"]:
        rs = [r for r in pick(arm="main", k=k)
              if r["T_hop_med"] != "" and r["R_m"] != FIT_EXCLUDE_R]
        xs = [r["h_max"] for r in rs]
        ys = [float(r["T_spread_med"]) for r in rs]
        if len(xs) >= 3:
            ca, cb, r2 = S.bootstrap_linear_ci(xs, ys)
            hop_fit[k] = {
                "startup_latency_s": round(ca.point, 4),
                "startup_ci": [round(ca.lo, 4), round(ca.hi, 4)],
                "marginal_per_hop_s": round(cb.point, 4),
                "marginal_per_hop_ci": [round(cb.lo, 4), round(cb.hi, 4)],
                "r2": round(r2, 4), "n_points": len(xs),
                "note": "T_spread = a + b*h_max over R in 94..300 (R=60 excluded)",
            }
    out["hop_cost_fit"] = hop_fit
    out["fits"] = fits

    # ------------------------------------------------- B5
    b5 = [r for r in b4_rows if r["mode"] == "seedonly"]
    b5_runs = [r for r in runs if r["mode"] == "seedonly"]
    tot_nodes = sum(int(r["n_nodes"]) for r in b5_runs)
    tot_complete = sum(int(r["n_complete"]) for r in b5_runs)
    if not b5_runs:
        # A missing arm is reported, never silently treated as a pass.
        out["B5"] = {"verdict": "NOT RUN", "n_runs": 0, "total_nodes": 0,
                     "nodes_completing_all_k_without_pooling": None,
                     "fraction": None, "wilson_lo": None, "wilson_hi": None,
                     "seeded_frac_mean": None,
                     "claim": "no individual node collects enough on its own; "
                              "pooling is a precondition, not an optimisation"}
    else:
        w5 = S.wilson(tot_complete, tot_nodes)
        out["B5"] = {
            "n_runs": len(b5_runs), "total_nodes": tot_nodes,
            "nodes_completing_all_k_without_pooling": tot_complete,
            "fraction": w5.point, "wilson_lo": w5.lo, "wilson_hi": w5.hi,
            "seeded_frac_mean": round(S.mean([r["seeded_frac"] for r in b5]), 5),
            "claim": "no individual node collects enough on its own; pooling is a "
                     "precondition, not an optimisation",
            "verdict": ("SUPPORTED" if tot_complete == 0 else "REFUTED"),
        }

    # =================================================== A6
    bhh = read(RES / "A6" / "t1_bhh.csv")
    dub_path = RES / "A6" / "t1_dubins.csv"
    dub = read(dub_path) if dub_path.exists() else []
    a6_rows = []
    for arm, rows in (("bhh", bhh), ("dubins", dub)):
        byk: dict[tuple, list[dict]] = defaultdict(list)
        for r in rows:
            byk[(float(r["eta"]), float(r["R_m"]))].append(r)
        for (eta, R), rs in sorted(byk.items()):
            t1 = [float(x["T1_s"]) for x in rs]
            ln = [float(x["tour_len_m"]) for x in rs]
            ci = S.bootstrap_ci(t1, resamples=cfg["stats"]["bootstrap_resamples"])
            kap = [float(x["max_kappa_rho"]) for x in rs if x["max_kappa_rho"] != ""]
            a6_rows.append({
                "arm": arm, "eta": eta, "R_m": R, "n_seeds": len(rs),
                "C_realised_med": S.median([float(x["C_realised"]) for x in rs]),
                "C_asymptotic": float(rs[0]["C_asymptotic"]),
                "tour_len_med_m": round(S.median(ln), 2),
                "T1_med_s": round(ci.point, 3), "T1_lo_s": round(ci.lo, 3),
                "T1_hi_s": round(ci.hi, 3),
                "max_kappa_rho": round(max(kap), 9) if kap else "",
                **prov})
    with open(OUT / "a6_by_config.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, list(a6_rows[0]))
        w.writeheader()
        w.writerows(a6_rows)

    # Dubins vs BHH ratio, and the kinematic bound
    eta0 = cfg["scenario"]["eta_reference"]
    ratios = []
    for R in g["R_grid_dubins_m"]:
        b = next((r for r in a6_rows if r["arm"] == "bhh" and r["eta"] == eta0
                  and r["R_m"] == float(R)), None)
        d = next((r for r in a6_rows if r["arm"] == "dubins" and r["eta"] == eta0
                  and r["R_m"] == float(R)), None)
        if b and d and b["T1_med_s"] > 0:
            ratios.append({"R_m": float(R), "bhh_T1_s": b["T1_med_s"],
                           "dubins_T1_s": d["T1_med_s"],
                           "ratio": round(d["T1_med_s"] / b["T1_med_s"], 4),
                           "below_kinematic_bound":
                               int(float(R) < v["kinematic_R_min_m"]), **prov})
    with open(OUT / "dubins_vs_bhh.csv", "w", newline="") as fh:
        if ratios:
            w = csv.DictWriter(fh, list(ratios[0]))
            w.writeheader()
            w.writerows(ratios)
    above = [r["ratio"] for r in ratios if not r["below_kinematic_bound"]]
    below = [r["ratio"] for r in ratios if r["below_kinematic_bound"]]
    out["kinematic_bound"] = {
        "R_min_m": v["kinematic_R_min_m"],
        "dubins_over_bhh_above_bound": [round(min(above), 3), round(max(above), 3)]
            if above else None,
        "dubins_over_bhh_below_bound": [round(min(below), 3), round(max(below), 3)]
            if below else None,
        "mean_above": round(S.mean(above), 4) if above else None,
        "mean_below": round(S.mean(below), 4) if below else None,
        "penalty_pct": round(100 * (S.mean(below) / S.mean(above) - 1), 2)
            if above and below else None,
        "worst_kappa_rho_over_all_tours":
            round(max(float(r["max_kappa_rho"]) for r in a6_rows
                      if r["max_kappa_rho"] != ""), 9) if dub else None,
    }

    # =================================================== composition
    # T_total(R) = T1(R) + T_spread(R); both from measured per-seed samples so the
    # CI on the sum is a joint bootstrap over the two independent seed sets.
    def seed_samples_T1(arm, eta, R):
        src = dub if arm == "dubins" else bhh
        return [float(x["T1_s"]) for x in src
                if abs(float(x["eta"]) - eta) < 1e-9 and abs(float(x["R_m"]) - R) < 1e-9]

    def seed_samples_Tspread(R, k):
        return [float(x["T_spread_s"]) for x in runs
                if x["mode"] == "spread" and int(x["trickle"]) == 1
                and abs(float(x["R_m"]) - R) < 1e-9 and int(x["k"]) == k
                and abs(float(x["spacing_m"]) - cfg["sweep"]["spacing_reference_m"]) < 1e-9
                and abs(float(x["adv_interval_s"]) - cfg["protocol"]["adv_interval_s"]) < 1e-9
                and int(x["censored"]) == 0]

    comp_rows = []
    comp_curves = {}
    import random
    # Two T1 sources. BHH covers the whole flight grid; the realised Dubins tour
    # covers only the five R where LKH was run but is ~1.7x longer. BHH is the
    # CONSERVATIVE choice for the conclusion reached here: a smaller T1 shrinks
    # the 1/R term and so pulls R* DOWN, towards the operating range. Both are
    # computed and reported.
    for t1_src in ("bhh", "dubins"):
        grid = (g["R_grid_flight_m"] if t1_src == "bhh" else g["R_grid_dubins_m"])
        for k in cfg["sweep"]["k_values"]:
            Rs, med, lo, hi = [], [], [], []
            for R in grid:
                t1s = seed_samples_T1(t1_src, eta0, float(R))
                tss = seed_samples_Tspread(float(R), k)
                if not t1s or not tss:
                    continue
                rng = random.Random(20260912 + k + int(R))
                reps = []
                for _ in range(2000):
                    a = t1s[rng.randrange(len(t1s))]
                    b = tss[rng.randrange(len(tss))]
                    reps.append(a + b)
                reps.sort()
                point = S.median(t1s) + S.median(tss)
                Rs.append(float(R)); med.append(point)
                lo.append(reps[int(0.025 * len(reps))])
                hi.append(reps[int(0.975 * len(reps))])
                comp_rows.append({"t1_source": t1_src, "k": k, "R_m": float(R),
                                  "T1_med_s": round(S.median(t1s), 3),
                                  "T_spread_med_s": round(S.median(tss), 3),
                                  "T_total_med_s": round(point, 3),
                                  "T_total_lo_s": round(reps[int(0.025*len(reps))], 3),
                                  "T_total_hi_s": round(reps[int(0.975*len(reps))], 3),
                                  "T_spread_share": round(S.median(tss) / point, 5),
                                  **prov})
            comp_curves[(t1_src, k)] = (Rs, med, lo, hi)
    with open(OUT / "composition.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, list(comp_rows[0]))
        w.writeheader()
        w.writerows(comp_rows)

    # R*: grid-search argmin on the measured curve, with a bootstrap CI, plus the
    # closed form. Both reported even when they disagree.
    rstar = {}
    rstar_dubins = {}
    sc_h = math.sqrt(g["hex_packing_coeff"])
    for t1_src in ("bhh", "dubins"):
      target = rstar if t1_src == "bhh" else rstar_dubins
      for k in cfg["sweep"]["k_values"]:
        Rs, med, _, _ = comp_curves[(t1_src, k)]
        if not Rs:
            continue
        i = min(range(len(med)), key=lambda j: med[j])
        # bootstrap R* by resampling both components per R
        rng = random.Random(777 + k)
        stars = []
        samples = {}
        for R in Rs:
            samples[R] = (seed_samples_T1(t1_src, eta0, R), seed_samples_Tspread(R, k))
        for _ in range(2000):
            curve = []
            for R in Rs:
                a, b = samples[R]
                curve.append(S.mean([a[rng.randrange(len(a))] for _ in range(8)])
                             + S.mean([b[rng.randrange(len(b))] for _ in range(8)]))
            stars.append(Rs[min(range(len(curve)), key=lambda j: curve[j])])
        stars.sort()
        # closed form from the measured T_hop at the reference R
        ref = pick(arm="main", R_m=150.0, k=k)
        th = float(ref[0]["T_hop_med"]) if ref and ref[0]["T_hop_med"] != "" else None
        closed = (math.sqrt(r_tx * t["beta_bhh"] * g["area_m2"]
                            / (sc_h * v["v_mps"] * th)) if th else None)
        # Same closed form fed the MARGINAL per-hop cost b instead of the ratio
        # T_spread/h_max, which is the quantity the derivation actually assumes.
        bmarg = (hop_fit.get(k) or {}).get("marginal_per_hop_s")
        closed_marg = (math.sqrt(r_tx * t["beta_bhh"] * g["area_m2"]
                                 / (sc_h * v["v_mps"] * bmarg))
                       if bmarg and bmarg > 0 else None)
        target[k] = {
            "t1_source": t1_src,
            "R_star_grid_m": Rs[i],
            "R_star_ci_m": [stars[int(0.025 * len(stars))],
                            stars[int(0.975 * len(stars))]],
            "T_total_at_R_star_s": round(med[i], 2),
            "interior_to_operating_range": bool(
                g["operating_range_m"][0] < Rs[i] < g["operating_range_m"][1]),
            "at_upper_boundary": Rs[i] >= g["operating_range_m"][1],
            "at_lower_boundary": Rs[i] <= g["operating_range_m"][0],
            "T_hop_used_s": th,
            "R_star_closed_form_m": round(closed, 1) if closed else None,
            "marginal_per_hop_s": bmarg,
            "R_star_closed_form_marginal_m": (round(closed_marg, 1)
                                              if closed_marg else None),
            "grid_max_R_m": max(Rs),
            "note": "grid search is capped by the R grid; a closed-form R* beyond "
                    "max(R) means the measured curve is still falling at the edge",
        }
    out["R_star"] = rstar
    out["R_star_with_realised_dubins_T1"] = rstar_dubins
    out["closed_form_selfcheck"] = {
        "T_hop_2s_gives_R_star_m": round(
            math.sqrt(r_tx * 0.7 * g["area_m2"] / (sc_h * v["v_mps"] * 2.0)), 1),
        "task_states_m": 736,
        "T_hop_needed_for_R_star_400m_s": round(
            r_tx * t["beta_bhh"] * g["area_m2"] / (sc_h * v["v_mps"] * 400.0 ** 2), 3),
    }

    # ================================================= pre-registration scorecard
    # The ranges below are transcribed from
    # docs/PREREGISTRATION-cluster-radius.md, which was committed BEFORE these
    # sweeps were read (git history is the evidence). The verdicts are computed
    # mechanically against those ranges so they cannot be written to taste after
    # seeing the data.
    REG = {
        "3.1": {"T_hop_band_s": [1.3, 4.0], "refute_above_s": 10.0},
        "3.2": {"k_exponent": [0.6, 1.4]},
        "3.3": {"R_exponent": [-0.9, -0.3]},
        "3.4": {"nc_exponent_max": 0.2, "nc_exponent_min": -0.4},
        "3.5": {"R_star_above_m": 400.0},
        "3.6": {"min_ratio_gap_pct": 5.0},
        "3.7": {"nodes_completing": 0},
    }
    sc = {}

    th8 = [r["T_hop_med"] for r in pick(arm="main", k=8)
           if r["T_hop_med"] != "" and r["R_m"] >= 94.0]
    th8 = [float(x) for x in th8]
    lo_b, hi_b = REG["3.1"]["T_hop_band_s"]
    if th8 and max(th8) > REG["3.1"]["refute_above_s"]:
        sc["3.1"] = "REFUTED"
    elif th8 and lo_b <= min(th8) and max(th8) <= hi_b:
        sc["3.1"] = "CONFIRMED"
    else:
        sc["3.1"] = "PARTIAL (right order of magnitude, outside the stated band)"

    def in_range(key, rng):
        f = fits.get(key) or {}
        e = f.get("exponent")
        if e is None:
            return "NOT MEASURED"
        return "CONFIRMED" if rng[0] <= e <= rng[1] else "REFUTED"

    sc["3.2"] = in_range("T_hop_vs_k_R150", REG["3.2"]["k_exponent"])
    sc["3.3"] = in_range("T_hop_vs_R_k8", REG["3.3"]["R_exponent"])
    sc["3.4"] = in_range("T_spread_vs_nc_R150",
                         [REG["3.4"]["nc_exponent_min"], REG["3.4"]["nc_exponent_max"]])
    k8v = rstar.get(8) or {}
    sc["3.5"] = ("CONFIRMED" if k8v.get("at_upper_boundary")
                 or (k8v.get("R_star_closed_form_m") or 0) > REG["3.5"]["R_star_above_m"]
                 else "REFUTED")
    gap = out["kinematic_bound"]["penalty_pct"]
    sc["3.6"] = ("CONFIRMED" if gap is not None
                 and gap > REG["3.6"]["min_ratio_gap_pct"] else "REFUTED")
    sc["3.7"] = ("NOT MEASURED" if out["B5"]["verdict"] == "NOT RUN"
                 else "CONFIRMED"
                 if out["B5"]["nodes_completing_all_k_without_pooling"]
                 == REG["3.7"]["nodes_completing"] else "REFUTED")
    out["registered_ranges"] = REG
    out["scorecard"] = sc

    (OUT / "summary.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print(json.dumps({"fits": {k: v.get("exponent") for k, v in fits.items()},
                      "B5": out["B5"]["verdict"],
                      "R_star": {k: v["R_star_grid_m"] for k, v in rstar.items()},
                      "kinematic_penalty_pct":
                          out["kinematic_bound"]["penalty_pct"],
                      "scorecard": sc}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
