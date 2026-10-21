# lanes

- Bắt đầu: 2026-10-21 01:35:01, chạy 498 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/l2_lanes.py --maps '/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/KW/k*' --lanes 4.5 6 7.5 9 12 --out docs/data/l2diag/lanes
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
clusters kmedoids: 2 / 4 / 6 / 8  meander4.5: 3.3 / 6.2 / 9 / 12.1  meander6: 3.1 / 5.4 / 7.9 / 10.3  meander7.5: 3.1 / 5.4 / 7.6 / 10.3  meander9: 3 / 5.3 / 7.3 / 9.5  meander12: 2.9 / 5 / 6.9 / 9.5
inside   kmedoids: 4.35 / 8.64 / 12.4 / 16.7  meander4.5: 6.46 / 14.1 / 19.9 / 26.8  meander6: 6.34 / 11.9 / 16.9 / 22.3  meander7.5: 6.02 / 11.1 / 15.2 / 19.9  meander9: 5.98 / 10.5 / 13.8 / 18.6  meander12: 6.08 / 9.62 / 12.5 / 17.3
transit  kmedoids: 5.15 / 6.48 / 9.07 / 10.8  meander4.5: 6.39 / 9.77 / 13.2 / 16.1  meander6: 6.04 / 9.7 / 11.8 / 16.1  meander7.5: 5.76 / 9.98 / 12.2 / 15.1  meander9: 5.8 / 10.4 / 12 / 15.7  meander12: 5.29 / 9.41 / 11.8 / 17
cover    kmedoids: 0.545 / 0.536 / 0.546 / 0.537  meander4.5: 0.763 / 0.816 / 0.819 / 0.819  meander6: 0.749 / 0.717 / 0.711 / 0.713  meander7.5: 0.725 / 0.658 / 0.653 / 0.648  meander9: 0.721 / 0.633 / 0.608 / 0.601  meander12: 0.72 / 0.576 / 0.559 / 0.562
farthest kmedoids: 5.8 / 5.76 / 5.84 / 5.5  meander4.5: 3.35 / 2.91 / 2.86 / 3.01  meander6: 3.35 / 3.43 / 3.47 / 3.49  meander7.5: 3.45 / 3.94 / 3.83 / 3.94  meander9: 3.73 / 4.13 / 4.31 / 4.38  meander12: 3.61 / 4.82 / 5.06 / 4.93
```
