---
status: current
updated: 2026-11-18
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
| `assign.csv` | map, seed, node, ai_node, hops (node thường giao cho AI node nào, cách bao nhiêu chặng; dùng cho K9) |

Dữ liệu cũ dùng được ngay: C4 (`logs/2026-10-27_1714-campaign4/`), gió và takeover (`logs/2026-10-31_0000-wind/`,
`logs/2026-11-01_0600-takeover/`), Deluge (`logs/2026-10-30_1545-deluge-r100/`).

## Nhánh lý thuyết

> 2026-11-16: bản thảo journal v1 ở `draft-v1/` (xem `draft-v1/README-vi.md`) đã có bản đầu của L1 (Định lý 1, NP-khó),
> một kết quả thay cho L2 (chặn phủ Λ\*, Định lý 2), L3 (Mệnh đề 3 và bán kính hỏi thích nghi) và một phần L4 (chặn một
> radio, chưa có chặn trên cho River). Các ô bên dưới chưa đánh dấu xong vì bản thảo còn chờ đánh giá.

- [ ] **L1** Phát biểu bài toán tối ưu; bổ đề NP-khó theo khuôn Le Ny 2012 (Định lý 2)
  - Đầu vào: `research_notes/literature/papers/leny2012-dtsp.md`, phác thảo ở `paper/j1/ND1-TRIAL-vi.md`. Đầu ra: mục
    Problem formulation trong `paper/j1/`.
  - Mục tiêu chung: tối thiểu tổng thời gian pha 1 + pha 2; tập critical cell là biến (chatlog mục 335, 338).
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

> 2026-11-18 (chatlog mục 336–337): sửa theo các quyết định ở mục 326–335 (`paper/j1/CONTEXT-vi.md`). Thêm K9 (chọn critical
> cell), K10 (mật độ), K11 (LB 5 seed); tách K1 thành ba bậc vì kênh làm phức tạp dần; K3 không còn chờ L3. Thứ tự đề xuất:
> K11, K9 (phần nối `river_plan.py` trước, solver khi có số), K1a, K10, K3, rồi K6, K5, K4, K1b, K1c, K7.
>
> Hạ tầng: container cloud mới không có bản build ns-3. `logs/2026-10-27_1714-campaign4/camp-bin5.tar.xz` có binary và thư
> viện CAMP-BIN5 nhưng không có header, nên binary có mã mới (như `--tree`) phải build lại ns-3.46 hoặc chạy trên máy người
> dùng. Tính thời gian build vào chi phí khi bàn trước lúc chạy.

- [ ] **K1a** Kênh A2G bậc 1: xác suất LoS theo góc ngẩng (Al-Hourani 2014), trạng thái LoS cố định cho mỗi node trong một
  lượt bay, che khuất log-normal tương quan không gian (Gudmundson 1991); giữ chế độ η cố định cũ để so với số C4
  - Đầu vào: `research_notes/literature/2026-11-12/04-a2g-channel.md`, `papers/alhourani2014-lap.md`,
    `papers/gudmundson1991-shadow.md`, CONTEXT mục 9. Chỉ sửa `uav-coop/examples/coop-pass.cc` (PHY, rẻ). Đầu ra: mô hình
    mới, R50 theo chế độ, lượt bay hiệu chỉnh, CSV theo schema chung. Cần bàn chi phí trước khi chạy.
  - Trạng thái: chưa nhận · Phiên: · Báo cáo:
- [ ] **K1b** Kênh bậc 2: fading tương quan theo thời gian (theo khối thời gian kết hợp thay vì bốc mỗi gói); hiệu chỉnh
  bằng dữ liệu Dryad (doi:10.25349/D9KS3W) nếu dùng được
  - Phụ thuộc: K1a. Trạng thái: chờ K1a · Phiên: · Báo cáo:
- [ ] **K1c** Kênh G2G có LoS/NLoS theo cấu trúc (phố, khối nhà, địa hình), thay che khuất độc lập mỗi cặp
  - Cần bản đồ vật cản và sửa `Link` trong `uav-coop2/examples/coop2-river.cc`; nặng, có thể để sau J1. Đầu vào: CONTEXT
    mục 9.
  - Trạng thái: chưa nhận · Phiên: · Báo cáo:
- [ ] **K2** Quỹ đạo sinh từ động lực bay: dẫn đường L1, gió đều 0–15 m/s cộng nhiễu loạn Dryden; có sai số dọc đường bay
  - Đầu vào: `uav-l2/tools/wind_path.py`, `research_notes/literature/2026-11-12/05-wind-deviation.md`. Đầu ra: bộ
    sinh quỹ đạo mới, `track.csv`.
  - Trạng thái: chưa nhận · Phiên: · Báo cáo:
