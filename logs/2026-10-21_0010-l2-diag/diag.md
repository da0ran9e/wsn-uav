# diag

- Bắt đầu: 2026-10-21 01:29:05, chạy 236 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/l2_diag.py --set kmedoids '/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/KW/k*' --set meander '/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MW/k*' --set subch '/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/SW/k*' --out docs/data/l2diag/diag --figs docs/figures --map k6-s4
```

**Kết quả**

```text
kmedoids k2-s10
kmedoids k2-s11
kmedoids k2-s20
kmedoids k2-s23
kmedoids k2-s25
kmedoids k2-s3
kmedoids k2-s4
kmedoids k2-s5
kmedoids k2-s8
kmedoids k2-s9
kmedoids k4-s1
kmedoids k4-s11
kmedoids k4-s12
kmedoids k4-s13
kmedoids k4-s16
kmedoids k4-s2
kmedoids k4-s20
kmedoids k4-s21
kmedoids k4-s5
kmedoids k4-s9
kmedoids k6-s11
kmedoids k6-s12
kmedoids k6-s13
kmedoids k6-s15
kmedoids k6-s16
kmedoids k6-s17
kmedoids k6-s2
kmedoids k6-s20
kmedoids k6-s4
kmedoids k6-s9
kmedoids k8-s1
kmedoids k8-s10
kmedoids k8-s11
kmedoids k8-s2
kmedoids k8-s4
kmedoids k8-s5
kmedoids k8-s6
kmedoids k8-s7
kmedoids k8-s8
kmedoids k8-s9
meander k2-s10
meander k2-s11
meander k2-s20
meander k2-s23
meander k2-s25
meander k2-s3
meander k2-s4
meander k2-s5
meander k2-s8
meander k2-s9
meander k4-s1
meander k4-s11
meander k4-s12
meander k4-s13
meander k4-s16
meander k4-s2
meander k4-s20
meander k4-s21
meander k4-s5
meander k4-s9
meander k6-s11
meander k6-s12
meander k6-s13
meander k6-s15
meander k6-s16
meander k6-s17
meander k6-s2
meander k6-s20
meander k6-s4
meander k6-s9
meander k8-s1
meander k8-s10
meander k8-s11
meander k8-s2
meander k8-s4
meander k8-s5
meander k8-s6
meander k8-s7
meander k8-s8
meander k8-s9
subch k2-s10
subch k2-s11
subch k2-s20
subch k2-s23
subch k2-s25
subch k2-s3
subch k2-s4
subch k2-s5
subch k2-s8
subch k2-s9
subch k4-s1
subch k4-s11
subch k4-s12
subch k4-s13
subch k4-s16
subch k4-s2
subch k4-s20
subch k4-s21
subch k4-s5
subch k4-s9
subch k6-s11
subch k6-s12
subch k6-s13
subch k6-s15
subch k6-s16
subch k6-s17
subch k6-s2
subch k6-s20
subch k6-s4
subch k6-s9
subch k8-s1
subch k8-s10
subch k8-s11
subch k8-s2
subch k8-s4
subch k8-s5
subch k8-s6
subch k8-s7
subch k8-s8
subch k8-s9
clusters          kmedoids: 2 / 4 / 6 / 8  meander: 3.3 / 6.2 / 9 / 12.1  subch: 2.7 / 6.4 / 8.3 / 11.5
crit              kmedoids: 13.5 / 26.9 / 39.9 / 50.1  meander: 16.5 / 30.6 / 47.3 / 59  subch: 12.2 / 25 / 37.4 / 46.7
cells             kmedoids: 152 / 309 / 451 / 611  meander: 152 / 309 / 451 / 611  subch: 152 / 309 / 451 / 611
latency_back      kmedoids: 213 / 369 / 512 / 682  meander: 285 / 529 / 738 / 950  subch: 232 / 480 / 632 / 807
latency_pass      kmedoids: 111 / 224 / 321 / 426  meander: 166 / 341 / 481 / 646  subch: 127 / 276 / 377 / 509
latency_transit   kmedoids: 45.3 / 85.9 / 122 / 183  meander: 66.9 / 122 / 179 / 220  subch: 65.5 / 134 / 180 / 222
latency_ret       kmedoids: 56.8 / 59.4 / 69.5 / 72.9  meander: 52.7 / 66.2 / 78.4 / 85  subch: 40.2 / 70.3 / 74.5 / 76.3
short_back        kmedoids: 211 / 356 / 498 / 647  meander: 276 / 504 / 680 / 908  subch: 231 / 432 / 577 / 754
short_pass        kmedoids: 111 / 224 / 321 / 426  meander: 166 / 341 / 481 / 646  subch: 127 / 276 / 377 / 509
short_transit     kmedoids: 58.4 / 101 / 136 / 179  meander: 77.4 / 129 / 170 / 217  subch: 69 / 119 / 174 / 211
short_ret         kmedoids: 42.3 / 30.7 / 41.9 / 42.7  meander: 33 / 34.2 / 28.7 / 45.3  subch: 35.5 / 36.2 / 26 / 33.7
axeMean           kmedoids: 4.27e+03 / 4.32e+03 / 4.12e+03 / 4.16e+03  meander: 3.98e+03 / 4.44e+03 / 4.34e+03 / 4.41e+03  subch: 3.54e+03 / 3.16e+03 / 3.37e+03 / 3.28e+03
axeFull           kmedoids: 0.55 / 0.625 / 0.5 / 0.55  meander: 0.35 / 0.617 / 0.593 / 0.6  subch: 0.258 / 0.111 / 0.152 / 0.15
Dmean             kmedoids: 4.27e+03 / 4.32e+03 / 4.12e+03 / 4.16e+03  meander: 3.98e+03 / 4.44e+03 / 4.34e+03 / 4.41e+03  subch: 3.54e+03 / 3.16e+03 / 3.37e+03 / 3.28e+03
Dsum              kmedoids: 8.53e+03 / 1.73e+04 / 2.47e+04 / 3.33e+04  meander: 1.29e+04 / 2.74e+04 / 3.86e+04 / 5.25e+04  subch: 9.26e+03 / 2.01e+04 / 2.78e+04 / 3.76e+04
reach             kmedoids: 0.887 / 0.881 / 0.909 / 0.909  meander: 0.895 / 0.855 / 0.862 / 0.861  subch: 0.928 / 0.947 / 0.946 / 0.95
reach50           kmedoids: 0.996 / 0.985 / 0.994 / 0.995  meander: 0.988 / 0.99 / 0.986 / 0.98  subch: 0.99 / 0.995 / 0.997 / 0.998
reach90           kmedoids: 0.565 / 0.574 / 0.646 / 0.654  meander: 0.633 / 0.488 / 0.512 / 0.522  subch: 0.736 / 0.81 / 0.79 / 0.813
allDirect         kmedoids: 0.13 / 0.138 / 0.0972 / 0.107  meander: 0.165 / 0.281 / 0.223 / 0.228  subch: 0.0546 / 0.0173 / 0.0371 / 0.041
clueW             kmedoids: 0.766 / 0.772 / 0.771 / 0.779  meander: 0.738 / 0.791 / 0.767 / 0.781  subch: 0.716 / 0.694 / 0.718 / 0.714
clueW50           kmedoids: 0.898 / 0.897 / 0.907 / 0.921  meander: 0.855 / 0.917 / 0.9 / 0.906  subch: 0.838 / 0.823 / 0.856 / 0.853
riverAll          kmedoids: 198 / 346 / 470 / 632  meander: 255 / 485 / 680 / 881  subch: 214 / 412 / 567 / 733
```
