"""Rebuild the scan indexes of the paper notes from their front matter.

    python3 tools/papers/paper_index.py

Reads research_notes/literature/papers/*.md (except INDEX.md, TOPICS.md) and writes:
  papers/INDEX.md          one row per paper: key, year, venue, DOI, relevance, topics, one-line summary
  papers/TOPICS.md         topic -> papers (topics come from the controlled list in research_notes/literature/METHOD-vi.md)
  papers/figures/INDEX.md  one row per figure used by a note (figure rule, CLAUDE.md §6 mục 131)
Warns about figures in papers/figures/ that no note uses, and about topics outside the controlled list.
"""
import collections, datetime, os, re, subprocess

ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
P = os.path.join(ROOT, "research_notes/literature/papers")
METHOD = open(os.path.join(ROOT, "research_notes/literature/METHOD-vi.md"), encoding="utf-8").read()
VOCAB = dict(re.findall(r"^\| `([a-z0-9-]+)` \| ([^|]+) \|", METHOD, re.M))
today = datetime.date.today().isoformat()
head = f"---\nstatus: current\nupdated: {today}\n---\n"


def fm(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    return {k.strip(): v.strip() for k, v in (l.split(":", 1) for l in m.group(1).split("\n") if ":" in l)} if m else {}


notes = []
for f in sorted(os.listdir(P)):
    if not f.endswith(".md") or f in ("INDEX.md", "TOPICS.md"): continue
    t = open(os.path.join(P, f), encoding="utf-8").read()
    m = fm(t); m["file"] = f; m["text"] = t
    one = re.search(r"## Tóm tắt một dòng\n+(.+)", t)
    m["one"] = one.group(1).strip() if one else ""
    notes.append(m)

rows = ["| Bài | Năm | Venue | DOI | Mức | Chủ đề | Tóm tắt một dòng |", "|---|---|---|---|---|---|---|"]
for n in sorted(notes, key=lambda n: (-len(n.get("relevance", "")), n.get("year", ""))):
    rows.append(f"| [{n.get('key', n['file'][:-3])}]({n['file']}) | {n.get('year', '')} | {n.get('venue', '')} | "
                f"{n.get('doi', '')} | {n.get('relevance', '')} | {n.get('topics', '')} | {n['one']} |")
open(os.path.join(P, "INDEX.md"), "w").write(head + "# Danh mục ghi chú bài báo\n\nSinh tự động bởi "
    "`tools/papers/paper_index.py`; đừng sửa tay. Cách ghi chú: `../METHOD-vi.md`.\n\n" + "\n".join(rows) + "\n")

by = collections.defaultdict(list)
for n in notes:
    for t in [x.strip() for x in n.get("topics", "").split(",") if x.strip()]:
        if t not in VOCAB: print(f"warning: {n['file']}: topic '{t}' not in METHOD-vi.md")
        by[t].append(n)
out = [head + "# Chủ đề → bài\n\nSinh tự động bởi `tools/papers/paper_index.py`. Mỗi dòng: bài, mức liên quan, "
       "tóm tắt một dòng. Tìm số liệu hay định lý cụ thể: `grep -n \"\\[SỐ\\]\\|\\[KQ\\]\" *.md`.\n"]
for t in sorted(by, key=lambda t: list(VOCAB).index(t) if t in VOCAB else 999):
    out.append(f"\n## `{t}` · {VOCAB.get(t, '?').strip()}\n")
    for n in sorted(by[t], key=lambda n: -len(n.get("relevance", ""))):
        out.append(f"- [{n.get('key')}]({n['file']}) {n.get('relevance', '')} · {n['one']}")
open(os.path.join(P, "TOPICS.md"), "w").write("\n".join(out) + "\n")

FD = os.path.join(P, "figures"); os.makedirs(FD, exist_ok=True)
used, fr = set(), ["| Tệp | Mô tả | Lệnh | Tham số | Ngày | Commit |", "|---|---|---|---|---|---|"]
for n in notes:
    for cap, path in re.findall(r"!\[([^\]]*)\]\((figures/[^)]+)\)", n["text"]):
        name = os.path.basename(path); used.add(name)
        fr.append(f"| `{name}` | {cap} | `tools/papers/pdf_extract.py` (cắt theo chú thích) | {n.get('doi', '')} | "
                  f"{n.get('updated', today)} | xem git log |")
open(os.path.join(FD, "INDEX.md"), "w").write(
    "# Hình trích từ bài báo\n\nHình gốc của các bài (có chữ, ngoại lệ của mục 63), chỉ những hình mà ghi chú dùng. "
    "Sinh tự động bởi `tools/papers/paper_index.py`.\n\n" + "\n".join(fr) + "\n")
for f in sorted(os.listdir(FD)):
    if f.endswith(".png") and f not in used: print(f"warning: figures/{f} not used by any note")
print(f"{len(notes)} notes, {len(by)} topics, {len(used)} figures")
