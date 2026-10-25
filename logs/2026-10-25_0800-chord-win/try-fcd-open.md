# try-fcd-open

- Bắt đầu: 2026-10-25 09:06:36, chạy 130 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/l1_rank.py --set open /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/ANIM/k12-s1,/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/ANIM/k16-s1 --draws 100 --jobs 2 --methods P+prog-kin-puq-stage-zero-redir-kt,P+prog-kin-puq-stage-zero-redir-kt-fcd,FC-puq-stage-zero-redir,DN-puq-stage-zero-redir --out logs/2026-10-25_0800-chord-win/l1rank/fcd-open
```

**Kết quả**

```text
open k12-s1: FC {'visits': 22, 'loops': 4.75, 'env': 'open', 'tour': 970.5985887964672, 'crits': 66, 'complete': 66, 'moved': 2562.348484848485, 'ready': [431.00874772727275, 918.0927200000001], 'key': 'FC/k12-s1/open'}
open k16-s1: FC {'visits': 29, 'loops': 7.5, 'env': 'open', 'tour': 1190.3171538501906, 'crits': 92, 'complete': 92, 'moved': 2479.0652173913045, 'ready': [513.7963463043478, 1131.90017], 'key': 'FC/k16-s1/open'}
open k12-s1: DN {'radius': 400.0, 'groups': 36, 'size': 1.83, 'visits': 20, 'loops': 9.12, 'env': 'open', 'tour': 912.6809234306481, 'crits': 66, 'complete': 66, 'moved': 2294.0454545454545, 'ready': [409.3485034848485, 830.58415], 'key': 'DN/k12-s1/open'}
open k16-s1: DN {'radius': 200.0, 'groups': 80, 'size': 1.15, 'visits': 29, 'loops': 7.81, 'env': 'open', 'tour': 1133.8567213882372, 'crits': 92, 'complete': 92, 'moved': 2502.717391304348, 'ready': [536.2304619565218, 1041.18611], 'key': 'DN/k16-s1/open'}
open k12-s1: 12 clusters, 66 critical cells; P+prog-kin-puq-stage-zero-redir-kt 939, P+prog-kin-puq-stage-zero-redir-kt-fcd 686, FC-puq-stage-zero-redir 815, DN-puq-stage-zero-redir 805 s
open k16-s1: 15 clusters, 92 critical cells; P+prog-kin-puq-stage-zero-redir-kt 1161, P+prog-kin-puq-stage-zero-redir-kt-fcd 863, FC-puq-stage-zero-redir 949, DN-puq-stage-zero-redir 967 s
```
