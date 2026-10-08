"""Compare manifest scenarios side by side.

    python3 tools/scenario_report.py OUT.csv LABEL=MANIFEST_PREFIX:SUMMARY_PREFIX ...

For each scenario reads PREFIX-cells.csv / PREFIX-missions.csv of uav-coop-manifest and
SUMMARY-cells.csv of uav-coop-summary, prints one table and writes OUT.csv.
"""
import csv, statistics as S, sys


def pct(v, q):
    v = sorted(v)
    return v[min(len(v) - 1, int(q * len(v)))] if v else float("nan")


def one(label, mp, sp):
    cells = list(csv.DictReader(open(mp + "-cells.csv")))
    miss = list(csv.DictReader(open(mp + "-missions.csv")))
    summ = list(csv.DictReader(open(sp + "-cells.csv")))
    runs = len(miss)
    lack = [r for r in cells if int(r["lacks0"]) > 0]
    lat = [float(r["fullS"]) - float(r["readyS"]) for r in lack if float(r["fullS"]) >= 0]
    st = [float(r["doneS"]) for r in summ if r["complete"] == "1"]
    out = {
        "scenario": label, "missions": runs,
        "summaryExact%": 100 * sum(r["exact"] == "1" and r["complete"] == "1" for r in summ) / len(summ),
        "summaryMedianS": S.median(st), "summaryP90S": pct(st, .9),
        "cellsLackingPerMission": len(lack) / runs,
        "lackingChunksMedian": S.median([int(r["lacks0"]) for r in lack]) if lack else 0,
        "lackingChunksMax": max([int(r["lacks0"]) for r in lack], default=0),
        "cellsLackingAfter": sum(int(r["lacksEnd"]) > 0 for r in cells),
        "chunksLackingAfter": sum(int(r["lacksEnd"]) for r in cells),
        "latencyMedianS": S.median(lat) if lat else 0, "latencyP90S": pct(lat, .9), "latencyMaxS": max(lat, default=0),
        "manifests": sum(int(r["manifests"]) for r in cells), "reverse": sum(int(r["reverse"]) for r in cells),
        "cellsPerManifest": sum(int(r["forwarded"]) for r in cells) / max(1, sum(int(r["manifests"]) for r in cells)),
        "toCH": sum(int(m["toCH"]) for m in miss), "chRemainder": sum(int(m["chRemainder"]) for m in miss),
        "copiesKept": sum(int(r["cached"]) for r in cells),
        "hopsDataMedian": S.median([int(m["hopsData"]) for m in miss]),
        "hopsManifestMedian": S.median([int(m["hopsManifest"]) for m in miss]),
        "hopsStoreMedian": S.median([int(m["hopsStore"]) for m in miss]),
        "cellsKeepGapBefore": sum(int(r["keepGap0"]) > 0 for r in cells) / runs,
        "cellsKeepGapAfter": sum(int(r["keepGapEnd"]) > 0 for r in cells) / runs,
        "keepGapChunksMaxAfter": max(int(r["keepGapEnd"]) for r in cells),
    }
    return out


def main():
    rows = []
    for arg in sys.argv[2:]:
        label, prefixes = arg.split("=", 1)
        mp, sp = prefixes.split(":")
        rows.append(one(label, mp, sp))
    with open(sys.argv[1], "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.3f}" if isinstance(v, float) else v) for k, v in r.items()})
    for k in rows[0]:
        if k == "scenario":
            print(f"{'':28}" + "".join(f"{r['scenario']:>16}" for r in rows))
            continue
        print(f"{k:28}" + "".join(f"{(f'{r[k]:.2f}' if isinstance(r[k], float) else r[k]):>16}" for r in rows))


if __name__ == "__main__":
    main()
