# score-part2

- Bắt đầu: 2026-10-26 04:44:04, chạy 85 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/l1_rank.py --set open /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/open/k8-s1,/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/open/k12-s1,/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/open/k16-s1 --set r500 /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/r500/k8-s1,/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/r500/k12-s1,/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/r500/k16-s1 --set r200 /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/r200/k8-s1,/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/r200/k12-s1,/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/r200/k16-s1 --set r100 /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/r100/k8-s1,/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/r100/k12-s1,/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/r100/k16-s1 --draws 100 --jobs 4        --methods Pd+prog-kin-puq-stage-zero-redir-kt-fcd --out /home/user/wsn-uav/logs/2026-10-26_0900-baselines/l1rank/part2
```

**Kết quả**

```text
open k8-s1: 8 clusters, 45 critical cells; Pd+prog-kin-puq-stage-zero-redir-kt-fcd 647 s
r500 k12-s1: 12 clusters, 66 critical cells; Pd+prog-kin-puq-stage-zero-redir-kt-fcd 950 s
open k12-s1: 12 clusters, 66 critical cells; Pd+prog-kin-puq-stage-zero-redir-kt-fcd 686 s
open k16-s1: 15 clusters, 92 critical cells; Pd+prog-kin-puq-stage-zero-redir-kt-fcd 863 s
r500 k8-s1: 8 clusters, 45 critical cells; Pd+prog-kin-puq-stage-zero-redir-kt-fcd 806 s
r500 k16-s1: 15 clusters, 92 critical cells; Pd+prog-kin-puq-stage-zero-redir-kt-fcd 1115 s
r200 k8-s1: 8 clusters, 45 critical cells; Pd+prog-kin-puq-stage-zero-redir-kt-fcd 850 s
r200 k12-s1: 12 clusters, 66 critical cells; Pd+prog-kin-puq-stage-zero-redir-kt-fcd 990 s
r100 k8-s1: 8 clusters, 45 critical cells; Pd+prog-kin-puq-stage-zero-redir-kt-fcd 875 s
r200 k16-s1: 15 clusters, 92 critical cells; Pd+prog-kin-puq-stage-zero-redir-kt-fcd 1192 s
r100 k12-s1: 12 clusters, 66 critical cells; Pd+prog-kin-puq-stage-zero-redir-kt-fcd 990 s
r100 k16-s1: 15 clusters, 92 critical cells; Pd+prog-kin-puq-stage-zero-redir-kt-fcd 1334 s
```
