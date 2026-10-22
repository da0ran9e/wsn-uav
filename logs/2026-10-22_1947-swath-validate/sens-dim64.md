# Độ nhạy lớp 1: D = 64, k-medoids vs CHORD-T

- Bắt đầu: 2026-10-22 23:09:12, chạy 88 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/l1_rank.py --set kmedoids '/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/VB/kmedoids/*' --set chordT1 '/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/VB/chordT1/*' --set chordT3 '/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/VB/chordT3/*' --draws 100 --methods P+prog-kin-puq-stage-zero-redir,P+prog-skin-puq-stage-zero-redir,B4-kin-puq-stage-zero-redir,B4-skin-puq-stage-zero-redir --jobs 4 --dim 64 --out /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/VB/sens64
```

**Kết quả**

```text
kmedoids k2-s10: 2 clusters, 11 critical cells; P+prog-kin-puq-stage-zero-redir 443, P+prog-skin-puq-stage-zero-redir 443, B4-kin-puq-stage-zero-redir 462, B4-skin-puq-stage-zero-redir 462 s
kmedoids k2-s23: 2 clusters, 11 critical cells; P+prog-kin-puq-stage-zero-redir 503, P+prog-skin-puq-stage-zero-redir 503, B4-kin-puq-stage-zero-redir 504, B4-skin-puq-stage-zero-redir 504 s
kmedoids k2-s9: 2 clusters, 13 critical cells; P+prog-kin-puq-stage-zero-redir 461, P+prog-skin-puq-stage-zero-redir 461, B4-kin-puq-stage-zero-redir 474, B4-skin-puq-stage-zero-redir 474 s
kmedoids k2-s4: 2 clusters, 13 critical cells; P+prog-kin-puq-stage-zero-redir 464, P+prog-skin-puq-stage-zero-redir 464, B4-kin-puq-stage-zero-redir 481, B4-skin-puq-stage-zero-redir 481 s
kmedoids k4-s20: 4 clusters, 20 critical cells; P+prog-kin-puq-stage-zero-redir 700, P+prog-skin-puq-stage-zero-redir 700, B4-kin-puq-stage-zero-redir 722, B4-skin-puq-stage-zero-redir 722 s
kmedoids k4-s13: 4 clusters, 23 critical cells; P+prog-kin-puq-stage-zero-redir 704, P+prog-skin-puq-stage-zero-redir 704, B4-kin-puq-stage-zero-redir 683, B4-skin-puq-stage-zero-redir 683 s
kmedoids k4-s2: 4 clusters, 24 critical cells; P+prog-kin-puq-stage-zero-redir 643, P+prog-skin-puq-stage-zero-redir 643, B4-kin-puq-stage-zero-redir 667, B4-skin-puq-stage-zero-redir 667 s
kmedoids k4-s21: 4 clusters, 26 critical cells; P+prog-kin-puq-stage-zero-redir 644, P+prog-skin-puq-stage-zero-redir 644, B4-kin-puq-stage-zero-redir 727, B4-skin-puq-stage-zero-redir 727 s
kmedoids k6-s11: 6 clusters, 33 critical cells; P+prog-kin-puq-stage-zero-redir 841, P+prog-skin-puq-stage-zero-redir 841, B4-kin-puq-stage-zero-redir 857, B4-skin-puq-stage-zero-redir 857 s
kmedoids k6-s9: 6 clusters, 35 critical cells; P+prog-kin-puq-stage-zero-redir 868, P+prog-skin-puq-stage-zero-redir 868, B4-kin-puq-stage-zero-redir 893, B4-skin-puq-stage-zero-redir 893 s
kmedoids k6-s13: 6 clusters, 39 critical cells; P+prog-kin-puq-stage-zero-redir 812, P+prog-skin-puq-stage-zero-redir 812, B4-kin-puq-stage-zero-redir 888, B4-skin-puq-stage-zero-redir 888 s
kmedoids k6-s20: 6 clusters, 39 critical cells; P+prog-kin-puq-stage-zero-redir 897, P+prog-skin-puq-stage-zero-redir 897, B4-kin-puq-stage-zero-redir 913, B4-skin-puq-stage-zero-redir 913 s
kmedoids k8-s1: 8 clusters, 45 critical cells; P+prog-kin-puq-stage-zero-redir 932, P+prog-skin-puq-stage-zero-redir 936, B4-kin-puq-stage-zero-redir 986, B4-skin-puq-stage-zero-redir 990 s
kmedoids k8-s8: 8 clusters, 43 critical cells; P+prog-kin-puq-stage-zero-redir 1013, P+prog-skin-puq-stage-zero-redir 1013, B4-kin-puq-stage-zero-redir 1072, B4-skin-puq-stage-zero-redir 1072 s
kmedoids k8-s10: 8 clusters, 44 critical cells; P+prog-kin-puq-stage-zero-redir 1031, P+prog-skin-puq-stage-zero-redir 1021, B4-kin-puq-stage-zero-redir 1025, B4-skin-puq-stage-zero-redir 1019 s
chordT1 k2-s10: 2 clusters, 11 critical cells; P+prog-kin-puq-stage-zero-redir 446, P+prog-skin-puq-stage-zero-redir 446, B4-kin-puq-stage-zero-redir 469, B4-skin-puq-stage-zero-redir 469 s
chordT1 k2-s23: 2 clusters, 11 critical cells; P+prog-kin-puq-stage-zero-redir 477, P+prog-skin-puq-stage-zero-redir 477, B4-kin-puq-stage-zero-redir 515, B4-skin-puq-stage-zero-redir 515 s
kmedoids k8-s11: 8 clusters, 46 critical cells; P+prog-kin-puq-stage-zero-redir 969, P+prog-skin-puq-stage-zero-redir 952, B4-kin-puq-stage-zero-redir 1032, B4-skin-puq-stage-zero-redir 1004 s
chordT1 k2-s4: 2 clusters, 13 critical cells; P+prog-kin-puq-stage-zero-redir 462, P+prog-skin-puq-stage-zero-redir 462, B4-kin-puq-stage-zero-redir 469, B4-skin-puq-stage-zero-redir 469 s
chordT1 k2-s9: 2 clusters, 13 critical cells; P+prog-kin-puq-stage-zero-redir 461, P+prog-skin-puq-stage-zero-redir 461, B4-kin-puq-stage-zero-redir 482, B4-skin-puq-stage-zero-redir 482 s
chordT1 k4-s20: 4 clusters, 20 critical cells; P+prog-kin-puq-stage-zero-redir 659, P+prog-skin-puq-stage-zero-redir 659, B4-kin-puq-stage-zero-redir 767, B4-skin-puq-stage-zero-redir 767 s
chordT1 k4-s13: 4 clusters, 23 critical cells; P+prog-kin-puq-stage-zero-redir 682, P+prog-skin-puq-stage-zero-redir 682, B4-kin-puq-stage-zero-redir 712, B4-skin-puq-stage-zero-redir 712 s
chordT1 k4-s2: 4 clusters, 24 critical cells; P+prog-kin-puq-stage-zero-redir 639, P+prog-skin-puq-stage-zero-redir 639, B4-kin-puq-stage-zero-redir 734, B4-skin-puq-stage-zero-redir 734 s
chordT1 k4-s21: 4 clusters, 26 critical cells; P+prog-kin-puq-stage-zero-redir 601, P+prog-skin-puq-stage-zero-redir 601, B4-kin-puq-stage-zero-redir 811, B4-skin-puq-stage-zero-redir 811 s
chordT1 k6-s11: 6 clusters, 33 critical cells; P+prog-kin-puq-stage-zero-redir 808, P+prog-skin-puq-stage-zero-redir 811, B4-kin-puq-stage-zero-redir 852, B4-skin-puq-stage-zero-redir 849 s
chordT1 k6-s9: 6 clusters, 35 critical cells; P+prog-kin-puq-stage-zero-redir 782, P+prog-skin-puq-stage-zero-redir 782, B4-kin-puq-stage-zero-redir 1027, B4-skin-puq-stage-zero-redir 1027 s
chordT1 k6-s13: 6 clusters, 39 critical cells; P+prog-kin-puq-stage-zero-redir 788, P+prog-skin-puq-stage-zero-redir 788, B4-kin-puq-stage-zero-redir 879, B4-skin-puq-stage-zero-redir 879 s
chordT1 k6-s20: 6 clusters, 39 critical cells; P+prog-kin-puq-stage-zero-redir 885, P+prog-skin-puq-stage-zero-redir 885, B4-kin-puq-stage-zero-redir 867, B4-skin-puq-stage-zero-redir 867 s
chordT1 k8-s1: 8 clusters, 45 critical cells; P+prog-kin-puq-stage-zero-redir 885, P+prog-skin-puq-stage-zero-redir 885, B4-kin-puq-stage-zero-redir 988, B4-skin-puq-stage-zero-redir 988 s
chordT1 k8-s10: 8 clusters, 44 critical cells; P+prog-kin-puq-stage-zero-redir 993, P+prog-skin-puq-stage-zero-redir 993, B4-kin-puq-stage-zero-redir 1031, B4-skin-puq-stage-zero-redir 1031 s
chordT3 k2-s10: 2 clusters, 11 critical cells; P+prog-kin-puq-stage-zero-redir 455, P+prog-skin-puq-stage-zero-redir 455, B4-kin-puq-stage-zero-redir 487, B4-skin-puq-stage-zero-redir 487 s
chordT1 k8-s8: 8 clusters, 43 critical cells; P+prog-kin-puq-stage-zero-redir 967, P+prog-skin-puq-stage-zero-redir 967, B4-kin-puq-stage-zero-redir 996, B4-skin-puq-stage-zero-redir 996 s
chordT3 k2-s23: 2 clusters, 11 critical cells; P+prog-kin-puq-stage-zero-redir 479, P+prog-skin-puq-stage-zero-redir 479, B4-kin-puq-stage-zero-redir 545, B4-skin-puq-stage-zero-redir 545 s
chordT1 k8-s11: 8 clusters, 46 critical cells; P+prog-kin-puq-stage-zero-redir 878, P+prog-skin-puq-stage-zero-redir 878, B4-kin-puq-stage-zero-redir 966, B4-skin-puq-stage-zero-redir 966 s
chordT3 k2-s4: 2 clusters, 13 critical cells; P+prog-kin-puq-stage-zero-redir 463, P+prog-skin-puq-stage-zero-redir 463, B4-kin-puq-stage-zero-redir 485, B4-skin-puq-stage-zero-redir 485 s
chordT3 k2-s9: 2 clusters, 13 critical cells; P+prog-kin-puq-stage-zero-redir 446, P+prog-skin-puq-stage-zero-redir 446, B4-kin-puq-stage-zero-redir 443, B4-skin-puq-stage-zero-redir 443 s
chordT3 k4-s20: 4 clusters, 20 critical cells; P+prog-kin-puq-stage-zero-redir 667, P+prog-skin-puq-stage-zero-redir 667, B4-kin-puq-stage-zero-redir 775, B4-skin-puq-stage-zero-redir 775 s
chordT3 k4-s13: 4 clusters, 23 critical cells; P+prog-kin-puq-stage-zero-redir 662, P+prog-skin-puq-stage-zero-redir 662, B4-kin-puq-stage-zero-redir 730, B4-skin-puq-stage-zero-redir 730 s
chordT3 k4-s2: 4 clusters, 24 critical cells; P+prog-kin-puq-stage-zero-redir 639, P+prog-skin-puq-stage-zero-redir 639, B4-kin-puq-stage-zero-redir 734, B4-skin-puq-stage-zero-redir 734 s
chordT3 k4-s21: 4 clusters, 26 critical cells; P+prog-kin-puq-stage-zero-redir 624, P+prog-skin-puq-stage-zero-redir 624, B4-kin-puq-stage-zero-redir 877, B4-skin-puq-stage-zero-redir 877 s
chordT3 k6-s11: 6 clusters, 33 critical cells; P+prog-kin-puq-stage-zero-redir 789, P+prog-skin-puq-stage-zero-redir 789, B4-kin-puq-stage-zero-redir 824, B4-skin-puq-stage-zero-redir 824 s
chordT3 k6-s13: 6 clusters, 39 critical cells; P+prog-kin-puq-stage-zero-redir 775, P+prog-skin-puq-stage-zero-redir 775, B4-kin-puq-stage-zero-redir 841, B4-skin-puq-stage-zero-redir 841 s
chordT3 k6-s9: 6 clusters, 35 critical cells; P+prog-kin-puq-stage-zero-redir 783, P+prog-skin-puq-stage-zero-redir 783, B4-kin-puq-stage-zero-redir 1039, B4-skin-puq-stage-zero-redir 1039 s
chordT3 k6-s20: 6 clusters, 39 critical cells; P+prog-kin-puq-stage-zero-redir 885, P+prog-skin-puq-stage-zero-redir 885, B4-kin-puq-stage-zero-redir 894, B4-skin-puq-stage-zero-redir 894 s
chordT3 k8-s1: 8 clusters, 45 critical cells; P+prog-kin-puq-stage-zero-redir 859, P+prog-skin-puq-stage-zero-redir 859, B4-kin-puq-stage-zero-redir 921, B4-skin-puq-stage-zero-redir 921 s
chordT3 k8-s10: 8 clusters, 44 critical cells; P+prog-kin-puq-stage-zero-redir 964, P+prog-skin-puq-stage-zero-redir 964, B4-kin-puq-stage-zero-redir 1000, B4-skin-puq-stage-zero-redir 1000 s
chordT3 k8-s8: 8 clusters, 43 critical cells; P+prog-kin-puq-stage-zero-redir 942, P+prog-skin-puq-stage-zero-redir 942, B4-kin-puq-stage-zero-redir 1087, B4-skin-puq-stage-zero-redir 1087 s
chordT3 k8-s11: 8 clusters, 46 critical cells; P+prog-kin-puq-stage-zero-redir 878, P+prog-skin-puq-stage-zero-redir 878, B4-kin-puq-stage-zero-redir 966, B4-skin-puq-stage-zero-redir 966 s
```
