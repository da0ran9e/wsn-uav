"""How usable is OpenStreetMap for an urban sample map: building footprints and heights in a small box per candidate area
(J1 context, chatlog item 350).

    python3 paper/j1/analysis/osm_probe.py [--half 0.003]

Fetches the OSM API 0.6 map call (www.openstreetmap.org; the Overpass and Geofabrik hosts are not reachable from this
container) for a box of +/- HALF degrees around each candidate centre, and counts building ways, the share with a height
or building:levels tag, the highest building, and road ways. Data (c) OpenStreetMap contributors, ODbL.
"""
import argparse, urllib.request, xml.etree.ElementTree as ET

AREAS = {
    "hanoi-caugiay": (21.0300, 105.7900),
    "hanoi-oceanpark": (20.9930, 105.9420),
    "hanoi-royalcity": (21.0020, 105.8150),
    "hcmc-district1": (10.7760, 106.7020),
    "singapore-cbd": (1.2830, 103.8510),
    "nyc-midtown": (40.7550, -73.9850),
}
ap = argparse.ArgumentParser(); ap.add_argument("--half", type=float, default=0.003); A = ap.parse_args()
print("| Khu | Toà nhà | Có chiều cao hoặc số tầng | Cao nhất (m, số tầng × 3 m nếu chỉ có số tầng) | Đường |")
print("|---|---|---|---|---|")
for name, (lat, lon) in AREAS.items():
    h = A.half
    url = f"https://www.openstreetmap.org/api/0.6/map?bbox={lon-h},{lat-h},{lon+h},{lat+h}"
    req = urllib.request.Request(url, headers={"User-Agent": "research-map-probe/0.1"})
    try:
        root = ET.fromstring(urllib.request.urlopen(req, timeout=60).read())
    except Exception as e:
        print(f"| {name} | lỗi: {e} | | | |"); continue
    nb = nh = nr = 0; top = 0.0
    for w in root.iter("way"):
        tags = {t.get("k"): t.get("v") for t in w.iter("tag")}
        if "building" in tags:
            nb += 1
            hm = None
            try:
                if "height" in tags: hm = float(tags["height"].split()[0].replace(",", "."))
                elif "building:levels" in tags: hm = 3.0 * float(tags["building:levels"])
            except ValueError:
                pass
            if hm is not None: nh += 1; top = max(top, hm)
        if "highway" in tags: nr += 1
    print(f"| {name} | {nb} | {nh} ({nh / nb * 100 if nb else 0:.0f} %) | {top:.0f} | {nr} |")
