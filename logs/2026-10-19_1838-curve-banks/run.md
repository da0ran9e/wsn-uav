# run

**Lệnh**

```bash
python3 tools/curve_banks.py --works /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/W/k4 /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/W/k6 /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/W/k8 --bin /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN --scratch /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/CURV --out docs/data/curve/banks --figs docs/figures
```

**Kết quả**

```text
k4: 4 clusters
k6: 6 clusters
/home/user/wsn-uav/uav-l2/tools/curve_banks.py:64: RuntimeWarning: Mean of empty slice
  spill=len(river - band) / max(len(river), 1), offset=float(np.nanmean(off))), band
k8: 8 clusters
angle banks  n  coverage  pathCoverage  spill  offset  river/band
  180 parallel  17  0.916  0.916  0.196  1.001  1.145
  180 local     17  0.960  0.921  0.188  0.988  1.186
  180 failed 1
  135 parallel  17  0.892  0.892  0.179  0.983  1.088
  135 local     17  0.964  0.874  0.195  0.921  1.201
  135 failed 1
  100 parallel  17  0.837  0.837  0.111  0.781  0.944
  100 local     17  0.962  0.846  0.187  0.940  1.186
  100 failed 1
   70 parallel  17  0.776  0.776  0.085  0.633  0.850
   70 local     17  0.976  0.825  0.172  0.876  1.181
   70 failed 1
```
