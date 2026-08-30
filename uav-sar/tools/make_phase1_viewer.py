"""Visualise the Phase 1 command changes: lane ownership, and the phase gate.

Two things need to be visible and neither shows up in a plain replay:

  * WHO SWEPT WHAT. Nodes are coloured by which fixed-wing UAV cued them, with
    a third colour for nodes cued by BOTH -- that third colour is the waste the
    lane split is meant to remove, so it has to be a colour and not a number.
  * WHEN EACH TEAM WORKED. A timeline per UAV, with the phase gate marked, so
    "the rotary team waits for the fixed-wing team" is something you can see
    rather than something you have to take on trust.

    python3 tools/make_phase1_viewer.py OUT.html LABEL=RUNDIR [LABEL=RUNDIR ...]
"""
import csv, math, os, re, sys, json

RC = 50.0

def load(run):
    m = list(csv.DictReader(open(os.path.join(run, "metrics.csv"))))[0]
    n, sp = int(m["gridSize"]), float(m["gridSpacing"])
    sensors = [(i * sp, j * sp) for i in range(n) for j in range(n)]
    fast, data, tmax = {}, {}, 0.0
    for r in csv.DictReader(open(os.path.join(run, "trajectories.csv"))):
        t, u = float(r["t"]), r["uavId"]
        tmax = max(tmax, t)
        (fast if r["role"] == "FAST" else data).setdefault(u, []).append(
            (t, float(r["x"]), float(r["y"])))
    ev = list(csv.DictReader(open(os.path.join(run, "events.csv"))))

    # which FAST UAV(s) ever came within RC of each node
    owners = []
    fk = sorted(fast)
    for sx, sy in sensors:
        who = 0
        for bit, u in enumerate(fk):
            if any((x - sx) ** 2 + (y - sy) ** 2 <= RC * RC for _, x, y in fast[u]):
                who |= (1 << bit)
        owners.append(who)

    # per-UAV working interval, and when each team is actually over the field
    spans = []
    for role, tracks in (("FAST", fast), ("DATA", data)):
        for u in sorted(tracks):
            pts = tracks[u]
            moving = [t for t, x, y in pts if -100 <= x <= 560 and -100 <= y <= 560]
            spans.append({"role": role, "uav": u,
                          "t0": pts[0][0], "t1": pts[-1][0],
                          "f0": min(moving) if moving else None,
                          "f1": max(moving) if moving else None})
    gates = [float(r["t"]) for r in ev if r["event"] == "gate_open"]
    victims = [(float(r["x"]), float(r["y"])) for r in ev if r["event"] == "victim"]
    clutter = [(float(r["x"]), float(r["y"])) for r in ev if r["event"] == "clutter"]

    both = sum(1 for w in owners if bin(w).count("1") > 1)
    cov = sum(1 for w in owners if w)
    per = [sum(1 for w in owners if w & (1 << b)) for b in range(len(fk))]
    dist = {}
    for tracks in (fast, data):
        for u, pts in tracks.items():
            dist[u] = sum(math.hypot(pts[i][1] - pts[i-1][1], pts[i][2] - pts[i-1][2])
                          for i in range(1, len(pts)))
    return {
        "sensors": sensors, "owners": owners, "nfast": len(fk),
        "fast": [[[round(x, 1), round(y, 1)] for _, x, y in fast[u]] for u in fk],
        "data": [[[round(x, 1), round(y, 1)] for _, x, y in data[u]] for u in sorted(data)],
        "spans": spans, "gates": gates, "victims": victims, "clutter": clutter,
        "tmax": tmax,
        "stat": {
            "both_pct": 100.0 * both / len(sensors),
            "cov_pct": 100.0 * cov / len(sensors),
            "imbal_pct": (100.0 * abs(per[0] - per[1]) / len(sensors)) if len(per) > 1 else 0.0,
            "fast_km": sum(dist[u] for u in fk) / 1000.0,
            "loc": int(m["victimsLocated"]), "vic": int(m["victimCount"]),
            "wrong": int(m["wrongFixes"]),
            "kJ": float(m["uavEnergyJ"]) / 1000.0,
            "tfix": float(m["timeToFixAtBS_s"]),
        },
    }

