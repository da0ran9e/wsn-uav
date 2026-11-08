#!/bin/bash
# Proposal v1 (LaTeX): regenerate body.tex from ../SIGDROP-PROPOSAL-vi.md, then xelatex twice.
set -e
cd "$(dirname "$0")"
python3 -c "s=open('../SIGDROP-PROPOSAL-vi.md').read(); open('_src.md','w').write(s.split('---\n',2)[2].replace('## 9. Kế hoạch thực hiện **[cần chốt]**','## 9. Kế hoạch thực hiện'))"
pandoc _src.md -f gfm-gfm_auto_identifiers -t latex --top-level-division=section -o body_raw.tex
python3 post.py
xelatex -interaction=nonstopmode main.tex >/dev/null || true
xelatex -interaction=nonstopmode main.tex >/dev/null || true
cp main.pdf SigDrop-proposal-v1.pdf
rm -f _src.md body_raw.tex main.aux main.log main.out main.toc
