"""Write the River plan (river_plan.py) as a plain-text file for the ns-3 trial (uav-coop2-river).

    python3 tools/river_export.py --deploy ../uav-coop/docs/data --path docs/data/path-a180.csv \
        --width 3.5 [--kg 2 --kl 1] --out docs/data/river-plan.txt

One record per line, cells as "q r":
  N    <packets sent, one per 0.5 m of the path>
  AXE  aq ar first last                      Seg(a) = [first, last]
  BANK aq ar side bq br  n c1q c1r ... cnq cnr    Path_side(a): a -> Bank
  CRIT kq kr
  NEED kq kr first last                      --windowAt crit: k needs only the Axe packets first..last
  CIRC kq kr mq mr aq ar bq br  n c...       member m of k fetches Seg(a) from Bank b along b -> m
  DIRECT kq kr aq ar  n c...                 direct pull: k -> a path (data goes back along it)
  CSET kq kr n mq mr first last              adaptive Circle of n members: m serves Axe cells first..last
  CSRC kq kr mq mr aq ar bq br  n c...       candidate m of k fetches Seg(a) from Bank b along b -> m
  CLINK kq kr mq mr  n c...                  k -> candidate m
"""
import argparse, math, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from river_plan import cellpath, load, load_around, plan  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deploy", required=True)
    ap.add_argument("--path", required=True)
    ap.add_argument("--width", type=float, default=3.5)
    ap.add_argument("--kg", type=float, default=2.0, help="critical: global outlier, score > mu + kg sd")
    ap.add_argument("--kl", type=float, default=1.0, help="critical: local outlier, score > mu + kl sd")
    ap.add_argument("--banks", default="parallel", choices=("parallel", "local"),
                    help="Banks along the sum vector's normal, or the path's local normal (CLAUDE.md §8 item 103)")
    ap.add_argument("--reentry", action="store_true",
                    help="a curved path may cross an Axe cell again: Seg(a) is its longest visit")
    ap.add_argument("--windowKB", type=float, default=0,
                    help="the cluster needs only this much of D (99 B packets), around where the UAV passes the CH")
    ap.add_argument("--windowAt", default="ch", choices=("ch", "crit"),
                    help="the window around the CH for the whole cluster, or around each critical cell (item 120)")
    ap.add_argument("--around", default="", help="CSV q,r,score of every domain cell: critical cells' local test "
                    "over the real neighbourhood (CLAUDE.md §8 item 135)")
    ap.add_argument("--axeNear", action="store_true", help="a packet sent just outside the cluster belongs to the "
                    "nearest cluster cell next to the UAV (CLAUDE.md §8 item 135)")
    ap.add_argument("--lossDb", type=float, default=None, help="with --axeNear: only if, on the pass channel with this "
                    "excess loss, a node of that cell hears it all but surely (river_plan.NEAR_EPS; item 163)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    geo = load(a.deploy, a.path)
    P = plan(geo, width=a.width, kg=a.kg, kl=a.kl, banks=a.banks, reentry=a.reentry,
             window=math.ceil(a.windowKB * 1000 / 99), window_at=a.windowAt,
             domain_sc=load_around(a.around) if a.around else None, near=a.axeNear, near_loss=a.lossDb)
    cells = lambda cs: f"{len(cs)} " + " ".join(f"{q} {r}" for q, r in cs)
    with open(a.out, "w") as f:
        f.write(f"N {len(geo['uav'])}\n")
        for x in P["axe"]:
            s = P["seg"][x]
            f.write(f"AXE {x[0]} {x[1]} {s[0]} {s[-1]}\n")
        for (x, side), b in sorted(P["bank"].items()):
            f.write(f"BANK {x[0]} {x[1]} {side} {b[0]} {b[1]} {cells(P['bpath'][(x, side)])}\n")
        for k in P["crit"]:
            f.write(f"CRIT {k[0]} {k[1]}\n")
        for k, (lo, hi) in sorted(P["need"].items()):
            f.write(f"NEED {k[0]} {k[1]} {lo} {hi}\n")
        for k in P["crit"]:
            for m, G, src in P["circle"][k]:
                for x, side, b, path in src:
                    f.write(f"CIRC {k[0]} {k[1]} {m[0]} {m[1]} {x[0]} {x[1]} {b[0]} {b[1]} {cells(path)}\n")
        for k in P["crit"]:
            for x in P["axe"]:
                if x != k:
                    f.write(f"DIRECT {k[0]} {k[1]} {x[0]} {x[1]} {cells(cellpath(k, x, geo['S'], geo['c']))}\n")
        for k in P["crit"]:
            A = P["adapt"][k]
            for n, mem in A["sets"].items():
                for m, (g0, g1) in mem:
                    if g1 < g0:   # more members than Axe cells: this one serves nothing
                        continue
                    f.write(f"CSET {k[0]} {k[1]} {n} {m[0]} {m[1]} {g0} {g1}\n")
            for (m, x), (b, path) in sorted(A["src"].items()):
                f.write(f"CSRC {k[0]} {k[1]} {m[0]} {m[1]} {x[0]} {x[1]} {b[0]} {b[1]} {cells(path)}\n")
            for m, path in sorted(A["link"].items()):
                f.write(f"CLINK {k[0]} {k[1]} {m[0]} {m[1]} {cells(path)}\n")
    print(f"{a.out}: {len(geo['uav'])} packets, Axe {len(P['axe'])}, critical {len(P['crit'])}")


if __name__ == "__main__":
    main()
