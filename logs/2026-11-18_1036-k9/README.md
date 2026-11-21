# K9: chọn critical cell và đánh đổi số critical cell (2026-11-18, chatlog mục 341)

Kế hoạch: `paper/j1/PLAN-K9-DATA-vi.md` (bước B0–B7). Phiên session_01Anfb7c. Dữ liệu C4 dựng lại trong scratchpad bằng
`logs/2026-10-27_1714-campaign4/child-setup.sh` (CAMP-BIN5 và hình học seed 1 của 12 thư mục C4); không cần build ns-3 cho
B0–B3.

## Giai đoạn 1 (B2): tập critical cell từ file ngoài

- Mã: thư mục nhiệm vụ có `crit.csv` (cột q,r, mọi cụm) thì dùng tập này thay Algorithm 3 ở mọi chỗ đọc critical cell:
  `river_plan.load` và `plan` (kế hoạch River, `river_export.py`), `mission_report.load_map` (LM-Tour, `river_surrogate`),
  `meander_lane.critical` (`mission.py --bendCrit`, làn meander). `mission.py --crit FILE` chép file vào thư mục nhiệm vụ một
  lần; chạy lại với file khác thì dừng.
- Kiểm: `b2-regress.md` (`paper/j1/analysis/crit_regress.py`) trên 12 thư mục C4 (k8, k12, k16 × open, r500, r200, r100):
  đưa đúng tập Algorithm 3 vào thì kế hoạch giống từng byte (và trùng kế hoạch chiến dịch đã bay), tập LM-Tour và tập uốn
  tour không đổi; đưa một tập khác (bỏ một cell mỗi cụm, thêm một cell) thì kế hoạch và báo cáo theo đúng tập đó. Đạt 12/12.
- Lỗi gặp và sửa: thư mục thử dùng symlink `d{k}` nên `d{k}/..` trỏ về thư mục gốc; `load` giờ tìm `crit.csv` theo tên
  (`os.path.normpath`), không qua symlink.

## Giai đoạn 2 (B0): tham số

- Đầu ra: `paper/j1/K9-PARAMS-vi.md` (ρ, cỡ dữ liệu D1–D3, thời gian xử lý theo bậc thiết bị, độ chính xác OSNet theo cỡ, tham
  số mạng). Phần lớn lấy từ repo (`research_notes/l1-edge-recognition/`, `research_notes/l1-signature-matching/`); web cho ρ
  (hai đoạn trích tìm kiếm) và bảng 6 của OSNet (đọc trang ar5iv).
- Còn là ước lượng: cỡ JPEG khung và ảnh cắt, thời gian OSNet x0,25 trên MCU, tỉ lệ node là camera, ρ mức thấp và giữa.

## Giai đoạn 3 (B1): luồng nền về AI node

- Script `paper/j1/analysis/bg_load.py`; kết quả `data/b1-k8.{md,csv}`, `data/b1-k12.*`, `data/b1-k16.*`; lệnh ở
  `b1-bg-load-*.md`. Kênh r100 (luồng nền không phụ thuộc kênh A2G), mô hình tải của `river_lb.py`.
- Tập AI cell: k-medoids theo số chặng cell trong từng cụm, N = 8…128, cộng tập Algorithm 3. Mỗi cụm giữ mesh riêng.
- Kết quả (k8, ngân sách 10 % thời gian, 30 % node là camera): ρ lớn nhất mà môi trường bận nhất còn chịu được là 0,2–1,9
  người/h với D1, 0,7–7,7 với D2, 13–145 với D3 khi N tăng từ 8 lên 128. Môi trường bận nhất là cell của AI node. k12, k16 cùng
  cỡ. Tập Algorithm 3 (45 cell) chỉ ngang N = 16 medoids, vì các critical cell của nó dồn cục (xa nhất 8 cell, 1 269 node đổ
  về một AI node).
- Hệ quả: D1, D2 không khả thi ở mọi ρ thật trên 802.15.4; D3 chỉ chịu được phố vắng tới phố thường nếu có khoảng 100 AI cell
  trở lên. Ở mức ρ khả thi, năng lực tính của AI node không bị chạm (N = 8: khoảng 2 bản ghi mỗi giây vào AI node bận nhất).

## Giai đoạn 4 (B3): chọn critical cell cho D3

