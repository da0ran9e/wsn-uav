---
status: current
updated: 2026-11-14
---
# Kế hoạch J1 theo hai nhánh: lý thuyết và kỹ thuật

File chung để các session nhận việc và báo cáo (chatlog mục 318–320). Đây là kế hoạch thử nghiệm, không sửa đề cương.
Mốc nộp J1 dự kiến 6–7/2027.

## Cách dùng

- Nhận việc: đổi `Trạng thái` thành `đang làm`, điền `Phiên` (ngày và mô tả ngắn session), commit và push ngay để session
  khác thấy. Mỗi session chỉ nhận việc của một nhánh.
- Xong việc: đánh `[x]`, đổi `Trạng thái` thành `xong`, viết `Báo cáo` trong một hai dòng (kết quả chính, đường dẫn file
  hoặc log, commit). Chi tiết để trong file đầu ra, không chép vào đây.
- Bị chặn: `Trạng thái` là `chờ`, ghi chờ việc gì (ví dụ `chờ K1`).
- Chỉ sửa dòng của việc mình nhận. Gặp xung đột git ở file này thì giữ cả hai bản sửa, vì mỗi session sửa dòng khác nhau.
- Việc cần chạy ns-3 hay chạy lâu thì bàn chi phí với người dùng trước (CLAUDE.md §6, mục 35).
- Thư mục làm việc: nhánh lý thuyết ghi vào `paper/j1/` và `uav-l2/tools/theory/`; nhánh kỹ thuật ghi vào `uav-l2/`,
  `uav-coop2/`. Cả hai ghi log vào `logs/` theo quy tắc mục 94.

Giá trị `Trạng thái`: `chưa nhận`, `đang làm`, `chờ`, `xong`.

## Dữ liệu chung giữa hai nhánh

Mỗi lần chạy của nhánh kỹ thuật xuất các CSV dưới đây vào `logs/<thư mục>/data/`, để script lý thuyết đọc thẳng. Đổi
schema thì sửa bảng này trước rồi báo ở việc liên quan.

| File | Cột |
|---|---|
| `cells.csv` | map, seed, cluster, q, r, role (spine, bank, ring, critical, other), ready_s, frames_tx |
| `holders.csv` | map, seed, cluster, packet, q, r (cell giữ gói sau lượt bay) |
| `track.csv` | map, seed, cluster, packet, x, y, x_plan, y_plan (điểm phát thật và dự kiến) |
| `runs.csv` | map, seed, scheme, channel, wind, T_star_s, readiness_mean_s, frames_total, energy_J |

Dữ liệu cũ dùng được ngay: C4 (`logs/2026-10-27_1714-campaign4/`), gió và takeover (`logs/2026-10-31_0000-wind/`,
`logs/2026-11-01_0600-takeover/`), Deluge (`logs/2026-10-30_1545-deluge-r100/`).

## Nhánh lý thuyết

- [ ] **L1** Phát biểu bài toán tối ưu; bổ đề NP-khó theo khuôn Le Ny 2012 (Định lý 2)
  - Đầu vào: `research_notes/literature/papers/leny2012-dtsp.md`, phác thảo ở `paper/j1/ND1-TRIAL-vi.md`. Đầu ra: mục
    Problem formulation trong `paper/j1/`.
  - Trạng thái: chưa nhận · Phiên: · Báo cáo:
- [ ] **L2** Định lý A bản chặt: biên an toàn theo file, số gói nhận khi bay ngang, số hạng √(Q ln m), trích Zeng 2018
  - Đầu vào: `uav-l2/tools/theory/theorem_a.py`, dữ liệu C4. Kiểm lại trên kênh K1 khi có. Đầu ra: phát biểu và chứng
    minh, hình so với số đo.
  - Trạng thái: chưa nhận · Phiên: · Báo cáo:
- [ ] **L2b** Định lý A khi bỏ giả định A1 (fading tương quan theo thời gian, che khuất tương quan không gian)
  - Phụ thuộc: K1. Đầu ra: điều kiện của định lý thay đổi thế nào, kiểm trên số đo K1.
  - Trạng thái: chờ K1 · Phiên: · Báo cáo:
- [ ] **L3** Mệnh đề B dạng xác suất; công thức bán kính hỏi h(ē) cho takeover
  - Đầu vào: `uav-l2/tools/theory/prop_b.py`, kết quả ngày 5. Đầu ra: phát biểu, chứng minh chặn số hop, công thức giao
    cho K3.
  - Trạng thái: chưa nhận · Phiên: · Báo cáo:
- [ ] **L4** Cận D theo khung Courtade–Wesel 2014; thử chứng minh River kém tối ưu không quá hằng số lần
  - Đầu vào: thời điểm sẵn sàng đo được (C4, `cells.csv`). Đầu ra: phát biểu, khoảng cách giữa cận và số đo.
  - Trạng thái: chưa nhận · Phiên: · Báo cáo:
- [ ] **L5** Mô hình chi phí pha 0 (PECEE): số frame thiết lập, thời gian bão hoà, chi phí chia theo số truy vấn; lý do lịch
  7 màu
  - Đầu ra: công thức và các đại lượng K7 phải đo. So với số đo K7 khi có.
  - Trạng thái: chưa nhận · Phiên: · Báo cáo:
