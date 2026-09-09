"""Step-through HTML for PA1: PHA 0 (P0.0-P0.6) -> T0 -> T1.

Seven steps, each showing what that stage DECIDED. The flight model is the thing
to look at: rows, offsets, and the weave that reaches the heads.

    python3 tools/make_pa1_steps.py OUT.html LABEL=RUNDIR [LABEL=RUNDIR ...]
"""
import csv, json, math, os, sys


def rows(d, n):
    p = os.path.join(d, n)
    return list(csv.DictReader(open(p))) if os.path.exists(p) else []


def load(d):
    C = {r["key"]: r["value"] for r in rows(d, "config.csv")}
    psi = math.radians(float(C["psiDeg"]))
    rowPitch = float(C["rowPitch"])
    a = float(C["cellPitch"])

    def to_row(x, y):
        return (math.cos(psi) * x + math.sin(psi) * y,
                -math.sin(psi) * x + math.cos(psi) * y)

    def to_world(u, w):
        return (math.cos(psi) * u - math.sin(psi) * w,
                math.sin(psi) * u + math.cos(psi) * w)

    cells = [{"id": int(c["id"]), "row": int(c["row"]),
              "x": float(c["cx"]), "y": float(c["cy"]),
              "served": c["class"] == "served",
              "hx": float(c["headX"]), "hy": float(c["headY"]),
              "off": float(c["headOffset"]), "soff": float(c["headSignedOffset"]),
              "cams": int(c["cameras"]), "elig": int(c["eligible"]),
              "files": int(c["files"]), "theta": float(c["theta"]),
              "weaveS": float(c["weaveS"]), "doseS": float(c["doseS"]),
              "orbits": int(c["orbits"])} for c in rows(d, "cells.csv")]
    nodes = [{"x": float(n["x"]), "y": float(n["y"]),
              "cam": n["camera"] == "1", "elig": n["eligible"] == "1"}
             for n in rows(d, "nodes.csv")]
    rws = [{"row": int(r["row"]), "w": float(r["w"]),
            "x0": float(r["x0"]), "y0": float(r["y0"]),
            "x1": float(r["x1"]), "y1": float(r["y1"]),
            "len": float(r["lengthM"]), "svc": float(r["serviceS"]),
            "heads": int(r["heads"])} for r in rows(d, "rows.csv")]
    part = {}
    for p in rows(d, "partition.csv"):
        part.setdefault(p["method"], {})[int(p["row"])] = int(p["vehicle"])
    summ = [{"m": r["method"], "M": int(r["M"]), "mk": float(r["makespanS"]),
             "imb": float(r["imbalancePct"]), "ch": float(r["changeS"]),
             "dp": float(r["depotS"])} for r in rows(d, "partsummary.csv")]

    # Two weave paths per row, both sampled here so the page draws data not maths:
    #   spec  -- the 2a-wavelength sinusoid the cost formula assumes
    #   real  -- a smooth path through the heads where they actually are
    weave = {}
    for rw in rws:
        seq = sorted((to_row(c["hx"], c["hy"])[0], c["soff"])
                     for c in cells if c["row"] == rw["row"] and c["served"])
        if len(seq) < 2:
            continue
        u0, u1 = seq[0][0], seq[-1][0]
        spec, real = [], []
        N = 260
        for k in range(N + 1):
            u = u0 + (u1 - u0) * k / N
            # spec: |offset| of the nearest head, swung as a full 2a-period sine
            j = min(range(len(seq)), key=lambda i: abs(seq[i][0] - u))
            spec.append(to_world(u, rw["w"] + abs(seq[j][1]) *
                                 math.sin(math.pi * (u - u0) / a)))
            # real: half-cosine between consecutive heads, through their signs
            i = 0
            while i + 1 < len(seq) and seq[i + 1][0] < u:
                i += 1
            if i + 1 < len(seq):
                ua, da = seq[i]
                ub, db = seq[i + 1]
                t = (u - ua) / (ub - ua) if ub > ua else 0.0
                t = max(0.0, min(1.0, t))
                w = da + (db - da) * (1 - math.cos(math.pi * t)) / 2
            else:
                w = seq[-1][1]
            real.append(to_world(u, rw["w"] + w))
        weave[rw["row"]] = {"spec": spec, "real": real}

    wc = rows(d, "weavecheck.csv")
    return {"cfg": C, "cells": cells, "nodes": nodes, "rows": rws,
            "hull": [[float(p["x"]), float(p["y"])] for p in rows(d, "hull.csv")],
            "part": part, "summ": summ, "weave": weave,
            "alt": int(wc[0]["alternating"]) if wc else 0,
            "pairs": int(wc[0]["pairs"]) if wc else 0}


