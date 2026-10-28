"""The campaign's table (CLAUDE.md §8 item 188) from score/R<R>/<env>-k<K>/: per scheme, channel and map, the mean
T* over every seed done (100 layer-1 draws each) and team 1's flight, and the paired differences against LM-Tour,
with a 95 % interval over seeds (the seed means, Student t), since the 100 draws of one seed share one ns-3
network realisation.

    python3 table.py [--csv OUT.csv] [--tex OUT.tex] [--results RESULTS-vi.md] > table.md

The first table has the paper's layout (paper/icc-v5/table-tstar.tex): a row per scheme, a column per range r,
each cell K = 8 / 12 / 16, "–" where the task is not done yet. --results rewrites that table and the paired
differences between the campaign4 markers of uav-l2/docs/RESULTS-vi.md section 7.1.

DTSP-N + River before its ns-3 run (item 194): the model-level estimate of logs/2026-10-28_0310-dtspn-fix/est (seed 1,
River predicted by the surrogate, lm_tour.py score --mode pred), marked *; its paired differences against LM-Tour
are taken between the two model-level estimates, and CHORD's and LM-Tour's own estimates against their ns-3 runs
show the model's error.
"""
import datetime
import argparse, csv, glob, math, os, re
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ENVS = ("open", "r500", "r200", "r100")
RANGE = {"open": "1 km", "r500": "500 m", "r200": "200 m", "r100": "150 m"}
MAPS = (8, 12, 16)
SCHEMES = (("LMD", "LM-Tour + River"), ("CP", "CHORD + River"), ("DR", "DTSP-N + River"), ("DN", "FC + DTSP-N"),
           ("B1", "No broadcast (rotary TSP)"), ("B7", "Oracle"))
L1 = {"DN-puq-stage-zero-redir": "DN", "B1": "B1", "B7": "B7", "P+prog-kin-puq-stage-zero-redir-kt-fcd": "CPl1"}
EST = os.path.join(HERE, "../2026-10-28_0310-dtspn-fix/est")
T975 = {1: 12.71, 2: 4.30, 3: 3.18, 4: 2.78, 5: 2.57, 6: 2.45, 7: 2.36, 8: 2.31, 9: 2.26, 10: 2.23}


def load():
    """{(scheme, env, K, R): {draw: (T*, team 1)}}, and the largest |T*| gap between l1_rank's and lm_tour's CHORD."""
    out, gap = {}, 0.0
    for d in sorted(glob.glob(f"{HERE}/score/R*/*-k*/done")):
        m = re.search(r"/R(\d+)/(\w+)-k(\d+)/done$", d)
        R, env, K, d = int(m[1]), m[2], int(m[3]), os.path.dirname(d)
        for r in csv.DictReader(open(f"{d}/score-ns3.csv")):
            s = next(s for s in ("LMD", "CP", "DR") if f"/{s}/" in r["work"])
            if s != "DR":   # DR rows here are the pass before item 193 (C4/DR-old); the fixed one is in score-dr.csv
                out.setdefault((s, env, K, R), {})[int(r["draw"])] = (float(r["Tstar"]), float(r["team1"]))
        if os.path.exists(f"{d}/done-dr"):
            for r in csv.DictReader(open(f"{d}/score-dr.csv")):
                out.setdefault(("DR", env, K, R), {})[int(r["draw"])] = (float(r["Tstar"]), float(r["team1"]))
        for r in csv.DictReader(open(f"{d}/l1-draws.csv")):
            out.setdefault((L1[r["method"]], env, K, R), {})[int(r["draw"])] = (float(r["Tstar"]), float(r["team1"] or 0))
        a, b = out[("CP", env, K, R)], out[("CPl1", env, K, R)]
        assert a.keys() == b.keys(), (env, K, R)
        gap = max(gap, max(abs(a[x][0] - b[x][0]) for x in a))
    return out, gap


def sg(v):
    """A signed number of seconds, 0 without a sign."""
    return "0" if abs(v) < 0.5 else f"{v:+.0f}"


def load_est():
    """{(scheme, env, K): {draw: T*}}, model level, seed 1: CP, LMD and the fixed DTSP-N + River (DRT as DR)."""
    out = {}
    for f in glob.glob(f"{EST}/*-k*/score-pred.csv"):
        m = re.search(r"/(\w+)-k(\d+)/score-pred\.csv$", f)
        for r in csv.DictReader(open(f)):
            s = next(s for s in ("LMD", "CP", "DRT") if f"/{s}/" in r["work"])
            out.setdefault(("DR" if s == "DRT" else s, m[1], int(m[2])), {})[int(r["draw"])] = float(r["Tstar"])
    return out


