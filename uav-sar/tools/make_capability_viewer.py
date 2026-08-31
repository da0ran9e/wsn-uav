"""Show what the capability-aware sweep is actually doing.

Three things have to be visible at once, because the argument is about their
interaction and any one of them alone is misleading:

  * WHERE THE CAPABILITY IS. Nodes are drawn by screening capability
    (observation x compute), so the dark ones are nodes worth flying over and
    the hollow ones are nodes that cannot produce evidence no matter what.
  * WHICH UAV TOOK WHICH WORK, and how even that came out on BOTH axes --
    capability and flight effort. Two bars per UAV, because balancing one while
    ignoring the other is the failure mode this replaced.
  * WHAT WAS SKIPPED. Cell-based planning deliberately does not fly over
    everything; the nodes it passed on have to be shown, not hidden.

    python3 tools/make_capability_viewer.py OUT.html LABEL=RUNDIR [...]
"""
import csv, glob, math, os, sys

RC = 50.0

def seg_dist(px, py, ax, ay, bx, by):
    vx, vy = bx - ax, by - ay
    L2 = vx * vx + vy * vy
    t = ((px - ax) * vx + (py - ay) * vy) / L2 if L2 > 0 else 0.0
    t = max(0.0, min(1.0, t))
    return math.hypot(px - (ax + t * vx), py - (ay + t * vy))

def load(run):
    caps = list(csv.DictReader(open(os.path.join(run, "capabilities.csv"))))
    m = list(csv.DictReader(open(os.path.join(run, "metrics.csv"))))[0]
    tracks, prev, dist = {}, {}, {}
    for r in csv.DictReader(open(os.path.join(run, "trajectories.csv"))):
        if r["role"] != "FAST":
            continue
        u, x, y = r["uavId"], float(r["x"]), float(r["y"])
        tracks.setdefault(u, []).append((x, y))
        if u in prev:
            dist[u] = dist.get(u, 0.0) + math.hypot(x - prev[u][0], y - prev[u][1])
        prev[u] = (x, y)
    uavs = sorted(tracks)
    owner, capu = [], {u: 0.0 for u in uavs}
    for c in caps:
        cx, cy = float(c["x"]), float(c["y"])
        who = -1
        for ui, u in enumerate(uavs):
            pts = tracks[u]
            hit = any(seg_dist(cx, cy, pts[k-1][0], pts[k-1][1], pts[k][0], pts[k][1]) <= RC
                      for k in range(1, len(pts)))
            if hit:
                if who < 0:
                    who = ui
                    capu[u] += float(c["screening"])
                else:
                    who = 99          # more than one UAV
        owner.append(who)
    ev = list(csv.DictReader(open(os.path.join(run, "events.csv"))))
    tot = sum(float(c["screening"]) for c in caps) or 1.0
    seen = sum(float(c["screening"]) for c, w in zip(caps, owner) if w >= 0)
    return dict(
        caps=[(float(c["x"]), float(c["y"]), float(c["screening"])) for c in caps],
        owner=owner, uavs=uavs,
        tracks=[[(round(x, 1), round(y, 1)) for x, y in tracks[u][::2]] for u in uavs],
        capu=[capu[u] for u in uavs], effu=[dist[u] / 1000.0 for u in uavs],
        victims=[(float(r["x"]), float(r["y"])) for r in ev if r["event"] == "victim"],
        cap_cov=100.0 * seen / tot,
        skipped=sum(1 for w in owner if w < 0),
        km=sum(dist.values()) / 1000.0,
        loc=int(m["victimsLocated"]), vic=int(m["victimCount"]),
        kJ=float(m["uavEnergyJ"]) / 1000.0, tfix=float(m["timeToFixAtBS_s"]),
    )

PAL = ["#2f6fd0", "#1f9d6b", "#b45cc4", "#d4761f", "#0e8f9c"]