HTML = r"""<title>PA1 — lập kế hoạch bay từng bước</title>
<style>
:root{--ink:#12151a;--dim:#5b6472;--line:#dfe3e9;--bg:#f7f8fa;--card:#fff;
 --a:#2f6fd0;--b:#e08a1e;--c:#b9c0cb;--ok:#1f9d6b;--bad:#c2410c}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){
 --ink:#e8ecf2;--dim:#9aa4b2;--line:#2a3038;--bg:#12151a;--card:#1a1f26}}
:root[data-theme=dark]{--ink:#e8ecf2;--dim:#9aa4b2;--line:#2a3038;--bg:#12151a;--card:#1a1f26}
body{background:var(--bg);color:var(--ink);margin:0;padding:18px;
 font:14px/1.55 system-ui,-apple-system,sans-serif}
h1{font-size:17px;margin:0 0 2px} h2{font-size:15px;margin:2px 0 6px}
.sub{color:var(--dim);font-size:12.5px;margin-bottom:14px}
.wrap{display:flex;gap:16px;flex-wrap:wrap;align-items:flex-start}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}
.map{width:664px;max-width:96vw;box-sizing:border-box}
.side{width:400px;max-width:96vw}
canvas{display:block;border-radius:6px;max-width:100%;height:auto}
.ctl{display:flex;gap:8px;align-items:center;margin-top:10px;flex-wrap:wrap}
button,select{font:inherit;padding:5px 11px;border:1px solid var(--line);
 border-radius:7px;background:var(--card);color:var(--ink);cursor:pointer}
button:hover{border-color:var(--dim)} button:disabled{opacity:.4;cursor:default}
.steps{display:flex;gap:5px;flex-wrap:wrap;margin-bottom:12px}
.chip{font-size:11.5px;padding:3px 9px;border-radius:20px;border:1px solid var(--line);
 color:var(--dim);cursor:pointer;white-space:nowrap}
.chip.on{background:var(--ink);color:var(--card);border-color:var(--ink)}
.chip.done{border-color:var(--dim);color:var(--ink)}
.body{font-size:13px;color:var(--dim);line-height:1.65}
.body b{color:var(--ink);font-weight:600}
table{border-collapse:collapse;font-size:12.5px;margin-top:10px;width:100%}
th,td{padding:3px 8px;text-align:right;border-bottom:1px solid var(--line)}
th{color:var(--dim);font-weight:500} td:first-child,th:first-child{text-align:left}
.leg{display:flex;gap:12px;flex-wrap:wrap;font-size:11.5px;color:var(--dim);margin-top:8px}
.sw{display:inline-block;width:11px;height:11px;border-radius:3px;vertical-align:-1px;margin-right:4px}
</style>
<h1>PA1 — lập kế hoạch bay cho đội cánh bằng, từng bước</h1>
<div class=sub id=sub></div>
<div class=steps id=chips></div>
<div class=wrap>
 <div class="card map">
  <canvas id=cv width=640 height=640></canvas>
  <div class=ctl>
   <button id=prev>‹ lùi</button><button id=next>tiếp ›</button>
   <select id=which></select><span class=leg id=leg></span>
  </div>
 </div>
 <div class="card side"><h2 id=h2></h2><div class=body id=txt></div><div id=tb></div></div>
</div>
<script>
const DATA=__DATA__;
const STEPS=[
 ["0 · P0.0/P0.1 — miền & hướng quét ψ","field"],
 ["1 · P0.2 — lưới XOAY theo ψ, đường hàng","grid"],
 ["2 · P0.4 — độ lệch δ và dải δ_max","offset"],
 ["3 · P0.5 — bầu CH có ý thức đường bay","head"],
 ["4 · P0.6/T0 — θ và chi phí phục vụ","demand"],
 ["5 · Đường lượn bám — spec vs thật","weave"],
 ["6 · T1 — chia HÀNG cho các UAV","part"]];
const sel=document.getElementById('which');
Object.keys(DATA).forEach(k=>sel.add(new Option(k,k)));
let R=DATA[sel.value], S=0, METHOD='credit-free';
const cv=document.getElementById('cv'), g=cv.getContext('2d');
const VEH=['#12151a','#7c3aed','#0e7490','#a16207','#be123c'];
const css=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();
let TX=x=>x, TY=y=>y, SC=1;
function fit(){
 let lo=[1e18,1e18],hi=[-1e18,-1e18];
 for(const p of R.hull){lo[0]=Math.min(lo[0],p[0]);lo[1]=Math.min(lo[1],p[1]);
  hi[0]=Math.max(hi[0],p[0]);hi[1]=Math.max(hi[1],p[1]);}
 const pad=30, w=hi[0]-lo[0], h=hi[1]-lo[1];
 SC=Math.min((cv.width-2*pad)/w,(cv.height-2*pad)/h);
 const ox=(cv.width-w*SC)/2, oy=(cv.height-h*SC)/2;
 TX=x=>ox+(x-lo[0])*SC; TY=y=>cv.height-(oy+(y-lo[1])*SC);
}
function poly(pts,col,w,alpha,close){g.save();g.globalAlpha=alpha;g.strokeStyle=col;
 g.lineWidth=w;g.lineJoin='round';g.beginPath();
 pts.forEach((p,i)=>i?g.lineTo(TX(p[0]),TY(p[1])):g.moveTo(TX(p[0]),TY(p[1])));
 if(close)g.closePath(); g.stroke();g.restore();}
function dot(x,y,r,col,rim){g.fillStyle=col;g.beginPath();g.arc(TX(x),TY(y),r,0,7);g.fill();
 if(rim){g.strokeStyle=rim;g.lineWidth=1.4;g.stroke();}}

function draw(){
 fit(); const key=STEPS[S][1];
 g.clearRect(0,0,cv.width,cv.height);
 g.fillStyle=css('--card');g.fillRect(0,0,cv.width,cv.height);
 poly(R.hull,css('--ink'),1.6,key==='field'?1:0.30,true);

 if(key==='field'){
  // the minimum-width direction, drawn as the pair of supporting lines
  const psi=+R.cfg.psiDeg*Math.PI/180, cx=R.hull.reduce((s,p)=>s+p[0],0)/R.hull.length,
        cy=R.hull.reduce((s,p)=>s+p[1],0)/R.hull.length, L=1e4;
  g.save();g.setLineDash([7,5]);g.globalAlpha=.85;g.strokeStyle=css('--a');g.lineWidth=2;
  g.beginPath();g.moveTo(TX(cx-L*Math.cos(psi)),TY(cy-L*Math.sin(psi)));
  g.lineTo(TX(cx+L*Math.cos(psi)),TY(cy+L*Math.sin(psi)));g.stroke();g.restore();
 }
 if(key!=='field'){
  for(const rw of R.rows){
   const inBand = key==='offset';
   if(inBand){
    // the delta_max band: everything the aircraft can weave out to
    const d=+R.cfg.maxOffset, psi=+R.cfg.psiDeg*Math.PI/180;
    const nx=-Math.sin(psi), ny=Math.cos(psi);
    g.save();g.globalAlpha=.13;g.fillStyle=css('--ok');g.beginPath();
    g.moveTo(TX(rw.x0+nx*d),TY(rw.y0+ny*d));g.lineTo(TX(rw.x1+nx*d),TY(rw.y1+ny*d));
    g.lineTo(TX(rw.x1-nx*d),TY(rw.y1-ny*d));g.lineTo(TX(rw.x0-nx*d),TY(rw.y0-ny*d));
    g.closePath();g.fill();g.restore();
   }
   let col=css('--dim'), wid=1.4, al=.6;
   if(key==='part'){const v=R.part[METHOD]?R.part[METHOD][rw.row]:undefined;
    if(v!==undefined){col=VEH[v%VEH.length];wid=3.4;al=1;}}
   poly([[rw.x0,rw.y0],[rw.x1,rw.y1]],col,wid,al,false);
  }
 }
 if(key==='grid'||key==='offset'||key==='head'||key==='demand'){
  for(const n of R.nodes){
   const c = !n.cam?css('--c') : (n.elig?css('--a'):css('--bad'));
   g.globalAlpha=key==='offset'?.85:.45; dot(n.x,n.y,1.6,c); g.globalAlpha=1;
  }
 }
 if(key==='offset'){
  for(const c of R.cells){ if(!c.served) continue;
   g.save();g.globalAlpha=.55;g.strokeStyle=css('--ink');g.lineWidth=1;
   const psi=+R.cfg.psiDeg*Math.PI/180, nx=-Math.sin(psi), ny=Math.cos(psi);
   const base=[c.hx-nx*c.soff, c.hy-ny*c.soff];
   g.beginPath();g.moveTo(TX(base[0]),TY(base[1]));g.lineTo(TX(c.hx),TY(c.hy));g.stroke();g.restore();}
 }
 if(key==='head'||key==='demand'||key==='weave'||key==='part'){
  const tmax=Math.max(...R.cells.filter(c=>c.served).map(c=>c.theta),1);
  for(const c of R.cells){
   if(!c.served){ dot(c.x,c.y,5,css('--bad'),css('--card')); continue; }
   let r=5;
   if(key==='demand') r=3.5+5*c.theta/tmax;
   dot(c.hx,c.hy,r,c.orbits&&key==='demand'?css('--b'):css('--ok'),css('--card'));
  }
 }
 if(key==='weave'){
  for(const k in R.weave){
   poly(R.weave[k].spec,css('--bad'),1.6,.75,false);
   poly(R.weave[k].real,css('--ok'),2.2,1,false);
  }
 }
 document.getElementById('sub').textContent =
  `${R.cfg.grid}x${R.cfg.grid} nút · R_c=${(+R.cfg.cellRadius).toFixed(0)}m (${(R.cfg.cellRadius/R.cfg.turnRadius).toFixed(2)}ρ)`+
  ` · a=${(+R.cfg.cellPitch).toFixed(0)}m · h=${(+R.cfg.rowPitch).toFixed(0)}m`+
  ` · δ_max=${(+R.cfg.maxOffset).toFixed(1)}m · ρ=${(+R.cfg.turnRadius).toFixed(1)}m`+
  ` · ψ=${(+R.cfg.psiDeg).toFixed(1)}°`;
}

function panel(){
 const C=R.cfg, key=STEPS[S][1];
 document.getElementById('h2').textContent=STEPS[S][0];
 const served=R.cells.filter(c=>c.served).length, orb=R.cells.filter(c=>c.orbits>0).length;
 const wS=R.cells.reduce((s,c)=>s+c.weaveS,0), dS=R.cells.reduce((s,c)=>s+c.doseS,0);
 const T={
 field:`Đơn giản hoá biên rồi lấy <b>bao lồi</b> (P0.0), rồi chọn <b>ψ</b> = phương vuông góc với <b>bề rộng nhỏ nhất</b>, bằng rotating calipers (P0.1).<br><br>Vì sao là bề rộng nhỏ nhất: chi phí mỗi lần rẽ <b>không phụ thuộc ψ</b> (h từ lưới, ρ từ khí động), và tổng độ dài hàng ≈ diện tích/h cũng không. Thứ duy nhất ψ đổi là <b>số hàng</b>.<br><br>min chi phí rẽ ⟺ min số hàng ⟺ <b>min bề rộng ⊥ ψ</b>.<br><br>Bề rộng nhỏ nhất <b>${(+C.minWidth).toFixed(1)} m</b>, diện tích ${(+C.area/1e4).toFixed(1)} ha, ψ = ${(+C.psiDeg).toFixed(1)}°.`,
 grid:`Lát lưới lục giác <b>XOAY theo ψ</b> để một trong ba họ hàng nằm dọc ψ (P0.2). Lưới xoay tự do nên <b>không có phạt lượng tử hoá 60°</b>.<br><br>Toán hex chạy <b>trong hệ hàng</b>, nên chỉ số axial <code>r</code> <b>chính là</b> chỉ số hàng — không phải khôi phục lại sau.<br><br><b>${R.cells.length} ô</b> trên <b>${R.rows.length} hàng</b>, cách nhau h = ${(+C.rowPitch).toFixed(0)} m.<br><br>Trạm gốc chỉ phát ⟨ψ, R_c, o⟩ — <b>vài byte</b>, và đó là toàn bộ chi phí phối hợp của Pha 0.`,
 offset:`Mỗi nút <b>tự tính</b> ô, đường hàng, và độ lệch δ (P0.4) — không trao đổi bản tin nào.<br><br>Dải xanh là <b>δ_max = a²/(π²ρ) = ${(+C.maxOffset).toFixed(1)} m</b>: xa hơn thế thì UAV <b>không bẻ lái nổi</b> để bám, và phải rẽ Dubins thật ra khỏi hàng.<br><br>Nút <b>xanh</b> đủ điều kiện, <b>đỏ</b> có camera nhưng ngoài dải, <b>xám</b> không camera.<br><br>δ_max/R_c = 3R_c/(π²ρ) = <b>${(C.maxOffset/C.cellRadius*1).toFixed(3)}</b> — <b>không phải hằng số</b>: bằng 4/π²=0.405 đúng tại điểm thiết kế R_c=4ρ/3, và lớn dần theo R_c.`,
 head:`<b>n* = argmin  c(θ(I<sub>ν</sub>)) + π²δ<sub>ν</sub>²/(4a·v)</b>  s.t. δ<sub>ν</sub> ≤ δ_max<br><br><b>Hai số hạng cùng đơn vị GIÂY</b> ⇒ không có trọng số nào để chọn, và do đó không có trọng số nào để bị chê là chỉnh tay. Mọi biến thể LEACH/HEED đều phải chọn một hệ số giữa hai đại lượng không cùng đơn vị.<br><br>Ràng buộc là <b>khả thi động học của phương tiện</b>, không phải sở thích của mạng.<br><br><b>${served}</b> ô có CH, <b>${C.barren}</b> không — trong đó <b>${C.infeasible}</b> là <b>hỏng F1</b>: có camera nhưng <b>không nút nào trong δ_max</b>.<br><br>⚠️ <b>Đo được: số hạng vị trí chỉ chiếm ~1% mục tiêu</b> (tối đa ~2.6% ngay tại δ_max), vì c(θ) cỡ 29 s còn số hạng vị trí cỡ 0.26 s. Nên ở bộ tham số này P0.5 <b>gần như trùng</b> với bầu theo năng lực thuần — <b>ràng buộc cứng δ≤δ_max làm gần hết việc</b>, không phải số hạng vị trí. CH được kéo về hàng chỉ <b>1.08–1.27×</b> so với một nút đủ điều kiện lấy ngẫu nhiên.`,
 demand:`Hai chặng: <b>k<sub>n</sub></b> = số TỆP cần để phân biệt (Chernoff), rồi <b>θ<sub>n</sub></b> = LIỀU cần để gom đủ k tệp trong K, phát mù luân phiên (sưu tầm phiếu).<br><br>Gộp hai thứ vào một số sẽ mất số hạng sưu tầm phiếu — chỗ mà <b>lịch phát</b> đi vào bài toán.<br><br>Bán kính chấm ∝ θ. <b>Cam</b> = phải lượn vòng.<br><br>Sàn Fano 1/(J+1) = <b>${(+C.fanoFloor).toFixed(3)}</b>, mục tiêu lỗi ${(+C.Pe).toFixed(3)} — F2 thoả.<br><br><b>${orb}/${served}</b> CH phải lượn vòng. Chi phí: liều <b>${dS.toFixed(0)} s</b>, lượn bám <b>${wS.toFixed(0)} s</b> (<b>${(100*wS/(wS+dS)).toFixed(0)}%</b>).`,
 weave:`<b>Đỏ</b> = đường mà công thức chi phí <b>giả định</b>: hình sin bước sóng 2a, tức hai CH liên tiếp <b>luôn đổi bên</b>.<br><br><b>Xanh</b> = đường mượt đi qua CH ở <b>đúng chỗ chúng đứng</b>.<br><br>Thực tế hai CH liên tiếp chỉ đổi bên <b>${R.alt}/${R.pairs}</b> lần. Khi cùng bên, UAV <b>không phải cắt ngang</b>, nên đường thật ngắn hơn nhiều — đo được <b>ngắn hơn 2–8×</b>.<br><br>Không phải lỗi: cùng một hình sin cũng sinh ra <b>δ_max</b>, nên spec <b>bảo thủ nhất quán</b> ở cả hai phía — đường dài hơn thực, và ngưỡng δ_max chặt hơn thực. Vì lượn bám chỉ chiếm ${(100*wS/(wS+dS)).toFixed(0)}% chi phí, nó <b>không đổi kết luận nào</b> — nhưng phải phát biểu đúng.`,
 part:`Đơn vị phân hoạch là <b>HÀNG</b>, không phải ô: UAV vào một hàng thì bay hết từ đầu này sang đầu kia, nên hàng <b>không chia được</b>.<br><br>W<sub>r</sub> = Σ c<sub>n</sub> trên hàng + độ dài hàng / v.<br><br><b>Không ép liền khối:</b> chi phí đổi hàng L(|Δr|·h, ρ) <b>không đơn điệu</b> theo |Δr| — dưới 2ρ là rẽ chật và đắt, nên <b>nhảy hàng có thể rẻ hơn</b> lấy hàng kế bên.<br><br>Chỉ có <b>${R.rows.length} hàng</b>, nên khi M tiến gần số hàng thì <b>lệch tải là tất yếu</b>.`};
 document.getElementById('txt').innerHTML=T[key];
 let tb='';
 if(key==='part'){
  tb='<table><tr><th>phương án</th><th>M</th><th>makespan</th><th>lệch</th><th>rẽ hàng</th></tr>';
  for(const r of R.summ) tb+=`<tr><td>${r.m}</td><td>${r.M}</td><td>${r.mk.toFixed(0)}s</td>`+
   `<td>${r.imb.toFixed(1)}%</td><td>${r.ch.toFixed(0)}s</td></tr>`;
  tb+='</table>';
 }
 if(key==='demand'){
  const cs=R.cells.filter(c=>c.served).slice().sort((x,y)=>y.theta-x.theta).slice(0,6);
  tb='<table><tr><th>ô</th><th>k tệp</th><th>θ (kB)</th><th>δ (m)</th><th>lượn vòng</th></tr>';
  for(const c of cs) tb+=`<tr><td>${c.id}</td><td>${c.files}</td>`+
   `<td>${(c.theta/1000).toFixed(0)}</td><td>${c.off.toFixed(1)}</td><td>${c.orbits||'—'}</td></tr>`;
  tb+='</table>';
 }
 document.getElementById('tb').innerHTML=tb;
 const L={offset:'<span><i class=sw style=background:var(--a)></i>trong δ_max</span><span><i class=sw style=background:var(--bad)></i>có camera, ngoài dải</span><span><i class=sw style=background:var(--c)></i>không camera</span>',
  head:'<span><i class=sw style=background:var(--ok)></i>cụm trưởng</span><span><i class=sw style=background:var(--bad)></i>ô không bầu được (F1)</span>',
  demand:'<span>bán kính ∝ θ</span><span><i class=sw style=background:var(--b)></i>phải lượn vòng</span>',
  weave:'<span><i class=sw style=background:var(--bad)></i>spec giả định (sin 2a)</span><span><i class=sw style=background:var(--ok)></i>đường thật qua CH</span>',
  part:'<span>màu = UAV</span>'};
 document.getElementById('leg').innerHTML=L[key]||'';
 document.querySelectorAll('.chip').forEach((c,i)=>{c.className='chip'+(i===S?' on':(i<S?' done':''));});
 document.getElementById('prev').disabled=S===0;
 document.getElementById('next').disabled=S===STEPS.length-1;
}
const chips=document.getElementById('chips');
STEPS.forEach((s,i)=>{const d=document.createElement('span');d.className='chip';
 d.textContent=s[0];d.onclick=()=>{S=i;draw();panel();};chips.appendChild(d);});
document.getElementById('prev').onclick=()=>{if(S>0){S--;draw();panel();}};
document.getElementById('next').onclick=()=>{if(S<STEPS.length-1){S++;draw();panel();}};
document.onkeydown=e=>{if(e.key==='ArrowRight')document.getElementById('next').click();
 if(e.key==='ArrowLeft')document.getElementById('prev').click();};
sel.onchange=()=>{R=DATA[sel.value];draw();panel();};
matchMedia('(prefers-color-scheme:dark)').addEventListener('change',()=>{draw();panel();});
draw();panel();
</script>
"""


def main():
    out, specs = sys.argv[1], sys.argv[2:]
    data = {}
    for sp in specs:
        label, d = sp.split("=", 1)
        data[label] = load(d)
    open(out, "w").write(HTML.replace("__DATA__", json.dumps(data)))
    print(f"  {out}  ({os.path.getsize(out)/1024:.0f} KB, {len(data)} runs)")


if __name__ == "__main__":
    main()
