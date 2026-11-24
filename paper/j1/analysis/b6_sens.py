"""K9 step B6 (rest): device tiers and node density at model level (paper/j1/PLAN-K9-DATA-vi.md, K9-PARAMS-vi.md).

    python3 b6_sens.py WORK B5_CSV HIGH_MD OUT_PREFIX

WORK: the C4 k8 mission folder (nodes, gateways). B5_CSV: b5_phase2.py output (index size per set and rho).
HIGH_MD: cc_select.py output at high rho (coverage of the all-cells set gives the largest feasible rho).

Density. Every load in B1, B3 and every index in B5 is linear in rho * fcam * n_c, so a map thinned to a share p of
its nodes behaves as the full map at rho * p, as long as the cells and gateway pairs stay (K10 has 7-10 nodes per cell at
400 and 280 nodes/km^2, so they do). The check: binomial thinning of every cell's node count, then the busiest medium of
the B3 sets against p times its value on the full map. River's own times change with density and need K10's ns-3 maps.

Device tiers (K9-PARAMS section 3). Option D3 puts feature extraction at the camera node and only a vector search at the
AI node, so per tier: the camera's busy share embedding every passer-by, the AI node's time to embed the reference set
and search its index (first pass L = 3 images, V1 L = 20), and the index size against the device's memory.
"""
import csv, math, os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE]
from bg_load import TAU, Cluster  # noqa: E402

DENS = {816: 1.0, 400: 400 / 816, 280: 280 / 816}
D3_BYTES, DIM, BW = 528, 512, 4e9   # INT8 vector + 16 B; index read at 4 GB/s (Pi 5 class, estimate)
# per-image embedding time (s): camera tiers embed one crop per passer-by, AI tiers embed the reference images
TIERS = [  # name, embed s per image, memory for the index (bytes), source
    ("T0 MCU (ESP32-S3)", 0.27, 8e6, "face embedding 255-287 ms on ESP32-S3 [repo]; PSRAM 8 MB"),
    ("T0 MCU (STM32N6)", 0.01, 4e6, "OSNet x0.25 extrapolated 3-10 ms [estimate]; 4.2 MB RAM"),
    ("T1 camera SoC", 0.01, 1e9, "about 100 crops/s [repo]"),
    ("T2 Pi 5 CPU", 1 / 12.6, 4e9, "ResNet-50 INT8 12.6/s (l1_mission.py); OSNet x0.25 faster"),
    ("T2 Pi 5 + Hailo-8L", 1 / 257.6, 4e9, "257.6/s (l1_mission.py)"),
]


def thin_check(W, crits_files, p, seed=1):
    out = []
    import json
    K = json.load(open(f"{W}/map.json"))["clusters"]
    cls = {k: Cluster(W, k) for k in range(1, K + 1)}
    for name, f in crits_files:
        S = {(int(r["q"]), int(r["r"])) for r in csv.DictReader(open(f))}
        full, thin = 0.0, 0.0
        rng = random.Random(seed)
        for k, c in cls.items():
            Sk = sorted(h for h in S if h in c.n)
            fr, _, _ = c.load(Sk)
            full = max(full, max(fr.values()) * TAU)
            n0 = dict(c.n)
            for h in c.cells:
                c.n[h] = max(1, sum(rng.random() < p for _ in range(n0[h])))
            fr, _, _ = c.load(Sk)
            thin = max(thin, max(fr.values()) * TAU)
            c.n.update(n0)
        out.append((name, len(S), thin / full))
    return out


def main():
    W, b5, high, out = sys.argv[1:5]
    data = os.path.dirname(b5)
    sets = [(t, f"{data}/crit-r100-R1-k8-s1-u0.1-{t}.csv") for t in ("rho20", "rho100", "rho200")]
    # largest feasible rho with an AI node in every cell (coverage at the all-cells set), fcam 0.3
    cap = {}
    for line in open(high):
        m = re.match(r"\| ([\d.]+) \| (\d+) \| 617 \| \d+ \| ([\d.]+) \|", line)
        if m:
            cap.setdefault(float(m.group(1)), []).append((float(m.group(3)), float(m.group(2)) * float(m.group(3))))
    rho_all = {u: max(v)[1] for u, v in cap.items()}   # the largest coverage: least rounding
    b5rows = list(csv.DictReader(open(b5)))
    L = []
    L.append("# K9 B6: node density and device tiers (model level, k8 r100)\n")
    L.append("## Density\n\nLoads and indexes scale with rho x fcam x density, so density d at rho equals the 816 nodes/km^2 "
             "map at rho x d / 816. Largest rho with an AI node in every cell (617 AI cells), fcam 0.3:\n")
    L.append("| budget | 816 | 400 | 280 |\n|---|---|---|---|")
    for u, r in sorted(rho_all.items()):
        L.append(f"| {u:g} | {r:.0f} | {r / DENS[400]:.0f} | {r / DENS[280]:.0f} |")
    L.append("\nThe B3 sets (chosen at 816 for rho 20 / 100 / 200, budget 0.1) serve, at 400 and 280 nodes/km^2:\n")
    L.append("| set | 816 | 400 | 280 |\n|---|---|---|---|")
    for t, _ in sets:
        r = float(t[3:])
        L.append(f"| {t} | {r:.0f} | {r / DENS[400]:.0f} | {r / DENS[280]:.0f} |")
    L.append("\nCheck by binomial thinning (seed 1): busiest medium on the thinned map / (p x full map); 1 is exact scaling.\n")
    L.append("| density | set | AI cells | ratio |\n|---|---|---|---|")
    for d in (400, 280):
        for name, n, r in thin_check(W, sets, DENS[d]):
            L.append(f"| {d} | {name} | {n} | {r / DENS[d]:.3f} |")
    L.append("\n## Device tiers (option D3)\n")
    L.append("Camera: busy share embedding one crop per passer-by at rho = 200 and 3 700 people/h. AI node: reference "
             "embedding plus search of the largest B5 index (Algorithm 3 at rho 200, fcam 0.3, 2 h), first pass L = 3 "
             "and V1 L = 20; the V1 visit itself is 78 s. Index bytes against the device memory.\n")
    big = max(int(r["index_max"]) for r in b5rows)
    small = min(int(r["index_max"]) for r in b5rows if r["feasible"] == "1")
    L.append(f"Largest index {big} vectors ({big * D3_BYTES / 1e6:.0f} MB); smallest feasible {small} "
             f"({small * D3_BYTES / 1e6:.1f} MB).\n")
    L.append("| tier | camera busy, rho 200 | camera busy, rho 3 700 | AI query L=3 (s) | V1 L=20 (s) | "
             "largest index fits | smallest fits | source |\n|---|---|---|---|---|---|---|---|")
    search = big * DIM / BW
    for name, e, mem, src in TIERS:
        L.append(f"| {name} | {200 / 3600 * e:.2%} | {3700 / 3600 * e:.1%} | {3 * e + search:.2f} | {20 * e + search:.2f} | "
                 f"{'yes' if big * D3_BYTES <= mem else 'no'} | {'yes' if small * D3_BYTES <= mem else 'no'} | {src} |")
    open(out + ".md", "w").write("\n".join(L) + "\n")
    print(open(out + ".md").read())


if __name__ == "__main__":
    main()
