# seoul-gangnam

- Bắt đầu: 2026-11-19 08:23:00, chạy 224 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 paper/j1/analysis/osm_district.py 2410520 seoul-gangnam $S/OSM/district-seoul-gangnam paper/j1/maps/seoul-gangnam paper/j1/figures
```

**Kết quả**

```text
강남구: 40.4 km², bbox 0.115 x 0.083 deg
70 tiles, 311799 nodes, 50394 ways
/usr/local/lib/python3.13/dist-packages/shapely/constructive.py:919: RuntimeWarning: invalid value encountered in polygonize
  return lib.polygonize(geometries, **kwargs)
---
status: reference
updated: 2026-11-19
---
# 강남구 (OSM relation 2410520)

- Diện tích 40.4 km²; tâm lat 37.49763, lon 127.06218.
- Toà nhà: 18655, có chiều cao 3475 (19 %); ≥ 60 m: 649; ≥ 100 m: 70; ≥ 120 m: 27; cao nhất 264 m.
- Nước: 1.1 % diện tích; hồ từ 2 ha: 2.
- Vùng cao tầng (nhà ≥ 60 m nới 100 m): 22.7 % diện tích.
- Địa hình (Terrarium z13): thấp nhất -6 m, trung vị 33 m, cao nhất 296 m; 39.6 % điểm cao hơn trung vị 5 m.
- Cell R = 100 m: 1558; chủ yếu nước 0 (0 %); chủ yếu trong vùng cao tầng 354 (23 %); chủ yếu trong vùng cấm bay hoặc vật cản 30 (2 %).
- Vùng cấm bay ước theo OSM (sân bay, đất quân sự): 0.0 % diện tích; (không tên) (military).
- Vật cản (nhà ≥ 100 m nới 50 m): 70 toà, 2.4 % diện tích.

| Hồ | Diện tích (ha) |
|---|---|
| 탄천 | 32.1 |
| (không tên) | 6.4 |
/home/user/wsn-uav/paper/j1/analysis/osm_district.py:277: UserWarning: Glyph 53444 (\N{HANGUL SYLLABLE TAN}) missing from font(s) DejaVu Sans, Inter, DejaVu Sans.
  fig.savefig(f"{A.figs}/map-{A.name}{'-labelled' if labelled else ''}.png", dpi=170); plt.close(fig)
/home/user/wsn-uav/paper/j1/analysis/osm_district.py:277: UserWarning: Glyph 52380 (\N{HANGUL SYLLABLE CEON}) missing from font(s) DejaVu Sans, Inter, DejaVu Sans.
  fig.savefig(f"{A.figs}/map-{A.name}{'-labelled' if labelled else ''}.png", dpi=170); plt.close(fig)
```
