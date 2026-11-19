"""Cut one district out of OpenStreetMap and mark its lakes and high areas (J1 context, chatlog item 352).

    python3 paper/j1/analysis/osm_district.py REL_ID NAME CACHE_DIR OUT_DIR FIG_DIR [--tall 60] [--zone 100]

REL_ID is the OSM relation of the district boundary (Hanoi's former districts are kept as boundary=historic relations
since the 2025 reform, e.g. 9421133 Quận Hoàng Mai, 9421132 Quận Cầu Giấy). Steps:
  1 the boundary polygon from the API call relation/REL_ID/full;
  2 every OSM element in its bounding box, fetched in 0.012-degree tiles of the map call (cached in CACHE_DIR);
  3 buildings (footprint, height from height=* or 3 m x building:levels, else unknown), water (natural=water,
    waterway=riverbank, landuse=reservoir|basin, water=*) and roads, clipped to the district;
  4 high-rise zones: buildings at least TALL m tall, each grown by ZONE m and merged (where the A2G channel is blocked);
  5 terrain: ground elevation from the public Terrarium tiles (Mapzen/AWS open data, zoom 13, about 19 m pixels), min,
    median, max inside the district and the share above median + 5 m (statistics only, not drawn: on flat cities the
    30 m SRTM-based tiles are dominated by noise, buildings and trees, and even mark points on lakes);
  6 no-fly proxies from OSM (the official no-fly map of the Ministry of Defence, cambay.mod.gov.vn, is managed as a state
    secret and not downloadable): aerodromes (aeroway=aerodrome) and military land (landuse=military) inside the box, and
    physical obstacles: buildings at least FLY m tall (the flight altitude) grown by CLEAR m;
  7 the R = 100 m hexagonal cells (flat-top) over the district: shares mostly water, in a high-rise zone, in a no-fly
    proxy or obstacle.
Writes OUT_DIR/{boundary.geojson, water.geojson, highrise.geojson, buildings.csv.gz, summary.md} (local metres around the
district centre, plus the centre in WGS84), FIG_DIR/map-NAME.png (no text) and FIG_DIR/map-NAME-labelled.png (legend,
lake names, scale bar). Data (c) OpenStreetMap contributors, ODbL; elevation: Terrarium tiles (SRTM and others).
"""
import argparse, csv, gzip, io, json, math, os, time, urllib.error, urllib.request, xml.etree.ElementTree as ET
import numpy as np
from shapely.geometry import Polygon, LineString, Point, box, mapping
from shapely.ops import unary_union, linemerge, polygonize
from shapely import prepared

ap = argparse.ArgumentParser()
ap.add_argument("rel"); ap.add_argument("name"); ap.add_argument("cache"); ap.add_argument("out"); ap.add_argument("figs")
ap.add_argument("--tall", type=float, default=60.0); ap.add_argument("--zone", type=float, default=100.0)
ap.add_argument("--tile", type=float, default=0.012)
ap.add_argument("--fly", type=float, default=100.0); ap.add_argument("--clear", type=float, default=50.0)
A = ap.parse_args()
UA = {"User-Agent": "research-map-probe/0.1"}
os.makedirs(A.cache, exist_ok=True); os.makedirs(A.out, exist_ok=True); os.makedirs(A.figs, exist_ok=True)


def get(url, path):
    """Download url to path once; None when it fails (HTTP 400 from the map call = too many nodes: split the tile)."""
    if not os.path.exists(path):
        for k in range(3):
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


def parse(path, nodes, ways, rels):
    root = ET.parse(path).getroot()
    for nd in root.iter("node"): nodes[nd.get("id")] = (float(nd.get("lat")), float(nd.get("lon")))
    for wy in root.iter("way"):
        ways[wy.get("id")] = ([r.get("ref") for r in wy.iter("nd")], {t.get("k"): t.get("v") for t in wy.iter("tag")})
    for rl in root.iter("relation"):
        rels[rl.get("id")] = ([(m.get("ref"), m.get("role")) for m in rl.iter("member") if m.get("type") == "way"],
                              {t.get("k"): t.get("v") for t in rl.iter("tag")})


