# open-k16

- Bắt đầu: 2026-10-27 23:27:00, chạy 1697 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
bash logs/2026-10-27_1714-campaign4/task.sh 1 open 16
```

**Kết quả**

```text
[0 s] CP mission
  run 1600109 river-full: D 4362, 6/6 critical done, sim 39.8 s, wall 41 s, 105616 hops, 3788 MAC give-ups, 0/158 gateway pairs with q < 0.5
  run 1600114 river-full: D 5142, 6/6 critical done, sim 10.6 s, wall 4 s, 10300 hops, 352 MAC give-ups, 0/112 gateway pairs with q < 0.5
  run 1600115 river-full: D 4747, 6/6 critical done, sim 7.5 s, wall 3 s, 8739 hops, 229 MAC give-ups, 0/122 gateway pairs with q < 0.5
[344 s] LMD plan + mission
  run 1600114 river-full: D 5322, 6/6 critical done, sim 19.2 s, wall 2 s, 6553 hops, 192 MAC give-ups, 0/103 gateway pairs with q < 0.5
  run 1600115 river-full: D 4767, 6/6 critical done, sim 5.9 s, wall 2 s, 5581 hops, 132 MAC give-ups, 0/129 gateway pairs with q < 0.5
  run 1600113 river-full: D 4845, 7/7 critical done, sim 61.1 s, wall 31 s, 87627 hops, 3213 MAC give-ups, 0/141 gateway pairs with q < 0.5
[845 s] DR plan + prefly + mission
  run 1600114 river-full: D 5090, 6/6 critical done, sim 11.7 s, wall 2 s, 6145 hops, 174 MAC give-ups, 0/104 gateway pairs with q < 0.5
  run 1600115 river-full: D 5055, 6/6 critical done, sim 6.4 s, wall 4 s, 8111 hops, 212 MAC give-ups, 0/131 gateway pairs with q < 0.5
  run 1600113 river-full: D 5344, 7/7 critical done, sim 18.1 s, wall 8 s, 19092 hops, 605 MAC give-ups, 0/127 gateway pairs with q < 0.5
[1520 s] score
/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/C4/CP/open/R1/k16-s1 [ns3]: T* 872 s (sd 493), team 1 1437 s, mean River ready 701 s
/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/C4/LMD/open/R1/k16-s1 [ns3]: T* 807 s (sd 468), team 1 1394 s, mean River ready 612 s
/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/C4/DR/open/R1/k16-s1 [ns3]: T* 817 s (sd 451), team 1 1449 s, mean River ready 669 s
open k16-s1: DN {'radius': 200.0, 'groups': 80, 'size': 1.15, 'visits': 29, 'loops': 7.81, 'env': 'open', 'tour': 1133.8567213882372, 'crits': 92, 'complete': 92, 'moved': 2502.717391304348, 'ready': [536.2304619565218, 1041.18611], 'key': 'DN/k16-s1/open'}
open k16-s1: 15 clusters, 92 critical cells; P+prog-kin-puq-stage-zero-redir-kt-fcd 872, DN-puq-stage-zero-redir 967, B1 5169, B7 404 s
[1697 s] done
```
