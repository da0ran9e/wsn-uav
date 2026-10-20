# trace-subch

- Bắt đầu: 2026-10-20 21:50:14, chạy 154 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
nice -n 10 bash tools/river_trace.sh /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/SW/k4-s2 /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/TR/sw-k4-s2 /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN && python3 tools/l1_anim.py --work /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/SW/k4-s2 --trace /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/TR/sw-k4-s2 --method P+prog-latency-puq-stage-zero --out /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/anim/l1-sw-k4s2.json && python3 tools/l1_steps.py --json /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/anim/l1-sw-k4s2.json --out docs/figures/l1-steps-sw-k4-s2.png
```

**Kết quả**

```text
run 1 river-full: D 3612, 7/7 critical done, sim 67.7 s, wall 147 s, 152616 hops, 5776 MAC give-ups, 0/157 gateway pairs with q < 0.5
  C1 identical to the folder's run
run 1 river-full: D 3321, 4/4 critical done, sim 26.3 s, wall 30 s, 26411 hops, 875 MAC give-ups, 0/112 gateway pairs with q < 0.5
  C2 identical to the folder's run
run 1 river-full: D 2562, 2/2 critical done, sim 2.0 s, wall 1 s, 982 hops, 52 MAC give-ups, 0/28 gateway pairs with q < 0.5
  C3 identical to the folder's run
run 1 river-full: D 3407, 4/4 critical done, sim 13.1 s, wall 17 s, 10280 hops, 466 MAC give-ups, 0/129 gateway pairs with q < 0.5
  C4 identical to the folder's run
run 1 river-full: D 1945, 2/2 critical done, sim 1.7 s, wall 1 s, 842 hops, 20 MAC give-ups, 0/49 gateway pairs with q < 0.5
  C5 identical to the folder's run
run 1 river-full: D 3886, 5/5 critical done, sim 48.1 s, wall 96 s, 109037 hops, 4172 MAC give-ups, 0/127 gateway pairs with q < 0.5
  C6 identical to the folder's run
/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/anim/l1-sw-k4s2.json: 0.55 MB; draw 0: c* cell 336, team 2 leaves 0 s, verifies c* at 560 s (visit 2), all at 4924 s; 24 decisions, 1 staging moves
```
