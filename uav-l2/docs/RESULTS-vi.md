# Kết quả CHORD và các baseline, kèm seed để chạy lại (CLAUDE.md §8 mục 166–169, 182)

Tệp này là nơi lưu số liệu so sánh CHORD (P\*) với các baseline FC, DN (mục 1–5) và Pd, B4, B1, B7 (mục 6). Mỗi lần có thêm lượt chạy thì cập nhật tại đây.

**Cập nhật 2026-10-26 (mục 182):** bảng chung bảy phương án trên cùng 12 tổ hợp ở mục 6.

**Trạng thái (2026-10-25, sau mục 169):** đã xong cả 12 tổ hợp: 3 bản đồ (k8-s1, k12-s1, k16-s1; mỗi cỡ một bản đồ chung cho mọi phương án) × 4 kênh (open, r500, r200, r100). Mỗi tổ hợp có 100 lượt bốc lớp 1.

Mục 169 thay đổi CHORD ở hai điểm (mục 2.2). Bảng dưới là số sau thay đổi; số trước đó nằm trong lịch sử git của tệp này (commit `df5b789`).

## 1. Ba phương án
- **CHORD (P\*)**, phương án đề xuất.
  - Cụm k-medoids có sẵn, tối đa 80 cell.
  - Đội 1 bay một đường thẳng qua CH của mỗi cụm; hướng bay và thứ tự cụm chọn chung (`--chordTour 0.6,0.8`).
  - Nối giữa các cụm bằng Dubins; hồ sơ vận tốc theo động học (`--kinPass`).
  - Phát bộ manh mối 400 kB (12 file) dọc Axe; River chuyển dữ liệu tới các critical cell.
  - Từ mục 169, bộ manh mối được mã fountain dạng hệ thống (systematic), cùng loại mã với FC và DN.
    - Cửa sổ River vẫn là các gói gốc, nên kết quả River trên ns-3 vẫn dùng được.
    - Mỗi cell tính mọi gói mã nó nghe được trên cả chuyến bay của đội 1. Nó báo cáo ngay khi tự giải được, hoặc khi River mang đủ, tuỳ cái nào tới trước.
  - River chạy với `--repair 20` (mục 2.2).
  - Phương pháp chấm: `P+prog-kin-puq-stage-zero-redir-kt-fcd`.
  - **CHORD-0** trong bảng: cùng River đã sửa nhưng chưa mã fountain (`P+prog-kin-puq-stage-zero-redir-kt`), để thấy riêng phần đóng góp của mã.
- **FC**, baseline (mục 166).
  - Cùng UAV cánh bằng: 50 m/s, nghiêng 45°, ±2 m/s².
  - Mỗi file mã hoá fountain lý tưởng: file j giải được khi cell giữ đủ (1 + 0,05)·K_j gói mã bất kỳ của nó. Gói các file xen kẽ theo tỉ lệ kích thước, 10 ms một gói, không lặp.
  - Đội 1 bay thẳng tới các critical cell theo thứ tự TSP, không hover. Nếu một lượt bay qua chưa đủ, UAV giảm về 25 m/s và lượn vòng bán kính 64 m tới khi đủ theo kỳ vọng (cộng biên 3√).
  - BS lập cả hai kiểu vòng (qua tâm cell và quanh tâm cell) rồi chọn tour ngắn hơn.
  - Không có River. Mỗi cell tự gom về CL của nó, mất 0,07 + 0,00789 × số gói phải chuyển (giây).
  - Pha 2 như P\*: `FC-puq-stage-zero-redir`.
  - Mã: `uav-l2/tools/fc_baseline.py`.
- **DN**, baseline (mục 168): như FC (mã fountain, không River, gom trong cell), chỉ khác tour.
  - Gom các critical cell gần nhau (gồm cả cell của CH) thành nhóm neighbor nhỏ: gộp dần hai nhóm có tâm gần nhau nhất, miễn là mọi thành viên còn nằm trong bán kính nhóm tính từ tâm.
  - Mỗi nhóm được phục vụ từ một quỹ đạo tròn quanh tâm nhóm. Bán kính bằng khoảng cách tới thành viên xa nhất, kẹp trong [64, 255] m; tốc độ theo nghiêng 45° (25–50 m/s). Neighborhood của nhóm là quỹ đạo này: UAV vào theo tiếp tuyến, chiều nào cũng được.
  - DTSP-N theo kiểu lấy mẫu, chốt thứ tự trước: thứ tự nhóm theo TSP Euclid của các tâm nhóm. Trên thứ tự đó, quy hoạch động chọn 1 trong 12 góc vào × 2 chiều cho mỗi nhóm, nối bằng Dubins (bán kính 255 m).
  - Khi bay: rời quỹ đạo ngay khi mọi thành viên đủ theo kỳ vọng, có tính cả phần nghe được trên đường; bỏ qua nhóm đã đủ.
  - BS lập tour với ba bán kính nhóm 200 / 300 / 400 m và bay tour ngắn nhất.
  - Mã: `uav-l2/tools/dn_baseline.py`; chấm: `DN-puq-stage-zero-redir`.
- Lớp 1 và pha 2 chung cho mọi phương án: 100 lượt bốc lớp 1 ghép cặp; LoRa 40 s mỗi lượt; đội 2 là UAV cánh quay 15 m/s thăm mọi critical cell.

## 2. Kết quả

Sinh bằng `uav-l2/tools/fc_table.py`; bản CSV ở `uav-l2/docs/data/results/chord-fc.csv`.

