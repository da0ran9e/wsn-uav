#!/bin/bash
# Set up a Deluge-lite session (SigDrop 2 backup design): campaign 4's binaries and seed-1 geometry
# (../2026-10-27_1714-campaign4/child-setup.sh), then CAMP-BIN9 = CAMP-BIN5 with river-bin9.xz (river-bin8 plus
# --tScope=all and the advert frame class).   CAMP_S=<scratchpad> bash setup.sh   (prints CHECK OK)
set -e
: "${CAMP_S:?set CAMP_S to the scratchpad of this session}"
L=$(cd "$(dirname "$0")" && pwd)
CAMP_S=$CAMP_S bash "$L/../2026-10-27_1714-campaign4/child-setup.sh"
rm -rf "$CAMP_S/CAMP-BIN9"
cp -a "$CAMP_S/CAMP-BIN5" "$CAMP_S/CAMP-BIN9"
xz -dc "$L/river-bin9.xz" > "$CAMP_S/CAMP-BIN9/river-bin"
chmod +x "$CAMP_S/CAMP-BIN9/river-bin"
h=$(sha256sum "$CAMP_S/CAMP-BIN9/river-bin" | cut -c1-16)
[ "$h" = a8978aa232b428a5 ] || { echo "river-bin hash $h, expected a8978aa232b428a5"; exit 1; }
LD_LIBRARY_PATH="$CAMP_S/CAMP-BIN9/lib" "$CAMP_S/CAMP-BIN9/river-bin" --help 2>&1 | grep -q tScope
for e in open r200; do [ -e "$CAMP_S/C4/CP/$e/R1/k12-s1/tour.json" ]; done
echo CHECK OK
