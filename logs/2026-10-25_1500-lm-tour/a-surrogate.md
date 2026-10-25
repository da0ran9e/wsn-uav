# a-surrogate

- Bắt đầu: 2026-10-25 16:58:42, chạy 137 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2/tools`

**Lệnh**

```bash
python3 river_surrogate.py --works /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/open/k8-s1,/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/open/k12-s1,/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/open/k16-s1,/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/r500/k8-s1,/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/r500/k12-s1,/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/r500/k16-s1,/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/r200/k8-s1,/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/r200/k12-s1,/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/r200/k16-s1,/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/r100/k8-s1,/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/r100/k12-s1,/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/r100/k16-s1 --out ../docs/data/results/river-surrogate
```

**Kết quả**

```text
/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/open/k8-s1: 45 critical cells
/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/open/k12-s1: 66 critical cells
/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/open/k16-s1: 92 critical cells
/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/r500/k8-s1: 45 critical cells
/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/r500/k12-s1: 66 critical cells
/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/r500/k16-s1: 92 critical cells
/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/r200/k8-s1: 45 critical cells
/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/r200/k12-s1: 66 critical cells
/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/r200/k16-s1: 92 critical cells
/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/r100/k8-s1: 45 critical cells
/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/r100/k12-s1: 66 critical cells
/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/r100/k16-s1: 92 critical cells
812 critical cells, doneS mean 67.3 s, sd 54.8, min 1.7, max 311.3; stalled 0
expected vs ns-3 lack: cell r 1.000 (mean 2200 vs 2183), CL r 1.000 (mean 2861 vs 2857)
  leave-one-map-out    mean     MAE   42.4 s  RMSE   55.4  R2 -0.023  bias  -0.4
  leave-one-map-out    formula  MAE   22.8 s  RMSE   34.7  R2  0.599  bias  +0.4
  leave-one-map-out    linear   MAE   23.0 s  RMSE   34.7  R2  0.597  bias  +0.1
  leave-one-map-out    trees    MAE   26.1 s  RMSE   42.3  R2  0.404  bias  -3.0
  leave-one-env-out    mean     MAE   51.9 s  RMSE   64.9  R2 -0.403  bias  +0.0
  leave-one-env-out    formula  MAE   22.3 s  RMSE   33.5  R2  0.626  bias  +0.2
  leave-one-env-out    linear   MAE   24.1 s  RMSE   34.4  R2  0.606  bias  -2.2
  leave-one-env-out    trees    MAE   28.6 s  RMSE   36.7  R2  0.550  bias  +5.0
formula on all: doneS = 0.71 + 2.29 hops + 1.97 lackCell/1000 + 4.26 cluLack/1000
tree importances: cluLack 0.54, lackCell 0.24, share 0.08, ncrit 0.04, lackCL 0.03, dpath 0.02, shareLack 0.01, naxe 0.01, ring2 0.01, ring1 0.01, loss 0.00, hops 0.00
```
