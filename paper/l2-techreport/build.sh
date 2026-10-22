#!/bin/sh
# Build the Layer-2 technical report (CLAUDE.md §8 item 127): figures, then two pdflatex passes for references.
set -e
cd "$(dirname "$0")"
python3 make_figs.py
pdflatex -interaction=nonstopmode -halt-on-error l2-techreport.tex > /dev/null
pdflatex -interaction=nonstopmode -halt-on-error l2-techreport.tex | grep -E "Output written|Warning|Overfull|Underfull" || true
rm -f l2-techreport.aux l2-techreport.log l2-techreport.out
