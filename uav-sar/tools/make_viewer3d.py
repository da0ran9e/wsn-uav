#!/usr/bin/env python3
"""Build a self-contained 3D HTML replay from one or more run directories.

Same inputs as make_viewer.py -- metrics.csv, events.csv, trajectories.csv,
config.txt -- rendered as an orbitable 3D scene instead of a flat map. The point
of the third dimension here is the FLIGHT LEVELS: the fixed-wing FAST scout and
the rotary-wing DATA carrier fly separated altitudes, and in a flat view the two
teams are drawn on top of each other, which hides who is doing what.

No external libraries: the projection, depth sorting and interaction are written
out inline, so the file opens anywhere with no network.

Usage:
    make_viewer3d.py OUT.html LABEL=RUNDIR [LABEL=RUNDIR ...]
"""
import csv
import json
import os
import sys

KEEP = {
    "takeoff", "clue_report", "summon_start", "elect_yield", "retarget",
    "echo_relay", "a2a_relay", "divert", "deliver_start", "deliver_move",
    "confirm", "reject", "next_task", "yield_stay", "report_tx", "report_rx",
    "fix_rx", "gt_done",
}
# Drawn from t=0 as world setup rather than as timeline events.
WORLD = {"victim", "clutter"}


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


def load(label, d):
    m = read_csv(os.path.join(d, "metrics.csv"))
    if not m:
        raise SystemExit(f"{d}: no metrics.csv")
    m = m[0]
    cfg = read_cfg(os.path.join(d, "config.txt"))

    victims, clutter, ev = [], [], []
    # Node data-accumulation state, the thing the flat viewer showed and the
    # first 3D cut lost. Only the FIRST time a node reaches each level is kept,
    # so this stays a few hundred entries instead of one per chunk.
    #   1 = has cue fragments      2 = evidence crossed the bar, it REPORTED
    #   3 = holds the whole dataset (confirmed or rejected on full data)
    LEVEL = {"cue_rx": 1, "clue_report": 2, "gt_done": 3, "confirm": 3, "reject": 3}
    best = {}
    for e in read_csv(os.path.join(d, "events.csv")):
        lv = LEVEL.get(e["event"])
        if lv is None:
            continue
        key = (round(float(e["x"]), 1), round(float(e["y"]), 1))
        cur = best.get(key)
        if cur is None or lv > cur[1]:
            best[key] = (round(float(e["t"]), 1), lv)
    nodes = sorted([[t, k[0], k[1], lv] for k, (t, lv) in best.items()])

    for e in read_csv(os.path.join(d, "events.csv")):
        k = e["event"]
        if k == "victim":
            victims.append([round(float(e["x"]), 1), round(float(e["y"]), 1)])
            continue
        if k == "clutter":
            clutter.append([round(float(e["x"]), 1), round(float(e["y"]), 1),
                            round(float(e["detail"] or 0), 2)])
            continue
        if k not in KEEP:
            continue
        ev.append([round(float(e["t"]), 1), e["role"], k,
                   round(float(e["x"]), 1), round(float(e["y"]), 1),
                   round(float(e["z"]), 1), e["detail"][:48]])

    traj = {}
    for r in read_csv(os.path.join(d, "trajectories.csv")):
        traj.setdefault(r["uavId"], {"role": r["role"], "p": []})["p"].append(
            [round(float(r["t"]), 1), round(float(r["x"]), 1),
             round(float(r["y"]), 1), round(float(r["z"]), 1)])
    for u in traj:
        traj[u]["p"].sort()

    def num(k, d_=-1.0):
        try:
            return float(m.get(k, d_))
        except Exception:
            return d_

    n = int(m["gridSize"])
    sp = float(m.get("gridSpacing") or 20.0)
    return {
        "label": label,
        "scheme": m["scheme"],
        "seed": int(m["seed"]),
        "grid": n,
        "spacing": sp,
        "extent": (n - 1) * sp,
        "numUav": int(m["numUav"]),
        "victims": victims or [[num("victimX"), num("victimY")]],
        "clutter": clutter,
        "fix": [num("reportedX"), num("reportedY")],
        "module": cfg.get("module", "?"),
        "traj": traj,
        "ev": ev,
        "nodes": nodes,
        "metrics": {
            "tFix": num("timeToFixAtBS_s"),
            "tReport": num("timeToReportAtBS_s"),
            "victimsLocated": num("victimsLocated"),
            "victimCount": num("victimCount"),
            "wrongFixes": num("wrongFixes"),
            "energyKJ": round(num("uavEnergyJ") / 1000.0, 1),
            "pkt": num("pktSent"),
            "err": num("reportErr_m"),
        },
    }


