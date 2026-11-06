"""Builds docs/DOCS-INDEX.md from the front matter of the governed docs (docs/REORG-GUIDE-vi.md step 8).
Each doc starts with
    ---
    status: current | reference | superseded | history
    updated: YYYY-MM-DD
    superseded_by: <path or text>        (optional)
    ---
Rerun after adding or retiring a doc; tools/check.py status lists docs that lack the block.

    python3 tools/build_index.py
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check import ROOT, GOVERNED, STATUSES, tracked  # noqa: E402

LABEL = {"current": "Hiện hành", "reference": "Tham khảo", "superseded": "Bị thay thế", "history": "Lịch sử"}
NOTE = {"current": "nguồn số liệu và mô tả đang dùng",
        "reference": "còn đúng, dùng để tra cứu nền",
        "superseded": "đã có bản mới hơn (cột cuối)",
        "history": "thử nghiệm hoặc hướng đã đóng, giữ để tra lại"}


def meta(path):
    text = open(os.path.join(ROOT, path), encoding="utf-8", errors="replace").read()
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    fm = dict(l.split(":", 1) for l in m.group(1).split("\n") if ":" in l) if m else {}
    fm = {k.strip(): v.strip() for k, v in fm.items()}
    title = next((l[2:].strip() for l in text.split("\n") if l.startswith("# ")), os.path.basename(path))
    return fm, title.replace("|", "\\|")


def main():
    rows = {s: [] for s in STATUSES}
    for f in sorted(tracked()):
        if f.endswith(".md") and f.startswith(GOVERNED) and not re.search(r"/(figures|figs|data)/", f):
            fm, title = meta(f)
            if fm.get("status") in rows:
                rel = os.path.relpath(f, "docs")
                rows[fm["status"]].append(f"| [`{f}`]({rel}) | {title} | {fm.get('updated', '')} | {fm.get('superseded_by', '')} |")
    out = ["# Chỉ mục tài liệu", "",
           "Sinh bằng `python3 tools/build_index.py` từ phần đầu (front matter) của mỗi tài liệu; không sửa tay.",
           "Thí nghiệm: `docs/EXPERIMENTS-INDEX.md`. Log: `logs/INDEX.md`. Chat log: `docs/chatlog/INDEX.md`.",
           "Module `uav-sar/`, `uav-coop/`, `uav-coop2/` có README và tài liệu riêng (xem bản đồ trong `CLAUDE.md`).", ""]
    for s in STATUSES:
        out += [f"## {LABEL[s]} ({len(rows[s])}): {NOTE[s]}", "", "| Tệp | Tiêu đề | Cập nhật | Thay bằng |",
                "|---|---|---|---|", *rows[s], ""]
    open(os.path.join(ROOT, "docs/DOCS-INDEX.md"), "w").write("\n".join(out))
    print({s: len(r) for s, r in rows.items()})


if __name__ == "__main__":
    main()