# 1 boundary
nodes, ways, rels = {}, {}, {}
parse(get(f"https://www.openstreetmap.org/api/0.6/relation/{A.rel}/full", f"{A.cache}/rel-{A.rel}.osm"), nodes, ways, rels)
mem, rtags = rels[A.rel]
outer = [[(nodes[n][1], nodes[n][0]) for n in ways[r][0]] for r, role in mem if role in ("outer", "") and r in ways]
bound_ll = max(polygonize(linemerge([LineString(c) for c in outer])), key=lambda p: p.area)
lon0, lat0 = bound_ll.centroid.x, bound_ll.centroid.y
KX, KY = 111320 * math.cos(math.radians(lat0)), 111320.0
to_xy = lambda lat, lon: ((lon - lon0) * KX, (lat - lat0) * KY)
bound = Polygon([to_xy(la, lo) for lo, la in bound_ll.exterior.coords])
w, s, e, n = bound_ll.bounds
print(f"{rtags.get('name')}: {bound.area / 1e6:.1f} km², bbox {e - w:.3f} x {n - s:.3f} deg")

# 2 tiles
nodes, ways, rels = {}, {}, {}
def fetch_box(x0, y0, x1, y1, tag):
    f = get(f"https://www.openstreetmap.org/api/0.6/map?bbox={x0:.6f},{y0:.6f},{x1:.6f},{y1:.6f}", f"{A.cache}/{tag}.osm")
    if f:
        parse(f, nodes, ways, rels); return 1
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2   # too many nodes: four quarters
    return sum(fetch_box(*b, f"{tag}{k}") for k, b in enumerate(((x0, y0, xm, ym), (xm, y0, x1, ym), (x0, ym, xm, y1), (xm, ym, x1, y1))))
i = 0; y = s
while y < n:
    x = w
    while x < e:
        fetch_box(x, y, min(x + A.tile, e), min(y + A.tile, n), f"t{i}_")
        i += 1; x += A.tile
    y += A.tile
print(f"{i} tiles, {len(nodes)} nodes, {len(ways)} ways")
xy = lambda nid: to_xy(*nodes[nid])


def height(tags):
    try:
        if "height" in tags: return float(tags["height"].split()[0].replace(",", ".")), "height"
        if "building:levels" in tags: return 3.0 * float(tags["building:levels"]), "levels"
    except ValueError:
        pass
    return None, "unknown"


def is_nofly(t):
    return t.get("aeroway") == "aerodrome" or t.get("landuse") == "military" or t.get("military") in ("base", "barracks", "airfield")


def is_water(t):
    return t.get("natural") == "water" or t.get("waterway") == "riverbank" or t.get("landuse") in ("reservoir", "basin") or "water" in t


# 3 features
bld, water, roads, used, nofly, coast = [], [], [], set(), [], []
for rid, (mem, t) in rels.items():
    if t.get("type") != "multipolygon" or not ("building" in t or is_water(t) or is_nofly(t)): continue
    lines = []
    for ref, role in mem:
        if ref in ways and role in ("outer", "") and len(ways[ref][0]) > 1 and all(q in nodes for q in ways[ref][0]):
            lines.append(LineString([xy(q) for q in ways[ref][0]])); used.add(ref)
    for p in (polygonize(linemerge(lines)) if lines else []):
        if p.area > 1:
            if "building" in t: bld.append((p, *height(t), t.get("name", "")))
            elif is_nofly(t): nofly.append((p, t.get("name", ""), t.get("aeroway") or "military"))
            else: water.append((p, t.get("name", "")))
for wid, (nds, t) in ways.items():
    if len(nds) < 2 or not all(q in nodes for q in nds): continue
    if "highway" in t and nds[0] != nds[-1]:
        roads.append(LineString([xy(q) for q in nds])); continue
    if t.get("natural") == "coastline":
        coast.append(LineString([xy(q) for q in nds])); continue
    if wid in used or nds[0] != nds[-1] or len(nds) < 4: continue
    if "building" in t or is_water(t) or is_nofly(t):
        p = Polygon([xy(q) for q in nds]); p = p if p.is_valid else p.buffer(0)
        if p.area <= 1: continue
        if "building" in t: bld.append((p, *height(t), t.get("name", "")))
        elif is_nofly(t): nofly.append((p, t.get("name", ""), t.get("aeroway") or "military"))
        else: water.append((p, t.get("name", "")))