- Script `paper/j1/analysis/cc_select.py`: River theo surrogate C4 (công thức, mỗi critical cell thêm vào làm cả cụm chậm hơn
  qua cluLack), mạng nền theo `bg_load.py` (ngân sách 10 / 20 %, 30 % node là camera, 528 B mỗi người, giới hạn 5 cell); số
  critical cell ít nhất còn khả thi (nhân đôi rồi chia đôi m), đặt chỗ bằng tìm kiếm cục bộ. Tập chọn ghi ở
  `data/crit-<thư mục>-u<ngân sách>-rho<ρ>.csv` (dùng với `mission.py --crit`).
- Lần chạy đầu (bản tính tải bằng vòng lặp Python) bị dừng ở giới hạn 1 giờ; bản hiện tại tính sẵn tải của mọi cặp (AI cell,
  cell), kiểm trùng với `bg_load.Cluster.load` ngay trong script, nhanh hơn 50–100 lần.
- k8 r100 (`data/cc-r100-R1-k8-s1.md`): ngân sách 10 %, ρ = 20 / 50 / 100 / 200 cần 24 / 34 / 69 / 161 critical cell, T1 mô
  hình 661 / 674 / 728 / 906 s; Algorithm 3 (45 cell) có T1 753 s và vi phạm giới hạn chặng (xa nhất 8 cell). r200 cùng số cell,
  T1 thấp hơn 7–30 s. Đối chiếu với kế hoạch River thật: lệch 0,00 s.
- k12 và k16 ở r100 (`data/cc-r100-R1-k12-s1.md`, `...-k16-s1.md`), ngân sách 10 %, ρ = 20 / 50 / 100 / 200: k12 cần 32 / 52 / 98 /
  220 critical cell, T1 992 / 1005 / 1061 / 1147 s (Algorithm 3: 66 cell, 1021 s); k16 cần 49 / 64 / 123 / 275, T1 1162 / 1168 /
  1235 / 1362 s (Algorithm 3: 92 cell, 1232 s). Algorithm 3 vi phạm giới hạn chặng trên cả ba bản đồ. Ở ρ ≤ 50 tập mới nhanh hơn
  Algorithm 3 trên cả ba bản đồ; ở ρ = 100 nhanh hơn trên k8, ngang trên k16, chậm hơn trên k12; ở ρ = 200 chậm hơn trên cả ba,
  vì cần nhiều critical cell hơn. So sánh này chưa công bằng cho tập mới: Algorithm 3 không chở nổi luồng nền ở các mức ρ đó
  (B1: chỉ tới khoảng 18 người/h trên k8).
- Surrogate khớp trên 4–9 critical cell mỗi cụm; tập tới 20 critical cell mỗi cụm nằm ngoài vùng khớp, B4 cần kiểm bằng ns-3.
- Chưa làm: T2 (pha 2) chưa vào hàm mục tiêu, để B5.

## Giai đoạn 5 (B4): kiểm surrogate bằng ns-3, seed 1

- Script `paper/j1/analysis/b4_run.sh` (pha 1 trong ns-3 với binary đóng băng CAMP-BIN5 và cờ của C4, bản đồ k8-s1, `--crit`
  lấy tập của B3) và `paper/j1/analysis/b4_compare.py` (doneS đo so với surrogate từng critical cell, T_k từng cụm, T1).
  Lệnh ở `b4-seed1.md`, `b4-compare-seed1.md`; kết quả `data/b4-seed1.{md,csv}`; đầu ra River từng cấu hình (`r*-rf-crit.csv`,
  `tour.json`, `mission.log`) ở `data/b4-seed1-raw/`. Thư mục làm việc đầy đủ 271 MB nằm trong scratchpad, không commit.
- 8 cấu hình: kênh r100, r200 × tập Algorithm 3, ρ = 20, 100, 200 (ngân sách 10 %), runSeed 1, 4 cấu hình song song, khoảng
  2 giờ 20 phút (rho200 chậm nhất).
- T1 đo / mô hình (s): r100 alg3 770 / 753, rho20 687 / 661, rho100 733 / 728, rho200 ≥ 1 231 / 906; r200 alg3 743 / 740,
  rho20 658 / 654, rho100 755 / 714, rho200 ≥ 1 231 / 876. Ở rho200, cụm 7 và 8 mỗi kênh còn 1 critical cell chưa xong khi River
  chạm giới hạn 900 s, nên T1 đo chỉ là cận dưới.
- Tới 70 critical cell (rho100), mô hình giữ đúng thứ tự trên r100 và lệch T1 dưới 41 s; trên r200 nó xếp rho100 nhanh hơn
  Algorithm 3 trong khi ns-3 đo chậm hơn 12 s. Ở 161 critical cell (rho200), mô hình sai hẳn: trong một cụm ns-3 trải từ 75 tới
  trên 900 s, mô hình đoán gần như một số cho cả cụm.
