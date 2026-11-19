# 2026-11-19 · Thăm dò dữ liệu OpenStreetMap cho bản đồ đô thị mẫu (chatlog mục 350)

Mục đích: xem khu đô thị nào có đủ dữ liệu toà nhà (đường viền, chiều cao) để làm bản đồ mẫu cho J1.

Lệnh: `probe.md` (`python3 paper/j1/analysis/osm_probe.py --half 0.003`): gọi OSM API 0.6 cho một ô ±0,003° (khoảng
0,4 km²) quanh tâm mỗi khu. Overpass và Geofabrik không vào được từ container này (bị chính sách mạng chặn), API của
www.openstreetmap.org thì được.

Kết quả: Singapore CBD 92 % toà nhà có chiều cao hoặc số tầng (cao nhất 245 m), Manhattan 79 % (366 m), Vinhomes Ocean
Park 70 % (90 m), Cầu Giấy 12 %, Royal City 10 %, Quận 1 16 %. Bảng ở `paper/j1/CONTEXT-vi.md` mục 18.

Dang dở: chưa tải cả khu; chưa kiểm độ đủ của đường viền toà nhà (số toà nhà ở Hà Nội có vẻ thiếu). Dữ liệu (c)
OpenStreetMap contributors, ODbL.
