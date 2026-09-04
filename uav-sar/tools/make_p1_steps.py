"""Step-through HTML: the flight plan being BUILT, one decision at a time.

Eight steps, each showing what that stage decided and what it cost. This is a
different question from the replay -- the replay flies the finished plan, this
one shows how the plan came to exist.

    python3 tools/make_p1_steps.py OUT.html LABEL=RUNDIR [LABEL=RUNDIR ...]
"""
import csv, json, os, sys


def rows(d, n):
    p = os.path.join(d, n)
    return list(csv.DictReader(open(p))) if os.path.exists(p) else []


def load(d):
    C = {r["key"]: r["value"] for r in rows(d, "config.csv")}
    cells = [{"id": int(c["id"]), "x": float(c["cx"]), "y": float(c["cy"]),
              "cls": c["class"], "score": float(c["score"]),
              "suspect": c["suspect"] == "1", "theta": float(c["theta"]),
              "pen": float(c["penaltyS"]), "orbits": int(c["orbits"]),
              "matchers": int(c["matchers"]), "leader": int(c["leader"]),
              "tloc": float(c["tLocal"]),
              "held": float(c.get("held", 0) or 0),
              "verdict": c.get("verdict", "none"),
              # ground truth, for SCORING the verdict only -- the pipeline never
              # reads it. It was missing, and the panel counted `undefined` and
              # reported 0 victims found when the confirmed cell was the right one.
              "real": c["holdsReal"] == "1",
              "obj": c["holdsObject"] == "1"}
             for c in rows(d, "cells.csv")]
    nodes = [{"x": float(n["x"]), "y": float(n["y"]), "m": n["modality"],
              "lead": 0} for n in rows(d, "nodes.csv")]
    leaders = {c["leader"] for c in cells if c["cls"] == "A"}
    for n, raw in zip(nodes, rows(d, "nodes.csv")):
        n["lead"] = 1 if (int(raw["id"]) in leaders) else 0
    part = {int(p["cellId"]): int(p["vehicle"]) for p in rows(d, "stage_partition.csv")}
    tours = {}
    for t in rows(d, "stage_tours.csv"):
        tours.setdefault((t["variant"], int(t["vehicle"])), []).append(
            [float(t["x"]), float(t["y"])])
    hd = {}
    for h in rows(d, "stage_headings.csv"):
        hd.setdefault(int(h["cellId"]), []).append(
            {"deg": float(h["hdgDeg"]), "on": h["chosen"] == "1"})
    veh = {}
    for p in rows(d, "path.csv"):
        veh.setdefault(int(p["vehicle"]), []).append(
            {"x": float(p["x"]), "y": float(p["y"]), "v": float(p["speedMps"])})
    cost = [{"v": int(c["vehicle"]), "nn": float(c["nnM"]), "opt": float(c["optM"]),
             "svc": float(c["serviceS"]), "t": float(c["speedTimeS"]),
             "ok": c["feasible"] == "1"} for c in rows(d, "stage_cost.csv")]
    hist = [{"it": int(h["iteration"]), "mk": float(h["makespanS"]),
             "cells": int(h["planCells"]), "ret": int(h["retired"]),
             "unc": int(h["uncovered"]), "ok": h["valid"] == "1"}
            for h in rows(d, "history.csv")]
    return {"cfg": C, "cells": cells, "nodes": nodes, "part": part,
            "tours": {f"{k[0]}|{k[1]}": v for k, v in tours.items()},
            "hd": hd, "veh": [veh[k] for k in sorted(veh)], "cost": cost,
            "hist": hist,
            "objs": [{"x": float(o["x"]), "y": float(o["y"]),
                      "real": o["real"] == "1"} for o in rows(d, "objects.csv")],
            "rc": float(C["cellRadius"]), "side": float(C["side"]),
            "vmin": float(C["vmin"]), "vmax": float(C["vmax"])}


