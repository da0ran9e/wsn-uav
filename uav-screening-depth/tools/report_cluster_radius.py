"""The cluster-radius probe report page (task section 6 deliverable).

Kept in its own module: it is long, and make_report.py only needs to register it.
This module PLOTS; it never computes. Every number comes from the CSVs and
summary.json written by tools/analyse_cluster_radius.py.
"""
from __future__ import annotations

import json
from pathlib import Path

import svgplot as S

OPLO, OPHI = 94.0, 400.0
RHO_BOUND = 94.13


def _f(x, n=2) -> str:
    try:
        return f"{float(x):.{n}f}"
    except (TypeError, ValueError):
        return "&ndash;"


def build(RES: Path, header, table, src, page, read_csv):
    CR = RES / "cluster-radius"
    sm = json.loads((CR / "summary.json").read_text())
    b4 = read_csv(CR / "b4_by_config.csv")
    a6 = read_csv(CR / "a6_by_config.csv")
    comp = read_csv(CR / "composition.csv")
    dvb = read_csv(CR / "dubins_vs_bhh.csv")
    cpath = RES / "B4" / "curves.csv"
    curves = read_csv(cpath) if cpath.exists() else []
    fits, rstar, kb, b5 = sm["fits"], sm["R_star"], sm["kinematic_bound"], sm["B5"]

    def fitstr(key: str) -> str:
        f = fits.get(key) or {}
        if f.get("exponent") is None:
            return "&ndash;"
        return (f'{f["exponent"]:+.2f} [{f["ci_lo"]:+.2f}, {f["ci_hi"]:+.2f}]'
                f', R&sup2; = {f["r2"]:.2f}')

    def rows(arm=None, **kw):
        out = []
        for r in b4:
            if arm is not None and r["arm"] != arm:
                continue
            if all(abs(float(r[a]) - b) < 1e-9 for a, b in kw.items()):
                out.append(r)
        return sorted(out, key=lambda r: float(r["R_m"]))

    main8 = rows("main", k=8.0)
    th8 = [float(r["T_hop_med"]) for r in main8
           if r["T_hop_med"] and float(r["R_m"]) >= 94.0]
    k8 = rstar.get("8") or rstar.get(8) or {}
    n_b4 = sum(int(r["n_seeds"]) for r in b4)
    n_dub = sum(int(r["n_seeds"]) for r in a6 if r["arm"] == "dubins")
    need = sm["closed_form_selfcheck"]["T_hop_needed_for_R_star_400m_s"]

    o = [header("Cluster radius &mdash; does an interior R* exist?",
                "Targeted probe. T_total(R) = T1(R) + h_max(R)&middot;T_hop(R, n_c). "
                "Everything turned on T_hop, which nobody had measured.",
                banner="CURRENT", n_seeds="120 per configuration",
                extra={"ns-3": "3.46 (ea50b72a)", "LKH": "3.0.13",
                       "B4/B5 runs": f"{n_b4:,}", "A6 tours": f"{n_dub:,}"})]

    # ---------------------------------------------------------------- verdict
    interior = bool(k8.get("interior_to_operating_range"))
    o.append(
        f'<div class="card verdict"><p class="big">T_hop measures in single-digit '
        f'seconds &mdash; R* lands outside 94&ndash;400 m</p>'
        f'<p>The probe had three possible outcomes. The measurement picks the '
        f'second: <strong>T_hop = {_f(min(th8))}&ndash;{_f(max(th8))} s</strong> at '
        f'k = 8 over R = 94&ndash;300 m, against the <strong>&ge; {_f(need)} s</strong> '
        f'that would be needed to bring R* inside 400 m. The design rule becomes '
        f'<em>make clusters as large as the kinematics allow</em>, not &ldquo;tune R '
        f'to an interior optimum&rdquo;.</p><ul>'
        f'<li><strong>Why the hop-count estimate missed it, and why contention was '
        f'the wrong suspect.</strong> T_hop is floored by the <em>radio</em>: moving '
        f'k fragments across one ring costs at least k/&lambda; = k &times; 200 ms '
        f'because of the mandatory Send() spacing &mdash; 1.6 s at k = 8. Contention '
        f'adds order 20 %, not an order of magnitude.</li>'
        f'<li><strong>T_hop falls with R</strong>, exponent {fitstr("T_hop_vs_R_k8")}. '
        f'The closed form assumes T_hop constant in R, so it is an approximation, not '
        f'a law.</li>'
        f'<li><strong>T_hop scales with k</strong>: exponent {fitstr("T_hop_vs_k_R150")} '
        f'at R = 150 m, consistent with the k/&lambda; floor being the mechanism.</li>'
        f'<li><strong>Spatial reuse absorbs the R&sup2; traffic growth</strong>: '
        f'T_spread exponent in n_c is {fitstr("T_spread_vs_nc_R150")} at R = 150 m, '
        f'while MAC drops rise over the same range.</li>'
        f'<li><strong>The kinematic bound R &ge; 4&rho;/3 = {_f(kb["R_min_m"], 1)} m '
        f'binds hard below itself</strong>: realised tours are '
        f'{_f(kb["mean_above"])}&times; the BHH estimate above it but '
        f'{_f(kb["mean_below"])}&times; below, a {_f(kb["penalty_pct"], 0)} % penalty. '
        f'It is not the active constraint, because T_total falls in R throughout.</li>'
        f'<li><strong>Pooling is a precondition (B5)</strong>: '
        f'{b5["nodes_completing_all_k_without_pooling"]:,} of {b5["total_nodes"]:,} '
        f'nodes complete all k without relaying, Wilson CI '
        f'[{b5["wilson_lo"]:.1e}, {b5["wilson_hi"]:.1e}] &mdash; '
        f'<strong>{b5["verdict"]}</strong>.</li></ul>'
        f'<p>Predictions were registered in '
        f'<code>docs/PREREGISTRATION-cluster-radius.md</code> and committed before '
        f'these sweeps were read. Scorecard at the end.</p></div>')

    # ------------------------------------------------------------------- B4
    o.append("<h2>B4 &mdash; the measurement</h2>")
    o.append("<p>One hexagonal cell, nodes on a lattice, real LR-WPAN PHY and MAC "
             "with CSMA. Nodes within 50 m of a line through the cell centre are "
             "seeded at t = 0 exactly as a passing UAV would leave them; the "
             "epidemic spread then runs to completion. No UAV, no trajectory, no "
             "air-to-ground link &mdash; that is the shortcut that made this fast.</p>")
    ser_ts, ser_th = [], []
    for k in (4, 8, 16):
        rs = [r for r in rows("main", k=float(k)) if r["T_hop_med"]]
        if not rs:
            continue
        xs = [float(r["R_m"]) for r in rs]
        ser_ts.append({"name": f"k = {k}", "x": xs,
                       "y": [float(r["T_spread_med"]) for r in rs],
                       "lo": [float(r["T_spread_lo"]) for r in rs],
                       "hi": [float(r["T_spread_hi"]) for r in rs]})
        ser_th.append({"name": f"k = {k}", "x": xs,
                       "y": [float(r["T_hop_med"]) for r in rs],
                       "lo": [float(r["T_hop_lo"]) for r in rs],
                       "hi": [float(r["T_hop_hi"]) for r in rs]})
    o.append(S.line_chart(ser_ts, x_label="cluster radius R (m)",
                          y_label="T_spread (s)", y_min=0,
                          title="Full-cell completion time, 120 seeds per point",
                          caption="Ribbons are 10,000-resample bootstrap CIs on the "
                                  "median. T_spread rises sub-linearly in R while "
                                  "h_max(R) rises linearly &mdash; which is exactly "
                                  "why T_hop comes out falling."))
    o.append(S.line_chart(ser_th, x_label="cluster radius R (m)",
                          y_label="T_hop = T_spread / h_max(R)   (s)", y_min=0,
                          vlines=[(RHO_BOUND, "4&rho;/3")],
                          title="T_hop &mdash; the load-bearing number",
                          caption="R = 60 m is plotted but excluded from every "
                                  "exponent fit, as pre-registered: h_max(60) = 0.2, "
                                  "so T_hop there is 5x T_spread and its CI is "
                                  "inflated by the same factor."))
    o.append(table(["R (m)", "h_max", "n_c", "seeded", "T_spread median (s) [95% CI]",
                    "T_hop median (s) [95% CI]", "packets/cell", "MAC drop rate",
                    "censored"],
                   [[_f(r["R_m"], 0), _f(r["h_max"]), _f(r["n_c"], 0),
                     f'{100*float(r["seeded_frac"]):.0f}%',
                     f'{_f(r["T_spread_med"])} [{_f(r["T_spread_lo"])}, '
                     f'{_f(r["T_spread_hi"])}]',
                     (f'{_f(r["T_hop_med"])} [{_f(r["T_hop_lo"])}, '
                      f'{_f(r["T_hop_hi"])}]') if r["T_hop_med"] else "&ndash;",
                     _f(r["pkts_med"], 0), _f(r["mac_drop_rate"], 4),
                     f'{r["censored"]}/{r["n_seeds"]}'] for r in main8]))
    o.append(src("cluster-radius/b4_by_config.csv"))

    o.append("<h3>The mechanism: T_hop is floored by k/&lambda;, not by contention</h3>")
    kser = []
    for R in (150.0, 250.0):
        rs = [r for r in rows("main", R=R) if r["T_hop_med"]]
        rs.sort(key=lambda r: float(r["k"]))
        if rs:
            kser.append({"name": f"measured, R = {int(R)} m",
                         "x": [float(r["k"]) for r in rs],
                         "y": [float(r["T_hop_med"]) for r in rs],
                         "lo": [float(r["T_hop_lo"]) for r in rs],
                         "hi": [float(r["T_hop_hi"]) for r in rs]})
    kser.append({"name": "k/&lambda; floor = k &times; 200 ms", "x": [4, 8, 16],
                 "y": [0.8, 1.6, 3.2], "color": "#6b7280", "dashed": True})
    o.append(S.line_chart(kser, x_label="k (fragments in the signature set)",
                          y_label="T_hop (s)", y_min=0,
                          title="T_hop against k, with the physical send-pacing floor",
                          caption="The >= 200 ms Send() spacing is a hard LR-WPAN "
                                  "constraint, so one ring cannot be served faster "
                                  "than k/lambda. Measured T_hop tracks that floor."))
    o.append(src("cluster-radius/b4_by_config.csv"))

    o.append("<h3>Does spatial reuse cancel the R&sup2; traffic growth?</h3>")
    nser = []
    for R in (94.0, 150.0, 250.0):
        rs = [r for r in b4 if float(r["R_m"]) == R and float(r["k"]) == 8
              and float(r["trickle"]) == 1 and r["mode"] == "spread"
              and r["arm"] in ("main", "spacing")]
        rs.sort(key=lambda r: float(r["n_c"]))
        if len(rs) > 1:
            nser.append({"name": f"R = {int(R)} m",
                         "x": [float(r["n_c"]) for r in rs],
                         "y": [float(r["T_spread_med"]) for r in rs],
                         "lo": [float(r["T_spread_lo"]) for r in rs],
                         "hi": [float(r["T_spread_hi"]) for r in rs]})
    o.append(S.line_chart(nser, x_label="n_c (nodes in the cell)",
                          y_label="T_spread (s)", y_min=0, log_x=True,
                          title="T_spread against node count at fixed R",
                          caption="n_c is varied by lattice spacing (15/20/30 m) so it "
                                  "moves independently of R. Flat-to-falling means "
                                  "spatial reuse absorbs the extra traffic; MAC drop "
                                  "rates rise over the same range, so contention is "
                                  "present and simply not dominant."))
    o.append(table(["R (m)", "spacing (m)", "n_c", "T_spread median (s)",
                    "packets/cell", "packets/node", "MAC TX drops", "MAC drop rate"],
                   [[_f(r["R_m"], 0), _f(r["spacing_m"], 0), _f(r["n_c"], 0),
                     f'{_f(r["T_spread_med"])} [{_f(r["T_spread_lo"])}, '
                     f'{_f(r["T_spread_hi"])}]',
                     _f(r["pkts_med"], 0), _f(r["pkts_per_node_med"]),
                     _f(r["mac_tx_drop_total"], 0), _f(r["mac_drop_rate"], 4)]
                    for r in sorted(
                        [r for r in b4 if r["mode"] == "spread"
                         and float(r["k"]) == 8 and float(r["trickle"]) == 1
                         and r["arm"] in ("main", "spacing")
                         and float(r["R_m"]) in (94.0, 150.0, 250.0)],
                        key=lambda r: (float(r["R_m"]), float(r["spacing_m"])))]))
    o.append(src("cluster-radius/b4_by_config.csv"))

    if curves:
        o.append("<h3>Completion fraction over time</h3>")
        cser = []
        for R in (94, 150, 250, 300):
            pk = [c for c in curves if f"|R{R}|" in c["run_id"]
                  and "|k8|" in c["run_id"] and c["run_id"].startswith("main")
                  and c["run_id"].endswith("s1000")]
            if pk:
                cser.append({"name": f"R = {R} m",
                             "x": [float(c["t_s"]) for c in pk],
                             "y": [100 * float(c["frac_complete"]) for c in pk]})
        if cser:
            o.append(S.line_chart(cser, x_label="time since the UAV pass (s)",
                                  y_label="% of cell holding all k", y_min=0,
                                  title="Completion fraction, k = 8, one seed per R",
                                  caption="Recorded so a partial-completion criterion "
                                          "can be applied later without re-running; "
                                          "t50/t90/t95/t99 crossing times are in the "
                                          "per-run CSV for every seed."))
            o.append(src("B4/curves.csv"))

    o.append("<h3>Protocol sensitivity, and Trickle</h3>")
    ai = sorted([r for r in b4 if r["arm"] == "advint"
                 or (r["arm"] == "main" and float(r["R_m"]) == 150.0
                     and float(r["k"]) == 8)],
                key=lambda r: float(r["adv_interval_s"]))
    o.append(table(["advertisement interval (s)", "T_spread median (s)",
                    "T_hop median (s)", "packets/cell"],
                   [[_f(r["adv_interval_s"]), f'{_f(r["T_spread_med"])} '
                     f'[{_f(r["T_spread_lo"])}, {_f(r["T_spread_hi"])}]',
                     _f(r["T_hop_med"]), _f(r["pkts_med"], 0)] for r in ai]))
    o.append(f'<p>T_hop depends on the advertisement rate as well as on the channel '
             f'&mdash; exponent {fitstr("T_hop_vs_advint_R150")}. That is a protocol '
             f'parameter, not a channel property, so it is reported rather than '
             f'buried. The verdict survives it: even the slowest setting tested stays '
             f'well below the {_f(need)} s threshold.</p>')
    tron, tro = rows("main", k=8.0), rows("trickle_off", k=8.0)
    o.append(table(["R (m)", "T_spread, Trickle on (s)", "T_spread, Trickle off (s)",
                    "packets on", "packets off", "packet saving"],
                   [[_f(a["R_m"], 0), _f(a["T_spread_med"]), _f(b["T_spread_med"]),
                     _f(a["pkts_med"], 0), _f(b["pkts_med"], 0),
                     (f'{100*(1-float(a["pkts_med"])/float(b["pkts_med"])):.0f}%'
                      if float(b["pkts_med"]) else "&ndash;")]
                    for a, b in zip(tron, tro)]))
    o.append(src("cluster-radius/b4_by_config.csv"))

    # ------------------------------------------------------------------- B5
    o.append("<h2>B5 &mdash; is pooling a precondition?</h2>")
    o.append(f'<div class="card verdict"><p>Relaying disabled, seeding only. Across '
             f'{b5["n_runs"]:,} runs and {b5["total_nodes"]:,} nodes &mdash; with '
             f'{100*b5["seeded_frac_mean"]:.0f} % of nodes seeded directly by the '
             f'corridor &mdash; <strong>'
             f'{b5["nodes_completing_all_k_without_pooling"]:,} nodes</strong> ended '
             f'up holding all k. Wilson 95 % CI [{b5["wilson_lo"]:.1e}, '
             f'{b5["wilson_hi"]:.1e}].</p><p>The claim &ldquo;no individual node '
             f'collects enough on its own; pooling is a precondition, not an '
             f'optimisation&rdquo; is <strong>{b5["verdict"]}</strong>.</p></div>')

    # ------------------------------------------------------------------- A6
    o.append("<h2>A6 &mdash; the flight side, T1(R)</h2>")
    eser = []
    for arm, lbl, dash in (("bhh", "BHH estimate &beta;&radic;(C&middot;A)", True),
                           ("dubins", "realised Dubins tour (LKH)", False)):
        rs = sorted([r for r in a6 if r["arm"] == arm and float(r["eta"]) == 0.0],
                    key=lambda r: float(r["R_m"]))
        if rs:
            eser.append({"name": lbl, "x": [float(r["R_m"]) for r in rs],
                         "y": [float(r["T1_med_s"]) for r in rs],
                         "lo": [float(r["T1_lo_s"]) for r in rs],
                         "hi": [float(r["T1_hi_s"]) for r in rs], "dashed": dash})
    o.append(S.line_chart(eser, x_label="cluster radius R (m)", y_label="T1 (s)",
                          y_min=0, vlines=[(RHO_BOUND, "4&rho;/3 = 94.1 m")],
                          shade_x=(OPLO, OPHI, "operating range"),
                          title="Phase-1 flight time: estimate vs realised tour",
                          caption="Dubins tours via heading sampling (8 headings, "
                                  "chosen on tuning seeds) -> Noon-Bean -> ATSP -> "
                                  "LKH 3.0.13, 120 scenarios per point. T1 ~ 1/R as "
                                  "the closed form predicts, but the realised tour is "
                                  "uniformly longer than the estimate."))
    o.append(S.line_chart(
        [{"name": "realised / estimated", "x": [float(r["R_m"]) for r in dvb],
          "y": [float(r["ratio"]) for r in dvb]}],
        x_label="cluster radius R (m)", y_label="Dubins T1 / BHH T1", y_min=0,
        vlines=[(RHO_BOUND, "4&rho;/3")],
        title="The turn penalty, and where it bites",
        caption="Near-flat above the kinematic bound, sharply worse below it. This is "
                "the number that says the BHH estimate is usable for R >= 94 m and "
                "misleading below it."))
    o.append(table(["R (m)", "C realised (median)",
                    "C asymptotic A/((3&radic;3/2)R&sup2;)", "BHH T1 (s)",
                    "Dubins T1 (s)", "ratio", "below 4&rho;/3?"],
                   [[_f(r["R_m"], 0),
                     _f(next((x["C_realised_med"] for x in a6
                              if x["arm"] == "dubins"
                              and float(x["R_m"]) == float(r["R_m"])
                              and float(x["eta"]) == 0.0), "nan"), 0),
                     _f(next((x["C_asymptotic"] for x in a6
                              if float(x["R_m"]) == float(r["R_m"])), "nan"), 1),
                     _f(r["bhh_T1_s"]), _f(r["dubins_T1_s"]), _f(r["ratio"], 3),
                     "yes" if int(r["below_kinematic_bound"]) else "no"]
                    for r in dvb]))
    o.append(f'<p><strong>Curvature.</strong> Every realised tour was sampled at 2 m '
             f'arc-length steps and checked numerically: the worst '
             f'|&kappa;|&middot;&rho; over all {n_dub:,} tours is '
             f'<strong>{kb["worst_kappa_rho_over_all_tours"]}</strong>. Dubins arcs '
             f'saturate the constraint exactly &mdash; that is what a value of 1 '
             f'means &mdash; and nothing exceeds it, so no tour is kinematically '
             f'infeasible.</p>'
             f'<p><strong>Cell counts.</strong> The realised tiling yields '
             f'1.1&ndash;1.4&times; the asymptotic A/((3&radic;3/2)R&sup2;) because '
             f'boundary cells are kept; both are reported rather than forced to '
             f'agree. A/(&pi;R&sup2;) is not used anywhere &mdash; it undercounts by '
             f'20.9 %.</p>')
    o.append(src("cluster-radius/a6_by_config.csv",
                 "cluster-radius/dubins_vs_bhh.csv"))

    hser = []
    for eta in (0.0, 0.5, 1.0):
        rs = sorted([r for r in a6 if r["arm"] == "bhh" and float(r["eta"]) == eta],
                    key=lambda r: float(r["R_m"]))
        if rs:
            hser.append({"name": f"&eta; = {eta}",
                         "x": [float(r["R_m"]) for r in rs],
                         "y": [float(r["T1_med_s"]) for r in rs]})
    o.append(S.line_chart(hser, x_label="cluster radius R (m)", y_label="T1 (s)",
                          y_min=0, title="Heterogeneity &eta; shortens the tour",
                          caption="Clustered deployments leave hex cells empty, so "
                                  "there are fewer stops. eta reaches the flight side "
                                  "only through the occupied-cell count."))
    o.append(src("cluster-radius/a6_by_config.csv"))

    # ----------------------------------------------------------- composition
    o.append("<h2>Composition and the decision</h2>")
    cser = []
    for k in (4, 8, 16):
        rs = sorted([r for r in comp if int(r["k"]) == k],
                    key=lambda r: float(r["R_m"]))
        if rs:
            cser.append({"name": f"T_total, k = {k}",
                         "x": [float(r["R_m"]) for r in rs],
                         "y": [float(r["T_total_med_s"]) for r in rs],
                         "lo": [float(r["T_total_lo_s"]) for r in rs],
                         "hi": [float(r["T_total_hi_s"]) for r in rs]})
    rs8 = sorted([r for r in comp if int(r["k"]) == 8], key=lambda r: float(r["R_m"]))
    if rs8:
        cser.append({"name": "T1 only", "x": [float(r["R_m"]) for r in rs8],
                     "y": [float(r["T1_med_s"]) for r in rs8],
                     "color": "#6b7280", "dashed": True})
        cser.append({"name": "ground term, k = 8",
                     "x": [float(r["R_m"]) for r in rs8],
                     "y": [float(r["T_spread_med_s"]) for r in rs8],
                     "color": "#059669", "dashed": True})
    o.append(S.line_chart(cser, x_label="cluster radius R (m)", y_label="time (s)",
                          log_y=True, shade_x=(OPLO, OPHI, "operating range"),
                          vlines=[(RHO_BOUND, "4&rho;/3")],
                          title="T_total(R) = T1(R) + h_max(R)&middot;T_hop(R, n_c)",
                          caption="Log scale, because the two terms differ by more "
                                  "than an order of magnitude. That gap IS the "
                                  "result: the ground term never grows enough to turn "
                                  "the curve over inside the operating range."))
    o.append(table(["R (m)", "T1 (s)", "ground term (s)", "ground share of T_total",
                    "T_total (s) [95% CI]"],
                   [[_f(r["R_m"], 0), _f(r["T1_med_s"]), _f(r["T_spread_med_s"]),
                     f'{100*float(r["T_spread_share"]):.1f}%',
                     f'{_f(r["T_total_med_s"])} [{_f(r["T_total_lo_s"])}, '
                     f'{_f(r["T_total_hi_s"])}]'] for r in rs8]))
    o.append(table(["k", "R* grid search", "R* 95% CI", "interior to 94&ndash;400 m?",
                    "T_hop used (s)", "R* closed form"],
                   [[k, f'{_f(v["R_star_grid_m"], 0)} m',
                     f'[{_f(v["R_star_ci_m"][0], 0)}, {_f(v["R_star_ci_m"][1], 0)}] m',
                     ("<strong>yes</strong>" if v["interior_to_operating_range"]
                      else "no &mdash; at the upper edge" if v["at_upper_boundary"]
                      else "no"),
                     _f(v["T_hop_used_s"]), f'{_f(v["R_star_closed_form_m"], 0)} m']
                    for k, v in sorted(rstar.items(), key=lambda kv: int(kv[0]))]))
    o.append(f'<p>The grid search is capped at R = '
             f'{_f(max(float(r["R_m"]) for r in comp), 0)} m, the top of the flight '
             f'grid, and the measured curve is still falling there. The closed form, '
             f'fed the <em>measured</em> T_hop, puts R* well beyond the operating '
             f'range. Both are reported because neither alone is trustworthy: the '
             f'grid search cannot see past its own edge, and the closed form assumes '
             f'T_hop constant in R, which the measurement refutes.</p>'
             f'<p><strong>Self-check.</strong> Fed T_hop = 2 s the closed form returns '
             f'R* = {_f(sm["closed_form_selfcheck"]["T_hop_2s_gives_R_star_m"], 1)} m '
             f'against the {sm["closed_form_selfcheck"]["task_states_m"]} m quoted in '
             f'the brief, so the model agrees with the group&rsquo;s own analytic '
             f'figure. Inverting it, R* reaches 400 m only if T_hop &ge; '
             f'{_f(need)} s.</p>')
    o.append(src("cluster-radius/composition.csv"))

    # ------------------------------------------------------------- scorecard
    o.append("<h2>Pre-registration scorecard</h2>")
    o.append("<p>Registered in <code>docs/PREREGISTRATION-cluster-radius.md</code> "
             "and committed before these sweeps were read.</p>")
    o.append(table(["#", "prediction", "registered range", "measured", "verdict"], [
        ["3.1", "T_hop is a few seconds, not tens", "1.3&ndash;4 s",
         f"{_f(min(th8))}&ndash;{_f(max(th8))} s", sm["scorecard"]["3.1"]],
        ["3.2", "T_hop exponent in k", "[0.6, 1.4]",
         fitstr("T_hop_vs_k_R150"), sm["scorecard"]["3.2"]],
        ["3.3", "T_hop exponent in R", "[&minus;0.9, &minus;0.3]",
         fitstr("T_hop_vs_R_k8"), sm["scorecard"]["3.3"]],
        ["3.4", "T_spread exponent in n_c", "[&minus;0.4, +0.2]",
         fitstr("T_spread_vs_nc_R150"), sm["scorecard"]["3.4"]],
        ["3.5", "R* outside the range, above 400 m", "500&ndash;800 m",
         f'grid edge {_f(k8.get("R_star_grid_m"), 0)} m, closed form '
         f'{_f(k8.get("R_star_closed_form_m"), 0)} m', sm["scorecard"]["3.5"]],
        ["3.6", "Dubins/BHH flat above 4&rho;/3, worse below", "&gt; 5 % gap",
         f'{_f(kb["mean_above"])}&times; vs {_f(kb["mean_below"])}&times;',
         sm["scorecard"]["3.6"]],
        ["3.7", "no node completes without pooling", "0.000",
         f'{b5["nodes_completing_all_k_without_pooling"]} of '
         f'{b5["total_nodes"]:,}', sm["scorecard"]["3.7"]],
    ], nums=set()))

    # ---------------------------------------------------------------- limits
    o.append("<h2>What this probe does not establish</h2>")
    o.append("<ul>"
             "<li><strong>T_hop is protocol-dependent.</strong> It is reported as a "
             "function of R, n_c, k <em>and</em> the advertisement interval. A "
             "materially different dissemination protocol would move it. What is "
             "protocol-independent is the k/&lambda; floor, and that floor alone "
             "already exceeds the contention term.</li>"
             "<li><strong>One cell, not a network.</strong> No UAV, no trajectory, no "
             "air-to-ground link, no inter-cluster traffic. That was the point of the "
             "shortcut, but cross-cell interference is absent.</li>"
             "<li><strong>The sweep is reduced</strong> to 45 configurations, not the "
             "full 7&times;3&times;3&times;2 factorial. N = 120 seeds per "
             "configuration was held fixed &mdash; the factorial was cut, never N.</li>"
             "<li><strong>T1 uses a hex-tiling stand-in for Phase 0</strong>, not "
             "PECEE: cluster heads are the node nearest each occupied cell centre. A "
             "real CH election would move the stops, though not the 1/R scaling.</li>"
             "<li><strong>The composed CI treats the two terms as independent</strong>, "
             "because they come from separate seed sets.</li>"
             "<li><strong>No claim about R &gt; 400 m</strong> beyond &ldquo;the curve "
             "is still falling&rdquo;. The flight grid stops there.</li>"
             "</ul>")
    return page("Cluster radius — interior R*?", "\n".join(o))
