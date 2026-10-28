"""The number tables of paper/TECHREPORT-vi.md section 3 from the campaign's scores (CLAUDE.md §8 item 208: at 70 %
of the jobs, update only those tables). Rewrites in place, rows only, headers and text untouched:
  - the seed-count table under "Số seed đã gộp vào từng ô";
  - §3.1, T* per scheme (table.py's means over the seeds every scheme has done, slowest first);
  - §3.1, LM-Tour relative to each scheme (Rotary TSP as a ratio, the others in %);
  - §3.2 (b), the mean River-ready time (ready.py's rows).
Without --apply it prints the new rows and the lines they replace.

    python3 techreport.py [--apply]
"""
import argparse, io, os, re, subprocess, sys
from collections import defaultdict
from contextlib import redirect_stdout

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import table as T  # noqa: E402

DOC = os.path.join(HERE, "../../paper/TECHREPORT-vi.md")
NAME = {"B1": "Rotary TSP (cận trên)", "DN": "FC + DTSP-N", "DR": "DTSP-N + River", "CP": "CHORD + River",
        "LMD": "**LM-Tour + River**"}
num = lambda x: f"{x:.1f}".replace(".", ",")
pct = lambda x: f"{x:+.0f}".replace("-", "−").replace("+", "+") if round(x) != 0 else "0"


def rows():
    X, _ = T.load()
    seeds = defaultdict(set)   # as table.py: the seeds every scheme has done
    for s, env, K, R in X:
        if all((t, env, K, R) in X for t in ("LMD", "CP", "DR", "DN")):
            seeds[(env, K)].add(R)
    mean = lambda s, env, K: np.mean([t for R in sorted(seeds[(env, K)]) for t, _ in X[(s, env, K, R)].values()])
    count = [f"| k{K} | " + " | ".join(str(len(seeds[(e, K)])) for e in T.ENVS) + " |" for K in T.MAPS]
    tstar = []
    for s in ("B1", "DN", "DR", "CP", "LMD"):
        cells = [" / ".join(f"{mean(s, e, K):.0f}" for K in T.MAPS) for e in T.ENVS]
        if s == "LMD":
            cells = [f"**{c}**" for c in cells]
        tstar.append(f"| {NAME[s]} | " + " | ".join(cells) + " |")
    rel = []
    for s, label in (("B1", "Rotary TSP (lần nhanh hơn)"), ("DN", "FC + DTSP-N"), ("DR", "DTSP-N + River"),
                     ("CP", "CHORD + River")):
        if s == "B1":
            cells = [" / ".join(f"{num(mean(s, e, K) / mean('LMD', e, K))}×" for K in T.MAPS) for e in T.ENVS]
        else:
            cells = [" / ".join(pct(100 * (mean("LMD", e, K) / mean(s, e, K) - 1)) for K in T.MAPS) for e in T.ENVS]
        rel.append(f"| {label} | " + " | ".join(cells) + " |")
    out = subprocess.run([sys.executable, os.path.join(HERE, "ready.py"), HERE], capture_output=True, text=True,
                         check=True).stdout
    r = {}
    for line in out.splitlines()[2:]:
        env, K, dr, cp, lm, _ = [c.strip() for c in line.strip("|").split("|")]
        r[(env, int(K))] = (dr, cp, lm)
    ready = [f"| {e} | 8 / 12 / 16 | " + " | ".join(" / ".join(r[(e, K)][i] for K in T.MAPS) for i in range(3)) + " |"
             for e in T.ENVS if all((e, K) in r for K in T.MAPS)]
    return dict(count=count, tstar=tstar, rel=rel, ready=ready)


def block(lines, header, n):
    """Index of the n table rows that follow the header row matching `header` (and its |---| line)."""
    i = next(k for k, l in enumerate(lines) if re.match(header, l))
    assert lines[i + 1].startswith("|---"), lines[i + 1]
    assert all(lines[i + 2 + j].startswith("|") for j in range(n)) and not lines[i + 2 + n].startswith("|"), header
    return i + 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    with redirect_stdout(io.StringIO()):
        R = rows()
    lines = open(DOC).read().split("\n")
    spots = [("count", r"^\| \| open \| r500 \| r200 \| r100 \|$", 3),
             ("tstar", r"^\| Phương án \| r = 1 000 m \(open\)", 5),
             ("rel", r"^\| So với \| open \| r500 \| r200 \| r100 \|$", 4),
             ("ready", r"^\| Kênh \| K \| DTSP-N \+ River \| CHORD \| LM-Tour \|$", 4)]
    for key, header, n in spots:
        i = block(lines, header, n)
        new = R[key]
        assert len(new) == n, (key, len(new))
        for old, nw in zip(lines[i:i + n], new):
            if old != nw:
                print(f"- {old}\n+ {nw}")
        lines[i:i + n] = new
    if a.apply:
        open(DOC, "w").write("\n".join(lines))
        print(f"applied to {os.path.relpath(DOC)}")


if __name__ == "__main__":
    main()