def grid(X, seeds, E):
    """{scheme: {env: "k8 / k12 / k16"}}: mean T* over the seeds done, "–" if none."""
    out = {}
    for s, _ in SCHEMES:
        out[s] = {}
        for env in ENVS:
            v = [np.mean([t for R in sorted(seeds[(env, K)]) if (s, env, K, R) in X for t, _ in X[(s, env, K, R)].values()])
                 if any((s, env, K, R) in X for R in seeds.get((env, K), ())) else None for K in MAPS]
            out[s][env] = " / ".join(f"{x:.0f}" if x is not None else
                                     f"{np.mean(list(E[(s, env, K)].values())):.0f}*" if (s, env, K) in E and s == "DR"
                                     else "–" for x, K in zip(v, MAPS))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="")
    ap.add_argument("--tex", default="")
    ap.add_argument("--results", default="")
    a = ap.parse_args()
    X, gap = load()
    E = load_est()
    seeds = defaultdict(set)
    for s, env, K, R in X:
        seeds[(env, K)].add(R)
    G = grid(X, seeds, E)
    n = sorted({len(v) for v in seeds.values()})
    gl = ["T\\* trung bình (s), K = 8 / 12 / 16 cụm; mỗi ô 100 lượt bốc lớp 1 × số seed đã xong "
          f"({'–'.join(map(str, (n[0], n[-1]))) if len(n) > 1 else n[0]}); – : chưa chạy xong.", "",
          "| phương án | r = 1000 m | 500 m | 200 m | 150 m |", "|---|---|---|---|---|"]
    gl += [f"| {name} | " + " | ".join(G[s][e] for e in ENVS) + " |" for s, name in SCHEMES]
    if any("*" in G["DR"][e] for e in ENVS):   # a DTSP-N + River cell still waits for its ns-3 run
        gl += ["", "\\* ước lượng mức mô hình của DTSP-N + River đã sửa (mục 193–194): seed 1, River dự đoán bằng bộ surrogate, chưa "
               "chạy ns-3; số đo ns-3 thay vào khi tác vụ xong. Cùng cách ước lượng, CHORD và LM-Tour lệch số ns-3 của "
               "chúng: " + ", ".join(f"k{K} {env} {sg(np.mean(list(E[('CP', env, K)].values())) - np.mean([t for t, _ in X[('CP', env, K, 1)].values()]))} / "
                                     f"{sg(np.mean(list(E[('LMD', env, K)].values())) - np.mean([t for t, _ in X[('LMD', env, K, 1)].values()]))} s"
                                     for K in MAPS for env in ENVS if ("CP", env, K) in E and ("CP", env, K, 1) in X).replace("-", "−") + "."]
    print("\n".join(gl) + "\n")
    if a.tex:
        with open(a.tex, "w") as f:
            f.write("% Generated by logs/2026-10-27_1714-campaign4/table.py (CLAUDE.md §8 items 187-189); \"--\" = not run yet.\n"
                    "\\begin{table*}[t]\\centering\\caption{Mean mission time $T^\\star$ (s), $K$ = 8 / 12 / 16 clusters, "
                    f"ns-3, 100 paired draws per seed, {n[-1] if n else 0} seed(s) so far. --: not run yet; $^*$: model-level "
                    "estimate (River predicted, not yet run in ns-3).}}\\label{{tab:tstar}}\n"
                    "\\setlength{\\tabcolsep}{3pt}\\footnotesize\n\\begin{tabular}{lcccc}\\toprule\n"
                    "Scheme & $r=1000$ m & 500 & 200 & 150 \\\\\\midrule\n")
            for s, name in SCHEMES:
                f.write(f"{name} & " + " & ".join(G[s][e].replace("–", "--").replace("*", "$^*$") for e in ENVS) + " \\\\\n")
            f.write("\\bottomrule\\end{tabular}\\end{table*}\n")
    rows = []
    for (s, env, K, R), v in sorted(X.items()):
        if s == "CPl1":
            continue
        T = np.array([t for t, _ in v.values()])
        rows.append(dict(scheme=s, env=env, map=f"k{K}-s1", seed=R, kind="ns3", draws=len(T), Tstar=round(float(T.mean()), 1),
                         TstarSd=round(float(T.std()), 1), team1=round(float(np.mean([u for _, u in v.values()])), 1)))
    for (s, env, K), v in sorted(E.items()):   # model-level estimates (item 194)
        T = np.array(list(v.values()))
        rows.append(dict(scheme=s, env=env, map=f"k{K}-s1", seed=1, kind="pred", draws=len(T), Tstar=round(float(T.mean()), 1),
                         TstarSd=round(float(T.std()), 1), team1=""))
    if a.csv:
        with open(a.csv, "w", newline="") as f:
            wr = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
            wr.writeheader()
            wr.writerows(rows)
    print(f"# Bảng chiến dịch (seed đã xong: {', '.join(f'k{K} {env} {len(seeds[(env, K)])}' for K in MAPS for env in ENVS if (env, K) in seeds)})\n")
    print(f"CHORD chấm bằng `l1_rank` và bằng `lm_tour score` lệch nhau tối đa {gap:.1f} s ở mọi lượt bốc.\n")
    print("T\\* trung bình (s) trên mọi seed và lượt bốc; ngoặc: số seed. Team 1: thời gian bay của đội 1 (s).\n")
    print("| kênh (r) | bản đồ | " + " | ".join(n for _, n in SCHEMES) + " | team 1 LM / CHORD / DR / DN |")
    print("|---|---|" + "---|" * len(SCHEMES) + "---|")
    for env in ENVS:
        for K in MAPS:
            if (env, K) not in seeds:
                continue
            Rs = sorted(seeds[(env, K)])
            have = lambda s: [R for R in Rs if (s, env, K, R) in X]   # DR is missing where it was paused (item 191)
            cell = lambda s: f"{np.mean([t for R in have(s) for t, _ in X[(s, env, K, R)].values()]):.0f}" if have(s) else "–"
            t1 = lambda s: (f"{np.mean([np.mean([u for _, u in X[(s, env, K, R)].values()]) for R in have(s)]):.0f}"
                            if have(s) else "–")
            print(f"| {env} ({RANGE[env]}) | k{K} | " + " | ".join(cell(s) for s, _ in SCHEMES)
                  + f" | {t1('LMD')} / {t1('CP')} / {t1('DR')} / {t1('DN')} | ({len(Rs)})")
    print("\nChênh ghép cặp so với LM-Tour (s, âm là LM-Tour nhanh hơn), ± nửa khoảng tin cậy 95 % theo trung bình từng "
          "seed; ngoặc: % lượt bốc LM-Tour nhanh hơn.\n")
    pairs = (("CP", "CHORD"), ("DR", "DTSP-N + River"), ("DN", "FC + DTSP-N"))
    dl = ["| kênh | bản đồ | " + " | ".join(f"LM − ({n})" for _, n in pairs) + " | (DTSP-N + River) − (FC + DTSP-N) |",
          "|---|---|" + "---|" * (len(pairs) + 1)]

    def diff(p, q, env, K, Rs):
        Rs = [R for R in Rs if (p, env, K, R) in X and (q, env, K, R) in X]
        if not Rs and "DR" in (p, q) and ("DR", env, K) in E:   # estimate against estimate (or DN, which has no River)
            a = E[(p, env, K)] if p != "DN" else {x: t for x, (t, _) in X[("DN", env, K, 1)].items()}
            b = E[(q, env, K)] if q != "DN" else {x: t for x, (t, _) in X[("DN", env, K, 1)].items()}
            v = np.array([a[x] - b[x] for x in a])
            return f"{v.mean():+.0f}* ({100 * np.mean(v < 0):.0f} %)".replace("-", "−")
        if not Rs:
            return "–"
        per = [np.mean([X[(p, env, K, R)][x][0] - X[(q, env, K, R)][x][0] for x in X[(p, env, K, R)]]) for R in Rs]
        allv = [X[(p, env, K, R)][x][0] - X[(q, env, K, R)][x][0] for R in Rs for x in X[(p, env, K, R)]]
        hw = T975.get(len(Rs) - 1, 1.96) * np.std(per, ddof=1) / math.sqrt(len(Rs)) if len(Rs) > 1 else float("nan")
        pm = f" ± {hw:.0f}" if len(Rs) > 1 else ""   # one seed: no interval over seeds yet
        return f"{np.mean(per):+.0f}{pm} ({100 * np.mean(np.array(allv) < 0):.0f} %)".replace("-", "−")
    for env in ENVS:
        for K in MAPS:
            if (env, K) not in seeds:
                continue
            Rs = sorted(seeds[(env, K)])
            dl.append(f"| {env} | k{K} | " + " | ".join(diff("LMD", q, env, K, Rs) for q, _ in pairs)
                      + f" | {diff('DR', 'DN', env, K, Rs)} |")
    print("\n".join(dl))
    if a.results:
        done = len(glob.glob(f"{HERE}/score/R*/*-k*/done"))
        when = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        block = (f"<!-- campaign4:begin (table.py --results) -->\nCập nhật {when}: {done}/120 tác vụ xong "
                 f"({len(seeds)}/12 ô có ít nhất một seed).\n\n" + "\n".join(gl) + "\n\nChênh ghép cặp (s; âm là phương án "
                 "đầu nhanh hơn; ± nửa khoảng tin cậy 95 % theo trung bình từng seed, khi đã có từ 2 seed). Ngoặc là % lượt "
                 "bốc phương án đầu nhanh hơn hẳn, các lượt còn lại phần lớn là hoà.\n\n" + "\n".join(dl)
                 + "\n<!-- campaign4:end -->")
        txt = open(a.results).read()
        i, j = txt.index("<!-- campaign4:begin"), txt.index("<!-- campaign4:end -->") + len("<!-- campaign4:end -->")
        open(a.results, "w").write(txt[:i] + block + txt[j:])


if __name__ == "__main__":
    main()
