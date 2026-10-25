# Kết quả CHORD, FC và DN, kèm seed để chạy lại (CLAUDE.md §8 mục 166–168)

Tệp này là nơi lưu số liệu so sánh CHORD (P\*) với hai baseline FC và DN. Mỗi lần có thêm lượt chạy thì cập nhật tại đây.

**Trạng thái (2026-10-25):** đã xong cả 12 tổ hợp: 3 bản đồ (k8-s1, k12-s1, k16-s1; mỗi cỡ một bản đồ chung cho cả ba phương án) × 4 kênh (open, r500, r200, r100). Mỗi tổ hợp có 100 lượt bốc lớp 1.

## 1. Ba phương án
- **CHORD (P\*)**, phương án đề xuất.
  - Cụm k-medoids có sẵn, tối đa 80 cell.
  - Đội 1 bay một đường thẳng qua CH của mỗi cụm; hướng bay và thứ tự cụm chọn chung (`--chordTour 0.6,0.8`).
  - Nối giữa các cụm bằng Dubins; hồ sơ vận tốc theo động học (`--kinPass`).
  - Phát bộ manh mối 400 kB (12 file) dọc Axe; River chuyển dữ liệu tới các critical cell.
  - Phương pháp chấm: `P+prog-kin-puq-stage-zero-redir-kt`.
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
- Lớp 1 và pha 2 chung cho cả ba: 100 lượt bốc lớp 1 ghép cặp; LoRa 40 s mỗi lượt; đội 2 là UAV cánh quay 15 m/s thăm mọi critical cell.

## 2. Kết quả

Sinh bằng `uav-l2/tools/fc_table.py`; bản CSV ở `uav-l2/docs/data/results/chord-fc.csv`.