| bản đồ | kênh | cụm | critical cell | phương án | đội 1 bay (s) | sẵn sàng TB / max (s) | đủ 12 manh mối | ghé / vòng lượn (nhóm) | T\* TB ± 95 % (s) | T\* trung vị / p90 (s) | hạng c\* | Tall (s) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| k8-s1 | open | 8 | 45 | CHORD | 782 | 238 / 655 | 45/45 |  | 647 ± 100 | 494 / 1043 | 2.30 | 10438 |
| k8-s1 | open | 8 | 45 | CHORD-0 | 782 | 336 / 680 | 45/45 |  | 762 ± 99 | 643 / 1250 | 2.29 | 10537 |
| k8-s1 | open | 8 | 45 | FC | 683 | 255 / 590 | 45/45 | 15 / 6.25 | 660 ± 103 | 546 / 1085 | 2.28 | 10447 |
| k8-s1 | open | 8 | 45 | DN | 669 | 271 / 594 | 45/45 | 16 / 5.31 (27 nhóm, 300 m) | 708 ± 101 | 636 / 1171 | 2.33 | 10441 |
| k8-s1 | r500 | 8 | 45 | CHORD | 782 | 364 / 719 | 45/45 |  | 784 ± 96 | 659 / 1203 | 2.25 | 10542 |
| k8-s1 | r500 | 8 | 45 | CHORD-0 | 782 | 382 / 719 | 45/45 |  | 808 ± 102 | 723 / 1253 | 2.39 | 10544 |
| k8-s1 | r500 | 8 | 45 | FC | 1499 | 695 / 1452 | 45/45 | 34 / 28.12 | 1138 ± 127 | 1205 / 1688 | 2.48 | 11100 |
| k8-s1 | r500 | 8 | 45 | DN | 1320 | 617 / 1289 | 45/45 | 22 / 24.62 (22 nhóm, 400 m) | 1078 ± 121 | 1074 / 1628 | 2.48 | 10975 |
| k8-s1 | r200 | 8 | 45 | CHORD | 782 | 437 / 769 | 45/45 |  | 876 ± 97 | 750 / 1308 | 2.38 | 10601 |
| k8-s1 | r200 | 8 | 45 | CHORD-0 | 782 | 437 / 769 | 45/45 |  | 870 ± 97 | 736 / 1306 | 2.37 | 10593 |
| k8-s1 | r200 | 8 | 45 | FC | 3357 | 1717 / 3310 | 45/45 | 45 / 98.62 | 2285 ± 214 | 2605 / 3407 | 2.64 | 12827 |
| k8-s1 | r200 | 8 | 45 | DN | 2687 | 1370 / 2659 | 45/45 | 27 / 74.62 (27 nhóm, 300 m) | 1904 ± 162 | 1920 / 2880 | 2.55 | 12201 |
| k8-s1 | r100 | 8 | 45 | CHORD | 782 | 454 / 895 | 45/45 |  | 872 ± 98 | 746 / 1206 | 2.29 | 10614 |
| k8-s1 | r100 | 8 | 45 | CHORD-0 | 782 | 454 / 895 | 45/45 |  | 880 ± 98 | 763 / 1284 | 2.36 | 10594 |
| k8-s1 | r100 | 8 | 45 | FC | 3621 | 1867 / 3589 | 45/45 | 45 / 123.25 | 2463 ± 229 | 2814 / 3667 | 2.66 | 13078 |
| k8-s1 | r100 | 8 | 45 | DN | 3305 | 1678 / 3269 | 45/45 | 37 / 114.19 (37 nhóm, 200 m) | 2190 ± 217 | 2226 / 3383 | 2.70 | 12755 |
| k12-s1 | open | 12 | 66 | CHORD | 1152 | 262 / 671 | 66/66 |  | 686 ± 69 | 583 / 994 | 1.80 | 16427 |
| k12-s1 | open | 12 | 66 | CHORD-0 | 1152 | 497 / 1007 | 66/66 |  | 939 ± 78 | 864 / 1390 | 1.99 | 16687 |
| k12-s1 | open | 12 | 66 | FC | 971 | 431 / 918 | 66/66 | 22 / 4.75 | 815 ± 82 | 790 / 1350 | 1.88 | 16620 |
| k12-s1 | open | 12 | 66 | DN | 913 | 409 / 831 | 66/66 | 20 / 9.12 (36 nhóm, 400 m) | 805 ± 81 | 755 / 1311 | 1.89 | 16580 |
| k12-s1 | r500 | 12 | 66 | CHORD | 1152 | 523 / 1008 | 66/66 |  | 950 ± 75 | 884 / 1371 | 1.99 | 16689 |
| k12-s1 | r500 | 12 | 66 | CHORD-0 | 1152 | 533 / 1033 | 66/66 |  | 949 ± 78 | 864 / 1401 | 1.98 | 16701 |
| k12-s1 | r500 | 12 | 66 | FC | 2228 | 1013 / 2167 | 66/66 | 49 / 34.25 | 1451 ± 144 | 1346 / 2359 | 2.08 | 17688 |
| k12-s1 | r500 | 12 | 66 | DN | 2011 | 967 / 1979 | 66/66 | 38 / 35 (41 nhóm, 300 m) | 1388 ± 126 | 1328 / 2167 | 1.97 | 17523 |
| k12-s1 | r200 | 12 | 66 | CHORD | 1152 | 566 / 1054 | 66/66 |  | 975 ± 76 | 903 / 1375 | 1.96 | 16717 |
| k12-s1 | r200 | 12 | 66 | CHORD-0 | 1152 | 566 / 1054 | 66/66 |  | 979 ± 76 | 914 / 1420 | 1.99 | 16712 |
| k12-s1 | r200 | 12 | 66 | FC | 4976 | 2505 / 4916 | 66/66 | 64 / 150.25 | 3288 ± 279 | 3505 / 4876 | 2.35 | 20297 |
| k12-s1 | r200 | 12 | 66 | DN | 4016 | 1964 / 3968 | 66/66 | 41 / 112.25 (41 nhóm, 300 m) | 2482 ± 230 | 2527 / 4027 | 2.09 | 19397 |
| k12-s1 | r100 | 12 | 66 | CHORD | 1152 | 585 / 1064 | 66/66 |  | 990 ± 76 | 919 / 1358 | 1.97 | 16734 |
| k12-s1 | r100 | 12 | 66 | CHORD-0 | 1152 | 585 / 1064 | 66/66 |  | 995 ± 76 | 919 / 1412 | 1.96 | 16725 |
| k12-s1 | r100 | 12 | 66 | FC | 5285 | 2663 / 5231 | 66/66 | 65 / 178.38 | 3460 ± 288 | 3684 / 5061 | 2.34 | 20580 |
| k12-s1 | r100 | 12 | 66 | DN | 5078 | 2559 / 5034 | 66/66 | 58 / 168.19 (58 nhóm, 200 m) | 3248 ± 294 | 3426 / 5033 | 2.26 | 20423 |
| k16-s1 | open | 15 | 92 | CHORD | 1415 | 419 / 1052 | 92/92 |  | 863 ± 96 | 803 / 1350 | 1.98 | 23234 |
| k16-s1 | open | 15 | 92 | CHORD-0 | 1415 | 631 / 1290 | 92/92 |  | 1115 ± 114 | 1084 / 1697 | 2.08 | 23546 |
| k16-s1 | open | 15 | 92 | FC | 1190 | 514 / 1132 | 92/92 | 29 / 7.5 | 949 ± 105 | 821 / 1509 | 2.02 | 23385 |
| k16-s1 | open | 15 | 92 | DN | 1134 | 536 / 1041 | 92/92 | 29 / 7.81 (80 nhóm, 200 m) | 967 ± 95 | 895 / 1432 | 1.94 | 23339 |
| k16-s1 | r500 | 15 | 92 | CHORD | 1415 | 642 / 1204 | 92/92 |  | 1107 ± 108 | 1099 / 1681 | 1.98 | 23494 |
| k16-s1 | r500 | 15 | 92 | CHORD-0 | 1415 | 683 / 1354 | 92/92 |  | 1137 ± 113 | 1096 / 1697 | 2.10 | 23546 |
| k16-s1 | r500 | 15 | 92 | FC | 2839 | 1320 / 2784 | 92/92 | 69 / 45.12 | 1801 ± 174 | 1669 / 2804 | 2.05 | 24840 |
| k16-s1 | r500 | 15 | 92 | DN | 2563 | 1238 / 2529 | 92/92 | 42 / 46.19 (44 nhóm, 400 m) | 1750 ± 176 | 1923 / 2826 | 2.10 | 24656 |
| k16-s1 | r200 | 15 | 92 | CHORD | 1415 | 720 / 1398 | 92/92 |  | 1192 ± 111 | 1192 / 1789 | 2.07 | 23558 |
| k16-s1 | r200 | 15 | 92 | CHORD-0 | 1415 | 720 / 1398 | 92/92 |  | 1183 ± 111 | 1194 / 1791 | 2.11 | 23560 |
| k16-s1 | r200 | 15 | 92 | FC | 6631 | 3264 / 6591 | 92/92 | 90 / 197.75 | 3964 ± 376 | 4177 / 6326 | 2.01 | 28501 |
| k16-s1 | r200 | 15 | 92 | DN | 5567 | 2746 / 5523 | 92/92 | 44 / 144.94 (44 nhóm, 400 m) | 3469 ± 330 | 3765 / 5624 | 2.17 | 27524 |
| k16-s1 | r100 | 15 | 92 | CHORD | 1415 | 735 / 1395 | 92/92 |  | 1215 ± 111 | 1183 / 1788 | 2.16 | 23548 |
| k16-s1 | r100 | 15 | 92 | CHORD-0 | 1415 | 735 / 1395 | 92/92 |  | 1214 ± 110 | 1196 / 1801 | 2.16 | 23566 |
| k16-s1 | r100 | 15 | 92 | FC | 7296 | 3619 / 7257 | 92/92 | 92 / 244.75 | 4368 ± 415 | 4617 / 6966 | 2.04 | 29153 |
| k16-s1 | r100 | 15 | 92 | DN | 6808 | 3424 / 6761 | 92/92 | 80 / 233.62 (80 nhóm, 200 m) | 4468 ± 355 | 4764 / 6649 | 2.40 | 28649 |