PAGE = """<title>Capability-Aware Sweep</title>
<style>
:root{--bg:#f6f7f9;--panel:#fff;--ink:#12151a;--dim:#5b6472;--line:#dfe3e9;
--field:#eaeff6;--skip:#c2410c;--dup:#8a6d3b;--good:#1f9d6b;--warn:#c2410c}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
--bg:#0e1116;--panel:#161b22;--ink:#e6edf3;--dim:#9198a1;--line:#2a313a;
--field:#1a212a;--skip:#f97362;--dup:#c8a25a;--good:#3fd39a;--warn:#f97362}}
:root[data-theme="dark"]{--bg:#0e1116;--panel:#161b22;--ink:#e6edf3;--dim:#9198a1;
--line:#2a313a;--field:#1a212a;--skip:#f97362;--dup:#c8a25a;--good:#3fd39a;--warn:#f97362}
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
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px}
.card h2{font-size:14.5px;margin:0 0 2px}
.card .tag{font-size:12.5px;color:var(--dim);margin:0 0 10px}
svg{width:100%;height:auto;display:block;border-radius:6px}
table{width:100%;border-collapse:collapse;margin-top:10px;font-size:13px}
td{padding:3.5px 0;border-bottom:1px solid var(--line)}
td:last-child{text-align:right;font-variant-numeric:tabular-nums;font-weight:600}
tr:last-child td{border-bottom:0}
.k{color:var(--dim);font-weight:400}
.bars{margin-top:10px}
.barrow{display:flex;align-items:center;gap:7px;font-size:11.5px;color:var(--dim);
margin-bottom:3px}
.barrow span.l{width:52px;flex:none}
.bar{height:9px;border-radius:3px;flex:none}
.bg{background:var(--line);height:9px;border-radius:3px;flex:1;overflow:hidden}
.legend{display:flex;gap:15px;flex-wrap:wrap;margin:20px 0 4px;font-size:13px;color:var(--dim)}
.legend i{display:inline-block;width:10px;height:10px;border-radius:50%;
vertical-align:middle;margin-right:6px}
.scroll{overflow-x:auto}
table.big{font-size:13px;min-width:680px;border-collapse:collapse}
table.big th{text-align:right;padding:6px 10px;border-bottom:1px solid var(--line);
color:var(--dim);font-weight:500;white-space:nowrap}
table.big th:first-child{text-align:left}
table.big td{padding:6px 10px;text-align:right;white-space:nowrap;
border-bottom:1px solid var(--line)}
table.big td:first-child{text-align:left;font-weight:500}
.best{color:var(--good);font-weight:700}
</style>
<div class="wrap">
<h1>Phase 1 — quét theo năng lực, không theo nút</h1>
<p class="sub">Nút đậm = năng lực sàng lọc cao (quan sát × tính toán) · nút rỗng = không camera, bay qua cũng vô ích</p>
<div class="note"><b>Replay ns-3.</b> Mỗi nút được tô theo <b>UAV cánh cố định nào đã gieo cue cho nó</b>.
Nút <b style="color:var(--skip)">đỏ</b> là nút <b>không UAV nào bay qua</b> — với quét theo ô thì đó là
lựa chọn có chủ ý, không phải lỗi. Hai thanh dưới mỗi bản đồ là <b>năng lực</b> và <b>công bay</b> của
từng UAV: cân một cái mà bỏ cái kia chính là lỗi mà bản này sửa.</div>
__CARDS__
<div class="legend">__LEG__
<span><i style="background:var(--skip)"></i>không được bay qua</span>
<span><i style="background:var(--dup)"></i>nhiều UAV cùng phủ</span>
</div>
__EXTRA__
</div>
"""