pb = prepared.prep(bound)
# sea: OSM draws it only as coastline ways with land on the left; split the district by them and keep the pieces whose
# nearest coastline segment has them on its right
if coast:
    pieces = [bound]
    cl = unary_union(coast)
    try:   # node the district outline with the coastline and rebuild the faces
        faces = polygonize(unary_union([LineString(bound.exterior.coords), cl.intersection(bound.buffer(1))]))
        pieces = [f for f in faces if pb.contains(f.representative_point())] or [bound]
    except Exception as ex:
        print("coastline split failed:", ex)
    segs = []
    for c in coast:
        cs = list(c.coords); segs += list(zip(cs, cs[1:]))
    for pc in pieces:
        if pc.area < 1e3: continue
        rp = pc.representative_point()
        best = None
        for (ax_, ay_), (bx_, by_) in segs:
            dx, dy = bx_ - ax_, by_ - ay_; L2 = dx * dx + dy * dy
            if L2 == 0: continue
            u = max(0, min(1, ((rp.x - ax_) * dx + (rp.y - ay_) * dy) / L2))
            d = math.hypot(ax_ + u * dx - rp.x, ay_ + u * dy - rp.y)
            if best is None or d < best[0]: best = (d, dx * (rp.y - ay_) - dy * (rp.x - ax_))
        if best and best[1] < 0: water.append((pc, "(biển)"))
bld = [(p.intersection(bound), h, src, nm) for p, h, src, nm in bld if pb.intersects(p)]
bld = [b for b in bld if not b[0].is_empty]
W = unary_union([p for p, _ in water]).intersection(bound) if water else Polygon()
lakes = []
for p, nm in water:
    g = p.intersection(bound)
    if g.area >= 2e4: lakes.append((nm or "(không tên)", g.area / 1e4, g))
lakes.sort(key=lambda x: -x[1])
R = unary_union(roads).intersection(bound) if roads else LineString()

# 4 high-rise zones
hs = [b for b in bld if b[1] is not None]
tall = [b for b in hs if b[1] >= A.tall]
Z = unary_union([b[0].buffer(A.zone) for b in tall]).intersection(bound) if tall else Polygon()

NF = unary_union([p for p, _, _ in nofly]).intersection(bound) if nofly else Polygon()
obst = [b for b in hs if b[1] >= A.fly]
OB = unary_union([b[0].buffer(A.clear) for b in obst]).intersection(bound) if obst else Polygon()
NFall = unary_union([NF, OB])
nf_named = sorted({(nm or "(không tên)", kd) for p, nm, kd in nofly if p.intersects(bound)}, key=lambda x: (x[1] != "aerodrome", x[0] == "(không tên)", x[0]))

# 5 terrain (Terrarium tiles, zoom 13)
def tile_xy(lat, lon, z):
    nn = 2 ** z
    return (lon + 180) / 360 * nn, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * nn
elev = []
try:
    from PIL import Image
    z = 13
    x0, y1 = tile_xy(s, w, z); x1, y0 = tile_xy(n, e, z)
    for tx in range(int(x0), int(x1) + 1):
        for ty in range(int(y0), int(y1) + 1):
            f = get(f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{tx}/{ty}.png", f"{A.cache}/dem-{z}-{tx}-{ty}.png")
            im = np.asarray(Image.open(f).convert("RGB"), float)
            hgt = im[..., 0] * 256 + im[..., 1] + im[..., 2] / 256 - 32768
            for py in range(0, 256, 2):
                for px in range(0, 256, 2):
                    lon = (tx + px / 256) / 2 ** z * 360 - 180
                    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (ty + py / 256) / 2 ** z))))
                    if pb.contains(Point(*to_xy(lat, lon))): elev.append((to_xy(lat, lon), hgt[py, px]))
except Exception as ex:
    print("terrain skipped:", ex)
ev = np.array([v for _, v in elev]) if elev else np.array([np.nan])
emed = float(np.nanmedian(ev))

