"""Phase 1: score sweep plans by flying them, and draw the comparison.

Every number here comes from tools/fly_sim.py -- the guidance law the simulation
itself uses -- so the plans differ only in their waypoint list. Two earlier
geometric approximations of the same comparison were wrong in opposite
directions (see fly_sim.py), which is why nothing is scored analytically here.

    python3 tools/phase1_plans.py                 # table
    python3 tools/phase1_plans.py OUT.html        # table + visual comparison
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fly_sim as F
from dubins_lanes import build_lanes, lane_configs, solve_exact

# Operational geometry (gridSize 24 @ 20 m, kUavBroadcastRadiusM 50).
X0, X1, Y0, Y1 = 0.0, 460.0, 0.0, 460.0
SPACING = 50.0
RC = 50.0
CHUNK_RATE = 5.0          # 1 chunk per kDisseminateStaggerS = 0.2 s
N_CHUNKS = 30             # 8xL0(150B) + 2xL1(600B) at kChunkBytes = 91
START = (-200.0, -200.0)  # BS corner
SENSORS = [(i * 20.0, j * 20.0) for i in range(24) for j in range(24)]


def shipping_waypoints(lanes, turn_out):
    """What BuildMission() emits: lanes in order, two turn waypoints outside."""
    wps, forward = [], True
    for idx, (xa, xb, yy) in enumerate(lanes):
        s0, s1 = (xa, xb) if forward else (xb, xa)
        wps += [(s0, yy), (s1, yy)]
        if idx + 1 < len(lanes):
            y_next = lanes[idx + 1][2]
            out = s1 + (1.0 if forward else -1.0) * turn_out
            wps += [(out, yy), (out, y_next)]
        forward = not forward
    return wps


def dubins_waypoints(lanes, R):
    """Lane endpoints in the exactly-optimal Dubins order, no turn waypoints."""
    _, order = solve_exact(lanes, R, (START[0], START[1], math.radians(45)))
    cfg = [lane_configs(l) for l in lanes]
    wps = []
    for (i, di) in order:
        entry, exit_ = cfg[i][di]
        wps += [(entry[0], entry[1]), (exit_[0], exit_[1])]
    return wps, order


def sweeps_needed(v, cstar=1.0):
    """The worst node sits under a lane: one chord per sweep, nothing from
    the neighbouring lanes (spacing == Rc)."""
    per_pass = (2.0 * RC / v) * CHUNK_RATE
    return math.ceil(N_CHUNKS * cstar / per_pass)


def score(name, wps, v, strict=True):
    pts, length, t, reached = F.fly(wps, START, v)
    assert reached == len(wps), f"{name}: only {reached}/{len(wps)} waypoints reached"
    cov = F.covered_fraction(pts, SENSORS, RC)
    # Coverage is not a formality: above ~25 m/s the turn radius grows past what
    # the lane geometry can absorb and the aircraft starts cutting corners, so
    # nodes get missed. A plan that misses nodes has not screened them, and its
    # T_screen is not comparable -- flag it rather than average it in.
    if strict:
        assert cov > 99.0, f"{name}: coverage only {cov:.1f}% -- plan is not a sweep"
    k = sweeps_needed(v)
    return {
        "name": name, "v": v, "pts": pts, "km": length / 1000.0,
        "sweep_s": t, "in_field": F.in_field_fraction(pts, X0, X1, Y0, Y1),
        "coverage": cov, "sweeps": k, "screen_s": k * t,
    }


def build_all(speeds):
    lanes = build_lanes(X0, X1, Y0, Y1, SPACING)
    out = []
    for v in speeds:
        R = F.turn_radius(v)
        out.append(score("boustrophedon", shipping_waypoints(lanes, 1.2 * R), v))
        wps, _ = dubins_waypoints(lanes, R)
        out.append(score("dubins", wps, v))
    return lanes, out


def table(rows):
    print(f"{'plan':<15}{'v':>5}{'R':>8}{'dist':>9}{'sweep':>8}"
          f"{'in-field':>10}{'cov':>7}{'sweeps':>8}{'T_screen':>10}")
    for r in rows:
        print(f"{r['name']:<15}{r['v']:5.0f}{F.turn_radius(r['v']):7.0f}m"
              f"{r['km']:8.2f}km{r['sweep_s']:7.0f}s{r['in_field']:9.1f}%"
              f"{r['coverage']:6.0f}%{r['sweeps']:8d}{r['screen_s']:9.0f}s")


# --------------------------------------------------------------------------
# Visual comparison
# --------------------------------------------------------------------------

PAGE = """<title>Phase 1 Sweep Plans</title>
<style>
:root{--bg:#f6f7f9;--panel:#fff;--ink:#12151a;--dim:#5b6472;--line:#dfe3e9;
--field:#e8edf5;--node:#c3ccd9;--in:#2f6fd0;--out:#d4761f;--good:#1f9d6b;--warn:#c2410c}
:root:not([data-theme="light"]){@media (prefers-color-scheme:dark){
:root{--bg:#0e1116;--panel:#161b22;--ink:#e6edf3;--dim:#9198a1;--line:#2a313a;
--field:#1c232c;--node:#39424e;--in:#5aa0ff;--out:#f0a24a;--good:#3fd39a;--warn:#f97362}}}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
--bg:#0e1116;--panel:#161b22;--ink:#e6edf3;--dim:#9198a1;--line:#2a313a;
--field:#1c232c;--node:#39424e;--in:#5aa0ff;--out:#f0a24a;--good:#3fd39a;--warn:#f97362}}
:root[data-theme="dark"]{--bg:#0e1116;--panel:#161b22;--ink:#e6edf3;--dim:#9198a1;
--line:#2a313a;--field:#1c232c;--node:#39424e;--in:#5aa0ff;--out:#f0a24a;
--good:#3fd39a;--warn:#f97362}
*{box-sizing:border-box}
body{margin:0;padding:28px 20px 48px;background:var(--bg);color:var(--ink);
font:15px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:1180px;margin:0 auto}
h1{font-size:23px;margin:0 0 6px;letter-spacing:-.01em}
.sub{color:var(--dim);margin:0 0 8px;font-size:14px}
.note{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--out);
border-radius:8px;padding:12px 14px;margin:18px 0 26px;font-size:13.5px;color:var(--dim)}
.note b{color:var(--ink)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:18px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px}
.card h2{font-size:14.5px;margin:0 0 2px;letter-spacing:-.005em}
.card .tag{font-size:12.5px;color:var(--dim);margin:0 0 10px}
svg{width:100%;height:auto;display:block;border-radius:6px}
table{width:100%;border-collapse:collapse;margin-top:11px;font-size:13px}
td{padding:3.5px 0;border-bottom:1px solid var(--line)}
td:last-child{text-align:right;font-variant-numeric:tabular-nums;font-weight:600}
tr:last-child td{border-bottom:0}
.k{color:var(--dim)}
.hi td:last-child{color:var(--good)}
.lo td:last-child{color:var(--warn)}
.legend{display:flex;gap:16px;flex-wrap:wrap;margin:22px 0 4px;font-size:13px;color:var(--dim)}
.legend i{display:inline-block;width:15px;height:3px;border-radius:2px;
vertical-align:middle;margin-right:6px}
.scroll{overflow-x:auto}
h3{font-size:15px;margin:34px 0 10px}
table.big{font-size:13px;min-width:620px}
table.big th{text-align:right;padding:6px 10px;border-bottom:1px solid var(--line);
color:var(--dim);font-weight:500;white-space:nowrap}
table.big th:first-child{text-align:left}
table.big td{padding:6px 10px;text-align:right;white-space:nowrap}
table.big td:first-child{text-align:left;font-weight:500}
table.big td:last-child{text-align:right}
.best{color:var(--good);font-weight:700}
</style>
<div class="wrap">
<h1>Phase 1 — kế hoạch quét của đội cánh cố định</h1>
<p class="sub">Vùng 460 × 460 m · 576 nút · bán kính quảng bá 50 m · góc nghiêng 45°</p>
<div class="note"><b>Đây là kế hoạch bay, không phải replay ns-3.</b>
Mọi đường bay dưới đây được bay qua <b>đúng luật dẫn đường của mô phỏng</b>
(<code>ControlTick</code> + <code>FlightController::Step</code>): hướng lái liên tục về waypoint,
tốc độ lượn giới hạn ở <code>g·tan φ / v</code>, nhận waypoint khi tới gần hoặc khi đã ngang qua.
Hai kế hoạch vì thế <b>chỉ khác nhau ở danh sách waypoint</b>. Cả bốn đều phủ 100 % số nút.</div>
__CARDS__
<div class="legend">
<span><i style="background:var(--in)"></i>bay trong vùng tìm kiếm</span>
<span><i style="background:var(--out)"></i>bay ngoài vùng — chi phí quay đầu</span>
<span><i style="background:var(--node);height:7px;width:7px;border-radius:50%"></i>nút cảm biến</span>
</div>
<h3>Thời gian sàng lọc theo tốc độ</h3>
<p class="sub" style="margin-bottom:12px">T<sub>screen</sub> = số lượt quét × thời gian một lượt.
Số lượt là số lần nút <em>xấu nhất</em> — nút nằm ngay dưới trục luống — phải được bay qua
để tích đủ bộ cue 30 chunk.</p>
<div class="scroll">__SWEEP__</div>
</div>
"""


def svg_panel(pts, lanes, w=420):
    pad = 120.0
    ax0, ax1 = X0 - pad - 130, X1 + pad + 130
    ay0, ay1 = Y0 - pad - 130, Y1 + pad
    sx = w / (ax1 - ax0)
    h = (ay1 - ay0) * sx

    def P(x, y):
        return (x - ax0) * sx, h - (y - ay0) * sx

    out = [f'<svg viewBox="0 0 {w:.0f} {h:.0f}" role="img">']
    fx, fy = P(X0, Y1)
    out.append(f'<rect x="{fx:.1f}" y="{fy:.1f}" width="{(X1-X0)*sx:.1f}" '
               f'height="{(Y1-Y0)*sx:.1f}" fill="var(--field)"/>')
    for s in SENSORS[::2]:
        px, py = P(*s)
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="1.05" fill="var(--node)"/>')
    # split the track into in-field / out-of-field runs so the cost is visible
    run, inside_prev = [], None
    for (x, y) in pts[::3]:
        inside = X0 <= x <= X1 and Y0 <= y <= Y1
        if inside_prev is None or inside == inside_prev:
            run.append(P(x, y))
        else:
            col = "var(--in)" if inside_prev else "var(--out)"
            d = " ".join(f"{a:.1f},{b:.1f}" for a, b in run)
            out.append(f'<polyline points="{d}" fill="none" stroke="{col}" '
                       f'stroke-width="1.5" stroke-linejoin="round"/>')
            run = [run[-1], P(x, y)] if run else [P(x, y)]
        inside_prev = inside
    if run:
        col = "var(--in)" if inside_prev else "var(--out)"
        d = " ".join(f"{a:.1f},{b:.1f}" for a, b in run)
        out.append(f'<polyline points="{d}" fill="none" stroke="{col}" stroke-width="1.5"/>')
    bx, by = P(*START)
    out.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="3.4" fill="var(--ink)"/>')
    out.append(f'<text x="{bx+7:.1f}" y="{by+4:.1f}" font-size="9.5" fill="var(--dim)">BS</text>')
    out.append("</svg>")
    return "".join(out)


def card(r, lanes, subtitle, best_keys=()):
    rows = [
        ("quãng đường", f"{r['km']:.2f} km", "km"),
        ("thời gian một lượt", f"{r['sweep_s']:.0f} s", "sweep_s"),
        ("bay trong vùng", f"{r['in_field']:.1f} %", "in_field"),
        ("phủ nút", f"{r['coverage']:.0f} %", "coverage"),
        ("số lượt quét cần", f"{r['sweeps']}", "sweeps"),
        ("T_screen", f"{r['screen_s']:.0f} s", "screen_s"),
    ]
    body = "".join(
        f'<tr class="{"hi" if k in best_keys else ""}">'
        f'<td class="k">{lbl}</td><td>{val}</td></tr>' for lbl, val, k in rows)
    title = ("Boustrophedon — quay đầu ngoài vùng" if r["name"] == "boustrophedon"
             else "Thứ tự luống tối ưu Dubins")
    return (f'<div class="card"><h2>{title}</h2><p class="tag">{subtitle}</p>'
            f'{svg_panel(r["pts"], lanes)}<table>{body}</table></div>')


def sweep_table(lanes):
    speeds = [12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 25.0, 28.0, 32.0]
    rows = []
    for v in speeds:
        R = F.turn_radius(v)
        a = score("boustrophedon", shipping_waypoints(lanes, 1.2 * R), v, strict=False)
        wps, _ = dubins_waypoints(lanes, R)
        b = score("dubins", wps, v, strict=False)
        rows.append((v, R, a, b))
    ok = [min(a["screen_s"], b["screen_s"]) for _, _, a, b in rows
          if a["coverage"] > 99.0 and b["coverage"] > 99.0]
    best = min(ok)
    out = ['<table class="big"><tr><th>v (m/s)</th><th>R(v)</th><th>2R / khoảng luống</th>'
           '<th>phủ nút</th><th>lượt quét</th><th>T_screen boustro.</th>'
           '<th>T_screen Dubins</th><th>Dubins lợi</th></tr>']
    for v, R, a, b in rows:
        gain = 100.0 * (a["screen_s"] - b["screen_s"]) / a["screen_s"]
        degraded = a["coverage"] <= 99.0 or b["coverage"] <= 99.0
        cb = ' class="best"' if abs(b["screen_s"] - best) < 1e-6 else ""
        ca = ' class="best"' if abs(a["screen_s"] - best) < 1e-6 else ""
        cov = (f'<span style="color:var(--warn)">{min(a["coverage"], b["coverage"]):.1f} %</span>'
               if degraded else f'{min(a["coverage"], b["coverage"]):.0f} %')
        out.append(f'<tr><td>{v:.0f}</td><td>{R:.0f} m</td><td>{2*R/SPACING:.2f}</td>'
                   f'<td>{cov}</td><td>{a["sweeps"]}</td><td{ca}>{a["screen_s"]:.0f} s</td>'
                   f'<td{cb}>{b["screen_s"]:.0f} s</td><td>{gain:.0f} %</td></tr>')
    out.append("</table>")
    return "".join(out)


def main():
    lanes = build_lanes(X0, X1, Y0, Y1, SPACING)
    _, rows = build_all([25.0, 16.0])
    table(rows)
    by = {(r["name"], r["v"]): r for r in rows}
    print(f"\nordering gain at v=25: "
          f"{100*(by[('boustrophedon',25.0)]['km']-by[('dubins',25.0)]['km'])/by[('boustrophedon',25.0)]['km']:.1f} % distance")
    a = by[("boustrophedon", 25.0)]["screen_s"]
    b = by[("dubins", 16.0)]["screen_s"]
    print(f"shipping @25 -> Dubins @16: {a:.0f} s -> {b:.0f} s ({100*(a-b)/a:.0f} % faster)")

    if len(sys.argv) > 1:
        cards = "".join([
            '<div class="grid">',
            card(by[("boustrophedon", 25.0)], lanes, "v = 25 m/s — đang chạy"),
            card(by[("dubins", 25.0)], lanes, "v = 25 m/s — chỉ đổi thứ tự luống",
                 best_keys=("km", "sweep_s")),
            card(by[("boustrophedon", 16.0)], lanes, "v = 16 m/s — chỉ đổi tốc độ",
                 best_keys=("sweeps",)),
            card(by[("dubins", 16.0)], lanes, "v = 16 m/s — đổi cả hai",
                 best_keys=("km", "in_field", "sweeps", "screen_s")),
            "</div>"])
        html = PAGE.replace("__CARDS__", cards).replace("__SWEEP__", sweep_table(lanes))
        with open(sys.argv[1], "w") as f:
            f.write(html)
        print(f"\n{sys.argv[1]}  ({len(html)//1024} KB)")


if __name__ == "__main__":
    main()