**Ý nghĩa các cột:**
- *đội 1 bay*: thời gian từ BS về BS. CHORD dùng hồ sơ vận tốc 45° có phần bù giao dữ liệu; FC là đường bay của chính nó.
- *sẵn sàng*: lúc CL của critical cell giữ đủ dữ liệu, trung bình và lớn nhất trên các critical cell.
  - CHORD-0: lúc đội 1 rời cụm + thời gian River. River không xong thì tính là rời cụm + 900 s.
  - CHORD: như CHORD-0, hoặc lúc cell tự giải mã đủ + gom trong cell, nếu sớm hơn.
  - FC, DN: lúc giải mã đủ + thời gian gom trong cell.
- *ghé / vòng lượn (nhóm)*: chỉ có ở FC và DN. Số điểm UAV phải bay tới (FC: critical cell; DN: nhóm) và tổng số vòng lượn; với DN kèm số nhóm và bán kính nhóm BS đã chọn.
- *T\**: lúc đội 2 xác minh xong cell điểm cao nhất c\*. *hạng c\**: c\* là cell thứ mấy đội 2 thăm. *Tall*: lúc đội 2 thăm hết các critical cell và về BS.

**T\* trung bình (s), tóm tắt:**

| kênh | k8 CHORD / FC / DN | k12 CHORD / FC / DN | k16 CHORD / FC / DN | CHORD so với baseline tốt hơn |
|---|---|---|---|---|
| open | **647** / 660 / 708 | **686** / 815 / 805 | **863** / 949 / 967 | nhanh hơn 2 / 15 / 9 % |
| r500 | **784** / 1 138 / 1 078 | **950** / 1 451 / 1 388 | **1 107** / 1 801 / 1 750 | nhanh hơn 27 / 32 / 37 % |
| r200 | **876** / 2 285 / 1 904 | **975** / 3 288 / 2 482 | **1 192** / 3 964 / 3 469 | nhanh hơn 54 / 61 / 66 % |
| r100 | **872** / 2 463 / 2 190 | **990** / 3 460 / 3 248 | **1 215** / 4 368 / 4 468 | nhanh hơn 60 / 70 / 72 % |

**So sánh ghép cặp với baseline tốt hơn** (cùng 100 lượt bốc lớp 1): chênh lệch T\* trung bình ± 95 %, và tỉ lệ lượt bốc CHORD nhanh hơn.

| kênh | k8 | k12 | k16 |
|---|---|---|---|
| open | −13 ± 34 s, 66 % (FC) | −120 ± 52 s, 80 % (DN) | −86 ± 38 s, 74 % (FC) |
| r500 | −294 ± 73 s, 81 % (DN) | −438 ± 98 s, 77 % (DN) | −643 ± 159 s, 71 % (DN) |
| r200 | −1 029 ± 131 s, 93 % (DN) | −1 507 ± 197 s, 91 % (DN) | −2 277 ± 315 s, 94 % (DN) |
| r100 | −1 318 ± 175 s, 87 % (DN) | −2 259 ± 286 s, 86 % (DN) | −3 153 ± 340 s, 97 % (FC) |

**Đọc nhanh:**
- CHORD nhanh hơn cả hai baseline ở cả 12 tổ hợp. Khoảng chênh có ý nghĩa thống kê ở 11/12 ô.
- Ngoại lệ là k8 kênh open, gần như hoà: −13 ± 34 s, CHORD nhanh hơn ở 66 % số lượt bốc.
  - Bản đồ nhỏ, bán kính nghe khoảng 1 km, nên tuyến nào cũng phủ hết các cell rất sớm.
  - Báo cáo của c\* về BS gần như cùng lúc: 279 s (CHORD) so với 286 s (FC).
  - Phần còn lại là pha 2, giống nhau ở mọi phương án.
- Từ r500 trở xuống, CHORD nhanh hơn 27–72 %, và khoảng cách tăng theo cỡ bản đồ.
  - Đường bay của CHORD giữ nguyên ở mọi kênh: 782 / 1 152 / 1 415 s. River bù phần thiếu dưới mặt đất.
  - Đường bay của FC và DN dài gấp 2–6 lần so với chính nó ở kênh open, vì phải lượn quanh từng cell hoặc từng nhóm.
- DN rút ngắn đường bay của FC 2–20 %, nhưng T\* không phải lúc nào cũng tốt hơn: ở k8 open, k16 open và k16 r100, DN chậm hơn FC 2–7 %.

### 2.1. Các cell River không xong
- **Trước mục 169:** River không xong ở 8 critical cell: 1/92 ở k16 open và 7/92 ở k16 r100. Mỗi cell thiếu đúng 1 gói, dù gói đó có node trong cụm giữ.
- **Sau khi sửa River (`--repair 20`, mục 2.2):** 0 cell kẹt ở cả 12 tổ hợp.
  - Thời gian River của các cell xong gần như không đổi. Ví dụ k16 r100: trung bình 111,0 → 114,5 s, chậm nhất 211 → 225 s.

