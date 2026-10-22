"""Build the PDF of a technical report from markdown (CLAUDE.md §8 item 125).

    pip install markdown playwright
    python3 paper/techreport/build.py paper/L3-TECHREPORT-vi.md <out_dir> [--fonts DIR]

Markdown conventions on top of GitHub tables and fences:
  ![fig:key](a.png "w=45") ![](b.png)   one figure; images in one paragraph sit side by side; w = percent of the
                                        text width for the whole row (default 100). The italic paragraph right
                                        after it is the caption, and a list right after that belongs to it too
  : tab:key Caption                     caption of the table right below it
  {fig:key} {tab:key}                   become "Hình N" / "Bảng N"
  ```algo                               pseudo code; its first line is the algorithm's title
The first lines are the title page: "# Title", "**Subtitle**", then a list of "Key: value" items.
Writes <out_dir>/<stem>.html and <stem>.pdf (A4, Chromium via Playwright). Fonts: Source Serif 4, IBM Plex Sans and
JetBrains Mono from Google Fonts, fetched once with curl into DIR (default <out_dir>/fonts); system fonts otherwise.
"""
import html as H
import os
import re
import subprocess
import sys

import markdown
from playwright.sync_api import sync_playwright

src, out = sys.argv[1], sys.argv[2]
fonts = sys.argv[sys.argv.index("--fonts") + 1] if "--fonts" in sys.argv else os.path.join(out, "fonts")
stem = os.path.splitext(os.path.basename(src))[0]
base = os.path.dirname(os.path.abspath(src))
os.makedirs(out, exist_ok=True)
text = open(src, encoding="utf-8").read()

# ---------- fonts ----------
FAMILIES = "family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400" \
           "&family=IBM+Plex+Sans:wght@400;600&family=JetBrains+Mono:wght@400"
css_path = os.path.join(fonts, "fonts.css")
if not os.path.exists(css_path):
    os.makedirs(fonts, exist_ok=True)
    try:
        css = subprocess.run(["curl", "-sSf", "-m", "30", "-A", "Mozilla/5.0 Chrome/120",
                              f"https://fonts.googleapis.com/css2?{FAMILIES}&display=swap"],
                             capture_output=True, text=True, check=True).stdout
        for url in sorted(set(re.findall(r"url\((https://[^)]+)\)", css))):
            name = os.path.basename(url)
            subprocess.run(["curl", "-sSf", "-m", "60", "-o", os.path.join(fonts, name), url], check=True)
            css = css.replace(url, "file://" + os.path.abspath(os.path.join(fonts, name)))
        open(css_path, "w").write(css)
    except (subprocess.CalledProcessError, OSError) as e:
        print("fonts not fetched, using system fonts:", e)
font_css = open(css_path).read() if os.path.exists(css_path) else ""

# ---------- title page ----------
m = re.match(r"# (.+?)\n\n\*\*(.+?)\*\*\n\n((?:- .+\n)+)", text)
assert m, "title, subtitle and metadata list expected at the top"
title, subtitle = m.group(1), m.group(2)
meta = [l[2:].split(":", 1) for l in m.group(3).strip().split("\n")]
text = text[m.end():]

# ---------- numbering ----------
labels, counts = {}, {"fig": 0, "tab": 0}
for kind, key in re.findall(r"(?:!\[|^: )(fig|tab):([\w-]+)", text, flags=re.M):
    counts[kind] += 1
    assert f"{kind}:{key}" not in labels, key
    labels[f"{kind}:{key}"] = counts[kind]
def ref(m):
    k = f"{m.group(1)}:{m.group(2)}"
    assert k in labels, f"unknown reference {k}"
    return ("Hình " if m.group(1) == "fig" else "Bảng ") + str(labels[k])
text = re.sub(r"\{(fig|tab):([\w-]+)\}", ref, text)

# Python-Markdown needs a blank line before a list that starts right under a paragraph
LIST = re.compile(r"^\s*(?:[-*]|\d+\.)\s")
lines, fence, prev = [], False, ""
for line in text.split("\n"):
    if line.startswith("```"):
        fence = not fence
    if not fence and LIST.match(line) and prev.strip() and not LIST.match(prev) and not prev.startswith("|") \
            and not prev.startswith("   ") and not prev.startswith(">"):
        lines.append("")
    lines.append(line)
    prev = line
