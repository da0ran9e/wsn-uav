# score-k8

- Bắt đầu: 2026-10-25 05:54:00, chạy 47 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/l1_rank.py --set r500 /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/ENV/r500/k8-s1 --set r200 /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/ENV/r200/k8-s1 --set r100 /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/ENV/r100/k8-s1 --set open /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/CTRY/P/k8-s1 --draws 100 --jobs 4 --methods P+prog-kin-puq-stage-zero-redir-kt,FC-puq-stage-zero-redir --out logs/2026-10-25_0600-fc-baseline/l1rank/k8
```

**Kết quả**

```text
r100 k8-s1: FC {'env': 'r100', 'tour': 3620.8375284570293, 'visits': 45, 'loops': 123.25, 'crits': 45, 'complete': 45, 'moved': 2126.3555555555554}
r200 k8-s1: FC {'env': 'r200', 'tour': 3356.9881676411314, 'visits': 45, 'loops': 98.62, 'crits': 45, 'complete': 45, 'moved': 1371.7555555555555}
r500 k8-s1: FC {'env': 'r500', 'tour': 1498.69225439972, 'visits': 34, 'loops': 28.12, 'crits': 45, 'complete': 45, 'moved': 2185.4}
open k8-s1: FC {'env': 'open', 'tour': 683.4438594726341, 'visits': 15, 'loops': 6.25, 'crits': 45, 'complete': 45, 'moved': 2397.3555555555554}
r100 k8-s1: 8 clusters, 45 critical cells; P+prog-kin-puq-stage-zero-redir-kt 878, FC-puq-stage-zero-redir 2463 s
open k8-s1: 8 clusters, 45 critical cells; P+prog-kin-puq-stage-zero-redir-kt 762, FC-puq-stage-zero-redir 660 s
r500 k8-s1: 8 clusters, 45 critical cells; P+prog-kin-puq-stage-zero-redir-kt 808, FC-puq-stage-zero-redir 1138 s
r200 k8-s1: 8 clusters, 45 critical cells; P+prog-kin-puq-stage-zero-redir-kt 860, FC-puq-stage-zero-redir 2285 s
```
