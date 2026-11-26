"""Cut a square window out of a forest or protected area: trails, streams, forest, terrain (J1 context v2, chatlog item 410).

    python3 paper/j1/analysis/osm_park.py NAME LAT LON CACHE_DIR OUT_DIR FIG_DIR [--size 10] [--rel ID | --way ID]

The window is SIZE x SIZE km centred at (LAT, LON), about what one fixed-wing sortie covers. Steps:
  1 the protected-area boundary (OSM relation or closed way, optional), clipped to the window; the area of interest (AOI) is
    window AND boundary, or the whole window without a boundary;
  2 every OSM element in the window from the API map call, in 0.03-degree tiles split in four on HTTP 400 (cached);
  3 trails (highway=path|footway|track|bridleway|steps|via_ferrata), roads (other highway values), streams
    (waterway=river|stream|canal|ditch|drain|brook), water areas, forest (landuse=forest, natural=wood), buildings, peaks
    and huts or shelters;
  4 terrain from the public Terrarium tiles (zoom 13, about 19 m pixels at the equator), resampled on a 25 m grid: elevation,
    slope, hillshade;
  5 the R = 100 m hexagonal cells (flat-top) over the AOI: share within 100 m of a trail or road (corridor cells), share with
    centre in OSM forest, in water, with slope above 30 degrees, and the local relief (max - min elevation within 100 m).
Writes OUT_DIR/{summary.md, stats.json, trails.geojson, streams.geojson} (local metres around the centre), FIG_DIR/park-NAME.png
(no text) and FIG_DIR/park-NAME-labelled.png (legend, scale bar). Data (c) OpenStreetMap contributors, ODbL; elevation:
Terrarium tiles (SRTM and other sources), AWS open data.
"""
import argparse, io, json, math, os, time, urllib.error, urllib.request, xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
from shapely.geometry import Polygon, LineString, Point, box, mapping
from shapely.ops import unary_union, linemerge, polygonize
from shapely import prepared

ap = argparse.ArgumentParser()
ap.add_argument("name"); ap.add_argument("lat", type=float); ap.add_argument("lon", type=float)
ap.add_argument("cache"); ap.add_argument("out"); ap.add_argument("figs")
ap.add_argument("--size", type=float, default=10.0); ap.add_argument("--tile", type=float, default=0.03)
ap.add_argument("--rel"); ap.add_argument("--way")
A = ap.parse_args()
UA = {"User-Agent": "research-map-probe/0.1"}
for d in (A.cache, A.out, A.figs): os.makedirs(d, exist_ok=True)
KX, KY = 111320 * math.cos(math.radians(A.lat)), 111320.0
to_xy = lambda lat, lon: ((lon - A.lon) * KX, (lat - A.lat) * KY)
half = A.size * 500
w, e = A.lon - half / KX, A.lon + half / KX
s, n = A.lat - half / KY, A.lat + half / KY
WIN = box(-half, -half, half, half)


def get(url, path):
    """Download url to path once; None on HTTP 400/509 (map call over the node limit: split the tile)."""
    if not os.path.exists(path):
        for _ in range(3):
            try:
                open(path, "wb").write(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180).read()); break
            except urllib.error.HTTPError as ex:
                if ex.code in (400, 509):
                    time.sleep(1); return None
                print("  retry", url, ex); time.sleep(5)
            except Exception as ex:
                print("  retry", url, ex); time.sleep(5)
        time.sleep(1)
    return path if os.path.exists(path) else None


def parse(path, nodes, ntags, ways, rels):
    root = ET.parse(path).getroot()
    for nd in root.iter("node"):
        nodes[nd.get("id")] = (float(nd.get("lat")), float(nd.get("lon")))
        t = {x.get("k"): x.get("v") for x in nd.iter("tag")}
        if t: ntags[nd.get("id")] = t
    for wy in root.iter("way"):
        ways[wy.get("id")] = ([r.get("ref") for r in wy.iter("nd")], {t.get("k"): t.get("v") for t in wy.iter("tag")})
    for rl in root.iter("relation"):
        rels[rl.get("id")] = ([(m.get("ref"), m.get("role")) for m in rl.iter("member") if m.get("type") == "way"],
                              {t.get("k"): t.get("v") for t in rl.iter("tag")})


def rings(mem, ways, nodes, roles=("outer", "")):
    lines = [LineString([to_xy(*nodes[x]) for x in ways[r][0] if x in nodes]) for r, role in mem
             if role in roles and r in ways and len(ways[r][0]) > 1]
    lines = [l for l in lines if len(l.coords) > 1]
    return list(polygonize(linemerge(lines))) if lines else []