HTML = r"""<title>Lập kế hoạch bay — từng bước</title>
<style>
:root{--ink:#12151a;--dim:#5b6472;--line:#dfe3e9;--bg:#f7f8fa;--card:#fff;
 --a:#2f6fd0;--b:#e08a1e;--c:#b9c0cb;--real:#1f9d6b;--dec:#c2410c;--warn:#c2410c}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){
 --ink:#e8ecf2;--dim:#9aa4b2;--line:#2a3038;--bg:#12151a;--card:#1a1f26}}
:root[data-theme=dark]{--ink:#e8ecf2;--dim:#9aa4b2;--line:#2a3038;--bg:#12151a;--card:#1a1f26}
body{background:var(--bg);color:var(--ink);margin:0;padding:18px;
 font:14px/1.55 system-ui,-apple-system,sans-serif}
h1{font-size:17px;margin:0 0 2px}
.sub{color:var(--dim);font-size:12.5px;margin-bottom:14px}
.wrap{display:flex;gap:16px;flex-wrap:wrap;align-items:flex-start}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}
.map{width:684px;max-width:96vw;box-sizing:border-box}
canvas{max-width:100%;height:auto}
canvas{display:block;border-radius:6px}
.side{width:380px;max-width:96vw}
.ctl{display:flex;gap:8px;align-items:center;margin-top:10px;flex-wrap:wrap}
button,select{font:inherit;padding:5px 11px;border:1px solid var(--line);
 border-radius:7px;background:var(--card);color:var(--ink);cursor:pointer}
button:hover{border-color:var(--dim)} button:disabled{opacity:.4;cursor:default}
.steps{display:flex;gap:5px;flex-wrap:wrap;margin-bottom:12px}
.chip{font-size:11.5px;padding:3px 9px;border-radius:20px;border:1px solid var(--line);
 color:var(--dim);cursor:pointer;white-space:nowrap}
.chip.on{background:var(--ink);color:var(--card);border-color:var(--ink)}
.chip.done{border-color:var(--dim);color:var(--ink)}
h2{font-size:15px;margin:2px 0 6px}
.body{font-size:13px;color:var(--dim);line-height:1.65}
.body b{color:var(--ink);font-weight:600}
.warn{color:var(--warn)}
table{border-collapse:collapse;font-size:12.5px;margin-top:10px;width:100%}
th,td{padding:3px 8px;text-align:right;border-bottom:1px solid var(--line)}
th{color:var(--dim);font-weight:500} td:first-child,th:first-child{text-align:left}
.leg{display:flex;gap:13px;flex-wrap:wrap;font-size:11.5px;color:var(--dim);margin-top:8px}
.sw{display:inline-block;width:11px;height:11px;border-radius:3px;vertical-align:-1px;margin-right:4px}
</style>
<h1>Lập kế hoạch bay cho đội cánh bằng — từng bước</h1>
<div class=sub id=sub></div>
<div class=steps id=chips></div>
<div class=wrap>
 <div class="card map">
  <canvas id=cv width=660 height=660></canvas>
  <div class=ctl>
   <button id=prev>‹ lùi</button><button id=next>tiếp ›</button>
   <select id=which></select>
   <span class=leg id=leg></span>
  </div>
 </div>
 <div class="card side">
  <h2 id=h2></h2><div class=body id=txt></div><div id=tb></div>
 </div>
</div>
<script>
const DATA=__DATA__;
const STEPS=[
 ["0 · Pha 0 — phân cluster & bầu CH","cells"],
 ["1 · Pha 0 — gán lớp A/B/C","class"],
 ["2 · T0 — nhu cầu θ theo NĂNG LỰC","demand"],
 ["3 · T1 — chia việc cho từng máy bay","part"],
 ["4 · T2 — đường bay thô (NN → 2-opt)","order"],
 ["5 · T2 — rời rạc hoá hướng mũi","head"],
 ["6 · T3 — hồ sơ tốc độ (quy hoạch tuyến tính)","speed"],
 ["7 · T4 — tinh chỉnh","refine"],
 ["8 · UAV BAY & phát → RỒI MỚI có vị trí nghi vấn","fly"]];
const sel=document.getElementById('which');
Object.keys(DATA).forEach(k=>sel.add(new Option(k,k)));
let R=DATA[sel.value], S=0;
const cv=document.getElementById('cv'), g=cv.getContext('2d');
const VEH=['#12151a','#7c3aed','#0e7490','#a16207','#be123c'];
const MOD={visual:'#2f6fd0',thermal:'#c2410c',acoustic:'#7c3aed',none:'#cbd2dc'};
const css=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const PAD=32, sc=()=> (cv.width-2*PAD)/(R.side+2*R.rc);
const tx=x=>PAD+(x+R.rc)*sc(), ty=y=>cv.height-(PAD+(y+R.rc)*sc());
function hex(cx,cy,r){g.beginPath();for(let i=0;i<6;i++){const a=Math.PI/180*(60*i+90);
 const X=cx+r*Math.cos(a),Y=cy+r*Math.sin(a);i?g.lineTo(X,Y):g.moveTo(X,Y);}g.closePath();}
function clsCol(c){return c==='A'?css('--a'):c==='B'?css('--b'):css('--c');}
function objs(){for(const o of R.objs){g.fillStyle=o.real?css('--real'):css('--dec');
 g.beginPath();g.arc(tx(o.x),ty(o.y),o.real?7:5.4,0,7);g.fill();
 g.strokeStyle=css('--ink');g.lineWidth=1.5;g.stroke();}}
function depot(){g.fillStyle=css('--ink');g.fillRect(tx(0)-5,ty(0)-5,10,10);}
function polyline(pts,col,w,alpha){g.save();g.globalAlpha=alpha;g.strokeStyle=col;
 g.lineWidth=w;g.lineJoin='round';g.beginPath();
 pts.forEach((p,i)=>i?g.lineTo(tx(p[0]),ty(p[1])):g.moveTo(tx(p[0]),ty(p[1])));
 g.stroke();g.restore();}
function speedCol(v){const t=Math.max(0,Math.min(1,(v-R.vmin)/(R.vmax-R.vmin)));
 const a=[250,220,60],b=[40,50,110];
 return `rgb(${a.map((q,i)=>Math.round(q+(b[i]-q)*t)).join(',')})`;}

function draw(){
 const S2=sc(), key=STEPS[S][1];
 g.clearRect(0,0,cv.width,cv.height);
 g.fillStyle=css('--card');g.fillRect(0,0,cv.width,cv.height);
 const smax=Math.max(...R.cells.map(c=>c.score),0.001);
 const tmax=Math.max(...R.cells.map(c=>c.theta),1);
 for(const c of R.cells){
  let col=css('--c'), al=0.16;
  if(key==='cells'){col=css('--a');al=0.10;}
  else if(key==='class'){col=clsCol(c.cls);al=0.30;}
  else if(key==='demand'){col=c.theta>0?css('--a'):css('--c');
    al=c.theta>0?0.14+0.55*(c.theta/tmax):0.10;}
  else if(key==='fly'){col=c.verdict==='confirm'?css('--a')
      :c.verdict==='reject'?css('--c'):css('--line');
    al=c.verdict==='confirm'?0.55:0.16;}
  else if(R.part[c.id]!==undefined){col=VEH[R.part[c.id]%VEH.length];al=0.20;}
  else {col=css('--c');al=0.08;}
  g.globalAlpha=al;g.fillStyle=col;hex(tx(c.x),ty(c.y),R.rc*S2);g.fill();g.globalAlpha=1;
  const susp=(key==='fly')&&c.verdict==='confirm';
  g.strokeStyle=susp?css('--ink'):css('--line');g.lineWidth=susp?2.1:0.9;
  hex(tx(c.x),ty(c.y),R.rc*S2);g.stroke();
  if(key==='demand'&&c.orbits>0){g.fillStyle=css('--warn');g.font='11px system-ui';
   g.textAlign='center';g.fillText('↻'+c.orbits,tx(c.x),ty(c.y)+4);}
 }
 if(key==='cells'){
  for(const n of R.nodes){g.fillStyle=MOD[n.m]||'#ccc';
   g.beginPath();g.arc(tx(n.x),ty(n.y),1.5,0,7);g.fill();}
  for(const n of R.nodes) if(n.lead){g.strokeStyle=css('--ink');g.lineWidth=1.4;
   g.beginPath();g.arc(tx(n.x),ty(n.y),5,0,7);g.stroke();}
 }
 if(key==='order'){
  Object.keys(R.tours).forEach(k=>{const [va,vi]=k.split('|');
   if(va==='nn') polyline(R.tours[k],css('--dim'),1.6,0.55);});
  Object.keys(R.tours).forEach(k=>{const [va,vi]=k.split('|');
   if(va==='opt') polyline(R.tours[k],VEH[vi%VEH.length],2.4,1);});
 }
 if(key==='head'||key==='speed'||key==='refine'){
  Object.keys(R.tours).forEach(k=>{const [va,vi]=k.split('|');
   if(va==='opt') polyline(R.tours[k],VEH[vi%VEH.length],2.2,key==='speed'?0.18:1);});
 }
 if(key==='head'){
  for(const c of R.cells){const H=R.hd[c.id]; if(!H) continue;
   for(const h of H){const a=h.deg*Math.PI/180, L=(h.on?36:21);
    g.save();g.globalAlpha=h.on?1:0.42;
    g.strokeStyle=h.on?css('--ink'):css('--dim');g.lineWidth=h.on?2.6:1.4;
    g.beginPath();g.moveTo(tx(c.x),ty(c.y));
    g.lineTo(tx(c.x)+L*Math.cos(a),ty(c.y)-L*Math.sin(a));g.stroke();g.restore();}
   g.fillStyle=css('--ink');g.beginPath();g.arc(tx(c.x),ty(c.y),2.4,0,7);g.fill();}
 }
 if(key==='speed'){
  R.veh.forEach((p,vi)=>{for(let i=0;i+1<p.length;i++){
   g.strokeStyle=speedCol(p[i].v);g.lineWidth=3.4;g.beginPath();
   g.moveTo(tx(p[i].x),ty(p[i].y));g.lineTo(tx(p[i+1].x),ty(p[i+1].y));g.stroke();}});
 }
 objs();depot();
}

function panel(){
 const C=R.cfg, key=STEPS[S][1];
 document.getElementById('h2').textContent=STEPS[S][0];
 const A=R.cells.filter(c=>c.cls==='A').length, B=R.cells.filter(c=>c.cls==='B').length,
   Cc=R.cells.filter(c=>c.cls==='C').length,
   D=R.cells.filter(c=>c.suspect).length,
   need=R.cells.filter(c=>c.theta>0).length,
   orb=R.cells.filter(c=>c.orbits>0).length,
   tl=R.cells.filter(c=>c.cls==='A').map(c=>c.tloc);
 const nn=R.cost.reduce((s,c)=>s+c.nn,0), op=R.cost.reduce((s,c)=>s+c.opt,0);
 const T={
 cells:`Phủ vùng bằng ô lục giác bán kính <b>R_c=${C.cellRadius} m</b>, rồi <b>bầu cụm trưởng theo NĂNG LỰC</b>: phương thức cảm biến là <b>bộ lọc cứng</b>, sau đó mới cân tính toán và tốc độ thu. Cây nội ô dựng <b>từ cụm trưởng đã bầu</b> — bầu vì một lý do rồi định tuyến từ cụm trưởng chọn vì lý do khác thì mọi số đếm chặng sau đó sai.<br><br>Bước hàng <b>h = 1.5·R_c = ${(+C.rowPitch).toFixed(0)} m</b> là đại lượng Pha 0 giao cho Pha 1, và là thứ nối kích thước ô với bán kính lượn <b>ρ = ${(+C.turnRadius).toFixed(1)} m</b>.`,
 class:`Chỉ <b>lớp A</b> tốn thời gian bay. Lớp B phát hiện được nhưng <b>không bao giờ phân biệt được</b> — gửi tham chiếu tới đó mua gì cũng vô ích, nên nó bị <b>loại khỏi bài toán định tuyến</b>. Đây là chỗ sự không đồng nhất của mạng <b>bớt việc</b> cho máy bay chứ không chỉ đổi trọng số.<br><br>A=${A} · B=${B} · C=${Cc}. Phát tham chiếu trong ô mất <b>T_local ${tl.length?(tl.reduce((a,b)=>a+b,0)/tl.length).toFixed(0):0} s trung bình, ${tl.length?Math.max(...tl).toFixed(0):0} s tối đa</b>.`,
 demand:`<b>Chưa có gì được phát hiện.</b> Máy bay chưa cất cánh nên chưa nút nào cầm tham chiếu, nên chưa nút nào nói được ở đó có gì. Tập nghi vấn là <b>ĐẦU RA</b> của Pha 1, không phải đầu vào — planner không được cầm nó.<br><br>Vậy mọi ô lớp A đều hỏi; ô <b>B/C nhận 0</b>.<br><br>θ ∝ <b>1/I_n</b> — cảm biến tốt hơn cần <b>ÍT</b> tham chiếu hơn. Đây là <b>nguồn duy nhất</b> của sự không đồng nhất trong nhu cầu, và là chỗ “mạng không đồng nhất” thành một <b>số hạng trong hàm mục tiêu</b> thay vì một tính từ.<br><br>Rồi θ được quy thành <b>giây bay</b>: bài toán giao dữ liệu liên tục thành bài toán <b>định tuyến tổ hợp</b>. ${need} ô cần phục vụ${orb?`, <b class=warn>${orb} ô phải lượn vòng</b> vì một lượt bay không đủ`:``}.<br><br><b>Liều tỉ lệ NGHỊCH với tốc độ</b> — với phương tiện không treo được, đó là biến điều khiển duy nhất.`,
 part:`Chia ô cho <b>${C.vehicles} máy bay</b>. Chi phí một khối được chấm bằng <b>Dubins</b>, không phải mét đường thẳng, và <b>chân depot nằm TRONG</b> phép cân bằng — cắt tuyến thành cung bằng nhau rồi mới nối depot là cân một đại lượng <b>không ai bay</b>.`,
 order:`Xám nhạt = thứ tự <b>láng giềng gần nhất</b>. Đậm = sau <b>2-opt + Or-opt</b>. Mọi phương án đều chấm bằng <b>đúng cái DP hướng mũi</b> sẽ dùng cho đáp án — chấm phương án bằng thước rẻ rồi chấm người thắng bằng thước thật là cách planner tự tin chọn phương án tệ hơn.<br><br>${nn.toFixed(0)} m → <b>${op.toFixed(0)} m</b> (ngắn hơn ${(100*(nn-op)/nn).toFixed(1)}%).`,
 head:`Với phương tiện không quay tại chỗ, quãng đường giữa hai chỗ <b>phụ thuộc hướng mũi ở CẢ HAI đầu</b> — nên đây không phải TSP metric. Mỗi ô được rời rạc hoá thành <b>8 hướng</b> (vạch mờ); vạch đậm là hướng T2 đã chọn.<br><br>Với thứ tự ô <b>cố định</b>, hướng tối ưu tìm được bằng <b>quy hoạch động — CHÍNH XÁC</b>. Chỉ THỨ TỰ là heuristic, nên xấp xỉ bị nhốt vào <b>một chỗ có tên</b>.`,
 speed:`Đổi biến sang <b>nghịch đảo tốc độ</b>: thời gian, liều, và hộp tốc độ đều thành <b>tuyến tính</b> ⇒ đây là một <b>quy hoạch tuyến tính, GIẢI CHÍNH XÁC</b>.<br><br>Màu vàng = chậm (giao nhiều liều), xanh đậm = nhanh. Máy bay <b>chậm lại đúng chỗ cần</b> rồi tăng tốc ở nơi không cần.<br><br><b>Khúc lượn bị GHIM</b> ở bán kính T2 đã lập, vì ρ = v²/(g·tanφ) phụ thuộc tốc độ — để LP đổi tốc độ trên khúc lượn là làm hỏng đường T2 vừa tìm. Không có ràng buộc này thì hai chặng <b>đúng riêng lẻ và sai khi ghép</b>.`,
 fly:`Máy bay bay tour đã lập và <b>phát quảng bá tập tham chiếu</b>. Nút nào nhận đủ thì chạy đối sánh với dữ liệu quan sát <b>của chính nó</b> rồi trả lời <b>XÁC NHẬN</b> hoặc <b>BÁC BỎ</b>.<br><br><b>Đến đây mới có tập vị trí nghi vấn</b> — và đó là đầu ra của Pha 1, đầu vào cho Pha 2.<br><br>Trước khi giao, nút bị chặn bởi <b>Fano: 1/(M+1)</b> — trần THÔNG TIN, quan sát lâu hơn không vượt được. Khoảng cách giữa hai giá trị đọc (trước/sau tham chiếu) chính là thứ máy bay bay ra để mua: <b>giao dữ liệu là hành vi GỠ NHẬP NHẰNG</b>, không phải hành vi vận chuyển.`,
 refine:`Đóng vòng phụ thuộc T0 phải cắt: chi phí phục vụ cần <b>khoảng lệch b</b>, mà b do tuyến quyết định, mà tuyến lại cần chi phí.<br><br>Thêm nữa, tuyến bay <b>rải tham chiếu miễn phí</b> lên mọi ô nằm gần nó — ô nào nhận đủ thì <b>không cần thăm</b>.<br><br><b>Vòng lặp KHÔNG co:</b> bỏ một ô làm tuyến ngắn lại, có thể khiến chính ô đó hết được phủ. Nên (1) chỉ kế hoạch <b>tự nhất quán</b> mới được nhận, và (2) <b>bước rút chia đôi</b> mỗi lần thất bại.`};
 document.getElementById('txt').innerHTML=T[key];
 let tb='';
 if(key==='part'||key==='order'||key==='speed'){
  tb='<table><tr><th>máy bay</th><th>NN (m)</th><th>tối ưu (m)</th><th>phục vụ (s)</th><th>thời gian (s)</th></tr>';
  R.cost.forEach(c=>tb+=`<tr><td><span class=sw style="background:${VEH[c.v%VEH.length]}"></span>${c.v+1}</td>`+
   `<td>${c.nn.toFixed(0)}</td><td>${c.opt.toFixed(0)}</td><td>${c.svc.toFixed(1)}</td>`+
   `<td>${c.ok?c.t.toFixed(0):'—'}</td></tr>`);
  tb+='</table>';
 }
 if(key==='fly'){
  const cf=R.cells.filter(c=>c.verdict==='confirm'), rj=R.cells.filter(c=>c.verdict==='reject');
  tb=`<table><tr><th>kết luận</th><th>số ô</th></tr>`+
   `<tr><td style="color:${css('--real')}">XÁC NHẬN</td><td>${cf.length}</td></tr>`+
   `<tr><td>bác bỏ</td><td>${rj.length}</td></tr></table>`+
   `<div class=body style="margin-top:8px">Trong ${cf.length} ô xác nhận, `+
   `<b>${cf.filter(c=>c.real).length}</b> ô thật sự chứa nạn nhân; `+
   `${R.cells.filter(c=>c.real).length} ô có nạn nhân trên toàn vùng.</div>`;
 }
 if(key==='refine'){
  tb='<table><tr><th>vòng</th><th>makespan</th><th>ô thăm</th><th>nghỉ hưu</th><th>hợp lệ</th></tr>';
  R.hist.forEach(h=>tb+=`<tr><td>${h.it}</td><td>${h.mk.toFixed(0)} s</td><td>${h.cells}</td>`+
   `<td>${h.ret}</td><td style="color:${h.ok?css('--real'):css('--dec')}">${h.ok?'✓':'✗ '+(h.unc?h.unc+' ô hở':'')}</td></tr>`);
  tb+='</table>';
  tb+=`<div class=body style="margin-top:8px">Kết quả nhận: <b>${R.cfg.feasible==='1'?(+R.cfg.makespan).toFixed(0)+' s ở vòng '+R.cfg.bestIter:'KHÔNG có kế hoạch hợp lệ'}</b> · ${R.cfg.consistent}/${R.hist.length} vòng hợp lệ</div>`;
 }
 document.getElementById('tb').innerHTML=tb;
 const L={fly:'<span><i class=sw style=background:var(--a)></i>ô XÁC NHẬN = vị trí nghi vấn (kết luận)</span><span><i class=sw style=background:var(--c)></i>bác bỏ</span>',
  cells:'<span><i class=sw style=background:#2f6fd0></i>visual</span><span><i class=sw style=background:#c2410c></i>thermal</span><span><i class=sw style=background:#7c3aed></i>acoustic</span><span>◯ cụm trưởng</span>',
  class:'<span><i class=sw style=background:var(--a)></i>A</span><span><i class=sw style=background:var(--b)></i>B</span><span><i class=sw style=background:var(--c)></i>C</span>',
  demand:'<span>đậm hơn = θ lớn hơn · ↻n = số vòng lượn</span>',
  speed:'<span><i class=sw style=background:rgb(250,220,60)></i>chậm (nhiều liều)</span><span><i class=sw style=background:rgb(40,50,110)></i>nhanh</span>'};
 document.getElementById('leg').innerHTML=(L[key]||'')+
  '<span><i class=sw style=background:var(--real)></i>nạn nhân</span><span><i class=sw style=background:var(--dec)></i>gây nhầm</span>';
 document.getElementById('sub').textContent=
  `${C.grid}×${C.grid} nút @${C.spacing} m · vùng ${C.side} m · R_c=${C.cellRadius} m · `+
  `${C.vehicles} máy bay · ρ=${(+C.turnRadius).toFixed(1)} m · θ×${C.thetaScale}`;
 document.querySelectorAll('.chip').forEach((c,i)=>{
  c.className='chip'+(i===S?' on':(i<S?' done':''));});
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
