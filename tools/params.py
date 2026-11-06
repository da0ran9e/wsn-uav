"""One source for the simulation parameter table (docs/REORG-GUIDE-vi.md step 7).
params.yaml at the repo root holds every row of the tables in paper/PARAMS-vi.md (sections 1-9);
`render` rewrites those tables from it, so edit params.yaml, never the tables.

    python3 tools/params.py render          # params.yaml -> tables in paper/PARAMS-vi.md
    python3 tools/params.py check           # exit 1 if the tables differ from params.yaml
    python3 tools/params.py extract         # one-off: tables -> params.yaml (used to create it)
The code does not read params.yaml yet; the "where" column names the constant each row comes from.
"""
import os, re, sys
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC = os.path.join(ROOT, "paper/PARAMS-vi.md")
YML = os.path.join(ROOT, "params.yaml")
HEAD = "| # | Tham số | Giá trị | Ở đâu | Nhãn | Nguồn / ghi chú |"
KEYS = ("id", "name", "value", "where", "label", "source")


def cells(line):
    parts = re.split(r"(?<!\\)\|", line.strip())[1:-1]
    assert len(parts) == len(KEYS), line
    return [p.strip() for p in parts]


def blocks(lines):
    """(section title, index of the header row, number of data rows) for each parameter table."""
    title = None
    for i, l in enumerate(lines):
        if l.startswith("## "):
            title = l[3:]
        if l == HEAD:
            n = 0
            while i + 2 + n < len(lines) and lines[i + 2 + n].startswith("|"):
                n += 1
            yield title, i, n


def extract():
    lines = open(DOC).read().split("\n")
    data = [{"section": t, "rows": [dict(zip(KEYS, cells(l))) for l in lines[i + 2:i + 2 + n]]}
            for t, i, n in blocks(lines)]
    with open(YML, "w") as fh:
        fh.write("# Simulation parameters: the one source for the tables of paper/PARAMS-vi.md (tools/params.py).\n")
        yaml.safe_dump(data, fh, allow_unicode=True, sort_keys=False, width=1000)


def rendered():
    data = yaml.safe_load(open(YML))
    lines = open(DOC).read().split("\n")
    out, j = [], 0
    for (t, i, n), sec in zip(blocks(lines), data):
        assert t == sec["section"], (t, sec["section"])
        out += lines[j:i + 2] + ["|" + "|".join(f" {r[k]} " if str(r[k]) else " " for k in KEYS) + "|"
                                 for r in sec["rows"]]
        j = i + 2 + n
    return "\n".join(out + lines[j:])


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "extract":
        extract()
    elif cmd == "render":
        text = rendered()                    # read the doc before opening it for writing
        open(DOC, "w").write(text)
    else:
        same = rendered() == open(DOC).read()
        print("tables match params.yaml" if same else "tables differ from params.yaml: run tools/params.py render")
        sys.exit(0 if same else 1)


if __name__ == "__main__":
    main()
