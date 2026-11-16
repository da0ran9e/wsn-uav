#!/bin/sh
# Build the J1 draft: pdflatex twice, output main.pdf in this folder.
cd "$(dirname "$0")" && pdflatex -interaction=nonstopmode -halt-on-error main.tex >build.log 2>&1 && pdflatex -interaction=nonstopmode -halt-on-error main.tex >>build.log 2>&1 && grep -E "Output written|Warning: (Reference|Citation)" build.log | sort | uniq -c | tail -8
