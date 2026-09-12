"""The HTML reports must be self-contained and must not overstate the data.

brief 9: inline CSS/JS, no CDN, opens from file:// with no network.
brief 13: no 1-1/e claim, no end-to-end guarantee, no 'converges quickly'.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "report"
RES = ROOT / "results"


@pytest.fixture(scope="module")
def reports():
    subprocess.run([sys.executable, "tools/make_report.py", "all"],
                   cwd=ROOT, check=True, capture_output=True)
    return {p.name: p.read_text() for p in REPORT.glob("*.html")}


def test_reports_exist(reports):
    assert "E0.html" in reports and "index.html" in reports


def test_no_external_resources(reports):
    """Self-contained: no network reference of any kind."""
    bad = re.compile(r'(?:src|href)\s*=\s*["\'](?:https?:)?//', re.I)
    for name, h in reports.items():
        assert not bad.search(h), f"{name} references an external resource"
        for token in ("cdn.", "googleapis", "unpkg", "jsdelivr", "cdnjs"):
            assert token not in h, f"{name} mentions {token}"


def test_css_is_inline_and_present(reports):
    for name, h in reports.items():
        assert "<style>" in h and ".chart{" in h, f"{name} lacks inline CSS"


def test_charts_are_inline_svg_not_images(reports):
    for name, h in reports.items():
        assert "<img" not in h, f"{name} uses <img>; charts must be inline SVG"
    assert reports["E0.html"].count("<svg") >= 6


def test_every_chart_links_its_csv(reports):
    """brief 9: every chart is accompanied by the CSV it was plotted from."""
    h = reports["E0.html"]
    n_svg = h.count("<svg")
    n_src = h.count("Plotted from:")
    assert n_src >= 5, f"only {n_src} CSV source lines for {n_svg} charts"
    for csv_name in ("alpha_sweep.csv", "decomposition.csv", "kernel_table.csv",
                     "lnk_fit.csv", "kstar.csv", "theta_tables.csv", "kstar_vs_C.csv"):
        assert f"../results/E0/{csv_name}" in h, f"{csv_name} not linked"
        assert (RES / "E0" / csv_name).exists(), f"{csv_name} linked but missing"


def test_trust_banner_present(reports):
    for name, h in reports.items():
        assert re.search(r'class="banner (CURRENT|STALE|VOID)"', h), name


def test_header_block_carries_provenance(reports):
    for name, h in reports.items():
        for field in ("git SHA", "generated", "N seeds", "config sha256"):
            assert field in h, f"{name} header missing {field}"


# ---- anti-pattern scan (brief 13) ---------------------------------------
FORBIDDEN = [
    (r"1\s*[-−]\s*1/e", "the (1-1/e) guarantee is wrong for set cover (brief 3.3)"),
    (r"converges quickly", "report the iteration distribution instead (brief E5)"),
    (r"theoretical guarantee on mission time", "no such guarantee exists (brief 3.4)"),
    (r"guarantee on (?:the )?(?:total |mission )?(?:flight )?time", "brief 3.4"),
]


def test_no_forbidden_claims(reports):
    for name, h in reports.items():
        for pat, why in FORBIDDEN:
            assert not re.search(pat, h, re.I), f"{name}: {why}"


def test_e0_does_not_claim_measured_r_or_f(reports):
    """r(k)/f(k) are assumed families in E0. The report must say so."""
    h = reports["E0.html"]
    assert "unmeasured" in h.lower() or "not data" in h.lower()
    assert "What E0 does not establish" in h


# ---- numbers in the report must come from the committed artifacts --------
def test_headline_numbers_match_verdict_json(reports):
    v = json.loads((RES / "E0" / "verdict.json").read_text())
    h = reports["E0.html"]
    assert f'GATE: {v["gate"]}' in h
    prop = v["per_policy"]["m-of-k/proportional-50"]
    assert f'{prop["frac_interior"]*100:.1f}%' in h
    assert f'>{prop["median_k_star"]}</td>' in h, \
        "median k* for the proportional policy is not rendered in any table cell"
    for f in v["feasibility_passes_per_ch"]:
        assert f'{f["passes_per_ch"]:.2f}' in h


def test_reported_passes_reproduce_the_brief_table(reports):
    """5.9 / 1.3 / 0.8 of brief 3.2 must appear, rounded as the brief rounds."""
    h = reports["E0.html"]
    assert "5.92" in h and "1.34" in h and "0.79" in h


def test_index_lists_the_whole_work_queue(reports):
    h = reports["index.html"]
    for eid in [f"E{i}" for i in range(11)]:
        assert f">{eid}<" in h or f'>{eid}</a>' in h, f"{eid} missing from dashboard"


def test_index_names_blocked_items_and_why(reports):
    h = reports["index.html"]
    assert "BLOCKED" in h
    assert "PECEE" in h and "ns-3" in h and "LKH" in h


# ---- cluster-radius probe page -------------------------------------------
CR_PAGE = "cluster-radius.html"


def _cr(reports):
    if CR_PAGE not in reports:
        pytest.skip("cluster-radius page not built (probe data absent)")
    return reports[CR_PAGE]


def test_cluster_radius_links_its_csvs(reports):
    h = _cr(reports)
    for name in ("cluster-radius/b4_by_config.csv", "cluster-radius/a6_by_config.csv",
                 "cluster-radius/composition.csv"):
        assert f"../results/{name}" in h, f"{name} not linked"
        assert (RES / name).exists(), f"{name} linked but missing"


def test_cluster_radius_declares_the_reduced_sweep(reports):
    """The sweep was cut from the full factorial; the page must say so, and must
    say N was not cut."""
    h = _cr(reports)
    assert "45 configurations" in h
    assert "never N" in h


def test_cluster_radius_reports_the_refuted_prediction(reports):
    """A failed prediction of mine must be stated, not quietly dropped."""
    h = _cr(reports)
    assert "REFUTED" in h
    assert "Pre-registration scorecard" in h
    assert "PREREGISTRATION-cluster-radius.md" in h


def test_cluster_radius_does_not_claim_T_hop_is_constant(reports):
    """The closed form assumes it; the measurement refutes it. The page must not
    assert constancy anywhere."""
    h = _cr(reports)
    assert "T_hop constant" not in h or "assumes T_hop constant" in h
    assert re.search(r"approximation, not a law", h)


def test_cluster_radius_states_protocol_dependence(reports):
    h = _cr(reports)
    assert "protocol parameter, not a channel property" in h


def test_cluster_radius_banner_matches_completeness(reports):
    """STALE exactly when an arm is missing; CURRENT only when all are present."""
    import json
    sm = json.loads((RES / "cluster-radius" / "summary.json").read_text())
    gaps = bool(sm.get("incomplete_configs")) or sm["B5"]["verdict"] == "NOT RUN"
    h = _cr(reports)
    expect = "STALE" if gaps else "CURRENT"
    assert f'class="banner {expect}"' in h, f"banner should be {expect}"


def test_cluster_radius_lists_its_limits(reports):
    h = _cr(reports)
    assert "What this probe does not establish" in h
    for token in ("protocol-dependent", "One cell, not a network", "PECEE"):
        assert token in h