# 1 boundary
aoi, bname = WIN, None
if A.rel or A.way:
    bn, bnt, bw, br = {}, {}, {}, {}
    kind, oid = ("relation", A.rel) if A.rel else ("way", A.way)
    f = get(f"https://www.openstreetmap.org/api/0.6/{kind}/{oid}/full", f"{A.cache}/{kind}-{oid}.osm")
    if f:
        parse(f, bn, bnt, bw, br)
        if A.rel:
            mem, t = br[A.rel]; bname = t.get("name")
            outer = unary_union(rings(mem, bw, bn))
            inner = unary_union(rings(mem, bw, bn, roles=("inner",)))
            poly = outer.difference(inner) if not inner.is_empty else outer
        else:
            refs, t = bw[A.way]; bname = t.get("name")
            poly = Polygon([to_xy(*bn[x]) for x in refs if x in bn])
        aoi = poly.buffer(0).intersection(WIN)
print(f"{A.name}: AOI {aoi.area / 1e6:.1f} km² of the {A.size:.0f} x {A.size:.0f} km window ({bname})")

# 2 tiles
nodes, ntags, ways, rels = {}, {}, {}, {}
def fetch_box(x0, y0, x1, y1, tag):
    f = get(f"https://www.openstreetmap.org/api/0.6/map?bbox={x0:.6f},{y0:.6f},{x1:.6f},{y1:.6f}", f"{A.cache}/{tag}.osm")
    if f:
        parse(f, nodes, ntags, ways, rels); return 1
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
    return sum(fetch_box(*b, f"{tag}{k}") for k, b in enumerate(((x0, y0, xm, ym), (xm, y0, x1, ym), (x0, ym, xm, y1), (xm, ym, x1, y1))))
i, y = 0, s
while y < n - 1e-9:
    x = w
    while x < e - 1e-9:
        fetch_box(x, y, min(x + A.tile, e), min(y + A.tile, n), f"t{i}_"); i += 1; x += A.tile
    y += A.tile
print(f"{i} tiles, {len(nodes)} nodes, {len(ways)} ways, {len(rels)} relations")

# 3 features
TRAIL = {"path", "footway", "track", "bridleway", "steps", "via_ferrata"}
NOROAD = {"proposed", "construction", "abandoned", "platform", "raceway", "elevator", "corridor"}
STREAM = {"river", "stream", "canal", "ditch", "drain", "brook"}
is_forest = lambda t: t.get("landuse") == "forest" or t.get("natural") == "wood"
is_water = lambda t: t.get("natural") == "water" or t.get("waterway") == "riverbank" or t.get("landuse") in ("reservoir", "basin")
trails, roads, streams, waterp, forest, nbld = [], [], [], [], [], 0
for wid, (refs, t) in ways.items():
    pts = [to_xy(*nodes[x]) for x in refs if x in nodes]
    if len(pts) < 2: continue
    closed = refs[0] == refs[-1] and len(pts) >= 4
    hw = t.get("highway")
    if hw in TRAIL: trails.append(LineString(pts))
    elif hw and hw not in NOROAD: roads.append(LineString(pts))
    if t.get("waterway") in STREAM: streams.append(LineString(pts))
    if closed and is_water(t): waterp.append(Polygon(pts).buffer(0))
    if closed and is_forest(t): forest.append(Polygon(pts).buffer(0))
    if "building" in t: nbld += 1
for rid, (mem, t) in rels.items():
    if t.get("type") != "multipolygon" or not (is_forest(t) or is_water(t)): continue
    ps = rings(mem, ways, nodes)
    if not ps: continue
    g = unary_union(ps)
    inner = rings(mem, ways, nodes, roles=("inner",))
    if inner: g = g.difference(unary_union(inner))
    (forest if is_forest(t) else waterp).append(g.buffer(0))
    if "building" in t: nbld += 1
clip = lambda gs: [g.intersection(aoi) for g in gs if g.intersects(aoi)]
trails, roads, streams = clip(trails), clip(roads), clip(streams)
forest_u = unary_union(clip(forest)) if forest else Polygon()
water_u = unary_union(clip(waterp)) if waterp else Polygon()
peaks = [to_xy(*nodes[k]) for k, t in ntags.items() if t.get("natural") == "peak" and aoi.contains(Point(to_xy(*nodes[k])))]
huts = [to_xy(*nodes[k]) for k, t in ntags.items() if (t.get("tourism") in ("alpine_hut", "wilderness_hut") or
        t.get("amenity") == "shelter") and aoi.contains(Point(to_xy(*nodes[k])))]
L = lambda gs: sum(g.length for g in gs) / 1000

# 4 terrain (Terrarium, zoom 13)
Z = 13
def tile_xy(lat, lon):
    k = 2 ** Z
    return (lon + 180) / 360 * k, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * k
