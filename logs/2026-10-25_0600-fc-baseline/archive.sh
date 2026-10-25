#!/bin/bash
# Mission folders packed for the repo (CLAUDE.md §8 item 167): the mission's inputs and results (map, plans,
# nodes, paths, River per-cell results, FC info and path), without the pass bitmaps (pass-bin rebuilds them bit for bit
# from the mission index, about 1 MB per cluster), the per-packet pass traces, logs and
# deploy scratch. One <channel>-<map>.tar.xz each, unpacked to a folder named by the map.
#   archive.sh WORK [WORK ...]
D=/home/user/wsn-uav/uav-l2/docs/data/results/raw
mkdir -p $D
for w in "$@"; do
  env=$(cat $w/env.txt 2>/dev/null || echo open); m=$(basename $w)
  tar -C $(dirname $w) -cJf $D/$env-$m.tar.xz --exclude='*.bin' --exclude='pass*-raw.csv' --exclude='pass*-track.csv' \
    --exclude='pass*-strip.csv' --exclude='*.log' --exclude='cand' \
    --exclude='tr' --exclude='ref*' $m
  echo "$env-$m.tar.xz $(du -k $D/$env-$m.tar.xz | cut -f1) kB $(sha256sum $D/$env-$m.tar.xz | cut -c1-16)"
done
