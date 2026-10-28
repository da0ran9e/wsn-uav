#!/bin/bash
# Main session helping seeds 8 and 9 on their k8 map (README, 19:37): camp2.sh runs every job of those seeds and
# job.sh exits 3 at once for k16/k12, but runlog has already rewritten their logs R<R>/<env>-k16|k12-<sch>.md, which
# belong to the helper sessions. Before each commit: restore those from git and drop the new ones.
#   bash clean-main.sh
cd "$(dirname "$0")"
for R in 8 9; do
  git checkout -q -- $(git ls-files "R$R/*-k16-*.md" "R$R/*-k12-*.md") 2>/dev/null
  git ls-files --others --exclude-standard "R$R/*-k16-*.md" "R$R/*-k12-*.md" | xargs -r rm -f
done