| bản đồ | kênh | cụm | critical cell | phương án | đội 1 bay (s) | sẵn sàng TB / max (s) | đủ 12 manh mối | ghé / vòng lượn (nhóm) | T\* TB ± 95 % (s) | T\* trung vị / p90 (s) | hạng c\* | Tall (s) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| k8-s1 | open | 8 | 45 | CHORD | 782 | 336 / 680 | 45/45 |  | 762 ± 99 | 643 / 1250 | 2.29 | 10537 |
| k8-s1 | open | 8 | 45 | FC | 683 | 255 / 590 | 45/45 | 15 / 6.25 | 660 ± 103 | 546 / 1085 | 2.28 | 10447 |
| k8-s1 | open | 8 | 45 | DN | 669 | 271 / 594 | 45/45 | 16 / 5.31 (27 nhóm, 300 m) | 708 ± 101 | 636 / 1171 | 2.33 | 10441 |
| k8-s1 | r500 | 8 | 45 | CHORD | 782 | 382 / 719 | 45/45 |  | 808 ± 102 | 723 / 1253 | 2.39 | 10544 |
| k8-s1 | r500 | 8 | 45 | FC | 1499 | 695 / 1452 | 45/45 | 34 / 28.12 | 1138 ± 127 | 1205 / 1688 | 2.48 | 11100 |
| k8-s1 | r500 | 8 | 45 | DN | 1320 | 617 / 1289 | 45/45 | 22 / 24.62 (22 nhóm, 400 m) | 1078 ± 121 | 1074 / 1628 | 2.48 | 10975 |
| k8-s1 | r200 | 8 | 45 | CHORD | 782 | 427 / 757 | 45/45 |  | 860 ± 97 | 728 / 1307 | 2.34 | 10591 |
| k8-s1 | r200 | 8 | 45 | FC | 3357 | 1717 / 3310 | 45/45 | 45 / 98.62 | 2285 ± 214 | 2605 / 3407 | 2.64 | 12827 |
| k8-s1 | r200 | 8 | 45 | DN | 2687 | 1370 / 2659 | 45/45 | 27 / 74.62 (27 nhóm, 300 m) | 1904 ± 162 | 1920 / 2880 | 2.55 | 12201 |
| k8-s1 | r100 | 8 | 45 | CHORD | 782 | 450 / 814 | 45/45 |  | 878 ± 98 | 763 / 1284 | 2.36 | 10599 |
| k8-s1 | r100 | 8 | 45 | FC | 3621 | 1867 / 3589 | 45/45 | 45 / 123.25 | 2463 ± 229 | 2814 / 3667 | 2.66 | 13078 |
| k8-s1 | r100 | 8 | 45 | DN | 3305 | 1678 / 3269 | 45/45 | 37 / 114.19 (37 nhóm, 200 m) | 2190 ± 217 | 2226 / 3383 | 2.70 | 12755 |
| k12-s1 | open | 12 | 66 | CHORD | 1152 | 497 / 1007 | 66/66 |  | 939 ± 78 | 864 / 1390 | 1.99 | 16687 |
| k12-s1 | open | 12 | 66 | FC | 971 | 431 / 918 | 66/66 | 22 / 4.75 | 815 ± 82 | 790 / 1350 | 1.88 | 16620 |
| k12-s1 | open | 12 | 66 | DN | 913 | 409 / 831 | 66/66 | 20 / 9.12 (36 nhóm, 400 m) | 805 ± 81 | 755 / 1311 | 1.89 | 16580 |
| k12-s1 | r500 | 12 | 66 | CHORD | 1152 | 533 / 1033 | 66/66 |  | 949 ± 78 | 864 / 1401 | 1.98 | 16701 |
| k12-s1 | r500 | 12 | 66 | FC | 2228 | 1013 / 2167 | 66/66 | 49 / 34.25 | 1451 ± 144 | 1346 / 2359 | 2.08 | 17688 |
| k12-s1 | r500 | 12 | 66 | DN | 2011 | 967 / 1979 | 66/66 | 38 / 35 (41 nhóm, 300 m) | 1388 ± 126 | 1328 / 2167 | 1.97 | 17523 |
| k12-s1 | r200 | 12 | 66 | CHORD | 1152 | 566 / 1054 | 66/66 |  | 978 ± 76 | 914 / 1420 | 1.99 | 16712 |
| k12-s1 | r200 | 12 | 66 | FC | 4976 | 2505 / 4916 | 66/66 | 64 / 150.25 | 3288 ± 279 | 3505 / 4876 | 2.35 | 20297 |
| k12-s1 | r200 | 12 | 66 | DN | 4016 | 1964 / 3968 | 66/66 | 41 / 112.25 (41 nhóm, 300 m) | 2482 ± 230 | 2527 / 4027 | 2.09 | 19397 |
| k12-s1 | r100 | 12 | 66 | CHORD | 1152 | 584 / 1064 | 66/66 |  | 994 ± 76 | 919 / 1412 | 1.96 | 16724 |
| k12-s1 | r100 | 12 | 66 | FC | 5285 | 2663 / 5231 | 66/66 | 65 / 178.38 | 3460 ± 288 | 3684 / 5061 | 2.34 | 20580 |
| k12-s1 | r100 | 12 | 66 | DN | 5078 | 2559 / 5034 | 66/66 | 58 / 168.19 (58 nhóm, 200 m) | 3248 ± 294 | 3426 / 5033 | 2.26 | 20423 |
| k16-s1 | open | 15 | 92 | CHORD | 1415 | 640 / 1698 | 91/92 | River kẹt 1 | 1161 ± 134 | 1084 / 1791 | 2.31 | 23559 |
| k16-s1 | open | 15 | 92 | FC | 1190 | 514 / 1132 | 92/92 | 29 / 7.5 | 949 ± 105 | 821 / 1509 | 2.02 | 23385 |
| k16-s1 | open | 15 | 92 | DN | 1134 | 536 / 1041 | 92/92 | 29 / 7.81 (80 nhóm, 200 m) | 967 ± 95 | 895 / 1432 | 1.94 | 23339 |
| k16-s1 | r500 | 15 | 92 | CHORD | 1415 | 681 / 1354 | 92/92 |  | 1137 ± 113 | 1096 / 1697 | 2.10 | 23546 |
| k16-s1 | r500 | 15 | 92 | FC | 2839 | 1320 / 2784 | 92/92 | 69 / 45.12 | 1801 ± 174 | 1669 / 2804 | 2.05 | 24840 |
| k16-s1 | r500 | 15 | 92 | DN | 2563 | 1238 / 2529 | 92/92 | 42 / 46.19 (44 nhóm, 400 m) | 1750 ± 176 | 1923 / 2826 | 2.10 | 24656 |
| k16-s1 | r200 | 15 | 92 | CHORD | 1415 | 716 / 1398 | 92/92 |  | 1181 ± 111 | 1185 / 1791 | 2.12 | 23560 |
| k16-s1 | r200 | 15 | 92 | FC | 6631 | 3264 / 6591 | 92/92 | 90 / 197.75 | 3964 ± 376 | 4177 / 6326 | 2.01 | 28501 |
| k16-s1 | r200 | 15 | 92 | DN | 5567 | 2746 / 5523 | 92/92 | 44 / 144.94 (44 nhóm, 400 m) | 3469 ± 330 | 3765 / 5624 | 2.17 | 27524 |
| k16-s1 | r100 | 15 | 92 | CHORD | 1415 | 792 / 2080 | 85/92 | River kẹt 7 | 1412 ± 187 | 1196 / 3089 | 3.23 | 22644 |
| k16-s1 | r100 | 15 | 92 | FC | 7296 | 3619 / 7257 | 92/92 | 92 / 244.75 | 4368 ± 415 | 4617 / 6966 | 2.04 | 29153 |
| k16-s1 | r100 | 15 | 92 | DN | 6808 | 3424 / 6761 | 92/92 | 80 / 233.62 (80 nhóm, 200 m) | 4468 ± 355 | 4764 / 6649 | 2.40 | 28649 |

