# Vòng 2: T* trên k8-s10 (k-medoids vs SWATH-K, critical cell theo lân cận thật)

- Bắt đầu: 2026-10-22 18:41:38, chạy 16 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/l1_rank.py --set kmedoids '/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/IT/KD-k8-s10' --set swath '/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/IT/SW-k8-s10' --draws 100 --methods P+prog-kin-puq-stage-zero-redir,P+prog-skin-puq-stage-zero-redir,B4-skin-puq-stage-zero-redir,B4-kin-puq-stage-zero-redir,B7 --jobs 4 --out /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/IT/r2
```

**Kết quả**

```text
swath SW-k8-s10: 8 clusters, 43 critical cells; P+prog-kin-puq-stage-zero-redir 884, P+prog-skin-puq-stage-zero-redir 744, B4-skin-puq-stage-zero-redir 787, B4-kin-puq-stage-zero-redir 921 s
kmedoids KD-k8-s10: 8 clusters, 44 critical cells; P+prog-kin-puq-stage-zero-redir 789, P+prog-skin-puq-stage-zero-redir 816, B4-skin-puq-stage-zero-redir 857, B4-kin-puq-stage-zero-redir 849 s
```
