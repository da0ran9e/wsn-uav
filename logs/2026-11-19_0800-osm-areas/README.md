# 2026-11-19 · Chín khu đô thị ứng viên cho bản đồ mẫu (chatlog mục 351)

Mục đích: so các khu đô thị ứng viên theo nhà (diện tích, chiều cao), hồ và sông, đất trống, và số cell R = 100 m không có
chỗ đặt node, để chọn bản đồ mẫu cho J1.

Lệnh: `areas.md` (`python3 paper/j1/analysis/osm_areas.py CACHE FIGS`), mỗi khu một ô 4 × 4 km tải theo 12 ô nhỏ qua OSM
API 0.6. Dữ liệu thô 238 MB nằm trong scratchpad (`OSM/`), không commit. Cần `pip install shapely`.

Đầu ra: bảng trong `areas.md` và `paper/j1/CONTEXT-vi.md` mục 18; hình `paper/j1/figures/osm-*.png`.

Giới hạn: biển (đường bờ biển) không được tính là nước, nên Marina (Singapore) và các khu ven biển bị thiếu phần nước;
34–69 % diện tích "chưa gắn thẻ" vì OSM ít gắn thẻ đất ở, nên số đất trống chỉ là cận dưới. Dữ liệu (c) OpenStreetMap
contributors, ODbL.