### 2.2. Hai thay đổi của mục 169 và phần đóng góp của từng cái
**Vì sao CHORD thua ở kênh open trước mục 169:** báo cáo của c\* về BS muộn hơn FC 100–150 s, còn pha 2 sau đó gần như bằng nhau. Có hai nguyên nhân:
1. **FC và DN được mã fountain, CHORD thì không.** Với mã fountain, gói nào nghe được cũng tính. CHORD phải có đủ một bản liền mạch của từng file, nên phải chờ River. Cách so sánh như vậy chưa công bằng: nó trộn hai yếu tố, cách mã hoá và đường bay cộng River.
2. **CHORD bay hết các dây cung.** Ở kênh open, một lượt bay qua đã đủ cho cả những cell cách 1 km, nên FC chỉ cần ghé khoảng một phần ba số critical cell.

**Sửa 1 – mã fountain hệ thống cho CHORD** (`l1_rank -fcd`; chỉ đổi cách chấm, không chạy lại ns-3):
- Đội 1 phát gói mã suốt chuyến bay, như FC và DN.
- Cửa sổ River gồm các gói gốc, nên River và kết quả ns-3 giữ nguyên.
- Mỗi cell tự giải mã từ những gì node của nó nghe được trên cả chuyến bay. Phần này dùng cùng mô hình thu và cùng cách gom trong cell như FC (`fc_baseline.realise`), một realisation với khoá `CHORDFC/<bản đồ>/<kênh>`.
- Báo cáo đầu tiên là lúc cell tự giải mã, báo cáo thứ hai là River. Mỗi báo cáo gồm mọi thứ cell có tới lúc đó.

**Sửa 2 – River `--repair 20`** (ns-3, `uav-coop2/examples/coop2-river.cc`; mặc định tắt).
- Đã lần theo từng gói của các cell kẹt (`logs/2026-10-25_0600-fc-baseline/stall-why.md` và `logs/2026-10-25_0800-chord-win/`), thấy hai lỗ hổng:
  1. **Gói không có trong cell Axe phụ trách nó.** Gói thuộc Seg của một cell Axe mà không node nào của cell đó nghe được; chỉ cell bên cạnh có (cụm C9 ở k16 r100). Cell Axe chỉ phân phối gói nó có, nên gói không bao giờ được đẩy đi. Sửa: khi gom, cell Axe xin những gói đó từ một cell kề bên có giữ chúng.
  2. **ACK nhầm.** ACK của 802.15.4 chỉ mang số thứ tự 8 bit, nên một khung có thể được coi là đã gửi nhờ ACK của một cuộc trao đổi khác, và thực ra bị mất (cụm C1 ở k16 r100, C6 ở k16 open). Sửa: một critical cell 20 s không nhận thêm gói mà vẫn thiếu sẽ hỏi lại các thành viên Circle. Thành viên thiếu thì hỏi lại Bank, Bank thiếu thì hỏi lại cell Axe, đều theo các đường đi đã có trong kế hoạch.
- **Kiểm chứng:**
  - Khi tắt, binary mới cho kết quả trùng từng byte với `river-bin` cũ.
  - Khi bật, ba cụm từng kẹt đều xong: C1 lúc 71 s, C9 lúc 119 s, C6 lúc 55 s (`logs/2026-10-25_0800-chord-win/repair-test.md`).
  - Ở những cụm không có lỗ hổng nào, cơ chế không kích hoạt, nên kết quả giữ nguyên (ví dụ cả 8 cụm của k8 open).

**Phần đóng góp, T\* trung bình (s):**

| | k8 open | k12 open | k16 open | k8 r500 | k16 r500 | k16 r100 |
|---|---|---|---|---|---|---|
| CHORD trước mục 169 | 762 | 939 | 1 161 | 808 | 1 137 | 1 412 |
| + River sửa (CHORD-0) | 762 | 939 | 1 115 | 808 | 1 137 | 1 214 |
| + mã fountain (CHORD) | 647 | 686 | 863 | 784 | 1 107 | 1 215 |

- Sửa River chỉ có tác dụng ở những ô có cell kẹt: k16 open và k16 r100.
- Mã fountain có tác dụng lớn ở kênh open, nhỏ ở r500, và gần như bằng 0 ở r200 và r100. Ở hai kênh này, một cell gần như không tự giải đủ được, nên River vẫn quyết định.

## 3. Seed và khoá ngẫu nhiên

| bản đồ | kênh | suy hao thêm (dB) | --clusters | --seed | cụm | mission index ns-3 | khoá FC, DN (CHORD: `CHORDFC/…`) | lượt bốc lớp 1 |
|---|---|---|---|---|---|---|---|---|
| k8-s1 | open | 0 | 8 | 1 | 8 | 800101-800108 | `FC/k8-s1/open, DN/k8-s1/open` | 0–99 |
| k8-s1 | r500 | 9.03 | 8 | 1 | 8 | 800101-800108 | `FC/k8-s1/r500, DN/k8-s1/r500` | 0–99 |
| k8-s1 | r200 | 19.77 | 8 | 1 | 8 | 800101-800108 | `FC/k8-s1/r200, DN/k8-s1/r200` | 0–99 |
| k8-s1 | r100 | 25.74 | 8 | 1 | 8 | 800101-800108 | `FC/k8-s1/r100, DN/k8-s1/r100` | 0–99 |
| k12-s1 | open | 0 | 12 | 1 | 12 | 1200101-1200112 | `FC/k12-s1/open, DN/k12-s1/open` | 0–99 |
| k12-s1 | r500 | 9.03 | 12 | 1 | 12 | 1200101-1200112 | `FC/k12-s1/r500, DN/k12-s1/r500` | 0–99 |
| k12-s1 | r200 | 19.77 | 12 | 1 | 12 | 1200101-1200112 | `FC/k12-s1/r200, DN/k12-s1/r200` | 0–99 |
| k12-s1 | r100 | 25.74 | 12 | 1 | 12 | 1200101-1200112 | `FC/k12-s1/r100, DN/k12-s1/r100` | 0–99 |
| k16-s1 | open | 0 | 16 | 1 | 15 | 1600101-1600115 | `FC/k16-s1/open, DN/k16-s1/open` | 0–99 |
| k16-s1 | r500 | 9.03 | 16 | 1 | 15 | 1600101-1600115 | `FC/k16-s1/r500, DN/k16-s1/r500` | 0–99 |
| k16-s1 | r200 | 19.77 | 16 | 1 | 15 | 1600101-1600115 | `FC/k16-s1/r200, DN/k16-s1/r200` | 0–99 |
| k16-s1 | r100 | 25.74 | 16 | 1 | 15 | 1600101-1600115 | `FC/k16-s1/r100, DN/k16-s1/r100` | 0–99 |

Mỗi khoá dùng như sau:
- **Bản đồ:** `mission.py --clusters K --seed S`. Seed S điều khiển miền (`map_gen`) và chia cụm (`partition`). Bước deploy không nhận seed và tất định theo bản đồ.
- **ns-3:** cụm k dùng mission index 100000·K + 100·S + k (`--mapRuns`).
  - Pass dùng index này cho fading A2G, kèm `--lossDb` theo kênh.
  - River dùng index này cho shadowing G2G, fading và các lần bốc của MAC.
  - Cùng index thì ns-3 cho kết quả giống hệt từng bit.
  - Cùng một bản đồ thì index giống nhau ở mọi kênh, nên mọi kênh và mọi phương án dùng chung một bộ bốc.