- [ ] **K3** Takeover với bán kính hỏi động theo h(ē); ghép Ring của các critical cell gần nhau
  - Công thức h = ⌈ê/(√3·R)⌉ + 1 và cách ước ê đã có, đánh giá ngoại tuyến ở `paper/j1/draft-v1/` (README mục 5); L3 chỉ
    còn cần cho chứng minh. Đầu vào: `uav-coop2/examples/coop2-river.cc` (`--takeoverSeq`). Đầu ra: số frame, thời điểm
    sẵn sàng so với bản 3 hop cố định.
  - Trạng thái: chưa nhận · Phiên: · Báo cáo:
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
  - Chỉ chạy Python, nhưng container chưa có LKH (cài trước). Đầu vào: `research_notes/literature/papers/isaacs2011-dtspn.md`.
    Đầu ra: tỉ số độ dài tour trên các bản đồ C4.
  - Trạng thái: chưa nhận · Phiên: · Báo cáo:
- [ ] **K7** Đo chi phí pha 0 trong ns-3: số frame và thời gian dựng lưới cell, CL, cặp gateway, bảng định tuyến, lịch kênh
  - Phụ thuộc: L5 (đại lượng cần đo). Đầu ra: số đo để so với mô hình L5.
  - Trạng thái: chờ L5 · Phiên: · Báo cáo:
- [ ] **K8** Nếu kịp: năng lượng cho AI trên node (khoảng 0,2–1,6 mJ mỗi lần suy luận theo tài liệu); surrogate cho
  LM-Tour
  - Phần tốc độ đối sánh μ của AI node chuyển sang K9 (cần ngay cho bài chọn critical cell).
  - Trạng thái: chưa nhận · Phiên: · Báo cáo:
- [ ] **K9** Chọn critical cell và đánh đổi số critical cell theo CONTEXT mục 13 (facility location có sức chứa, ràng buộc
  H chặng và bộ nhớ, không dùng D_min; mục tiêu chung là tổng thời gian pha 1 + pha 2, chatlog mục 338), thay Algorithm 3
  (score vượt μ + 2σ) của `uav-coop2/tools/river_plan.py`
  - Các bước: (1) `river_plan.py` và `mission.py` nhận tập critical cell từ file ngoài; (2) thêm thuộc tính AI node
    (M_v, μ_v) và lượng dữ liệu d_u vào bản đồ; (3) solver Python dùng surrogate T̂_River cho T_giao; (4) quét số critical
    cell (ít đến nhiều) trên cùng bản đồ, đo T\* pha 1 bằng ns-3 và thời gian pha 2 bằng mô hình đội 2, vẽ đường đánh đổi;
    (5) chạy lại với tập tối ưu. Đầu ra: `assign.csv`, tập critical cell, đường đánh đổi, T\* so với Algorithm 3.
  - μ chưa có nguồn đo (mục 338): dùng mô hình theo bậc thiết bị của K12 và quét độ nhạy. Bước (1) làm được ngay.
  - Kế hoạch chi tiết: [PLAN-K9-DATA-vi.md](PLAN-K9-DATA-vi.md) (bước B0–B7).
  - Trạng thái: đang làm · Phiên: 2026-11-18, phiên ghi chú bài báo (session_01Anfb7c); xong B2, B0, B1, B3, B4 seed 1 (mục 348:
    tạm dừng ở 1 seed), B5; còn B6, B7 · Báo cáo: [logs/2026-11-18_1036-k9](../../logs/2026-11-18_1036-k9/README.md)
- [ ] **K10** Mật độ phụ 400 và 280 node/km² (giãn cách 50 và 60 m, CONTEXT mục 4 và 10)
  - `uav-l2/tools/map_gen.py --spacing`; kiểm deploy, partition và chọn cặp gateway với cell 7–10 node, rồi chạy pha 1.
    Đầu ra: T\*, P_k mức cell và số cặp gateway theo mật độ.
  - Trạng thái: chưa nhận · Phiên: · Báo cáo:
