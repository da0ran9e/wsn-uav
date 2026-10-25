# 2026-10-25 · Rà soát trước chiến dịch số liệu (CLAUDE.md §8 mục 160)

**Mục đích:** xem giả lập đã đủ chặt để chạy chiến dịch lấy số cho bài chưa. Không chạy ns-3 mới; chỉ kiểm tra trên các thư mục đã có.

## Kiểm tra đã chạy

**`kt-kmed-vs-chordT.md`:** k-medoids (đường dài nhất) so với CHORD-T CLUE 80 %, trên 16 bản đồ ghép cặp (`scratchpad/VB`).
- Thời điểm rời cụm lấy từ `kin_time` ở góc nghiêng 45°: hồ sơ vận tốc thật, cụm thiếu được bù bằng giảm tốc hoặc lượn. Lượt bay ns-3 của mục 157 cũng bay theo hồ sơ này.
- Thời điểm rời cụm được lấy trung bình theo số critical cell.
- Kết quả: CHORD-T rời cụm sớm hơn 25 s TB, tốt hơn ở 15/16 bản đồ. Tour ngắn hơn 46 s TB.
- Phần bù của CHORD-T: 9–41 s mỗi bản đồ; của k-medoids: 0–17 s.
- Kết luận: lợi của lớp 2 (trước đây −29 s T\*, đo khi lượt bay giữ 50 m/s) vẫn còn sau khi sửa vận tốc.

**`per-baseline-vs-pass.md`:** mô hình PER của baseline so với mô hình của lượt bay ns-3.

| | fading | ngưỡng |
|---|---|---|
| baseline (`mission_baselines.per`, dùng cho B2, B3, B5, B8) | Nakagami m = 1,8 | cứng −100 dBm |
| lượt bay ns-3 (xấp xỉ bằng `a2g_radius`) | Rician K = 2 | 50 % PER của PSDU 127 B ở −101 dBm |

Hai mô hình lệch nhau:

| cách UAV | PER baseline | PER lượt bay |
|---|---|---|
| 300 m | 0,34 % | 1,07 % |
| 800 m | 31 % | 24 % |
| 1 km | 61 % | 49 % |

## Phát hiện khác (đọc mã, không chạy)

- **Seed ns-3:** `mission.py` gọi `pass-bin` và `river-bin` với `--firstRun=1 --runs=1` cho mọi cụm của mọi bản đồ. Mọi lượt bay vì thế dùng cùng một chuỗi số ngẫu nhiên.
- **SWATH-K** (`swath_mission.py`) chưa có `--kinPass`.
- **Binary:** `BIN/pass-bin` là v2 (có cột t). `BIN2/river-bin` có Trickle và cho kết quả giống `BIN/river-bin` khi chạy River (`logs/2026-10-23_0706-baselines/regress-river.md`). Cả hai đều nằm trong scratchpad.
- **Thời gian thực mỗi bản đồ k8** (2 tiến trình): lượt bay + River 196–214 s, kéo thẳng 73 s, Trickle 710 s (k2: 330 s).
- **Thời gian phát LoRa** theo công thức Semtech (SF10, 125 kHz, CR 4/5, tiền tố 8 symbol, header tường minh, CRC, không LDRO):
  - tải 10 B: 0,289 s;
  - tải 17–24 B: 0,371 s;
  - tải 25 B: 0,412 s;
  - tải 40 B: 0,535 s.
  - Giá trị 0,4 s hiện dùng đúng nếu báo cáo ≤ 24 B: 1 B mã cụm, cộng 2 B (mã cell, điểm) cho mỗi critical cell, nên tối đa 11 cell. Ghi chú trong `PARAM-SOURCES-vi.md` rằng "0,37 s ứng với khoảng 10 B" là sai: 0,37 s ứng với 17–24 B.

## Đề xuất gửi người dùng (chờ duyệt)

**Sửa trước khi chạy** (không cần dựng lại binary):
1. `firstRun` theo bản đồ và cụm, giống nhau giữa các phương án trên cùng bản đồ để giữ ghép cặp.
2. Baseline dùng chung hàm PER với lượt bay.
3. Đóng băng binary vào một thư mục chiến dịch, ghi sha256.

**Cần chốt:**
- P\*: A hay B (mục 159).
- Kênh chính.
- Danh sách phương án.
- N (đề xuất 120 bản đồ, Trickle trên 40).

**Dang dở:** mọi việc trên chờ người dùng trả lời.
