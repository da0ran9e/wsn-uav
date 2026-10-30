#!/bin/bash
# Set up a session for run.sh: campaign 4's binaries and seed-1 CHORD geometry (../2026-10-27_1714-campaign4/
# child-setup.sh), then CAMP-BIN6 = CAMP-BIN5 with river-bin8.xz (PHY state counters, --tScope, --pageBreaks with Seg breaks, direct pull with River's repairs).
#   CAMP_S=<scratchpad> bash setup.sh        (prints CHECK OK at the end)
set -e
: "${CAMP_S:?set CAMP_S to the scratchpad of this session}"
L=$(cd "$(dirname "$0")" && pwd)
CAMP_S=$CAMP_S bash "$L/../2026-10-27_1714-campaign4/child-setup.sh"
rm -rf "$CAMP_S/CAMP-BIN6"
cp -a "$CAMP_S/CAMP-BIN5" "$CAMP_S/CAMP-BIN6"
xz -dc "$L/river-bin8.xz" > "$CAMP_S/CAMP-BIN6/river-bin"
chmod +x "$CAMP_S/CAMP-BIN6/river-bin"
h=$(sha256sum "$CAMP_S/CAMP-BIN6/river-bin" | cut -c1-16)
[ "$h" = d22ef674a82974b9 ] || { echo "river-bin hash $h, expected d22ef674a82974b9"; exit 1; }
LD_LIBRARY_PATH="$CAMP_S/CAMP-BIN6/lib" "$CAMP_S/CAMP-BIN6/river-bin" --help 2>&1 | grep -q tScope
[ -d "$CAMP_S/C4/CP/r100/R1/k8-s1" ] && [ -e "$CAMP_S/C4/CP/r100/R1/k8-s1/plan8.txt" ]
echo CHECK OK
