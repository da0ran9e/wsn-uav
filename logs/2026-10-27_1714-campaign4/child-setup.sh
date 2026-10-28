#!/bin/bash
# Set up a campaign session (CLAUDE.md §8 item 201): the frozen binaries (CAMP-BIN5, the ones of the main session) and
# seed 1's CHORD geometry from the repo into $CAMP_S, scikit-learn for lm_tour.
#   CAMP_S=<scratchpad> bash child-setup.sh
set -e
: "${CAMP_S:?set CAMP_S to the scratchpad of this session}"
L=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$CAMP_S/C4"
tar xJf "$L/camp-bin5.tar.xz" -C "$CAMP_S"
tar xJf "$L/geometry-r1.tar.xz" -C "$CAMP_S/C4"
pip install --break-system-packages -q scikit-learn 2>&1 | grep -v WARNING || true
python3 -c 'import sklearn, numpy, scipy; print("python ok", sklearn.__version__)'
(cd "$CAMP_S/CAMP-BIN5" && sha256sum deploy-bin pass-bin river-bin | cut -c1-16)   # expect 508c170d 4bb3832e 60a32c12
ls "$CAMP_S/C4/CP/"*/R1 | head -3