# 6 cells
Rc = 100.0; cells = wcell = zcell = ncell = 0
pn = prepared.prep(NFall) if not NFall.is_empty else None
pw = prepared.prep(W) if not W.is_empty else None; pz = prepared.prep(Z) if not Z.is_empty else None
bx0, by0, bx1, by1 = bound.bounds
q = int(bx0 / (1.5 * Rc)) - 1
while 1.5 * Rc * q <= bx1 + Rc:
    cx = 1.5 * Rc * q; r = int((by0 - 2 * Rc) / (math.sqrt(3) * Rc) - q / 2) - 1
    while math.sqrt(3) * Rc * (r + q / 2) <= by1 + Rc:
        cy = math.sqrt(3) * Rc * (r + q / 2)
        if pb.contains(Point(cx, cy)):
            hexp = Polygon([(cx + Rc * math.cos(math.pi / 3 * k), cy + Rc * math.sin(math.pi / 3 * k)) for k in range(6)])
            cells += 1
            if pw and pw.intersects(hexp) and W.intersection(hexp).area > 0.5 * hexp.area: wcell += 1
            if pz and pz.intersects(hexp) and Z.intersection(hexp).area > 0.5 * hexp.area: zcell += 1
            if pn and pn.intersects(hexp) and NFall.intersection(hexp).area > 0.5 * hexp.area: ncell += 1
        r += 1
    q += 1

# outputs
def geo(path, geoms):
    json.dump({"type": "FeatureCollection", "crs_note": f"local metres, origin lat {lat0:.6f} lon {lon0:.6f}",
               "features": [{"type": "Feature", "properties": pr, "geometry": mapping(g)} for g, pr in geoms]},
              open(path, "w"))
geo(f"{A.out}/boundary.geojson", [(bound, {"name": rtags.get("name"), "osm_relation": A.rel})])
geo(f"{A.out}/water.geojson", [(g, {"name": nm, "ha": round(ha, 2)}) for nm, ha, g in lakes])
geo(f"{A.out}/highrise.geojson", [(Z, {"tall_m": A.tall, "zone_m": A.zone})])
geo(f"{A.out}/nofly.geojson", [(NF, {"kind": "aerodrome or military land (OSM proxy)"}), (OB, {"kind": f"buildings >= {A.fly:.0f} m grown {A.clear:.0f} m"})])
with gzip.open(f"{A.out}/buildings.csv.gz", "wt") as f:
    wr = csv.writer(f); wr.writerow(["cx", "cy", "area_m2", "height_m", "height_src", "name", "wkt"])
    for p, h, src, nm in bld:
        c = p.centroid; wr.writerow([f"{c.x:.1f}", f"{c.y:.1f}", f"{p.area:.0f}", "" if h is None else f"{h:.1f}", src, nm,
                                     p.simplify(0.5).wkt])
summ = ["---", "status: reference", f"updated: {time.strftime('%Y-%m-%d')}", "---", f"# {rtags.get('name')} (OSM relation {A.rel})", "",
        f"- Diện tích {bound.area / 1e6:.1f} km²; tâm lat {lat0:.5f}, lon {lon0:.5f}.",
        f"- Toà nhà: {len(bld)}, có chiều cao {len(hs)} ({len(hs) / max(len(bld), 1) * 100:.0f} %); "
        f"≥ {A.tall:.0f} m: {len(tall)}; ≥ 100 m: {sum(b[1] >= 100 for b in hs)}; ≥ 120 m: {sum(b[1] >= 120 for b in hs)}; "
        f"cao nhất {max([b[1] for b in hs] or [0]):.0f} m.",
        f"- Nước: {W.area / bound.area * 100:.1f} % diện tích; hồ từ 2 ha: {len(lakes)}.",
        f"- Vùng cao tầng (nhà ≥ {A.tall:.0f} m nới {A.zone:.0f} m): {Z.area / bound.area * 100:.1f} % diện tích.",
        f"- Địa hình (Terrarium z13): thấp nhất {np.nanmin(ev):.0f} m, trung vị {emed:.0f} m, cao nhất {np.nanmax(ev):.0f} m; "
        f"{np.mean(ev > emed + 5) * 100:.1f} % điểm cao hơn trung vị 5 m.",
        f"- Cell R = 100 m: {cells}; chủ yếu nước {wcell} ({wcell / max(cells, 1) * 100:.0f} %); "
        f"chủ yếu trong vùng cao tầng {zcell} ({zcell / max(cells, 1) * 100:.0f} %); chủ yếu trong vùng cấm bay hoặc vật cản {ncell} "
        f"({ncell / max(cells, 1) * 100:.0f} %).",
        f"- Vùng cấm bay ước theo OSM (sân bay, đất quân sự): {NF.area / bound.area * 100:.1f} % diện tích; "
        + (", ".join(f"{nm} ({kd})" for nm, kd in nf_named[:8]) or "không có") + ".",
        f"- Vật cản (nhà ≥ {A.fly:.0f} m nới {A.clear:.0f} m): {len(obst)} toà, {OB.area / bound.area * 100:.1f} % diện tích.", "",
        "| Hồ | Diện tích (ha) |", "|---|---|"] + [f"| {nm} | {ha:.1f} |" for nm, ha, _ in lakes[:25]]
