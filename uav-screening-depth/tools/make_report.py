#!/usr/bin/env python3.10
"""Generate the self-contained HTML reports (AGENT-BRIEF 9).

  make_report.py E0      -> report/E0.html
  make_report.py index   -> report/index.html
  make_report.py all     -> everything available

Self-contained: CSS and SVG are inline, no CDN, no network. Opens from file://.
Every chart links the CSV it was plotted from, and every CSV is committed.
"""
from __future__ import annotations

import csv
import html
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

import provenance  # noqa: E402
import svgplot as S  # noqa: E402

REPORT = ROOT / "report"
RES = ROOT / "results"

# Work-queue state. Maintained by hand alongside STATUS.md; the dashboard
# renders it. "blocked" carries the reason.
QUEUE = [
    ("E0", "Numerical feasibility of k* (GO/NO-GO gate)", "done",
     "GO, conditional -- see E0 report"),
    ("E1", "Scenario generator (non-convex region, heterogeneity h)", "todo",
     "needs shapely"),
    ("E2", "Phase 0 via PECEE", "blocked", "PECEE not present in this environment"),
    ("E3", "Channel measurement in ns-3", "blocked", "no ns-3 tree in this environment"),
    ("E4", "Discretisation + submodular greedy dose cover", "todo",
     "unblocked: pure Python; needs E1/E2 geometry or a synthetic stand-in"),
    ("E5", "Dubins tour + iterative refinement", "blocked",
     "LKH absent; heading sampling/Noon-Bean can be written first"),
    ("E6", "Baselines (incl. zeng-sca, tuned lawnmower)", "todo", "after E4/E5"),
    ("E7", "Validate theta against packet-level simulation", "blocked", "no ns-3"),
    ("E8", "T_total(k) sweep -> Figure H1", "todo", "after E5/E6"),
    ("E9", "k* vs ln C -> Figure H2", "todo", "E0 carries a preview only"),
    ("E10", "Sensitivity -> Figures H4, H5", "todo", "after E6"),
]


def read_csv(p: Path) -> list[dict]:
    with open(p, newline="") as fh:
        return list(csv.DictReader(fh))


def page(title: str, body: str) -> str:
    return (f"<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
            f"<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<title>{html.escape(title)}</title><style>{S.CSS}</style></head>"
            f"<body><div class=\"wrap\">{body}</div></body></html>\n")


def header(exp: str, subtitle: str, *, banner: str, n_seeds: str,
           extra: dict | None = None) -> str:
    st = provenance.stamp(ROOT / "config" / "default.yaml")
    meta = {
        "git SHA": st["git_commit"][:12] + (" (dirty)" if st["git_dirty"] else ""),
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"),
        "N seeds": n_seeds,
        "config sha256": st["config_sha256"][:16],
        "source sha256": st["source_sha256"][:16],
        "python": st["python_version"],
        **(extra or {}),
    }
    cells = "".join(f"<div>{html.escape(k)}<b>{html.escape(str(v))}</b></div>"
                    for k, v in meta.items())
    return (f'<h1>{html.escape(exp)}</h1><p class="sub">{subtitle}</p>'
            f'<div class="card"><span class="banner {banner}">{banner}</span>'
            f'<div class="meta">{cells}</div></div>')


def table(cols: list[str], rows: list[list], *, nums: set[int] | None = None) -> str:
    nums = nums or set(range(1, len(cols)))
    th = "".join(f'<th class="{"num" if i in nums else ""}">{html.escape(c)}</th>'
                 for i, c in enumerate(cols))
    tr = []
    for r in rows:
        tds = "".join(f'<td class="{"num" if i in nums else ""}">{c}</td>'
                      for i, c in enumerate(r))
        tr.append(f"<tr>{tds}</tr>")
    return (f'<div class="tw"><table><thead><tr>{th}</tr></thead>'
            f'<tbody>{"".join(tr)}</tbody></table></div>')


