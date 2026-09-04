"""Self-contained animated HTML replay of a Phase-1 plan.

Plays the aircraft along the paths at the speeds the LP chose, and fills each
class-A cell as the reference dose it has received accumulates. No external
libraries: everything is inlined so the file opens anywhere.

    python3 tools/make_p1_viewer.py OUT.html LABEL=RUNDIR [LABEL=RUNDIR ...]
"""
import csv, json, math, os, sys


def rows(d, n):
    p = os.path.join(d, n)
    return list(csv.DictReader(open(p))) if os.path.exists(p) else []


def load(d):
    C = {r["key"]: r["value"] for r in rows(d, "config.csv")}
    cells = [{"id": int(c["id"]), "x": float(c["cx"]), "y": float(c["cy"]),
              "cls": c["class"], "score": float(c["score"]),
              "suspect": c["suspect"] == "1", "theta": float(c["theta"]),
              "real": c["holdsReal"] == "1", "obj": c["holdsObject"] == "1"}
             for c in rows(d, "cells.csv")]
    objs = [{"x": float(o["x"]), "y": float(o["y"]), "real": o["real"] == "1"}
            for o in rows(d, "objects.csv")]
    veh = {}
    for p in rows(d, "path.csv"):
        veh.setdefault(int(p["vehicle"]), []).append(
            {"x": float(p["x"]), "y": float(p["y"]), "v": float(p["speedMps"]),
             "L": float(p["lengthM"]), "t": float(p["tStartS"])})
    hist = [{"it": int(h["iteration"]), "mk": float(h["makespanS"]),
             "cells": int(h.get("planCells", 0)), "ok": h["valid"] == "1"}
            for h in rows(d, "history.csv")]
    return {"cfg": C, "cells": cells, "objs": objs,
            "veh": [veh[k] for k in sorted(veh)], "hist": hist,
            "rc": float(C["cellRadius"]), "side": float(C["side"]),
            "prxD50": float(C["prxD50"]), "vmin": float(C["vmin"]),
            "vmax": float(C["vmax"])}