HTML = r"""<!doctype html>
<meta charset="utf-8">
<title>UAV-SAR — 3D replay</title>
<style>
:root{--bg:#0d1014;--pan:#161b22;--ln:#232b36;--tx:#e7ecf2;--tx2:#93a1b1;
      --fast:#4aa3ff;--data:#2ed3a0;--vic:#ff5f56;--clu:#c07ae8;--bs:#f0e9d8;
      --warn:#ffb020;--ok:#35c07e;--cue:#8a7b2e;--hot:#ffd63d;--done:#2ed3a0}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--tx);
     font:13px/1.5 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
#wrap{display:flex;height:100vh}
#view{flex:1;position:relative;min-width:0}
canvas{display:block;width:100%;height:100%;cursor:grab}
canvas:active{cursor:grabbing}
#side{width:270px;flex:none;background:var(--pan);border-left:1px solid var(--ln);
      padding:14px;overflow:auto}
h1{font-size:14px;margin:0 0 2px}
.sub{color:var(--tx2);font-size:11px;margin-bottom:12px}
.grp{margin-bottom:14px}
.grp h2{font-size:11px;text-transform:uppercase;letter-spacing:.08em;
        color:var(--tx2);margin:0 0 6px;font-weight:600}
button{background:#1e2632;color:var(--tx);border:1px solid var(--ln);
       border-radius:6px;padding:5px 9px;font:inherit;font-size:12px;cursor:pointer;
       margin:0 4px 4px 0}
button:hover{border-color:#3a4553}
button.on{background:#2a63a8;border-color:#3a7fd0}
.tile{display:flex;justify-content:space-between;padding:2px 0;
      border-bottom:1px solid var(--ln);font-size:12px}
.tile b{font-variant-numeric:tabular-nums}
.k{color:var(--tx2)}
.it{display:flex;align-items:center;gap:7px;margin:3px 0;font-size:12px}
.sw{width:13px;height:13px;border-radius:3px;flex:none}
.sw.ring{background:transparent;border:2px solid var(--vic);border-radius:50%}
.sw.dash{background:transparent;border:2px dashed var(--clu);border-radius:50%}
#bar{position:absolute;left:0;right:0;bottom:0;padding:10px 14px;
     background:linear-gradient(transparent,rgba(13,16,20,.92) 35%);
     display:flex;gap:10px;align-items:center}
#bar input[type=range]{flex:1}
#clock{font-variant-numeric:tabular-nums;min-width:86px;font-size:12px;color:var(--tx2)}
#hint{position:absolute;top:10px;left:14px;font-size:11px;color:var(--tx2)}
label.sl{display:flex;align-items:center;gap:6px;font-size:11px;color:var(--tx2);
         margin:4px 0}
label.sl input{flex:1}
</style>
<div id=wrap>
  <div id=view>
    <canvas id=c></canvas>
    <div id=hint>kéo để xoay · lăn chuột để phóng · shift+kéo để dịch</div>
    <div id=bar>
      <button id=play>▶</button>
      <input id=scrub type=range min=0 max=1000 value=0>
      <span id=clock>0.0 s</span>
    </div>
  </div>
  <div id=side>
    <h1 id=title></h1>
    <div class=sub id=subtitle></div>
    <div class=grp><h2>Nhánh</h2><div id=schemes></div></div>
    <div class=grp><h2>Chú giải</h2>
      <div class=it><span class="sw" style="background:var(--fast)"></span>FAST — cánh cố định, mức trên</div>
      <div class=it><span class="sw" style="background:var(--data)"></span>DATA — rotary-wing, mức dưới</div>
      <div class=it><span class="sw ring"></span>nạn nhân thật</div>
      <div class=it><span class="sw dash"></span>vật gây nhầm</div>
      <div class=it><span class="sw" style="background:var(--bs)"></span>trạm gốc</div>
      <div class=it><span class="sw" style="background:var(--warn)"></span>giao hàng / xác nhận</div>
      <div class=it><span class="sw" style="background:var(--cue)"></span>nút đã nhận mảnh cue</div>
      <div class=it><span class="sw" style="background:var(--hot)"></span>nút đã BÁO bằng chứng</div>
      <div class=it><span class="sw" style="background:var(--done)"></span>nút giữ ĐỦ bộ dữ liệu</div>
    </div>
    <div class=grp><h2>Hiển thị</h2>
      <label class=sl>cao độ ×<input id=zex type=range min=1 max=10 step=.5 value=4></label>
      <button id=btrail class=on>vệt bay</button>
      <button id=bdrop class=on>đường rọi</button>
      <button id=bgrid class=on>lưới nút</button>
      <div id=ncount style="font-size:11px;color:var(--tx2);margin-top:4px"></div>
    </div>
    <div class=grp><h2>Kết quả</h2><div id=stats></div></div>
    <div class=grp><h2>Sự kiện gần đây</h2><div id=log style="font-size:11px;color:var(--tx2)"></div></div>
  </div>
</div>
<script>
const RUNS = __DATA__;
let ri = 0, R = RUNS[0];
const cv = document.getElementById('c'), ctx = cv.getContext('2d');
let W = 0, H = 0, DPR = Math.min(2, window.devicePixelRatio || 1);

// ---- camera ---------------------------------------------------------------
let az = -0.7, el = 0.62, dist = 1.0, panx = 0, pany = 0, zex = 4;
function css(v){return getComputedStyle(document.documentElement).getPropertyValue(v).trim();}

function resize(){
  W = cv.clientWidth; H = cv.clientHeight;
  cv.width = W * DPR; cv.height = H * DPR;
  ctx.setTransform(DPR,0,0,DPR,0,0);
}
window.addEventListener('resize', ()=>{resize(); draw();});

function project(x, y, z){
  const E = R.extent, cx = E/2, cy = E/2;
  let dx = x - cx, dy = y - cy, dz = z * zex;
  const ca = Math.cos(az), sa = Math.sin(az);
  let x1 =  dx*ca + dy*sa;
  let y1 = -dx*sa + dy*ca;
  const ce = Math.cos(el), se = Math.sin(el);
  const depthY =  y1*ce + dz*se;
  const upZ    = -y1*se + dz*ce;
  const D = E*1.9*dist - depthY;
  if (D < 20) return null;
  const f = Math.min(W,H) * 1.15;
  return [W/2 + panx + x1*f/D, H/2 + pany - upZ*f/D, D];
}

function line(a, b, col, w, alpha){
  const p = project(a[0],a[1],a[2]), q = project(b[0],b[1],b[2]);
  if(!p||!q) return;
  ctx.globalAlpha = alpha===undefined?1:alpha;
  ctx.strokeStyle = col; ctx.lineWidth = w||1;
  ctx.beginPath(); ctx.moveTo(p[0],p[1]); ctx.lineTo(q[0],q[1]); ctx.stroke();
  ctx.globalAlpha = 1;
}
function dot(x,y,z,r,col,alpha){
  const p = project(x,y,z); if(!p) return;
  const s = r * (Math.min(W,H)*1.15) / p[2] * 6;
  ctx.globalAlpha = alpha===undefined?1:alpha;
  ctx.fillStyle = col; ctx.beginPath();
  ctx.arc(p[0],p[1],Math.max(1.1,s),0,6.284); ctx.fill();
  ctx.globalAlpha = 1;
}
function ring(x,y,r,col,dash){
  ctx.strokeStyle = col; ctx.lineWidth = 2; ctx.setLineDash(dash?[5,4]:[]);
  ctx.beginPath();
  let first = true;
  for(let a=0;a<=6.30;a+=0.18){
    const p = project(x+r*Math.cos(a), y+r*Math.sin(a), 0);
    if(!p){first=true;continue;}
    if(first){ctx.moveTo(p[0],p[1]);first=false;} else ctx.lineTo(p[0],p[1]);
  }
  ctx.stroke(); ctx.setLineDash([]);
}
function label(x,y,z,txt,col){
  const p = project(x,y,z); if(!p) return;
  ctx.fillStyle = col; ctx.font = '11px ui-monospace,monospace';
  ctx.fillText(txt, p[0]+8, p[1]+4);
}

// ---- state ----------------------------------------------------------------
let T = 0, TMAX = 1, playing = false, showTrail = true, showDrop = true, showGrid = true;
function horizon(){
  let m = 1;
  for(const u in R.traj){const p = R.traj[u].p; if(p.length) m = Math.max(m, p[p.length-1][0]);}
  for(const e of R.ev) m = Math.max(m, e[0]);
  return m;
}
function posAt(p, t){
  if(!p.length) return null;
  if(t <= p[0][0]) return p[0];
  let lo=0, hi=p.length-1;
  while(lo<hi-1){const mid=(lo+hi)>>1; if(p[mid][0]<=t) lo=mid; else hi=mid;}
  const a=p[lo], b=p[hi];
  if(t>=b[0]) return b;
  const k=(t-a[0])/Math.max(1e-6,b[0]-a[0]);
  return [t, a[1]+(b[1]-a[1])*k, a[2]+(b[2]-a[2])*k, a[3]+(b[3]-a[3])*k];
}

function draw(){
  ctx.clearRect(0,0,W,H);
  const E = R.extent, sp = R.spacing;

  // ground frame
  const corners = [[0,0],[E,0],[E,E],[0,E]];
  ctx.strokeStyle = '#2c3644'; ctx.lineWidth = 1.5;
  for(let i=0;i<4;i++) line([corners[i][0],corners[i][1],0],
                            [corners[(i+1)%4][0],corners[(i+1)%4][1],0], '#2c3644', 1.5);
  // ground grid lines every 5 cells
  const step = sp*5;
  for(let g=0; g<=E+1; g+=step){
    line([g,0,0],[g,E,0],'#1c2430',1,0.9);
    line([0,g,0],[E,g,0],'#1c2430',1,0.9);
  }
  // sensors, coloured by how much of the reference dataset they hold
  const nst = new Map();
  for(const n of R.nodes){ if(n[0] > T) break; nst.set(n[1]+'|'+n[2], n[3]); }
  if(showGrid){
    for(let i=0;i<R.grid;i+=1) for(let j=0;j<R.grid;j+=1){
      const x=i*sp, y=j*sp, lv=nst.get(x.toFixed(1)+'|'+y.toFixed(1));
      if(lv===undefined){ if((i+j)%2) continue;   // decimate the inert ones only
                          dot(x,y,0,0.05,'#33404f',0.8); continue; }
      if(lv===1) dot(x,y,0,0.07,css('--cue'),0.85);
      else if(lv===2) dot(x,y,0,0.10,css('--hot'),1);
      else dot(x,y,0,0.12,css('--done'),1);
    }
  }
  // world objects
  for(const c of R.clutter){ ring(c[0],c[1],26,css('--clu'),true);
                             label(c[0],c[1],0,'s='+c[2],css('--clu')); }
  R.victims.forEach((v,i)=>{ ring(v[0],v[1],26,css('--vic'),false);
                             ring(v[0],v[1],44,css('--vic'),false);
                             label(v[0],v[1],0,'V'+(i+1),css('--vic')); });
  // BS
  const bp = project(0,0,0);
  if(bp){ ctx.fillStyle = css('--bs'); ctx.fillRect(bp[0]-4,bp[1]-4,8,8); }

  // trails + current positions, far to near
  const items = [];
  for(const u in R.traj){
    const tr = R.traj[u], col = tr.role==='FAST'?css('--fast'):css('--data');
    if(showTrail){
      let prev = null;
      for(const q of tr.p){
        if(q[0] > T) break;
        if(prev) line([prev[1],prev[2],prev[3]],[q[1],q[2],q[3]],col,1.6,0.5);
        prev = q;
      }
    }
    const now = posAt(tr.p, T);
    if(now){
      const p = project(now[1],now[2],now[3]);
      if(p) items.push({d:p[2], f:()=>{
        if(showDrop) line([now[1],now[2],0],[now[1],now[2],now[3]],col,1,0.35);
        dot(now[1],now[2],0,0.03,col,0.35);
        dot(now[1],now[2],now[3],0.11,col,1);
        label(now[1],now[2],now[3], tr.role+' '+u, col);
      }});
    }
  }
  // recent events as pulses
  for(const e of R.ev){
    if(e[0] > T || T - e[0] > 14) continue;
    const age = (T-e[0])/14;
    let col = css('--warn');
    if(e[2]==='confirm') col = css('--ok');
    else if(e[2]==='reject') col = css('--clu');
    else if(e[2]==='summon_start') col = css('--vic');
    else if(e[2]==='report_rx'||e[2]==='fix_rx') col = css('--bs');
    const z = e[5]||0;
    const p = project(e[3],e[4],z);
    if(p) items.push({d:p[2], f:()=>{
      dot(e[3],e[4],z, 0.09*(1-age)+0.03, col, 1-age*0.85);
    }});
  }
  items.sort((a,b)=>b.d-a.d).forEach(i=>i.f());

  let c1=0,c2=0,c3=0;
  nst.forEach(v=>{ if(v===1)c1++; else if(v===2)c2++; else c3++; });
  document.getElementById('ncount').textContent =
    `cue ${c1} · báo ${c2} · đủ dữ liệu ${c3}`;
  document.getElementById('clock').textContent = T.toFixed(1)+' s';
  document.getElementById('scrub').value = Math.round(T/TMAX*1000);
  const L = R.ev.filter(e=>e[0]<=T).slice(-7).reverse()
    .map(e=>`${e[0].toFixed(0)}s · ${e[1]} · ${e[2]}${e[6]?' · '+e[6]:''}`).join('<br>');
  document.getElementById('log').innerHTML = L;
}

function stats(){
  const m = R.metrics;
  const row=(k,v)=>`<div class=tile><span class=k>${k}</span><b>${v}</b></div>`;
  document.getElementById('stats').innerHTML =
    row('nạn nhân định vị', `${m.victimsLocated}/${m.victimCount}`) +
    row('toạ độ sai người', m.wrongFixes) +
    row('thời gian tới toạ độ', m.tFix>0?m.tFix.toFixed(1)+' s':'—') +
    row('sai số', m.err>=0?m.err.toFixed(1)+' m':'—') +
    row('năng lượng', m.energyKJ+' kJ') +
    row('gói tin', m.pkt);
  document.getElementById('title').textContent = R.label;
  document.getElementById('subtitle').textContent =
    `${R.scheme} · seed ${R.seed} · ${R.grid}×${R.grid} @ ${R.spacing} m · ${R.numUav} UAV`;
}

function setRun(i){
  ri = i; R = RUNS[i]; TMAX = horizon(); T = 0;
  document.querySelectorAll('#schemes button').forEach((b,k)=>b.classList.toggle('on',k===i));
  stats(); draw();
}

// ---- interaction ----------------------------------------------------------
let drag = null;
cv.addEventListener('mousedown', e=>{drag={x:e.clientX,y:e.clientY,sh:e.shiftKey};});
window.addEventListener('mouseup', ()=>{drag=null;});
window.addEventListener('mousemove', e=>{
  if(!drag) return;
  const dx = e.clientX-drag.x, dy = e.clientY-drag.y;
  drag.x = e.clientX; drag.y = e.clientY;
  if(drag.sh){ panx += dx; pany += dy; }
  else { az -= dx*0.006; el = Math.max(0.05, Math.min(1.45, el + dy*0.005)); }
  draw();
});
cv.addEventListener('wheel', e=>{
  e.preventDefault();
  dist = Math.max(0.25, Math.min(3.0, dist * (1 + Math.sign(e.deltaY)*0.1)));
  draw();
}, {passive:false});

document.getElementById('scrub').addEventListener('input', e=>{
  T = e.target.value/1000*TMAX; draw();
});
document.getElementById('play').addEventListener('click', ()=>{
  playing = !playing;
  document.getElementById('play').textContent = playing?'❚❚':'▶';
});
document.getElementById('zex').addEventListener('input', e=>{zex=+e.target.value; draw();});
for(const [id,set] of [['btrail',v=>showTrail=v],['bdrop',v=>showDrop=v],['bgrid',v=>showGrid=v]]){
  document.getElementById(id).addEventListener('click', e=>{
    const on = !e.target.classList.contains('on');
    e.target.classList.toggle('on', on); set(on); draw();
  });
}
document.getElementById('schemes').innerHTML =
  RUNS.map((r,i)=>`<button>${r.label}</button>`).join('');
document.querySelectorAll('#schemes button').forEach((b,i)=>b.onclick=()=>setRun(i));

let last = performance.now();
function loop(now){
  const dt = (now-last)/1000; last = now;
  if(playing){ T += dt*8; if(T>TMAX){T=0;} draw(); }
  requestAnimationFrame(loop);
}
resize(); setRun(0); requestAnimationFrame(loop);
</script>
"""


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    out = sys.argv[1]
    runs = []
    for spec in sys.argv[2:]:
        if "=" not in spec:
            raise SystemExit(f"expected LABEL=RUNDIR, got {spec}")
        label, d = spec.split("=", 1)
        runs.append(load(label, d))
    html = HTML.replace("__DATA__", json.dumps(runs, separators=(",", ":")))
    with open(out, "w") as f:
        f.write(html)
    print(f"{out}  ({len(html)//1024} KB, {len(runs)} runs)")


if __name__ == "__main__":
    main()