- **FC, DN, và phần tự giải mã của CHORD:** mỗi phương án một realisation thu gói, `numpy.random.default_rng` khởi tạo bằng 8 byte đầu của sha256(khoá), little-endian. Khoá của CHORD là `CHORDFC/<bản đồ>/<kênh>`.
- **Lớp 1:** lượt d dùng các khoá sau, giống nhau cho mọi phương án và mọi kênh (ghép cặp):
  - kho ảnh của critical cell (q, r): sha256("<bản đồ>/<d>/<q>/<r>");
  - pha LoRa của các CH: sha256("<bản đồ>"), lấy 4 byte đầu.

## 4. Chạy lại

**Code:** nhánh `claude/document-review-xslwgg`.
- Kênh và cổng gói gần (near-packet gate): từ commit `3aee7f1` (mục 163).
- FC và cách tính River quá hạn: từ commit `dd691e7`.
- DN: từ commit thêm `dn_baseline.py` (mục 168). Kết quả FC sau khi tách phần dùng chung vẫn giống hệt.
- CHORD `-fcd` và River `--repair`: từ commit `dafc836` (mục 169); `mission.py --riverRepair`.

**Binary đóng băng** (`scratchpad/CAMP-BIN4`, mục 169; giống `CAMP-BIN3` trừ `river-bin`; dựng lại theo `logs/2026-10-25_0330-env-modes/build-pass-v3.md` và `logs/2026-10-25_0300-campaign/freeze-bin.md`, `river-bin` là target `uav-coop2-river` từ commit `dafc836`):

| binary | nguồn | sha256 |
|---|---|---|
| deploy-bin | `uav-coop` deploy | `e38d9e5efe2d696ebf742c97f5962c3a99df4a3c71f8f7c47bad57a3a797faac` |
| pass-bin (v3, có `--lossDb`) | `uav-coop/examples/coop-pass.cc` | `6f70076266e4a65787f9e74c25729af85279f50da095993659b4ab34ff576099` |
| river-bin (có `--repair`) | `uav-coop2/examples/coop2-river.cc` | `2e636b6dcacf9bd56dceaa9f0249b428c8b07e97bfcba56d32f704b3fcb54819` |
| river-bin cũ (CAMP-BIN3, trước mục 169) | như trên, trước commit `dafc836` | `ed66896e909daf7d31dc00e68eb739f267dc440e97b4f38da8253dc9473c6f0e` |

**Lệnh** (BIN = CAMP-BIN4, ENV ∈ {open, r500, r200, r100}):

```text
# 1. nhiệm vụ CHORD trên một bản đồ và một kênh (bản đồ, deploy, tour, pass ns-3, River ns-3)
python3 uav-l2/tools/mission.py --clusters K --seed 1 --bin BIN --windowKB 400 --windowAt crit --critRing domain \
  --axeNear --chordTour 0.6,0.8 --kinPass --mapRuns --env ENV --riverRepair 20 --schemes rf --jobs 2 --work WORK
# 2. chấm CHORD, CHORD-0, FC và DN (FC, DN và phần tự giải mã của CHORD chạy bên trong, ghi *-info.json,
#    *-path.csv, *-cells.csv vào WORK)
python3 uav-l2/tools/l1_rank.py --set ENV WORK[,WORK...] [--set ...] --draws 100 --jobs 4 \
  --methods P+prog-kin-puq-stage-zero-redir-kt-fcd,P+prog-kin-puq-stage-zero-redir-kt,FC-puq-stage-zero-redir,DN-puq-stage-zero-redir \
  --out L1
# 3. bảng này
python3 uav-l2/tools/fc_table.py uav-l2/docs/data/results/chord-fc L1 WORK [WORK ...]
```

**Lượt chạy nằm ở đâu:**
- Bản đồ, deploy, tour và pass ns-3: như trước mục 169.
  - k8 ở r500, r200, r100: `logs/2026-10-25_0330-env-modes`; k8 open: mục 161.
  - k12 và k16 open: mục 164; ở ba kênh còn lại: `logs/2026-10-25_0600-fc-baseline/chord-env.sh`.
- River với `--repair 20` trên cả 12 thư mục, chép sang `scratchpad/FIX/<kênh>/<bản đồ>`: `logs/2026-10-25_0800-chord-win/river-fix.sh`.
- Chấm và dựng bảng: `logs/2026-10-25_0800-chord-win/score.sh` (log `score-all.md`, `table-all.md`).

**Bản lưu dữ liệu:** `uav-l2/docs/data/results/raw/<kênh>-<bản đồ>.tar.xz`, 1,1–2,2 MB mỗi tệp, tổng 20 MB cho 12 tệp (`logs/2026-10-25_0600-fc-baseline/archive.sh`). Từ mục 169 đây là các thư mục `FIX/` (River có `--repair`); bản trước nằm trong lịch sử git.
- Gồm: bản đồ, cụm, node, đường bay, kế hoạch River, kết quả River từng critical cell, thông tin và đường bay của FC, DN và phần tự giải mã của CHORD.
- Không gồm bitmap của lượt bay ns-3 (khoảng 1 MB mỗi cụm). Để dựng lại: giải nén vào một thư mục, rồi chạy lại đúng lệnh 1 trên thư mục đó. Chỉ bước pass chạy lại; các bước khác đã có kết quả nên được bỏ qua. Sau đó lệnh 2 và 3 cho lại bảng trên.
- Đã kiểm chứng trên `r200-k8-s1` (`logs/2026-10-25_0600-fc-baseline/roundtrip.md`): 8 bitmap pass dựng lại, cùng 8 kế hoạch và 16 tệp kết quả River (`rf`, `d`), giống hệt bản gốc từng byte (32/32 tệp).

## 5. Giới hạn (cần nêu khi dùng số này)
- Mã fountain lý tưởng: phần dư 5 %, không tính chi phí giải mã.
- Gom trong cell bắt đầu ngay khi cell giải mã đủ, kể cả khi UAV còn phát gần đó. Trong ns-3, việc này sẽ chậm hơn vì phải tranh kênh, nên số của FC hơi lạc quan.
- BS lập tour theo kỳ vọng. Khi bay thật, một cell có thể vẫn thiếu; trên k8, cả 45/45 cell đều đủ ở cả hai baseline.
- DTSP-N của DN là heuristic: chốt thứ tự trước, rồi lấy 24 mẫu cấu hình mỗi nhóm. Không phải lời giải tối ưu, nhưng đây là cách làm chuẩn cho DTSP-N và đã có lợi hơn FC.
- Chỉ có một realisation thu gói cho mỗi bản đồ và kênh. Phương sai của T\* lấy từ 100 lượt bốc lớp 1.
- Phần tự giải mã của CHORD dùng mô hình thu giải tích (như FC và DN), không phải bitmap ns-3. Nó tính cả gói nghe được trên đường bay nối giữa các cụm. Phần River vẫn là ns-3.
- Mỗi cỡ chỉ có một bản đồ. Kết luận về bản đồ lớn và nhỏ cần thêm bản đồ (chiến dịch ở mục 165).

