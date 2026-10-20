# sens2

- Bắt đầu: 2026-10-20 21:31:54, chạy 922 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
bash ../logs/2026-10-20_1834-l1-mission/sens.sh && python3 tools/l1_sens.py --runs base dim64 dim256 rho0 rho05 m105 m693 --data docs/data/l1rank/sens --figs docs/figures --out docs/data/l1rank/sens-table.csv
```

**Kết quả**

```text
base k2-s10: 2 clusters, 11 critical cells; P+prog-latency-puq-stage-zero 400, P-latency-puq-stage-zero 401, B4-latency-puq-stage-zero 401, B1 776 s
base k2-s11: 2 clusters, 16 critical cells; P+prog-latency-puq-stage-zero 458, P-latency-puq-stage-zero 465, B4-latency-puq-stage-zero 481, B1 1064 s
base k2-s23: 2 clusters, 11 critical cells; P+prog-latency-puq-stage-zero 397, P-latency-puq-stage-zero 408, B4-latency-puq-stage-zero 401, B1 942 s
base k2-s20: 2 clusters, 15 critical cells; P+prog-latency-puq-stage-zero 437, P-latency-puq-stage-zero 445, B4-latency-puq-stage-zero 510, B1 1037 s
base k2-s25: 2 clusters, 12 critical cells; P+prog-latency-puq-stage-zero 419, P-latency-puq-stage-zero 427, B4-latency-puq-stage-zero 425, B1 750 s
base k2-s3: 2 clusters, 12 critical cells; P+prog-latency-puq-stage-zero 435, P-latency-puq-stage-zero 443, B4-latency-puq-stage-zero 487, B1 746 s
base k2-s4: 2 clusters, 14 critical cells; P+prog-latency-puq-stage-zero 397, P-latency-puq-stage-zero 415, B4-latency-puq-stage-zero 434, B1 766 s
base k2-s5: 2 clusters, 15 critical cells; P+prog-latency-puq-stage-zero 401, P-latency-puq-stage-zero 392, B4-latency-puq-stage-zero 435, B1 1026 s
base k2-s8: 2 clusters, 14 critical cells; P+prog-latency-puq-stage-zero 406, P-latency-puq-stage-zero 417, B4-latency-puq-stage-zero 423, B1 939 s
base k2-s9: 2 clusters, 15 critical cells; P+prog-latency-puq-stage-zero 419, P-latency-puq-stage-zero 429, B4-latency-puq-stage-zero 444, B1 953 s
base k4-s1: 4 clusters, 25 critical cells; P+prog-latency-puq-stage-zero 481, P-latency-puq-stage-zero 477, B4-latency-puq-stage-zero 583, B1 1559 s
base k4-s11: 4 clusters, 31 critical cells; P+prog-latency-puq-stage-zero 557, P-latency-puq-stage-zero 564, B4-latency-puq-stage-zero 575, B1 1887 s
base k4-s12: 4 clusters, 26 critical cells; P+prog-latency-puq-stage-zero 609, P-latency-puq-stage-zero 628, B4-latency-puq-stage-zero 711, B1 1754 s
base k4-s13: 4 clusters, 25 critical cells; P+prog-latency-puq-stage-zero 553, P-latency-puq-stage-zero 558, B4-latency-puq-stage-zero 573, B1 1527 s
base k4-s16: 4 clusters, 30 critical cells; P+prog-latency-puq-stage-zero 602, P-latency-puq-stage-zero 613, B4-latency-puq-stage-zero 643, B1 1963 s
base k4-s2: 4 clusters, 27 critical cells; P+prog-latency-puq-stage-zero 523, P-latency-puq-stage-zero 538, B4-latency-puq-stage-zero 543, B1 1595 s
base k4-s20: 4 clusters, 21 critical cells; P+prog-latency-puq-stage-zero 557, P-latency-puq-stage-zero 567, B4-latency-puq-stage-zero 576, B1 1380 s
base k4-s21: 4 clusters, 29 critical cells; P+prog-latency-puq-stage-zero 529, P-latency-puq-stage-zero 536, B4-latency-puq-stage-zero 581, B1 1769 s
base k4-s5: 4 clusters, 24 critical cells; P+prog-latency-puq-stage-zero 544, P-latency-puq-stage-zero 557, B4-latency-puq-stage-zero 548, B1 1531 s
base k4-s9: 4 clusters, 31 critical cells; P+prog-latency-puq-stage-zero 616, P-latency-puq-stage-zero 643, B4-latency-puq-stage-zero 755, B1 1793 s
base k6-s11: 6 clusters, 34 critical cells; P+prog-latency-puq-stage-zero 636, P-latency-puq-stage-zero 635, B4-latency-puq-stage-zero 706, B1 2186 s
base k6-s12: 6 clusters, 36 critical cells; P+prog-latency-puq-stage-zero 733, P-latency-puq-stage-zero 736, B4-latency-puq-stage-zero 743, B1 2268 s
base k6-s13: 6 clusters, 43 critical cells; P+prog-latency-puq-stage-zero 601, P-latency-puq-stage-zero 607, B4-latency-puq-stage-zero 634, B1 2744 s
base k6-s15: 6 clusters, 40 critical cells; P+prog-latency-puq-stage-zero 700, P-latency-puq-stage-zero 704, B4-latency-puq-stage-zero 757, B1 2570 s
base k6-s16: 6 clusters, 40 critical cells; P+prog-latency-puq-stage-zero 748, P-latency-puq-stage-zero 758, B4-latency-puq-stage-zero 829, B1 2553 s
base k6-s17: 6 clusters, 36 critical cells; P+prog-latency-puq-stage-zero 675, P-latency-puq-stage-zero 675, B4-latency-puq-stage-zero 692, B1 2646 s
base k6-s2: 6 clusters, 44 critical cells; P+prog-latency-puq-stage-zero 662, P-latency-puq-stage-zero 675, B4-latency-puq-stage-zero 737, B1 2769 s
base k6-s20: 6 clusters, 43 critical cells; P+prog-latency-puq-stage-zero 705, P-latency-puq-stage-zero 712, B4-latency-puq-stage-zero 805, B1 2404 s
base k6-s4: 6 clusters, 45 critical cells; P+prog-latency-puq-stage-zero 761, P-latency-puq-stage-zero 770, B4-latency-puq-stage-zero 846, B1 3114 s
base k6-s9: 6 clusters, 38 critical cells; P+prog-latency-puq-stage-zero 695, P-latency-puq-stage-zero 706, B4-latency-puq-stage-zero 760, B1 2483 s
base k8-s1: 8 clusters, 49 critical cells; P+prog-latency-puq-stage-zero 775, P-latency-puq-stage-zero 786, B4-latency-puq-stage-zero 909, B1 3115 s
base k8-s10: 8 clusters, 45 critical cells; P+prog-latency-puq-stage-zero 784, P-latency-puq-stage-zero 810, B4-latency-puq-stage-zero 714, B1 2686 s
base k8-s2: 8 clusters, 50 critical cells; P+prog-latency-puq-stage-zero 713, P-latency-puq-stage-zero 721, B4-latency-puq-stage-zero 759, B1 3238 s
base k8-s11: 8 clusters, 51 critical cells; P+prog-latency-puq-stage-zero 758, P-latency-puq-stage-zero 757, B4-latency-puq-stage-zero 784, B1 3093 s
base k8-s5: 8 clusters, 47 critical cells; P+prog-latency-puq-stage-zero 858, P-latency-puq-stage-zero 870, B4-latency-puq-stage-zero 849, B1 3008 s
base k8-s4: 8 clusters, 52 critical cells; P+prog-latency-puq-stage-zero 622, P-latency-puq-stage-zero 636, B4-latency-puq-stage-zero 714, B1 3524 s
base k8-s6: 8 clusters, 54 critical cells; P+prog-latency-puq-stage-zero 674, P-latency-puq-stage-zero 680, B4-latency-puq-stage-zero 817, B1 3210 s
base k8-s7: 8 clusters, 55 critical cells; P+prog-latency-puq-stage-zero 805, P-latency-puq-stage-zero 805, B4-latency-puq-stage-zero 823, B1 3638 s
base k8-s8: 8 clusters, 48 critical cells; P+prog-latency-puq-stage-zero 786, P-latency-puq-stage-zero 792, B4-latency-puq-stage-zero 845, B1 2874 s
base k8-s9: 8 clusters, 50 critical cells; P+prog-latency-puq-stage-zero 762, P-latency-puq-stage-zero 776, B4-latency-puq-stage-zero 920, B1 2893 s
dim64 k2-s10: 2 clusters, 11 critical cells; P+prog-latency-puq-stage-zero 451, P-latency-puq-stage-zero 451, B4-latency-puq-stage-zero 463, B1 776 s
dim64 k2-s11: 2 clusters, 16 critical cells; P+prog-latency-puq-stage-zero 551, P-latency-puq-stage-zero 539, B4-latency-puq-stage-zero 536, B1 1064 s
dim64 k2-s20: 2 clusters, 15 critical cells; P+prog-latency-puq-stage-zero 502, P-latency-puq-stage-zero 507, B4-latency-puq-stage-zero 599, B1 1037 s
dim64 k2-s23: 2 clusters, 11 critical cells; P+prog-latency-puq-stage-zero 455, P-latency-puq-stage-zero 442, B4-latency-puq-stage-zero 459, B1 942 s
dim64 k2-s25: 2 clusters, 12 critical cells; P+prog-latency-puq-stage-zero 461, P-latency-puq-stage-zero 462, B4-latency-puq-stage-zero 478, B1 750 s
dim64 k2-s3: 2 clusters, 12 critical cells; P+prog-latency-puq-stage-zero 541, P-latency-puq-stage-zero 554, B4-latency-puq-stage-zero 630, B1 746 s
dim64 k2-s4: 2 clusters, 14 critical cells; P+prog-latency-puq-stage-zero 488, P-latency-puq-stage-zero 493, B4-latency-puq-stage-zero 520, B1 766 s
dim64 k2-s5: 2 clusters, 15 critical cells; P+prog-latency-puq-stage-zero 459, P-latency-puq-stage-zero 455, B4-latency-puq-stage-zero 516, B1 1026 s
dim64 k2-s8: 2 clusters, 14 critical cells; P+prog-latency-puq-stage-zero 466, P-latency-puq-stage-zero 489, B4-latency-puq-stage-zero 477, B1 939 s
dim64 k2-s9: 2 clusters, 15 critical cells; P+prog-latency-puq-stage-zero 474, P-latency-puq-stage-zero 473, B4-latency-puq-stage-zero 534, B1 953 s
dim64 k4-s1: 4 clusters, 25 critical cells; P+prog-latency-puq-stage-zero 537, P-latency-puq-stage-zero 552, B4-latency-puq-stage-zero 738, B1 1559 s
dim64 k4-s11: 4 clusters, 31 critical cells; P+prog-latency-puq-stage-zero 624, P-latency-puq-stage-zero 631, B4-latency-puq-stage-zero 652, B1 1887 s
dim64 k4-s12: 4 clusters, 26 critical cells; P+prog-latency-puq-stage-zero 702, P-latency-puq-stage-zero 703, B4-latency-puq-stage-zero 834, B1 1754 s
dim64 k4-s13: 4 clusters, 25 critical cells; P+prog-latency-puq-stage-zero 682, P-latency-puq-stage-zero 698, B4-latency-puq-stage-zero 662, B1 1527 s
dim64 k4-s16: 4 clusters, 30 critical cells; P+prog-latency-puq-stage-zero 734, P-latency-puq-stage-zero 740, B4-latency-puq-stage-zero 835, B1 1963 s
dim64 k4-s2: 4 clusters, 27 critical cells; P+prog-latency-puq-stage-zero 625, P-latency-puq-stage-zero 635, B4-latency-puq-stage-zero 611, B1 1595 s
dim64 k4-s20: 4 clusters, 21 critical cells; P+prog-latency-puq-stage-zero 662, P-latency-puq-stage-zero 686, B4-latency-puq-stage-zero 699, B1 1380 s
dim64 k4-s21: 4 clusters, 29 critical cells; P+prog-latency-puq-stage-zero 599, P-latency-puq-stage-zero 598, B4-latency-puq-stage-zero 713, B1 1769 s
dim64 k4-s5: 4 clusters, 24 critical cells; P+prog-latency-puq-stage-zero 623, P-latency-puq-stage-zero 635, B4-latency-puq-stage-zero 668, B1 1531 s
dim64 k4-s9: 4 clusters, 31 critical cells; P+prog-latency-puq-stage-zero 832, P-latency-puq-stage-zero 884, B4-latency-puq-stage-zero 1060, B1 1793 s
dim64 k6-s11: 6 clusters, 34 critical cells; P+prog-latency-puq-stage-zero 753, P-latency-puq-stage-zero 759, B4-latency-puq-stage-zero 842, B1 2186 s
dim64 k6-s12: 6 clusters, 36 critical cells; P+prog-latency-puq-stage-zero 931, P-latency-puq-stage-zero 943, B4-latency-puq-stage-zero 1104, B1 2268 s
dim64 k6-s13: 6 clusters, 43 critical cells; P+prog-latency-puq-stage-zero 809, P-latency-puq-stage-zero 810, B4-latency-puq-stage-zero 974, B1 2744 s
dim64 k6-s15: 6 clusters, 40 critical cells; P+prog-latency-puq-stage-zero 888, P-latency-puq-stage-zero 889, B4-latency-puq-stage-zero 971, B1 2570 s
dim64 k6-s16: 6 clusters, 40 critical cells; P+prog-latency-puq-stage-zero 925, P-latency-puq-stage-zero 930, B4-latency-puq-stage-zero 1001, B1 2553 s
dim64 k6-s17: 6 clusters, 36 critical cells; P+prog-latency-puq-stage-zero 896, P-latency-puq-stage-zero 899, B4-latency-puq-stage-zero 1050, B1 2646 s
dim64 k6-s2: 6 clusters, 44 critical cells; P+prog-latency-puq-stage-zero 861, P-latency-puq-stage-zero 863, B4-latency-puq-stage-zero 951, B1 2769 s
dim64 k6-s20: 6 clusters, 43 critical cells; P+prog-latency-puq-stage-zero 946, P-latency-puq-stage-zero 954, B4-latency-puq-stage-zero 1085, B1 2404 s
dim64 k6-s4: 6 clusters, 45 critical cells; P+prog-latency-puq-stage-zero 1039, P-latency-puq-stage-zero 1043, B4-latency-puq-stage-zero 1122, B1 3114 s
dim64 k6-s9: 6 clusters, 38 critical cells; P+prog-latency-puq-stage-zero 879, P-latency-puq-stage-zero 916, B4-latency-puq-stage-zero 1028, B1 2483 s
dim64 k8-s10: 8 clusters, 45 critical cells; P+prog-latency-puq-stage-zero 1032, P-latency-puq-stage-zero 1037, B4-latency-puq-stage-zero 1066, B1 2686 s
dim64 k8-s1: 8 clusters, 49 critical cells; P+prog-latency-puq-stage-zero 940, P-latency-puq-stage-zero 945, B4-latency-puq-stage-zero 1150, B1 3115 s
dim64 k8-s11: 8 clusters, 51 critical cells; P+prog-latency-puq-stage-zero 938, P-latency-puq-stage-zero 949, B4-latency-puq-stage-zero 1037, B1 3093 s
dim64 k8-s2: 8 clusters, 50 critical cells; P+prog-latency-puq-stage-zero 925, P-latency-puq-stage-zero 924, B4-latency-puq-stage-zero 958, B1 3238 s
dim64 k8-s5: 8 clusters, 47 critical cells; P+prog-latency-puq-stage-zero 1057, P-latency-puq-stage-zero 1070, B4-latency-puq-stage-zero 1150, B1 3008 s
dim64 k8-s4: 8 clusters, 52 critical cells; P+prog-latency-puq-stage-zero 795, P-latency-puq-stage-zero 801, B4-latency-puq-stage-zero 899, B1 3524 s
dim64 k8-s6: 8 clusters, 54 critical cells; P+prog-latency-puq-stage-zero 817, P-latency-puq-stage-zero 820, B4-latency-puq-stage-zero 1011, B1 3210 s
dim64 k8-s7: 8 clusters, 55 critical cells; P+prog-latency-puq-stage-zero 1076, P-latency-puq-stage-zero 1082, B4-latency-puq-stage-zero 1170, B1 3638 s
dim64 k8-s8: 8 clusters, 48 critical cells; P+prog-latency-puq-stage-zero 938, P-latency-puq-stage-zero 943, B4-latency-puq-stage-zero 1083, B1 2874 s
dim64 k8-s9: 8 clusters, 50 critical cells; P+prog-latency-puq-stage-zero 981, P-latency-puq-stage-zero 981, B4-latency-puq-stage-zero 1256, B1 2893 s
dim256 k2-s10: 2 clusters, 11 critical cells; P+prog-latency-puq-stage-zero 369, P-latency-puq-stage-zero 372, B4-latency-puq-stage-zero 360, B1 776 s
dim256 k2-s11: 2 clusters, 16 critical cells; P+prog-latency-puq-stage-zero 388, P-latency-puq-stage-zero 415, B4-latency-puq-stage-zero 425, B1 1064 s
dim256 k2-s20: 2 clusters, 15 critical cells; P+prog-latency-puq-stage-zero 390, P-latency-puq-stage-zero 401, B4-latency-puq-stage-zero 433, B1 1037 s
dim256 k2-s23: 2 clusters, 11 critical cells; P+prog-latency-puq-stage-zero 377, P-latency-puq-stage-zero 383, B4-latency-puq-stage-zero 369, B1 942 s
dim256 k2-s25: 2 clusters, 12 critical cells; P+prog-latency-puq-stage-zero 383, P-latency-puq-stage-zero 395, B4-latency-puq-stage-zero 390, B1 750 s
dim256 k2-s3: 2 clusters, 12 critical cells; P+prog-latency-puq-stage-zero 389, P-latency-puq-stage-zero 394, B4-latency-puq-stage-zero 434, B1 746 s
dim256 k2-s4: 2 clusters, 14 critical cells; P+prog-latency-puq-stage-zero 344, P-latency-puq-stage-zero 365, B4-latency-puq-stage-zero 385, B1 766 s
dim256 k2-s5: 2 clusters, 15 critical cells; P+prog-latency-puq-stage-zero 360, P-latency-puq-stage-zero 358, B4-latency-puq-stage-zero 406, B1 1026 s
dim256 k2-s8: 2 clusters, 14 critical cells; P+prog-latency-puq-stage-zero 355, P-latency-puq-stage-zero 385, B4-latency-puq-stage-zero 364, B1 939 s
dim256 k2-s9: 2 clusters, 15 critical cells; P+prog-latency-puq-stage-zero 379, P-latency-puq-stage-zero 392, B4-latency-puq-stage-zero 397, B1 953 s
dim256 k4-s1: 4 clusters, 25 critical cells; P+prog-latency-puq-stage-zero 467, P-latency-puq-stage-zero 458, B4-latency-puq-stage-zero 541, B1 1559 s
dim256 k4-s11: 4 clusters, 31 critical cells; P+prog-latency-puq-stage-zero 530, P-latency-puq-stage-zero 536, B4-latency-puq-stage-zero 534, B1 1887 s
dim256 k4-s12: 4 clusters, 26 critical cells; P+prog-latency-puq-stage-zero 553, P-latency-puq-stage-zero 561, B4-latency-puq-stage-zero 605, B1 1754 s
dim256 k4-s13: 4 clusters, 25 critical cells; P+prog-latency-puq-stage-zero 484, P-latency-puq-stage-zero 498, B4-latency-puq-stage-zero 512, B1 1527 s
dim256 k4-s16: 4 clusters, 30 critical cells; P+prog-latency-puq-stage-zero 520, P-latency-puq-stage-zero 524, B4-latency-puq-stage-zero 540, B1 1963 s
dim256 k4-s2: 4 clusters, 27 critical cells; P+prog-latency-puq-stage-zero 502, P-latency-puq-stage-zero 520, B4-latency-puq-stage-zero 503, B1 1595 s
dim256 k4-s20: 4 clusters, 21 critical cells; P+prog-latency-puq-stage-zero 467, P-latency-puq-stage-zero 471, B4-latency-puq-stage-zero 480, B1 1380 s
dim256 k4-s21: 4 clusters, 29 critical cells; P+prog-latency-puq-stage-zero 490, P-latency-puq-stage-zero 517, B4-latency-puq-stage-zero 529, B1 1769 s
dim256 k4-s5: 4 clusters, 24 critical cells; P+prog-latency-puq-stage-zero 503, P-latency-puq-stage-zero 513, B4-latency-puq-stage-zero 518, B1 1531 s
dim256 k4-s9: 4 clusters, 31 critical cells; P+prog-latency-puq-stage-zero 547, P-latency-puq-stage-zero 579, B4-latency-puq-stage-zero 652, B1 1793 s
dim256 k6-s11: 6 clusters, 34 critical cells; P+prog-latency-puq-stage-zero 566, P-latency-puq-stage-zero 564, B4-latency-puq-stage-zero 621, B1 2186 s
dim256 k6-s12: 6 clusters, 36 critical cells; P+prog-latency-puq-stage-zero 582, P-latency-puq-stage-zero 599, B4-latency-puq-stage-zero 657, B1 2268 s
dim256 k6-s13: 6 clusters, 43 critical cells; P+prog-latency-puq-stage-zero 555, P-latency-puq-stage-zero 566, B4-latency-puq-stage-zero 546, B1 2744 s
dim256 k6-s15: 6 clusters, 40 critical cells; P+prog-latency-puq-stage-zero 597, P-latency-puq-stage-zero 608, B4-latency-puq-stage-zero 623, B1 2570 s
dim256 k6-s16: 6 clusters, 40 critical cells; P+prog-latency-puq-stage-zero 673, P-latency-puq-stage-zero 679, B4-latency-puq-stage-zero 711, B1 2553 s
dim256 k6-s17: 6 clusters, 36 critical cells; P+prog-latency-puq-stage-zero 543, P-latency-puq-stage-zero 548, B4-latency-puq-stage-zero 536, B1 2646 s
dim256 k6-s2: 6 clusters, 44 critical cells; P+prog-latency-puq-stage-zero 542, P-latency-puq-stage-zero 555, B4-latency-puq-stage-zero 584, B1 2769 s
dim256 k6-s20: 6 clusters, 43 critical cells; P+prog-latency-puq-stage-zero 657, P-latency-puq-stage-zero 663, B4-latency-puq-stage-zero 701, B1 2404 s
dim256 k6-s4: 6 clusters, 45 critical cells; P+prog-latency-puq-stage-zero 620, P-latency-puq-stage-zero 630, B4-latency-puq-stage-zero 701, B1 3114 s
dim256 k6-s9: 6 clusters, 38 critical cells; P+prog-latency-puq-stage-zero 650, P-latency-puq-stage-zero 668, B4-latency-puq-stage-zero 654, B1 2483 s
dim256 k8-s1: 8 clusters, 49 critical cells; P+prog-latency-puq-stage-zero 707, P-latency-puq-stage-zero 718, B4-latency-puq-stage-zero 756, B1 3115 s
dim256 k8-s10: 8 clusters, 45 critical cells; P+prog-latency-puq-stage-zero 626, P-latency-puq-stage-zero 633, B4-latency-puq-stage-zero 636, B1 2686 s
dim256 k8-s11: 8 clusters, 51 critical cells; P+prog-latency-puq-stage-zero 663, P-latency-puq-stage-zero 672, B4-latency-puq-stage-zero 688, B1 3093 s
dim256 k8-s2: 8 clusters, 50 critical cells; P+prog-latency-puq-stage-zero 655, P-latency-puq-stage-zero 665, B4-latency-puq-stage-zero 635, B1 3238 s
dim256 k8-s4: 8 clusters, 52 critical cells; P+prog-latency-puq-stage-zero 595, P-latency-puq-stage-zero 599, B4-latency-puq-stage-zero 656, B1 3524 s
dim256 k8-s5: 8 clusters, 47 critical cells; P+prog-latency-puq-stage-zero 719, P-latency-puq-stage-zero 734, B4-latency-puq-stage-zero 714, B1 3008 s
dim256 k8-s6: 8 clusters, 54 critical cells; P+prog-latency-puq-stage-zero 624, P-latency-puq-stage-zero 623, B4-latency-puq-stage-zero 685, B1 3210 s
dim256 k8-s7: 8 clusters, 55 critical cells; P+prog-latency-puq-stage-zero 691, P-latency-puq-stage-zero 695, B4-latency-puq-stage-zero 737, B1 3638 s
dim256 k8-s8: 8 clusters, 48 critical cells; P+prog-latency-puq-stage-zero 714, P-latency-puq-stage-zero 712, B4-latency-puq-stage-zero 776, B1 2874 s
dim256 k8-s9: 8 clusters, 50 critical cells; P+prog-latency-puq-stage-zero 679, P-latency-puq-stage-zero 679, B4-latency-puq-stage-zero 804, B1 2893 s
rho0 k2-s10: 2 clusters, 11 critical cells; P+prog-latency-puq-stage-zero 388, P-latency-puq-stage-zero 402, B4-latency-puq-stage-zero 390, B1 793 s
rho0 k2-s11: 2 clusters, 16 critical cells; P+prog-latency-puq-stage-zero 419, P-latency-puq-stage-zero 416, B4-latency-puq-stage-zero 496, B1 1103 s
rho0 k2-s23: 2 clusters, 11 critical cells; P+prog-latency-puq-stage-zero 421, P-latency-puq-stage-zero 433, B4-latency-puq-stage-zero 423, B1 959 s
rho0 k2-s20: 2 clusters, 15 critical cells; P+prog-latency-puq-stage-zero 464, P-latency-puq-stage-zero 472, B4-latency-puq-stage-zero 440, B1 978 s
rho0 k2-s25: 2 clusters, 12 critical cells; P+prog-latency-puq-stage-zero 435, P-latency-puq-stage-zero 445, B4-latency-puq-stage-zero 449, B1 817 s
rho0 k2-s3: 2 clusters, 12 critical cells; P+prog-latency-puq-stage-zero 428, P-latency-puq-stage-zero 444, B4-latency-puq-stage-zero 459, B1 775 s
rho0 k2-s4: 2 clusters, 14 critical cells; P+prog-latency-puq-stage-zero 417, P-latency-puq-stage-zero 429, B4-latency-puq-stage-zero 457, B1 856 s
rho0 k2-s5: 2 clusters, 15 critical cells; P+prog-latency-puq-stage-zero 474, P-latency-puq-stage-zero 468, B4-latency-puq-stage-zero 463, B1 1064 s
rho0 k2-s8: 2 clusters, 14 critical cells; P+prog-latency-puq-stage-zero 371, P-latency-puq-stage-zero 378, B4-latency-puq-stage-zero 377, B1 1055 s
rho0 k2-s9: 2 clusters, 15 critical cells; P+prog-latency-puq-stage-zero 403, P-latency-puq-stage-zero 410, B4-latency-puq-stage-zero 406, B1 982 s
rho0 k4-s1: 4 clusters, 25 critical cells; P+prog-latency-puq-stage-zero 499, P-latency-puq-stage-zero 508, B4-latency-puq-stage-zero 565, B1 1820 s
rho0 k4-s11: 4 clusters, 31 critical cells; P+prog-latency-puq-stage-zero 581, P-latency-puq-stage-zero 591, B4-latency-puq-stage-zero 627, B1 1769 s
rho0 k4-s12: 4 clusters, 26 critical cells; P+prog-latency-puq-stage-zero 605, P-latency-puq-stage-zero 613, B4-latency-puq-stage-zero 630, B1 1640 s
rho0 k4-s13: 4 clusters, 25 critical cells; P+prog-latency-puq-stage-zero 513, P-latency-puq-stage-zero 532, B4-latency-puq-stage-zero 549, B1 1573 s
rho0 k4-s16: 4 clusters, 30 critical cells; P+prog-latency-puq-stage-zero 593, P-latency-puq-stage-zero 598, B4-latency-puq-stage-zero 632, B1 1980 s
rho0 k4-s2: 4 clusters, 27 critical cells; P+prog-latency-puq-stage-zero 545, P-latency-puq-stage-zero 545, B4-latency-puq-stage-zero 627, B1 1724 s
rho0 k4-s20: 4 clusters, 21 critical cells; P+prog-latency-puq-stage-zero 579, P-latency-puq-stage-zero 569, B4-latency-puq-stage-zero 655, B1 1529 s
rho0 k4-s21: 4 clusters, 29 critical cells; P+prog-latency-puq-stage-zero 587, P-latency-puq-stage-zero 605, B4-latency-puq-stage-zero 605, B1 1921 s
rho0 k4-s5: 4 clusters, 24 critical cells; P+prog-latency-puq-stage-zero 506, P-latency-puq-stage-zero 510, B4-latency-puq-stage-zero 553, B1 1579 s
rho0 k4-s9: 4 clusters, 31 critical cells; P+prog-latency-puq-stage-zero 659, P-latency-puq-stage-zero 696, B4-latency-puq-stage-zero 742, B1 1746 s
rho0 k6-s11: 6 clusters, 34 critical cells; P+prog-latency-puq-stage-zero 578, P-latency-puq-stage-zero 591, B4-latency-puq-stage-zero 654, B1 1967 s
rho0 k6-s12: 6 clusters, 36 critical cells; P+prog-latency-puq-stage-zero 671, P-latency-puq-stage-zero 690, B4-latency-puq-stage-zero 731, B1 2418 s
rho0 k6-s13: 6 clusters, 43 critical cells; P+prog-latency-puq-stage-zero 598, P-latency-puq-stage-zero 598, B4-latency-puq-stage-zero 627, B1 2561 s
rho0 k6-s15: 6 clusters, 40 critical cells; P+prog-latency-puq-stage-zero 622, P-latency-puq-stage-zero 622, B4-latency-puq-stage-zero 696, B1 2664 s
rho0 k6-s16: 6 clusters, 40 critical cells; P+prog-latency-puq-stage-zero 628, P-latency-puq-stage-zero 632, B4-latency-puq-stage-zero 742, B1 2254 s
rho0 k6-s17: 6 clusters, 36 critical cells; P+prog-latency-puq-stage-zero 663, P-latency-puq-stage-zero 675, B4-latency-puq-stage-zero 689, B1 2287 s
rho0 k6-s2: 6 clusters, 44 critical cells; P+prog-latency-puq-stage-zero 710, P-latency-puq-stage-zero 708, B4-latency-puq-stage-zero 754, B1 2741 s
rho0 k6-s20: 6 clusters, 43 critical cells; P+prog-latency-puq-stage-zero 695, P-latency-puq-stage-zero 680, B4-latency-puq-stage-zero 723, B1 2446 s
rho0 k6-s4: 6 clusters, 45 critical cells; P+prog-latency-puq-stage-zero 686, P-latency-puq-stage-zero 686, B4-latency-puq-stage-zero 790, B1 2868 s
rho0 k6-s9: 6 clusters, 38 critical cells; P+prog-latency-puq-stage-zero 674, P-latency-puq-stage-zero 693, B4-latency-puq-stage-zero 765, B1 2122 s
rho0 k8-s1: 8 clusters, 49 critical cells; P+prog-latency-puq-stage-zero 819, P-latency-puq-stage-zero 830, B4-latency-puq-stage-zero 1043, B1 3216 s
rho0 k8-s10: 8 clusters, 45 critical cells; P+prog-latency-puq-stage-zero 685, P-latency-puq-stage-zero 690, B4-latency-puq-stage-zero 752, B1 2620 s
rho0 k8-s2: 8 clusters, 50 critical cells; P+prog-latency-puq-stage-zero 794, P-latency-puq-stage-zero 812, B4-latency-puq-stage-zero 835, B1 3425 s
rho0 k8-s11: 8 clusters, 51 critical cells; P+prog-latency-puq-stage-zero 758, P-latency-puq-stage-zero 747, B4-latency-puq-stage-zero 814, B1 2924 s
rho0 k8-s5: 8 clusters, 47 critical cells; P+prog-latency-puq-stage-zero 893, P-latency-puq-stage-zero 899, B4-latency-puq-stage-zero 1016, B1 3117 s
rho0 k8-s4: 8 clusters, 52 critical cells; P+prog-latency-puq-stage-zero 729, P-latency-puq-stage-zero 729, B4-latency-puq-stage-zero 769, B1 3725 s
rho0 k8-s6: 8 clusters, 54 critical cells; P+prog-latency-puq-stage-zero 803, P-latency-puq-stage-zero 808, B4-latency-puq-stage-zero 836, B1 2929 s
rho0 k8-s7: 8 clusters, 55 critical cells; P+prog-latency-puq-stage-zero 761, P-latency-puq-stage-zero 759, B4-latency-puq-stage-zero 768, B1 3206 s
rho0 k8-s8: 8 clusters, 48 critical cells; P+prog-latency-puq-stage-zero 842, P-latency-puq-stage-zero 854, B4-latency-puq-stage-zero 956, B1 2592 s
rho0 k8-s9: 8 clusters, 50 critical cells; P+prog-latency-puq-stage-zero 888, P-latency-puq-stage-zero 903, B4-latency-puq-stage-zero 918, B1 2973 s
rho05 k2-s10: 2 clusters, 11 critical cells; P+prog-latency-puq-stage-zero 393, P-latency-puq-stage-zero 395, B4-latency-puq-stage-zero 400, B1 848 s
rho05 k2-s11: 2 clusters, 16 critical cells; P+prog-latency-puq-stage-zero 389, P-latency-puq-stage-zero 394, B4-latency-puq-stage-zero 423, B1 1114 s
rho05 k2-s20: 2 clusters, 15 critical cells; P+prog-latency-puq-stage-zero 437, P-latency-puq-stage-zero 449, B4-latency-puq-stage-zero 435, B1 978 s
rho05 k2-s23: 2 clusters, 11 critical cells; P+prog-latency-puq-stage-zero 407, P-latency-puq-stage-zero 400, B4-latency-puq-stage-zero 414, B1 978 s
rho05 k2-s25: 2 clusters, 12 critical cells; P+prog-latency-puq-stage-zero 385, P-latency-puq-stage-zero 395, B4-latency-puq-stage-zero 415, B1 716 s
rho05 k2-s3: 2 clusters, 12 critical cells; P+prog-latency-puq-stage-zero 483, P-latency-puq-stage-zero 489, B4-latency-puq-stage-zero 499, B1 820 s
rho05 k2-s4: 2 clusters, 14 critical cells; P+prog-latency-puq-stage-zero 366, P-latency-puq-stage-zero 377, B4-latency-puq-stage-zero 399, B1 773 s
rho05 k2-s5: 2 clusters, 15 critical cells; P+prog-latency-puq-stage-zero 347, P-latency-puq-stage-zero 349, B4-latency-puq-stage-zero 401, B1 988 s
rho05 k2-s8: 2 clusters, 14 critical cells; P+prog-latency-puq-stage-zero 366, P-latency-puq-stage-zero 386, B4-latency-puq-stage-zero 383, B1 943 s
rho05 k2-s9: 2 clusters, 15 critical cells; P+prog-latency-puq-stage-zero 373, P-latency-puq-stage-zero 383, B4-latency-puq-stage-zero 420, B1 918 s
rho05 k4-s1: 4 clusters, 25 critical cells; P+prog-latency-puq-stage-zero 513, P-latency-puq-stage-zero 523, B4-latency-puq-stage-zero 568, B1 1410 s
rho05 k4-s11: 4 clusters, 31 critical cells; P+prog-latency-puq-stage-zero 597, P-latency-puq-stage-zero 616, B4-latency-puq-stage-zero 679, B1 2004 s
rho05 k4-s12: 4 clusters, 26 critical cells; P+prog-latency-puq-stage-zero 570, P-latency-puq-stage-zero 599, B4-latency-puq-stage-zero 655, B1 1797 s
rho05 k4-s13: 4 clusters, 25 critical cells; P+prog-latency-puq-stage-zero 602, P-latency-puq-stage-zero 613, B4-latency-puq-stage-zero 745, B1 1678 s
rho05 k4-s16: 4 clusters, 30 critical cells; P+prog-latency-puq-stage-zero 549, P-latency-puq-stage-zero 554, B4-latency-puq-stage-zero 610, B1 1894 s
rho05 k4-s2: 4 clusters, 27 critical cells; P+prog-latency-puq-stage-zero 594, P-latency-puq-stage-zero 604, B4-latency-puq-stage-zero 647, B1 1645 s
rho05 k4-s20: 4 clusters, 21 critical cells; P+prog-latency-puq-stage-zero 516, P-latency-puq-stage-zero 525, B4-latency-puq-stage-zero 579, B1 1324 s
rho05 k4-s21: 4 clusters, 29 critical cells; P+prog-latency-puq-stage-zero 612, P-latency-puq-stage-zero 623, B4-latency-puq-stage-zero 639, B1 1811 s
rho05 k4-s5: 4 clusters, 24 critical cells; P+prog-latency-puq-stage-zero 561, P-latency-puq-stage-zero 560, B4-latency-puq-stage-zero 595, B1 1531 s
rho05 k4-s9: 4 clusters, 31 critical cells; P+prog-latency-puq-stage-zero 572, P-latency-puq-stage-zero 603, B4-latency-puq-stage-zero 650, B1 2054 s
rho05 k6-s11: 6 clusters, 34 critical cells; P+prog-latency-puq-stage-zero 685, P-latency-puq-stage-zero 694, B4-latency-puq-stage-zero 766, B1 2313 s
rho05 k6-s12: 6 clusters, 36 critical cells; P+prog-latency-puq-stage-zero 688, P-latency-puq-stage-zero 718, B4-latency-puq-stage-zero 710, B1 2544 s
rho05 k6-s13: 6 clusters, 43 critical cells; P+prog-latency-puq-stage-zero 543, P-latency-puq-stage-zero 557, B4-latency-puq-stage-zero 534, B1 2604 s
rho05 k6-s15: 6 clusters, 40 critical cells; P+prog-latency-puq-stage-zero 578, P-latency-puq-stage-zero 576, B4-latency-puq-stage-zero 678, B1 2424 s
rho05 k6-s16: 6 clusters, 40 critical cells; P+prog-latency-puq-stage-zero 709, P-latency-puq-stage-zero 709, B4-latency-puq-stage-zero 766, B1 1999 s
rho05 k6-s17: 6 clusters, 36 critical cells; P+prog-latency-puq-stage-zero 631, P-latency-puq-stage-zero 631, B4-latency-puq-stage-zero 657, B1 2491 s
rho05 k6-s2: 6 clusters, 44 critical cells; P+prog-latency-puq-stage-zero 611, P-latency-puq-stage-zero 627, B4-latency-puq-stage-zero 627, B1 2639 s
rho05 k6-s20: 6 clusters, 43 critical cells; P+prog-latency-puq-stage-zero 725, P-latency-puq-stage-zero 727, B4-latency-puq-stage-zero 751, B1 2367 s
rho05 k6-s4: 6 clusters, 45 critical cells; P+prog-latency-puq-stage-zero 715, P-latency-puq-stage-zero 713, B4-latency-puq-stage-zero 830, B1 2969 s
rho05 k6-s9: 6 clusters, 38 critical cells; P+prog-latency-puq-stage-zero 649, P-latency-puq-stage-zero 659, B4-latency-puq-stage-zero 783, B1 2395 s
rho05 k8-s10: 8 clusters, 45 critical cells; P+prog-latency-puq-stage-zero 656, P-latency-puq-stage-zero 656, B4-latency-puq-stage-zero 725, B1 2490 s
rho05 k8-s1: 8 clusters, 49 critical cells; P+prog-latency-puq-stage-zero 682, P-latency-puq-stage-zero 691, B4-latency-puq-stage-zero 734, B1 2662 s
rho05 k8-s2: 8 clusters, 50 critical cells; P+prog-latency-puq-stage-zero 740, P-latency-puq-stage-zero 781, B4-latency-puq-stage-zero 814, B1 3447 s
rho05 k8-s11: 8 clusters, 51 critical cells; P+prog-latency-puq-stage-zero 782, P-latency-puq-stage-zero 788, B4-latency-puq-stage-zero 782, B1 3082 s
rho05 k8-s5: 8 clusters, 47 critical cells; P+prog-latency-puq-stage-zero 855, P-latency-puq-stage-zero 873, B4-latency-puq-stage-zero 883, B1 2955 s
rho05 k8-s4: 8 clusters, 52 critical cells; P+prog-latency-puq-stage-zero 696, P-latency-puq-stage-zero 711, B4-latency-puq-stage-zero 759, B1 3330 s
rho05 k8-s6: 8 clusters, 54 critical cells; P+prog-latency-puq-stage-zero 655, P-latency-puq-stage-zero 673, B4-latency-puq-stage-zero 684, B1 3394 s
rho05 k8-s7: 8 clusters, 55 critical cells; P+prog-latency-puq-stage-zero 713, P-latency-puq-stage-zero 722, B4-latency-puq-stage-zero 786, B1 3780 s
rho05 k8-s8: 8 clusters, 48 critical cells; P+prog-latency-puq-stage-zero 825, P-latency-puq-stage-zero 831, B4-latency-puq-stage-zero 950, B1 2886 s
rho05 k8-s9: 8 clusters, 50 critical cells; P+prog-latency-puq-stage-zero 878, P-latency-puq-stage-zero 887, B4-latency-puq-stage-zero 959, B1 2992 s
m105 k2-s10: 2 clusters, 11 critical cells; P+prog-latency-puq-stage-zero 375, P-latency-puq-stage-zero 382, B4-latency-puq-stage-zero 390, B1 749 s
m105 k2-s11: 2 clusters, 16 critical cells; P+prog-latency-puq-stage-zero 368, P-latency-puq-stage-zero 383, B4-latency-puq-stage-zero 368, B1 1050 s
m105 k2-s20: 2 clusters, 15 critical cells; P+prog-latency-puq-stage-zero 392, P-latency-puq-stage-zero 404, B4-latency-puq-stage-zero 395, B1 1160 s
m105 k2-s23: 2 clusters, 11 critical cells; P+prog-latency-puq-stage-zero 434, P-latency-puq-stage-zero 455, B4-latency-puq-stage-zero 455, B1 861 s
m105 k2-s25: 2 clusters, 12 critical cells; P+prog-latency-puq-stage-zero 385, P-latency-puq-stage-zero 389, B4-latency-puq-stage-zero 392, B1 853 s
m105 k2-s3: 2 clusters, 12 critical cells; P+prog-latency-puq-stage-zero 414, P-latency-puq-stage-zero 440, B4-latency-puq-stage-zero 426, B1 750 s
m105 k2-s4: 2 clusters, 14 critical cells; P+prog-latency-puq-stage-zero 375, P-latency-puq-stage-zero 384, B4-latency-puq-stage-zero 439, B1 936 s
m105 k2-s5: 2 clusters, 15 critical cells; P+prog-latency-puq-stage-zero 353, P-latency-puq-stage-zero 356, B4-latency-puq-stage-zero 414, B1 1082 s
m105 k2-s8: 2 clusters, 14 critical cells; P+prog-latency-puq-stage-zero 400, P-latency-puq-stage-zero 427, B4-latency-puq-stage-zero 425, B1 889 s
m105 k2-s9: 2 clusters, 15 critical cells; P+prog-latency-puq-stage-zero 431, P-latency-puq-stage-zero 431, B4-latency-puq-stage-zero 413, B1 981 s
m105 k4-s1: 4 clusters, 25 critical cells; P+prog-latency-puq-stage-zero 536, P-latency-puq-stage-zero 545, B4-latency-puq-stage-zero 555, B1 1741 s
m105 k4-s11: 4 clusters, 31 critical cells; P+prog-latency-puq-stage-zero 579, P-latency-puq-stage-zero 591, B4-latency-puq-stage-zero 629, B1 1582 s
m105 k4-s12: 4 clusters, 26 critical cells; P+prog-latency-puq-stage-zero 525, P-latency-puq-stage-zero 548, B4-latency-puq-stage-zero 639, B1 1485 s
m105 k4-s13: 4 clusters, 25 critical cells; P+prog-latency-puq-stage-zero 487, P-latency-puq-stage-zero 494, B4-latency-puq-stage-zero 504, B1 1463 s
m105 k4-s16: 4 clusters, 30 critical cells; P+prog-latency-puq-stage-zero 477, P-latency-puq-stage-zero 489, B4-latency-puq-stage-zero 503, B1 2000 s
m105 k4-s2: 4 clusters, 27 critical cells; P+prog-latency-puq-stage-zero 455, P-latency-puq-stage-zero 461, B4-latency-puq-stage-zero 497, B1 1661 s
m105 k4-s20: 4 clusters, 21 critical cells; P+prog-latency-puq-stage-zero 565, P-latency-puq-stage-zero 572, B4-latency-puq-stage-zero 618, B1 1447 s
m105 k4-s5: 4 clusters, 24 critical cells; P+prog-latency-puq-stage-zero 499, P-latency-puq-stage-zero 507, B4-latency-puq-stage-zero 509, B1 1567 s
m105 k4-s21: 4 clusters, 29 critical cells; P+prog-latency-puq-stage-zero 582, P-latency-puq-stage-zero 591, B4-latency-puq-stage-zero 665, B1 1947 s
m105 k4-s9: 4 clusters, 31 critical cells; P+prog-latency-puq-stage-zero 545, P-latency-puq-stage-zero 582, B4-latency-puq-stage-zero 637, B1 2106 s
m105 k6-s11: 6 clusters, 34 critical cells; P+prog-latency-puq-stage-zero 606, P-latency-puq-stage-zero 640, B4-latency-puq-stage-zero 652, B1 2303 s
m105 k6-s12: 6 clusters, 36 critical cells; P+prog-latency-puq-stage-zero 655, P-latency-puq-stage-zero 663, B4-latency-puq-stage-zero 683, B1 2117 s
m105 k6-s13: 6 clusters, 43 critical cells; P+prog-latency-puq-stage-zero 699, P-latency-puq-stage-zero 694, B4-latency-puq-stage-zero 785, B1 2466 s
m105 k6-s15: 6 clusters, 40 critical cells; P+prog-latency-puq-stage-zero 645, P-latency-puq-stage-zero 635, B4-latency-puq-stage-zero 734, B1 2548 s
m105 k6-s16: 6 clusters, 40 critical cells; P+prog-latency-puq-stage-zero 678, P-latency-puq-stage-zero 661, B4-latency-puq-stage-zero 709, B1 2790 s
m105 k6-s17: 6 clusters, 36 critical cells; P+prog-latency-puq-stage-zero 532, P-latency-puq-stage-zero 544, B4-latency-puq-stage-zero 519, B1 2174 s
m105 k6-s2: 6 clusters, 44 critical cells; P+prog-latency-puq-stage-zero 678, P-latency-puq-stage-zero 695, B4-latency-puq-stage-zero 748, B1 2900 s
m105 k6-s20: 6 clusters, 43 critical cells; P+prog-latency-puq-stage-zero 661, P-latency-puq-stage-zero 654, B4-latency-puq-stage-zero 700, B1 2732 s
m105 k6-s4: 6 clusters, 45 critical cells; P+prog-latency-puq-stage-zero 709, P-latency-puq-stage-zero 701, B4-latency-puq-stage-zero 780, B1 2668 s
m105 k6-s9: 6 clusters, 38 critical cells; P+prog-latency-puq-stage-zero 749, P-latency-puq-stage-zero 775, B4-latency-puq-stage-zero 824, B1 2371 s
m105 k8-s1: 8 clusters, 49 critical cells; P+prog-latency-puq-stage-zero 831, P-latency-puq-stage-zero 838, B4-latency-puq-stage-zero 907, B1 3078 s
m105 k8-s10: 8 clusters, 45 critical cells; P+prog-latency-puq-stage-zero 747, P-latency-puq-stage-zero 746, B4-latency-puq-stage-zero 821, B1 2462 s
m105 k8-s11: 8 clusters, 51 critical cells; P+prog-latency-puq-stage-zero 738, P-latency-puq-stage-zero 747, B4-latency-puq-stage-zero 878, B1 2915 s
m105 k8-s2: 8 clusters, 50 critical cells; P+prog-latency-puq-stage-zero 667, P-latency-puq-stage-zero 671, B4-latency-puq-stage-zero 831, B1 2933 s
m105 k8-s5: 8 clusters, 47 critical cells; P+prog-latency-puq-stage-zero 795, P-latency-puq-stage-zero 799, B4-latency-puq-stage-zero 835, B1 2925 s
m105 k8-s4: 8 clusters, 52 critical cells; P+prog-latency-puq-stage-zero 713, P-latency-puq-stage-zero 704, B4-latency-puq-stage-zero 830, B1 3290 s
m105 k8-s6: 8 clusters, 54 critical cells; P+prog-latency-puq-stage-zero 787, P-latency-puq-stage-zero 791, B4-latency-puq-stage-zero 853, B1 3671 s
m105 k8-s7: 8 clusters, 55 critical cells; P+prog-latency-puq-stage-zero 762, P-latency-puq-stage-zero 789, B4-latency-puq-stage-zero 858, B1 3214 s
m105 k8-s8: 8 clusters, 48 critical cells; P+prog-latency-puq-stage-zero 892, P-latency-puq-stage-zero 894, B4-latency-puq-stage-zero 1021, B1 2707 s
m105 k8-s9: 8 clusters, 50 critical cells; P+prog-latency-puq-stage-zero 821, P-latency-puq-stage-zero 838, B4-latency-puq-stage-zero 832, B1 3140 s
m693 k2-s10: 2 clusters, 11 critical cells; P+prog-latency-puq-stage-zero 427, P-latency-puq-stage-zero 429, B4-latency-puq-stage-zero 462, B1 840 s
m693 k2-s11: 2 clusters, 16 critical cells; P+prog-latency-puq-stage-zero 431, P-latency-puq-stage-zero 461, B4-latency-puq-stage-zero 472, B1 946 s
m693 k2-s20: 2 clusters, 15 critical cells; P+prog-latency-puq-stage-zero 468, P-latency-puq-stage-zero 472, B4-latency-puq-stage-zero 488, B1 953 s
m693 k2-s23: 2 clusters, 11 critical cells; P+prog-latency-puq-stage-zero 382, P-latency-puq-stage-zero 397, B4-latency-puq-stage-zero 377, B1 1025 s
m693 k2-s25: 2 clusters, 12 critical cells; P+prog-latency-puq-stage-zero 438, P-latency-puq-stage-zero 444, B4-latency-puq-stage-zero 440, B1 825 s
m693 k2-s3: 2 clusters, 12 critical cells; P+prog-latency-puq-stage-zero 391, P-latency-puq-stage-zero 396, B4-latency-puq-stage-zero 376, B1 854 s
m693 k2-s4: 2 clusters, 14 critical cells; P+prog-latency-puq-stage-zero 376, P-latency-puq-stage-zero 385, B4-latency-puq-stage-zero 403, B1 911 s
m693 k2-s5: 2 clusters, 15 critical cells; P+prog-latency-puq-stage-zero 406, P-latency-puq-stage-zero 417, B4-latency-puq-stage-zero 467, B1 1083 s
m693 k2-s8: 2 clusters, 14 critical cells; P+prog-latency-puq-stage-zero 432, P-latency-puq-stage-zero 449, B4-latency-puq-stage-zero 522, B1 990 s
m693 k2-s9: 2 clusters, 15 critical cells; P+prog-latency-puq-stage-zero 358, P-latency-puq-stage-zero 360, B4-latency-puq-stage-zero 372, B1 976 s
m693 k4-s1: 4 clusters, 25 critical cells; P+prog-latency-puq-stage-zero 561, P-latency-puq-stage-zero 560, B4-latency-puq-stage-zero 626, B1 1767 s
m693 k4-s11: 4 clusters, 31 critical cells; P+prog-latency-puq-stage-zero 568, P-latency-puq-stage-zero 582, B4-latency-puq-stage-zero 626, B1 2038 s
m693 k4-s12: 4 clusters, 26 critical cells; P+prog-latency-puq-stage-zero 522, P-latency-puq-stage-zero 547, B4-latency-puq-stage-zero 607, B1 1868 s
m693 k4-s13: 4 clusters, 25 critical cells; P+prog-latency-puq-stage-zero 607, P-latency-puq-stage-zero 604, B4-latency-puq-stage-zero 763, B1 1510 s
m693 k4-s16: 4 clusters, 30 critical cells; P+prog-latency-puq-stage-zero 568, P-latency-puq-stage-zero 577, B4-latency-puq-stage-zero 581, B1 1627 s
m693 k4-s2: 4 clusters, 27 critical cells; P+prog-latency-puq-stage-zero 501, P-latency-puq-stage-zero 513, B4-latency-puq-stage-zero 545, B1 1563 s
m693 k4-s20: 4 clusters, 21 critical cells; P+prog-latency-puq-stage-zero 555, P-latency-puq-stage-zero 544, B4-latency-puq-stage-zero 549, B1 1323 s
m693 k4-s5: 4 clusters, 24 critical cells; P+prog-latency-puq-stage-zero 539, P-latency-puq-stage-zero 545, B4-latency-puq-stage-zero 591, B1 1462 s
m693 k4-s21: 4 clusters, 29 critical cells; P+prog-latency-puq-stage-zero 521, P-latency-puq-stage-zero 535, B4-latency-puq-stage-zero 625, B1 1695 s
m693 k4-s9: 4 clusters, 31 critical cells; P+prog-latency-puq-stage-zero 622, P-latency-puq-stage-zero 630, B4-latency-puq-stage-zero 690, B1 1805 s
m693 k6-s11: 6 clusters, 34 critical cells; P+prog-latency-puq-stage-zero 722, P-latency-puq-stage-zero 720, B4-latency-puq-stage-zero 789, B1 2193 s
m693 k6-s12: 6 clusters, 36 critical cells; P+prog-latency-puq-stage-zero 689, P-latency-puq-stage-zero 702, B4-latency-puq-stage-zero 751, B1 2347 s
m693 k6-s13: 6 clusters, 43 critical cells; P+prog-latency-puq-stage-zero 660, P-latency-puq-stage-zero 675, B4-latency-puq-stage-zero 691, B1 2544 s
m693 k6-s15: 6 clusters, 40 critical cells; P+prog-latency-puq-stage-zero 619, P-latency-puq-stage-zero 629, B4-latency-puq-stage-zero 731, B1 2445 s
m693 k6-s16: 6 clusters, 40 critical cells; P+prog-latency-puq-stage-zero 657, P-latency-puq-stage-zero 656, B4-latency-puq-stage-zero 671, B1 2520 s
m693 k6-s17: 6 clusters, 36 critical cells; P+prog-latency-puq-stage-zero 569, P-latency-puq-stage-zero 575, B4-latency-puq-stage-zero 658, B1 2274 s
m693 k6-s2: 6 clusters, 44 critical cells; P+prog-latency-puq-stage-zero 694, P-latency-puq-stage-zero 685, B4-latency-puq-stage-zero 773, B1 2594 s
m693 k6-s20: 6 clusters, 43 critical cells; P+prog-latency-puq-stage-zero 693, P-latency-puq-stage-zero 693, B4-latency-puq-stage-zero 695, B1 2378 s
m693 k6-s4: 6 clusters, 45 critical cells; P+prog-latency-puq-stage-zero 743, P-latency-puq-stage-zero 749, B4-latency-puq-stage-zero 985, B1 2791 s
m693 k6-s9: 6 clusters, 38 critical cells; P+prog-latency-puq-stage-zero 757, P-latency-puq-stage-zero 782, B4-latency-puq-stage-zero 779, B1 2145 s
m693 k8-s10: 8 clusters, 45 critical cells; P+prog-latency-puq-stage-zero 711, P-latency-puq-stage-zero 712, B4-latency-puq-stage-zero 851, B1 2707 s
m693 k8-s1: 8 clusters, 49 critical cells; P+prog-latency-puq-stage-zero 702, P-latency-puq-stage-zero 713, B4-latency-puq-stage-zero 799, B1 2608 s
m693 k8-s11: 8 clusters, 51 critical cells; P+prog-latency-puq-stage-zero 725, P-latency-puq-stage-zero 736, B4-latency-puq-stage-zero 810, B1 3404 s
m693 k8-s2: 8 clusters, 50 critical cells; P+prog-latency-puq-stage-zero 881, P-latency-puq-stage-zero 874, B4-latency-puq-stage-zero 835, B1 3411 s
m693 k8-s5: 8 clusters, 47 critical cells; P+prog-latency-puq-stage-zero 921, P-latency-puq-stage-zero 922, B4-latency-puq-stage-zero 925, B1 3041 s
m693 k8-s4: 8 clusters, 52 critical cells; P+prog-latency-puq-stage-zero 846, P-latency-puq-stage-zero 844, B4-latency-puq-stage-zero 1049, B1 3019 s
m693 k8-s6: 8 clusters, 54 critical cells; P+prog-latency-puq-stage-zero 816, P-latency-puq-stage-zero 832, B4-latency-puq-stage-zero 837, B1 3358 s
m693 k8-s7: 8 clusters, 55 critical cells; P+prog-latency-puq-stage-zero 909, P-latency-puq-stage-zero 923, B4-latency-puq-stage-zero 1065, B1 3220 s
m693 k8-s8: 8 clusters, 48 critical cells; P+prog-latency-puq-stage-zero 793, P-latency-puq-stage-zero 796, B4-latency-puq-stage-zero 815, B1 3393 s
m693 k8-s9: 8 clusters, 50 critical cells; P+prog-latency-puq-stage-zero 813, P-latency-puq-stage-zero 854, B4-latency-puq-stage-zero 981, B1 2969 s
run base method B1 maps 40 Tstar 2069.3 ci 275.6 rank 17.14 first 0.037 dB4 1414.9 betterThanB4 0
run base method B4-latency-puq-stage-zero maps 40 Tstar 654.4 ci 48.4 rank 2.47 first 0.406 dB4 0.0 betterThanB4 0
run base method B7 maps 40 Tstar 298.2 ci 12.4 rank 1.0 first 1.0 dB4 -356.1 betterThanB4 40
run base method P+prog-latency-puq-stage-zero maps 40 Tstar 604.8 ci 43.2 rank 2.21 first 0.423 dB4 -49.6 betterThanB4 38
run base method P-latency-puq-stage-zero maps 40 Tstar 613.3 ci 43.4 rank 2.21 first 0.419 dB4 -41.0 betterThanB4 34
run dim64 method B1 maps 40 Tstar 2069.3 ci 275.6 rank 17.14 first 0.037 dB4 1229.5 betterThanB4 0
run dim64 method B4-latency-puq-stage-zero maps 40 Tstar 839.8 ci 75.6 rank 3.49 first 0.341 dB4 0.0 betterThanB4 0
run dim64 method B7 maps 40 Tstar 298.2 ci 12.4 rank 1.0 first 1.0 dB4 -541.6 betterThanB4 40
run dim64 method P+prog-latency-puq-stage-zero maps 40 Tstar 747.4 ci 62.5 rank 2.97 first 0.356 dB4 -92.4 betterThanB4 37
run dim64 method P-latency-puq-stage-zero maps 40 Tstar 754.6 ci 63.2 rank 2.96 first 0.359 dB4 -85.1 betterThanB4 36
run dim256 method B1 maps 40 Tstar 2069.3 ci 275.6 rank 17.14 first 0.037 dB4 1499.4 betterThanB4 0
run dim256 method B4-latency-puq-stage-zero maps 40 Tstar 569.9 ci 39.7 rank 2.03 first 0.459 dB4 0.0 betterThanB4 0
run dim256 method B7 maps 40 Tstar 298.2 ci 12.4 rank 1.0 first 1.0 dB4 -271.7 betterThanB4 40
run dim256 method P+prog-latency-puq-stage-zero maps 40 Tstar 536.3 ci 36.2 rank 1.86 first 0.471 dB4 -33.6 betterThanB4 34
run dim256 method P-latency-puq-stage-zero maps 40 Tstar 546.2 ci 35.7 rank 1.87 first 0.463 dB4 -23.7 betterThanB4 29
run rho0 method B1 maps 40 Tstar 2042.9 ci 260.0 rank 16.91 first 0.036 dB4 1382.3 betterThanB4 0
run rho0 method B4-latency-puq-stage-zero maps 40 Tstar 660.6 ci 53.5 rank 2.49 first 0.405 dB4 0.0 betterThanB4 0
run rho0 method B7 maps 40 Tstar 297.0 ci 12.1 rank 1.0 first 1.0 dB4 -363.6 betterThanB4 40
run rho0 method P+prog-latency-puq-stage-zero maps 40 Tstar 609.6 ci 45.2 rank 2.23 first 0.41 dB4 -51.0 betterThanB4 38
run rho0 method P-latency-puq-stage-zero maps 40 Tstar 616.7 ci 45.2 rank 2.22 first 0.416 dB4 -43.9 betterThanB4 33
run rho05 method B1 maps 40 Tstar 2049.7 ci 270.1 rank 16.98 first 0.042 dB4 1406.4 betterThanB4 0
run rho05 method B4-latency-puq-stage-zero maps 40 Tstar 643.3 ci 49.6 rank 2.42 first 0.397 dB4 0.0 betterThanB4 0
run rho05 method B7 maps 40 Tstar 297.2 ci 12.0 rank 1.0 first 1.0 dB4 -346.1 betterThanB4 40
run rho05 method P+prog-latency-puq-stage-zero maps 40 Tstar 591.3 ci 44.3 rank 2.16 first 0.409 dB4 -52.1 betterThanB4 37
run rho05 method P-latency-puq-stage-zero maps 40 Tstar 601.5 ci 44.9 rank 2.16 first 0.404 dB4 -41.8 betterThanB4 34
run m105 method B1 maps 40 Tstar 2042.9 ci 261.7 rank 16.92 first 0.036 dB4 1401.0 betterThanB4 0
run m105 method B4-latency-puq-stage-zero maps 40 Tstar 641.8 ci 56.1 rank 2.34 first 0.415 dB4 0.0 betterThanB4 0
run m105 method B7 maps 40 Tstar 300.5 ci 13.4 rank 1.0 first 1.0 dB4 -341.3 betterThanB4 40
run m105 method P+prog-latency-puq-stage-zero maps 40 Tstar 588.6 ci 47.6 rank 2.08 first 0.426 dB4 -53.3 betterThanB4 37
run m105 method P-latency-puq-stage-zero maps 40 Tstar 597.8 ci 46.9 rank 2.08 first 0.418 dB4 -44.1 betterThanB4 32
run m693 method B1 maps 40 Tstar 2035.6 ci 262.9 rank 16.84 first 0.037 dB4 1358.7 betterThanB4 0
run m693 method B4-latency-puq-stage-zero maps 40 Tstar 676.8 ci 58.3 rank 2.61 first 0.393 dB4 0.0 betterThanB4 0
run m693 method B7 maps 40 Tstar 296.7 ci 12.1 rank 1.0 first 1.0 dB4 -380.1 betterThanB4 40
run m693 method P+prog-latency-puq-stage-zero maps 40 Tstar 614.9 ci 49.4 rank 2.29 first 0.401 dB4 -61.9 betterThanB4 36
run m693 method P-latency-puq-stage-zero maps 40 Tstar 622.9 ci 49.3 rank 2.29 first 0.405 dB4 -53.9 betterThanB4 35
```