def svg_map(d, w=420):
    pad = 140.0
    ax0, ax1, ay0, ay1 = -pad - 100, 460 + pad, -pad - 100, 460 + pad
    sc = w / (ax1 - ax0); h = (ay1 - ay0) * sc
    P = lambda x, y: ((x - ax0) * sc, h - (y - ay0) * sc)
    o = [f'<svg viewBox="0 0 {w:.0f} {h:.0f}" role="img">']
    fx, fy = P(0, 460)
    o.append(f'<rect x="{fx:.1f}" y="{fy:.1f}" width="{460*sc:.1f}" '
             f'height="{460*sc:.1f}" fill="var(--field)"/>')
    for (x, y, sgn), who in zip(d["caps"], d["owner"]):
        px, py = P(x, y)
        r = 1.1 + 2.6 * min(1.0, sgn)          # size = capability
        if who < 0:
            o.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{max(r,1.8):.1f}" '
                     f'fill="none" stroke="var(--skip)" stroke-width="1.1"/>')
        elif who == 99:
            o.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:.1f}" fill="var(--dup)"/>')
        else:
            col = PAL[who % len(PAL)]
            if sgn <= 0.01:
                o.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="1.6" fill="none" '
                         f'stroke="{col}" stroke-width="0.9" opacity="0.55"/>')
            else:
                o.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:.1f}" fill="{col}"/>')
    for i, tr in enumerate(d["tracks"]):
        pts = " ".join(f"{a:.1f},{b:.1f}" for a, b in (P(x, y) for x, y in tr))
        o.append(f'<polyline points="{pts}" fill="none" stroke="{PAL[i%len(PAL)]}" '
                 f'stroke-width="1.4" opacity="0.9"/>')
    for vx, vy in d["victims"]:
        px, py = P(vx, vy)
        o.append(f'<path d="M{px-5:.1f},{py:.1f}L{px:.1f},{py-5:.1f}L{px+5:.1f},{py:.1f}'
                 f'L{px:.1f},{py+5:.1f}Z" fill="var(--ink)" stroke="var(--panel)"/>')
    o.append("</svg>")
    return "".join(o)

def bars(d):
    def row(label, vals, unit):
        mx = max(vals) or 1.0
        out = []
        for i, v in enumerate(vals):
            out.append(f'<div class="barrow"><span class="l">{label if i==0 else ""}</span>'
                       f'<div class="bg"><div class="bar" style="width:{100*v/mx:.0f}%;'
                       f'background:{PAL[i%len(PAL)]}"></div></div>'
                       f'<span style="width:52px;text-align:right">{v:.2f}{unit}</span></div>')
        return "".join(out)
    def imb(v):
        return 100.0 * (max(v) - min(v)) / (sum(v) / len(v)) if v and sum(v) else 0.0
    return (f'<div class="bars">{row("năng lực", d["capu"], "")}'
            f'{row("công bay", d["effu"], " km")}</div>'
            f'<table><tr><td class="k">lệch năng lực</td><td>{imb(d["capu"]):.1f} %</td></tr>'
            f'<tr><td class="k">lệch công bay</td><td>{imb(d["effu"]):.1f} %</td></tr>'
            f'<tr><td class="k">năng lực được phủ</td><td>{d["cap_cov"]:.1f} %</td></tr>'
            f'<tr><td class="k">nút bỏ qua</td><td>{d["skipped"]}</td></tr>'
            f'<tr><td class="k">tổng quãng đường</td><td>{d["km"]:.1f} km</td></tr>'
            f'<tr><td class="k">nạn nhân định vị</td><td>{d["loc"]}/{d["vic"]}</td></tr>'
            f'<tr><td class="k">thời gian tới toạ độ</td><td>'
            f'{("%.0f s" % d["tfix"]) if d["tfix"]>0 else "—"}</td></tr></table>')

def main():
    out_path, args = sys.argv[1], sys.argv[2:]
    runs = [(a.split("=", 1)[0], load(a.split("=", 1)[1])) for a in args]
    cards = ['<div class="grid">']
    for label, d in runs:
        cards.append(f'<div class="card"><h2>{label}</h2>'
                     f'<p class="tag">{len(d["uavs"])} UAV cánh cố định</p>'
                     f'{svg_map(d)}{bars(d)}</div>')
    cards.append("</div>")
    nmax = max(len(d["uavs"]) for _, d in runs)
    leg = "".join(f'<span><i style="background:{PAL[i%len(PAL)]}"></i>FAST-{i+1}</span>'
                  for i in range(nmax))
    html = (PAGE.replace("__CARDS__", "".join(cards)).replace("__LEG__", leg)
                .replace("__EXTRA__", os.environ.get("CAP_EXTRA", "")))
    open(out_path, "w").write(html)
    print(f"{out_path}  ({len(html)//1024} KB, {len(runs)} runs)")

if __name__ == "__main__":
    main()
