#!/bin/bash
# One seed R of the Deluge-lite experiment, both regimes: River (rf) at once, then the Trickle setting the
# coordinator picks after tuning (dl-config.txt: dla or dlb), pushed as each step ends.
#   CAMP_S=<scratchpad> bash dl-session.sh R
set -e
R=$1
L=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$L/../.." && pwd)
B=claude/document-review-xslwgg
push() {
  cd $REPO && git add $L/results/*-R$R-* && git commit -qm "deluge-lite: seed R$R $1 (k12-s1, LM-Tour)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || true
  for i in 2 4 8 16 0; do git pull -q --rebase origin $B && git push -q -u origin $B && break; [ $i = 0 ] || sleep $i; done
  cd $L
}
cd $L
for E in open r200; do bash dl-run.sh $E $R; done
push "River"
until [ -e $L/dl-config.txt ]; do sleep 60; (cd $REPO && git pull -q --rebase origin $B) || true; done
CFG=$(cat $L/dl-config.txt)
for E in open r200; do bash dl-run.sh $E $R $CFG; push "Deluge-lite $E"; done
touch $L/results/done-R$R
