# screen

- Bắt đầu: 2026-10-23 18:57:46, chạy 15 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2/tools`

**Lệnh**

```bash
python3 l2_screen.py ../../logs/2026-10-23_1855-meander-wins/screen-table.md  b200w1-CHORD=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SCR/b200w1/chord:kin b200w1-MEANDER=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SCR/b200w1/ml:route b90w1-CHORD=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SCR/b90w1/chord:kin b90w1-MEANDER=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SCR/b90w1/ml:route b300w08-CHORD=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SCR/b300w08/chord:kin b300w08-MEANDER=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SCR/b300w08/ml:route b120w07-CHORD=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SCR/b120w07/chord:kin b120w07-MEANDER=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SCR/b120w07/ml:route
```

**Kết quả**

```text
| | cụm | cell | 50 m/s (s) | 45° + giao đủ (s, số cụm phải bù) | 30° + giao đủ | critical | khoảng cách TB (m) | p90 (m) | > 606 m |
|---|---|---|---|---|---|---|---|---|---|
| b200w1-CHORD | 11 | 716 | 925 | 992 (11) | 1067 (11) | 53 | 274 | 648 | 6 |
| b200w1-MEANDER | 11 | 716 | 944 | 980 (5) | 1014 (5) | 57 | 237 | 544 | 3 |
| b90w1-CHORD | 8 | 677 | 763 | 788 (7) | 860 (7) | 46 | 377 | 891 | 9 |
| b90w1-MEANDER | 8 | 677 | 890 | 906 (1) | 931 (1) | 50 | 250 | 516 | 2 |
| b300w08-CHORD | 11 | 764 | 942 | 1004 (11) | 1083 (11) | 51 | 343 | 701 | 10 |
| b300w08-MEANDER | 11 | 764 | 912 | 999 (6) | 1036 (6) | 56 | 242 | 513 | 3 |
| b120w07-CHORD | 13 | 847 | 1224 | 1287 (11) | 1395 (11) | 62 | 256 | 569 | 6 |
| b120w07-MEANDER | 13 | 847 | 1110 | 1123 (6) | 1154 (5) | 66 | 209 | 389 | 1 |
```