## 6. Bảng chung bảy phương án (mục 182)

Cùng 12 tổ hợp (3 bản đồ × 4 kênh), cùng 100 lượt bốc lớp 1 ghép cặp như mục 2. CHORD, FC, DN cho lại đúng số mục 2.

### 6.1. Bốn phương án thêm
- **Pd: CHORD nhưng kéo trực tiếp thay River** (`Pd+prog-kin-puq-stage-zero-redir-kt-fcd`).
  - Cùng đường bay, cùng mã fountain và phần tự giải mã như CHORD.
  - Dưới mặt đất, mỗi critical cell hỏi thẳng từng cell Axe phần nó thiếu của đoạn dữ liệu mà cell Axe đó giữ (scheme `direct` của `coop2-river`), không có Banks và Circle.
  - Chạy trên ns-3 với cùng binary và mission index như River.
  - `direct` không có cơ chế `--repair` mà River có từ mục 169.
- **B4: CHORD không có hợp tác dưới mặt đất** (`B4-kin-puq-stage-zero-redir-kt-fcd`).
  - Cùng đường bay và cùng realisation thu gói mã fountain như CHORD.
  - Không River, không kéo: mỗi critical cell chỉ báo những manh mối nó tự giải được, sau khi gom trong cell.
- **B1: không có pha 1.** UAV cánh quay thăm mọi critical cell theo TSP và gửi tệp lớn tại từng cell.
- **B7: oracle.** Đội 2 bay thẳng tới c\*; là chặn dưới của T\*.
- B1 và B7 không dùng kênh A2G của đội 1, nên số giống nhau ở mọi kênh.

### 6.2. Kết quả

Sinh bằng `uav-l2/tools/cmp_table.py`; bản CSV ở `uav-l2/docs/data/results/baselines.csv`.

T\* trung bình ± 95 % (s), 100 lượt bốc lớp 1 ghép cặp:

| kênh | bản đồ | CHORD | FC | DN | Pd | B4 | B1 | B7 |
|---|---|---|---|---|---|---|---|---|
| open | k8-s1 | 647 ± 100 | 660 ± 103 | 708 ± 101 | 647 ± 100 | 650 ± 100 | 2926 ± 313 | 322 ± 17 |
| open | k12-s1 | 686 ± 69 | 815 ± 82 | 805 ± 81 | 686 ± 69 | 687 ± 70 | 4168 ± 465 | 402 ± 20 |
| open | k16-s1 | 863 ± 96 | 949 ± 105 | 967 ± 95 | 863 ± 96 | 862 ± 95 | 5169 ± 593 | 404 ± 21 |
| r500 | k8-s1 | 784 ± 96 | 1138 ± 127 | 1078 ± 121 | 806 ± 97 | 1379 ± 207 | 2926 ± 313 | 322 ± 17 |
| r500 | k12-s1 | 950 ± 75 | 1451 ± 144 | 1388 ± 126 | 950 ± 75 | 2030 ± 259 | 4168 ± 465 | 402 ± 20 |
| r500 | k16-s1 | 1107 ± 108 | 1801 ± 174 | 1750 ± 176 | 1115 ± 108 | 2549 ± 378 | 5169 ± 593 | 404 ± 21 |
| r200 | k8-s1 | 876 ± 97 | 2285 ± 214 | 1904 ± 162 | 850 ± 98 | 3711 ± 303 | 2926 ± 313 | 322 ± 17 |
| r200 | k12-s1 | 975 ± 76 | 3288 ± 279 | 2482 ± 230 | 990 ± 76 | 5277 ± 420 | 4168 ± 465 | 402 ± 20 |
| r200 | k16-s1 | 1192 ± 111 | 3964 ± 376 | 3469 ± 330 | 1192 ± 113 | 6298 ± 617 | 5169 ± 593 | 404 ± 21 |
| r100 | k8-s1 | 872 ± 98 | 2463 ± 229 | 2190 ± 217 | 875 ± 98 | 3860 ± 316 | 2926 ± 313 | 322 ± 17 |
| r100 | k12-s1 | 990 ± 76 | 3460 ± 288 | 3248 ± 294 | 990 ± 76 | 5308 ± 412 | 4168 ± 465 | 402 ± 20 |
| r100 | k16-s1 | 1215 ± 111 | 4368 ± 415 | 4468 ± 355 | 1334 ± 162 | 6358 ± 598 | 5169 ± 593 | 404 ± 21 |

Chênh lệch ghép cặp so với CHORD (phương án − CHORD, s; trong ngoặc: % lượt bốc CHORD nhanh hơn):

| kênh | bản đồ | FC | DN | Pd | B4 | B1 | B7 |
|---|---|---|---|---|---|---|---|
| open | k8-s1 | +13 ± 34 (66 %) | +61 ± 40 (60 %) | -0 ± 0 (2 %) | +3 ± 6 (18 %) | +2278 ± 313 (91 %) | -325 ± 94 (0 %) |
| open | k12-s1 | +130 ± 49 (77 %) | +120 ± 52 (80 %) | +0 ± 0 (0 %) | +2 ± 3 (3 %) | +3482 ± 468 (97 %) | -283 ± 70 (0 %) |
| open | k16-s1 | +86 ± 38 (74 %) | +104 ± 73 (60 %) | +0 ± 0 (0 %) | -1 ± 2 (0 %) | +4306 ± 570 (93 %) | -458 ± 90 (0 %) |
| r500 | k8-s1 | +354 ± 74 (81 %) | +294 ± 73 (81 %) | +21 ± 19 (54 %) | +595 ± 197 (74 %) | +2141 ± 309 (89 %) | -462 ± 92 (0 %) |
| r500 | k12-s1 | +501 ± 113 (75 %) | +438 ± 98 (77 %) | -0 ± 8 (39 %) | +1080 ± 253 (81 %) | +3218 ± 468 (95 %) | -548 ± 76 (0 %) |
| r500 | k16-s1 | +694 ± 105 (90 %) | +643 ± 159 (71 %) | +8 ± 8 (42 %) | +1442 ± 368 (80 %) | +4062 ± 565 (92 %) | -703 ± 102 (0 %) |
| r200 | k8-s1 | +1409 ± 168 (93 %) | +1028 ± 131 (93 %) | -26 ± 25 (36 %) | +2835 ± 297 (97 %) | +2050 ± 308 (88 %) | -554 ± 94 (0 %) |
| r200 | k12-s1 | +2313 ± 252 (99 %) | +1507 ± 197 (91 %) | +15 ± 16 (60 %) | +4302 ± 426 (100 %) | +3193 ± 466 (96 %) | -573 ± 76 (0 %) |
| r200 | k16-s1 | +2772 ± 302 (97 %) | +2277 ± 315 (94 %) | -0 ± 13 (41 %) | +5106 ± 620 (96 %) | +3977 ± 559 (92 %) | -788 ± 103 (0 %) |
| r100 | k8-s1 | +1590 ± 184 (93 %) | +1318 ± 175 (87 %) | +3 ± 21 (39 %) | +2987 ± 307 (98 %) | +2053 ± 308 (88 %) | -551 ± 94 (0 %) |
| r100 | k12-s1 | +2471 ± 262 (99 %) | +2259 ± 286 (86 %) | +0 ± 12 (49 %) | +4318 ± 422 (100 %) | +3178 ± 467 (96 %) | -587 ± 76 (0 %) |
| r100 | k16-s1 | +3153 ± 340 (97 %) | +3253 ± 358 (95 %) | +119 ± 97 (38 %) | +5142 ± 597 (98 %) | +3954 ± 559 (92 %) | -810 ± 103 (0 %) |