PAGE = """<title>Phase 1 Lane Command</title>
<style>
:root{--bg:#f6f7f9;--panel:#fff;--ink:#12151a;--dim:#5b6472;--line:#dfe3e9;
--field:#eaeff6;--u1:#2f6fd0;--u2:#1f9d6b;--dup:#d4761f;--none:#c2410c;
--data:#8b5cf6;--good:#1f9d6b;--warn:#c2410c;--grid:#cdd5e0}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
--bg:#0e1116;--panel:#161b22;--ink:#e6edf3;--dim:#9198a1;--line:#2a313a;
--field:#1a212a;--u1:#5aa0ff;--u2:#3fd39a;--dup:#f0a24a;--none:#f97362;
--data:#a78bfa;--good:#3fd39a;--warn:#f97362;--grid:#39424e}}
:root[data-theme="dark"]{--bg:#0e1116;--panel:#161b22;--ink:#e6edf3;--dim:#9198a1;
--line:#2a313a;--field:#1a212a;--u1:#5aa0ff;--u2:#3fd39a;--dup:#f0a24a;--none:#f97362;
--data:#a78bfa;--good:#3fd39a;--warn:#f97362;--grid:#39424e}
*{box-sizing:border-box}
body{margin:0;padding:26px 20px 46px;background:var(--bg);color:var(--ink);
font:15px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:1200px;margin:0 auto}
h1{font-size:23px;margin:0 0 5px;letter-spacing:-.01em}
h3{font-size:15.5px;margin:32px 0 10px}
.sub{color:var(--dim);margin:0 0 6px;font-size:13.5px}
.note{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--dup);
border-radius:8px;padding:11px 14px;margin:16px 0 24px;font-size:13.5px;color:var(--dim)}
.note b{color:var(--ink)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:18px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px}
.card h2{font-size:14.5px;margin:0 0 2px}
.card .tag{font-size:12.5px;color:var(--dim);margin:0 0 10px}
svg{width:100%;height:auto;display:block;border-radius:6px}
table{width:100%;border-collapse:collapse;margin-top:11px;font-size:13px}
td{padding:3.5px 0;border-bottom:1px solid var(--line)}
td:last-child{text-align:right;font-variant-numeric:tabular-nums;font-weight:600}
tr:last-child td{border-bottom:0}
.k{color:var(--dim);font-weight:400}
.hi td:last-child{color:var(--good)}
.lo td:last-child{color:var(--warn)}
.legend{display:flex;gap:15px;flex-wrap:wrap;margin:20px 0 4px;font-size:13px;color:var(--dim)}
.legend i{display:inline-block;width:9px;height:9px;border-radius:50%;
vertical-align:middle;margin-right:6px}
.legend i.l{width:15px;height:3px;border-radius:2px}
.scroll{overflow-x:auto}
table.big{font-size:13px;min-width:640px;border-collapse:collapse}
table.big th{text-align:right;padding:6px 10px;border-bottom:1px solid var(--line);
color:var(--dim);font-weight:500;white-space:nowrap}
table.big th:first-child{text-align:left}
table.big td{padding:6px 10px;text-align:right;white-space:nowrap;border-bottom:1px solid var(--line)}
table.big td:first-child{text-align:left;font-weight:500}
.best{color:var(--good);font-weight:700}
</style>
<div class="wrap">
<h1>Phase 1 — chỉ huy đội cánh cố định</h1>
<p class="sub">24×24 nút · 460 × 460 m · 2 FAST + 2 DATA · bán kính quảng bá 50 m</p>
<div class="note"><b>Đây là replay ns-3 thật</b> (không phải mô hình quy hoạch).
Mỗi nút được tô theo <b>UAV cánh cố định nào đã rải cue cho nó</b>; màu cam là nút được
<b>cả hai</b> UAV phủ — đó chính là phần công bị làm hai lần mà việc chia luống nhằm bỏ đi.</div>
__CARDS__
<div class="legend">
<span><i style="background:var(--u1)"></i>chỉ FAST-1 phủ</span>
<span><i style="background:var(--u2)"></i>chỉ FAST-2 phủ</span>
<span><i style="background:var(--dup)"></i><b>cả hai phủ — trùng việc</b></span>
<span><i style="background:var(--none)"></i>không UAV nào phủ</span>
<span><i class="l" style="background:var(--data)"></i>đội DATA (cánh quay)</span>
</div>
<h3>Ai làm gì, lúc nào</h3>
<p class="sub" style="margin-bottom:10px">Thanh đậm = UAV đang ở trên vùng tìm kiếm.
Vạch đứng = thời điểm cổng pha mở (đội DATA bắt đầu Phase 2).</p>
__TIMELINE__
<h3>Tổng hợp — 8 hạt giống mỗi nhánh</h3>
<div class="scroll">__SUMMARY__</div>
</div>
"""