- [ ] **L6** Định lý C (giá trị thông tin của kế hoạch), phát biểu theo H(f(X)); chỉ làm nếu kịp
  - Đầu vào: Gallager 1976, Minsky 2003 (cần PDF). Đầu ra: làm hoặc bỏ, kèm lý do.
  - Trạng thái: chưa nhận · Phiên: · Báo cáo:
- [ ] **L7** Đọc và ghi chú theo `research_notes/literature/METHOD-vi.md`: Wang 2020 (IoT-J), Stojanovic 2009, Gallager 1976
  - Phụ thuộc: người dùng gửi PDF. Đầu ra: ghi chú trong `research_notes/literature/papers/`, đoạn định vị đóng góp.
  - Trạng thái: chờ PDF · Phiên: · Báo cáo:

## Nhánh kỹ thuật

- [ ] **K1** Kênh có tương quan: fading tương quan theo thời gian, che khuất log-normal tương quan không gian, hiệu chỉnh
  bằng dữ liệu Dryad (doi:10.25349/D9KS3W)
  - Đầu vào: `research_notes/literature/2026-11-12/04-a2g-channel.md`. Đầu ra: mô hình kênh mới trong ns-3, lượt bay
    hiệu chỉnh, CSV theo schema chung. Cần bàn chi phí trước khi chạy.
  - Trạng thái: chưa nhận · Phiên: · Báo cáo:
- [ ] **K2** Quỹ đạo sinh từ động lực bay: dẫn đường L1, gió đều 0–15 m/s cộng nhiễu loạn Dryden; có sai số dọc đường bay
  - Đầu vào: `uav-l2/tools/wind_path.py`, `research_notes/literature/2026-11-12/05-wind-deviation.md`. Đầu ra: bộ
    sinh quỹ đạo mới, `track.csv`.
  - Trạng thái: chưa nhận · Phiên: · Báo cáo:
- [ ] **K3** Takeover với bán kính hỏi động theo h(ē); ghép Ring của các critical cell gần nhau
  - Phụ thuộc: L3 (công thức h(ē)). Đầu vào: `uav-coop2/examples/coop2-river.cc` (`--takeoverSeq`). Đầu ra: số frame,
    thời điểm sẵn sàng so với bản 3 hop cố định.
  - Trạng thái: chờ L3 · Phiên: · Báo cáo:
- [ ] **K4** Baseline công bằng: Deluge có low-power listening, cùng tập cell đích, quét Imin và cỡ page; một bản kiểu
  Typhoon
  - Đầu vào: `logs/2026-10-30_1545-deluge-r100/`, `research_notes/literature/2026-11-12/02-code-dissemination.md`.
    Đầu ra: bảng so sánh mới. Cần bàn chi phí trước khi chạy.
  - Trạng thái: chưa nhận · Phiên: · Báo cáo:
- [ ] **K5** Kịch bản vùng cấm bay: đa giác cấm trên bản đồ, tour né vùng, camera bên trong chỉ nhận qua mặt đất
  - Đầu ra: so River với FC và kéo trực tiếp trên vài bản đồ. Báo L2 để dự đoán trước kết quả.
  - Trạng thái: chưa nhận · Phiên: · Báo cáo:
- [ ] **K6** Tour tham chiếu để đo CHORD và LM-Tour cách tối ưu bao xa: lấy mẫu, biến đổi Noon–Bean, giải bằng LKH (theo
  Isaacs 2011)
  - Chỉ chạy Python. Đầu vào: `research_notes/literature/papers/isaacs2011-dtspn.md`. Đầu ra: tỉ số độ dài tour trên
    các bản đồ C4.
  - Trạng thái: chưa nhận · Phiên: · Báo cáo:
- [ ] **K7** Đo chi phí pha 0 trong ns-3: số frame và thời gian dựng lưới cell, CL, cặp gateway, bảng định tuyến, lịch kênh
  - Phụ thuộc: L5 (đại lượng cần đo). Đầu ra: số đo để so với mô hình L5.
  - Trạng thái: chờ L5 · Phiên: · Báo cáo:
- [ ] **K8** Nếu kịp: năng lượng cho AI trên node (khoảng 0,2–1,6 mJ mỗi lần suy luận theo tài liệu); surrogate cho
  LM-Tour
  - Trạng thái: chưa nhận · Phiên: · Báo cáo:

## Điểm gặp

Cứ 3–4 tuần một lần, hoặc khi một việc có phụ thuộc vừa xong. Mỗi lần ghi một dòng: ngày, việc đã đối chiếu, kết luận,
việc đổi hướng.

| Ngày | Đối chiếu | Kết luận | Đổi hướng |
|---|---|---|---|

## Để sau J1

Pha 2 (UAV cánh quay thăm mục tiêu biết dần, trọng số cập nhật online); chọn CL, CH, CGW bằng supervised learning; thời
gian chạy AI theo CPU và bộ nhớ; mô phỏng bộ nhớ và buffer; mục "Phát triển layer 2 của pha 1 kết hợp tối ưu thời điểm
thăm của pha 2" (người dùng chưa viết xong).
