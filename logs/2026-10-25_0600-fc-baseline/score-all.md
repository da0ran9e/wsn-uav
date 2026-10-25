# score-all

- Bắt đầu: 2026-10-25 07:11:00, chạy 284 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/l1_rank.py   --set r500 /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/ENV/r500/k8-s1,/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/ENV/r500/k12-s1,/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/ENV/r500/k16-s1   --set r200 /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/ENV/r200/k8-s1,/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/ENV/r200/k12-s1,/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/ENV/r200/k16-s1   --set r100 /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/ENV/r100/k8-s1,/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/ENV/r100/k12-s1,/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/ENV/r100/k16-s1   --set open /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/CTRY/P/k8-s1,/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/ANIM/k12-s1,/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/ANIM/k16-s1   --draws 100 --jobs 4 --methods P+prog-kin-puq-stage-zero-redir-kt,FC-puq-stage-zero-redir,DN-puq-stage-zero-redir --out /home/user/wsn-uav/logs/2026-10-25_0600-fc-baseline/l1rank/all
```

**Kết quả**

```text
r500 k8-s1: FC {'visits': 34, 'loops': 28.12, 'env': 'r500', 'tour': 1498.69225439972, 'crits': 45, 'complete': 45, 'moved': 2185.4, 'ready': [695.4290282222222, 1452.07072], 'key': 'FC/k8-s1/r500'}
r200 k12-s1: FC {'visits': 64, 'loops': 150.25, 'env': 'r200', 'tour': 4976.376712686357, 'crits': 66, 'complete': 66, 'moved': 1219.7272727272727, 'ready': [2505.093345151515, 4915.77333], 'key': 'FC/k12-s1/r200'}
r500 k8-s1: DN {'radius': 400.0, 'groups': 22, 'size': 2.05, 'visits': 22, 'loops': 24.62, 'env': 'r500', 'tour': 1319.5211567729666, 'crits': 45, 'complete': 45, 'moved': 1880.1333333333334, 'ready': [617.1349186666665, 1289.1603499999999], 'key': 'DN/k8-s1/r500'}
r500 k12-s1: FC {'visits': 49, 'loops': 34.25, 'env': 'r500', 'tour': 2227.793333917504, 'crits': 66, 'complete': 66, 'moved': 2192.409090909091, 'ready': [1012.6415925757577, 2167.31354], 'key': 'FC/k12-s1/r500'}
r500 k16-s1: FC {'visits': 69, 'loops': 45.12, 'env': 'r500', 'tour': 2838.5754693663184, 'crits': 92, 'complete': 92, 'moved': 2361.782608695652, 'ready': [1320.350334347826, 2783.9128100000003], 'key': 'FC/k16-s1/r500'}
r200 k12-s1: DN {'radius': 300.0, 'groups': 41, 'size': 1.61, 'visits': 41, 'loops': 112.25, 'env': 'r200', 'tour': 4015.8455092521517, 'crits': 66, 'complete': 66, 'moved': 1786.3636363636363, 'ready': [1964.3706212121215, 3968.1918800000003], 'key': 'DN/k12-s1/r200'}
r500 k8-s1: 8 clusters, 45 critical cells; P+prog-kin-puq-stage-zero-redir-kt 808, FC-puq-stage-zero-redir 1138, DN-puq-stage-zero-redir 1078 s
r500 k12-s1: DN {'radius': 300.0, 'groups': 41, 'size': 1.61, 'visits': 38, 'loops': 35.0, 'env': 'r500', 'tour': 2011.1061783239547, 'crits': 66, 'complete': 66, 'moved': 2159.712121212121, 'ready': [967.1104316666666, 1978.7089700000001], 'key': 'DN/k12-s1/r500'}
r500 k16-s1: DN {'radius': 400.0, 'groups': 44, 'size': 2.09, 'visits': 42, 'loops': 46.19, 'env': 'r500', 'tour': 2562.9790870661463, 'crits': 92, 'complete': 92, 'moved': 2136.836956521739, 'ready': [1237.9045348913041, 2528.7475], 'key': 'DN/k16-s1/r500'}
r200 k12-s1: 12 clusters, 66 critical cells; P+prog-kin-puq-stage-zero-redir-kt 978, FC-puq-stage-zero-redir 3288, DN-puq-stage-zero-redir 2481 s
r200 k16-s1: FC {'visits': 90, 'loops': 197.75, 'env': 'r200', 'tour': 6630.725144654897, 'crits': 92, 'complete': 92, 'moved': 1396.5108695652175, 'ready': [3264.4851011956516, 6591.23237], 'key': 'FC/k16-s1/r200'}
r500 k12-s1: 12 clusters, 66 critical cells; P+prog-kin-puq-stage-zero-redir-kt 949, FC-puq-stage-zero-redir 1451, DN-puq-stage-zero-redir 1389 s
r200 k8-s1: FC {'visits': 45, 'loops': 98.62, 'env': 'r200', 'tour': 3356.9881676411314, 'crits': 45, 'complete': 45, 'moved': 1371.7555555555555, 'ready': [1716.8940402222222, 3309.98966], 'key': 'FC/k8-s1/r200'}
r200 k16-s1: DN {'radius': 400.0, 'groups': 44, 'size': 2.09, 'visits': 44, 'loops': 144.94, 'env': 'r200', 'tour': 5566.8814211686085, 'crits': 92, 'complete': 92, 'moved': 2035.0217391304348, 'ready': [2745.8821910869565, 5522.70092], 'key': 'DN/k16-s1/r200'}
r200 k8-s1: DN {'radius': 300.0, 'groups': 27, 'size': 1.67, 'visits': 27, 'loops': 74.62, 'env': 'r200', 'tour': 2686.6597801176113, 'crits': 45, 'complete': 45, 'moved': 1773.4, 'ready': [1370.0554593333334, 2658.6716700000006], 'key': 'DN/k8-s1/r200'}
r100 k12-s1: FC {'visits': 65, 'loops': 178.38, 'env': 'r100', 'tour': 5285.108172978908, 'crits': 66, 'complete': 66, 'moved': 2463.151515151515, 'ready': [2662.663204848485, 5230.58004], 'key': 'FC/k12-s1/r100'}
r100 k12-s1: DN {'radius': 200.0, 'groups': 58, 'size': 1.14, 'visits': 58, 'loops': 168.19, 'env': 'r100', 'tour': 5078.453176121742, 'crits': 66, 'complete': 66, 'moved': 2262.3939393939395, 'ready': [2558.603621515151, 5034.2175099999995], 'key': 'DN/k12-s1/r100'}
r200 k8-s1: 8 clusters, 45 critical cells; P+prog-kin-puq-stage-zero-redir-kt 860, FC-puq-stage-zero-redir 2285, DN-puq-stage-zero-redir 1905 s
r500 k16-s1: 15 clusters, 92 critical cells; P+prog-kin-puq-stage-zero-redir-kt 1137, FC-puq-stage-zero-redir 1801, DN-puq-stage-zero-redir 1750 s
r100 k8-s1: FC {'visits': 45, 'loops': 123.25, 'env': 'r100', 'tour': 3620.8375284570293, 'crits': 45, 'complete': 45, 'moved': 2126.3555555555554, 'ready': [1866.7456120000002, 3589.2978100000005], 'key': 'FC/k8-s1/r100'}
r100 k8-s1: DN {'radius': 200.0, 'groups': 37, 'size': 1.22, 'visits': 37, 'loops': 114.19, 'env': 'r100', 'tour': 3304.9648164592636, 'crits': 45, 'complete': 45, 'moved': 2343.6666666666665, 'ready': [1678.0688633333336, 3269.04759], 'key': 'DN/k8-s1/r100'}
r100 k16-s1: FC {'visits': 92, 'loops': 244.75, 'env': 'r100', 'tour': 7295.77269844521, 'crits': 92, 'complete': 92, 'moved': 2137.195652173913, 'ready': [3619.1263867391303, 7256.56975], 'key': 'FC/k16-s1/r100'}
r100 k12-s1: 12 clusters, 66 critical cells; P+prog-kin-puq-stage-zero-redir-kt 995, FC-puq-stage-zero-redir 3460, DN-puq-stage-zero-redir 3248 s
r100 k8-s1: 8 clusters, 45 critical cells; P+prog-kin-puq-stage-zero-redir-kt 878, FC-puq-stage-zero-redir 2463, DN-puq-stage-zero-redir 2190 s
r200 k16-s1: 15 clusters, 92 critical cells; P+prog-kin-puq-stage-zero-redir-kt 1181, FC-puq-stage-zero-redir 3964, DN-puq-stage-zero-redir 3469 s
r100 k16-s1: DN {'radius': 200.0, 'groups': 80, 'size': 1.15, 'visits': 80, 'loops': 233.62, 'env': 'r100', 'tour': 6808.169121816714, 'crits': 92, 'complete': 92, 'moved': 2233.9565217391305, 'ready': [3424.3155908695644, 6761.12889], 'key': 'DN/k16-s1/r100'}
open k8-s1: FC {'visits': 15, 'loops': 6.25, 'env': 'open', 'tour': 683.4438594726341, 'crits': 45, 'complete': 45, 'moved': 2397.3555555555554, 'ready': [254.97446866666667, 589.51178], 'key': 'FC/k8-s1/open'}
open k12-s1: FC {'visits': 22, 'loops': 4.75, 'env': 'open', 'tour': 970.5985887964672, 'crits': 66, 'complete': 66, 'moved': 2562.348484848485, 'ready': [431.00874772727275, 918.0927200000001], 'key': 'FC/k12-s1/open'}
open k8-s1: DN {'radius': 300.0, 'groups': 27, 'size': 1.67, 'visits': 16, 'loops': 5.31, 'env': 'open', 'tour': 668.624439098373, 'crits': 45, 'complete': 45, 'moved': 2389.9333333333334, 'ready': [271.3156851111111, 593.6187900000001], 'key': 'DN/k8-s1/open'}
open k16-s1: FC {'visits': 29, 'loops': 7.5, 'env': 'open', 'tour': 1190.3171538501906, 'crits': 92, 'complete': 92, 'moved': 2479.0652173913045, 'ready': [513.7963463043478, 1131.90017], 'key': 'FC/k16-s1/open'}
open k12-s1: DN {'radius': 400.0, 'groups': 36, 'size': 1.83, 'visits': 20, 'loops': 9.12, 'env': 'open', 'tour': 912.6809234306481, 'crits': 66, 'complete': 66, 'moved': 2294.0454545454545, 'ready': [409.3485034848485, 830.58415], 'key': 'DN/k12-s1/open'}
open k8-s1: 8 clusters, 45 critical cells; P+prog-kin-puq-stage-zero-redir-kt 762, FC-puq-stage-zero-redir 660, DN-puq-stage-zero-redir 708 s
r100 k16-s1: 15 clusters, 92 critical cells; P+prog-kin-puq-stage-zero-redir-kt 1412, FC-puq-stage-zero-redir 4368, DN-puq-stage-zero-redir 4468 s
open k16-s1: DN {'radius': 200.0, 'groups': 80, 'size': 1.15, 'visits': 29, 'loops': 7.81, 'env': 'open', 'tour': 1133.8567213882372, 'crits': 92, 'complete': 92, 'moved': 2502.717391304348, 'ready': [536.2304619565218, 1041.18611], 'key': 'DN/k16-s1/open'}
open k12-s1: 12 clusters, 66 critical cells; P+prog-kin-puq-stage-zero-redir-kt 939, FC-puq-stage-zero-redir 815, DN-puq-stage-zero-redir 805 s
open k16-s1: 15 clusters, 92 critical cells; P+prog-kin-puq-stage-zero-redir-kt 1161, FC-puq-stage-zero-redir 949, DN-puq-stage-zero-redir 967 s
```
