# CLAUDE.md · uav-sar

## UAV-SAR: READ THE STATUS DOC FIRST

**Before doing anything in `uav-sar/`, read `uav-sar/docs/STATUS.md`.** It is the
single source of current truth: what the measurements actually say, which
published numbers are stale or void, the ranked open problems, and the method
rules that were learned expensively (N ≥ 120, never trust a single seed, never
rebuild mid-campaign, assert on every scripted edit).

Two things that document will tell you but which are worth stating here too,
because they invert the project's original assumptions:

- **Cooperation does not buy the cost advantage — closing the loop does.** The
  `closed-loop` non-cooperative baseline beats `proposed` on time, energy and
  packets (0/120 paired wins on packets). What cooperation defensibly buys is a
  −29 % p90 localization error. Do not write or repeat "edge cooperation makes
  SAR faster and cheaper"; the data does not support it.
- **Numbers measured at N = 20 are void.** They missed a real 3.3 % failure mode
  and understated a delivery error by 42 %.

Note the surrounding sections were written for the older `src/wsn-uav/` layout;
the live work is in `uav-sar/` and builds via
`cd /home/user/ns3-dev && cmake --build cmake-cache -j 3`.