HTML = """<title>Phase 1 replay</title>
<style>
:root{--ink:#12151a;--dim:#5b6472;--line:#dfe3e9;--bg:#f7f8fa;--card:#fff;
      --a:#2f6fd0;--b:#e08a1e;--c:#b9c0cb;--real:#1f9d6b;--dec:#c2410c}
:root:not([data-theme=light]) @media (prefers-color-scheme:dark){}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){
  --ink:#e8ecf2;--dim:#9aa4b2;--line:#2a3038;--bg:#12151a;--card:#1a1f26}}
:root[data-theme=dark]{--ink:#e8ecf2;--dim:#9aa4b2;--line:#2a3038;--bg:#12151a;--card:#1a1f26}
body{background:var(--bg);color:var(--ink);font:14px/1.5 system-ui,-apple-system,sans-serif;
     margin:0;padding:18px}
h1{font-size:17px;margin:0 0 2px}
.sub{color:var(--dim);font-size:12.5px;margin-bottom:14px}
.wrap{display:flex;gap:16px;flex-wrap:wrap;align-items:flex-start}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}
canvas{display:block;border-radius:6px}
.ctl{display:flex;gap:10px;align-items:center;margin-top:10px;flex-wrap:wrap}
button,select{font:inherit;padding:5px 11px;border:1px solid var(--line);
  border-radius:7px;background:var(--card);color:var(--ink);cursor:pointer}
button:hover{border-color:var(--dim)}
input[type=range]{flex:1;min-width:190px}
.k{font-variant-numeric:tabular-nums;color:var(--dim);font-size:12.5px}
table{border-collapse:collapse;font-size:12.5px}
th,td{padding:3px 9px;text-align:right;border-bottom:1px solid var(--line)}
th{color:var(--dim);font-weight:500}
td:first-child,th:first-child{text-align:left}
.leg{display:flex;gap:14px;flex-wrap:wrap;font-size:12px;color:var(--dim);margin-top:8px}
.sw{display:inline-block;width:11px;height:11px;border-radius:3px;vertical-align:-1px;margin-right:5px}
.note{max-width:330px;font-size:12.5px;color:var(--dim);line-height:1.6}
.note b{color:var(--ink);font-weight:600}
</style>
<h1 id=ttl>Phase 1 — replay</h1>
<div class=sub id=sub></div>
<div class=wrap>
  <div class=card>
    <canvas id=cv width=680 height=680></canvas>
    <div class=ctl>
      <button id=play>▶ chạy</button>
      <button id=rew>⟲</button>
      <select id=which></select>
      <input type=range id=sl min=0 max=1000 value=0>
      <span class=k id=clock>0 s</span>
    </div>
    <div class=leg>
      <span><i class=sw style=background:var(--a)></i>ô lớp A</span>
      <span><i class=sw style=background:var(--b)></i>lớp B</span>
      <span><i class=sw style=background:var(--c)></i>lớp C</span>
      <span><i class=sw style=background:var(--real)></i>nạn nhân thật</span>
      <span><i class=sw style=background:var(--dec)></i>vật gây nhầm</span>
      <span>viền đậm = ô nghi vấn (∈ D) · ô sáng dần = liều tham chiếu đã nhận</span>
    </div>
  </div>
  <div class=card>
    <div class=note id=note></div>
    <table id=tb></table>
  </div>
</div>
<script>
const DATA = __DATA__;
const sel = document.getElementById('which');
Object.keys(DATA).forEach(k => sel.add(new Option(k, k)));
let R = DATA[sel.value], T = 0, playing = false, last = 0;

const cv = document.getElementById('cv'), g = cv.getContext('2d');
const VEH = ['#12151a','#7c3aed','#0e7490','#a16207','#be123c'];

function span(){ let m=0; R.veh.forEach(p=>{ if(p.length) m=Math.max(m,p[p.length-1].t+p[p.length-1].L/Math.max(1,p[p.length-1].v)); }); return Math.max(m,1); }
function css(n){ return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); }

function tx(x){ const pad=34, s=(cv.width-2*pad)/(R.side+2*R.rc); return pad+(x+R.rc)*s; }
function ty(y){ const pad=34, s=(cv.height-2*pad)/(R.side+2*R.rc); return cv.height-(pad+(y+R.rc)*s); }
function sc(){ const pad=34; return (cv.width-2*pad)/(R.side+2*R.rc); }

// dose a cell has received up to time T, from every aircraft
function doseAt(c){
  let d=0;
  const lam = 4000, d50 = R.prxD50, w = 35;
  R.veh.forEach(p=>{ for(const s of p){
    if(s.t>T) break;
    const dist=Math.hypot(s.x-c.x,s.y-c.y);
    const pr=1/(1+Math.exp((dist-d50)/w));
    d += lam*s.L*pr/Math.max(1,s.v);
  }});
  return d;
}

function hex(cx,cy,r){ g.beginPath();
  for(let i=0;i<6;i++){ const a=Math.PI/180*(60*i+90); const X=cx+r*Math.cos(a), Y=cy+r*Math.sin(a);
    i?g.lineTo(X,Y):g.moveTo(X,Y); } g.closePath(); }

function draw(){
  const S=sc();
  g.clearRect(0,0,cv.width,cv.height);
  g.fillStyle=css('--card'); g.fillRect(0,0,cv.width,cv.height);
  for(const c of R.cells){
    const base = c.cls==='A'?css('--a'):c.cls==='B'?css('--b'):css('--c');
    const need = c.theta>0 ? Math.min(1, doseAt(c)/c.theta) : 0;
    g.globalAlpha = 0.13 + 0.55*need;
    g.fillStyle = base; hex(tx(c.x),ty(c.y),R.rc*S); g.fill();
    g.globalAlpha = 1;
    g.strokeStyle = c.suspect?css('--ink'):css('--line');
    g.lineWidth = c.suspect?2.1:0.9; hex(tx(c.x),ty(c.y),R.rc*S); g.stroke();
  }
  R.veh.forEach((p,vi)=>{
    g.strokeStyle=VEH[vi%VEH.length]; g.globalAlpha=.20; g.lineWidth=4.4;
    g.beginPath(); p.forEach((s,i)=> i?g.lineTo(tx(s.x),ty(s.y)):g.moveTo(tx(s.x),ty(s.y))); g.stroke();
    g.globalAlpha=1; g.lineWidth=2.4; g.beginPath(); let started=false, head=null;
    for(const s of p){ if(s.t>T) break; head=s;
      if(!started){ g.moveTo(tx(s.x),ty(s.y)); started=true; } else g.lineTo(tx(s.x),ty(s.y)); }
    g.strokeStyle=VEH[vi%VEH.length]; g.stroke();
    if(head){ g.fillStyle=VEH[vi%VEH.length]; g.beginPath();
      g.arc(tx(head.x),ty(head.y),5.4,0,7); g.fill();
      g.fillStyle=css('--card'); g.beginPath(); g.arc(tx(head.x),ty(head.y),2.1,0,7); g.fill(); }
  });
  for(const o of R.objs){ g.fillStyle=o.real?css('--real'):css('--dec');
    g.beginPath(); g.arc(tx(o.x),ty(o.y),o.real?7:5.4,0,7); g.fill();
    g.strokeStyle=css('--card'); g.lineWidth=1.6; g.stroke(); }
  g.fillStyle=css('--ink'); g.fillRect(tx(0)-5,ty(0)-5,10,10);
  document.getElementById('clock').textContent = T.toFixed(0)+' s';
  document.getElementById('sl').value = 1000*T/span();
}

function info(){
  const C=R.cfg;
  document.getElementById('sub').textContent =
    `${C.grid}×${C.grid} nút @${C.spacing} m · vùng ${C.side} m · R_c=${C.cellRadius} m ` +
    `(h=${(+C.rowPitch).toFixed(0)} m) · ${C.vehicles} máy bay · ρ=${(+C.turnRadius).toFixed(1)} m`;
  const served = R.cells.filter(c=>c.theta>0).length;
  const A = R.cells.filter(c=>c.cls==='A').length;
  document.getElementById('note').innerHTML =
    `<b>Chỉ ô lớp A tốn thời gian bay.</b> ${A}/${R.cells.length} ô là lớp A; ` +
    `kế hoạch thăm ${served} ô — phần còn lại nhận đủ liều <b>miễn phí</b> vì nằm gần ` +
    `đường bay đã phải bay dù sao.<br><br>` +
    `<b>Ô sáng dần</b> theo liều tham chiếu tích luỹ. Máy bay <b>bay chậm lại</b> ở nơi ` +
    `cần nhiều liều: liều tỉ lệ nghịch với tốc độ, và đó là biến điều khiển duy nhất của ` +
    `một phương tiện không treo được.<br><br>` +
    `<b>T4 không co.</b> Bỏ một ô làm tuyến ngắn lại, có thể khiến chính ô đó hết được phủ. ` +
    `Nên chỉ kế hoạch <i>tự nhất quán</i> mới được nhận, và bước rút bị chia đôi mỗi lần thất bại.`;
  let h = '<tr><th>vòng T4</th><th>makespan</th><th>ô thăm</th><th>hợp lệ</th></tr>';
  for(const r of R.hist)
    h += `<tr><td>${r.it}</td><td>${r.mk.toFixed(0)} s</td><td>${r.cells}</td>` +
         `<td style="color:${r.ok?css('--real'):css('--dec')}">${r.ok?'✓':'✗'}</td></tr>`;
  document.getElementById('tb').innerHTML = h;
}

document.getElementById('play').onclick = e => {
  playing = !playing; e.target.textContent = playing ? '❚❚ dừng' : '▶ chạy';
  last = performance.now(); if (playing) requestAnimationFrame(step);
};
document.getElementById('rew').onclick = () => { T = 0; draw(); };
document.getElementById('sl').oninput = e => { T = span()*e.target.value/1000; draw(); };
sel.onchange = () => { R = DATA[sel.value]; T = 0; info(); draw(); };
function step(now){ if(!playing) return;
  T += (now-last)/1000*8; last = now;
  if (T > span()) { T = span(); playing = false;
    document.getElementById('play').textContent='▶ chạy'; }
  draw(); if (playing) requestAnimationFrame(step); }
matchMedia('(prefers-color-scheme:dark)').addEventListener('change', draw);
info(); draw();
</script>
"""


def main():
    out, specs = sys.argv[1], sys.argv[2:]
    data = {}
    for sp in specs:
        label, d = sp.split("=", 1)
        data[label] = load(d)
    open(out, "w").write(HTML.replace("__DATA__", json.dumps(data)))
    kb = os.path.getsize(out) / 1024
    print(f"  {out}  ({kb:.0f} KB, {len(data)} runs)")


if __name__ == "__main__":
    main()
