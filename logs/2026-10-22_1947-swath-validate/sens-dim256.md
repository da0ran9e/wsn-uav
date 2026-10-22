# Độ nhạy lớp 1: D = 256, k-medoids vs CHORD-T

- Bắt đầu: 2026-10-22 23:10:40, chạy 86 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/l1_rank.py --set kmedoids '/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/VB/kmedoids/*' --set chordT1 '/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/VB/chordT1/*' --set chordT3 '/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/VB/chordT3/*' --draws 100 --methods P+prog-kin-puq-stage-zero-redir,P+prog-skin-puq-stage-zero-redir,B4-kin-puq-stage-zero-redir,B4-skin-puq-stage-zero-redir --jobs 4 --dim 256 --out /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/VB/sens256
```

**Kết quả**

```text
kmedoids k2-s23: 2 clusters, 11 critical cells; P+prog-kin-puq-stage-zero-redir 403, P+prog-skin-puq-stage-zero-redir 403, B4-kin-puq-stage-zero-redir 417, B4-skin-puq-stage-zero-redir 417 s
kmedoids k2-s10: 2 clusters, 11 critical cells; P+prog-kin-puq-stage-zero-redir 368, P+prog-skin-puq-stage-zero-redir 368, B4-kin-puq-stage-zero-redir 360, B4-skin-puq-stage-zero-redir 360 s
kmedoids k2-s4: 2 clusters, 13 critical cells; P+prog-kin-puq-stage-zero-redir 354, P+prog-skin-puq-stage-zero-redir 354, B4-kin-puq-stage-zero-redir 364, B4-skin-puq-stage-zero-redir 364 s
kmedoids k2-s9: 2 clusters, 13 critical cells; P+prog-kin-puq-stage-zero-redir 363, P+prog-skin-puq-stage-zero-redir 363, B4-kin-puq-stage-zero-redir 382, B4-skin-puq-stage-zero-redir 382 s
kmedoids k4-s20: 4 clusters, 20 critical cells; P+prog-kin-puq-stage-zero-redir 492, P+prog-skin-puq-stage-zero-redir 492, B4-kin-puq-stage-zero-redir 500, B4-skin-puq-stage-zero-redir 500 s
kmedoids k4-s13: 4 clusters, 23 critical cells; P+prog-kin-puq-stage-zero-redir 481, P+prog-skin-puq-stage-zero-redir 481, B4-kin-puq-stage-zero-redir 492, B4-skin-puq-stage-zero-redir 492 s
kmedoids k4-s2: 4 clusters, 24 critical cells; P+prog-kin-puq-stage-zero-redir 502, P+prog-skin-puq-stage-zero-redir 502, B4-kin-puq-stage-zero-redir 507, B4-skin-puq-stage-zero-redir 507 s
kmedoids k4-s21: 4 clusters, 26 critical cells; P+prog-kin-puq-stage-zero-redir 519, P+prog-skin-puq-stage-zero-redir 519, B4-kin-puq-stage-zero-redir 539, B4-skin-puq-stage-zero-redir 539 s
kmedoids k6-s11: 6 clusters, 33 critical cells; P+prog-kin-puq-stage-zero-redir 614, P+prog-skin-puq-stage-zero-redir 614, B4-kin-puq-stage-zero-redir 647, B4-skin-puq-stage-zero-redir 647 s
kmedoids k6-s9: 6 clusters, 35 critical cells; P+prog-kin-puq-stage-zero-redir 664, P+prog-skin-puq-stage-zero-redir 664, B4-kin-puq-stage-zero-redir 665, B4-skin-puq-stage-zero-redir 665 s
kmedoids k6-s13: 6 clusters, 39 critical cells; P+prog-kin-puq-stage-zero-redir 575, P+prog-skin-puq-stage-zero-redir 575, B4-kin-puq-stage-zero-redir 580, B4-skin-puq-stage-zero-redir 580 s
kmedoids k6-s20: 6 clusters, 39 critical cells; P+prog-kin-puq-stage-zero-redir 632, P+prog-skin-puq-stage-zero-redir 632, B4-kin-puq-stage-zero-redir 626, B4-skin-puq-stage-zero-redir 626 s
kmedoids k8-s1: 8 clusters, 45 critical cells; P+prog-kin-puq-stage-zero-redir 713, P+prog-skin-puq-stage-zero-redir 697, B4-kin-puq-stage-zero-redir 734, B4-skin-puq-stage-zero-redir 707 s
chordT1 k2-s10: 2 clusters, 11 critical cells; P+prog-kin-puq-stage-zero-redir 362, P+prog-skin-puq-stage-zero-redir 362, B4-kin-puq-stage-zero-redir 367, B4-skin-puq-stage-zero-redir 367 s
kmedoids k8-s10: 8 clusters, 44 critical cells; P+prog-kin-puq-stage-zero-redir 675, P+prog-skin-puq-stage-zero-redir 686, B4-kin-puq-stage-zero-redir 668, B4-skin-puq-stage-zero-redir 670 s
kmedoids k8-s8: 8 clusters, 43 critical cells; P+prog-kin-puq-stage-zero-redir 717, P+prog-skin-puq-stage-zero-redir 717, B4-kin-puq-stage-zero-redir 750, B4-skin-puq-stage-zero-redir 750 s
chordT1 k2-s23: 2 clusters, 11 critical cells; P+prog-kin-puq-stage-zero-redir 382, P+prog-skin-puq-stage-zero-redir 382, B4-kin-puq-stage-zero-redir 403, B4-skin-puq-stage-zero-redir 403 s
kmedoids k8-s11: 8 clusters, 46 critical cells; P+prog-kin-puq-stage-zero-redir 703, P+prog-skin-puq-stage-zero-redir 682, B4-kin-puq-stage-zero-redir 773, B4-skin-puq-stage-zero-redir 743 s
chordT1 k2-s4: 2 clusters, 13 critical cells; P+prog-kin-puq-stage-zero-redir 347, P+prog-skin-puq-stage-zero-redir 347, B4-kin-puq-stage-zero-redir 360, B4-skin-puq-stage-zero-redir 360 s
chordT1 k2-s9: 2 clusters, 13 critical cells; P+prog-kin-puq-stage-zero-redir 359, P+prog-skin-puq-stage-zero-redir 359, B4-kin-puq-stage-zero-redir 382, B4-skin-puq-stage-zero-redir 382 s
chordT1 k4-s13: 4 clusters, 23 critical cells; P+prog-kin-puq-stage-zero-redir 466, P+prog-skin-puq-stage-zero-redir 466, B4-kin-puq-stage-zero-redir 491, B4-skin-puq-stage-zero-redir 491 s
chordT1 k4-s20: 4 clusters, 20 critical cells; P+prog-kin-puq-stage-zero-redir 464, P+prog-skin-puq-stage-zero-redir 464, B4-kin-puq-stage-zero-redir 553, B4-skin-puq-stage-zero-redir 553 s
chordT1 k4-s2: 4 clusters, 24 critical cells; P+prog-kin-puq-stage-zero-redir 487, P+prog-skin-puq-stage-zero-redir 487, B4-kin-puq-stage-zero-redir 514, B4-skin-puq-stage-zero-redir 514 s
chordT1 k4-s21: 4 clusters, 26 critical cells; P+prog-kin-puq-stage-zero-redir 455, P+prog-skin-puq-stage-zero-redir 455, B4-kin-puq-stage-zero-redir 551, B4-skin-puq-stage-zero-redir 551 s
chordT1 k6-s11: 6 clusters, 33 critical cells; P+prog-kin-puq-stage-zero-redir 577, P+prog-skin-puq-stage-zero-redir 594, B4-kin-puq-stage-zero-redir 608, B4-skin-puq-stage-zero-redir 628 s
chordT1 k6-s13: 6 clusters, 39 critical cells; P+prog-kin-puq-stage-zero-redir 549, P+prog-skin-puq-stage-zero-redir 549, B4-kin-puq-stage-zero-redir 565, B4-skin-puq-stage-zero-redir 565 s
chordT1 k6-s9: 6 clusters, 35 critical cells; P+prog-kin-puq-stage-zero-redir 584, P+prog-skin-puq-stage-zero-redir 584, B4-kin-puq-stage-zero-redir 686, B4-skin-puq-stage-zero-redir 686 s
chordT1 k6-s20: 6 clusters, 39 critical cells; P+prog-kin-puq-stage-zero-redir 620, P+prog-skin-puq-stage-zero-redir 620, B4-kin-puq-stage-zero-redir 633, B4-skin-puq-stage-zero-redir 633 s
chordT1 k8-s1: 8 clusters, 45 critical cells; P+prog-kin-puq-stage-zero-redir 666, P+prog-skin-puq-stage-zero-redir 666, B4-kin-puq-stage-zero-redir 686, B4-skin-puq-stage-zero-redir 686 s
chordT3 k2-s10: 2 clusters, 11 critical cells; P+prog-kin-puq-stage-zero-redir 359, P+prog-skin-puq-stage-zero-redir 359, B4-kin-puq-stage-zero-redir 363, B4-skin-puq-stage-zero-redir 363 s
chordT1 k8-s10: 8 clusters, 44 critical cells; P+prog-kin-puq-stage-zero-redir 642, P+prog-skin-puq-stage-zero-redir 642, B4-kin-puq-stage-zero-redir 642, B4-skin-puq-stage-zero-redir 642 s
chordT1 k8-s8: 8 clusters, 43 critical cells; P+prog-kin-puq-stage-zero-redir 677, P+prog-skin-puq-stage-zero-redir 677, B4-kin-puq-stage-zero-redir 699, B4-skin-puq-stage-zero-redir 699 s
chordT3 k2-s23: 2 clusters, 11 critical cells; P+prog-kin-puq-stage-zero-redir 390, P+prog-skin-puq-stage-zero-redir 390, B4-kin-puq-stage-zero-redir 409, B4-skin-puq-stage-zero-redir 409 s
chordT3 k2-s4: 2 clusters, 13 critical cells; P+prog-kin-puq-stage-zero-redir 351, P+prog-skin-puq-stage-zero-redir 351, B4-kin-puq-stage-zero-redir 363, B4-skin-puq-stage-zero-redir 363 s
chordT1 k8-s11: 8 clusters, 46 critical cells; P+prog-kin-puq-stage-zero-redir 625, P+prog-skin-puq-stage-zero-redir 625, B4-kin-puq-stage-zero-redir 700, B4-skin-puq-stage-zero-redir 700 s
chordT3 k2-s9: 2 clusters, 13 critical cells; P+prog-kin-puq-stage-zero-redir 362, P+prog-skin-puq-stage-zero-redir 362, B4-kin-puq-stage-zero-redir 362, B4-skin-puq-stage-zero-redir 362 s
chordT3 k4-s13: 4 clusters, 23 critical cells; P+prog-kin-puq-stage-zero-redir 463, P+prog-skin-puq-stage-zero-redir 463, B4-kin-puq-stage-zero-redir 492, B4-skin-puq-stage-zero-redir 492 s
chordT3 k4-s20: 4 clusters, 20 critical cells; P+prog-kin-puq-stage-zero-redir 462, P+prog-skin-puq-stage-zero-redir 462, B4-kin-puq-stage-zero-redir 550, B4-skin-puq-stage-zero-redir 550 s
chordT3 k4-s2: 4 clusters, 24 critical cells; P+prog-kin-puq-stage-zero-redir 487, P+prog-skin-puq-stage-zero-redir 487, B4-kin-puq-stage-zero-redir 514, B4-skin-puq-stage-zero-redir 514 s
chordT3 k4-s21: 4 clusters, 26 critical cells; P+prog-kin-puq-stage-zero-redir 452, P+prog-skin-puq-stage-zero-redir 452, B4-kin-puq-stage-zero-redir 561, B4-skin-puq-stage-zero-redir 561 s
chordT3 k6-s11: 6 clusters, 33 critical cells; P+prog-kin-puq-stage-zero-redir 572, P+prog-skin-puq-stage-zero-redir 572, B4-kin-puq-stage-zero-redir 599, B4-skin-puq-stage-zero-redir 599 s
chordT3 k6-s13: 6 clusters, 39 critical cells; P+prog-kin-puq-stage-zero-redir 528, P+prog-skin-puq-stage-zero-redir 528, B4-kin-puq-stage-zero-redir 533, B4-skin-puq-stage-zero-redir 533 s
chordT3 k6-s9: 6 clusters, 35 critical cells; P+prog-kin-puq-stage-zero-redir 581, P+prog-skin-puq-stage-zero-redir 581, B4-kin-puq-stage-zero-redir 696, B4-skin-puq-stage-zero-redir 696 s
chordT3 k6-s20: 6 clusters, 39 critical cells; P+prog-kin-puq-stage-zero-redir 614, P+prog-skin-puq-stage-zero-redir 614, B4-kin-puq-stage-zero-redir 622, B4-skin-puq-stage-zero-redir 622 s
chordT3 k8-s1: 8 clusters, 45 critical cells; P+prog-kin-puq-stage-zero-redir 616, P+prog-skin-puq-stage-zero-redir 616, B4-kin-puq-stage-zero-redir 622, B4-skin-puq-stage-zero-redir 622 s
chordT3 k8-s8: 8 clusters, 43 critical cells; P+prog-kin-puq-stage-zero-redir 660, P+prog-skin-puq-stage-zero-redir 660, B4-kin-puq-stage-zero-redir 721, B4-skin-puq-stage-zero-redir 721 s
chordT3 k8-s10: 8 clusters, 44 critical cells; P+prog-kin-puq-stage-zero-redir 637, P+prog-skin-puq-stage-zero-redir 637, B4-kin-puq-stage-zero-redir 629, B4-skin-puq-stage-zero-redir 629 s
chordT3 k8-s11: 8 clusters, 46 critical cells; P+prog-kin-puq-stage-zero-redir 625, P+prog-skin-puq-stage-zero-redir 625, B4-kin-puq-stage-zero-redir 700, B4-skin-puq-stage-zero-redir 700 s
```
