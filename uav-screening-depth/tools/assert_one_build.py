"""Refuse to aggregate a result set whose runs carry different provenance
stamps (AGENT-BRIEF 6.5). Wired into every aggregation path.

Usage: assert_one_build.py <csv-with-provenance-columns> [...]
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

KEYS = ("schema_version", "prov_id", "source_sha256", "binary_mtime",
        "binary_size", "config_sha256")


def check(paths: list[Path]) -> int:
    seen: dict[tuple, list[str]] = {}
    for p in paths:
        with open(p, newline="") as fh:
            rows = list(csv.DictReader(fh))
        if not rows:
            print(f"EMPTY   {p}")
            return 2
        present = [k for k in KEYS if k in rows[0]]
        if not present:
            print(f"NO-PROVENANCE  {p}: none of {KEYS} present")
            return 2
        for r in rows:
            seen.setdefault(tuple(r[k] for k in present), []).append(str(p))
    if len(seen) != 1:
        print("MIXED BUILD PROVENANCE -- refusing to aggregate:")
        for stamp_, files in seen.items():
            print(f"  {stamp_}  <- {sorted(set(files))}")
        return 1
    stamp_ = next(iter(seen))
    print(f"ONE BUILD  ok  {dict(zip(present, stamp_))}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(check([Path(a) for a in sys.argv[1:]]))
