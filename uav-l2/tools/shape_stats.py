"""Shape statistics of the Eden regions of map_gen.py over many seeds: elongation, bend, holes, convexity.

    python3 tools/shape_stats.py   (run from uav-l2/)
"""
import sys, math, random, statistics as st
sys.path.insert(0, 'tools')
from map_gen import centre, hull_cells, holes, NB
import numpy as np

def grow(seed, n):
    rng = random.Random(seed); cells, fr, onf, S = [], [], set(), set()
    def add(h):
        cells.append(h); S.add(h)
        for dq, dr in NB:
            m = (h[0]+dq, h[1]+dr)
            if m not in S and m not in onf: onf.add(m); fr.append(m)
    add((0, 0))
    while len(cells) < n:
        k = rng.randrange(len(fr)); h = fr[k]; fr[k] = fr[-1]; fr.pop(); onf.discard(h); add(h)
    return cells

def hole_groups(cells):
    H = set(holes(cells)); seen = set(); sizes = []
    for h in H:
        if h in seen: continue
        st_ = [h]; seen.add(h); k = 0
        while st_:
            x = st_.pop(); k += 1
            for dq, dr in NB:
                m = (x[0]+dq, x[1]+dr)
                if m in H and m not in seen: seen.add(m); st_.append(m)
        sizes.append(k)
    return sizes

for n in (60, 300):
    el, bend, nh, mh, cv = [], [], [], [], []
    for seed in range(1, 201):
        c = grow(seed, n); P = np.array([centre(h) for h in c])
        P0 = P - P.mean(0); w, v = np.linalg.eigh(np.cov(P0.T))
        el.append(math.sqrt(w[1] / w[0]))
        # bend: project on the long axis, take the mean lateral offset in 10 slices; curvature = max |offset of
        # slice means| from the chord joining the end slices, divided by the length
        t = P0 @ v[:, 1]; u = P0 @ v[:, 0]
        edges = np.linspace(t.min(), t.max(), 11); mids, offs = [], []
        for i in range(10):
            m = (t >= edges[i]) & (t <= edges[i+1])
            if m.any(): mids.append(t[m].mean()); offs.append(u[m].mean())
        mids, offs = np.array(mids), np.array(offs)
        chord = offs[0] + (offs[-1] - offs[0]) * (mids - mids[0]) / (mids[-1] - mids[0])
        bend.append(np.abs(offs - chord).max() / (t.max() - t.min()))
        g = hole_groups(c); nh.append(len(g)); mh.append(max(g) if g else 0)
        cv.append(len(c) / len(hull_cells(c)))
    q = lambda x: f"median {st.median(x):.2f}, p90 {np.percentile(x, 90):.2f}, max {max(x):.2f}"
    print(f"{n} cells, 200 seeds:")
    print(f"  elongation (long/short axis)    {q(el)}")
    print(f"  bend (max offset / length)      {q(bend)}")
    print(f"  holes per region                {q(nh)}")
    print(f"  largest hole, cells             {q(mh)}")
    print(f"  convexity                       {q(cv)}")