Đội 1 của CHORD, Pd và B4 bay cùng một đường: 782 / 1 152 / 1 415 s (k8 / k12 / k16) ở mọi kênh. Đường bay của FC và DN như mục 2.

**River và kéo trực tiếp ở mức critical cell** (ns-3, cùng các cell; *xong*: giây từ lúc đội 1 rời cụm tới lúc CL giữ đủ cửa sổ; *cell d nhanh hơn*: số cell kéo trực tiếp xong sớm hơn River, trong các cell cả hai đều xong; *lượt truyền*: tổng số lượt chuyển gói một chặng của mọi cụm):

| kênh | bản đồ | cell | xong TB rf / d (s) | xong max rf / d (s) | kẹt rf / d | cell d nhanh hơn | lượt truyền rf / d (nghìn) | MAC lỗi rf / d (nghìn) |
|---|---|---|---|---|---|---|---|---|
| open | k8-s1 | 45 | 8 / 8 | 35 / 30 | 0 / 0 | 22/45 | 146 / 138 | 5 / 5 |
| open | k12-s1 | 66 | 8 / 8 | 50 / 47 | 0 / 0 | 35/66 | 247 / 254 | 8 / 9 |
| open | k16-s1 | 92 | 10 / 10 | 69 / 47 | 0 / 0 | 48/92 | 517 / 530 | 19 / 19 |
| r500 | k8-s1 | 45 | 54 / 71 | 159 / 206 | 0 / 0 | 10/45 | 1612 / 1621 | 61 / 61 |
| r500 | k12-s1 | 66 | 45 / 57 | 90 / 106 | 0 / 0 | 19/66 | 2112 / 2084 | 79 / 77 |
| r500 | k16-s1 | 92 | 62 / 67 | 244 / 134 | 0 / 0 | 26/92 | 3721 / 3492 | 147 / 133 |
| r200 | k8-s1 | 45 | 108 / 95 | 311 / 235 | 0 / 0 | 30/45 | 3107 / 2481 | 135 / 93 |
| r200 | k12-s1 | 66 | 78 / 83 | 136 / 164 | 0 / 0 | 25/66 | 3897 / 3315 | 165 / 123 |
| r200 | k16-s1 | 92 | 99 / 90 | 259 / 170 | 0 / 0 | 57/92 | 6169 / 5185 | 264 / 196 |
| r100 | k8-s1 | 45 | 126 / 113 | 300 / 283 | 0 / 0 | 35/45 | 3542 / 2825 | 168 / 109 |
| r100 | k12-s1 | 66 | 96 / 95 | 183 / 184 | 0 / 0 | 34/66 | 4736 / 3795 | 222 / 145 |
| r100 | k16-s1 | 92 | 115 / 105 | 225 / 197 | 0 / 6 | 56/86 | 7114 / 5801 | 334 / 227 |

### 6.3. Đọc nhanh
- **CHORD nhanh nhất trong các phương án làm được, hoà với Pd.** B7 (oracle) là chặn dưới: 322 / 402 / 404 s.
- **Hợp tác dưới mặt đất là phần làm nên lợi thế của một lượt bay qua CH.** So B4 với CHORD (cùng đường bay, cùng mã):
  - Kênh open: như nhau (+3 ± 6 s ở k8; 82–99 % số lượt bốc bằng hệt), vì cell tự giải mã đủ trước khi River xong.
  - Từ r500 trở xuống, B4 chậm hơn 1,8–5,4 lần; ở r200 và r100 B4 còn chậm hơn cả B1 (không có pha 1).
  - Lý do: số critical cell tự giải đủ 12 manh mối từ lượt bay là 100 % ở open, 64–66 % ở r500, và gần như 0 ở r200, r100 (1 cell trên 406). Không có hợp tác, báo cáo của cell thiếu manh mối nên BS xếp hạng sai.
- **River không nhanh hơn kéo trực tiếp về T\*.** Ở open, Pd và CHORD bằng hệt (mọi cell tự giải mã trước). Ở 9 ô kênh khác, chênh lệch nhỏ:
  - khoảng tin cậy chứa 0 ở 5 ô;
  - CHORD nhanh hơn ở r500 k8 (+21 ± 19 s, 3 %) và r500 k16 (+8 ± 8 s, 1 %); Pd nhanh hơn ở r200 k8 (−26 ± 25 s, 3 %);
  - k16 r100: Pd chậm hơn +119 ± 97 s, vì 6/92 critical cell của kéo trực tiếp không xong. Đây là lỗi thiếu một gói mà River đã sửa bằng `--repair` ở mục 169; kéo trực tiếp chưa có cơ chế này. Với cơ chế đó, nhiều khả năng Pd cũng hoà ở ô này.
  - Ở mức cell, River xong sớm hơn ở r500 (trung bình 54 / 45 / 62 s so với 71 / 57 / 67 s). Ở r200 và r100, kéo trực tiếp xong sớm hơn hoặc ngang (trừ r200 k12: 78 so với 83 s), và dùng ít lượt truyền hơn 15–20 %.
  - Phần River chắc chắn hơn: 0 cell kẹt ở cả 12 tổ hợp.
  - **Không nên viết rằng River làm nhiệm vụ nhanh hơn kéo trực tiếp;** số liệu này không ủng hộ. Điều số liệu ủng hộ: cần hợp tác dưới mặt đất (B4), và River không kẹt cell nào.
- **B1 chậm hơn CHORD 3,3–6 lần**, nhưng CHORD chỉ nhanh hơn ở 88–97 % số lượt bốc: khi c\* nằm sớm trong tour TSP, B1 tới c\* trước cả khi báo cáo của CHORD về BS.
- FC và DN như mục 2.

### 6.4. Chạy lại
- **ns-3 kéo trực tiếp** cho k12 và k16 (8 thư mục `scratchpad/FIX/<kênh>/k{12,16}-s1`, `CAMP-BIN4`): `logs/2026-10-26_0900-baselines/pd-run.sh`, 4 tiến trình song song. Đây là lệnh 1 của mục 4 với `--schemes d`.
  - k8 dùng các lượt `d` đã có (chạy bằng `CAMP-BIN3`). Chạy lại k8 r200 bằng `CAMP-BIN4` cho 8/8 tệp `r*-d-crit.csv` giống hệt từng byte (`pd-r200-k8-s1-check.md`), vì `--repair` không chạm tới `direct`.
