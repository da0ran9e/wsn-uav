"""Candidate urban sample maps from OpenStreetMap: buildings, heights, water, open land and empty cells
(J1 context, chatlog items 350-351).

    python3 paper/j1/analysis/osm_areas.py CACHE_DIR FIG_DIR [--half-km 2.0] [--tile 0.012] [--only NAME,...]

For each candidate area, a square of +/- HALF km around its centre (default 4 x 4 km, the size of map k8) is fetched in
tiles through the OSM API 0.6 map call (www.openstreetmap.org; Overpass and Geofabrik are not reachable from this
container) and cached as raw XML in CACHE_DIR (not committed). Polygons, clipped to the square:
  building  any closed way or multipolygon with building=*; height from height=* or 3 m x building:levels
  water     natural=water, waterway=riverbank, landuse=reservoir|basin, water=*
  open      parks, pitches, golf, grass, meadow, farmland, construction, brownfield, greenfield, forest, wood, scrub,
            wetland, cemetery (land where few devices stand)
  roads     highway=* lines buffered by 5 m
Prints, per area, the shares of the square that are building footprint, water, open land, road and none of these
(untagged), the share of buildings with a height, the buildings taller than 100 m and 120 m, and the R = 100 m hexagonal
cells (flat-top, the simulator's cell size) that are mostly water (> 50 %) or empty (no building and < 50 m of road:
nowhere to mount a device). Writes FIG_DIR/osm-<area>.png without text (buildings dark, water blue, open green, roads
light). Data (c) OpenStreetMap contributors, ODbL.
"""
import argparse, math, os, time, urllib.request, xml.etree.ElementTree as ET
from shapely.geometry import Polygon, LineString, box, Point
from shapely.ops import unary_union, linemerge, polygonize
from shapely import prepared

AREAS = {   # name: (lat, lon)
    "hanoi-oceanpark": (20.9930, 105.9420),
    "hanoi-ecopark": (20.9530, 105.9480),
    "hanoi-mydinh": (21.0200, 105.7800),
    "hanoi-linhdam": (20.9650, 105.8300),
    "hanoi-starlake": (21.0600, 105.8000),
    "hcmc-thuthiem": (10.7780, 106.7200),
    "hcmc-phumyhung": (10.7280, 106.7050),
    "singapore-marina": (1.2830, 103.8550),
    "singapore-punggol": (1.4050, 103.9050),
}
ap = argparse.ArgumentParser()
ap.add_argument("cache"); ap.add_argument("figs")
ap.add_argument("--half-km", type=float, default=2.0); ap.add_argument("--tile", type=float, default=0.012)
ap.add_argument("--only", default="")
A = ap.parse_args()
OPEN_LEISURE = {"park", "garden", "pitch", "golf_course", "playground", "recreation_ground", "nature_reserve", "common"}
OPEN_LANDUSE = {"grass", "meadow", "farmland", "construction", "brownfield", "greenfield", "recreation_ground", "forest",
                "orchard", "cemetery", "village_green", "plant_nursery", "allotments"}
OPEN_NATURAL = {"wood", "scrub", "grassland", "wetland", "sand", "heath", "bare_rock"}


def fetch(name, lat, lon):
    dlat = A.half_km / 111.32; dlon = A.half_km / (111.32 * math.cos(math.radians(lat)))
    s, w, n, e = lat - dlat, lon - dlon, lat + dlat, lon + dlon
    os.makedirs(f"{A.cache}/{name}", exist_ok=True)
    nodes, ways, rels = {}, {}, {}
    i = 0
    y = s
    while y < n - 1e-9:
        x = w
        while x < e - 1e-9:
            f = f"{A.cache}/{name}/t{i}.osm"
            if not os.path.exists(f):
                url = f"https://www.openstreetmap.org/api/0.6/map?bbox={x:.6f},{y:.6f},{min(x + A.tile, e):.6f},{min(y + A.tile, n):.6f}"
                req = urllib.request.Request(url, headers={"User-Agent": "research-map-probe/0.1"})
                for k in range(3):
                    try:
                        open(f, "wb").write(urllib.request.urlopen(req, timeout=120).read()); break
                    except Exception as ex:
                        print(f"  {name} tile {i}: {ex}"); time.sleep(5)
                time.sleep(1)
            if os.path.exists(f):
                root = ET.parse(f).getroot()
                for nd in root.iter("node"): nodes[nd.get("id")] = (float(nd.get("lat")), float(nd.get("lon")))
                for wy in root.iter("way"):
                    ways[wy.get("id")] = ([r.get("ref") for r in wy.iter("nd")], {t.get("k"): t.get("v") for t in wy.iter("tag")})
                for rl in root.iter("relation"):
                    rels[rl.get("id")] = ([(m.get("ref"), m.get("role")) for m in rl.iter("member") if m.get("type") == "way"],
                                          {t.get("k"): t.get("v") for t in rl.iter("tag")})
            i += 1; x += A.tile
        y += A.tile
    return nodes, ways, rels, (lat, lon)


def kind(tags):
    if "building" in tags or "building:part" in tags: return "building"
    if tags.get("natural") == "water" or tags.get("waterway") == "riverbank" or tags.get("landuse") in ("reservoir", "basin") or "water" in tags:
        return "water"
    if tags.get("leisure") in OPEN_LEISURE or tags.get("landuse") in OPEN_LANDUSE or tags.get("natural") in OPEN_NATURAL:
        return "open"
    return None


def height(tags):
    try:
        if "height" in tags: return float(tags["height"].split()[0].replace(",", "."))
        if "building:levels" in tags: return 3.0 * float(tags["building:levels"])
    except ValueError:
        return None
    return None