- Mô hình đoán T_k thấp hơn đo ở mọi cấu hình (lệch trung bình −7 tới −44 s khi chưa tới 70 cell). Phần lớn do cụm 7 và 8: ở
  Algorithm 3 r100, cụm 8 đoán 91 s, đo 248 s. Số đo cụm 8 trùng từng số với dữ liệu khớp surrogate, còn cụm 2 thì không (dữ
  liệu khớp 147–300 s, B4 99–188 s, cùng tập Algorithm 3); dữ liệu khớp đến từ thư mục FIX với CAMP-BIN4. Nguyên nhân chưa rõ.
  Một seed chưa tách được sai số của mô hình khỏi biến động theo lần chạy.
- Chưa làm: seed thứ hai (mục 348: tạm dừng ở 1 seed).

## Giai đoạn 6 (B5): tổng thời gian hai pha, phương án D3

- Script `paper/j1/analysis/b5_phase2.py`; lệnh ở `b5-phase2-seed1.md`; kết quả `data/b5-seed1.{md,csv}`. Chạy 30 s,
  không cần ns-3.
- Đầu vào: 8 thư mục B4. Pha 1 là số đo ns-3: cell chưa xong tính bằng 900 s, nên rho200 là cận dưới. Pha 2 dùng mô hình V1
  của `mission_policy.py`: đội 2 bay 15 m/s, rời trạm gốc ở báo cáo đầu tiên, thăm theo điểm. Mỗi lần xác minh tốn 78 s theo
  CONTEXT mục 17. Pha 2 kết thúc khi V1 xác nhận đúng AI cell (mục 349).
- Lớp 1 cho D3:
  - mỗi node giao về AI cell gần nhất trong cụm;
  - kho của AI cell c có ρ · 2 h · 0,3 · n_c vector;
  - mỗi AI cell đặt ngưỡng riêng để cell chỉ có người lạ báo YES với xác suất 0,1 (CONTEXT mục 16);
  - điểm số theo mô hình binormal của `l1_mission.py`, k = 1 hoặc 3 vector của mục tiêu;
  - node thật rút đều trên mọi node;
  - 300 lượt rút, ghép cặp giữa các tập.
- Mỗi tập ở đúng ρ nó được chọn (r100, k = 1 / 3): rho20 cho T 823 / 820 s, thành công 0,63 / 0,93; rho100 cho T 962 / 940 s,
  0,60 / 0,93; rho200 cho T 1 312 / 1 153 s, 0,61 / 0,92. Algorithm 3 ở ρ = 20 (vượt ngưỡng tải một chút, ρ_max 18) cho T
  889 / 862 s, 0,66 / 0,95. r200 cùng xu hướng.
- Ở cùng ρ = 20, tập ít AI cell nhanh nhất: 24 cell cho T 823 s, 45 cho 889 s, 69 cho 933 s, 161 cho 1 234 s (k = 1). Pha 2
  cộng thêm khoảng 130–250 s sau T1. Phần pha 2 tăng theo số AI cell, vì mỗi AI cell báo nhầm với xác suất 0,1: số cell báo YES
  tăng từ 2,8 lên 16,5, số lần thăm từ 1,8 lên 3,6.
- Kho lớn ít làm giảm tỉ lệ bắt được mục tiêu: kho 12 780 vector cho 0,63, kho 1 368 vector cho 0,71 (k = 1). Lý do là ngưỡng chỉ
  tăng theo log của cỡ kho.
- Kết quả phụ thuộc giả định báo nhầm 0,1 cho mỗi AI cell: giả định này làm tập nhiều AI cell chịu nhiều lần thăm sai. Nếu giữ
  tỉ lệ báo nhầm của cả hệ thống cố định thì phải nâng ngưỡng theo số AI cell; B6 nên so hai cách.
- Mục 348 (nghi vấn ở node thường): khoảng cách từ node thật tới AI cell của nó trung bình 2,5 cell (tối đa 5) ở rho20, 1,0 cell
  (tối đa 4) ở rho200. B5 cho V1 xác minh tại AI cell; nếu V1 cần ảnh gốc ở node thường thì phải cộng thời gian chuyển ảnh
  hoặc bay tới cell đó.

## Giai đoạn 7 (B6, phần báo nhầm): hai cách đặt ngưỡng

