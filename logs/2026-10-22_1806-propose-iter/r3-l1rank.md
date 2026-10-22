# Vòng 3: SWATH-K luồng 6/7/8 cell, k8-s10

- Bắt đầu: 2026-10-22 19:14:20, chạy 13 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/l1_rank.py --set swath6 '/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/IT/SW-k8-s10' --set swath7 '/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/IT/SW7-k8-s10' --set swath8 '/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/IT/SW8-k8-s10' --draws 100 --methods P+prog-skin-puq-stage-zero-redir,B4-skin-puq-stage-zero-redir,B7 --jobs 4 --out /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/IT/r3
```

**Kết quả**

```text
swath6 SW-k8-s10: 8 clusters, 43 critical cells; P+prog-skin-puq-stage-zero-redir 744, B4-skin-puq-stage-zero-redir 787, B7 337 s
swath7 SW7-k8-s10: 8 clusters, 47 critical cells; P+prog-skin-puq-stage-zero-redir 751, B4-skin-puq-stage-zero-redir 860, B7 339 s
swath8 SW8-k8-s10: 8 clusters, 48 critical cells; P+prog-skin-puq-stage-zero-redir 859, B4-skin-puq-stage-zero-redir 984, B7 364 s
```