**Ý nghĩa các cột:**
- *đội 1 bay*: thời gian từ BS về BS. CHORD dùng hồ sơ vận tốc 45° có phần bù giao dữ liệu; FC là đường bay của chính nó.
- *sẵn sàng*: lúc CL của critical cell giữ đủ dữ liệu, trung bình và lớn nhất trên các critical cell.
  - CHORD: lúc đội 1 rời cụm + thời gian River. River không xong thì tính là rời cụm + 900 s.
  - FC, DN: lúc giải mã đủ + thời gian gom trong cell.
- *ghé / vòng lượn (nhóm)*: chỉ có ở FC và DN. Số điểm UAV phải bay tới (FC: critical cell; DN: nhóm) và tổng số vòng lượn; với DN kèm số nhóm và bán kính nhóm BS đã chọn.
- *T\**: lúc đội 2 xác minh xong cell điểm cao nhất c\*. *hạng c\**: c\* là cell thứ mấy đội 2 thăm. *Tall*: lúc đội 2 thăm hết các critical cell và về BS.

**T\* trung bình (s), tóm tắt:**

| kênh | k8 CHORD / FC / DN | k12 CHORD / FC / DN | k16 CHORD / FC / DN | CHORD so với baseline tốt hơn |
|---|---|---|---|---|
| open | 762 / **660** / 708 | 939 / 815 / **805** | 1 161 / **949** / 967 | chậm hơn 16 / 17 / 22 % |
| r500 | **808** / 1 138 / 1 078 | **949** / 1 451 / 1 388 | **1 137** / 1 801 / 1 750 | nhanh hơn 25 / 32 / 35 % |
| r200 | **860** / 2 285 / 1 904 | **978** / 3 288 / 2 482 | **1 181** / 3 964 / 3 469 | nhanh hơn 55 / 61 / 66 % |
| r100 | **878** / 2 463 / 2 190 | **994** / 3 460 / 3 248 | **1 412** / 4 368 / 4 468 | nhanh hơn 60 / 69 / 68 % |

**Đọc nhanh:**
- Ở kênh open, hai baseline nhanh hơn CHORD 16–22 %. Lý do là bán kính nghe khoảng 1 km, nên một lượt bay qua giao đủ cho nhiều cell cùng lúc; FC chỉ phải ghé 15–29 cell, khoảng một phần ba số critical cell.
- Từ r500 trở xuống, CHORD nhanh hơn baseline tốt nhất 25–69 %, và khoảng cách tăng khi bản đồ lớn hơn.
  - Đường bay của CHORD không đổi theo kênh: 782 / 1 152 / 1 415 s. River bù phần thiếu dưới mặt đất.
  - Đường bay của FC và DN dài gấp 2–6 lần so với chính nó ở kênh open, vì phải ghé từng critical cell (hoặc từng nhóm) và lượn nhiều vòng.
