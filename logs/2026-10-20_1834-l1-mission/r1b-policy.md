# r1b-policy

- Bắt đầu: 2026-10-20 18:50:57, chạy 433 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/l1_rank.py --set kmedoids '/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/camp/k*-s*,/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MK/k*' --draws 50 --jobs 2 --methods 'P,P-short,P-latency,P-pu-stage,P-short-pu-stage,P-latency-pu-stage,P+prog,P+prog-short,P+prog-latency,P+prog-pu-stage,P+prog-short-pu-stage,P+prog-latency-pu-stage,B4,B4-short,B4-latency,B4-pu-stage,B4-short-pu-stage,B4-latency-pu-stage,B7' --out docs/data/l1rank/r1b
```

**Kết quả**

```text
kmedoids k4-s2: 4 clusters, 27 critical cells; P 663, P-short 636, P-latency 665, P-pu-stage 583 s
kmedoids k6-s4: 6 clusters, 45 critical cells; P 761, P-short 754, P-latency 793, P-pu-stage 818 s
kmedoids k2-s10: 2 clusters, 11 critical cells; P 509, P-short 578, P-latency 509, P-pu-stage 476 s
kmedoids k2-s11: 2 clusters, 16 critical cells; P 547, P-short 547, P-latency 547, P-pu-stage 506 s
kmedoids k2-s20: 2 clusters, 15 critical cells; P 567, P-short 654, P-latency 567, P-pu-stage 551 s
kmedoids k2-s23: 2 clusters, 11 critical cells; P 454, P-short 454, P-latency 454, P-pu-stage 470 s
kmedoids k2-s25: 2 clusters, 12 critical cells; P 540, P-short 540, P-latency 540, P-pu-stage 484 s
kmedoids k8-s4: 8 clusters, 52 critical cells; P 757, P-short 895, P-latency 762, P-pu-stage 734 s
kmedoids k2-s4: 2 clusters, 14 critical cells; P 485, P-short 679, P-latency 485, P-pu-stage 491 s
kmedoids k2-s5: 2 clusters, 15 critical cells; P 466, P-short 466, P-latency 466, P-pu-stage 458 s
kmedoids k2-s8: 2 clusters, 14 critical cells; P 521, P-short 575, P-latency 521, P-pu-stage 470 s
kmedoids k2-s9: 2 clusters, 15 critical cells; P 538, P-short 602, P-latency 538, P-pu-stage 518 s
kmedoids k4-s1: 4 clusters, 25 critical cells; P 657, P-short 669, P-latency 657, P-pu-stage 547 s
kmedoids k4-s11: 4 clusters, 31 critical cells; P 688, P-short 645, P-latency 688, P-pu-stage 647 s
kmedoids k4-s12: 4 clusters, 26 critical cells; P 712, P-short 720, P-latency 760, P-pu-stage 689 s
kmedoids k4-s13: 4 clusters, 25 critical cells; P 701, P-short 767, P-latency 701, P-pu-stage 661 s
kmedoids k4-s20: 4 clusters, 21 critical cells; P 637, P-short 646, P-latency 642, P-pu-stage 632 s
kmedoids k4-s16: 4 clusters, 30 critical cells; P 755, P-short 726, P-latency 761, P-pu-stage 681 s
kmedoids k4-s5: 4 clusters, 24 critical cells; P 630, P-short 621, P-latency 630, P-pu-stage 569 s
kmedoids k4-s21: 4 clusters, 29 critical cells; P 717, P-short 683, P-latency 717, P-pu-stage 591 s
kmedoids k4-s9: 4 clusters, 31 critical cells; P 789, P-short 705, P-latency 789, P-pu-stage 732 s
kmedoids k6-s11: 6 clusters, 34 critical cells; P 757, P-short 708, P-latency 757, P-pu-stage 720 s
kmedoids k6-s12: 6 clusters, 36 critical cells; P 823, P-short 788, P-latency 788, P-pu-stage 841 s
kmedoids k6-s13: 6 clusters, 43 critical cells; P 801, P-short 793, P-latency 697, P-pu-stage 709 s
kmedoids k6-s15: 6 clusters, 40 critical cells; P 784, P-short 784, P-latency 784, P-pu-stage 797 s
kmedoids k6-s16: 6 clusters, 40 critical cells; P 885, P-short 940, P-latency 899, P-pu-stage 884 s
kmedoids k6-s17: 6 clusters, 36 critical cells; P 778, P-short 778, P-latency 723, P-pu-stage 817 s
kmedoids k6-s2: 6 clusters, 44 critical cells; P 788, P-short 721, P-latency 721, P-pu-stage 741 s
kmedoids k6-s20: 6 clusters, 43 critical cells; P 838, P-short 842, P-latency 838, P-pu-stage 786 s
kmedoids k6-s9: 6 clusters, 38 critical cells; P 874, P-short 883, P-latency 874, P-pu-stage 829 s
kmedoids k8-s1: 8 clusters, 49 critical cells; P 966, P-short 847, P-latency 862, P-pu-stage 954 s
kmedoids k8-s10: 8 clusters, 45 critical cells; P 825, P-short 831, P-latency 831, P-pu-stage 848 s
kmedoids k8-s11: 8 clusters, 51 critical cells; P 863, P-short 863, P-latency 828, P-pu-stage 904 s
kmedoids k8-s2: 8 clusters, 50 critical cells; P 752, P-short 752, P-latency 752, P-pu-stage 838 s
kmedoids k8-s5: 8 clusters, 47 critical cells; P 941, P-short 992, P-latency 965, P-pu-stage 974 s
kmedoids k8-s6: 8 clusters, 54 critical cells; P 795, P-short 792, P-latency 753, P-pu-stage 821 s
kmedoids k8-s7: 8 clusters, 55 critical cells; P 942, P-short 849, P-latency 837, P-pu-stage 963 s
kmedoids k8-s8: 8 clusters, 48 critical cells; P 835, P-short 873, P-latency 863, P-pu-stage 810 s
kmedoids k8-s9: 8 clusters, 50 critical cells; P 957, P-short 834, P-latency 910, P-pu-stage 853 s
```