text = "\n".join(lines)

body = markdown.markdown(text, tab_length=2, extensions=["tables", "fenced_code"])

# ---------- figures ----------
IMG = re.compile(r'<img alt="([^"]*)" src="([^"]+)"(?: title="([^"]*)")? ?/?>')
def figure(m):
    imgs = IMG.findall(m.group(1))
    key = imgs[0][0]
    w = re.search(r"w=(\d+)", imgs[0][2] or "")
    row = "".join(f'<img src="file://{os.path.normpath(os.path.join(base, p))}" alt="">' for _, p, _ in imgs)
    for _, p, _ in imgs:
        assert os.path.exists(os.path.normpath(os.path.join(base, p))), p
    cap, lst = m.group(2), m.group(3) or ""
    return (f'<figure id="{key}"><div class="row" style="width:{w.group(1) if w else 100}%">{row}</div>'
            f'<figcaption><b>Hình {labels[key]}.</b> {cap}{lst}</figcaption></figure>')
body, nf = re.subn(r'<p>((?:<img [^>]+>\s*)+)</p>\s*<p><em>(.*?)</em></p>\s*(<ul>.*?</ul>)?', figure, body, flags=re.S)
assert nf == counts["fig"] and "<img" not in re.sub(r"<figure.*?</figure>", "", body, flags=re.S), (nf, counts)

# ---------- tables ----------
def table(m):
    return f'<div class="tab" id="{m.group(1)}"><p class="tcap"><b>Bảng {labels[m.group(1)]}.</b> {m.group(2)}</p><table>'
body, nt = re.subn(r"<p>: (tab:[\w-]+) (.*?)</p>\s*<table>", table, body, flags=re.S)
assert nt == counts["tab"], (nt, counts)
body = re.sub(r'(<div class="tab".*?</table>)', r"\1</div>", body, flags=re.S)

# ---------- algorithms ----------
def algo(m):
    first, _, rest = m.group(1).partition("\n")
    return f'<div class="algo"><div class="ahead">{first}</div><pre>{rest.rstrip()}</pre></div>'
body = re.sub(r'<pre><code class="language-algo">(.*?)</code></pre>', algo, body, flags=re.S)
body = body.replace("<blockquote>", '<aside class="note">').replace("</blockquote>", "</aside>")

# ---------- contents ----------
heads = re.findall(r"<h2>(.*?)</h2>", body)
for h in heads:
    cls = ' class="appendix"' if h.startswith("Phụ lục") else ""
    body = body.replace(f"<h2>{h}</h2>", f'<h2 id="s-{heads.index(h)}"{cls}>{h}</h2>', 1)
toc = "".join(f'<li><a href="#s-{i}">{h}</a></li>' for i, h in enumerate(heads))

page = f"""<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>{H.escape(title)}</title>
<style>{font_css}{open(os.path.join(os.path.dirname(__file__), "report.css"), encoding="utf-8").read()}</style></head>
<body><section class="cover"><p class="kind">Báo cáo kỹ thuật</p><h1>{title}</h1><p class="sub">{subtitle}</p>
<dl>{"".join(f"<dt>{k.strip()}</dt><dd>{v.strip()}</dd>" for k, v in meta)}</dl>
<nav><p>Nội dung</p><ol>{toc}</ol></nav></section>
<main>{body}</main></body></html>"""
html_path = os.path.join(out, stem + ".html")
open(html_path, "w", encoding="utf-8").write(page)

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
    pg = b.new_page()
    pg.goto("file://" + os.path.abspath(html_path))
    pg.wait_for_load_state("networkidle")
    pg.evaluate("document.fonts.ready")
    foot = (f'<div style="width:100%;font:7.5pt sans-serif;color:#6b6f72;padding:0 18mm;display:flex;'
            f'justify-content:space-between"><span>{H.escape(title)}</span>'
            '<span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>')
    pg.pdf(path=os.path.join(out, stem + ".pdf"), format="A4", print_background=True, display_header_footer=True,
           header_template="<div></div>", footer_template=foot,
           margin={"top": "18mm", "bottom": "20mm", "left": "18mm", "right": "18mm"})
    b.close()
print(f"{counts['fig']} figures, {counts['tab']} tables, {len(heads)} sections -> {stem}.html, {stem}.pdf")
