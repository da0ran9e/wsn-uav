# screen

- Bắt đầu: 2026-10-21 03:27:44, chạy 777 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/l2_lanes.py --maps '/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/KW/k*' --lanes 4.5 6 7.5 9 --frags 0.25 0.5 --out docs/data/l2diag/screen
```

**Kết quả**

```text
k2-s10
k2-s11
k2-s20
k2-s23
k2-s25
k2-s3
k2-s4
k2-s5
k2-s8
k2-s9
k4-s1
k4-s11
k4-s12
k4-s13
k4-s16
k4-s2
k4-s20
k4-s21
k4-s5
k4-s9
k6-s11
k6-s12
k6-s13
k6-s15
k6-s16
k6-s17
k6-s2
k6-s20
k6-s4
k6-s9
k8-s1
k8-s10
k8-s11
k8-s2
k8-s4
k8-s5
k8-s6
k8-s7
k8-s8
k8-s9
clusters kmedoids: 2 / 4 / 6 / 8  meander4.5: 3.3 / 6.2 / 9 / 12.1  meander6: 3.1 / 5.4 / 7.9 / 10.3  meander7.5: 3.1 / 5.4 / 7.6 / 10.3  meander9: 3 / 5.3 / 7.3 / 9.5  meander4.5f0.5: 2.5 / 5.8 / 7.6 / 10.5  meander6f0.5: 2.8 / 5 / 7.4 / 9.9  meander7.5f0.5: 2.9 / 5.1 / 7.2 / 9.7  meander9f0.5: 2.9 / 5.2 / 7.1 / 9.4
inside   kmedoids: 4.35 / 8.64 / 12.4 / 16.7  meander4.5: 6.46 / 14.1 / 19.9 / 26.8  meander6: 6.34 / 11.9 / 16.9 / 22.3  meander7.5: 6.02 / 11.1 / 15.2 / 19.9  meander9: 5.98 / 10.5 / 13.8 / 18.6  meander4.5f0.5: 5.17 / 12.4 / 17.4 / 25  meander6f0.5: 5.6 / 10.7 / 16.2 / 21.6  meander7.5f0.5: 5.76 / 10.4 / 14.6 / 19.2  meander9f0.5: 5.91 / 9.99 / 13.5 / 18.2
transit  kmedoids: 5.15 / 6.48 / 9.07 / 10.8  meander4.5: 6.39 / 9.77 / 13.2 / 16.1  meander6: 6.04 / 9.7 / 11.8 / 16.1  meander7.5: 5.76 / 9.98 / 12.2 / 15.1  meander9: 5.8 / 10.4 / 12 / 15.7  meander4.5f0.5: 5.88 / 9.69 / 12.9 / 16.8  meander6f0.5: 5.27 / 9.15 / 11.4 / 14.9  meander7.5f0.5: 5.67 / 9.27 / 12 / 14.5  meander9f0.5: 5.81 / 9.6 / 12.1 / 15.6
total    kmedoids: 9.5 / 15.1 / 21.5 / 27.5  meander4.5: 12.8 / 23.9 / 33.1 / 42.9  meander6: 12.4 / 21.6 / 28.7 / 38.4  meander7.5: 11.8 / 21 / 27.4 / 35  meander9: 11.8 / 20.9 / 25.8 / 34.3  meander4.5f0.5: 11.1 / 22.1 / 30.3 / 41.9  meander6f0.5: 10.9 / 19.9 / 27.7 / 36.5  meander7.5f0.5: 11.4 / 19.7 / 26.6 / 33.7  meander9f0.5: 11.7 / 19.6 / 25.5 / 33.8
withLeadskmedoids: 10.5 / 17.2 / 24.6 / 31.6  meander4.5: 14.5 / 27.1 / 37.7 / 49.1  meander6: 14 / 24.3 / 32.8 / 43.6  meander7.5: 13.4 / 23.8 / 31.2 / 40.2  meander9: 13.3 / 23.6 / 29.5 / 39.1  meander4.5f0.5: 12.3 / 25 / 34.2 / 47.2  meander6f0.5: 12.3 / 22.4 / 31.5 / 41.5  meander7.5f0.5: 12.9 / 22.3 / 30.2 / 38.7  meander9f0.5: 13.2 / 22.2 / 29.2 / 38.6
cover    kmedoids: 0.545 / 0.536 / 0.546 / 0.537  meander4.5: 0.763 / 0.816 / 0.819 / 0.819  meander6: 0.749 / 0.717 / 0.711 / 0.713  meander7.5: 0.725 / 0.658 / 0.653 / 0.648  meander9: 0.721 / 0.633 / 0.608 / 0.601  meander4.5f0.5: 0.632 / 0.739 / 0.738 / 0.77  meander6f0.5: 0.683 / 0.665 / 0.692 / 0.693  meander7.5f0.5: 0.705 / 0.644 / 0.636 / 0.628  meander9f0.5: 0.711 / 0.626 / 0.598 / 0.592
farthest kmedoids: 5.8 / 5.76 / 5.84 / 5.5  meander4.5: 3.35 / 2.91 / 2.86 / 3.01  meander6: 3.35 / 3.43 / 3.47 / 3.49  meander7.5: 3.45 / 3.94 / 3.83 / 3.94  meander9: 3.73 / 4.13 / 4.31 / 4.38  meander4.5f0.5: 4.65 / 3.48 / 3.6 / 3.38  meander6f0.5: 3.91 / 3.98 / 3.74 / 3.78  meander7.5f0.5: 3.76 / 4.2 / 4.06 / 4.19  meander9f0.5: 3.94 / 4.32 / 4.52 / 4.52
```