- DN rút ngắn đường bay của FC 2–20 %, nhưng T\* không phải lúc nào cũng tốt hơn, vì thứ tự giao khác nhau: ở k8 open, k16 open và k16 r100, DN chậm hơn FC 2–7 %.
- Không phương án nào thiếu manh mối, trừ các cell River kẹt của CHORD (mục 2.1).

### 2.1. Các cell River không xong (CHORD)
- **Số cell:** k16-s1 open 1/92, k16-s1 r100 7/92. Không có cell nào kẹt ở 10 tổ hợp còn lại.
- **Cách tính khi chấm:** cell kẹt báo cáo lúc đội 1 rời cụm + 900 s, chỉ với những gì node của nó tự nghe được (thường không có manh mối nào). Vì vậy T\* của CHORD ở k16 r100 (1 412 s, p90 3 089 s) và ở k16 open bị kéo lên. Đây là cách tính bảo thủ, bất lợi cho CHORD.
- **Mỗi cell kẹt đều thiếu đúng 1 gói,** và gói đó có node trong cụm giữ. Có hai nguyên nhân (`logs/2026-10-25_0600-fc-baseline/stall-why.md`, chạy lại có vết và khớp từng cell với lượt chính):
  1. **Gói thuộc Seg của một cell Axe mà không node nào của cell đó nghe được.** Cụm C9 ở r100, gói 3910 thuộc Seg của cell (−13, 21), nhưng chỉ 10 node của cell bên cạnh (−12, 21) giữ nó. Cell Axe chỉ phân phối gói của chính mình, nên gói này không bao giờ được đẩy đi, và cả 6 critical cell của C9 đều thiếu nó. Ở r100 bán kính nghe chỉ khoảng 100 m, nên chuyện này dễ xảy ra hơn hẳn.
  2. **Cell Axe có giữ gói, nhưng River làm rơi gói trên đường đi và không hỏi lại.** Gặp ở cụm C1 ở r100 (gói 3831) và cụm C6 ở open (mục 165).
- **Sửa** cần đổi giao thức River trong ns-3: cell Axe lấy nốt gói Seg còn thiếu từ hàng xóm, và có cơ chế hỏi lại gói đã rơi. Sau đó phải dựng lại `river-bin` và chạy lại River trên cả 12 thư mục; bitmap lượt bay ns-3 giữ nguyên. Việc này đang chờ người dùng quyết định.

## 3. Seed và khoá ngẫu nhiên

| bản đồ | kênh | suy hao thêm (dB) | --clusters | --seed | cụm | mission index ns-3 | khoá FC, DN | lượt bốc lớp 1 |
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
- **FC, DN:** mỗi phương án một realisation thu gói, `numpy.random.default_rng` khởi tạo bằng 8 byte đầu của sha256(khoá), little-endian.
- **Lớp 1:** lượt d dùng các khoá sau, giống nhau cho mọi phương án và mọi kênh (ghép cặp):
  - kho ảnh của critical cell (q, r): sha256("<bản đồ>/<d>/<q>/<r>");
  - pha LoRa của các CH: sha256("<bản đồ>"), lấy 4 byte đầu.

## 4. Chạy lại

**Code:** nhánh `claude/document-review-xslwgg`.
- Kênh và cổng gói gần (near-packet gate): từ commit `3aee7f1` (mục 163).
- FC và cách tính River quá hạn: từ commit `dd691e7`.
- DN: từ commit thêm `dn_baseline.py` (mục 168). Kết quả FC sau khi tách phần dùng chung vẫn giống hệt.

**Binary đóng băng** (`scratchpad/CAMP-BIN3`; dựng lại theo `logs/2026-10-25_0330-env-modes/build-pass-v3.md` và `logs/2026-10-25_0300-campaign/freeze-bin.md`):

| binary | nguồn | sha256 |
|---|---|---|
| deploy-bin | `uav-coop` deploy | `e38d9e5efe2d696ebf742c97f5962c3a99df4a3c71f8f7c47bad57a3a797faac` |
| pass-bin (v3, có `--lossDb`) | `uav-coop/examples/coop-pass.cc` | `6f70076266e4a65787f9e74c25729af85279f50da095993659b4ab34ff576099` |
| river-bin | `uav-coop2` River | `ed66896e909daf7d31dc00e68eb739f267dc440e97b4f38da8253dc9473c6f0e` |

