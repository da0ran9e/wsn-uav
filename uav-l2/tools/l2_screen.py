"""One row per layer-2 work folder (CLAUDE.md §8 item 147): team 1's tour (kin_time) and how close the critical
cells lie to their cluster's flight line.

    python3 tools/l2_screen.py OUT.md LABEL=WORK:KIND [...]       # KIND kin (CHORD-T) or route (meander_lane)

Columns: clusters, land cells, tour at 50 m/s, with the speed profile and the delivery fixes at 45 and 30 degree
bank (clusters fixed), the tour's metres by kind (over the clusters' cores, their leads, transits between clusters
including MEANDER's turns between lanes, to and from the BS; kin_time.run), critical cells, their mean and 90th-percentile distance to the path, and how many lie
farther than twice the River half width (2 OMEGA, 606 m).
"""
import sys

import numpy as np

import kin_time
from meander_lane import OMEGA


def row(label, w, kind):
    M, o = kin_time.run(w, kind)
    d = np.array([np.min(np.linalg.norm(C["geo"]["path"] - np.array(C["geo"]["c"][h]), axis=1))
                  for C in M["cl"].values() for h in C["P"]["crit"]])
    t = [f"{o[p]['profile'] + o[p]['fix']:.0f} ({len(o[p]['how'])})" for p in kin_time.PHIS]
    q = o["parts"]
    return (f"| {label} | {len(M['cl'])} | {M['m']['cells']} | {o['const']:.0f} | {t[0]} | {t[1]} | "
            + " | ".join(f"{q[x] / 1000:.1f}" for x in ("core", "lead", "transit", "bs"))
            + f" | {len(d)} | {d.mean():.0f} | {np.percentile(d, 90):.0f} | {(d > 2 * OMEGA).sum()} |")


def main():
    out = ["| | cụm | cell | 50 m/s (s) | 45° + giao đủ (s, số cụm phải bù) | 30° + giao đủ | trên cụm (km) | "
           "dẫn vào/ra (km) | nối giữa cụm (km) | BS (km) | critical | khoảng cách TB (m) | p90 (m) | > 606 m |",
           "|---" * 14 + "|"]
    for arg in sys.argv[2:]:
        label, spec = arg.split("=", 1)
        w, kind = spec.rsplit(":", 1)
        out.append(row(label, w, kind))
    open(sys.argv[1], "w").write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