def src(*paths: str) -> str:
    links = " &middot; ".join(f'<a href="../results/{p}">{p}</a>' for p in paths)
    return f'<p class="src">Plotted from: {links}</p>'


# ==========================================================================
# E0
# ==========================================================================

def build_e0() -> str:
    v = json.loads((RES / "E0" / "verdict.json").read_text())
    alpha = read_csv(RES / "E0" / "alpha_sweep.csv")
    decomp = read_csv(RES / "E0" / "decomposition.csv")
    kern = read_csv(RES / "E0" / "kernel_table.csv")
    tt = read_csv(RES / "E0" / "theta_tables.csv")
    lnk = read_csv(RES / "E0" / "lnk_fit.csv")
    kvc = read_csv(RES / "E0" / "kstar_vs_C.csv")
    gr, qc = v["gate_reasoning"], v["quasiconvexity"]
    pol, reg = v["per_policy"], v["per_regime"]

    o = [header("E0 &mdash; Numerical feasibility of k*",
                "GO / NO-GO gate. Does T_total(k) have an interior minimum at all? "
                "Direct numerical evaluation, no simulator.",
                banner="CURRENT",
                n_seeds="n/a &mdash; deterministic",
                extra={"config points": f"{v['n_config_points']:,}",
                       "k grid": f"{v['k_grid'][0]}..{v['k_grid'][1]}",
                       "wall time": f"{v['wall_s']}s"})]

    # ---- verdict -----------------------------------------------------------
    o.append(f'''<div class="card verdict"><p class="big">GATE: {v["gate"]}</p>
<p>The brief's stop condition &mdash; <em>k* on a boundary for more than half the
grid in <strong>both</strong> regimes</em> &mdash; is <strong>not met</strong>
({gr["frac_boundary_all_k"]*100:.1f}% boundary in all-k,
{gr["frac_boundary_m_of_k_aggregate"]*100:.1f}% in the m-of-k aggregate), so E1 is
unblocked. But the headline per-regime numbers are close to the threshold and
they <strong>average over structurally different cases</strong>. The conditional
verdict is what matters:</p>
<ul>
<li><strong>The premise holds under Regime B with m proportional to k</strong>:
{pol["m-of-k/proportional-50"]["frac_interior"]*100:.1f}% of the grid has an
interior k*, median k* = {pol["m-of-k/proportional-50"]["median_k_star"]}.</li>
<li><strong>It fails outright with m held fixed</strong>:
{pol["m-of-k/fixed-3"]["frac_interior"]*100:.0f}% interior &mdash; k* = 40 on
<em>every single one</em> of the {pol["m-of-k/fixed-3"]["n_config_points"]:,} grid
points, because &theta; is flat in k so extra files are free. <em>There is no
optimum to find.</em></li>
<li><strong>It is vacuous in Regime A</strong>: interior for
{pol["all-k/equal-k"]["frac_interior"]*100:.1f}% of the grid, but median k* =
{pol["all-k/equal-k"]["median_k_star"]} with
{pol["all-k/equal-k"]["frac_at_lower"]*100:.1f}% pinned at the k=2 floor, and the
median interior optimum beats the boundary by only 0.2% &mdash; below the 1%
meaningfulness bar. "How large should k be?" answers "as small as possible".</li>
</ul>
<p>So the paper's question is well posed <strong>only</strong> in Regime B with
m &prop; k. Section&nbsp;2 below shows that is not a free modelling choice: the
Appendix&nbsp;A.2 evidence model <em>forces</em> it.</p></div>''')

    # ---- acceptance 1: interior fractions ---------------------------------
    o.append("<h2>Acceptance 1 &mdash; fraction of the grid with an interior k*</h2>")
    o.append("<p>Reported per regime exactly as the brief asks, and then per "
             "m-policy, which is where the structure lives.</p>")
    o.append(table(
        ["regime (as the brief defines it)", "config points", "interior",
         "interior &amp; meaningful (&ge;1% depth)", "on a boundary"],
        [[k, f"{d['n_config_points']:,}", f"{d['frac_interior']*100:.1f}%",
          f"{d['frac_interior_meaningful']*100:.1f}%", f"{d['frac_boundary']*100:.1f}%"]
         for k, d in reg.items()]))
    o.append(table(
        ["m-policy", "config points", "interior", "interior &amp; meaningful",
         "at k=2 floor", "at k=40 ceiling", "median k*", "k* range"],
        [[k, f"{d['n_config_points']:,}", f"{d['frac_interior']*100:.1f}%",
          f"{d['frac_interior_meaningful']*100:.1f}%",
          f"{d['frac_at_lower']*100:.1f}%", f"{d['frac_at_upper']*100:.1f}%",
          d["median_k_star"], f"{d['min_k_star']}&ndash;{d['max_k_star']}"]
         for k, d in pol.items()]))
    o.append(src("E0/kstar.csv"))

    # ---- decomposition chart ---------------------------------------------
    o.append("<h3>Where the shape comes from</h3>")
    names = ["all-k (m=k)", "m-of-k, m fixed = 3", "m-of-k, m = ceil(0.5k)"]
    ser = []
    for nm in names:
        sub = [r for r in decomp if r["series"] == nm]
        ks = [int(r["k"]) for r in sub]
        ser.append({"name": nm, "x": ks,
                    "y": [float(r["T_total_s"]) for r in sub],
                    "marker_at": next(int(r["k"]) for r in sub if r["is_kstar"] == "1")})
    o.append(S.line_chart(ser, x_label="k (signature set size, files)",
                          y_label="T_total (s)", log_y=True,
                          title="T_total(k) under the three m-policies, one reference config",
                          caption="Dot marks k*. Same r(k), f(k), R=100 m, T_miss=10 sweeps "
                                  "throughout, so the only difference is how m is chosen. "
                                  "Fixed m falls monotonically to the k=40 ceiling; all-k "
                                  "rises almost immediately; only m&prop;k turns over."))
    sub = [r for r in decomp if r["series"] == "m-of-k, m = ceil(0.5k)"]
    ks = [int(r["k"]) for r in sub]
    o.append(S.line_chart(
        [{"name": "T1 (dissemination)", "x": ks, "y": [float(r["T1_s"]) for r in sub]},
         {"name": "r(k)&middot;T2 (verification)", "x": ks,
          "y": [float(r["r_times_T2_s"]) for r in sub]},
         {"name": "(1-r(k))&middot;T_miss", "x": ks,
          "y": [float(r["one_minus_r_times_Tmiss_s"]) for r in sub]},
         {"name": "T_total", "x": ks, "y": [float(r["T_total_s"]) for r in sub],
          "color": "#111827",
          "marker_at": next(int(r["k"]) for r in sub if r["is_kstar"] == "1")}],
        x_label="k", y_label="time (s)",
        title="The three terms of T_total(k), m = ceil(0.5k)",
        caption="The interior optimum is the crossing of a rising T1 against a falling "
                "miss cost. The verification term r&middot;T2 is small here, so the "
                "trade-off the paper describes is really T1 against the miss penalty, "
                "not T1 against verification."))
    o.append(src("E0/decomposition.csv"))

    # ---- acceptance 2: feasibility ---------------------------------------
    o.append("<h2>Acceptance 2 &mdash; feasibility at the default operating point</h2>")
    o.append("<p>&lambda; = 5 opportunities/s (the LR-WPAN ceiling), p = 0.3, "
             "broadcast radius 50 m, v = 20 m/s. One straight pass over a CH spends "
             "2R/v = 5 s in range, delivering 25 opportunities.</p>")
    o.append(table(["requirement", "&theta; (opportunities)", "in-range time needed (s)",
                    "passes over each CH"],
                   [[f["requirement"], f'{f["theta_ops"]:.1f}',
                     f'{f["in_range_s_needed"]:.1f}', f'<strong>{f["passes_per_ch"]:.2f}</strong>']
                    for f in v["feasibility_passes_per_ch"]]))
    o.append(S.bar_chart(
        [f["requirement"] for f in v["feasibility_passes_per_ch"]],
        [{"name": "passes per CH required", "y": [f["passes_per_ch"]
                                                  for f in v["feasibility_passes_per_ch"]]},
         {"name": "1 pass (what a single sweep gives)",
          "y": [1.0] * len(v["feasibility_passes_per_ch"]), "color": "#9ca3af"}],
        y_label="passes over each CH", title="Dose feasibility, k = 10",
        caption="Regime A needs the UAV over every cluster ~5.9 times. Reproduces the "
                "brief's 5.9 / 1.3 / 0.8 exactly."))
    o.append(f'''<div class="card flag"><p><strong>Regime A is operationally
marginal, and that is a finding, not a detail.</strong> Requiring all k files at
every CH costs 5.92 passes per cluster at k=10 &mdash; six full area sweeps. At
the k* that Regime A actually selects (median k* =
{pol["all-k/equal-k"]["median_k_star"]}) the demand falls to about 1.4 passes,
which is feasible; but that is the same thing as saying Regime A is only feasible
where k is too small for the screening question to be interesting. The paper must
say this rather than assume all-k quietly.</p></div>''')
    o.append(src("E0/theta_tables.csv"))

    # ---- acceptance 3: ln k ----------------------------------------------
    o.append("<h2>Acceptance 3 &mdash; does the ln k factor survive Regime B?</h2>")
    lk = v["ln_k_survival"]
    o.append(f'''<p><strong>No.</strong> It exists only in Regime A, exactly as the
brief predicts. In Regime A &theta; grows
{lk["all-k"]["ratio_k40_over_k4"]}&times; from k=4 to k=40
({lk["all-k"]["theta_k4"]} &rarr; {lk["all-k"]["theta_k40"]} opportunities). With
m held fixed at 3, &theta; <em>falls</em>
({lk["m-of-k fixed m=3"]["theta_k4"]} &rarr;
{lk["m-of-k fixed m=3"]["theta_k40"]}, a factor
{lk["m-of-k fixed m=3"]["ratio_k40_over_k4"]}).</p>''')
    series = []
    for name in ("all-k", "m-of-k fixed m=2", "m-of-k fixed m=3", "m-of-k fixed m=5",
                 "m-of-k proportional-30", "m-of-k proportional-50"):
        sub = [r for r in lnk if r["series"] == name]
        if sub:
            series.append({"name": name, "x": [int(r["k"]) for r in sub],
                           "y": [float(r["theta_ops"]) for r in sub]})
    o.append(S.line_chart(series, x_label="k", y_label="&theta; (opportunities)",
                          log_y=True, title="&theta;(k) by regime and m-policy",
                          caption="Regime A rises ~k ln k. Fixed-m curves are flat to "
                                  "falling. Proportional-m rises, with the visible "
                                  "parity sawtooth discussed below."))
    o.append(table(
        ["k", "&theta;_A (all-k)", "&theta;_A / k", "&theta; m=2", "&theta; m=3", "&theta; m=5"],
        [[k] + [next((f'{float(r["theta_ops"]):.1f}' for r in lnk
                      if r["series"] == s and int(r["k"]) == k), "&ndash;")
                for s in ("all-k",)]
         + [next((f'{float(r["theta_over_k"]):.2f}' for r in lnk
                  if r["series"] == "all-k" and int(r["k"]) == k), "&ndash;")]
         + [next((f'{float(r["theta_ops"]):.1f}' for r in lnk
                  if r["series"] == f"m-of-k fixed m={m}" and int(r["k"]) == k), "&ndash;")
            for m in (2, 3, 5)]
         for k in (4, 6, 10, 16, 25, 40)]))
    o.append(f'''<div class="card flag"><p><strong>And the ln k factor is mild even
where it exists.</strong> At C_conf = 0.95 the closed form is
&theta;_A &asymp; k&middot;[ln k + 2.97] / |ln(1&minus;p)|, and ln k only spans
0.69&ndash;3.69 over k = 2&hellip;40, so the constant dominates. Per-file cost
&theta;_A/k grows just
{lk["all-k"]["per_file_growth_k4_to_k40"]}&times; from k=4 to k=40 while the linear
factor contributes 10&times;. "&theta;_A grows like k ln k" must not be read in
the paper as "&theta;_A is driven by ln k".</p></div>''')
    o.append(src("E0/lnk_fit.csv", "E0/theta_tables.csv"))

    # ---- m is not a free choice ------------------------------------------
    o.append("<h2>Which m-policy is physically real?</h2>")
    o.append('''<p>The whole verdict turns on this, so it cannot be left as a
modelling preference. Appendix&nbsp;A.2 fixes the fragment evidence model:
<code>evidence_i = 1 &minus; (1&minus;0.90)^(pixelCount_i/totalPixels)</code>,
pixel-stride interleaved. With k files partitioning one payload each fragment
carries pixel fraction 1/k, so noisy-OR over m received fragments gives</p>
<p style="text-align:center"><code>C = 1 &minus; (1&minus;0.90)^(m/k)</code></p>
<p>&mdash; a function of the <em>ratio</em> m/k alone. Inverting for a screening
threshold thr gives <code>&alpha; = m/k = ln(1&minus;thr)/ln(0.10)</code>. Because
each fragment's evidence <em>shrinks</em> as k grows, m must grow in proportion to
k to hold confidence fixed. <strong>m is therefore not a free knob and it is not
constant: the proportional policy is the one the group's own ICCE evidence model
implies, with &alpha; set by the screening threshold.</strong> The fixed-m policy,
which destroys the optimum, corresponds to no threshold at all.</p>
<p>This derivation is <em>not</em> in the brief &mdash; it is assumption A1 in
<code>docs/AUDIT-E0.md</code> and needs review.</p>''')
    thr = [float(a["suspicion_threshold"]) for a in alpha]
    o.append(S.line_chart(
        [{"name": "interior k* exists", "x": thr,
          "y": [float(a["frac_interior"]) * 100 for a in alpha]},
         {"name": "interior &amp; meaningful (&ge;1% depth)", "x": thr,
          "y": [float(a["frac_interior_meaningful"]) * 100 for a in alpha]},
         {"name": "quasiconvex, continuous m", "x": thr,
          "y": [float(a["frac_quasiconvex_continuous_m"]) * 100 for a in alpha]},
         {"name": "quasiconvex, integer m", "x": thr,
          "y": [float(a["frac_quasiconvex"]) * 100 for a in alpha], "dashed": True}],
        x_label="suspicion threshold thr  (&alpha; = m/k is derived from it)",
        y_label="% of the r &times; f &times; R &times; T_miss grid", y_min=0,
        title="Does an interior k* exist, as a function of the screening threshold?",
        caption="1,620 config points per threshold. An interior k* exists for "
                "86-99.6% of the grid across thr = 0.30-0.80 (&alpha; = 0.16-0.70). "
                "It collapses at thr &rarr; 0.90, where &alpha; &rarr; 1 and the "
                "regime degenerates into all-k."))
    o.append(table(
        ["thr", "&alpha; = m/k", "interior", "interior &amp; meaningful",
         "median k*", "median depth", "qcvx (integer m)", "qcvx (continuous m)",
         "median violation", "passes/CH at k*"],
        [[f'{a["suspicion_threshold"]:.3f}', f'{a["alpha_m_over_k"]:.3f}',
          f'{a["frac_interior"]*100:.1f}%', f'{a["frac_interior_meaningful"]*100:.1f}%',
          f'<strong>{a["median_k_star"]}</strong>', f'{a["median_rel_depth"]*100:.1f}%',
          f'{a["frac_quasiconvex_integer_m"]*100:.0f}%',
          f'{a["frac_quasiconvex_continuous_m"]*100:.1f}%',
          f'{a["median_max_violation_rel"]*100:.1f}%',
          f'{a["median_passes_at_kstar"]:.2f}']
         for a in v["alpha_view"]]))
    o.append('<p>k* falls monotonically 32 &rarr; 3 as the threshold rises, which is '
             'the sign of a genuine, tunable interior optimum rather than a numerical '
             'accident. The last row (thr = 0.90, &alpha; = 1) <em>is</em> Regime A and '
             'reproduces its 50.6% / median k* = 3 exactly &mdash; a consistency check '
             'on two independently coded paths.</p>')
    o.append(src("E0/alpha_sweep.csv"))

    # ---- quasiconvexity --------------------------------------------------
    o.append("<h2>The quasiconvexity claim &mdash; it does not hold as stated</h2>")
    o.append(f'''<div class="card flag"><p>The paper's central structural claim is
that T_total(k) is quasiconvex in k, so a unique interior optimum exists. Measured:</p>
<div class="kv">
<div><div class="l">quasiconvex, integer m, m=&lceil;&alpha;k&rceil;</div>
<div class="v">0%</div></div>
<div><div class="l">quasiconvex, continuous m = &alpha;k</div>
<div class="v">{qc["frac_quasiconvex_continuous_m_range"][0]*100:.1f}&ndash;{qc["frac_quasiconvex_continuous_m_range"][1]*100:.1f}%</div></div>
<div><div class="l">median violation size, integer m</div>
<div class="v">{qc["median_violation_magnitude_range_integer_m"][0]*100:.1f}&ndash;{qc["median_violation_magnitude_range_integer_m"][1]*100:.1f}%</div></div>
</div>
<p><strong>Mechanism, measured not assumed.</strong> Under m = &lceil;&alpha;k&rceil;
the <em>realised</em> ratio m/k oscillates with the parity of k &mdash; at
&alpha;=0.5, k=3 gives m/k = 0.67 but k=4 gives 0.50 &mdash; so &theta; zigzags
(+7.7 / &minus;1.4 opportunities alternating) and T_total alternates by 1&ndash;15%.
Replacing &lceil;&alpha;k&rceil; with real-valued m = &alpha;k removes the
oscillation entirely at every &alpha; tested, and quasiconvexity is then recovered
in {qc["frac_quasiconvex_continuous_m_range"][1]*100:.1f}% of cases.</p>
<p><strong>So: the objective is quasiconvex; the realisable curve is not.</strong>
m is physically an integer, so this is not an artifact to be waved away. The paper
must either state the claim as quasiconvexity <em>in trend</em> and report the
sawtooth, or promote m to a second decision variable and optimise over (k, m)
jointly. Asserting a unique interior optimum of the realised curve would be
false.</p></div>''')
    sub_i = [r for r in decomp if r["series"] == "m-of-k, m = ceil(0.5k)"]
    sub_c = [r for r in decomp if r["series"] == "m-of-k, m = 0.5k continuous"]
    o.append(S.line_chart(
        [{"name": "integer m = ceil(0.5k)", "x": [int(r["k"]) for r in sub_i],
          "y": [float(r["theta_ops"]) for r in sub_i]},
         {"name": "continuous m = 0.5k", "x": [int(r["k"]) for r in sub_c],
          "y": [float(r["theta_ops"]) for r in sub_c]}],
        x_label="k", y_label="&theta; (opportunities)",
        title="The integrality sawtooth in &theta;, and what it looks like without it",
        caption="The sawtooth is entirely the ceiling function. This is the whole "
                "reason the strict quasiconvexity test fails."))
    o.append(src("E0/decomposition.csv"))

    # ---- kernel ----------------------------------------------------------
    o.append("<h2>The dose kernel (brief &sect;3.1), reproduced</h2>")
    o.append(table(["p", "&kappa; = p (linearised)", "&kappa; = |ln(1&minus;p)| (correct)",
                    "understatement"],
                   [[r["p"], f'{float(r["kernel_linear"]):.3f}',
                     f'{float(r["kernel_log"]):.3f}',
                     f'{float(r["relative_error"])*100:+.1f}%'] for r in kern]))
    o.append(S.bar_chart([r["p"] for r in kern],
                         [{"name": "understatement of the linearised kernel (%)",
                           "y": [float(r["relative_error"]) * 100 for r in kern],
                           "color": "#dc2626"}],
                         y_label="% understated", title="Error from using &int;p dt",
                         value_fmt="{:.0f}",
                         caption="Worst exactly where p is largest, i.e. closest to the "
                                 "UAV. The campaign uses &kappa; = &minus;ln(1&minus;p) "
                                 "everywhere; --kernel=linear exists only as an ablation."))
    o.append(src("E0/kernel_table.csv"))

    # ---- k* vs ln C preview ---------------------------------------------
    o.append("<h2>Preview only &mdash; k* against ln C</h2>")
    o.append("<p>E9 is the real measurement. This is the same model evaluated at fixed "
             "R = 100 m with the area varied so C spans 10&ndash;640, and it is shown "
             "because it is cheap, not because it settles anything.</p>")
    want = [("m-of-k", "proportional-50"), ("all-k", "equal-k"), ("m-of-k", "fixed-3")]
    ser = []
    for rg, pl in want:
        by_c: dict[float, list[int]] = {}
        for r in kvc:
            if r["regime"] == rg and r["m_policy"] == pl:
                by_c.setdefault(float(r["ln_C"]), []).append(int(r["k_star"]))
        xs = sorted(by_c)
        ser.append({"name": f"{rg} / {pl}", "x": xs,
                    "y": [sorted(by_c[x])[len(by_c[x]) // 2] for x in xs]})
    o.append(S.line_chart(ser, x_label="ln C  (C = number of clusters)",
                          y_label="median k* over the grid", y_min=0,
                          title="k* vs ln C &mdash; PREVIEW, not a fitted result",
                          caption="No slope, intercept or R^2 is quoted here: that is "
                                  "E9's job with CIs over 120 seeds. Note the fixed-m "
                                  "curve is pinned at 40 independently of C, as expected."))
    o.append(src("E0/kstar_vs_C.csv"))

    # ---- what this does not establish ------------------------------------
    o.append("<h2>What E0 does not establish</h2>")
    o.append('''<ul>
<li><strong>No measurement of r(k) or f(k).</strong> They are parameterised
families spanning plausible shapes, not data. E0 asks whether an optimum can
exist, never where it is. Every k* here is a property of an assumed r/f pair.</li>
<li><strong>T1 and T2 are closed-form stand-ins</strong> (lawnmower length over a
square region; BHH tour plus a per-visit Dubins coefficient). No trajectory is
planned and no Dubins path is flown. E5 replaces both.</li>
<li><strong>No channel model.</strong> p = 0.3 at a reference distance is the
Appendix A.2 constant; there is no p(d). E3 measures it.</li>
<li><strong>No statistics.</strong> Every number is deterministic &mdash; a
function evaluation, not a sample. The brief's N &ge; 120 rule applies from E1 on;
there are no CIs here because there is nothing to be uncertain about except the
assumptions themselves.</li>
<li><strong>No approximation guarantee of any kind</strong>, end-to-end or
step-local (brief &sect;3.3, &sect;3.4).</li>
</ul>''')
    return page("E0 — Numerical feasibility of k*", "\n".join(o))


# ==========================================================================
# index
# ==========================================================================

def build_index() -> str:
    v = json.loads((RES / "E0" / "verdict.json").read_text())
    pol = v["per_policy"]
    o = [header("uav-screening-depth &mdash; campaign dashboard",
                "How large should the signature set k be? Work queue, headline "
                "numbers, and open problems.",
                banner="CURRENT", n_seeds="E0 deterministic; N&ge;120 from E1")]
    o.append(f'''<div class="card verdict"><p><strong>E0 gate: {v["gate"]}</strong>
&mdash; conditional. An interior k* exists robustly only in Regime B with
m&nbsp;&prop;&nbsp;k ({pol["m-of-k/proportional-50"]["frac_interior"]*100:.1f}% of
the grid, median k* = {pol["m-of-k/proportional-50"]["median_k_star"]}); it does
not exist at all with m fixed, and it is cosmetic in Regime A. The quasiconvexity
claim holds for the objective but not for the realisable integer-m curve.
<a href="E0.html">Full E0 report &rarr;</a></p></div>''')

    o.append("<h2>Headline numbers</h2>")
    o.append('<div class="kv">'
             f'<div><div class="l">interior k*, m &prop; k</div><div class="v">'
             f'{pol["m-of-k/proportional-50"]["frac_interior"]*100:.1f}%</div></div>'
             f'<div><div class="l">interior k*, m fixed</div><div class="v">'
             f'{pol["m-of-k/fixed-3"]["frac_interior"]*100:.0f}%</div></div>'
             f'<div><div class="l">median k* (m &prop; k)</div><div class="v">'
             f'{pol["m-of-k/proportional-50"]["median_k_star"]}</div></div>'
             f'<div><div class="l">passes/CH, Regime A, k=10</div><div class="v">5.92</div></div>'
             f'<div><div class="l">quasiconvex, integer m</div><div class="v">0%</div></div>'
             '</div>')

    o.append("<h2>Work queue</h2>")
    lbl = {"done": "done", "todo": "not started", "blocked": "BLOCKED",
           "part": "partial"}
    rows = []
    for eid, desc, st, note in QUEUE:
        link = (f'<a href="{eid}.html">{eid}</a>'
                if (REPORT / f"{eid}.html").exists() else eid)
        rows.append([f'<span class="q {st}"></span>{link}', desc,
                     lbl[st], html.escape(note)])
    o.append(table(["item", "goal", "status", "note"], rows, nums=set()))

    o.append("<h2>Open problems, ranked</h2>")
    o.append('''<ol>
<li><strong>Is m proportional to k, or fixed?</strong> The entire premise depends
on it and the two answers are not close: 95% interior vs 0%. E0 derives
proportionality from the Appendix A.2 evidence model (assumption A1, needs
review). If A1 is wrong and m is in fact fixed, the paper has no question to
ask.</li>
<li><strong>Quasiconvexity fails for integer m.</strong> Either restate the claim
as trend-level and report the 1&ndash;15% sawtooth, or optimise over (k, m)
jointly.</li>
<li><strong>Regime A is operationally marginal</strong> (5.9 passes/CH at k=10).
If the paper needs all-k it must argue feasibility, not assume it.</li>
<li><strong>r(k) and f(k) are entirely unmeasured.</strong> They set where k*
lands. Nothing downstream of E0 is quantitative until they come from data.</li>
<li><strong>Environment:</strong> ns-3, PECEE and LKH are absent here, which
blocks E2, E3, E5 and E7 &mdash; see <code>env.txt</code>.</li>
</ol>''')
    o.append('<p class="src">Source of truth for current state: '
             '<code>STATUS.md</code>. This page is generated by '
             '<code>tools/make_report.py</code>.</p>')
    return page("uav-screening-depth — dashboard", "\n".join(o))


def main(argv: list[str]) -> int:
    REPORT.mkdir(parents=True, exist_ok=True)
    which = argv[1:] or ["all"]
    targets = {"E0": build_e0, "index": build_index}
    todo = list(targets) if which == ["all"] else which
    for t in todo:
        if t not in targets:
            print(f"unknown report {t!r}; known: {list(targets)}")
            return 2
        out = REPORT / f"{t}.html"
        out.write_text(targets[t]())
        print(f"wrote {out.relative_to(ROOT)}  ({out.stat().st_size/1024:.1f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