**Lệnh** (BIN = CAMP-BIN3, ENV ∈ {open, r500, r200, r100}):

```text
# 1. nhiệm vụ CHORD trên một bản đồ và một kênh (bản đồ, deploy, tour, pass ns-3, River ns-3)
python3 uav-l2/tools/mission.py --clusters K --seed 1 --bin BIN --windowKB 400 --windowAt crit --critRing domain \
  --axeNear --chordTour 0.6,0.8 --kinPass --mapRuns --env ENV --schemes rf --jobs 2 --work WORK
# 2. chấm CHORD, FC và DN (FC, DN chạy bên trong, ghi fc-/dn-info.json và fc-/dn-path.csv vào WORK)
python3 uav-l2/tools/l1_rank.py --set ENV WORK[,WORK...] [--set ...] --draws 100 --jobs 4 \
  --methods P+prog-kin-puq-stage-zero-redir-kt,FC-puq-stage-zero-redir,DN-puq-stage-zero-redir --out L1
# 3. bảng này
python3 uav-l2/tools/fc_table.py uav-l2/docs/data/results/chord-fc L1 WORK [WORK ...]
```

**Lượt chạy nằm ở đâu:**
- Thư mục k8 chạy thêm `--schemes rf,d`: phương án kéo thẳng (`d`) có chạy, nhưng không dùng trong bảng này.
- Thư mục open: k8-s1 là `scratchpad/CTRY/P/k8-s1` (mục 161); k12-s1 và k16-s1 là `scratchpad/ANIM/k*-s1` (mục 164).
- k12-s1 và k16-s1 ở r500, r200, r100: `logs/2026-10-25_0600-fc-baseline/chord-env.sh`.
- Lệnh chấm cả 12 tổ hợp: `logs/2026-10-25_0600-fc-baseline/score.sh` (log `score-all.md`). Lệnh dựng bảng: `table-all.md`.

**Bản lưu dữ liệu:** `uav-l2/docs/data/results/raw/<kênh>-<bản đồ>.tar.xz`, 1,1–2,2 MB mỗi tệp, tổng 20 MB cho 12 tệp (`logs/2026-10-25_0600-fc-baseline/archive.sh`).
- Gồm: bản đồ, cụm, node, đường bay, kế hoạch River, kết quả River từng critical cell, thông tin và đường bay FC.
- Không gồm bitmap của lượt bay ns-3 (khoảng 1 MB mỗi cụm). Để dựng lại: giải nén vào một thư mục, rồi chạy lại đúng lệnh 1 trên thư mục đó. Chỉ bước pass chạy lại; các bước khác đã có kết quả nên được bỏ qua. Sau đó lệnh 2 và 3 cho lại bảng trên.
- Đã kiểm chứng trên `r200-k8-s1` (`logs/2026-10-25_0600-fc-baseline/roundtrip.md`): 8 bitmap pass dựng lại, cùng 8 kế hoạch và 16 tệp kết quả River (`rf`, `d`), giống hệt bản gốc từng byte (32/32 tệp).

## 5. Giới hạn của FC và DN (cần nêu khi dùng số này)
- Mã fountain lý tưởng: phần dư 5 %, không tính chi phí giải mã.
- Gom trong cell bắt đầu ngay khi cell giải mã đủ, kể cả khi UAV còn phát gần đó. Trong ns-3, việc này sẽ chậm hơn vì phải tranh kênh, nên số của FC hơi lạc quan.
- BS lập tour theo kỳ vọng. Khi bay thật, một cell có thể vẫn thiếu; trên k8, cả 45/45 cell đều đủ ở cả hai baseline.
- DTSP-N của DN là heuristic: chốt thứ tự trước, rồi lấy 24 mẫu cấu hình mỗi nhóm. Không phải lời giải tối ưu, nhưng đây là cách làm chuẩn cho DTSP-N và đã có lợi hơn FC.
- Chỉ có một realisation thu gói cho mỗi bản đồ và kênh. Phương sai của T\* lấy từ 100 lượt bốc lớp 1.
