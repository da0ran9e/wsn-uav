#!/bin/bash
# Draft v5 with the changes merged (CLAUDE.md §8 item 185): v5 pages 1-4 + tail.tex compiled.
set -e; cd "$(dirname "$0")"
python3 estimate.py >/dev/null && python3 fig_mission.py
pdflatex -interaction=nonstopmode tail.tex >/dev/null; pdflatex -interaction=nonstopmode tail.tex >/dev/null
python3 -c "
import pymupdf
v=pymupdf.open('/root/.claude/uploads/fd83db84-4832-5a0e-be6a-d1201f4d6a60/35bd33b7-SigDrop_ICC_draft_v5.pdf')
o=pymupdf.open(); o.insert_pdf(v,from_page=0,to_page=3); o.insert_pdf(pymupdf.open('tail.pdf')); o.save('SigDrop_ICC_draft_v5-merged.pdf')
print(o.page_count,'pages')"
