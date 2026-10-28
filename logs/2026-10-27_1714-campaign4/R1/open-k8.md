# open-k8

- Bắt đầu: 2026-10-28 04:59:07, chạy 1078 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
bash logs/2026-10-27_1714-campaign4/task.sh 1 open 8
```

**Kết quả**

```text
[0 s] CP mission
  run 800106 river-full: D 4702, 6/6 critical done, sim 21.1 s, wall 8 s, 12000 hops, 442 MAC give-ups, 0/189 gateway pairs with q < 0.5
  run 800107 river-full: D 4938, 5/5 critical done, sim 12.3 s, wall 5 s, 9386 hops, 383 MAC give-ups, 0/136 gateway pairs with q < 0.5
  run 800108 river-full: D 5226, 5/5 critical done, sim 33.7 s, wall 14 s, 31569 hops, 1067 MAC give-ups, 0/120 gateway pairs with q < 0.5
[219 s] LMD plan + mission
  run 800107 river-full: D 4967, 5/5 critical done, sim 8.9 s, wall 4 s, 7267 hops, 270 MAC give-ups, 0/137 gateway pairs with q < 0.5
  run 800106 river-full: D 4527, 6/6 critical done, sim 24.2 s, wall 8 s, 12791 hops, 436 MAC give-ups, 0/195 gateway pairs with q < 0.5
  run 800108 river-full: D 5219, 5/5 critical done, sim 33.2 s, wall 13 s, 35922 hops, 963 MAC give-ups, 0/121 gateway pairs with q < 0.5
[519 s] score
/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/C4/CP/open/R1/k8-s1 [ns3]: T* 672 s (sd 519), team 1 784 s, mean River ready 361 s
/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/C4/LMD/open/R1/k8-s1 [ns3]: T* 633 s (sd 499), team 1 698 s, mean River ready 302 s
open k8-s1: DN {'radius': 300.0, 'groups': 27, 'size': 1.67, 'visits': 16, 'loops': 5.31, 'env': 'open', 'tour': 668.624439098373, 'crits': 45, 'complete': 45, 'moved': 2389.9333333333334, 'ready': [271.3156851111111, 593.6187900000001], 'key': 'DN/k8-s1/open'}
open k8-s1: 8 clusters, 45 critical cells; P+prog-kin-puq-stage-zero-redir-kt-fcd 672, DN-puq-stage-zero-redir 708, B1 2926, B7 322 s
[582 s] done
[582 s] DR plan + prefly + mission
dtsp-n + river: C7 150 deg r 127.5 m, C3 60 deg r 63.7 m, C1 0 deg r 63.7 m, C6 60 deg r 127.5 m, C2 150 deg r 63.7 m, C4 60 deg r 127.5 m, C5 30 deg r 63.7 m, C8 60 deg r 127.5 m
  run 800106 river-full: D 6098, 6/6 critical done, sim 9.3 s, wall 3 s, 5843 hops, 278 MAC give-ups, 0/161 gateway pairs with q < 0.5
  run 800107 river-full: D 5514, 5/5 critical done, sim 4.0 s, wall 2 s, 4289 hops, 190 MAC give-ups, 0/135 gateway pairs with q < 0.5
  run 800108 river-full: D 6403, 5/5 critical done, sim 15.0 s, wall 5 s, 11799 hops, 283 MAC give-ups, 0/119 gateway pairs with q < 0.5
/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/C4/DR/open/R1/k8-s1 [ns3]: T* 783 s (sd 555), team 1 1066 s, mean River ready 504 s
[1078 s] done (DR)
```
