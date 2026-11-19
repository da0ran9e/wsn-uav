# 2026-11-19 · Cắt bản đồ quận Hoàng Mai, đánh dấu hồ và vùng cao tầng (chatlog mục 352)

Mục đích: lấy bản đồ một quận làm bản đồ đô thị mẫu, đánh dấu hồ và vùng cao.

Lệnh: `hoangmai.md` (`python3 paper/j1/analysis/osm_district.py 9421133 hoangmai ...`). Ranh giới quận lấy từ relation
lịch sử 9421133 (sau cải cách 2025, OSM giữ ranh giới quận cũ dưới dạng boundary=historic); dữ liệu trong khung bao tải
theo 45 ô qua OSM API 0.6 (dữ liệu thô trong scratchpad `OSM/district-hoangmai/`, không commit); độ cao từ ô Terrarium
(Mapzen/AWS, z13).

Đầu ra: `paper/j1/maps/hoangmai/` (ranh giới, hồ, vùng cao tầng dạng GeoJSON theo mét cục bộ; toà nhà
`buildings.csv.gz`; `summary.md`), hình `paper/j1/figures/map-hoangmai*.png`.

Kết quả: 40,2 km²; 17,9 % là nước, 50 hồ từ 2 ha (Yên Sở, Linh Đàm, Đầm Lớn, Định Công, Hồ Cầu) và sông Hồng; 2 921 toà
nhà, 13 % có chiều cao, 81 toà ≥ 60 m, 23 toà ≥ 120 m (cao nhất 174 m); vùng cao tầng chiếm 5,2 % diện tích; 1 552 cell
R = 100 m, 16 % chủ yếu là nước, 5 % chủ yếu trong vùng cao tầng. Địa hình phẳng (trung vị 9 m); lớp độ cao ban đầu được vẽ
nhưng nhiễu (đánh dấu cả điểm trên mặt hồ) nên đã bỏ khỏi hình, chỉ giữ thống kê.

Giới hạn: OSM ở Hà Nội thiếu nhiều nhà dân thấp tầng (2 921 toà là quá ít cho 40 km²) và 87 % nhà thiếu chiều cao, nên vùng
cao tầng chỉ gồm các toà đã có dữ liệu. Dữ liệu (c) OpenStreetMap contributors, ODbL.
