"""Repo hygiene check (docs/REORG-GUIDE-vi.md step 8). Reports, does not fix:
  links    relative Markdown links and images that point to a missing file
  status   governed docs without a `status:` front matter line
  index    images in a figures/ folder that its INDEX.md does not mention
  large    tracked files over the size limit
docs/chatlog/ (verbatim user text) and logs/ (run records) are not link-checked.

    python3 tools/check.py [links|status|index|large ...] [--limit-mb 5] [--staged]
--staged checks only the files staged for commit (the pre-commit hook, tools/hooks/pre-commit), so problems
that predate a commit do not block it. Exit code 1 when anything is reported.
"""
import argparse, os, re, subprocess, sys
from urllib.parse import unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOVERNED = ("paper/", "uav-l2/docs/", "docs/progress/", "research_notes/", "reports/")
STATUSES = ("current", "reference", "superseded", "history")
LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
IMG = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")


def tracked():
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True).stdout
    return [f for f in out.split("\0") if f]


def front_status(path):
    """Value of `status:` in a leading YAML block, or None."""
    with open(os.path.join(ROOT, path), encoding="utf-8", errors="replace") as fh:
        if fh.readline().strip() != "---":
            return None
        for line in fh:
            if line.strip() == "---":
                return None
            if line.startswith("status:"):
                return line.split(":", 1)[1].strip()
    return None


def links(files):
    bad = []
    for f in files:
        if not f.endswith(".md") or f.startswith(("docs/chatlog/", "logs/")):
            continue
        text = open(os.path.join(ROOT, f), encoding="utf-8", errors="replace").read()
        text = re.sub(r"```.*?```", "", text, flags=re.S)        # code blocks are not links
        for m in LINK.finditer(text):
            t = m.group(1)
            if re.match(r"^[a-z]+:", t) or t.startswith("#"):
                continue
            p = unquote(t.split("#")[0])
            if p and not os.path.exists(os.path.normpath(os.path.join(ROOT, os.path.dirname(f), p))):
                bad.append(f"{f}: {t}")
    return bad


def status(files):
    bad = []
    for f in files:
        if f.endswith(".md") and f.startswith(GOVERNED) and "/figures/" not in f and "/figs/" not in f and "/data/" not in f:
            s = front_status(f)
            if s not in STATUSES:
                bad.append(f"{f}: status={s}")
    return bad


def index(files):
    bad = []
    dirs = {os.path.dirname(f) for f in files if "/figures/" in f + "/" and f.lower().endswith(IMG)}
    for d in sorted(dirs):
        idx = os.path.join(ROOT, d, "INDEX.md")
        text = open(idx, encoding="utf-8", errors="replace").read() if os.path.exists(idx) else None
        if text is None:
            continue                                 # folders made before rule 131 have no INDEX.md
        for f in files:
            if os.path.dirname(f) == d and f.lower().endswith(IMG) and os.path.basename(f) not in text:
                bad.append(f"{d}/INDEX.md: missing {os.path.basename(f)}")
    return bad


def large(files, limit_mb):
    return [f"{f}: {os.path.getsize(os.path.join(ROOT, f)) / 2**20:.1f} MB" for f in files
            if os.path.isfile(os.path.join(ROOT, f)) and os.path.getsize(os.path.join(ROOT, f)) > limit_mb * 2**20]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("checks", nargs="*", default=["links", "status", "index", "large"])
    ap.add_argument("--limit-mb", type=float, default=5)
    ap.add_argument("--staged", action="store_true")
    a = ap.parse_args()
    files = tracked()
    if a.staged:
        out = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"], cwd=ROOT,
                             capture_output=True, text=True).stdout
        files = [f for f in out.split("\0") if f]
    found = 0
    for c in a.checks:
        rows = large(files, a.limit_mb) if c == "large" else globals()[c](files)
        print(f"## {c}: {len(rows)}")
        for r in rows:
            print("  " + r)
        found += len(rows)
    sys.exit(1 if found else 0)


if __name__ == "__main__":
    main()
