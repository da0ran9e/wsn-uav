"""Prepare one paper for note taking: page-marked text, metadata (DOI via Crossref) and cropped figures.

    python3 tools/papers/pdf_extract.py PDF KEY WORKDIR

Writes, under WORKDIR/KEY/ (scratchpad, never committed):
  pages.txt   full text, each page preceded by '=== tr. N ===' (N = page index in the PDF, used for (tr. N) refs)
  meta.txt    DOI found in the first two pages and the Crossref record (title, authors, venue, year)
  fig/        every figure, cropped at 2x: KEY-figN.png (N = number in the caption), figs.tsv (file, page, caption)
Figure crop: for each text block starting with 'Fig.'/'Figure', the union of the vector drawings and images between
that caption and the nearest body-text block or other caption above it, in the caption's column, plus the short text
blocks (axis labels) next to them. Pages whose figures are raster scans without a text caption give no crop.
Copy only the figures the note uses to research_notes/literature/papers/figures/.
"""
import json, os, re, subprocess, sys, urllib.parse
import pymupdf

pdf, key, work = sys.argv[1:4]
d = os.path.join(work, key); fd = os.path.join(d, "fig"); os.makedirs(fd, exist_ok=True)
doc = pymupdf.open(pdf)
with open(os.path.join(d, "pages.txt"), "w") as f:
    for i, p in enumerate(doc):
        f.write(f"\n=== tr. {i + 1} ===\n" + p.get_text())
first = re.sub(r"\s+", " ", " ".join(doc[i].get_text() for i in range(min(2, len(doc)))))
doi = re.search(r"(10\.\d{4,9}/[^\s,;\"<>]+)", first)
doi = doi.group(1).rstrip(".)]") if doi else ""
q = f"https://api.crossref.org/works/{doi}" if doi else \
    "https://api.crossref.org/works?rows=1&query.bibliographic=" + urllib.parse.quote(first[:400])
try:
    r = json.loads(subprocess.run(["curl", "-s", "-m", "25", q], capture_output=True, text=True).stdout)["message"]
    it = r["items"][0] if "items" in r else r
    rec = dict(doi=it["DOI"], title=(it.get("title") or [""])[0], venue=(it.get("container-title") or [""])[0],
               year=it.get("issued", {}).get("date-parts", [[None]])[0][0],
               authors=", ".join(f"{a.get('given', '')} {a.get('family', '')}".strip() for a in it.get("author", [])))
except Exception as e:
    rec = dict(error=str(e)[:80])
with open(os.path.join(d, "meta.txt"), "w") as f:
    f.write(f"doi_in_pdf: {doi}\n" + "".join(f"{k}: {v}\n" for k, v in rec.items()))

rows = []
for pno, page in enumerate(doc):
    W = page.rect.width
    blocks = [b for b in page.get_text("blocks") if b[6] == 0]
    cap_re = re.compile(r"(Fig\.|Figure|FIGURE|Fig)\s*(\d+)")
    gfx = [dr["rect"] for dr in page.get_drawings() if dr["rect"].width > 2 or dr["rect"].height > 2]
    for img in page.get_images(full=True):
        try:
            r_ = page.get_image_bbox(img)
            if not r_.is_empty and not r_.is_infinite: gfx.append(r_)
        except Exception:
            pass
    for b in blocks:
        m = cap_re.match(b[4].strip())
        if not m: continue
        cap = pymupdf.Rect(b[:4])
        x0, x1 = (0, W) if cap.width > 0.55 * W else ((0, W / 2) if cap.x0 < W / 2 else (W / 2, W))
        barrier = [pymupdf.Rect(t[:4]) for t in blocks if t[3] <= cap.y0 + 1 and t is not b
                   and (len(t[4]) > 200 or cap_re.match(t[4].strip()))
                   and pymupdf.Rect(t[:4]).x0 < x1 and pymupdf.Rect(t[:4]).x1 > x0]
        top = max([r.y1 for r in barrier], default=0)
        g = [r for r in gfx if r.y0 >= top - 2 and r.y1 <= cap.y0 + 2 and r.x1 > x0 and r.x0 < x1]
        if not g: continue
        reg = pymupdf.Rect(g[0])
        for r in g[1:]: reg |= r
        near = reg + (-40, -10, 40, 10)                  # axis labels and tick numbers are short text blocks
        for t in blocks:
            r = pymupdf.Rect(t[:4])
            if t is not b and len(t[4]) < 200 and not cap_re.match(t[4].strip()) and r.y0 >= top - 2 \
                    and r.y1 <= cap.y0 + 2 and r.intersects(near):
                reg |= r
        reg = (reg | cap) & page.rect
        if reg.height < 40: continue
        name = f"{key}-fig{m.group(2)}.png"
        page.get_pixmap(clip=reg + (-4, -4, 4, 4), matrix=pymupdf.Matrix(2, 2)).save(os.path.join(fd, name))
        rows.append((name, pno + 1, re.sub(r"\s+", " ", b[4]).strip()[:200]))
with open(os.path.join(fd, "figs.tsv"), "w") as f:
    for r in rows: f.write("\t".join(map(str, r)) + "\n")
words = sum(len(p.get_text().split()) for p in doc)
print(f"{key}: {len(doc)} pages, {words} words, {len(rows)} figures, doi {rec.get('doi', doi)}")
print(f"  {rec.get('title', '')} | {rec.get('venue', '')} | {rec.get('year', '')}")
for r in rows: print(f"  {r[0]} (tr. {r[1]}) {r[2][:90]}")