def svg_map(d, w=430):
    pad = 150.0
    ax0, ax1, ay0, ay1 = -pad - 110, 460 + pad, -pad - 110, 460 + pad
    sc = w / (ax1 - ax0); h = (ay1 - ay0) * sc
    P = lambda x, y: ((x - ax0) * sc, h - (y - ay0) * sc)
    o = [f'<svg viewBox="0 0 {w:.0f} {h:.0f}" role="img">']
    fx, fy = P(0, 460)
    o.append(f'<rect x="{fx:.1f}" y="{fy:.1f}" width="{460*sc:.1f}" height="{460*sc:.1f}" '
             f'fill="var(--field)"/>')
    col = {0: "var(--none)", 1: "var(--u1)", 2: "var(--u2)", 3: "var(--dup)"}
    for (sx, sy), who in zip(d["sensors"], d["owners"]):
        px, py = P(sx, sy)
        r = 2.6 if who == 3 or who == 0 else 1.7
        o.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r}" fill="{col.get(who,"var(--dup)")}"/>')
    for arr, c, wdt in ((d["data"], "var(--data)", 1.0), (d["fast"], None, 1.5)):
        for i, tr in enumerate(arr):
            cc = c or (f'var(--u{i+1})' if i < 2 else "var(--dim)")
            pts = " ".join(f"{a:.1f},{b:.1f}" for a, b in (P(x, y) for x, y in tr[::2]))
            o.append(f'<polyline points="{pts}" fill="none" stroke="{cc}" '
                     f'stroke-width="{wdt}" opacity="{0.55 if c else 0.95}"/>')
    for vx, vy in d["victims"]:
        px, py = P(vx, vy)
        o.append(f'<path d="M{px-5:.1f},{py:.1f}L{px:.1f},{py-5:.1f}L{px+5:.1f},{py:.1f}'
                 f'L{px:.1f},{py+5:.1f}Z" fill="var(--ink)" stroke="var(--panel)"/>')
    for cx, cy in d["clutter"]:
        px, py = P(cx, cy)
        o.append(f'<rect x="{px-3:.1f}" y="{py-3:.1f}" width="6" height="6" '
                 f'fill="none" stroke="var(--dim)" stroke-width="1.3"/>')
    o.append("</svg>")
    return "".join(o)

