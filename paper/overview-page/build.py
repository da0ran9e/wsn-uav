"""Build the web page of a reference document: markdown -> HTML body inside template.html, with a contents rail,
glossary tips on every #g-… link, MathJax for the $$…$$ formulas and the figures copied to fig/.

    pip install markdown
    python3 paper/overview-page/build.py . <out_dir> [--doc overview|river-l3|l2]

  overview  paper/OVERVIEW-vi.md (CLAUDE.md §8 item 119) -> <out_dir>/river-overview.html,
            republished to https://claude.ai/artifact/BTcAwySMrwES5tHsLdCKw2
  river-l3  paper/RIVER-L3-vi.md (items 122, 124) -> <out_dir>/river-l3.html,
            republished to https://claude.ai/artifact/WpB2R7G7pVpo4QUwjW4DXB
  l2        paper/L2-PARTITION-vi.md (items 123, 124) -> <out_dir>/l2-partition.html,
            republished to https://claude.ai/artifact/4RMXn44sBxd4YLig4NBhqb
All write the figures to <out_dir>/fig/*.png.
"""
import html as H
import os
import re
import shutil
import sys
import unicodedata

import markdown
from markdown.extensions.toc import TocExtension

DOCS = {
    "overview": dict(
        src="OVERVIEW-vi.md", out="river-overview.html", figures=5, title="Tổng quan nghiên cứu River",
        eyebrow="Tài liệu tham chiếu nghiên cứu · bản đang chốt cho paper",
        lede="Giao truy vấn tìm kiếm tới mạng camera IoT bằng một lượt bay UAV cánh bằng, và hợp tác mặt đất có "
             "lập kế hoạch để lấp phần dữ liệu còn thiếu.",
        chips=[("Phiên bản", "21‑10‑2026"), ("Lời gốc:", "CLAUDE.md §8, mục 1–119"),
               ("Mọi số liệu:", "thăm dò, N &lt; 120")]),
    "river-l3": dict(
        src="RIVER-L3-vi.md", out="river-l3.html", figures=13, title="River: cơ chế lớp 3",
        eyebrow="Lớp 3 của Pha 1 · bản rút gọn",
        lede="Hợp tác mặt đất sau một lượt bay UAV: từng thuật toán với mã giả ngắn, mã giả đầy đủ và hình từng bước.",
        chips=[("Phiên bản", "22‑10‑2026"), ("Mọi số liệu:", "thăm dò, N &lt; 120")]),
    "l2": dict(
        src="L2-PARTITION-vi.md", out="l2-partition.html", figures=6, title="Lớp 2: phân vùng MEANDER",
        eyebrow="Lớp 2 của Pha 1 · bản rút gọn",
        lede="Chọn đường bay trước, rồi chia cluster theo đường bay: luồng cong bám địa hình, từng bước với mã giả "
             "và hình.",
        chips=[("Phiên bản", "22‑10‑2026"), ("Tình trạng:", "chưa thắng cluster có sẵn; chờ so công bằng")]),
}
repo, out = sys.argv[1], sys.argv[2]
doc = DOCS[sys.argv[sys.argv.index("--doc") + 1] if "--doc" in sys.argv else "overview"]
src = os.path.join(repo, "paper", doc["src"])
text = open(src, encoding="utf-8").read()


def slugify(value, separator):
    value = value.replace("đ", "d").replace("Đ", "D")
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[%s\s]+" % separator, separator, value)


# display math out of markdown's way
maths = []
def keep_math(m):
    maths.append(m.group(1))
    return f"\n\nMATHBLOCK{len(maths) - 1}\n\n"
text = re.sub(r"\$\$(.+?)\$\$", keep_math, text, flags=re.S)

# GitHub lets a list start right under a paragraph and nest by 2 spaces; Python-Markdown needs a blank line before it
LIST = re.compile(r"^\s*(?:[-*]|\d+\.)\s")
lines, fence, prev = [], False, ""
for line in text.split("\n"):
    if line.startswith("```"):
        fence = not fence
    quote = line.startswith(">")
    core, pcore = (line[1:].lstrip() if quote else line), (prev[1:].lstrip() if prev.startswith(">") else prev)
    if not fence and LIST.match(core) and pcore.strip() and not LIST.match(pcore) and not pcore.startswith("|") \
            and not pcore.startswith("   ") and quote == prev.startswith(">"):
        lines.append(">" if quote else "")
    lines.append(line)
    prev = line
text = "\n".join(lines)

# the page has its own header: drop the markdown title and subtitle
text = re.sub(r"\A# .+?\n\n\*\*.+?\*\*\n", "", text, flags=re.S)

body = markdown.markdown(text, tab_length=2, extensions=["tables", "fenced_code", TocExtension(slugify=slugify, toc_depth="2-3")])

for i, m in enumerate(maths):
    body = body.replace(f"<p>MATHBLOCK{i}</p>", f'<div class="math">$${H.escape(m)}$$</div>')
assert "MATHBLOCK" not in body

body = re.sub(r'<pre><code class="language-mermaid">(.*?)</code></pre>', r'<pre class="mermaid">\1</pre>', body, flags=re.S)
body = re.sub(r"<table>", '<div class="table-wrap"><table>', body)
body = body.replace("</table>", "</table></div>")

# figures: image paragraph + following italic caption paragraph + its list
os.makedirs(os.path.join(out, "fig"), exist_ok=True)
def figure(m):
    alt, path = m.group(1), m.group(2)
    name = os.path.basename(path)
    shutil.copy(os.path.normpath(os.path.join(repo, "paper", path)), os.path.join(out, "fig", name))
    return f'<figure><div class="plate"><img src="fig/{name}" alt="{alt}" loading="lazy"></div>'
body = re.sub(r'<p><img alt="([^"]*)" src="([^"]+)" ?/?></p>', figure, body)
body = re.sub(r'(<figure><div class="plate">.*?</div>)\s*<p><em>(.*?)</em></p>\s*(<[ou]l>.*?</[ou]l>)?',
              lambda m: f'{m.group(1)}<figcaption><strong>{m.group(2)}</strong>{m.group(3) or ""}</figcaption></figure>',
              body, flags=re.S)
assert body.count("<figure>") == body.count("</figure>") == doc["figures"], body.count("<figure>")

# version and scope bullets are already in the page header
body, n = re.subn(r"\A\s*<ul>.*?</ul>\s*(?=<blockquote>)", "", body, flags=re.S)
assert n == 1

# blockquote "Cách đọc" becomes a note
body = body.replace("<blockquote>", '<aside class="note">').replace("</blockquote>", "</aside>")

toc = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body)
nav = "\n".join(f'<li><a href="#{i}">{re.sub(r"<[^>]+>", "", t)}</a></li>' for i, t in toc)

tpl = open(os.path.join(os.path.dirname(__file__), "template.html"), encoding="utf-8").read()
chips = "\n".join(f"      <li>{k} <strong>{v}</strong></li>" for k, v in doc["chips"])
for k, v in (("TITLE", doc["title"]), ("EYEBROW", doc["eyebrow"]), ("LEDE", doc["lede"]), ("CHIPS", chips)):
    tpl = tpl.replace("{{%s}}" % k, v)
page = tpl.replace("{{NAV}}", nav).replace("{{BODY}}", body)
open(os.path.join(out, doc["out"]), "w", encoding="utf-8").write(page)
print(len(page), "bytes;", len(toc), "sections;", len(maths), "formulas")
