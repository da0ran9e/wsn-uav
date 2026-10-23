# scenario-screen

- Bắt đầu: 2026-10-23 19:44:43, chạy 11 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2/tools`

**Lệnh**

```bash
python3 l2_screen.py ../../logs/2026-10-23_1920-factor-sweep/scenario-table.md S-s1-CHORD=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SW/K8-spine10-width0.7-bend60-bsend-span14-q400-s1/chord:kin S-s1-MEANDER=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SW/K8-spine10-width0.7-bend60-bsend-span14-q400-s1/ml:route S-s2-CHORD=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SW/K8-spine10-width0.7-bend60-bsend-span14-q400-s2/chord:kin S-s2-MEANDER=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SW/K8-spine10-width0.7-bend60-bsend-span14-q400-s2/ml:route S-s3-CHORD=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SW/K8-spine10-width0.7-bend60-bsend-span14-q400-s3/chord:kin S-s3-MEANDER=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SW/K8-spine10-width0.7-bend60-bsend-span14-q400-s3/ml:route
```

**Kết quả**

```text
| | cụm | cell | 50 m/s (s) | 45° + giao đủ (s, số cụm phải bù) | 30° + giao đủ | 60° + giao đủ | trên cụm (km) | dẫn vào/ra (km) | nối giữa cụm (km) | BS (km) | critical | khoảng cách TB (m) | p90 (m) | > 606 m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S-s1-CHORD | 11 | 703 | 1035 | 1095 (11) | 1167 (11) | 1095 (11) | 19.8 | 5.6 | 15.4 | 10.9 | 51 | 282 | 635 | 7 |
| S-s1-MEANDER | 11 | 703 | 561 | 672 (7) | 691 (6) | 672 (7) | 23.6 | 1.0 | 1.5 | 2.0 | 52 | 208 | 486 | 3 |
| S-s2-CHORD | 10 | 655 | 1014 | 1064 (9) | 1133 (9) | 1064 (9) | 18.1 | 5.1 | 13.7 | 13.8 | 51 | 362 | 678 | 8 |
| S-s2-MEANDER | 10 | 655 | 567 | 690 (6) | 717 (5) | 681 (6) | 22.5 | 1.0 | 1.8 | 3.0 | 53 | 246 | 495 | 3 |
| S-s3-CHORD | 10 | 719 | 913 | 967 (9) | 1041 (9) | 967 (9) | 18.2 | 5.1 | 13.6 | 8.8 | 54 | 289 | 673 | 8 |
| S-s3-MEANDER | 10 | 719 | 562 | 665 (9) | 683 (8) | 665 (9) | 23.6 | 1.0 | 1.4 | 2.1 | 55 | 326 | 796 | 9 |
```