open(f"{A.out}/summary.md", "w").write("\n".join(summ) + "\n"); print("\n".join(summ))

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch, Patch
from matplotlib.path import Path as MPath


def patch(ax, g, **kw):
    for p in getattr(g, "geoms", [g]):
        if p.is_empty or p.geom_type != "Polygon": continue
        v = list(p.exterior.coords); c = [MPath.MOVETO] + [MPath.LINETO] * (len(v) - 2) + [MPath.CLOSEPOLY]
        for hole in p.interiors:
            hv = list(hole.coords); v += hv; c += [MPath.MOVETO] + [MPath.LINETO] * (len(hv) - 2) + [MPath.CLOSEPOLY]
        ax.add_patch(PathPatch(MPath(v, c), **kw))


def draw(labelled):
    W_, H_ = bx1 - bx0, by1 - by0
    fig = plt.figure(figsize=(8, 8 * H_ / W_)); ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(bx0 - 50, bx1 + 50); ax.set_ylim(by0 - 50, by1 + 50); ax.set_aspect("equal"); ax.axis("off")
    patch(ax, bound, facecolor="#f4f1ea", edgecolor="#333333", lw=1.2)
    for g in getattr(R, "geoms", [R]):
        if g.geom_type == "LineString": ax.plot(*g.xy, c="#ffffff", lw=0.6)
    patch(ax, Z, facecolor="#e8a0a0", edgecolor="#b03030", lw=0.8, alpha=0.45)
    patch(ax, W, facecolor="#7fb3e0", edgecolor="none")
    patch(ax, NF, facecolor="#8e5ad6", edgecolor="#5b2fa3", lw=0.8, alpha=0.35, hatch="///")
    patch(ax, OB, facecolor="#8e5ad6", edgecolor="#5b2fa3", lw=0.8, alpha=0.55)
    for p, h, src, nm in bld:
        col = "#9a9a9a" if h is None else ("#555555" if h < A.tall else ("#b03030" if h < 120 else "#5a0f0f"))
        patch(ax, p, facecolor=col, edgecolor="none")
    if labelled:
        for nm, ha, g in lakes[:12]:
            if nm != "(không tên)":
                c = g.representative_point(); ax.text(c.x, c.y, nm, fontsize=6, ha="center", color="#123a63")
        x0, y0 = bx0 + 100, by0 + 100
        ax.plot([x0, x0 + 1000], [y0, y0], c="k", lw=2); ax.text(x0 + 500, y0 + 60, "1 km", ha="center", fontsize=7)
        ax.legend(handles=[Patch(color="#7fb3e0", label="hồ, sông"), Patch(color="#e8a0a0", label=f"vùng cao tầng (nhà ≥ {A.tall:.0f} m, nới {A.zone:.0f} m)"),
                           Patch(color="#555555", label=f"nhà < {A.tall:.0f} m"), Patch(color="#b03030", label=f"nhà {A.tall:.0f}–120 m"),
                           Patch(color="#5a0f0f", label="nhà > 120 m"), Patch(color="#9a9a9a", label="nhà chưa rõ chiều cao"),
                           Patch(facecolor="#8e5ad6", alpha=0.35, hatch="///", label="cấm bay ước theo OSM (sân bay, quân sự)"),
                           Patch(facecolor="#8e5ad6", alpha=0.55, label=f"vật cản: nhà ≥ {A.fly:.0f} m nới {A.clear:.0f} m")]
,
                  loc="upper right", fontsize=7, frameon=True)
    fig.savefig(f"{A.figs}/map-{A.name}{'-labelled' if labelled else ''}.png", dpi=170); plt.close(fig)
draw(False); draw(True)
