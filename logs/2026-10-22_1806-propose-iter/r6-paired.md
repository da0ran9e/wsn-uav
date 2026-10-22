# Vòng 6: chấm lại vòng 4-5 có ghép cặp thế giới (tên thư mục = tên bản đồ)

- Bắt đầu: 2026-10-22 19:48:53, chạy 54 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/l1_rank.py --set kmedoids '/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/PR/KD/*' --set swath '/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/PR/SW/*' --set kmedoids0 '/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/PR/KD0/*' --set swath0 '/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/PR/SW0/*' --draws 100 --methods P+prog-kin-puq-stage-zero-redir,P+prog-skin-puq-stage-zero-redir,B4-skin-puq-stage-zero-redir,B7 --jobs 4 --out /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/IT/r6
```

**Kết quả**

```text
swath k4-s2: 4 clusters, 23 critical cells; P+prog-kin-puq-stage-zero-redir 617, P+prog-skin-puq-stage-zero-redir 569, B4-skin-puq-stage-zero-redir 607, B7 283 s
kmedoids k4-s2: 4 clusters, 24 critical cells; P+prog-kin-puq-stage-zero-redir 535, P+prog-skin-puq-stage-zero-redir 535, B4-skin-puq-stage-zero-redir 551, B7 290 s
kmedoids k6-s9: 6 clusters, 35 critical cells; P+prog-kin-puq-stage-zero-redir 725, P+prog-skin-puq-stage-zero-redir 725, B4-skin-puq-stage-zero-redir 744, B7 321 s
kmedoids k8-s10: 8 clusters, 44 critical cells; P+prog-kin-puq-stage-zero-redir 810, P+prog-skin-puq-stage-zero-redir 825, B4-skin-puq-stage-zero-redir 801, B7 338 s
kmedoids0 k4-s2: 4 clusters, 24 critical cells; P+prog-kin-puq-stage-zero-redir 536, P+prog-skin-puq-stage-zero-redir 536, B4-skin-puq-stage-zero-redir 573, B7 290 s
swath k6-s9: 6 clusters, 39 critical cells; P+prog-kin-puq-stage-zero-redir 846, P+prog-skin-puq-stage-zero-redir 719, B4-skin-puq-stage-zero-redir 731, B7 326 s
swath k8-s10: 8 clusters, 43 critical cells; P+prog-kin-puq-stage-zero-redir 957, P+prog-skin-puq-stage-zero-redir 797, B4-skin-puq-stage-zero-redir 825, B7 345 s
swath0 k4-s2: 4 clusters, 23 critical cells; P+prog-kin-puq-stage-zero-redir 619, P+prog-skin-puq-stage-zero-redir 577, B4-skin-puq-stage-zero-redir 665, B7 283 s
kmedoids0 k6-s9: 6 clusters, 35 critical cells; P+prog-kin-puq-stage-zero-redir 730, P+prog-skin-puq-stage-zero-redir 730, B4-skin-puq-stage-zero-redir 793, B7 321 s
kmedoids0 k8-s10: 8 clusters, 44 critical cells; P+prog-kin-puq-stage-zero-redir 805, P+prog-skin-puq-stage-zero-redir 827, B4-skin-puq-stage-zero-redir 784, B7 338 s
swath0 k6-s9: 6 clusters, 39 critical cells; P+prog-kin-puq-stage-zero-redir 851, P+prog-skin-puq-stage-zero-redir 724, B4-skin-puq-stage-zero-redir 746, B7 326 s
swath0 k8-s10: 8 clusters, 43 critical cells; P+prog-kin-puq-stage-zero-redir 974, P+prog-skin-puq-stage-zero-redir 818, B4-skin-puq-stage-zero-redir 890, B7 345 s
```
