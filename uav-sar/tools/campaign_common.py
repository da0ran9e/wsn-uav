"""Shared, dependency-free helpers for the uav-sar campaign scripts.

Every campaign_*.py script imports from here so that the two things every
script got wrong are fixed in exactly one place:

  * S9  -- the victim position was reconstructed from a HARD-CODED 20 m grid
           spacing, so delivery error was ~11x wrong at any other
           --gridSpacing.  `victim_pos()` now resolves the spacing from the
           data, and says so loudly on stderr when it cannot.
  * S15 -- the 90th percentile was `xs[int(0.9*n)-1]`, which is off by one
           whenever n is not a multiple of 10.  `p90()` uses nearest-rank.

See tools/README.md for the metric definitions and for which metric is
retracted (S8).
"""
import math
import os
import sys

LEGACY_SPACING = 20.0  # the value that used to be hard-coded everywhere

_warned = set()


def _warn_once(key, msg):
    if key not in _warned:
        _warned.add(key)
        print("WARNING: " + msg, file=sys.stderr)


def _col(row, name):
    """Value of a metrics.csv column, or None if the column is absent/empty."""
    v = row.get(name)
    return None if v is None or v == "" else v


def grid_spacing(m, fallback=None):
    """Grid spacing in metres for one run, given its metrics.csv row (a dict).

    S9 resolution order:
      1. the `gridSpacing` column, once the C++ side emits it;
      2. `fallback`, when the caller itself set --gridSpacing for this run
         (sweep scripts know the value they asked for);
      3. the legacy 20.0 m constant -- warns on stderr, because this silently
         produced an ~11x error in every previously published sweep.
    """
    v = _col(m, "gridSpacing")
    if v is not None:
        return float(v)
    if fallback is not None:
        return float(fallback)
    _warn_once(
        "spacing",
        "metrics.csv has no 'gridSpacing' column; assuming %.1f m (S9). "
        "Delivery/leader errors are WRONG if the run used a different "
        "--gridSpacing. Rebuild the binary so it emits gridSpacing."
        % LEGACY_SPACING,
    )
    return LEGACY_SPACING


def victim_pos(m, fallback_spacing=None):
    """True victim (target ground node) position for one run.  S9.

    Prefers the authoritative `victimX`/`victimY` columns; otherwise
    reconstructs the lattice position from targetNodeId and whatever spacing
    `grid_spacing()` can establish.

    The reconstruction assumes node ids are laid out row-major after the BS
    (id 0) and the UAVs (ids 1..numUav) -- true for the lattice deployment,
    and the reason victimX/victimY exist: it will NOT survive W7's move to
    random deployment.
    """
    vx, vy = _col(m, "victimX"), _col(m, "victimY")
    if vx is not None and vy is not None:
        return float(vx), float(vy)
    tid = int(m["targetNodeId"])
    grid = int(m["gridSize"])
    nuav = int(m["numUav"])
    sp = grid_spacing(m, fallback_spacing)
    k = tid - (1 + nuav)
    return (k % grid) * sp, (k // grid) * sp


def build_id(run_dir):
    """The binary's build stamp for one run, from config.txt (or None)."""
    try:
        for line in open(os.path.join(run_dir, "config.txt")):
            if line.startswith("build="):
                return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return None


def assert_one_build(run_dirs, label=""):
    """Refuse to aggregate runs produced by different binaries.

    Audit meta-finding: rebuilding while a campaign was in flight silently mixed
    two binaries inside one result set, and it was caught only because the
    timing happened to be noticed. A campaign that spans builds is not a
    campaign, so this raises rather than warns.
    """
    seen = {}
    for d in run_dirs:
        b = build_id(d)
        if b is not None:
            seen.setdefault(b, []).append(d)
    if len(seen) > 1:
        lines = "\n".join(f"    {b}: {len(v)} runs (e.g. {v[0]})"
                          for b, v in sorted(seen.items()))
        raise SystemExit(
            f"REFUSING to aggregate {label or 'these runs'}: they span "
            f"{len(seen)} different binaries.\n{lines}\n"
            "  Delete the output directory and re-run the whole campaign on one build."
        )
    return next(iter(seen), None)


def nearest_rank(xs, q):
    """Nearest-rank quantile: the smallest value at or above fraction q.

    S15: every script used `xs[int(q*n)-1]`, which floors instead of ceiling
    and is therefore one position low whenever q*n is not an integer.
    n=15, q=0.9: int(13.5)-1 = index 12 (13th value); correct is
    ceil(13.5)-1 = index 13 (14th value).
    """
    if not xs:
        return float("nan")
    s = sorted(xs)
    return s[min(len(s) - 1, max(0, math.ceil(q * len(s)) - 1))]


def p90(xs):
    """90th percentile, nearest-rank.  S15."""
    return nearest_rank(xs, 0.90)


def iqr(xs):
    """(p25, p75, p75-p25), nearest-rank -- same convention as p90."""
    if not xs:
        return float("nan"), float("nan"), float("nan")
    lo, hi = nearest_rank(xs, 0.25), nearest_rank(xs, 0.75)
    return lo, hi, hi - lo