tx0, ty0 = tile_xy(n, w); tx1, ty1 = tile_xy(s, e)
TX = range(int(tx0), int(tx1) + 1); TY = range(int(ty0), int(ty1) + 1)
mos = np.zeros((256 * len(TY), 256 * len(TX)))
for j, ty in enumerate(TY):
    for i2, tx in enumerate(TX):
        f = get(f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{Z}/{tx}/{ty}.png", f"{A.cache}/dem-{Z}-{tx}-{ty}.png")
        im = np.asarray(Image.open(f).convert("RGB"), dtype=float)
        mos[256 * j:256 * j + 256, 256 * i2:256 * i2 + 256] = im[..., 0] * 256 + im[..., 1] + im[..., 2] / 256 - 32768
G = 25.0
gx = np.arange(-half, half + G, G); gy = np.arange(-half, half + G, G)
XX, YY = np.meshgrid(gx, gy)
lon_g, lat_g = A.lon + XX / KX, A.lat + YY / KY
px = (np.array([tile_xy(la, lo) for la, lo in zip(lat_g.ravel(), lon_g.ravel())]) - [TX[0], TY[0]]) * 256
c, r = np.clip(px[:, 0], 0, mos.shape[1] - 1.001), np.clip(px[:, 1], 0, mos.shape[0] - 1.001)
c0, r0 = c.astype(int), r.astype(int); fc, fr = c - c0, r - r0
elev = ((mos[r0, c0] * (1 - fc) + mos[r0, c0 + 1] * fc) * (1 - fr) + (mos[r0 + 1, c0] * (1 - fc) + mos[r0 + 1, c0 + 1] * fc) * fr).reshape(XX.shape)
dzdy, dzdx = np.gradient(elev, G)
slope = np.degrees(np.arctan(np.hypot(dzdx, dzdy)))
inside = np.array([aoi.contains(Point(p)) for p in zip(XX.ravel(), YY.ravel())]).reshape(XX.shape)
ev, sv = elev[inside], slope[inside]
az, alt = math.radians(315), math.radians(45)
asp = np.arctan2(-dzdx, dzdy)
shade = np.clip(np.sin(alt) * np.cos(np.radians(slope)) + np.cos(alt) * np.sin(np.radians(slope)) * np.cos(az - asp), 0, 1)

# 5 cells
R = 100.0
corr = prepared.prep(unary_union(trails + roads).buffer(R)) if (trails or roads) else None
pf, pw = prepared.prep(forest_u), prepared.prep(water_u)
cells = []
dx, dy = 1.5 * R, math.sqrt(3) * R
for ci in range(int(-half / dx) - 1, int(half / dx) + 2):
    for cj in range(int(-half / dy) - 1, int(half / dy) + 2):
        x0, y0 = ci * dx, cj * dy + (dy / 2 if ci % 2 else 0)
        p = Point(x0, y0)
        if not aoi.contains(p): continue
        ii, jj = int(round((y0 + half) / G)), int(round((x0 + half) / G))
        k = int(R / G)
        sub = elev[max(ii - k, 0):ii + k + 1, max(jj - k, 0):jj + k + 1]
        cells.append((corr.contains(p) if corr else False, pf.contains(p), pw.contains(p), slope[ii, jj] > 30, float(sub.max() - sub.min())))
C = np.array(cells, dtype=float)
st = {
    "name": A.name, "boundary": bname, "lat": A.lat, "lon": A.lon, "window_km": A.size, "aoi_km2": round(aoi.area / 1e6, 1),
    "trail_km": round(L(trails), 1), "road_km": round(L(roads), 1), "stream_km": round(L(streams), 1),
    "trail_km_per_km2": round(L(trails) / (aoi.area / 1e6), 2), "forest_share_osm": round(forest_u.area / aoi.area, 3),
    "water_share": round(water_u.area / aoi.area, 3), "buildings": nbld, "peaks": len(peaks), "huts_shelters": len(huts),
    "elev_min": round(float(ev.min())), "elev_median": round(float(np.median(ev))), "elev_max": round(float(ev.max())),
    "slope_median_deg": round(float(np.median(sv)), 1), "slope_gt20_share": round(float((sv > 20).mean()), 3),
    "slope_gt30_share": round(float((sv > 30).mean()), 3), "cells": len(C),
    "cells_corridor_share": round(float(C[:, 0].mean()), 3), "cells_forest_share": round(float(C[:, 1].mean()), 3),
    "cells_water_share": round(float(C[:, 2].mean()), 3), "cells_steep_share": round(float(C[:, 3].mean()), 3),
    "cell_relief_median_m": round(float(np.median(C[:, 4]))), "cell_relief_p90_m": round(float(np.percentile(C[:, 4], 90))),
}
json.dump(st, open(f"{A.out}/stats.json", "w"), indent=1, ensure_ascii=False)
gj = lambda gs, p: json.dump({"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": mapping(g), "properties": {}} for g in gs if not g.is_empty]}, open(p, "w"))
gj(trails, f"{A.out}/trails.geojson"); gj(streams, f"{A.out}/streams.geojson")
open(f"{A.out}/summary.md", "w").write(f"""---
status: current
updated: {time.strftime('%Y-%m-%d')}
---
# {A.name}: cửa sổ {A.size:.0f} × {A.size:.0f} km

Tâm {A.lat:.4f}, {A.lon:.4f}; ranh giới OSM: {bname or 'không dùng'}. Vùng xét (cửa sổ giao ranh giới) {st['aoi_km2']} km².
Dữ liệu (c) OpenStreetMap contributors, ODbL; độ cao từ Terrarium tiles z13. Sinh bằng `paper/j1/analysis/osm_park.py`.

- Đường mòn {st['trail_km']} km ({st['trail_km_per_km2']} km/km²), đường xe {st['road_km']} km, suối và sông {st['stream_km']} km.
- Rừng theo OSM {100 * st['forest_share_osm']:.0f} % diện tích (OSM có thể thiếu), mặt nước {100 * st['water_share']:.1f} %.
- {st['buildings']} toà nhà, {st['peaks']} đỉnh, {st['huts_shelters']} lán hoặc chỗ trú.
- Độ cao {st['elev_min']}–{st['elev_max']} m (trung vị {st['elev_median']} m); độ dốc trung vị {st['slope_median_deg']}°,
  {100 * st['slope_gt20_share']:.0f} % diện tích dốc trên 20°, {100 * st['slope_gt30_share']:.0f} % dốc trên 30°.
- {st['cells']} cell R = 100 m: {100 * st['cells_corridor_share']:.0f} % cách đường mòn hoặc đường xe không quá 100 m,
  {100 * st['cells_forest_share']:.0f} % có tâm trong rừng OSM, {100 * st['cells_water_share']:.1f} % trên nước,
  {100 * st['cells_steep_share']:.0f} % dốc trên 30°; chênh cao trong bán kính 100 m quanh tâm cell trung vị
  {st['cell_relief_median_m']} m, phân vị 90 là {st['cell_relief_p90_m']} m.
""")

