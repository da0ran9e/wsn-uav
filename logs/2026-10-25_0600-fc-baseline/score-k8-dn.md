# score-k8-dn

- Bắt đầu: 2026-10-25 06:26:22, chạy 72 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/l1_rank.py --set r500 /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/ENV/r500/k8-s1 --set r200 /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/ENV/r200/k8-s1 --set r100 /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/ENV/r100/k8-s1 --set open /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/CTRY/P/k8-s1 --draws 100 --jobs 4 --methods P+prog-kin-puq-stage-zero-redir-kt,FC-puq-stage-zero-redir,DN-puq-stage-zero-redir --out logs/2026-10-25_0600-fc-baseline/l1rank/k8
```

**Kết quả**

```text
r100 k8-s1: FC {'visits': 45, 'loops': 123.25, 'env': 'r100', 'tour': 3620.8375284570293, 'crits': 45, 'complete': 45, 'moved': 2126.3555555555554, 'ready': [1866.7456120000002, 3589.2978100000005], 'key': 'FC/k8-s1/r100'}
r200 k8-s1: FC {'visits': 45, 'loops': 98.62, 'env': 'r200', 'tour': 3356.9881676411314, 'crits': 45, 'complete': 45, 'moved': 1371.7555555555555, 'ready': [1716.8940402222222, 3309.98966], 'key': 'FC/k8-s1/r200'}
r500 k8-s1: FC {'visits': 34, 'loops': 28.12, 'env': 'r500', 'tour': 1498.69225439972, 'crits': 45, 'complete': 45, 'moved': 2185.4, 'ready': [695.4290282222222, 1452.07072], 'key': 'FC/k8-s1/r500'}
open k8-s1: FC {'visits': 15, 'loops': 6.25, 'env': 'open', 'tour': 683.4438594726341, 'crits': 45, 'complete': 45, 'moved': 2397.3555555555554, 'ready': [254.97446866666667, 589.51178], 'key': 'FC/k8-s1/open'}
r100 k8-s1: DN {'radius': 200.0, 'groups': 37, 'size': 1.22, 'visits': 37, 'loops': 114.19, 'env': 'r100', 'tour': 3304.9648164592636, 'crits': 45, 'complete': 45, 'moved': 2343.6666666666665, 'ready': [1678.0688633333336, 3269.04759], 'key': 'DN/k8-s1/r100'}
r200 k8-s1: DN {'radius': 300.0, 'groups': 27, 'size': 1.67, 'visits': 27, 'loops': 74.62, 'env': 'r200', 'tour': 2686.6597801176113, 'crits': 45, 'complete': 45, 'moved': 1773.4, 'ready': [1370.0554593333334, 2658.6716700000006], 'key': 'DN/k8-s1/r200'}
r500 k8-s1: DN {'radius': 400.0, 'groups': 22, 'size': 2.05, 'visits': 22, 'loops': 24.62, 'env': 'r500', 'tour': 1319.5211567729666, 'crits': 45, 'complete': 45, 'moved': 1880.1333333333334, 'ready': [617.1349186666665, 1289.1603499999999], 'key': 'DN/k8-s1/r500'}
open k8-s1: DN {'radius': 300.0, 'groups': 27, 'size': 1.67, 'visits': 16, 'loops': 5.31, 'env': 'open', 'tour': 668.624439098373, 'crits': 45, 'complete': 45, 'moved': 2389.9333333333334, 'ready': [271.3156851111111, 593.6187900000001], 'key': 'DN/k8-s1/open'}
r100 k8-s1: 8 clusters, 45 critical cells; P+prog-kin-puq-stage-zero-redir-kt 878, FC-puq-stage-zero-redir 2463, DN-puq-stage-zero-redir 2190 s
r200 k8-s1: 8 clusters, 45 critical cells; P+prog-kin-puq-stage-zero-redir-kt 860, FC-puq-stage-zero-redir 2285, DN-puq-stage-zero-redir 1905 s
r500 k8-s1: 8 clusters, 45 critical cells; P+prog-kin-puq-stage-zero-redir-kt 808, FC-puq-stage-zero-redir 1138, DN-puq-stage-zero-redir 1078 s
open k8-s1: 8 clusters, 45 critical cells; P+prog-kin-puq-stage-zero-redir-kt 762, FC-puq-stage-zero-redir 660, DN-puq-stage-zero-redir 708 s
```