- [ ] **K11** Cây dùng chung và lập kế hoạch cân tải (`--tree`, `uav-coop2/tools/river_lb.py`) đủ 5 seed của DLG (k8, r100)
  - Đầu vào: `paper/j1/draft-v1/analysis/run_lb.sh`, `lb_compare.py`, kết quả seed 1 ở `paper/j1/draft-v1/figs/lb-seed1.md`.
    Đầu ra: bảng 5 seed thay bảng một seed trong `paper/j1/draft-v1/README-vi.md` mục 9.
  - Trạng thái: chờ (tạm bỏ qua để làm K9, mục 341; cần build ns-3.46 có `--tree`) · Phiên: 2026-11-18 (session_01Anfb7c) · Báo cáo:

- [ ] **K12** Khảo sát bộ nhớ và đối sánh ở node (chatlog mục 338, CONTEXT mục 14): lượng ảnh và khung có người mỗi giờ của
  camera đô thị, dung lượng nhớ của node camera rẻ, chính sách lưu của hệ phân tích video tại biên; mô hình μ (thời gian
  đối sánh) theo bậc thiết bị và theo loại dữ liệu gửi về AI node (ảnh gốc, ảnh cắt người, vector đặc trưng)
  - Đầu vào: `research_notes/l1-edge-recognition/edge_devices.md`, `research_notes/literature/2026-11-12/06-deployment.md`.
    Tra repo trước rồi mới lên internet (CLAUDE.md mục 328). Đầu ra: bảng tham số cho K9 và một đề xuất chính sách giữ/bỏ.
  - Kế hoạch chi tiết: [PLAN-K9-DATA-vi.md](PLAN-K9-DATA-vi.md) (bước B0–B7).
  - Trạng thái: chưa nhận · Phiên: · Báo cáo:
- [ ] **K13** Pha 2 trong J1 (chatlog mục 338): mục tiêu chung là tối thiểu tổng thời gian pha 1 + pha 2. Đưa mô hình đội 2
  (UAV cánh quay, `uav-l2/docs/MISSION-vi.md`, `mission_policy.py`) vào cùng đường đo với pha 1, báo T_pha1 + T_pha2
  - Đầu ra: thời gian hai pha theo từng bản đồ và từng tập critical cell (dùng cho K9); báo L1 để đưa vào phát biểu bài toán.
  - Cần thử (mục 348): trường hợp điểm nghi vấn nằm ở legacy node. Cách hiểu của người ghi, chờ người dùng xác nhận: người
    được thấy ở camera của một node thường (không có AI), AI node chỉ giữ bản ghi; ảnh nằm ở node thường nên với V1 việc đối
    sánh lại bằng bộ tham chiếu R không làm tại chỗ được, phải chuyển về AI node (thêm số chặng giao) hoặc lên UAV. So pha 2
    khi nghi vấn ở AI node và ở node thường, theo khoảng cách giao.
  - Kế hoạch chi tiết: [PLAN-K9-DATA-vi.md](PLAN-K9-DATA-vi.md) (bước B0–B7).
  - Trạng thái: chưa nhận · Phiên: · Báo cáo:

- [ ] **K14** Bản đồ đô thị mẫu từ OpenStreetMap (chatlog mục 350, CONTEXT mục 18): toà nhà (đường viền, chiều cao), đường
  phố, node đặt theo nhà và phố ở mật độ khoảng 816 node/km², lưới cell lục giác phủ lên; xuất cùng định dạng bản đồ hiện có
  để `mission.py` chạy được
  - Đầu ra cho K1a (LoS A2G bằng hình học), K1c (LoS G2G), K5 (nhà cao hơn độ cao bay thành vùng cấm) và điểm lơ lửng V1.
    Chỉ dùng API của www.openstreetmap.org (Overpass, Geofabrik bị chặn). Ghi nguồn ODbL.
  - Chờ người dùng chọn khu mẫu.
  - Trạng thái: chưa nhận · Phiên: · Báo cáo:

## Điểm gặp

Cứ 3–4 tuần một lần, hoặc khi một việc có phụ thuộc vừa xong. Mỗi lần ghi một dòng: ngày, việc đã đối chiếu, kết luận,
việc đổi hướng.

| Ngày | Đối chiếu | Kết luận | Đổi hướng |
|---|---|---|---|

## Để sau J1

Pha 2 với mục tiêu biết dần và trọng số cập nhật online (bản cơ bản của pha 2 đã vào J1 ở K13); chọn CL, CH, CGW bằng supervised learning; thời
gian chạy AI theo CPU và bộ nhớ; mô phỏng bộ nhớ và buffer; mục "Phát triển layer 2 của pha 1 kết hợp tối ưu thời điểm
thăm của pha 2" (người dùng chưa viết xong).
