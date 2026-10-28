# open-k12

- Bắt đầu: 2026-10-28 02:32:21, chạy 631 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
bash logs/2026-10-27_1714-campaign4/task.sh 1 open 12
```

**Kết quả**

```text
[0 s] CP mission
  run 1200111 river-full: D 5200, 7/7 critical done, sim 12.9 s, wall 10 s, 19872 hops, 602 MAC give-ups, 0/153 gateway pairs with q < 0.5
  run 1200110 river-full: D 4629, 6/6 critical done, sim 14.0 s, wall 11 s, 16400 hops, 767 MAC give-ups, 0/181 gateway pairs with q < 0.5
  run 1200112 river-full: D 4749, 5/5 critical done, sim 14.6 s, wall 8 s, 16006 hops, 580 MAC give-ups, 0/145 gateway pairs with q < 0.5
[44 s] LMD plan + mission
  run 1200110 river-full: D 4670, 6/6 critical done, sim 14.0 s, wall 9 s, 15651 hops, 602 MAC give-ups, 0/181 gateway pairs with q < 0.5
  run 1200111 river-full: D 4669, 7/7 critical done, sim 33.1 s, wall 16 s, 31792 hops, 1093 MAC give-ups, 0/153 gateway pairs with q < 0.5
  run 1200112 river-full: D 4729, 5/5 critical done, sim 37.0 s, wall 25 s, 54915 hops, 1713 MAC give-ups, 0/163 gateway pairs with q < 0.5
[523 s] score
/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/C4/CP/open/R1/k12-s1 [ns3]: T* 742 s (sd 375), team 1 1292 s, mean River ready 566 s
/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/C4/LMD/open/R1/k12-s1 [ns3]: T* 721 s (sd 376), team 1 1085 s, mean River ready 473 s
open k12-s1: DN {'radius': 400.0, 'groups': 36, 'size': 1.83, 'visits': 20, 'loops': 9.12, 'env': 'open', 'tour': 912.6809234306481, 'crits': 66, 'complete': 66, 'moved': 2294.0454545454545, 'ready': [409.3485034848485, 830.58415], 'key': 'DN/k12-s1/open'}
open k12-s1: 12 clusters, 66 critical cells; P+prog-kin-puq-stage-zero-redir-kt-fcd 742, DN-puq-stage-zero-redir 805, B1 4168, B7 402 s
[631 s] done
```
