# Vòng 5: Axe gồm cả gói phát sát mép cụm, 3 bản đồ

- Bắt đầu: 2026-10-22 19:44:47, chạy 22 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/l1_rank.py --set kmedoids '/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/IT/KDN-*' --set swath '/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/IT/SWN-*' --draws 100 --methods P+prog-kin-puq-stage-zero-redir,P+prog-skin-puq-stage-zero-redir,B4-kin-puq-stage-zero-redir,B4-skin-puq-stage-zero-redir,B7 --jobs 4 --out /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/IT/r5
```

**Kết quả**

```text
kmedoids KDN-k4-s2: 4 clusters, 24 critical cells; P+prog-kin-puq-stage-zero-redir 572, P+prog-skin-puq-stage-zero-redir 572, B4-kin-puq-stage-zero-redir 599, B4-skin-puq-stage-zero-redir 599 s
swath SWN-k4-s2: 4 clusters, 23 critical cells; P+prog-kin-puq-stage-zero-redir 591, P+prog-skin-puq-stage-zero-redir 538, B4-kin-puq-stage-zero-redir 593, B4-skin-puq-stage-zero-redir 548 s
kmedoids KDN-k6-s9: 6 clusters, 35 critical cells; P+prog-kin-puq-stage-zero-redir 745, P+prog-skin-puq-stage-zero-redir 745, B4-kin-puq-stage-zero-redir 843, B4-skin-puq-stage-zero-redir 843 s
kmedoids KDN-k8-s10: 8 clusters, 44 critical cells; P+prog-kin-puq-stage-zero-redir 741, P+prog-skin-puq-stage-zero-redir 704, B4-kin-puq-stage-zero-redir 769, B4-skin-puq-stage-zero-redir 756 s
swath SWN-k6-s9: 6 clusters, 39 critical cells; P+prog-kin-puq-stage-zero-redir 788, P+prog-skin-puq-stage-zero-redir 647, B4-kin-puq-stage-zero-redir 819, B4-skin-puq-stage-zero-redir 676 s
swath SWN-k8-s10: 8 clusters, 43 critical cells; P+prog-kin-puq-stage-zero-redir 920, P+prog-skin-puq-stage-zero-redir 783, B4-kin-puq-stage-zero-redir 953, B4-skin-puq-stage-zero-redir 811 s
```
