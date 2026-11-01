"""Sequenced takeover (rfS) vs simultaneous oracle takeover (rfT), sigma 100, seeds 1-3 -> compare-seq.md"""
import csv, glob, math, os, importlib.util
H = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("cmp", f"{H}/compare.py")
NOM = f"{H}/../2026-10-30_1545-deluge-r100/results"
def crit(d, tag):
    done = n = 0; cmax = []; ctrl = fr = 0; per = {}
    for k in range(1, 9):
        m = 0.0
        for c in csv.DictReader(open(f"{d}/r{k}-{tag}-crit.csv")):
            x = float(c["doneS"]); n += 1; done += x >= 0; m = max(m, x if x >= 0 else 900)
        cmax.append(m); per[k] = m
        ctrl += int(next(csv.DictReader(open(f"{d}/r{k}-{tag}-runs.csv")))["control"])
        fr += sum(int(r["framesTx"]) for r in csv.DictReader(open(f"{d}/r{k}-{tag}-energy.csv")))
    return done, n, sum(cmax) / 8, per, ctrl, fr
def ts(d):
    v = [float(r["Tstar"]) for r in csv.DictReader(open(f"{d}/l1-draws.csv")) if r["method"].split("-")[0] == "P+prog"]
    return sum(v) / len(v)
L = ["| seed | xong T → S | sẵn sàng TB 8 cụm (s): danh nghĩa / T / S | cụm có takeover: sẵn sàng T → S (s) | frame điều khiển T → S | frame phát tổng T → S | T* danh nghĩa / T / S |", "|---" * 7 + "|"]
dS = []
for R in (1, 2, 3):
    W = f"/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/WIND/s100/R{R}/k8-s1"
    a, b = crit(W, "rfT"), crit(W, "rfS")
    ks = [k for k in range(1, 9) if open(f"{W}/r{k}-rfT.log").read().count("\ntakeover") or open(f"{W}/r{k}-rfT.log").read().startswith("takeover")]
    tn, tt, tS = ts(f"{NOM}/R{R}"), ts(f"{H}/results/s100-R{R}"), ts(f"{H}/results/rfS-s100-R{R}")
    dS.append(tS - tn)
    L.append(f"| {R} | {a[0]}/{a[1]} → {b[0]}/{b[1]} | {crit(NOM + f'/R{R}', 'rf')[2]:.0f} / {a[2]:.0f} / {b[2]:.0f} | "
             + ", ".join(f"c{k}: {a[3][k]:.0f} → {b[3][k]:.0f}" for k in ks)
             + f" | {a[4]} → {b[4]} | {a[5]} → {b[5]} | {tn:.0f} / {tt:.0f} / {tS:.0f} |")
m = sum(dS) / 3; ci = 4.30 * math.sqrt(sum((x - m) ** 2 for x in dS) / 2) / math.sqrt(3)
L.append(f"\nT* (S) − danh nghĩa theo seed: {[round(x) for x in dS]}, trung bình {m:+.1f} ± {ci:.1f} s (CI 95 % theo seed, t, n = 3)")
open(f"{H}/compare-seq.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
