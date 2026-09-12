"""Minimal inline-SVG charts for the self-contained HTML reports (brief 9).

No matplotlib, no CDN, no data: URIs -- the charts ARE markup, so the reports
open correctly from file:// with no network, which is the requirement.
"""
from __future__ import annotations

import html
import math

PALETTE = ["#2563eb", "#d97706", "#059669", "#dc2626", "#7c3aed", "#0891b2",
           "#be185d", "#4d7c0f"]


def _nice(lo: float, hi: float, n: int = 6) -> tuple[float, float, list[float]]:
    if hi <= lo:
        hi = lo + 1.0
    raw = (hi - lo) / n
    mag = 10 ** math.floor(math.log10(raw))
    step = min((m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw), default=mag * 10)
    lo2 = math.floor(lo / step) * step
    hi2 = math.ceil(hi / step) * step
    ticks, t = [], lo2
    while t <= hi2 + step * 1e-9:
        ticks.append(round(t, 10))
        t += step
    return lo2, hi2, ticks


def _fmt(v: float) -> str:
    a = abs(v)
    if a == 0:
        return "0"
    if a >= 1e5 or a < 1e-3:
        return f"{v:.0e}"
    if a >= 100:
        return f"{v:.0f}"
    if a >= 10:
        return f"{v:.1f}"
    if a >= 1:
        return f"{v:.2f}"
    return f"{v:.3f}"


