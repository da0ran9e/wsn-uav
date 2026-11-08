#!/bin/bash
# Build SigDrop-proposal-v1.pdf: pandoc (gfm -> html with pdf.css), then Chromium via the preinstalled Node Playwright.
set -e
cd "$(dirname "$0")"
pandoc SIGDROP-PROPOSAL-vi.md -f gfm+tex_math_dollars -t html5 --mathml --standalone --metadata pagetitle="SigDrop proposal" --css pdf.css -o _tmp.html
node pdf.js "$PWD/_tmp.html" "$PWD/SigDrop-proposal-v1.pdf"
rm -f _tmp.html