- Cùng script `b5_phase2.py`, thêm `--fa`. `cell:0.1` là cách của B5: mỗi AI cell chỉ có người lạ báo YES với xác suất 0,1,
  nên số báo nhầm tăng theo số AI cell; kết quả trùng từng số với B5. `sys:E` giữ kỳ vọng E lần báo nhầm cho cả hệ thống
  (xác suất mỗi cell E / số AI cell). Chạy E = 2,4 (bằng tập 24 cell ở cách B5) và E = 1. Lệnh ở `b6-fa-*.md`, kết quả
  `data/b6-fa-{cell-0-1,sys-2-4,sys-1}.{md,csv}`, mỗi lần 30 s.
- r100, ρ = 20, k = 1, T (s) / thành công:

  | tập | cell 0,1 | hệ thống E = 2,4 | hệ thống E = 1 |
  |---|---|---|---|
  | rho20 (24 cell) | 823 / 0,63 | 823 / 0,63 | 781 / 0,55 |
  | Algorithm 3 (45) | 889 / 0,66 | 836 / 0,58 | 823 / 0,52 |
  | rho100 (69) | 933 / 0,69 | 879 / 0,59 | 864 / 0,54 |
  | rho200 (161) | 1 234 / 0,71 | 1 061 / 0,58 | 1 051 / 0,53 |

- Khi giữ báo nhầm cố định cho cả hệ thống, số cell báo YES gần như bằng nhau ở mọi tập (khoảng 3 với E = 2,4), khoảng cách T
  giữa các tập hẹp lại (rho100 hơn rho20 56 s thay vì 110 s) nhưng thứ tự giữ nguyên. Tỉ lệ thành công đổi chiều: tập ít cell
  được ngưỡng mỗi cell thấp hơn nên bắt mục tiêu tốt hơn (0,63 so với 0,58 ở E = 2,4). Như vậy tập ít AI cell thắng ở cả hai
  cách; phần chênh còn lại đến từ T1 và số lần thăm.
- r200 và các ρ, k khác cùng xu hướng.

## Giai đoạn 8 (B6, phần còn lại): ρ cao, mật độ, bậc thiết bị

- ρ cao: `cc_select.py` trên k8 r100 với ρ = 400, 800, 1 500, 3 700 (lệnh `b6-high-rho.md`, kết quả `data/b6-high/`, 289 s). Ngân
  sách 10 %: ρ = 400 cần 344 critical cell; từ ρ = 800 thì đặt AI node ở cả 617 cell vẫn không đủ, ρ lớn nhất khi mọi cell có AI
  node là 640 người/h (ngân sách 20 %: 1 275). Phố thương mại (1 500) và giờ cao điểm Manhattan (3 700) vì vậy không khả thi với
  D3 ở 30 % node là camera. T1 của các tập trên 70 critical cell lấy từ surrogate nên không tin được (B4).
- Mật độ (`b6_sens.py`, lệnh `b6-density-devices.md`, kết quả `data/b6-density-devices.md`). Mọi tải ở B1, B3 và cỡ kho ở B5
  tuyến tính theo ρ × tỉ lệ camera × mật độ, nên bản đồ 400 node/km² ở ρ tương đương bản đồ 816 ở ρ × 400 / 816. Tập chọn cho
  ρ = 20 / 100 / 200 ở 816 chở được ρ = 41 / 204 / 408 ở 400 và 58 / 291 / 583 ở 280; ρ lớn nhất khi mọi cell có AI node là
  1 306 (400) và 1 865 (280). Kiểm bằng cách lọc ngẫu nhiên node từng cell: tỉ số đúng tới 1–2 % với 24 cell, nhưng lệch tới
  23 % ở 280 node/km² với 161 cell, vì cell bận nhất nặng thêm khi mỗi AI cell chỉ gom vài cell. Thời gian River đổi theo mật độ
  thì cần bản đồ ns-3 của K10.
- Bậc thiết bị: D3 đặt việc trích đặc trưng ở camera, AI node chỉ tìm vector, nên bậc thiết bị không đổi kết luận. Camera bận
  1,5 % ở ρ = 200 và 28 % ở ρ = 3 700 với ESP32-S3 (trường hợp xấu nhất); các bậc khác dưới 10 %. Ở AI node, tìm trong kho lớn
  nhất (152 280 vector, 80 MB) cộng trích bộ tham chiếu mất dưới 1 s ở lượt đầu và dưới 5,5 s cho V1 (L = 20), nhỏ so với 78 s
  mỗi lần xác minh. Giới hạn duy nhất là bộ nhớ: MCU không chứa nổi kho lớn (80 MB) nếu không có thẻ nhớ, chứa được kho nhỏ nhất
  (0,7 MB).

