# Bản đồ mẫu rừng và khu bảo tồn (chatlog mục 410)

Mục đích: khảo sát địa hình một số khu rừng và khu bảo tồn cho bối cảnh J1 v2 (rừng, tìm người mất tích, 802.15.4).

Lệnh: mỗi khu một file `<khu>.md`, chạy `python3 paper/j1/analysis/osm_park.py NAME LAT LON CACHE OUT FIGS --rel ID|--way ID`
với cửa sổ 10 × 10 km. Ranh giới tra bằng Nominatim: Cúc Phương r15882261, Bạch Mã r7122565, Hoàng Liên r7144302, Cát Tiên r7090891,
Yosemite r1643367, Great Smoky Mountains r2131838, Bayerischer Wald r1864214, Kinabalu w499086161. Dữ liệu OSM qua API map call
(Overpass bị chặn), độ cao Terrarium z13 (AWS). Cache thô để ở scratchpad, không commit.

Đầu ra: `paper/j1/maps-forest/<khu>/{summary.md, stats.json, trails.geojson, streams.geojson}`, bảng `paper/j1/maps-forest/INDEX.md`,
hình `paper/j1/figures/park-<khu>[-labelled].png`.

Kết quả chính: hai nhóm địa hình, phẳng hoặc thoải (Cát Tiên, Bayerischer Wald; chênh cao trong 100 m quanh tâm cell dưới 50 m) và
núi (sáu khu còn lại; 90–160 m trung vị); đường mòn và đường xe chỉ phủ 4–8 % cell ở các vườn Việt Nam. Lớp rừng OSM không dùng được.
Còn dở: chưa có lớp phủ rừng tin cậy (cần bản đồ lớp phủ như ESA WorldCover); chưa tính che khuất địa hình cho A2G.
