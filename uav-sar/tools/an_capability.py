"""Score a capability-aware Phase 1 sweep.

The metrics that matter change once nodes differ. "Nodes covered" stops being
the question, because a node with no camera cannot produce evidence however
often it is flown over. What is asked here instead:

  cap_cov    share of the field's total SCREENING CAPABILITY (obs x cpu) that
             came within the cue radius of some fixed-wing path
  cell_seed  share of CELLS that reached the capability target -- the thing
             cell-based planning is actually trying to achieve
  cap_imbal  spread of capability across the fixed-wing UAVs (max-min)/mean
  eff_imbal  same for flight distance -- "capability and effort both even"
             is two constraints, and reporting one hides the other
"""
import csv, glob, math, os, statistics as st, sys

RC = 50.0

def seg_dist(px, py, ax, ay, bx, by):
    vx, vy = bx - ax, by - ay
    L2 = vx * vx + vy * vy
    t = ((px - ax) * vx + (py - ay) * vy) / L2 if L2 > 0 else 0.0
    t = max(0.0, min(1.0, t))
    return math.hypot(px - (ax + t * vx), py - (ay + t * vy))

def analyse_run(d):
    caps = list(csv.DictReader(open(os.path.join(d, "capabilities.csv"))))
    m = list(csv.DictReader(open(os.path.join(d, "metrics.csv"))))[0]
    tracks, prev, dist = {}, {}, {}
    for r in csv.DictReader(open(os.path.join(d, "trajectories.csv"))):
        if r["role"] != "FAST":
            continue
        u, x, y = r["uavId"], float(r["x"]), float(r["y"])
        tracks.setdefault(u, []).append((x, y))
        if u in prev:
            dist[u] = dist.get(u, 0.0) + math.hypot(x - prev[u][0], y - prev[u][1])
        prev[u] = (x, y)
    uavs = sorted(tracks)
    # capability seeded, per UAV. Track points are sampled, so the segment
    # between consecutive samples is used rather than the samples alone --
    # at 25 m/s and a 1 s trajectory tick, point-only tests would miss nodes
    # the aircraft flew straight past.
    seeded = {u: set() for u in uavs}
    for u in uavs:
        pts = tracks[u]
        for i, c in enumerate(caps):
            cx, cy = float(c["x"]), float(c["y"])
            for k in range(1, len(pts)):
                if seg_dist(cx, cy, pts[k-1][0], pts[k-1][1], pts[k][0], pts[k][1]) <= RC:
                    seeded[u].add(i); break
    totcap = sum(float(c["screening"]) for c in caps)
    capu = {u: sum(float(caps[i]["screening"]) for i in seeded[u]) for u in uavs}
    allseed = set().union(*seeded.values()) if seeded else set()
    cap_cov = 100.0 * sum(float(caps[i]["screening"]) for i in allseed) / totcap if totcap else 0.0
    node_cov = 100.0 * len(allseed) / len(caps)
    # cells reaching 70% of their own capability
    cell_tot, cell_got = {}, {}
    for i, c in enumerate(caps):
        cid = c["cellId"]
        cell_tot[cid] = cell_tot.get(cid, 0.0) + float(c["screening"])
        if i in allseed:
            cell_got[cid] = cell_got.get(cid, 0.0) + float(c["screening"])
    live = [cid for cid, t in cell_tot.items() if t > 1e-9]
    cell_seed = 100.0 * sum(1 for cid in live
                            if cell_got.get(cid, 0) >= 0.7 * cell_tot[cid]) / len(live)
    def imbal(v):
        v = list(v)
        return 100.0 * (max(v) - min(v)) / (sum(v) / len(v)) if v and sum(v) else 0.0
    return dict(cap_cov=cap_cov, node_cov=node_cov, cell_seed=cell_seed,
                cap_imbal=imbal(capu.values()), eff_imbal=imbal(dist.values()),
                km=sum(dist.values()) / 1000.0, nfast=len(uavs),
                loc=int(m["victimsLocated"]), vic=int(m["victimCount"]),
                wrong=int(m["wrongFixes"]), kJ=float(m["uavEnergyJ"]) / 1000.0,
                tfix=float(m["timeToFixAtBS_s"]))

def main():
    base = sys.argv[1]
    arms = sys.argv[2:]
    hdr = (f"{'arm':<12}{'n':>3}{'FAST':>5}{'cap_cov':>9}{'node_cov':>9}{'cell_seed':>10}"
           f"{'cap_imb':>9}{'eff_imb':>9}{'km':>7}{'loc':>8}{'wrong':>6}{'kJ':>7}{'tFix':>7}")
    print(hdr); print("-" * len(hdr))
    for arm in arms:
        rs = []
        for d in sorted(glob.glob(f"{base}/{arm}/s*"), key=lambda p: int(p.split("s")[-1])):
            if os.path.exists(os.path.join(d, "capabilities.csv")):
                try: rs.append(analyse_run(d))
                except Exception: pass
        if not rs:
            print(f"{arm:<12} (no runs)"); continue
        g = lambda k: st.mean(r[k] for r in rs)
        tf = [r["tfix"] for r in rs if r["tfix"] > 0]
        loc = sum(r["loc"] for r in rs); vic = sum(r["vic"] for r in rs)
        print(f"{arm:<12}{len(rs):>3}{rs[0]['nfast']:>5}{g('cap_cov'):8.1f}%{g('node_cov'):8.1f}%"
              f"{g('cell_seed'):9.1f}%{g('cap_imbal'):8.1f}%{g('eff_imbal'):8.1f}%"
              f"{g('km'):7.1f}{loc:5d}/{vic:<2}{sum(r['wrong'] for r in rs):6d}"
              f"{g('kJ'):7.0f}{(st.mean(tf) if tf else float('nan')):7.0f}")

if __name__ == "__main__":
    main()
