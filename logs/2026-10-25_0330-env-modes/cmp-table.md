# cmp-table

- Bắt đầu: 2026-10-25 04:28:02, chạy 28 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/ns3_cmp.py logs/2026-10-25_0330-env-modes/cmp-table-out.md open=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/CTRY/P/k8-s1:kin:logs/2026-10-25_0330-env-modes/l1rank/open r500=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/ENV/r500/k8-s1:kin:logs/2026-10-25_0330-env-modes/l1rank/r500 r200=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/ENV/r200/k8-s1:kin:logs/2026-10-25_0330-env-modes/l1rank/r200 r100=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/ENV/r100/k8-s1:kin:logs/2026-10-25_0330-env-modes/l1rank/r100
```

**Kết quả**

```text
| bản đồ | phương án | tour 45° (s) | critical | rời cụm TB (s) | River xong TB / p90 / max (s) | sẵn sàng TB (s) | đủ 12 manh mối | T* TB (s) |
|---|---|---|---|---|---|---|---|---|
| k8-s1 | open | 782 | 45 | 328 | 8 / 18 / 35 | 336 | 100% | 762 |
| k8-s1 | r500 | 782 | 45 | 328 | 54 / 103 / 160 | 382 | 100% | 808 |
| k8-s1 | r200 | 782 | 45 | 328 | 99 / 208 / 216 | 427 | 100% | 860 |
| k8-s1 | r100 | 782 | 45 | 328 | 121 / 233 / 270 | 450 | 100% | 878 |
| | critical chung | 45 / 45 / 45 / 45 / 45 | | | | | | |
```
