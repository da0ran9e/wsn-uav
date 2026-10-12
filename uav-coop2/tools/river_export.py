"""Write the River plan (river_plan.py) as a plain-text file for the ns-3 trial (uav-coop2-river).

    python3 tools/river_export.py --deploy ../uav-coop/docs/data --path docs/data/path-a180.csv \
        --width 3.5 [--kg 2 --kl 1] --out docs/data/river-plan.txt

One record per line, cells as "q r":
  N    <packets sent, one per 0.5 m of the path>
  AXE  aq ar first last                      Seg(a) = [first, last]
  BANK aq ar side bq br  n c1q c1r ... cnq cnr    Path_side(a): a -> Bank
  CRIT kq kr
  CIRC kq kr mq mr aq ar bq br  n c...       member m of k fetches Seg(a) from Bank b along b -> m
  DIRECT kq kr aq ar  n c...                 direct pull: k -> a path (data goes back along it)
"""
import argparse, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from river_plan import load, plan, cellpath  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deploy", required=True)
    ap.add_argument("--path", required=True)
    ap.add_argument("--width", type=float, default=3.5)
    ap.add_argument("--kg", type=float, default=2.0, help="critical: global outlier, score > mu + kg sd")
    ap.add_argument("--kl", type=float, default=1.0, help="critical: local outlier, score > mu + kl sd")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    geo = load(a.deploy, a.path)
    P = plan(geo, width=a.width, kg=a.kg, kl=a.kl)
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
        for k in P["crit"]:
            for m, G, src in P["circle"][k]:
                for x, side, b, path in src:
                    f.write(f"CIRC {k[0]} {k[1]} {m[0]} {m[1]} {x[0]} {x[1]} {b[0]} {b[1]} {cells(path)}\n")
        for k in P["crit"]:
            for x in P["axe"]:
                if x != k:
                    f.write(f"DIRECT {k[0]} {k[1]} {x[0]} {x[1]} {cells(cellpath(k, x, geo['S'], geo['c']))}\n")
    print(f"{a.out}: {len(geo['uav'])} packets, Axe {len(P['axe'])}, critical {len(P['crit'])}")


if __name__ == "__main__":
    main()