- **Chấm:** `logs/2026-10-26_0900-baselines/score.sh 1` (CHORD, FC, DN, B4, B1, B7) và `score.sh 2` (Pd); 100 lượt bốc, khoá như mục 3. B4 dùng cùng khoá `CHORDFC/<bản đồ>/<kênh>` với CHORD.
- **Bảng:** `python3 uav-l2/tools/cmp_table.py uav-l2/docs/data/results/baselines logs/2026-10-26_0900-baselines/l1rank/part1-draws.csv logs/2026-10-26_0900-baselines/l1rank/part2-draws.csv`; bảng cell River/kéo trực tiếp: `logs/2026-10-26_0900-baselines/river_cmp.py`.

## 7. Chiến dịch bốn phương án (CLAUDE.md §8 mục 187–189) · đang chạy

**Khung của mục 187:**

| phương án | nội dung |
|---|---|
| LM-Tour + River | đề xuất 2: DTSP-N qua đĩa B(CH, ξ), rồi uốn về các critical cell trọng số cao (`lm_tour.py plan --dtspn --weight cl --wmin 1`) |
| CHORD + River | đề xuất 1: CHORD thường, tức dây cung dài nhất qua CH, chọn riêng từng cụm, không `--chordTour` |
| DTSP-N + River | một lượt mỗi cụm, uốn qua mọi critical cell (`--dtspnRiver`, có `prefly.py`) |
| FC + DTSP-N | DN của mục 2 |
| No broadcast (rotary TSP) | B1 |
| Oracle | B7 |

**Thiết lập chạy:**
- Ba bản đồ k8-s1, k12-s1, k16-s1 (8, 12, 15 cụm), bốn kênh, 10 seed mô phỏng.
- Seed R dời chỉ số mission ns-3 thêm 10⁷·(R − 1) và có khoá hiện thực hoá riêng, cùng khối 100 lượt bốc lớp 1 riêng. Seed 1 giữ đúng các khoá ở mục 3.
- Binary `CAMP-BIN5`, đã kiểm chứng cho kết quả giống từng byte với bản lưu trữ.
- Log: `logs/2026-10-27_1714-campaign4/`.

**Dữ liệu:**
- Số liệu từng (phương án, kênh, bản đồ, seed): `data/results/campaign4.csv`.
- Bảng LaTeX cho paper: `paper/icc-v5/table-campaign4.tex`.
- Cả hai sinh lại bằng `python3 logs/2026-10-27_1714-campaign4/table.py --csv uav-l2/docs/data/results/campaign4.csv --tex paper/icc-v5/table-campaign4.tex`.

### 7.1. Kết quả (cập nhật dần theo tác vụ)
**DTSP-N + River đã sửa (mục 191–193).**
- Bản đầu chỉ uốn nhẹ, chỉ vào đĩa của 50–70 % critical cell.
- Bản sửa (`through_crit`) đi zigzag qua đĩa của mọi critical cell.
- Số của bản cũ đã bỏ khỏi bảng. Bản sửa chạy lại cho mọi tác vụ, kể cả các tác vụ đã xong.
- Chi tiết: `logs/2026-10-28_0240-dtspn-check`, `logs/2026-10-28_0310-dtspn-fix`.

<!-- campaign4:begin (table.py --results) -->
Cập nhật 2026-10-28 03:02 UTC: 8/120 tác vụ xong (8/12 ô có ít nhất một seed).

T\* trung bình (s), K = 8 / 12 / 16 cụm; mỗi ô 100 lượt bốc lớp 1 × số seed đã xong (1); – : chưa chạy xong.

| phương án | r = 1000 m | 500 m | 200 m | 150 m |
|---|---|---|---|---|
| LM-Tour + River | – / 721 / 807 | – / 905 / 1063 | – / 959 / 1063 | – / 978 / 1093 |
| CHORD + River | – / 742 / 872 | – / 1013 / 1150 | – / 1075 / 1257 | – / 1091 / 1278 |
| DTSP-N + River | – / – / – | – / – / – | – / – / 1505* | – / – / – |
| FC + DTSP-N | – / 805 / 967 | – / 1389 / 1750 | – / 2481 / 3469 | – / 3248 / 4468 |
| No broadcast (rotary TSP) | – / 4168 / 5169 | – / 4168 / 5169 | – / 4168 / 5169 | – / 4168 / 5169 |
| Oracle | – / 402 / 404 | – / 402 / 404 | – / 402 / 404 | – / 402 / 404 |

\* ước lượng mức mô hình của DTSP-N + River đã sửa (mục 193–194): seed 1, River dự đoán bằng bộ surrogate, chưa chạy ns-3; số đo ns-3 thay vào khi tác vụ xong. Cùng cách ước lượng, CHORD và LM-Tour lệch số ns-3 của chúng: k16 r200 +9 / +19 s.

Chênh ghép cặp (s; âm là phương án đầu nhanh hơn; ± nửa khoảng tin cậy 95 % theo trung bình từng seed, khi đã có từ 2 seed). Ngoặc là % lượt bốc phương án đầu nhanh hơn hẳn, các lượt còn lại phần lớn là hoà.

| kênh | bản đồ | LM − (CHORD) | LM − (DTSP-N + River) | LM − (FC + DTSP-N) | (DTSP-N + River) − (FC + DTSP-N) |
|---|---|---|---|---|---|
| open | k12 | −21 (34 %) | – | −84 (56 %) | – |
| open | k16 | −66 (54 %) | – | −160 (70 %) | – |
| r500 | k12 | −109 (59 %) | – | −484 (82 %) | – |
| r500 | k16 | −87 (58 %) | – | −687 (85 %) | – |
| r200 | k12 | −116 (61 %) | – | −1522 (90 %) | – |
| r200 | k16 | −193 (62 %) | −422* (75 %) | −2406 (97 %) | −1964* (96 %) |
| r100 | k12 | −113 (67 %) | – | −2270 (89 %) | – |
| r100 | k16 | −185 (63 %) | – | −3375 (94 %) | – |
<!-- campaign4:end -->

**Đối chiếu:**
- FC + DTSP-N, B1 và B7 trùng đúng với số của mục 2 và mục 6 ở seed 1 (ví dụ DN r200 k16 3469 s, r100 k12 3248 s), vì khoá seed 1 không đổi.
- CHORD chấm bằng `l1_rank` và bằng `lm_tour score` cho cùng T\* ở mọi lượt bốc (lệch 0,0 s).

**Đọc tạm, seed 1 (chưa được kết luận):**
1. LM-Tour nhanh hơn CHORD ở mọi ô đã xong: 3 % (k12, 1 km) đến 15 % (k16, r200 và r100). Nó cũng nhanh hơn FC + DTSP-N từ 80 s (k12 1 km) tới 3,4 nghìn s (k16 r100).
2. DTSP-N + River: chờ số của bản đã sửa.
4. Mỗi ô mới có một hiện thực mạng. Theo quy tắc N ≥ 120 và "không tin một seed", cần chờ thêm seed trước khi đưa vào paper.
