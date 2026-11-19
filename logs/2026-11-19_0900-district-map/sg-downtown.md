# sg-downtown

- Bắt đầu: 2026-11-19 08:29:16, chạy 15 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 paper/j1/analysis/osm_district.py 19910172 sg-downtown $S/OSM/district-sg-downtown paper/j1/maps/sg-downtown paper/j1/figures
```

**Kết quả**

```text
Downtown Core: 5.1 km², bbox 0.028 x 0.036 deg
9 tiles, 77372 nodes, 16081 ways
---
status: reference
updated: 2026-11-19
---
# Downtown Core (OSM relation 19910172)

- Diện tích 5.1 km²; tâm lat 1.28679, lon 103.85550.
- Toà nhà: 757, có chiều cao 598 (79 %); ≥ 60 m: 78; ≥ 100 m: 42; ≥ 120 m: 38; cao nhất 245 m.
- Nước: 2.0 % diện tích; hồ từ 2 ha: 1.
- Vùng cao tầng (nhà ≥ 60 m nới 100 m): 27.0 % diện tích.
- Địa hình (Terrarium z13): thấp nhất -17 m, trung vị 13 m, cao nhất 127 m; 30.3 % điểm cao hơn trung vị 5 m.
- Cell R = 100 m: 195; chủ yếu nước 2 (1 %); chủ yếu trong vùng cao tầng 52 (27 %); chủ yếu trong vùng cấm bay hoặc vật cản 16 (8 %).
- Vùng cấm bay ước theo OSM (sân bay, đất quân sự): 0.0 % diện tích; không có.
- Vật cản (nhà ≥ 100 m nới 50 m): 42 toà, 10.9 % diện tích.

| Hồ | Diện tích (ha) |
|---|---|
| (biển) | 9.2 |
```
