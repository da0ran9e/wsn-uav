# ns3-cmp

- Bắt đầu: 2026-10-24 09:40:49, chạy 39 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2/tools`

**Lệnh**

```bash
python3 ns3_cmp.py ../../logs/2026-10-24_0714-ns3-given-ch/ns3-cmp-table.md 'CHORD-T uốn=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/NS157/chordB/k8-s*:kin:../../logs/2026-10-24_0714-ns3-given-ch/l1rank/chordB' 'MEANDER luồng 8=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/NS157/ml8/k8-s*:route:../../logs/2026-10-24_0714-ns3-given-ch/l1rank/ml8' 'MEANDER luồng 10=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/NS157/ml10/k8-s*:route:../../logs/2026-10-24_0714-ns3-given-ch/l1rank/ml10'
```

**Kết quả**

```text
| bản đồ | phương án | tour 45° (s) | critical | rời cụm TB (s) | River xong TB / p90 / max (s) | sẵn sàng TB (s) | đủ 12 manh mối | T* TB (s) |
|---|---|---|---|---|---|---|---|---|
| k8-s1 | CHORD-T uốn | 604 | 36 | 261 | 10 / 26 / 32 | 272 | 100% | 662 |
| k8-s1 | MEANDER luồng 8 | 534 | 37 | 270 | 45 / 72 / 75 | 315 | 95% | 763 |
| k8-s1 | MEANDER luồng 10 | 532 | 39 | 370 | 38 / 77 / 104 | 408 | 100% | 833 |
| | critical chung | 36 / 36 / 37 / 39 | | | | | | |
| k8-s2 | CHORD-T uốn | 531 | 37 | 251 | 16 / 41 / 70 | 267 | 100% | 632 |
| k8-s2 | MEANDER luồng 8 | 576 | 38 | 319 | 47 / 100 / 195 | 365 | 100% | 721 |
| k8-s2 | MEANDER luồng 10 | 590 | 38 | 302 | 52 / 112 / 171 | 355 | 92% | 723 |
| | critical chung | 37 / 37 / 38 / 38 | | | | | | |
| k8-s3 | CHORD-T uốn | 576 | 44 | 267 | 27 / 54 / 99 | 294 | 100% | 692 |
| k8-s3 | MEANDER luồng 8 | 632 | 43 | 322 | 48 / 148 / 166 | 370 | 100% | 749 |
| k8-s3 | MEANDER luồng 10 | 531 | 43 | 327 | 41 / 91 / 136 | 368 | 100% | 812 |
| | critical chung | 39 / 44 / 43 / 43 | | | | | | |
```
