"""Exit 0 when two JSON files hold the same structure and every number agrees to |a - b| <= 1e-9 (1 + |b|)
(float round-off), else 1. Used by child-geom-check.sh.
    python3 json_close.py A.json B.json
"""
import json, sys


def close(a, b):
    if isinstance(a, dict):
        return isinstance(b, dict) and a.keys() == b.keys() and all(close(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return isinstance(b, list) and len(a) == len(b) and all(close(x, y) for x, y in zip(a, b))
    if isinstance(a, (int, float)) and not isinstance(a, bool):
        return isinstance(b, (int, float)) and not isinstance(b, bool) and abs(a - b) <= 1e-9 * (1 + abs(b))
    return a == b


sys.exit(0 if close(json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))) else 1)
