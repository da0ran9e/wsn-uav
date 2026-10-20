# 2026-10-19 · Matching time on a Raspberry-class critical cell (CLAUDE.md §8 item 95)

**Purpose:** replace the fixed MATCH = 5 s with a matching time computed from the device: Pi 5 + Hailo-8L, or Pi 5 CPU alone.

**Changes:**
- `uav-l2/tools/l1_mission.py`: new `match_time()`, `DEVICES` and `--device`.
- `uav-l2/tools/mission_policy.py`: `run()` takes a `match=` argument.

**Command:** `run.md`. Log: `run.md`. 240 configurations × 1 200 missions; ran in about 10 min; no ns-3 run.

**Inputs:** the geometry rebuilt by `regeom.py` (scratchpad `W/`, see `logs/2026-10-19_1500-l1-propose/`) and the saved River results.

**Outputs:**
- `uav-l2/docs/data/mission/l1m-hailo8l-summary.csv`
- `uav-l2/docs/data/mission/l1m-hailo8l-draws.csv.gz`
- report: `uav-l2/docs/L1-MISSION-vi.md` §7

**Result:**
- T_match is 0.03 s for L = 3 with Hailo-8L, and 0.25 s on the CPU.
- Mission end changes by −3.8 s on average against MATCH = 5 s; success rates are unchanged.
- Without a prebuilt index, re-embedding takes M / R: 39 s for M = 10 000 with Hailo-8L, 13 min on the CPU.

**Open:** DECODE, BW and the 20 GMAC/s search rate are estimates, not measurements on a Pi.
