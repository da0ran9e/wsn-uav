# 16 bản đồ, ghép cặp: k-medoids vs SWATH-K

- Bắt đầu: 2026-10-22 20:32:11, chạy 127 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/l1_rank.py --set kmedoids '/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/VB/kmedoids/*' --set swath '/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/VB/swath/*' --draws 100 --methods P+prog-kin-puq-stage-zero-redir,P+prog-skin-puq-stage-zero-redir,B4-kin-puq-stage-zero-redir,B4-skin-puq-stage-zero-redir,B7 --jobs 2 --out /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/VB/v16
```

**Kết quả**

```text
kmedoids k2-s23: 2 clusters, 11 critical cells; P+prog-kin-puq-stage-zero-redir 447, P+prog-skin-puq-stage-zero-redir 447, B4-kin-puq-stage-zero-redir 456, B4-skin-puq-stage-zero-redir 456 s
kmedoids k2-s10: 2 clusters, 11 critical cells; P+prog-kin-puq-stage-zero-redir 394, P+prog-skin-puq-stage-zero-redir 394, B4-kin-puq-stage-zero-redir 395, B4-skin-puq-stage-zero-redir 395 s
kmedoids k2-s9: 2 clusters, 13 critical cells; P+prog-kin-puq-stage-zero-redir 409, P+prog-skin-puq-stage-zero-redir 409, B4-kin-puq-stage-zero-redir 437, B4-skin-puq-stage-zero-redir 437 s
kmedoids k2-s4: 2 clusters, 13 critical cells; P+prog-kin-puq-stage-zero-redir 392, P+prog-skin-puq-stage-zero-redir 392, B4-kin-puq-stage-zero-redir 403, B4-skin-puq-stage-zero-redir 403 s
kmedoids k4-s13: 4 clusters, 23 critical cells; P+prog-kin-puq-stage-zero-redir 565, P+prog-skin-puq-stage-zero-redir 565, B4-kin-puq-stage-zero-redir 586, B4-skin-puq-stage-zero-redir 586 s
kmedoids k4-s2: 4 clusters, 24 critical cells; P+prog-kin-puq-stage-zero-redir 535, P+prog-skin-puq-stage-zero-redir 535, B4-kin-puq-stage-zero-redir 551, B4-skin-puq-stage-zero-redir 551 s
kmedoids k4-s20: 4 clusters, 20 critical cells; P+prog-kin-puq-stage-zero-redir 572, P+prog-skin-puq-stage-zero-redir 572, B4-kin-puq-stage-zero-redir 584, B4-skin-puq-stage-zero-redir 584 s
kmedoids k4-s21: 4 clusters, 26 critical cells; P+prog-kin-puq-stage-zero-redir 547, P+prog-skin-puq-stage-zero-redir 547, B4-kin-puq-stage-zero-redir 576, B4-skin-puq-stage-zero-redir 576 s
kmedoids k6-s11: 6 clusters, 33 critical cells; P+prog-kin-puq-stage-zero-redir 713, P+prog-skin-puq-stage-zero-redir 713, B4-kin-puq-stage-zero-redir 717, B4-skin-puq-stage-zero-redir 717 s
kmedoids k6-s13: 6 clusters, 39 critical cells; P+prog-kin-puq-stage-zero-redir 653, P+prog-skin-puq-stage-zero-redir 653, B4-kin-puq-stage-zero-redir 676, B4-skin-puq-stage-zero-redir 676 s
kmedoids k6-s20: 6 clusters, 39 critical cells; P+prog-kin-puq-stage-zero-redir 714, P+prog-skin-puq-stage-zero-redir 714, B4-kin-puq-stage-zero-redir 719, B4-skin-puq-stage-zero-redir 719 s
kmedoids k6-s9: 6 clusters, 35 critical cells; P+prog-kin-puq-stage-zero-redir 725, P+prog-skin-puq-stage-zero-redir 725, B4-kin-puq-stage-zero-redir 744, B4-skin-puq-stage-zero-redir 744 s
kmedoids k8-s1: 8 clusters, 45 critical cells; P+prog-kin-puq-stage-zero-redir 785, P+prog-skin-puq-stage-zero-redir 767, B4-kin-puq-stage-zero-redir 835, B4-skin-puq-stage-zero-redir 827 s
kmedoids k8-s10: 8 clusters, 44 critical cells; P+prog-kin-puq-stage-zero-redir 810, P+prog-skin-puq-stage-zero-redir 825, B4-kin-puq-stage-zero-redir 791, B4-skin-puq-stage-zero-redir 801 s
kmedoids k8-s11: 8 clusters, 46 critical cells; P+prog-kin-puq-stage-zero-redir 786, P+prog-skin-puq-stage-zero-redir 767, B4-kin-puq-stage-zero-redir 836, B4-skin-puq-stage-zero-redir 817 s
kmedoids k8-s8: 8 clusters, 43 critical cells; P+prog-kin-puq-stage-zero-redir 822, P+prog-skin-puq-stage-zero-redir 822, B4-kin-puq-stage-zero-redir 853, B4-skin-puq-stage-zero-redir 853 s
swath k2-s10: 2 clusters, 15 critical cells; P+prog-kin-puq-stage-zero-redir 439, P+prog-skin-puq-stage-zero-redir 419, B4-kin-puq-stage-zero-redir 461, B4-skin-puq-stage-zero-redir 448 s
swath k2-s23: 2 clusters, 13 critical cells; P+prog-kin-puq-stage-zero-redir 529, P+prog-skin-puq-stage-zero-redir 512, B4-kin-puq-stage-zero-redir 558, B4-skin-puq-stage-zero-redir 549 s
swath k2-s4: 2 clusters, 13 critical cells; P+prog-kin-puq-stage-zero-redir 516, P+prog-skin-puq-stage-zero-redir 497, B4-kin-puq-stage-zero-redir 513, B4-skin-puq-stage-zero-redir 495 s
swath k2-s9: 2 clusters, 13 critical cells; P+prog-kin-puq-stage-zero-redir 454, P+prog-skin-puq-stage-zero-redir 444, B4-kin-puq-stage-zero-redir 441, B4-skin-puq-stage-zero-redir 438 s
swath k4-s13: 4 clusters, 23 critical cells; P+prog-kin-puq-stage-zero-redir 633, P+prog-skin-puq-stage-zero-redir 563, B4-kin-puq-stage-zero-redir 633, B4-skin-puq-stage-zero-redir 580 s
swath k4-s2: 4 clusters, 23 critical cells; P+prog-kin-puq-stage-zero-redir 617, P+prog-skin-puq-stage-zero-redir 569, B4-kin-puq-stage-zero-redir 638, B4-skin-puq-stage-zero-redir 607 s
swath k4-s20: 4 clusters, 25 critical cells; P+prog-kin-puq-stage-zero-redir 679, P+prog-skin-puq-stage-zero-redir 605, B4-kin-puq-stage-zero-redir 708, B4-skin-puq-stage-zero-redir 624 s
swath k4-s21: 4 clusters, 27 critical cells; P+prog-kin-puq-stage-zero-redir 568, P+prog-skin-puq-stage-zero-redir 542, B4-kin-puq-stage-zero-redir 603, B4-skin-puq-stage-zero-redir 586 s
swath k6-s11: 6 clusters, 36 critical cells; P+prog-kin-puq-stage-zero-redir 781, P+prog-skin-puq-stage-zero-redir 672, B4-kin-puq-stage-zero-redir 786, B4-skin-puq-stage-zero-redir 685 s
swath k6-s13: 6 clusters, 41 critical cells; P+prog-kin-puq-stage-zero-redir 699, P+prog-skin-puq-stage-zero-redir 593, B4-kin-puq-stage-zero-redir 746, B4-skin-puq-stage-zero-redir 633 s
swath k6-s20: 6 clusters, 38 critical cells; P+prog-kin-puq-stage-zero-redir 824, P+prog-skin-puq-stage-zero-redir 708, B4-kin-puq-stage-zero-redir 837, B4-skin-puq-stage-zero-redir 734 s
swath k6-s9: 6 clusters, 39 critical cells; P+prog-kin-puq-stage-zero-redir 846, P+prog-skin-puq-stage-zero-redir 719, B4-kin-puq-stage-zero-redir 868, B4-skin-puq-stage-zero-redir 731 s
swath k8-s1: 8 clusters, 43 critical cells; P+prog-kin-puq-stage-zero-redir 887, P+prog-skin-puq-stage-zero-redir 778, B4-kin-puq-stage-zero-redir 939, B4-skin-puq-stage-zero-redir 824 s
swath k8-s10: 8 clusters, 43 critical cells; P+prog-kin-puq-stage-zero-redir 957, P+prog-skin-puq-stage-zero-redir 797, B4-kin-puq-stage-zero-redir 987, B4-skin-puq-stage-zero-redir 825 s
swath k8-s8: 8 clusters, 42 critical cells; P+prog-kin-puq-stage-zero-redir 815, P+prog-skin-puq-stage-zero-redir 741, B4-kin-puq-stage-zero-redir 883, B4-skin-puq-stage-zero-redir 795 s
swath k8-s11: 8 clusters, 51 critical cells; P+prog-kin-puq-stage-zero-redir 893, P+prog-skin-puq-stage-zero-redir 771, B4-kin-puq-stage-zero-redir 919, B4-skin-puq-stage-zero-redir 782 s
```
