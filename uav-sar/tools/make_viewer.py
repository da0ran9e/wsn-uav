#!/usr/bin/env python3
"""Build a self-contained HTML replay viewer from one or more run directories.

Closes the repro gap flagged in RESULTS-honest.md: the HTML viewers in
docs/visualize/ were produced ad hoc and had no committed generator, so they
were illustrations that nobody could regenerate or check against the data. This
script reads only the CSVs a run already emits (metrics.csv, events.csv,
trajectories.csv, config.txt) and inlines them, so a viewer is reproducible from
a run directory and from nothing else.

Multiple run directories become multiple SCHEMES in one file, switchable in the
UI, which is what makes a proposed-vs-baseline comparison honest: the same
seed, the same field, the same victim, side by side on one clock.

Usage:
    make_viewer.py OUT.html LABEL=RUNDIR [LABEL=RUNDIR ...]
"""
import csv
import json
import os
import sys


def read_csv(path):
    try:
        with open(path) as f:
            return list(csv.DictReader(f))
    except Exception:
        return []


def read_cfg(path):
    out = {}
    try:
        for line in open(path):
            if "=" in line:
                k, v = line.strip().split("=", 1)
                out[k] = v
    except Exception:
        pass
    return out


# Events worth drawing. Anything else is dropped so the payload stays small and
# the legend stays readable.
KEEP = {
    "takeoff", "cue_tx", "cue_rx", "clue_report", "share", "summon_start",
    "elect_yield", "retarget", "echo_relay", "a2a_relay", "divert",
    "deliver_start", "full_tx", "confirm", "gt_done", "report_tx", "report_rx",
    "fix_rx", "yield_return", "retarget_divert", "report_pickup",
}


def load_run(label, d):
    m = read_csv(os.path.join(d, "metrics.csv"))
    if not m:
        raise SystemExit(f"{d}: no metrics.csv")
    m = m[0]
    cfg = read_cfg(os.path.join(d, "config.txt"))
    ev, traj = [], []
    for e in read_csv(os.path.join(d, "events.csv")):
        if e["event"] not in KEEP:
            continue
        ev.append([round(float(e["t"]), 2), int(e["nodeId"]), e["role"], e["event"],
                   e["detail"][:60], round(float(e["x"]), 1), round(float(e["y"]), 1)])
    for r in read_csv(os.path.join(d, "trajectories.csv")):
        traj.append([round(float(r["t"]), 1), int(r["uavId"]), r["role"],
                     round(float(r["x"]), 1), round(float(r["y"]), 1),
                     round(float(r["z"]), 1)])
    grid = int(m["gridSize"])
    sp = float(m.get("gridSpacing") or 20.0)
    def num(k, d_=-1.0):
        try:
            return float(m.get(k, d_))
        except Exception:
            return d_
    return {
        "label": label,
        "scheme": m["scheme"],
        "seed": int(m["seed"]),
        "grid": grid,
        "spacing": sp,
        "numUav": int(m["numUav"]),
        "victim": [num("victimX"), num("victimY")],
        "fix": [num("reportedX"), num("reportedY")],
        "build": cfg.get("build", "?"),
        "metrics": {
            "t_report": num("timeToReportAtBS_s"),
            "t_localize": num("timeToLocalize_s"),
            "t_victim": num("timeToCompleteData_s"),
            "t_fix": num("timeToFixAtBS_s"),
            "fix_err": num("reportErr_m"),
            "energy_kJ": round(num("uavEnergyJ", 0) / 1000.0, 1),
            "pkts": int(num("pktSent", 0)),
        },
        "events": ev,
        "traj": traj,
    }