def card(label, tag, d, hi=()):
    s = d["stat"]
    rows = [("nút bị phủ hai lần", f'{s["both_pct"]:.1f} %', "both"),
            ("lệch tải giữa 2 UAV", f'{s["imbal_pct"]:.1f} %', "imbal"),
            ("phủ nút (FAST)", f'{s["cov_pct"]:.1f} %', "cov"),
            ("quãng đường FAST", f'{s["fast_km"]:.1f} km', "km"),
            ("nạn nhân định vị", f'{s["loc"]}/{s["vic"]}', "loc"),
            ("toạ độ sai người", f'{s["wrong"]}', "wrong"),
            ("thời gian tới toạ độ", f'{s["tfix"]:.0f} s', "tfix")]
    body = "".join(f'<tr class="{"hi" if k in hi else ""}"><td class="k">{a}</td>'
                   f'<td>{b}</td></tr>' for a, b, k in rows)
    return (f'<div class="card"><h2>{label}</h2><p class="tag">{tag}</p>'
            f'{svg_map(d)}<table>{body}</table></div>')

def timeline(runs):
    tmax = max(d["tmax"] for _, _, d in runs) or 1.0
    W, RH = 900, 20
    out = ['<div class="scroll">']
    for label, _, d in runs:
        rows = d["spans"]
        h = len(rows) * RH + 34
        o = [f'<svg viewBox="0 0 {W} {h}" role="img" style="min-width:640px">']
        o.append(f'<text x="0" y="12" font-size="12.5" fill="var(--ink)" '
                 f'font-weight="600">{label}</text>')
        for i, sp in enumerate(rows):
            y = 24 + i * RH
            x0, x1 = 90 + 780 * sp["t0"] / tmax, 90 + 780 * sp["t1"] / tmax
            c = "var(--u1)" if sp["role"] == "FAST" and i == 0 else \
                "var(--u2)" if sp["role"] == "FAST" else "var(--data)"
            o.append(f'<text x="0" y="{y+11}" font-size="11" fill="var(--dim)">'
                     f'{sp["role"]}-{sp["uav"]}</text>')
            o.append(f'<rect x="{x0:.1f}" y="{y+4:.0f}" width="{max(1,x1-x0):.1f}" height="10" '
                     f'rx="3" fill="{c}" opacity="0.25"/>')
            if sp["f0"] is not None:
                a = 90 + 780 * sp["f0"] / tmax; b = 90 + 780 * sp["f1"] / tmax
                o.append(f'<rect x="{a:.1f}" y="{y+4:.0f}" width="{max(1,b-a):.1f}" '
                         f'height="10" rx="3" fill="{c}"/>')
        for g in d["gates"]:
            gx = 90 + 780 * g / tmax
            o.append(f'<line x1="{gx:.1f}" y1="18" x2="{gx:.1f}" y2="{h-14}" '
                     f'stroke="var(--dup)" stroke-width="1.6" stroke-dasharray="3,3"/>')
            o.append(f'<text x="{gx+4:.1f}" y="{h-4}" font-size="10.5" '
                     f'fill="var(--dup)">cổng mở {g:.0f}s</text>')
        o.append(f'<text x="{W-40}" y="{h-4}" font-size="10.5" fill="var(--dim)">'
                 f'{tmax:.0f}s</text></svg>')
        out.append("".join(o))
    out.append("</div>")
    return "".join(out)

def main():
    out_path, args = sys.argv[1], sys.argv[2:]
    runs = []
    for a in args:
        label, run = a.split("=", 1)
        runs.append((label, run, load(run)))
    cards = ['<div class="grid">']
    for i, (label, run, d) in enumerate(runs):
        hi = ("both", "imbal", "km", "loc") if i == len(runs) - 1 else ()
        cards.append(card(label, os.path.basename(run), d, hi))
    cards.append("</div>")
    summary = os.environ.get("PHASE1_SUMMARY", "<p class='sub'>(chưa có)</p>")
    html = (PAGE.replace("__CARDS__", "".join(cards))
                .replace("__TIMELINE__", timeline(runs))
                .replace("__SUMMARY__", summary))
    open(out_path, "w").write(html)
    print(f"{out_path}  ({len(html)//1024} KB, {len(runs)} runs)")

if __name__ == "__main__":
    main()