## Giai đoạn 9 (B7): viết vào bản thảo J1

- Mục VIII-F "Where to place the AI nodes" trong `paper/j1/draft-v1/tex/sec-eval.tex` (tiếng Anh), Bảng VII (số AI cell cần và
  T1 theo ρ, ba bản đồ), Hình 8 (surrogate so với ns-3) và Hình 9 (thời gian xác nhận theo số AI cell, hai cách đặt ngưỡng).
  Chỗ TODO đỏ còn lại: seed thứ hai và thời gian River ở mật độ thấp. Câu vector rời camera đã chốt (mục 376): vector chỉ đi
  từ camera tới AI node, trạm gốc vẫn chỉ nhận điểm số; TODO đó thay bằng một câu.
- Hình do `paper/j1/draft-v1/analysis/fig_k9.py` sinh: bản có nhãn ở `paper/j1/draft-v1/figs/k9-*.{pdf,png}`, bản không chữ ở
  `paper/j1/figures/` (INDEX). Lệnh ở `paper/j1/draft-v1/runs/fig-k9.md`. PDF dựng lại bằng `tex/build.sh` (cài thêm texlive
  trong container): 13 trang, không còn tham chiếu hỏng.
- Mã thí nghiệm K9 thêm vào `docs/EXPERIMENTS-INDEX.md`; mục 10 thêm vào README của bản thảo.

## Giai đoạn 10 (B8): phương án lai (mục 375)

- `cc_select.py` thêm `--npu F --vec B --crop B`: tỉ lệ F camera có NPU gửi vector, còn lại gửi ảnh cắt. Camera có NPU coi như
  rải đều, nên mỗi môi trường chở tải kỳ vọng với bản ghi trung bình F · vec + (1 − F) · crop mỗi người. Chạy trên k8 r100 với
  F = 0,8 / 0,5 / 0,2 / 0 (vector 532 B, ảnh cắt 5 KB) và hai độ nhạy ở F = 0,5 (ảnh cắt 15 KB; vector 4,1 KB), ρ = 20 / 50 /
  100 / 200, ngân sách 10 và 20 %; 6 lượt song song, mỗi lượt 225–337 s. Lệnh ở `b8-cc-*.md`, kết quả `data/b8/<tag>/`.
- Tổng hợp bằng `paper/j1/analysis/b8_summary.py` (lệnh `b8-summary.md`, kết quả `data/b8/summary.md`). Ngân sách 10 %, số AI
  cell cần ở ρ = 20 / 50 / 100: D3 24 / 34 / 69; lai F = 0,8 cần 39 / 94 / 212; F = 0,5 cần 74 / 198 / 454; F = 0,2 cần 114 / 334 /
  không đủ; chỉ ảnh cắt 140 / 414 / không đủ. Ngân sách 20 % thì gần như chia đôi số cell cần. Ảnh cắt 15 KB làm F = 0,5 cần
  237 cell ngay ở ρ = 20; vector 4,1 KB (2 048 chiều fp16) thì F = 0,5 cần 122, gần bằng chỉ ảnh cắt.
- Pha 2, đọc trên đường của B5 (ρ = 20, r100, k = 1, nội suy theo số AI cell): T là 823 s với D3, 870 / 949 / 1 080 s với F = 0,8
  / 0,5 / 0,2 và 1 165 s khi chỉ có ảnh cắt (báo nhầm 0,1 mỗi AI cell); 823 / 832 / 889 / 968 / 1 019 s khi giữ 2,4 lần báo nhầm
  cho cả hệ thống.
- K mô hình mỗi AI node: AI node trích đặc trưng L ảnh truy vấn bằng từng mô hình. Với K = 5 trên Pi 5 CPU thêm 0,95 s ở lượt đầu
  (L = 3) và 6,4 s khi xác minh V1 (L = 20, mỗi lần thăm 78 s); với Hailo-8L dưới 0,4 s. K gần như không đổi kết quả.
- Giới hạn: các tập trên khoảng 70 AI cell nằm ngoài vùng surrogate đúng (B4), nên T1 và T của F ≤ 0,5 ở ρ ≥ 50 chỉ là ước lượng
  thô. Phần ảnh cắt được AI node trích bằng mô hình đầy đủ nên có thể chính xác hơn vector của mô hình nhẹ; B8 chưa tính khác
  biệt này (cùng mô hình điểm số với B5). Tập lai khác hẳn tập của B4, nên muốn chắc phải chạy ns-3 cho F = 0,8 và 0,5 ở ρ = 20
  (39 và 74 AI cell).
