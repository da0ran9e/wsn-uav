# try-fcd-k8

- Bắt đầu: 2026-10-25 09:05:11, chạy 33 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/l1_rank.py --set open /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/CTRY/P/k8-s1 --set r200 /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/ENV/r200/k8-s1 --draws 100 --jobs 2 --methods P+prog-kin-puq-stage-zero-redir-kt,P+prog-kin-puq-stage-zero-redir-kt-fcd,FC-puq-stage-zero-redir --out logs/2026-10-25_0800-chord-win/l1rank/fcd-k8
```

**Kết quả**

```text
r200 k8-s1: FC {'visits': 45, 'loops': 98.62, 'env': 'r200', 'tour': 3356.9881676411314, 'crits': 45, 'complete': 45, 'moved': 1371.7555555555555, 'ready': [1716.8940402222222, 3309.98966], 'key': 'FC/k8-s1/r200'}
open k8-s1: FC {'visits': 15, 'loops': 6.25, 'env': 'open', 'tour': 683.4438594726341, 'crits': 45, 'complete': 45, 'moved': 2397.3555555555554, 'ready': [254.97446866666667, 589.51178], 'key': 'FC/k8-s1/open'}
r200 k8-s1: 8 clusters, 45 critical cells; P+prog-kin-puq-stage-zero-redir-kt 860, P+prog-kin-puq-stage-zero-redir-kt-fcd 860, FC-puq-stage-zero-redir 2285 s
open k8-s1: 8 clusters, 45 critical cells; P+prog-kin-puq-stage-zero-redir-kt 762, P+prog-kin-puq-stage-zero-redir-kt-fcd 647, FC-puq-stage-zero-redir 660 s
```
