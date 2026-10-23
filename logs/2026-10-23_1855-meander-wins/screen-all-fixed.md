# screen-all-fixed

- Bắt đầu: 2026-10-23 19:06:52, chạy 28 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2/tools`

**Lệnh**

```bash
python3 l2_screen.py ../../logs/2026-10-23_1855-meander-wins/screen-all-fixed-table.md k8s1-CHORD=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/CK9/k8-s1:kin k8s1-MEANDER=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/ML/k8-s1:route b200w1-CHORD=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SCR/b200w1/chord:kin b200w1-MEANDER=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SCR/b200w1/ml:route b90w1-CHORD=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SCR/b90w1/chord:kin b90w1-MEANDER=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SCR/b90w1/ml:route b300w08-CHORD=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SCR/b300w08/chord:kin b300w08-MEANDER=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SCR/b300w08/ml:route b120w07-s1-CHORD=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SCR/b120w07-s1/chord:kin b120w07-s1-MEANDER=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SCR/b120w07-s1/ml:route b120w07-s3-CHORD=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SCR/b120w07-s3/chord:kin b120w07-s3-MEANDER=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SCR/b120w07-s3/ml:route b120w07-s5-CHORD=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SCR/b120w07-s5/chord:kin b120w07-s5-MEANDER=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SCR/b120w07-s5/ml:route b120w07-s6-CHORD=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SCR/b120w07-s6/chord:kin b120w07-s6-MEANDER=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SCR/b120w07-s6/ml:route
```

**Kết quả**

```text
| | cụm | cell | 50 m/s (s) | 45° + giao đủ (s, số cụm phải bù) | 30° + giao đủ | trên cụm (km) | dẫn vào/ra (km) | nối giữa cụm (km) | BS (km) | critical | khoảng cách TB (m) | p90 (m) | > 606 m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| k8s1-CHORD | 9 | 617 | 743 | 790 (9) | 854 (9) | 17.8 | 4.6 | 9.1 | 5.6 | 47 | 346 | 805 | 11 |
| k8s1-MEANDER | 9 | 617 | 731 | 791 (5) | 840 (5) | 18.8 | 2.0 | 6.2 | 9.5 | 45 | 275 | 568 | 4 |
| b200w1-CHORD | 11 | 716 | 925 | 992 (11) | 1067 (11) | 19.2 | 5.6 | 13.3 | 8.1 | 53 | 274 | 648 | 6 |
| b200w1-MEANDER | 11 | 716 | 784 | 830 (5) | 865 (5) | 24.0 | 1.5 | 4.1 | 9.5 | 57 | 237 | 544 | 3 |
| b90w1-CHORD | 8 | 677 | 763 | 788 (7) | 860 (7) | 15.2 | 4.1 | 10.6 | 8.3 | 46 | 377 | 891 | 9 |
| b90w1-MEANDER | 8 | 677 | 770 | 790 (2) | 814 (2) | 18.5 | 1.0 | 1.5 | 17.5 | 50 | 250 | 516 | 2 |
| b300w08-CHORD | 11 | 764 | 942 | 1004 (11) | 1083 (11) | 19.8 | 5.6 | 14.1 | 7.7 | 51 | 343 | 701 | 10 |
| b300w08-MEANDER | 11 | 764 | 752 | 864 (6) | 899 (6) | 24.1 | 1.5 | 3.9 | 8.0 | 56 | 242 | 513 | 3 |
| b120w07-s1-CHORD | 13 | 847 | 1224 | 1287 (11) | 1395 (11) | 24.5 | 6.6 | 22.3 | 7.8 | 62 | 256 | 569 | 6 |
| b120w07-s1-MEANDER | 13 | 847 | 910 | 945 (7) | 977 (6) | 27.6 | 1.5 | 4.6 | 11.7 | 66 | 209 | 389 | 1 |
| b120w07-s3-CHORD | 12 | 830 | 1147 | 1206 (12) | 1292 (12) | 21.3 | 6.1 | 16.5 | 13.5 | 58 | 303 | 705 | 9 |
| b120w07-s3-MEANDER | 12 | 830 | 950 | 1004 (4) | 1041 (4) | 26.0 | 1.5 | 7.3 | 12.7 | 59 | 260 | 633 | 7 |
| b120w07-s5-CHORD | 10 | 853 | 950 | 981 (9) | 1045 (9) | 19.2 | 5.1 | 12.0 | 11.2 | 57 | 374 | 721 | 13 |
| b120w07-s5-MEANDER | 10 | 853 | 653 | 714 (6) | 735 (6) | 21.1 | 1.0 | 1.7 | 8.8 | 59 | 300 | 592 | 6 |
| b120w07-s6-CHORD | 13 | 834 | 1147 | 1232 (13) | 1329 (13) | 22.2 | 6.6 | 20.8 | 7.7 | 61 | 258 | 487 | 3 |
| b120w07-s6-MEANDER | 13 | 834 | 821 | 867 (9) | 900 (9) | 26.2 | 1.5 | 3.4 | 10.0 | 65 | 242 | 493 | 2 |
```
