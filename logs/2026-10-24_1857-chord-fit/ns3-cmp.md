# ns3-cmp

- Bắt đầu: 2026-10-24 19:19:12, chạy 24 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2/tools`

**Lệnh**

```bash
python3 ns3_cmp.py ../../logs/2026-10-24_1857-chord-fit/ns3-cmp-table.md 'A CHORD-T=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/NS159/A/k8-s*:kin:../../logs/2026-10-24_1857-chord-fit/l1rank/A' 'B vừa đủ=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/NS159/B/k8-s*:kin:../../logs/2026-10-24_1857-chord-fit/l1rank/B' 'D vừa đủ + River=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/NS159/D/k8-s*:kin:../../logs/2026-10-24_1857-chord-fit/l1rank/D'
```

**Kết quả**

```text
| bản đồ | phương án | tour 45° (s) | critical | rời cụm TB (s) | River xong TB / p90 / max (s) | sẵn sàng TB (s) | đủ 12 manh mối | T* TB (s) |
|---|---|---|---|---|---|---|---|---|
| k8-s1 | A CHORD-T | 782 | 45 | 328 | 8 / 17 / 40 | 336 | 100% | 762 |
| k8-s1 | B vừa đủ | 712 | 45 | 320 | 9 / 25 / 38 | 329 | 100% | 760 |
| k8-s1 | D vừa đủ + River | 795 | 45 | 337 | 8 / 16 / 49 | 345 | 100% | 784 |
| | critical chung | 45 / 45 / 45 / 45 | | | | | | |
| k8-s2 | A CHORD-T | 718 | 45 | 330 | 7 / 16 / 27 | 337 | 100% | 744 |
| k8-s2 | B vừa đủ | 708 | 45 | 330 | 7 / 16 / 21 | 337 | 100% | 745 |
| k8-s2 | D vừa đủ + River | 780 | 45 | 331 | 8 / 18 / 39 | 339 | 100% | 719 |
| | critical chung | 45 / 45 / 45 / 45 | | | | | | |
| k8-s3 | A CHORD-T | 808 | 51 | 354 | 7 / 12 / 24 | 360 | 100% | 770 |
| k8-s3 | B vừa đủ | 823 | 51 | 363 | 6 / 14 / 23 | 369 | 100% | 779 |
| k8-s3 | D vừa đủ + River | 895 | 51 | 388 | 8 / 17 / 33 | 396 | 100% | 781 |
| | critical chung | 51 / 51 / 51 / 51 | | | | | | |
```
