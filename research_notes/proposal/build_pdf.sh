#!/bin/bash
# Build SIGDROP-PROPOSAL-vi.pdf: pandoc (gfm -> html with pdf.css), then Chromium via the preinstalled Node Playwright.
set -e
cd "$(dirname "$0")"
pandoc SIGDROP-PROPOSAL-vi.md -f gfm -t html5 --standalone --metadata pagetitle="SigDrop proposal" --css pdf.css -o _tmp.html
node pdf.js "$PWD/_tmp.html" "$PWD/SIGDROP-PROPOSAL-vi.pdf"
rm -f _tmp.html