def analyse(name, nodes, ways, rels, centre):
    lat0, lon0 = centre
    kx = 111320 * math.cos(math.radians(lat0)); ky = 111320
    xy = lambda nid: ((nodes[nid][1] - lon0) * kx, (nodes[nid][0] - lat0) * ky)
    H = A.half_km * 1000; square = box(-H, -H, H, H)
    polys = {"building": [], "water": [], "open": []}; heights = []; roads = []
    used_in_rel = set()
    for rid, (mem, tags) in rels.items():
        if tags.get("type") != "multipolygon": continue
        k = kind(tags)
        if not k: continue
        lines = []
        for ref, role in mem:
            if ref in ways and role in ("outer", "") and all(n in nodes for n in ways[ref][0]) and len(ways[ref][0]) > 1:
                lines.append(LineString([xy(n) for n in ways[ref][0]])); used_in_rel.add(ref)
        for p in polygonize(linemerge(lines) if lines else []):
            if p.is_valid and p.area > 1: polys[k].append(p)
        if k == "building": heights.append(height(tags))
    for wid, (nds, tags) in ways.items():
        if not all(n in nodes for n in nds) or len(nds) < 2: continue
        if "highway" in tags and nds[0] != nds[-1]:
            roads.append(LineString([xy(n) for n in nds])); continue
        k = kind(tags)
        if k and nds[0] == nds[-1] and len(nds) >= 4 and wid not in used_in_rel:
            p = Polygon([xy(n) for n in nds])
            if not p.is_valid: p = p.buffer(0)
            if p.area > 1:
                polys[k].append(p)
                if k == "building": heights.append(height(tags))
    U = {k: unary_union(v).intersection(square) if v else Polygon() for k, v in polys.items()}
    R = unary_union([r.buffer(5) for r in roads]).intersection(square) if roads else Polygon()
    water = U["water"]; bld = U["building"].difference(water); opn = U["open"].difference(water).difference(bld)
    rd = R.difference(water).difference(bld)
    tot = square.area
    other = tot - water.area - bld.area - opn.area - rd.difference(opn).area
    hs = [h for h in heights if h is not None]
    # hexagonal cells, flat-top, circumradius 100 m
    Rc = 100.0; cells = water_cells = empty_cells = 0
    pw = prepared.prep(water) if not water.is_empty else None
    pb = prepared.prep(U["building"]) if not U["building"].is_empty else None
    road_lines = unary_union(roads).intersection(square) if roads else LineString()
    q = -int(H / (1.5 * Rc)) - 1
    while 1.5 * Rc * q <= H:
        cx = 1.5 * Rc * q
        r = -int(H / (math.sqrt(3) * Rc)) - 2
        while True:
            cy = math.sqrt(3) * Rc * (r + q / 2)
            if cy > H + Rc: break
            if abs(cx) <= H - Rc and abs(cy) <= H - Rc:
                hexp = Polygon([(cx + Rc * math.cos(math.pi / 3 * k), cy + Rc * math.sin(math.pi / 3 * k)) for k in range(6)])
                cells += 1
                if pw and pw.intersects(hexp) and water.intersection(hexp).area > 0.5 * hexp.area: water_cells += 1
                elif not (pb and pb.intersects(hexp)) and road_lines.intersection(hexp).length < 50: empty_cells += 1
            r += 1
        q += 1
    row = (f"| {name} | {bld.area / tot * 100:.0f} % | {water.area / tot * 100:.0f} % | {opn.area / tot * 100:.0f} % | "
           f"{rd.difference(opn).area / tot * 100:.0f} % | {max(other, 0) / tot * 100:.0f} % | {len(heights)} | "
           f"{len(hs) / max(len(heights), 1) * 100:.0f} % | {sum(h > 100 for h in hs)} / {sum(h > 120 for h in hs)} | "
           f"{max(hs) if hs else 0:.0f} m | {water_cells / cells * 100:.0f} % | {empty_cells / cells * 100:.0f} % |")
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path as MPath
    fig = plt.figure(figsize=(5, 5)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(-H, H); ax.set_ylim(-H, H); ax.axis("off")
    fig.patch.set_facecolor("#f4f1ea")
    def draw(g, c):
        for p in getattr(g, "geoms", [g]):
            if p.is_empty or p.geom_type != "Polygon": continue
            verts = list(p.exterior.coords); codes = [MPath.MOVETO] + [MPath.LINETO] * (len(verts) - 2) + [MPath.CLOSEPOLY]
            for hole in p.interiors:
                hv = list(hole.coords); verts += hv; codes += [MPath.MOVETO] + [MPath.LINETO] * (len(hv) - 2) + [MPath.CLOSEPOLY]
            ax.add_patch(PathPatch(MPath(verts, codes), facecolor=c, edgecolor="none"))
    draw(opn, "#b9d9a5"); draw(water, "#7fb3e0"); draw(rd, "#ffffff"); draw(bld, "#555555")
    os.makedirs(A.figs, exist_ok=True); fig.savefig(f"{A.figs}/osm-{name}.png", dpi=110); plt.close(fig)
    return row


print("| Khu | Nhà (diện tích) | Nước | Đất trống có thẻ | Đường | Chưa gắn thẻ | Số nhà | Có chiều cao | > 100 m / > 120 m | Cao nhất | Cell nước | Cell không chỗ đặt node |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|")
for name, (lat, lon) in AREAS.items():
    if A.only and name not in A.only.split(","): continue
    print(analyse(name, *fetch(name, lat, lon)), flush=True)
