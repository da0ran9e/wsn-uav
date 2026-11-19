# tokyo-minato

- Bắt đầu: 2026-11-19 08:29:49, chạy 90 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 paper/j1/analysis/osm_district.py 1761717 tokyo-minato $S/OSM/district-tokyo-minato paper/j1/maps/tokyo-minato paper/j1/figures
```

**Kết quả**

```text
港区: 23.9 km², bbox 0.074 x 0.060 deg
35 tiles, 475276 nodes, 89301 ways
---
status: reference
updated: 2026-11-19
---
# 港区 (OSM relation 1761717)

- Diện tích 23.9 km²; tâm lat 35.64976, lon 139.74280.
- Toà nhà: 27000, có chiều cao 2615 (10 %); ≥ 60 m: 225; ≥ 100 m: 123; ≥ 120 m: 89; cao nhất 325 m.
- Nước: 14.1 % diện tích; hồ từ 2 ha: 8.
- Vùng cao tầng (nhà ≥ 60 m nới 100 m): 28.6 % diện tích.
- Địa hình (Terrarium z13): thấp nhất -15 m, trung vị 20 m, cao nhất 86 m; 37.2 % điểm cao hơn trung vị 5 m.
- Cell R = 100 m: 923; chủ yếu nước 118 (13 %); chủ yếu trong vùng cao tầng 262 (28 %); chủ yếu trong vùng cấm bay hoặc vật cản 54 (6 %).
- Vùng cấm bay ước theo OSM (sân bay, đất quân sự): 0.1 % diện tích; 赤坂プレスセンター (military).
- Vật cản (nhà ≥ 100 m nới 50 m): 123 toà, 8.7 % diện tích.

| Hồ | Diện tích (ha) |
|---|---|
| (biển) | 274.3 |
| (không tên) | 12.1 |
| 高浜運河 | 12.1 |
| (không tên) | 8.9 |
| 有明西運河 | 8.4 |
| 芝浦西運河 | 4.6 |
| 天王洲運河 | 3.2 |
| 新芝運河 | 2.6 |
/home/user/wsn-uav/paper/j1/analysis/osm_district.py:303: UserWarning: Glyph 39640 (\N{CJK UNIFIED IDEOGRAPH-9AD8}) missing from font(s) DejaVu Sans, DejaVu Sans, Inter.
  fig.savefig(f"{A.figs}/map-{A.name}{'-labelled' if labelled else ''}.png", dpi=170); plt.close(fig)
/home/user/wsn-uav/paper/j1/analysis/osm_district.py:303: UserWarning: Glyph 27996 (\N{CJK UNIFIED IDEOGRAPH-6D5C}) missing from font(s) DejaVu Sans, DejaVu Sans, Inter.
  fig.savefig(f"{A.figs}/map-{A.name}{'-labelled' if labelled else ''}.png", dpi=170); plt.close(fig)
/home/user/wsn-uav/paper/j1/analysis/osm_district.py:303: UserWarning: Glyph 36939 (\N{CJK UNIFIED IDEOGRAPH-904B}) missing from font(s) DejaVu Sans, DejaVu Sans, Inter.
  fig.savefig(f"{A.figs}/map-{A.name}{'-labelled' if labelled else ''}.png", dpi=170); plt.close(fig)
/home/user/wsn-uav/paper/j1/analysis/osm_district.py:303: UserWarning: Glyph 27827 (\N{CJK UNIFIED IDEOGRAPH-6CB3}) missing from font(s) DejaVu Sans, DejaVu Sans, Inter.
  fig.savefig(f"{A.figs}/map-{A.name}{'-labelled' if labelled else ''}.png", dpi=170); plt.close(fig)
/home/user/wsn-uav/paper/j1/analysis/osm_district.py:303: UserWarning: Glyph 26377 (\N{CJK UNIFIED IDEOGRAPH-6709}) missing from font(s) DejaVu Sans, DejaVu Sans, Inter.
  fig.savefig(f"{A.figs}/map-{A.name}{'-labelled' if labelled else ''}.png", dpi=170); plt.close(fig)
/home/user/wsn-uav/paper/j1/analysis/osm_district.py:303: UserWarning: Glyph 26126 (\N{CJK UNIFIED IDEOGRAPH-660E}) missing from font(s) DejaVu Sans, DejaVu Sans, Inter.
  fig.savefig(f"{A.figs}/map-{A.name}{'-labelled' if labelled else ''}.png", dpi=170); plt.close(fig)
/home/user/wsn-uav/paper/j1/analysis/osm_district.py:303: UserWarning: Glyph 35199 (\N{CJK UNIFIED IDEOGRAPH-897F}) missing from font(s) DejaVu Sans, DejaVu Sans, Inter.
  fig.savefig(f"{A.figs}/map-{A.name}{'-labelled' if labelled else ''}.png", dpi=170); plt.close(fig)
/home/user/wsn-uav/paper/j1/analysis/osm_district.py:303: UserWarning: Glyph 33437 (\N{CJK UNIFIED IDEOGRAPH-829D}) missing from font(s) DejaVu Sans, DejaVu Sans, Inter.
  fig.savefig(f"{A.figs}/map-{A.name}{'-labelled' if labelled else ''}.png", dpi=170); plt.close(fig)
/home/user/wsn-uav/paper/j1/analysis/osm_district.py:303: UserWarning: Glyph 28006 (\N{CJK UNIFIED IDEOGRAPH-6D66}) missing from font(s) DejaVu Sans, DejaVu Sans, Inter.
  fig.savefig(f"{A.figs}/map-{A.name}{'-labelled' if labelled else ''}.png", dpi=170); plt.close(fig)
/home/user/wsn-uav/paper/j1/analysis/osm_district.py:303: UserWarning: Glyph 22825 (\N{CJK UNIFIED IDEOGRAPH-5929}) missing from font(s) DejaVu Sans, DejaVu Sans, Inter.
  fig.savefig(f"{A.figs}/map-{A.name}{'-labelled' if labelled else ''}.png", dpi=170); plt.close(fig)
/home/user/wsn-uav/paper/j1/analysis/osm_district.py:303: UserWarning: Glyph 29579 (\N{CJK UNIFIED IDEOGRAPH-738B}) missing from font(s) DejaVu Sans, DejaVu Sans, Inter.
  fig.savefig(f"{A.figs}/map-{A.name}{'-labelled' if labelled else ''}.png", dpi=170); plt.close(fig)
/home/user/wsn-uav/paper/j1/analysis/osm_district.py:303: UserWarning: Glyph 27954 (\N{CJK UNIFIED IDEOGRAPH-6D32}) missing from font(s) DejaVu Sans, DejaVu Sans, Inter.
  fig.savefig(f"{A.figs}/map-{A.name}{'-labelled' if labelled else ''}.png", dpi=170); plt.close(fig)
/home/user/wsn-uav/paper/j1/analysis/osm_district.py:303: UserWarning: Glyph 26032 (\N{CJK UNIFIED IDEOGRAPH-65B0}) missing from font(s) DejaVu Sans, DejaVu Sans, Inter.
  fig.savefig(f"{A.figs}/map-{A.name}{'-labelled' if labelled else ''}.png", dpi=170); plt.close(fig)
```
