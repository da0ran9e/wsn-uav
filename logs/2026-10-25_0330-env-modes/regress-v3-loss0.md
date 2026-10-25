# regress-v3-loss0

- Bắt đầu: 2026-10-25 03:06:14, chạy 33 s, mã thoát 0
- Thư mục: `/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/RG`

**Lệnh**

```bash
LD_LIBRARY_PATH=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/CAMP-BIN/lib /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN/pass-bin-v3 --nodes=c1-nodes-s35.csv --path=c1-path-s35.csv --firstRun=200401 --runs=1 --bits --out=v3 && cmp v3-bits-r200401.bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/CTRY/P/k2-s4/pass1-bits-r200401.bin && echo BITS-IDENTICAL && cmp v3-strip.csv /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/CTRY/P/k2-s4/pass1-strip.csv && echo STRIP-IDENTICAL
```

**Kết quả**

```text
path c1-path-s35.csv: 2221 m = 51.1 s at 43.4 m/s on average (its speed profile), 5113 packets (one every 10 ms); altitude 100 m
nodes c1-nodes-s35.csv: 1675, CH #724
channel: free space to 100 m, then alpha 3.00, excess loss 0.00 dB, Rician K 2.0; +10 dBm, sensitivity -100 dBm, 127 B PSDU
  mission 200401: 1675/1675 nodes heard something, mean 3413 packets; CH 4219 (run 712); mean fade power 0.9999

by horizontal distance from the path (1 missions):
      dist  nodes   rx mean  run mean   done50  done100  done200  done500 done1000 done2000
   0- 100 m    253      3831       926   100.0%   100.0%   100.0%   100.0%   100.0%    31.6%
 100- 200 m    238      3763       610   100.0%   100.0%   100.0%   100.0%    98.3%    14.7%
 200- 300 m    291      3631       361   100.0%   100.0%   100.0%   100.0%    93.5%     3.1%
 300- 400 m    255      3401       191   100.0%   100.0%   100.0%   100.0%    76.9%     0.0%
 400- 500 m    224      3334       112   100.0%   100.0%   100.0%   100.0%    70.5%     0.0%
 500- 600 m    194      3175        67   100.0%   100.0%   100.0%   100.0%    44.3%     0.0%
 600- 700 m    116      2886        43   100.0%   100.0%   100.0%    94.0%     8.6%     0.0%
 700- 800 m     41      2723        26   100.0%   100.0%   100.0%    97.6%     2.4%     0.0%
 800- 900 m     33      2084        18   100.0%   100.0%   100.0%    39.4%     0.0%     0.0%
 900-1000 m     20      1759        12   100.0%   100.0%   100.0%     5.0%     0.0%     0.0%
1000-1100 m     10      1419        10   100.0%   100.0%   100.0%     0.0%     0.0%     0.0%
CH #724: rx mean 4219 of 5113, longest run mean 712
52022 CHECKS PASSED
BITS-IDENTICAL
STRIP-IDENTICAL
```
