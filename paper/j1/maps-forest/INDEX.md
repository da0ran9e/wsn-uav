---
status: current
updated: 2026-11-26
---
# Bản đồ mẫu rừng và khu bảo tồn (J1 bối cảnh v2, chatlog mục 410)

Mỗi khu một cửa sổ 10 × 10 km (cỡ một chuyến bay), cắt theo ranh giới khu bảo vệ trong OSM. Sinh bằng `paper/j1/analysis/osm_park.py`,
log `logs/2026-11-26_1500-park-maps/`, hình `paper/j1/figures/park-<khu>[-labelled].png`. Dữ liệu (c) OpenStreetMap contributors,
ODbL; độ cao từ Terrarium tiles z13 (SRTM và nguồn khác), lấy mẫu lưới 25 m.

Xếp từ phẳng tới dốc. Chênh cao cell là hiệu độ cao lớn nhất và nhỏ nhất trong bán kính 100 m quanh tâm cell R = 100 m (trung vị /
phân vị 90). Cell sát tuyến là cell có tâm cách đường mòn hoặc đường xe không quá 100 m.

| Khu | Địa hình | Vùng xét (km²) | Độ cao (m) | Độ dốc trung vị (°) | Diện tích dốc > 30° | Chênh cao cell (m) | Đường mòn (km/km²) | Cell sát tuyến | Suối (km) | Toà nhà |
|---|---|---|---|---|---|---|---|---|---|---|
| [VQG Cát Tiên (Đồng Nai)](cattien/summary.md) | rừng đất thấp, phẳng | 92.2 | 83–247 | 4.2 | 0 % | 14 / 26 | 0.44 | 8 % | 9.8 | 31 |
| [NP Bayerischer Wald (Đức)](bayerwald/summary.md) | núi thấp, thoải | 59.4 | 764–1440 | 10.1 | 0 % | 44 / 79 | 2.64 | 44 % | 178.4 | 281 |
| [VQG Cúc Phương (Ninh Bình)](cucphuong/summary.md) | núi đá vôi karst | 87.8 | 20–600 | 22.9 | 27 % | 92 / 140 | 0.29 | 8 % | 0.0 | 12 |
| [Yosemite NP (Mỹ)](yosemite/summary.md) | núi granit, thung lũng sâu | 100.0 | 1203–2766 | 20.3 | 29 % | 91 / 295 | 1.66 | 27 % | 82.4 | 1246 |
| [VQG Bạch Mã (Huế)](bachma/summary.md) | núi ven biển | 81.0 | 32–1455 | 27.5 | 40 % | 126 / 185 | 0.09 | 4 % | 28.5 | 16 |
| [Great Smoky Mountains NP (Mỹ)](smokies/summary.md) | núi rừng, suối dày | 100.0 | 730–2025 | 28.6 | 42 % | 118 / 157 | 0.72 | 19 % | 169.6 | 16 |
| [Kinabalu Park (Malaysia)](kinabalu/summary.md) | núi cao, đỉnh 4 095 m | 87.6 | 1002–4057 | 30.8 | 52 % | 152 / 296 | 0.23 | 4 % | 24.0 | 136 |
| [VQG Hoàng Liên (Lào Cai)](hoanglien/summary.md) | núi cao, Fansipan | 70.1 | 1180–3117 | 32.4 | 58 % | 156 / 227 | 0.25 | 5 % | 10.9 | 316 |

Lưu ý dữ liệu:
- Lớp rừng của OSM không dùng được: đa giác rừng lớn bị cắt ở biên cửa sổ nên nhiều khu ra gần 0 % dù thực tế là rừng kín.
- Đường mòn và suối ở các vườn Việt Nam trên OSM có thể thưa hơn thực tế nhiều (Cúc Phương không có suối nào trong OSM; vùng karst cũng ít
  suối mặt). Mật độ đường mòn vì vậy là cận dưới, nhất là với Việt Nam.
- Kinabalu: vùng quanh đỉnh bị nhoè do dữ liệu SRTM thiếu và được nội suy. Cát Tiên: địa hình phẳng nên bóng đổ chủ yếu là nhiễu tán
  rừng trong SRTM.
- Bayerischer Wald: nửa phía đông cửa sổ nằm ngoài ranh giới (bên Séc), nên vùng xét chỉ 59 km².
- Yosemite, Kinabalu và Hoàng Liên có nhiều toà nhà vì cửa sổ chứa thung lũng Yosemite, khu trụ sở vườn Kinabalu và rìa thị xã Sa Pa.