def line_chart(series: list[dict], *, x_label: str, y_label: str, title: str = "",
               width: int = 760, height: int = 360, log_y: bool = False,
               y_min: float | None = None, caption: str = "",
               vlines: list[tuple] | None = None,
               shade_x: tuple | None = None, log_x: bool = False) -> str:
    """series: [{name, x, y, lo?, hi?, marker_at?, dashed?, color?}]

    lo/hi draw a confidence ribbon. vlines is [(x, label), ...]; shade_x is
    (x0, x1, label) for an operating-range band.
    """
    ml, mr, mt, mb = 68, 150, 28 if title else 14, 46
    pw, ph = width - ml - mr, height - mt - mb
    xs = [v for s in series for v in s["x"]]
    ys = [v for s in series for v in s["y"] if v is not None and (not log_y or v > 0)]
    for s_ in series:
        for key in ("lo", "hi"):
            for v in s_.get(key, []) or []:
                if v is not None and (not log_y or v > 0):
                    ys.append(v)
    if vlines:
        xs += [vx for vx, _ in vlines]
    if shade_x:
        xs += [shade_x[0], shade_x[1]]
    if log_x:
        lx0, lx1 = math.log10(min(xs)), math.log10(max(xs))
        pad = 0.04 * max(lx1 - lx0, 1e-9)
        lx0, lx1 = lx0 - pad, lx1 + pad
        xticks = [v for v in sorted(set(xs))]
        x0, x1 = 10 ** lx0, 10 ** lx1
    else:
        x0, x1, xticks = _nice(min(xs), max(xs))
    if log_y:
        ly0, ly1 = math.log10(min(ys)), math.log10(max(ys))
        ly0, ly1 = math.floor(ly0), math.ceil(ly1)
        yticks = [10 ** e for e in range(int(ly0), int(ly1) + 1)]
        ty = lambda v: mt + ph - (math.log10(v) - ly0) / max(ly1 - ly0, 1e-9) * ph
    else:
        lo = min(ys) if y_min is None else y_min
        y0, y1, yticks = _nice(lo, max(ys))
        ty = lambda v: mt + ph - (v - y0) / (y1 - y0) * ph
    if log_x:
        tx = lambda v: ml + (math.log10(v) - math.log10(x0)) / \
            (math.log10(x1) - math.log10(x0)) * pw
    else:
        tx = lambda v: ml + (v - x0) / (x1 - x0) * pw

    o = [f'<svg viewBox="0 0 {width} {height}" width="100%" role="img" '
         f'aria-label="{html.escape(title or y_label)}" class="chart">']
    if title:
        o.append(f'<text x="{ml}" y="16" class="ct">{html.escape(title)}</text>')
    for t in yticks:
        y = ty(t)
        if not (mt - 1 <= y <= mt + ph + 1):
            continue
        o.append(f'<line x1="{ml}" y1="{y:.1f}" x2="{ml+pw}" y2="{y:.1f}" class="grid"/>'
                 f'<text x="{ml-8}" y="{y+4:.1f}" class="tk" text-anchor="end">{_fmt(t)}</text>')
    for t in xticks:
        x = tx(t)
        if not (ml - 1 <= x <= ml + pw + 1):
            continue
        o.append(f'<line x1="{x:.1f}" y1="{mt}" x2="{x:.1f}" y2="{mt+ph}" class="grid"/>'
                 f'<text x="{x:.1f}" y="{mt+ph+18}" class="tk" text-anchor="middle">{_fmt(t)}</text>')
    if shade_x:
        sx0, sx1 = max(x0, shade_x[0]), min(x1, shade_x[1])
        if sx1 > sx0:
            o.append(f'<rect x="{tx(sx0):.1f}" y="{mt}" width="{tx(sx1)-tx(sx0):.1f}" '
                     f'height="{ph}" fill="#2563eb" opacity="0.06"/>')
            if len(shade_x) > 2 and shade_x[2]:
                o.append(f'<text x="{(tx(sx0)+tx(sx1))/2:.1f}" y="{mt+12}" '
                         f'class="tk" text-anchor="middle">{html.escape(shade_x[2])}</text>')
    for vx, vlab in (vlines or []):
        if x0 <= vx <= x1:
            o.append(f'<line x1="{tx(vx):.1f}" y1="{mt}" x2="{tx(vx):.1f}" '
                     f'y2="{mt+ph}" stroke="#dc2626" stroke-width="1.5" '
                     f'stroke-dasharray="4,3"/>')
            if vlab:
                o.append(f'<text x="{tx(vx)+4:.1f}" y="{mt+ph-6}" class="tk" '
                         f'fill="#dc2626">{html.escape(vlab)}</text>')
    o.append(f'<line x1="{ml}" y1="{mt+ph}" x2="{ml+pw}" y2="{mt+ph}" class="ax"/>'
             f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{mt+ph}" class="ax"/>')
    o.append(f'<text x="{ml+pw/2:.0f}" y="{height-6}" class="al" text-anchor="middle">'
             f'{html.escape(x_label)}</text>')
    o.append(f'<text x="14" y="{mt+ph/2:.0f}" class="al" text-anchor="middle" '
             f'transform="rotate(-90 14 {mt+ph/2:.0f})">{html.escape(y_label)}</text>')

    for i, s in enumerate(series):
        c = s.get("color", PALETTE[i % len(PALETTE)])
        lo, hi = s.get("lo"), s.get("hi")
        if lo and hi:
            up = [(tx(x), ty(v)) for x, v in zip(s["x"], hi)
                  if v is not None and (not log_y or v > 0)]
            dn = [(tx(x), ty(v)) for x, v in zip(s["x"], lo)
                  if v is not None and (not log_y or v > 0)][::-1]
            if len(up) > 1 and len(dn) > 1:
                d = " ".join(f"{'M' if j == 0 else 'L'}{x:.1f},{y:.1f}"
                             for j, (x, y) in enumerate(up + dn)) + " Z"
                o.append(f'<path d="{d}" fill="{c}" opacity="0.16" stroke="none"/>')
        pts = [(tx(x), ty(y)) for x, y in zip(s["x"], s["y"])
               if y is not None and (not log_y or y > 0)]
        d = " ".join(f"{'M' if j == 0 else 'L'}{x:.1f},{y:.1f}" for j, (x, y) in enumerate(pts))
        dash = ' stroke-dasharray="5,4"' if s.get("dashed") else ""
        o.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="2"{dash}/>')
        if s.get("marker_at") is not None:
            mx = s["marker_at"]
            my = s["y"][s["x"].index(mx)]
            o.append(f'<circle cx="{tx(mx):.1f}" cy="{ty(my):.1f}" r="5" fill="{c}" '
                     f'stroke="#fff" stroke-width="2"/>')
        ly = mt + 14 + i * 18
        o.append(f'<line x1="{ml+pw+12}" y1="{ly}" x2="{ml+pw+34}" y2="{ly}" '
                 f'stroke="{c}" stroke-width="2"{dash}/>'
                 f'<text x="{ml+pw+40}" y="{ly+4}" class="lg">{html.escape(s["name"])}</text>')
    o.append("</svg>")
    if caption:
        o.append(f'<p class="cap">{caption}</p>')
    return "\n".join(o)


def bar_chart(groups: list[str], series: list[dict], *, y_label: str, title: str = "",
              width: int = 760, height: int = 340, y_max: float | None = None,
              caption: str = "", value_fmt: str = "{:.2f}") -> str:
    """groups: category labels. series: [{name, y: [... one per group]}]"""
    ml, mr, mt, mb = 68, 150, 28 if title else 14, 56
    pw, ph = width - ml - mr, height - mt - mb
    ys = [v for s in series for v in s["y"]]
    y0, y1, yticks = _nice(0.0, y_max if y_max is not None else max(ys))
    ty = lambda v: mt + ph - (v - y0) / (y1 - y0) * ph
    gw = pw / max(len(groups), 1)
    bw = gw * 0.78 / max(len(series), 1)

    o = [f'<svg viewBox="0 0 {width} {height}" width="100%" role="img" '
         f'aria-label="{html.escape(title or y_label)}" class="chart">']
    if title:
        o.append(f'<text x="{ml}" y="16" class="ct">{html.escape(title)}</text>')
    for t in yticks:
        y = ty(t)
        o.append(f'<line x1="{ml}" y1="{y:.1f}" x2="{ml+pw}" y2="{y:.1f}" class="grid"/>'
                 f'<text x="{ml-8}" y="{y+4:.1f}" class="tk" text-anchor="end">{_fmt(t)}</text>')
    o.append(f'<line x1="{ml}" y1="{mt+ph}" x2="{ml+pw}" y2="{mt+ph}" class="ax"/>')
    o.append(f'<text x="14" y="{mt+ph/2:.0f}" class="al" text-anchor="middle" '
             f'transform="rotate(-90 14 {mt+ph/2:.0f})">{html.escape(y_label)}</text>')
    for gi, g in enumerate(groups):
        gx = ml + gi * gw
        o.append(f'<text x="{gx+gw/2:.1f}" y="{mt+ph+18}" class="tk" '
                 f'text-anchor="middle">{html.escape(g)}</text>')
        for si, s in enumerate(series):
            v = s["y"][gi]
            c = s.get("color", PALETTE[si % len(PALETTE)])
            x = gx + gw * 0.11 + si * bw
            h = max(0.0, mt + ph - ty(v))
            o.append(f'<rect x="{x:.1f}" y="{ty(v):.1f}" width="{bw-2:.1f}" '
                     f'height="{h:.1f}" fill="{c}" rx="2"/>')
            if h > 14:
                o.append(f'<text x="{x+(bw-2)/2:.1f}" y="{ty(v)-4:.1f}" class="vl" '
                         f'text-anchor="middle">{value_fmt.format(v)}</text>')
    for si, s in enumerate(series):
        c = s.get("color", PALETTE[si % len(PALETTE)])
        ly = mt + 14 + si * 18
        o.append(f'<rect x="{ml+pw+12}" y="{ly-7}" width="22" height="10" fill="{c}" rx="2"/>'
                 f'<text x="{ml+pw+40}" y="{ly+3}" class="lg">{html.escape(s["name"])}</text>')
    o.append("</svg>")
    if caption:
        o.append(f'<p class="cap">{caption}</p>')
    return "\n".join(o)


CSS = """
:root{--fg:#111827;--mut:#6b7280;--bd:#e5e7eb;--bg:#fff;--sb:#f9fafb;
--ok:#065f46;--okbg:#ecfdf5;--warn:#92400e;--warnbg:#fffbeb;--bad:#991b1b;--badbg:#fef2f2;}
*{box-sizing:border-box}
body{margin:0;background:var(--sb);color:var(--fg);
font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}
.wrap{max-width:1080px;margin:0 auto;padding:28px 20px 72px}
h1{font-size:26px;margin:0 0 4px;letter-spacing:-.01em}
h2{font-size:19px;margin:38px 0 10px;padding-bottom:6px;border-bottom:2px solid var(--bd)}
h3{font-size:15.5px;margin:24px 0 8px}
p{margin:10px 0}
.sub{color:var(--mut);margin:0 0 18px}
.card{background:var(--bg);border:1px solid var(--bd);border-radius:10px;padding:18px 20px;margin:16px 0}
.banner{display:inline-block;padding:5px 12px;border-radius:999px;font-weight:650;font-size:12.5px;
letter-spacing:.04em;text-transform:uppercase}
.CURRENT{background:var(--okbg);color:var(--ok);border:1px solid #a7f3d0}
.STALE{background:var(--warnbg);color:var(--warn);border:1px solid #fde68a}
.VOID{background:var(--badbg);color:var(--bad);border:1px solid #fecaca}
.meta{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px 22px;margin:14px 0 0}
.meta div{font-size:13px;color:var(--mut)}
.meta b{display:block;color:var(--fg);font-weight:600;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;
font-size:12.5px;word-break:break-all}
table{border-collapse:collapse;width:100%;font-size:13.5px;margin:12px 0}
th,td{border-bottom:1px solid var(--bd);padding:7px 9px;text-align:right}
th:first-child,td:first-child{text-align:left}
thead th{background:var(--sb);font-weight:650;font-size:12.5px;color:var(--mut);
text-transform:uppercase;letter-spacing:.03em}
tbody tr:hover{background:var(--sb)}
td.num,th.num{font-variant-numeric:tabular-nums;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.tw{overflow-x:auto}
.chart{display:block;margin:6px 0 0;background:var(--bg)}
.ct{font-size:13px;font-weight:650;fill:var(--fg)}
.tk{font-size:11px;fill:var(--mut)}
.al{font-size:11.5px;fill:var(--mut)}
.lg{font-size:11.5px;fill:var(--fg)}
.vl{font-size:10px;fill:var(--mut);font-variant-numeric:tabular-nums}
.grid{stroke:var(--bd);stroke-width:1}
.ax{stroke:#9ca3af;stroke-width:1}
.cap{font-size:12.5px;color:var(--mut);margin:8px 0 0;border-left:3px solid var(--bd);padding-left:10px}
.src{font-size:12px;margin:10px 0 0}
.src a{color:#2563eb}
code{background:var(--sb);border:1px solid var(--bd);border-radius:4px;padding:1px 5px;
font:12.5px ui-monospace,SFMono-Regular,Menlo,monospace}
.verdict{border-left:4px solid #059669;background:var(--okbg)}
.verdict.no{border-left-color:#dc2626;background:var(--badbg)}
.flag{border-left:4px solid #d97706;background:var(--warnbg)}
.big{font-size:30px;font-weight:700;letter-spacing:-.02em}
ul,ol{margin:10px 0;padding-left:22px}li{margin:5px 0}
.kv{display:flex;gap:26px;flex-wrap:wrap;margin:12px 0}
.kv>div{min-width:140px}.kv .l{font-size:12px;color:var(--mut)}
.kv .v{font-size:21px;font-weight:650;font-variant-numeric:tabular-nums}
.q{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:6px}
.q.done{background:#059669}.q.blocked{background:#dc2626}.q.todo{background:#d1d5db}
.q.part{background:#d97706}
"""
