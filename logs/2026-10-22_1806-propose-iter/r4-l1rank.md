# Vòng 4: kiểm tra chéo k4-s2, k6-s9 (k-medoids vs SWATH-K)

- Bắt đầu: 2026-10-22 19:36:21, chạy 13 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/l1_rank.py --set kmedoids '/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/IT/KD-k4-s2,/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/IT/KD-k6-s9' --set swath '/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/IT/SW-k4-s2,/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/IT/SW-k6-s9' --draws 100 --methods P+prog-kin-puq-stage-zero-redir,P+prog-skin-puq-stage-zero-redir,B4-kin-puq-stage-zero-redir,B4-skin-puq-stage-zero-redir,B7 --jobs 4 --out /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/IT/r4
```

**Kết quả**

```text
swath SW-k4-s2: 4 clusters, 23 critical cells; P+prog-kin-puq-stage-zero-redir 631, P+prog-skin-puq-stage-zero-redir 573, B4-kin-puq-stage-zero-redir 678, B4-skin-puq-stage-zero-redir 625 s
kmedoids KD-k4-s2: 4 clusters, 24 critical cells; P+prog-kin-puq-stage-zero-redir 537, P+prog-skin-puq-stage-zero-redir 537, B4-kin-puq-stage-zero-redir 628, B4-skin-puq-stage-zero-redir 628 s
kmedoids KD-k6-s9: 6 clusters, 35 critical cells; P+prog-kin-puq-stage-zero-redir 755, P+prog-skin-puq-stage-zero-redir 755, B4-kin-puq-stage-zero-redir 898, B4-skin-puq-stage-zero-redir 898 s
swath SW-k6-s9: 6 clusters, 39 critical cells; P+prog-kin-puq-stage-zero-redir 868, P+prog-skin-puq-stage-zero-redir 723, B4-kin-puq-stage-zero-redir 922, B4-skin-puq-stage-zero-redir 779 s
```
