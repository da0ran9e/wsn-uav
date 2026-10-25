# Kết quả CHORD và FC, kèm seed để chạy lại (CLAUDE.md §8 mục 166–167)

Tệp này là nơi lưu số liệu so sánh CHORD (P\*) với baseline FC. Mỗi lần có thêm lượt chạy thì cập nhật tại đây.

**Trạng thái (2026-10-25):**
- k8-s1 đã xong ở cả bốn kênh.
- k12-s1 và k16-s1: CHORD ở r500, r200, r100 đang chạy (`logs/2026-10-25_0600-fc-baseline/chord-env.sh`). Bảng sẽ được bổ sung khi xong.

## 1. Hai phương án
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
- Lớp 1 và pha 2 chung cho cả hai: 100 lượt bốc lớp 1 ghép cặp; LoRa 40 s mỗi lượt; đội 2 là UAV cánh quay 15 m/s thăm mọi critical cell.

## 2. Kết quả

Sinh bằng `uav-l2/tools/fc_table.py`; bản CSV ở `uav-l2/docs/data/results/chord-fc.csv`.

| bản đồ | kênh | cụm | critical cell | phương án | đội 1 bay (s) | sẵn sàng TB / max (s) | đủ 12 manh mối | ghé / vòng lượn | T\* TB ± 95 % (s) | T\* trung vị / p90 (s) | hạng c\* | Tall (s) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| k8-s1 | open | 8 | 45 | CHORD | 782 | 336 / 680 | 45/45 |  | 762 ± 99 | 643 / 1250 | 2.29 | 10537 |
| k8-s1 | open | 8 | 45 | FC | 683 | 255 / 590 | 45/45 | 15 / 6.25 | 660 ± 103 | 546 / 1085 | 2.28 | 10447 |
| k8-s1 | r500 | 8 | 45 | CHORD | 782 | 382 / 719 | 45/45 |  | 808 ± 102 | 723 / 1253 | 2.39 | 10544 |
| k8-s1 | r500 | 8 | 45 | FC | 1499 | 695 / 1452 | 45/45 | 34 / 28.12 | 1138 ± 127 | 1205 / 1688 | 2.48 | 11100 |
| k8-s1 | r200 | 8 | 45 | CHORD | 782 | 427 / 757 | 45/45 |  | 860 ± 97 | 728 / 1307 | 2.34 | 10591 |
| k8-s1 | r200 | 8 | 45 | FC | 3357 | 1717 / 3310 | 45/45 | 45 / 98.62 | 2285 ± 214 | 2605 / 3407 | 2.64 | 12827 |
| k8-s1 | r100 | 8 | 45 | CHORD | 782 | 450 / 814 | 45/45 |  | 878 ± 98 | 763 / 1284 | 2.36 | 10599 |
| k8-s1 | r100 | 8 | 45 | FC | 3621 | 1867 / 3589 | 45/45 | 45 / 123.25 | 2463 ± 229 | 2814 / 3667 | 2.66 | 13078 |

**Ý nghĩa các cột:**
- *đội 1 bay*: thời gian từ BS về BS. CHORD dùng hồ sơ vận tốc 45° có phần bù giao dữ liệu; FC là đường bay của chính nó.
- *sẵn sàng*: lúc CL của critical cell giữ đủ dữ liệu, trung bình và lớn nhất trên các critical cell.
  - CHORD: lúc đội 1 rời cụm + thời gian River. River không xong thì tính là rời cụm + 900 s.
  - FC: lúc giải mã đủ + thời gian gom trong cell.
- *ghé / vòng lượn*: chỉ có ở FC. Số critical cell UAV phải bay tới, và tổng số vòng lượn.
- *T\**: lúc đội 2 xác minh xong cell điểm cao nhất c\*. *hạng c\**: c\* là cell thứ mấy đội 2 thăm. *Tall*: lúc đội 2 thăm hết các critical cell và về BS.

**Đọc nhanh:**
- Ở kênh open, FC nhanh hơn: T\* 660 so với 762 s. Lý do là bán kính nghe khoảng 1 km, nên một lượt bay qua giao đủ cho nhiều cell cùng lúc; chỉ phải ghé 15/45 cell.
- Khi kênh xấu đi, FC phải ghé từng cell và lượn nhiều vòng. Đội 1 của FC bay 1 499 → 3 621 s, còn CHORD vẫn 782 s, vì River bù phần thiếu dưới mặt đất.
- Trên k8, CHORD nhanh hơn FC 29 % ở r500, 62 % ở r200 và 64 % ở r100.

## 3. Seed và khoá ngẫu nhiên

