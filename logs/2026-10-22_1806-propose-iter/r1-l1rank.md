# Vòng 1: T* trên k8-s10

- Bắt đầu: 2026-10-22 18:14:58, chạy 20 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/l1_rank.py --set kmedoids '/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/IT/KC-k8-s10' --set meanderK '/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/IT/MK-k8-s10' --draws 100 --methods P+prog-latency-puq-stage-zero-redir,P+prog-kin-puq-stage-zero-redir,B4-kin-puq-stage-zero-redir,B7 --jobs 4 --out /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/IT/r1
```

**Kết quả**

```text
kmedoids KC-k8-s10: 8 clusters, 45 critical cells; P+prog-latency-puq-stage-zero-redir 782, P+prog-kin-puq-stage-zero-redir 812, B4-kin-puq-stage-zero-redir 872, B7 350 s
meanderK MK-k8-s10: 8 clusters, 57 critical cells; P+prog-latency-puq-stage-zero-redir 792, P+prog-kin-puq-stage-zero-redir 857, B4-kin-puq-stage-zero-redir 943, B7 337 s
```
