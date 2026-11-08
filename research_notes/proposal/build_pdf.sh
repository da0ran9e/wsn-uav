#!/bin/bash
# Build SigDrop-proposal-v1.pdf: pandoc (gfm + TeX math -> HTML with MathML, title page, table of contents, pdf.css),
# then Chromium via the preinstalled Node Playwright.
set -e
cd "$(dirname "$0")"
python3 - <<'PY'
s = open("SIGDROP-PROPOSAL-vi.md").read().split("---\n", 2)[2]      # drop the YAML status block
lines = s.split("\n"); i = next(k for k, l in enumerate(lines) if l.startswith("# "))
open("_tmp.md", "w").write("\n".join(lines[i + 1:]))                  # the title goes to the title block
PY
pandoc _tmp.md -f gfm+tex_math_dollars -t html5 --mathml --standalone --toc --toc-depth=3 \
  --metadata-file meta.yaml --css pdf.css -o _tmp.html
node pdf.js "$PWD/_tmp.html" "$PWD/SigDrop-proposal-v1.pdf"
rm -f _tmp.html _tmp.md
