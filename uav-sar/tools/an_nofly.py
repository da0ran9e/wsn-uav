"""Score a run against its no-fly zones, and against what the zones hid.

Two questions, and the second is the interesting one:

  INCURSION  did the aircraft actually enter a zone? Clipping the lanes stops
             the plan from AIMING inside, but a curvature-limited aircraft
             turning between two clipped pieces can still cut the corner. That
             has to be measured, not assumed away.
  SHADOWED   how much screening capability sits inside the zones, and did the
             cell-based plan still satisfy those cells from outside? This is the
             premise under test: node coverage simply cannot reach a shadowed
             node, while cell coverage can still meet the cell's target using
             the members that lie outside.
"""
import csv, glob, math, os, statistics as st, sys

RC = 50.0


class Zone:
    """A circle or an axis-aligned rectangle, answering the same question."""

    def __init__(self, row):
        self.rect = row.get("shape") == "rect"
        if self.rect:
            self.x0, self.y0 = float(row["x0"]), float(row["y0"])
            self.x1, self.y1 = float(row["x1"]), float(row["y1"])
        else:
            self.x, self.y, self.r = float(row["x"]), float(row["y"]), float(row["r"])

    def contains(self, px, py):
        if self.rect:
            return self.x0 < px < self.x1 and self.y0 < py < self.y1
        return math.hypot(px - self.x, py - self.y) < self.r

    def depth(self, px, py):
        """How far inside, 0 when outside -- the number that says whether an
        incursion is a graze or a transit."""
        if not self.contains(px, py):
            return 0.0
        if self.rect:
            return min(px - self.x0, self.x1 - px, py - self.y0, self.y1 - py)
        return self.r - math.hypot(px - self.x, py - self.y)

    def area(self):
        return ((self.x1 - self.x0) * (self.y1 - self.y0) if self.rect
                else math.pi * self.r * self.r)


def zones(run):
    p = os.path.join(run, "nofly.csv")
    if not os.path.exists(p):
        return []
    return [Zone(r) for r in csv.DictReader(open(p))]


def seg_dist(px, py, ax, ay, bx, by):
    vx, vy = bx - ax, by - ay
    L2 = vx * vx + vy * vy
    t = ((px - ax) * vx + (py - ay) * vy) / L2 if L2 > 0 else 0.0
    t = max(0.0, min(1.0, t))
    return math.hypot(px - (ax + t * vx), py - (ay + t * vy))


def analyse(run):
    z = zones(run)
    caps = list(csv.DictReader(open(os.path.join(run, "capabilities.csv"))))
    m = list(csv.DictReader(open(os.path.join(run, "metrics.csv"))))[0]
    tracks, prev, dist = {}, {}, {}
    samples = inside = 0
    deepest = 0.0
    for r in csv.DictReader(open(os.path.join(run, "trajectories.csv"))):
        if r["role"] != "FAST":
            continue
        u, x, y = r["uavId"], float(r["x"]), float(r["y"])
        tracks.setdefault(u, []).append((x, y))
        if u in prev:
            dist[u] = dist.get(u, 0.0) + math.hypot(x - prev[u][0], y - prev[u][1])
        prev[u] = (x, y)
        samples += 1
        for zz in z:
            d = zz.depth(x, y)
            if d > 0:
                inside += 1
                deepest = max(deepest, d)
                break

    # capability inside the zones, and whether its cells were still served
    tot = sum(float(c["screening"]) for c in caps) or 1.0
    shadow = 0.0
    seeded_all = set()
    for i, c in enumerate(caps):
        cx, cy, s = float(c["x"]), float(c["y"]), float(c["screening"])
        if any(zz.contains(cx, cy) for zz in z):
            shadow += s
        for pts in tracks.values():
            if any(seg_dist(cx, cy, pts[k-1][0], pts[k-1][1], pts[k][0], pts[k][1]) <= RC
                   for k in range(1, len(pts))):
                seeded_all.add(i); break
    seen = sum(float(caps[i]["screening"]) for i in seeded_all)

    cell_tot, cell_got = {}, {}
    for i, c in enumerate(caps):
        cid = c["cellId"]
        cell_tot[cid] = cell_tot.get(cid, 0.0) + float(c["screening"])
        if i in seeded_all:
            cell_got[cid] = cell_got.get(cid, 0.0) + float(c["screening"])
    live = [cid for cid, t in cell_tot.items() if t > 1e-9]
    cell_ok = 100.0 * sum(1 for cid in live
                          if cell_got.get(cid, 0) >= 0.7 * cell_tot[cid]) / len(live)

    d = list(dist.values())
    return dict(nz=len(z), incur=100.0 * inside / max(1, samples), deepest=deepest,
                zarea=sum(zz.area() for zz in z),
                cap_cov=100.0 * seen / tot, shadow=100.0 * shadow / tot,
                cell_ok=cell_ok, km=sum(d) / 1000.0,
                imb=100.0 * (max(d) - min(d)) / (sum(d) / len(d)) if d else 0.0,
                loc=int(m["victimsLocated"]), vic=int(m["victimCount"]),
                kJ=float(m["uavEnergyJ"]) / 1000.0, tfix=float(m["timeToFixAtBS_s"]))


def main():
    root, arms = sys.argv[1], sys.argv[2:]
    hdr = (f"{'arm':<12}{'n':>3}{'zones':>6}{'incur%':>8}{'deep m':>8}{'shadow%':>9}"
           f"{'cap_cov':>9}{'cell_ok':>9}{'km':>7}{'imb%':>7}{'loc':>8}{'kJ':>7}{'tFix':>7}")
    print(hdr); print("-" * len(hdr))
    for arm in arms:
        rs = []
        for d in sorted(glob.glob(f"{root}/{arm}/s*"), key=lambda p: int(p.split("s")[-1])):
            if os.path.exists(os.path.join(d, "capabilities.csv")):
                try: rs.append(analyse(d))
                except Exception: pass
        if not rs:
            print(f"{arm:<12} (no runs)"); continue
        g = lambda k: st.mean(r[k] for r in rs)
        tf = [r["tfix"] for r in rs if r["tfix"] > 0]
        print(f"{arm:<12}{len(rs):>3}{rs[0]['nz']:>6}{g('incur'):7.2f}%{g('deepest'):8.1f}"
              f"{g('shadow'):8.1f}%{g('cap_cov'):8.1f}%{g('cell_ok'):8.1f}%{g('km'):7.1f}"
              f"{g('imb'):7.1f}{sum(r['loc'] for r in rs):4d}/{sum(r['vic'] for r in rs):<3}"
              f"{g('kJ'):7.0f}{(st.mean(tf) if tf else float('nan')):7.0f}")


def assert_no_incursion(root, arms):
    """A no-fly zone the aircraft enters is not a no-fly zone. Fail loudly."""
    bad = []
    for arm in arms:
        for d in sorted(glob.glob(f"{root}/{arm}/s*")):
            if not os.path.exists(os.path.join(d, "capabilities.csv")):
                continue
            r = analyse(d)
            if r["incur"] > 0:
                bad.append(f"{d}: {r['incur']:.3f}% inside, {r['deepest']:.1f} m deep")
    assert not bad, "no-fly zones were entered:\n  " + "\n  ".join(bad)
    return True


if __name__ == "__main__":
    main()