# figures
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
def draw(labelled):
    fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
    ax.imshow(shade, extent=(-half - G / 2, half + G / 2, -half - G / 2, half + G / 2), origin="lower", cmap="gray", vmin=0, vmax=1.3)
    def fill(g, **kw):
        for p in getattr(g, "geoms", [g]):
            if p.geom_type == "Polygon" and not p.is_empty:
                ax.fill(*p.exterior.xy, lw=0, **kw)
    fill(forest_u, color="#2e7d32", alpha=0.28); fill(water_u, color="#1e88e5", alpha=0.9)
    for g in streams:
        for l in getattr(g, "geoms", [g]):
            if l.geom_type == "LineString": ax.plot(*l.xy, color="#1e88e5", lw=0.6)
    for gs, col, lw in ((roads, "#212121", 1.0), (trails, "#d84315", 0.8)):
        for g in gs:
            for l in getattr(g, "geoms", [g]):
                if l.geom_type == "LineString": ax.plot(*l.xy, color=col, lw=lw)
    if aoi is not WIN:
        for p in getattr(aoi, "geoms", [aoi]):
            if p.geom_type == "Polygon": ax.plot(*p.exterior.xy, color="#6a1b9a", lw=1.2)
    if huts: ax.plot(*zip(*huts), "^", color="#ffb300", ms=5, mec="k", mew=0.4)
    ax.set_xlim(-half, half); ax.set_ylim(-half, half); ax.set_aspect("equal"); ax.axis("off")
    if labelled:
        ax.legend(handles=[Patch(color="#2e7d32", alpha=0.4, label="rừng (OSM)"), Patch(color="#1e88e5", label="mặt nước"),
                           Line2D([], [], color="#1e88e5", lw=1, label="suối, sông"), Line2D([], [], color="#d84315", lw=1.5, label="đường mòn"),
                           Line2D([], [], color="#212121", lw=1.5, label="đường xe"), Line2D([], [], color="#6a1b9a", lw=1.5, label="ranh giới khu bảo vệ"),
                           Line2D([], [], marker="^", ls="", color="#ffb300", mec="k", label="lán, chỗ trú")],
                  loc="upper right", fontsize=7, framealpha=0.85)
        ax.plot([-half + 300, -half + 1300], [-half + 300] * 2, color="k", lw=3)
        ax.text(-half + 800, -half + 420, "1 km", ha="center", fontsize=8)
    fig.savefig(f"{A.figs}/park-{A.name}{'-labelled' if labelled else ''}.png", bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
draw(False); draw(True)
print(json.dumps(st, ensure_ascii=False))