HTML = r"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>UAV-SAR replay — __TITLE__</title>
<style>
:root{--surface:#fcfcfb;--panel:#f4f4f2;--border:#e2e1dd;--text:#0b0b0b;
--text2:#52514e;--muted:#8a8983;--fast:#2a78d6;--data:#1baf7a;--victim:#e34948;
--bs:#0b0b0b;--good:#008300;--accent:#2a78d6;--warn:#c47b00;--node:#c9c8c2;
--hot:#e87b34;}
@media (prefers-color-scheme:dark){:root{--surface:#1a1a19;--panel:#222220;
--border:#3a3936;--text:#fff;--text2:#c3c2b7;--muted:#8a8983;--fast:#3987e5;
--data:#199e70;--victim:#e66767;--bs:#e8e7e0;--good:#35c07e;--accent:#3987e5;
--warn:#e0a030;--node:#4a4945;--hot:#ef8f4d;}}
:root[data-theme=dark]{--surface:#1a1a19;--panel:#222220;--border:#3a3936;
--text:#fff;--text2:#c3c2b7;--fast:#3987e5;--data:#199e70;--victim:#e66767;
--bs:#e8e7e0;--good:#35c07e;--accent:#3987e5;--warn:#e0a030;--node:#4a4945;--hot:#ef8f4d;}
:root[data-theme=light]{--surface:#fcfcfb;--panel:#f4f4f2;--border:#e2e1dd;
--text:#0b0b0b;--text2:#52514e;--fast:#2a78d6;--data:#1baf7a;--victim:#e34948;
--bs:#0b0b0b;--good:#008300;--accent:#2a78d6;--warn:#c47b00;--node:#c9c8c2;--hot:#e87b34;}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--surface);color:var(--text);
font:14px/1.45 -apple-system,"Segoe UI",Roboto,sans-serif;padding:14px}
header{margin-bottom:10px}
h1{font-size:17px;font-weight:650}
.sub{color:var(--text2);font-size:12.5px;margin-top:2px}
.tabs{display:flex;gap:6px;flex-wrap:wrap;margin:10px 0}
.tabs button{background:var(--panel);color:var(--text2);border:1px solid var(--border);
border-radius:7px;padding:6px 13px;font-size:13px;font-weight:600;cursor:pointer}
.tabs button.on{background:var(--accent);color:#fff;border-color:var(--accent)}
.tiles{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px}
.tile{background:var(--panel);border:1px solid var(--border);border-radius:8px;
padding:7px 13px;min-width:112px}
.tile .lbl{font-size:10.5px;color:var(--text2);text-transform:uppercase;letter-spacing:.04em}
.tile .val{font-size:19px;font-weight:700;font-variant-numeric:tabular-nums}
.tile .val small{font-size:11px;font-weight:400;color:var(--text2)}
.tile.good .val{color:var(--good)}.tile.bad .val{color:var(--victim)}
.layout{display:flex;gap:12px;align-items:flex-start;flex-wrap:wrap}
.mapwrap{flex:1 1 640px;min-width:330px;display:flex;flex-direction:column;gap:8px}
canvas{width:100%;border:1px solid var(--border);border-radius:8px;
background:var(--surface);display:block}
.controls{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.controls button{background:var(--accent);color:#fff;border:0;border-radius:6px;
padding:6px 15px;font-weight:600;font-size:13px;cursor:pointer}
.controls input[type=range]{flex:1;min-width:140px;accent-color:var(--accent)}
.controls .t{font-variant-numeric:tabular-nums;font-weight:600;min-width:86px}
.controls select{background:var(--panel);color:var(--text);border:1px solid var(--border);
border-radius:6px;padding:5px 8px}
.side{flex:0 1 320px;min-width:270px;display:flex;flex-direction:column;gap:10px}
.card{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:10px 12px}
.card h2{font-size:11px;text-transform:uppercase;letter-spacing:.05em;
color:var(--text2);margin-bottom:7px}
.legend{display:flex;flex-wrap:wrap;gap:6px 13px;font-size:12px}
.legend .it{display:flex;align-items:center;gap:5px;color:var(--text2)}
.sw{width:10px;height:10px;border-radius:3px;flex:0 0 auto}
.sw.ring{background:transparent;border:2.5px solid var(--victim);border-radius:50%}
.sw.tri{width:0;height:0;border-left:5px solid transparent;border-right:5px solid transparent;
border-bottom:10px solid var(--fast);border-radius:0}
#log{font:11.5px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;max-height:290px;
overflow-y:auto;color:var(--text2)}
#log div{padding:1px 0;border-bottom:1px solid var(--border)}
#log .hi{color:var(--text);font-weight:600}
#log b{color:var(--accent);font-variant-numeric:tabular-nums}
.note{font-size:11.5px;color:var(--muted);margin-top:9px;line-height:1.5}
table{border-collapse:collapse;width:100%;font-size:12px}
th,td{text-align:right;padding:3px 5px;border-bottom:1px solid var(--border)}
th:first-child,td:first-child{text-align:left}
th{color:var(--text2);font-weight:600;font-size:10.5px;text-transform:uppercase}
.win{color:var(--good);font-weight:700}
</style>
</head>
<body>
<header>
  <h1>UAV-SAR replay — __TITLE__</h1>
  <div class="sub" id="sub"></div>
</header>

<div class="tabs" id="tabs"></div>
<div class="tiles" id="tiles"></div>

<div class="layout">
  <div class="mapwrap">
    <canvas id="cv" width="1000" height="1000"></canvas>
    <div class="controls">
      <button id="play">▶ Play</button>
      <input type="range" id="scrub" min="0" value="0" step="0.1">
      <span class="t" id="tnow">0.0 s</span>
      <select id="speed">
        <option value="1">1×</option>
        <option value="4" selected>4×</option>
        <option value="10">10×</option>
        <option value="25">25×</option>
      </select>
    </div>
    <div class="card">
      <h2>Legend</h2>
      <div class="legend">
        <div class="it"><span class="sw tri"></span>FAST UAV</div>
        <div class="it"><span class="sw" style="background:var(--data)"></span>DATA UAV</div>
        <div class="it"><span class="sw" style="background:var(--bs)"></span>Base station</div>
        <div class="it"><span class="sw ring"></span>victim (true)</div>
        <div class="it"><span class="sw" style="background:var(--warn)"></span>fix @ BS</div>
        <div class="it"><span class="sw" style="background:var(--node)"></span>sensor</div>
        <div class="it"><span class="sw" style="background:var(--hot)"></span>node reporting evidence</div>
        <div class="it"><span class="sw" style="background:var(--good)"></span>node holds full data</div>
      </div>
    </div>
  </div>

  <div class="side">
    <div class="card">
      <h2>All schemes, this seed</h2>
      <table id="cmp"></table>
      <div class="note" id="cmpnote"></div>
    </div>
    <div class="card">
      <h2>Event log (to current time)</h2>
      <div id="log"></div>
    </div>
  </div>
</div>

<div class="note" id="prov"></div>

<script>
const RUNS = __DATA__;
let cur = 0, t = 0, playing = false, last = 0;
const cv = document.getElementById('cv'), ctx = cv.getContext('2d');

function R(){ return RUNS[cur]; }
function tmax(){ const r=R(); let m=0;
  for(const p of r.traj) if(p[0]>m) m=p[0];
  for(const e of r.events) if(e[0]>m) m=e[0];
  return Math.max(m,1); }

// ---- world -> canvas -------------------------------------------------------
function bounds(){
  const r=R(), pad=r.spacing*2.2, ext=(r.grid-1)*r.spacing;
  return {x0:-pad, y0:-pad, x1:ext+pad, y1:ext+pad};
}
function proj(x,y){
  const b=bounds(), s=Math.min(cv.width/(b.x1-b.x0), cv.height/(b.y1-b.y0));
  return [ (x-b.x0)*s, cv.height-(y-b.y0)*s ];
}

// ---- per-run derived state -------------------------------------------------
function nodeStates(r, tnow){
  // node id -> 'hot' (reported evidence) | 'done' (holds full dataset)
  const st = new Map();
  for(const e of r.events){
    if(e[0]>tnow) break;
    if(e[3]==='clue_report'||e[3]==='cue_rx') { if(!st.has(e[1])) st.set(e[1],'hot'); }
    if(e[3]==='gt_done'||e[3]==='confirm') st.set(e[1],'done');
  }
  return st;
}
function uavAt(r, tnow){
  const by = new Map();
  for(const p of r.traj){
    if(p[0]>tnow) continue;
    by.set(p[1], p);
  }
  return by;
}
function trails(r, tnow){
  const by=new Map();
  for(const p of r.traj){ if(p[0]>tnow) continue;
    if(!by.has(p[1])) by.set(p[1],[]); by.get(p[1]).push(p); }
  return by;
}

function css(v){ return getComputedStyle(document.documentElement).getPropertyValue(v).trim(); }

function draw(){
  const r=R(); ctx.clearRect(0,0,cv.width,cv.height);
  const b=bounds(), s=Math.min(cv.width/(b.x1-b.x0), cv.height/(b.y1-b.y0));

  // sensor lattice
  const st=nodeStates(r,t);
  const nodeC=css('--node'), hotC=css('--hot'), goodC=css('--good');
  const rad=Math.max(1.1, r.spacing*s*0.17);
  // node ids run BS=0, UAVs=1..numUav, sensors after that, row-major
  for(let i=0;i<r.grid*r.grid;i++){
    const gx=(i%r.grid)*r.spacing, gy=Math.floor(i/r.grid)*r.spacing;
    const id=i+1+r.numUav;
    const [px,py]=proj(gx,gy);
    const s2=st.get(id);
    ctx.fillStyle = s2==='done'?goodC : s2==='hot'?hotC : nodeC;
    ctx.globalAlpha = s2? 0.95 : 0.5;
    ctx.beginPath(); ctx.arc(px,py,rad,0,6.284); ctx.fill();
  }
  ctx.globalAlpha=1;

  // UAV trails
  const tr=trails(r,t);
  for(const [id,pts] of tr){
    ctx.strokeStyle = pts[0][2]==='FAST'?css('--fast'):css('--data');
    ctx.globalAlpha=0.35; ctx.lineWidth=1.6; ctx.beginPath();
    pts.forEach((p,i)=>{ const [px,py]=proj(p[3],p[4]); i?ctx.lineTo(px,py):ctx.moveTo(px,py); });
    ctx.stroke();
  }
  ctx.globalAlpha=1;

  // victim (true) + BS
  const [vx,vy]=proj(r.victim[0],r.victim[1]);
  ctx.strokeStyle=css('--victim'); ctx.lineWidth=3;
  ctx.beginPath(); ctx.arc(vx,vy,11,0,6.284); ctx.stroke();
  ctx.beginPath(); ctx.arc(vx,vy,20,0,6.284); ctx.globalAlpha=0.35; ctx.stroke(); ctx.globalAlpha=1;
  const [bx,by]=proj(0,0);
  ctx.fillStyle=css('--bs'); ctx.fillRect(bx-6,by-6,12,12);

  // fix reported to the BS, once it has arrived
  if(r.metrics.t_fix>=0 && t>=r.metrics.t_fix && r.fix[0]>=0){
    const [fx,fy]=proj(r.fix[0],r.fix[1]);
    ctx.strokeStyle=css('--warn'); ctx.lineWidth=2.5;
    ctx.beginPath(); ctx.moveTo(fx-8,fy-8); ctx.lineTo(fx+8,fy+8);
    ctx.moveTo(fx+8,fy-8); ctx.lineTo(fx-8,fy+8); ctx.stroke();
    ctx.strokeStyle=css('--warn'); ctx.globalAlpha=0.5; ctx.lineWidth=1.5;
    ctx.beginPath(); ctx.moveTo(fx,fy); ctx.lineTo(vx,vy); ctx.stroke(); ctx.globalAlpha=1;
  }

  // UAVs
  for(const [id,p] of uavAt(r,t)){
    const [px,py]=proj(p[3],p[4]);
    if(p[2]==='FAST'){
      ctx.fillStyle=css('--fast'); ctx.beginPath();
      ctx.moveTo(px,py-8); ctx.lineTo(px-7,py+6); ctx.lineTo(px+7,py+6); ctx.closePath(); ctx.fill();
    } else {
      ctx.fillStyle=css('--data'); ctx.beginPath(); ctx.arc(px,py,7,0,6.284); ctx.fill();
    }
  }
}

const EVLBL={summon_start:'SUMMON fired',echo_relay:'ECHO relay (closed-loop)',
 a2a_relay:'A2A relay to DATA',divert:'DATA diverts',deliver_start:'delivery begins',
 confirm:'CONFIRM (dataset complete)',report_rx:'REPORT at BS',fix_rx:'fix decoded at BS',
 retarget:'leader re-aims',elect_yield:'leader yields',takeoff:'takeoff',
 report_tx:'report sent',yield_return:'UAV yields, returns home',
 report_pickup:'courier claims report',retarget_divert:'DATA re-aims'};
function renderLog(){
  const r=R(), out=[];
  for(const e of r.events){
    if(e[0]>t) break;
    const lbl=EVLBL[e[3]]; if(!lbl) continue;
    out.push(`<div><b>${e[0].toFixed(1)}s</b> <span class="hi">${lbl}</span>`+
             (e[4]?` — ${e[4]}`:'')+`</div>`);
  }
  document.getElementById('log').innerHTML = out.slice(-160).reverse().join('') ||
    '<div style="color:var(--muted)">nothing yet</div>';
}

function fmt(v,u,dp){ return v<0? '—' : v.toFixed(dp===undefined?1:dp)+(u||''); }
function renderTiles(){
  const m=R().metrics;
  const tiles=[
    ['mission @ BS', fmt(m.t_report,' s'), m.t_report>=0?'good':'bad'],
    ['localize', fmt(m.t_localize,' s'), ''],
    ['victim served', fmt(m.t_victim,' s'), m.t_victim>=0?'good':'bad'],
    ['fix @ BS', m.fix_err>=0?m.fix_err.toFixed(1)+' m':'— none —',
      m.fix_err>=0?'good':'bad'],
    ['energy', m.energy_kJ+' kJ',''],
    ['packets', m.pkts.toLocaleString(),''],
  ];
  document.getElementById('tiles').innerHTML = tiles.map(
    ([l,v,c])=>`<div class="tile ${c}"><div class="lbl">${l}</div><div class="val">${v}</div></div>`
  ).join('');
}
function renderCmp(){
  const rows=[['scheme','mission','victim','fix err','kJ','pkts']];
  const best={t:1e9,e:1e9,p:1e9};
  RUNS.forEach(r=>{const m=r.metrics;
    if(m.t_report>=0) best.t=Math.min(best.t,m.t_report);
    best.e=Math.min(best.e,m.energy_kJ); best.p=Math.min(best.p,m.pkts);});
  const body=RUNS.map((r,i)=>{const m=r.metrics;
    const w=(v,b)=>v===b?' class="win"':'';
    return `<tr${i===cur?' style="outline:1px solid var(--accent)"':''}>`+
      `<td>${r.label}</td><td${w(m.t_report,best.t)}>${fmt(m.t_report,'')}</td>`+
      `<td>${fmt(m.t_victim,'')}</td>`+
      `<td>${m.fix_err>=0?m.fix_err.toFixed(1):'—'}</td>`+
      `<td${w(m.energy_kJ,best.e)}>${m.energy_kJ}</td>`+
      `<td${w(m.pkts,best.p)}>${m.pkts.toLocaleString()}</td></tr>`;}).join('');
  document.getElementById('cmp').innerHTML =
    '<tr>'+rows[0].map(h=>`<th>${h}</th>`).join('')+'</tr>'+body;
  document.getElementById('cmpnote').textContent =
    'Green = best of the schemes shown. "—" in fix err means the scheme produced '+
    'no position at all, which is the permanent outcome for every blind-coverage '+
    'baseline: it has nothing to report.';
}
function renderTabs(){
  document.getElementById('tabs').innerHTML = RUNS.map((r,i)=>
    `<button class="${i===cur?'on':''}" onclick="pick(${i})">${r.label}</button>`).join('');
}
window.pick=function(i){ cur=i; t=0; setup(); };

function setup(){
  const r=R();
  document.getElementById('sub').textContent =
    `${r.grid}×${r.grid} = ${(r.grid*r.grid).toLocaleString()} sensors, `+
    `${((r.grid-1)*r.spacing).toFixed(0)}×${((r.grid-1)*r.spacing).toFixed(0)} m, `+
    `${r.numUav} UAV, seed ${r.seed}`;
  document.getElementById('scrub').max = tmax();
  document.getElementById('prov').textContent =
    `Generated by tools/make_viewer.py from the run's own CSVs. Build ${r.build}. `+
    `Every marker is an event the simulation actually logged; nothing here is drawn from `+
    `simulator state the nodes could not observe.`;
  renderTabs(); renderTiles(); renderCmp(); renderLog(); draw();
}

document.getElementById('scrub').addEventListener('input',e=>{
  t=parseFloat(e.target.value);
  document.getElementById('tnow').textContent=t.toFixed(1)+' s';
  renderLog(); draw(); });
document.getElementById('play').addEventListener('click',()=>{
  playing=!playing; document.getElementById('play').textContent=playing?'❚❚ Pause':'▶ Play';
  last=performance.now(); if(playing) requestAnimationFrame(tick); });
function tick(now){
  if(!playing) return;
  const sp=parseFloat(document.getElementById('speed').value);
  t=Math.min(tmax(), t+(now-last)/1000*sp); last=now;
  document.getElementById('scrub').value=t;
  document.getElementById('tnow').textContent=t.toFixed(1)+' s';
  renderLog(); draw();
  if(t>=tmax()){ playing=false; document.getElementById('play').textContent='▶ Play'; return; }
  requestAnimationFrame(tick);
}
setup();
</script>
</body>
</html>
"""


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    out = sys.argv[1]
    runs = []
    for spec in sys.argv[2:]:
        label, d = spec.split("=", 1)
        runs.append(load_run(label, d))
    title = f"{runs[0]['grid']}×{runs[0]['grid']} — seed {runs[0]['seed']}"
    html = HTML.replace("__DATA__", json.dumps(runs, separators=(",", ":")))
    html = html.replace("__TITLE__", title)
    with open(out, "w") as f:
        f.write(html)
    print(f"{out}  ({os.path.getsize(out)/1024:.0f} KB, {len(runs)} schemes)")


if __name__ == "__main__":
    main()
