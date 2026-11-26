---
status: reference
updated: 2026-11-26
---
# J1 phiên bản đô thị (urban-v1)

Bộ bối cảnh và phát biểu bài toán cho kịch bản tìm người trong một quận đô thị hiện đại, bàn từ chatlog mục 338 tới mục 407
(2026-11-18 đến 2026-11-26). Ngày 2026-11-26 người dùng chuyển J1 sang kịch bản rừng quốc gia và khu bảo tồn (mục 408), vì kịch bản
đó ít lỗ hổng lập luận hơn. Bộ đô thị được giữ nguyên làm một phiên bản riêng: nếu sau này làm tiếp hướng đô thị thì cần một giải pháp
khác (mạng rất dày, nhà cao tầng che kênh, dữ liệu riêng tư, hạ tầng di động có sẵn).

## Tệp trong thư mục này

| Tệp | Nội dung |
|---|---|
| [CONTEXT-vi.md](CONTEXT-vi.md) | bối cảnh chi tiết, 33 mục, có nguồn và số liệu |
| [CONTEXT-SUMMARY-vi.md](CONTEXT-SUMMARY-vi.md) | bản tóm tắt gạch ý, có hình |
| [L1-VARIABLES-vi.md](L1-VARIABLES-vi.md) | biến quyết định, các câu đã chốt về cấu trúc bài toán, bảng mục tiêu |
| [PROBLEMS-vi.md](PROBLEMS-vi.md) | ba bài toán cốt lõi (P0), (P1), (P2) |
| [OUTLINE-vi.md](OUTLINE-vi.md) | dàn ý bài |
| [RESULTS-vi.md](RESULTS-vi.md) | tổng hợp kết quả hai nhánh tới 2026-11-23 |

## Các quyết định chính của phiên bản này

- Tìm người mất tích trong một quận đô thị 5–60 km², tiên nghiệm đều; mục tiêu là phân vị 0,9 của T\*, có cơ chế vá.
- Mạng dùng chung kiểu Amazon Sidewalk: chuông cửa, camera tường, camera cột, máy bán hàng; 816 node/km²; node pin không chuyển tiếp;
  cột đèn chuyển tiếp ở cell cần.
- Một UAV cánh bằng VTOL ở pha 1, UAV cánh quay xác minh V1 ở pha 2; trạm gốc ở đội cứu nạn cứu hộ.
- Truy vấn ảnh 400 KB; dữ liệu về AI node theo phương án lai (vector từ camera có NPU, ảnh cắt từ camera yếu).
- Ba bài toán giải riêng theo pha; phần mặt đất nằm trong bài tối ưu pha 1; pha 2 cũng được tối ưu.

## Tệp liên quan nằm ngoài thư mục này (giữ nguyên chỗ cũ)

- Bản đồ OSM 12 khu đô thị: `paper/j1/maps/`, hình `paper/j1/figures/map-*`, `cells-*`, `osm-*`; script `paper/j1/analysis/osm_*.py`,
  `urban_nodes.py`, `g2g_density.py`; log `logs/2026-11-17_1500-g2g-density/`, `logs/2026-11-19_*`.
- Việc K9 (đặt AI node, dữ liệu nền) của phiên kỹ thuật: `paper/j1/PLAN-K9-DATA-vi.md`, `K9-PARAMS-vi.md`, `K9-REPORT-vi.md`, log
  `logs/2026-11-18_1036-k9/`. Phần lớn kết quả K9 dùng bản đồ tổng hợp C4 nên vẫn dùng được cho kịch bản mới sau khi đổi tham số.
- Chặn không hợp tác khi truy vấn nhỏ: `paper/j1/figs-q/`.
- Mẫu phát biểu bài toán (không phụ thuộc kịch bản): `paper/j1/FORMULATION-EXAMPLES-vi.md`.