| bản đồ | kênh | suy hao thêm (dB) | --clusters | --seed | cụm | mission index ns-3 | khoá FC | lượt bốc lớp 1 |
|---|---|---|---|---|---|---|---|---|
| k8-s1 | open | 0 | 8 | 1 | 8 | 800101-800108 | `FC/k8-s1/open` | 0–99 |
| k8-s1 | r500 | 9.03 | 8 | 1 | 8 | 800101-800108 | `FC/k8-s1/r500` | 0–99 |
| k8-s1 | r200 | 19.77 | 8 | 1 | 8 | 800101-800108 | `FC/k8-s1/r200` | 0–99 |
| k8-s1 | r100 | 25.74 | 8 | 1 | 8 | 800101-800108 | `FC/k8-s1/r100` | 0–99 |

Mỗi khoá dùng như sau:
- **Bản đồ:** `mission.py --clusters K --seed S`. Seed S điều khiển miền (`map_gen`) và chia cụm (`partition`). Bước deploy không nhận seed và tất định theo bản đồ.
- **ns-3:** cụm k dùng mission index 100000·K + 100·S + k (`--mapRuns`).
  - Pass dùng index này cho fading A2G, kèm `--lossDb` theo kênh.
  - River dùng index này cho shadowing G2G, fading và các lần bốc của MAC.
  - Cùng index thì ns-3 cho kết quả giống hệt từng bit.
  - Cùng một bản đồ thì index giống nhau ở mọi kênh, nên mọi kênh và mọi phương án dùng chung một bộ bốc.
- **FC:** một realisation thu gói, `numpy.random.default_rng` khởi tạo bằng 8 byte đầu của sha256(khoá FC), little-endian.
- **Lớp 1:** lượt d dùng các khoá sau, giống nhau cho mọi phương án và mọi kênh (ghép cặp):
  - kho ảnh của critical cell (q, r): sha256("<bản đồ>/<d>/<q>/<r>");
  - pha LoRa của các CH: sha256("<bản đồ>"), lấy 4 byte đầu.

## 4. Chạy lại

**Code:** nhánh `claude/document-review-xslwgg`.
- Kênh và cổng gói gần (near-packet gate): từ commit `3aee7f1` (mục 163).
- FC và cách tính River quá hạn: từ commit `dd691e7`.

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
# 2. chấm CHORD và FC (FC chạy bên trong, ghi fc-info.json và fc-path.csv vào WORK)
python3 uav-l2/tools/l1_rank.py --set ENV WORK[,WORK...] [--set ...] --draws 100 --jobs 4 \
  --methods P+prog-kin-puq-stage-zero-redir-kt,FC-puq-stage-zero-redir --out L1
# 3. bảng này
python3 uav-l2/tools/fc_table.py uav-l2/docs/data/results/chord-fc L1 WORK [WORK ...]
```

Các thư mục k8 trong bảng chạy thêm `--schemes rf,d`: phương án kéo thẳng (`d`) có chạy, nhưng không dùng trong bảng này. Thư mục open của k8-s1 là `scratchpad/CTRY/P/k8-s1` (mục 161). Lệnh chấm đúng như trên nằm ở `logs/2026-10-25_0600-fc-baseline/score-k8.md`.

**Bản lưu dữ liệu:** `uav-l2/docs/data/results/raw/<kênh>-<bản đồ>.tar.xz`, khoảng 1,2 MB mỗi tệp (`logs/2026-10-25_0600-fc-baseline/archive.sh`).
- Gồm: bản đồ, cụm, node, đường bay, kế hoạch River, kết quả River từng critical cell, thông tin và đường bay FC.
- Không gồm bitmap của lượt bay ns-3 (khoảng 1 MB mỗi cụm). Để dựng lại: giải nén vào một thư mục, rồi chạy lại đúng lệnh 1 trên thư mục đó. Chỉ bước pass chạy lại; các bước khác đã có kết quả nên được bỏ qua. Sau đó lệnh 2 và 3 cho lại bảng trên.
- Đã kiểm chứng trên `r200-k8-s1` (`logs/2026-10-25_0600-fc-baseline/roundtrip.md`): 8 bitmap pass dựng lại, cùng 8 kế hoạch và 16 tệp kết quả River (`rf`, `d`), giống hệt bản gốc từng byte (32/32 tệp).

## 5. Giới hạn của FC (cần nêu khi dùng số này)
- Mã fountain lý tưởng: phần dư 5 %, không tính chi phí giải mã.
- Gom trong cell bắt đầu ngay khi cell giải mã đủ, kể cả khi UAV còn phát gần đó. Trong ns-3, việc này sẽ chậm hơn vì phải tranh kênh, nên số của FC hơi lạc quan.
- BS lập tour theo kỳ vọng. Khi bay thật, một cell có thể vẫn thiếu; trên k8, cả 45/45 cell đều đủ.
- Chỉ có một realisation thu gói cho mỗi bản đồ và kênh. Phương sai của T\* lấy từ 100 lượt bốc lớp 1.
