"""T* of CHORD and every baseline on the same missions and layer-1 draws (CLAUDE.md §8 item 182).

    python3 tools/cmp_table.py OUT DRAWS.csv [DRAWS.csv ...]

DRAWS: l1_rank --out prefixes' -draws.csv files, sets named by channel (they may split the methods between them; the
draws are paired by map, channel and draw index). Writes OUT.md and OUT.csv:
  T*        mean ± 95 % half-width over the draws, per map, channel and design; team 1's flight (BS to BS)
  vs CHORD  paired T* difference (design - CHORD), mean ± 95 % half-width, and the share of draws CHORD is faster
"""
import csv, sys

import numpy as np

DESIGNS = (("P+prog-kin-puq-stage-zero-redir-kt-fcd", "CHORD"), ("FC-puq-stage-zero-redir", "FC"),
           ("DN-puq-stage-zero-redir", "DN"), ("Pd+prog-kin-puq-stage-zero-redir-kt-fcd", "Pd"),
           ("B4-kin-puq-stage-zero-redir-kt-fcd", "B4"), ("B1", "B1"), ("B7", "B7"))
ENVS, MAPS = ("open", "r500", "r200", "r100"), ("k8-s1", "k12-s1", "k16-s1")


def main():
    out, files = sys.argv[1], sys.argv[2:]
    T = {}
    team1 = {}
    for f in files:
        for r in csv.DictReader(open(f)):
            T[(r["set"], r["map"], r["method"], int(r["draw"]))] = float(r["Tstar"])
            team1[(r["set"], r["map"], r["method"])] = float(r["team1"])
    designs = [(m, l) for m, l in DESIGNS if any(k[2] == m for k in T)]
    rows = []
    for e in ENVS:
        for mp in MAPS:
            base = {d: t for (s, m, me, d), t in T.items() if s == e and m == mp and me == DESIGNS[0][0]}
            for meth, label in designs:
                x = {d: t for (s, m, me, d), t in T.items() if s == e and m == mp and me == meth}
                if not x:
                    continue
                ts = np.array(list(x.values()))
                dd = np.array([x[d] - base[d] for d in sorted(x) if d in base])
                rows.append(dict(channel=e, map=mp, design=label, draws=len(ts),
                                 team1=round(team1[(e, mp, meth)], 1) if label not in ("B1", "B7") else "",
                                 Tstar=round(ts.mean(), 1), ci=round(1.96 * ts.std(ddof=1) / np.sqrt(len(ts)), 1),
                                 diff=round(dd.mean(), 1) if label != "CHORD" else "",
                                 diff_ci=round(1.96 * dd.std(ddof=1) / np.sqrt(len(dd)), 1) if label != "CHORD" else "",
                                 chord_faster=round(float(np.mean(dd > 0)) * 100) if label != "CHORD" else ""))
    with open(f"{out}.csv", "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)
    get = {(r["channel"], r["map"], r["design"]): r for r in rows}
    labels = [l for _, l in designs]
    md = ["T\\* trung bình ± 95 % (s), 100 lượt bốc lớp 1 ghép cặp:", "",
          "| kênh | bản đồ | " + " | ".join(labels) + " |", "|---" * (2 + len(labels)) + "|"]
    for e in ENVS:
        for mp in MAPS:
            md.append(f"| {e} | {mp} | " + " | ".join(
                f"{get[(e, mp, l)]['Tstar']:.0f} ± {get[(e, mp, l)]['ci']:.0f}" if (e, mp, l) in get else "–"
                for l in labels) + " |")
    md += ["", "Chênh lệch ghép cặp so với CHORD (phương án − CHORD, s; trong ngoặc: % lượt bốc CHORD nhanh hơn):", "",
           "| kênh | bản đồ | " + " | ".join(labels[1:]) + " |", "|---" * (1 + len(labels)) + "|"]
    for e in ENVS:
        for mp in MAPS:
            md.append(f"| {e} | {mp} | " + " | ".join(
                f"{get[(e, mp, l)]['diff']:+.0f} ± {get[(e, mp, l)]['diff_ci']:.0f} ({get[(e, mp, l)]['chord_faster']} %)"
                if (e, mp, l) in get else "–" for l in labels[1:]) + " |")
    md += ["", "Đội 1 bay, BS về BS (s):", "", "| kênh | bản đồ | " + " | ".join(
        l for l in labels if l not in ("B1", "B7")) + " |", "|---" * (2 + len([l for l in labels if l not in ("B1", "B7")])) + "|"]
    for e in ENVS:
        for mp in MAPS:
            md.append(f"| {e} | {mp} | " + " | ".join(
                f"{get[(e, mp, l)]['team1']:.0f}" if (e, mp, l) in get else "–" for l in labels if l not in ("B1", "B7"))
                + " |")
    open(f"{out}.md", "w").write("\n".join(md) + "\n")


if __name__ == "__main__":
    main()
