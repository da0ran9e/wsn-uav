---
status: current
updated: 2026-11-20
---
# Sionna RT cho kênh đô thị của J1 (2026-11-20, chatlog mục 399)

Tiếp [TOOL-VAN3TWIN-vi.md](TOOL-VAN3TWIN-vi.md): bỏ VaN3Twin, xét dùng thẳng Sionna RT. Chưa cài, chưa chạy. Nguồn: [gói]
là đọc wheel `sionna-rt` 2.2.0 tải từ PyPI (không cài), [web] là tra mới hôm nay, [repo] là tài liệu trong repo.

## Sionna RT hiện nay

- Gói riêng `sionna-rt`, bản mới nhất 2.2.0, Apache-2.0, Python ≥ 3.10, chạy trên Mitsuba 3.9.1 và Dr.Jit 1.5.0; không còn
  cần TensorFlow [gói: METADATA].
- Không có GPU thì tự chuyển sang biến thể `llvm_ad_mono_polarized`, tức chạy CPU [gói: `sionna/rt/__init__.py`].
- Vật liệu ITU-R P.2040 có miền tần số ghi rõ: bê tông 1–100 GHz, gạch 1–40 GHz, kính 0,1–100 GHz, kim loại 1–100 GHz,
  đất rất khô 1–10 GHz, nên 2,4 GHz nằm trong miền [gói: `radio_materials/itu.py`].
- Hai bộ giải: `PathSolver` tính từng đường truyền cho mọi cặp phát–thu (LoS, phản xạ gương, phản xạ khuếch tán, xuyên
  vật, nhiễu xạ); `RadioMapSolver` tính bản đồ công suất trên lưới ô (mặc định 10 m) cho mỗi máy phát [gói:
  `radio_map_solver.py`]. Nhiễu xạ có từ bản 1.2 cho cả hai bộ giải, mặc định tắt [web: release notes v1.2.0].
- Cảnh nạp từ XML Mitsuba với mesh PLY; Blender chỉ là một cách tạo cảnh, mesh tự sinh từ đa giác OSM cũng được.
- Chưa thấy công trình nào kiểm Sionna cho A2G 2,4 GHz ở đô thị. Gần nhất: bộ dữ liệu AERPAW so Sionna với RSS đo từ UAV ở
  3,3 GHz, cảnh dựng từ OSM; một nghiên cứu ở Rome so Sionna 1.0.2 với đo của 1 664 thiết bị di động [web].

## Dùng vào việc nào

Đầu vào hình học đã có: đường viền và chiều cao toà nhà, đường phố, vị trí node của bốn khu
[repo: `paper/j1/analysis/osm_district.py`, `urban_nodes.py`, PLAN-TRACKS K14].

Cách A, hiệu chỉnh: dò tia trên vài ô nhỏ (khoảng 0,4 km², vài trăm node mỗi ô), rồi khớp tham số cho mô hình hình học mà
ns-3 dùng. Các tham số cần khớp:
- đường P_LoS theo góc ngẩng cho A2G (kiểu Al-Hourani) và độ lệch shadowing σ khi LoS và khi NLoS (K1a);
- suy hao mỗi toà nhà chắn ngang (đang giả định 15 dB) và số mũ suy hao dọc phố khi hai node cùng phố (K1c);
- tuỳ chọn, hệ số K Rician khi LoS (K1b).

Cách B, bảng tra trực tiếp: tính sẵn path gain cho mọi cặp cần dùng trên cả bản đồ, ns-3 đọc bảng. Node đứng yên nên G2G
chỉ cần tính một lần cho các cặp trong khoảng 150 m. Ở 816 node/km² mỗi node có chừng 58 láng giềng, tức khoảng 380 000
cặp cho 13 000 node. A2G cần lấy mẫu đường bay (ví dụ mỗi 20 m) rồi tính từ mỗi điểm tới các node trong tầm, và phải tính
lại khi đổi tuyến.

Tôi nghiêng về cách A. Cách A tốn vài ô dò tia, mô hình trong ns-3 vẫn chạy nhanh và đổi tuyến bay thoải mái, kết quả lại
nói được thành tham số trong bài. Cách B sát thực tế hơn nhưng bảng A2G gắn với tuyến bay, mà tuyến bay chính là thứ thuật
toán của ta thay đổi; chi phí trên CPU cũng chưa biết.

## Giới hạn cần nói trong bài

- Toà nhà OSM là khối đùn (LoD1): không cây, không xe, không biển hiệu, mái phẳng. Bài VaN3Twin cũng ghi đô thị lệch nhiều
  hơn nông thôn vì thiếu xe đỗ và cây [TOOL-VAN3TWIN-vi.md].
- Chiều cao toà nhà phần lớn phải đoán ở khu Hà Nội, TP.HCM; Punggol và Downtown Core dữ liệu tốt hơn [repo: CONTEXT mục 18].
- Vật liệu gán chung (bê tông cho tường, kính cho cao tầng nếu muốn), không có số đo để chỉnh.
- Không có số đo 2,4 GHz đô thị của riêng ta, nên Sionna chỉ thay mô hình thống kê bằng mô hình hình học chi tiết hơn,
  không phải dữ liệu thật.

## Thử nghiệm nhỏ đề xuất (chờ duyệt)

1. Cài `sionna-rt` vào container (kéo Mitsuba, Dr.Jit, khoảng vài trăm MB, chưa đo).
2. Sinh mesh một ô 0,4 km² của Punggol từ dữ liệu OSM đã có: đùn mỗi toà nhà thành khối, thêm mặt đất; xuất PLY và XML.
3. Đo thời gian trên CPU 4 nhân:
   - `RadioMapSolver` từ một điểm UAV ở 100 m, ô 5 m;
   - `PathSolver` cho khoảng 300 node G2G, max_depth 3, bật và tắt nhiễu xạ.
4. Từ số đo thời gian, quyết định cách A cần bao nhiêu ô và cách B có khả thi không.

Bước 2 và 3 ước khoảng một giờ công, thời gian máy chạy chưa biết. Ghi log theo mục 94, ảnh vào `paper/j1/figures/`.

## Bài nên cân nhắc ghi chú

- Hoydis và cs., Sionna RT, arXiv 2303.11103, cùng technical report của bản 1.x (nvlabs.github.io/sionna/rt/tech-report):
  mô hình vật lý và cách tính, cần nếu dùng.
- Bộ dữ liệu AERPAW so Sionna với đo UAV, arXiv 2510.08752: bằng chứng gần nhất cho A2G.
- "On the Limitations of Ray-Tracing for Learning-Based RF Tasks in Urban Environments", arXiv 2507.19653: kiểm Sionna ở
  đô thị Rome, dùng cho mục giới hạn.
