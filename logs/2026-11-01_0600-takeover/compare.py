"""Before / after the takeover repair on the wind table (k8-s1, r100, CHORD passes): python3 compare.py -> compare.md/.csv
Before = River (rf) on the flown path (logs/2026-10-31_0000-wind), after = River + takeover (rfT, this folder),
nominal = River on the planned path (logs/2026-10-30_1545-deluge-r100). T*: mean of 100 paired layer-1 draws per seed;
paired after - before per draw. Ready: last critical cell, from the UAV leaving its cluster (900 s when not done).
"""
import csv, glob, math, os
H = os.path.dirname(os.path.abspath(__file__))
OLD, NOM = f"{H}/../2026-10-31_0000-wind/results", f"{H}/../2026-10-30_1545-deluge-r100/results"
T95 = {1: 12.71, 2: 4.30, 3: 3.18, 4: 2.78}

def crit(d, tag):
    done = n = miss = 0; last = 0.0; hops = 0
    for f in sorted(glob.glob(f"{d}/r*-{tag}-crit.csv")):
        for c in csv.DictReader(open(f)):
            x = float(c["doneS"]); n += 1; done += x >= 0; miss += int(c["missing"]); last = max(last, x if x >= 0 else 900)
    for f in glob.glob(f"{d}/r*-{tag}-runs.csv"):
        hops += int(next(csv.DictReader(open(f)))["hops"])
    return done, n, last, miss, hops

def draws(d, base="P+prog"):
    return {int(r["draw"]): float(r["Tstar"]) for r in csv.DictReader(open(f"{d}/l1-draws.csv")) if r["method"].split("-")[0] == base}

rows = []
for sig in (50, 100, 200):
    for R in (1, 2, 3):
        a, b = f"{H}/results/s{sig}-R{R}", f"{OLD}/s{sig}-R{R}"
        if not os.path.exists(f"{a}/l1-draws.csv"): continue
        ta, tb, tn = draws(a), draws(b), draws(f"{NOM}/R{R}")
        da, db = crit(a, "rfT"), crit(b, "rf")
        diff = [ta[i] - tb[i] for i in ta if i in tb]
        m = sum(diff) / len(diff); sd = math.sqrt(sum((x - m) ** 2 for x in diff) / (len(diff) - 1))
        rows.append(dict(sigma=sig, seed=R, done_before=f"{db[0]}/{db[1]}", done_after=f"{da[0]}/{da[1]}",
                         ready_before=round(db[2]), ready_after=round(da[2]), missing_before=db[3], missing_after=da[3],
                         hops_before=db[4], hops_after=da[4], T_nominal=round(sum(tn.values()) / len(tn), 1),
                         T_before=round(sum(tb.values()) / len(tb), 1), T_after=round(sum(ta.values()) / len(ta), 1),
                         dT=round(m, 1), dT_ci_draw=round(1.96 * sd / math.sqrt(len(diff)), 1),
                         after_better=sum(x < 0 for x in diff), after_worse=sum(x > 0 for x in diff)))
with open(f"{H}/compare.csv", "w", newline="") as f:
    w = csv.DictWriter(f, list(rows[0])); w.writeheader(); w.writerows(rows)
L = ["| σ | seed | xong trước → sau | cell cuối, s | gói thiếu | T* danh nghĩa | T* trước | T* sau | ΔT* (sau − trước) | sau tốt/xấu hơn (lượt) |", "|---" * 10 + "|"]
for r in rows:
    L.append(f"| {r['sigma']} | {r['seed']} | {r['done_before']} → {r['done_after']} | {r['ready_before']} → {r['ready_after']} | "
             f"{r['missing_before']} → {r['missing_after']} | {r['T_nominal']} | {r['T_before']} | {r['T_after']} | "
             f"{r['dT']} ± {r['dT_ci_draw']} | {r['after_better']}/{r['after_worse']} |")
L.append("")
for sig in (50, 100, 200):
    ds = [r["dT"] for r in rows if r["sigma"] == sig]
    rel = [r["T_after"] - r["T_nominal"] for r in rows if r["sigma"] == sig]
    rb = [r["T_before"] - r["T_nominal"] for r in rows if r["sigma"] == sig]
    if not ds: continue
    n = len(ds); m = sum(ds) / n
    ci = T95[n - 1] * math.sqrt(sum((x - m) ** 2 for x in ds) / (n - 1)) / math.sqrt(n) if n > 1 else float("nan")
    L.append(f"σ={sig}: {n} seed, ΔT* trung bình {m:.1f} s (CI theo seed ± {ci:.1f}); T* trên danh nghĩa: trước +{sum(rb)/n:.1f} s, sau +{sum(rel)/n:.1f} s")
open(f"{H}/compare.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
