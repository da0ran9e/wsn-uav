// WSN-UAV log visualizer — ES module
// Parses NS-3 markdown event logs and replays them as a top-down SVG view.

const SVG_NS = "http://www.w3.org/2000/svg";
const DEFAULT_LOG = "visualize/result/scenario1/13-05-26/13-55-31.md";

// ------------------------- Parser -------------------------

function unescapeCell(s) {
  return s.replace(/\\\|/g, "|").replace(/<br\s*\/?>/g, "\n").trim();
}

function parseLog(text) {
  const lines = text.split(/\r?\n/);
  const rows = [];
  let inTable = false;
  for (const ln of lines) {
    if (!ln.startsWith("|")) { inTable = false; continue; }
    // header / separator?
    if (/^\|\s*-{3,}/.test(ln) || /^\|\s*simtime\s*\|/i.test(ln)) { inTable = true; continue; }
    if (!inTable) continue;
    const parts = ln.split("|").slice(1, -1);
    if (parts.length < 3) continue;
    rows.push(parts.map(unescapeCell));
  }
  return rows.map(([t, m, c]) => ({ t, module: m, content: c }));
}

// Build world from setup rows + event list from runtime rows
function buildWorld(rows) {
  const world = {
    scenario: "scenario",
    bsId: null, uavId: null,
    sensorIdRange: null,
    bsPos: null, uavStart: null,
    sensors: new Map(),     // id -> {x,y,z}
    gridBounds: null,       // {w,h,spacing}
    waypoints: [],          // {t,x,y,z}
    events: [],             // {t, module, kind, payload, raw}
  };

  for (const row of rows) {
    const { t, module: mod, content } = row;
    let m;

    if (t === "-") {
      // Setup phase
      if ((m = content.match(/BaseStation ID=(\d+)/))) world.bsId = +m[1];
      else if ((m = content.match(/UAV ID=(\d+)/))) world.uavId = +m[1];
      else if ((m = content.match(/Sensors:\s*(\d+)×(\d+)\s*\(IDs=(\d+)-(\d+)\)/))) {
        world.sensorIdRange = { rows: +m[1], cols: +m[2], lo: +m[3], hi: +m[4] };
      } else if ((m = content.match(/BaseStation:\s*\(([-0-9.]+),\s*([-0-9.]+),\s*([-0-9.]+)\)/))) {
        world.bsPos = { x: +m[1], y: +m[2], z: +m[3] };
      } else if ((m = content.match(/UAV:\s*\(([-0-9.]+),\s*([-0-9.]+),\s*([-0-9.]+)\)/))) {
        world.uavStart = { x: +m[1], y: +m[2], z: +m[3] };
      } else if ((m = content.match(/Sensors:\s*grid\s*\[0,(\d+(?:\.\d+)?)\]\s*×\s*\[0,(\d+(?:\.\d+)?)\]\s*spacing=(\d+(?:\.\d+)?)m/))) {
        world.gridBounds = { w: +m[1], h: +m[2], spacing: +m[3] };
      }
      continue;
    }

    const time = parseFloat(t);
    if (!Number.isFinite(time)) continue;

    const ev = { t: time, module: mod, kind: "other", payload: {}, raw: content };

    if ((m = content.match(/TX beacon \(size=(\d+)B\)/))) {
      ev.kind = "tx"; ev.payload.size = +m[1];
    } else if ((m = content.match(/RX packet \(size=(\d+)B\)/))) {
      ev.kind = "rx"; ev.payload.size = +m[1];
    } else if ((m = content.match(/CMD waypoint t=([-0-9.eE]+)s\s*->\s*\(([-0-9.]+),\s*([-0-9.]+),\s*([-0-9.]+)\)/))) {
      ev.kind = "waypoint";
      const wp = { t: +m[1], x: +m[2], y: +m[3], z: +m[4] };
      ev.payload = wp;
      world.waypoints.push(wp);
    } else if ((m = content.match(/pos sample, v=([-0-9.]+) m\/s/))) {
      ev.kind = "vsample"; ev.payload.v = +m[1];
    } else if ((m = content.match(/send topology to UAV\[(\d+)\] \(nodes=(\d+) size=(\d+)B sent=(OK|FAIL)\)/))) {
      ev.kind = "bs_to_uav";
      ev.payload = { uavId: +m[1], nodes: +m[2], size: +m[3], ok: m[4] === "OK" };
    } else if (/received topology/.test(content)) {
      ev.kind = "uav_recv";
    } else if ((m = content.match(/drop packet/))) {
      ev.kind = "drop";
    }
    world.events.push(ev);
  }

  // Sort events by time (stable enough — rows already mostly ordered)
  world.events.sort((a, b) => a.t - b.t);

  // Allocate sensor positions from grid if available
  if (world.sensorIdRange && world.gridBounds) {
    const { lo, hi, rows: rN, cols: cN } = world.sensorIdRange;
    const { w, h } = world.gridBounds;
    const stepX = cN > 1 ? w / (cN - 1) : 0;
    const stepY = rN > 1 ? h / (rN - 1) : 0;
    let id = lo;
    for (let r = 0; r < rN && id <= hi; r++) {
      for (let c = 0; c < cN && id <= hi; c++) {
        world.sensors.set(id, { x: c * stepX, y: r * stepY, z: 0 });
        id++;
      }
    }
  }

  return world;
}

// Interpolate UAV position from waypoints at simtime T
function uavPositionAt(world, T) {
  const wps = world.waypoints;
  if (wps.length === 0) return world.uavStart || { x: 0, y: 0, z: 0 };
  if (T <= wps[0].t) return wps[0];
  if (T >= wps[wps.length - 1].t) return wps[wps.length - 1];
  let lo = 0, hi = wps.length - 1;
  while (hi - lo > 1) {
    const mid = (lo + hi) >> 1;
    if (wps[mid].t <= T) lo = mid; else hi = mid;
  }
  const a = wps[lo], b = wps[hi];
  const f = (T - a.t) / (b.t - a.t || 1);
  return { x: a.x + (b.x - a.x) * f, y: a.y + (b.y - a.y) * f, z: a.z + (b.z - a.z) * f };
}

// ------------------------- Renderer -------------------------

class Renderer {
  constructor(svg, world) {
    this.svg = svg;
    this.world = world;
    this.size = { w: 800, h: 600 };
    this.computeBounds();
    this.fitViewBox();
    this.renderStatic();
  }

  computeBounds() {
    const xs = [], ys = [];
    if (this.world.bsPos)    { xs.push(this.world.bsPos.x); ys.push(this.world.bsPos.y); }
    if (this.world.uavStart) { xs.push(this.world.uavStart.x); ys.push(this.world.uavStart.y); }
    for (const s of this.world.sensors.values()) { xs.push(s.x); ys.push(s.y); }
    for (const w of this.world.waypoints)       { xs.push(w.x); ys.push(w.y); }
    if (xs.length === 0) { xs.push(0, 100); ys.push(0, 100); }
    const minX = Math.min(...xs), maxX = Math.max(...xs);
    const minY = Math.min(...ys), maxY = Math.max(...ys);
    const padX = Math.max(10, (maxX - minX) * 0.1);
    const padY = Math.max(10, (maxY - minY) * 0.1);
    this.bounds = { minX: minX - padX, maxX: maxX + padX, minY: minY - padY, maxY: maxY + padY };
  }

  fitViewBox() {
    const { minX, maxX, minY, maxY } = this.bounds;
    // flip Y so larger Y is up
    this.svg.setAttribute("viewBox", `${minX} ${-maxY} ${maxX - minX} ${maxY - minY}`);
  }

  // World point -> SVG point (we just negate Y to flip)
  pt(x, y) { return [x, -y]; }

  el(tag, attrs = {}, parent = null) {
    const e = document.createElementNS(SVG_NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }

  clear(id) {
    const g = this.svg.querySelector(id);
    while (g.firstChild) g.removeChild(g.firstChild);
    return g;
  }

  renderStatic() {
    // Grid
    const gGrid = this.clear("#g-grid");
    const { minX, maxX, minY, maxY } = this.bounds;
    const span = Math.max(maxX - minX, maxY - minY);
    let step = 10;
    if (span > 400) step = 50;
    else if (span > 150) step = 20;
    const x0 = Math.ceil(minX / step) * step;
    const y0 = Math.ceil(minY / step) * step;
    for (let x = x0; x <= maxX; x += step) {
      this.el("line", { class: "grid-line", x1: x, y1: -minY, x2: x, y2: -maxY }, gGrid);
    }
    for (let y = y0; y <= maxY; y += step) {
      this.el("line", { class: "grid-line", x1: minX, y1: -y, x2: maxX, y2: -y }, gGrid);
    }
    // Axes through 0,0
    this.el("line", { class: "axis", x1: minX, y1: 0, x2: maxX, y2: 0 }, gGrid);
    this.el("line", { class: "axis", x1: 0, y1: -minY, x2: 0, y2: -maxY }, gGrid);

    // Sensors
    const gS = this.clear("#g-sensors");
    this.sensorNodes = new Map();
    const r = Math.max(2, span / 120);
    for (const [id, s] of this.world.sensors) {
      const [px, py] = this.pt(s.x, s.y);
      const g = this.el("g", { transform: `translate(${px} ${py})` }, gS);
      const c = this.el("circle", { class: "sensor", r }, g);
      this.el("text", { class: "sensor-label", y: -r - 2 }, g).textContent = id;
      this.sensorNodes.set(id, c);
    }

    // BS
    const gBS = this.clear("#g-bs");
    if (this.world.bsPos) {
      const [px, py] = this.pt(this.world.bsPos.x, this.world.bsPos.y);
      const side = Math.max(8, span / 60);
      const g = this.el("g", { transform: `translate(${px} ${py})` }, gBS);
      this.bsNode = this.el("rect", { class: "bs", x: -side/2, y: -side/2, width: side, height: side, rx: 2 }, g);
      this.el("text", { class: "bs-label", y: -side/2 - 4 }, g).textContent = `BS#${this.world.bsId ?? 0}`;
    }

    // UAV future-path (dashed) — initial render of waypoints
    const gT = this.clear("#g-trails");
    if (this.world.waypoints.length > 0) {
      const d = this.world.waypoints.map(w => {
        const [x, y] = this.pt(w.x, w.y);
        return `${x},${y}`;
      }).join(" ");
      this.el("polyline", { class: "uav-trail-future", points: d, id: "uav-future" }, gT);
      this.el("polyline", { class: "uav-trail-past", points: "", id: "uav-past" }, gT);
    }

    // UAV sprite
    const gU = this.clear("#g-uav");
    const uavSize = Math.max(8, span / 55);
    this.uavSize = uavSize;
    this.uavGroup = this.el("g", {}, gU);
    this.uavTri = this.el("polygon", { class: "uav",
      points: `0,${-uavSize} ${uavSize*0.7},${uavSize*0.7} ${-uavSize*0.7},${uavSize*0.7}` }, this.uavGroup);
    this.uavLabel = this.el("text", { class: "uav-label", y: -uavSize - 4 }, this.uavGroup);
    this.uavLabel.textContent = `UAV#${this.world.uavId ?? 1}`;
    this.prevUavPos = null;
  }

  setUavPosition(pos, T) {
    if (!this.uavGroup) return;
    const [px, py] = this.pt(pos.x, pos.y);
    let angle = 0;
    if (this.prevUavPos) {
      const dx = pos.x - this.prevUavPos.x;
      const dy = pos.y - this.prevUavPos.y;
      if (Math.hypot(dx, dy) > 1e-3) {
        // angle: 0 means triangle points "up" (toward +Y world). atan2(dx, dy) -> rotation about origin
        angle = Math.atan2(dx, dy) * 180 / Math.PI;
      }
    }
    this.uavGroup.setAttribute("transform", `translate(${px} ${py}) rotate(${angle})`);
    this.prevUavPos = { ...pos };

    // Update past trail up to time T
    const past = this.svg.querySelector("#uav-past");
    if (past) {
      const wps = this.world.waypoints;
      const pts = [];
      for (const w of wps) {
        if (w.t <= T) {
          const [x, y] = this.pt(w.x, w.y);
          pts.push(`${x},${y}`);
        } else break;
      }
      const [cx, cy] = this.pt(pos.x, pos.y);
      pts.push(`${cx},${cy}`);
      past.setAttribute("points", pts.join(" "));
    }
  }

  flashSensor(id) {
    const c = this.sensorNodes.get(id);
    if (!c) return;
    c.classList.add("flash");
    setTimeout(() => c.classList.remove("flash"), 220);
  }
  flashBS() {
    if (!this.bsNode) return;
    this.bsNode.classList.add("flash");
    setTimeout(() => this.bsNode.classList.remove("flash"), 220);
  }
  flashUav() {
    if (!this.uavTri) return;
    this.uavTri.style.fill = "var(--brand-orange)";
    setTimeout(() => { this.uavTri.style.fill = ""; }, 220);
  }
  txRing(worldX, worldY) {
    const [px, py] = this.pt(worldX, worldY);
    const g = this.svg.querySelector("#g-rings");
    const c = this.el("circle", { class: "tx-ring", cx: px, cy: py, r: 1 }, g);
    const span = this.bounds.maxX - this.bounds.minX;
    const target = Math.max(20, span / 12);
    const start = performance.now();
    const dur = 600;
    const animate = (now) => {
      const t = (now - start) / dur;
      if (t >= 1) { c.remove(); return; }
      c.setAttribute("r", 1 + (target - 1) * t);
      c.setAttribute("opacity", String(1 - t));
      requestAnimationFrame(animate);
    };
    requestAnimationFrame(animate);
  }
  arrowBsToUav(uavPos, label) {
    if (!this.world.bsPos) return;
    const [x1, y1] = this.pt(this.world.bsPos.x, this.world.bsPos.y);
    const [x2, y2] = this.pt(uavPos.x, uavPos.y);
    const g = this.svg.querySelector("#g-arrows");
    const line = this.el("line", { class: "arrow-bs-uav", x1, y1, x2, y2 }, g);
    const txt = this.el("text", { class: "arrow-label",
      x: (x1 + x2) / 2, y: (y1 + y2) / 2 - 4 }, g);
    txt.textContent = label;
    const start = performance.now();
    const dur = 700;
    const animate = (now) => {
      const t = (now - start) / dur;
      if (t >= 1) { line.remove(); txt.remove(); return; }
      line.setAttribute("opacity", String(0.85 * (1 - t)));
      txt.setAttribute("opacity", String(1 - t));
      requestAnimationFrame(animate);
    };
    requestAnimationFrame(animate);
  }
}

// ------------------------- Player -------------------------

class Player {
  constructor(world, renderer, ui) {
    this.world = world;
    this.renderer = renderer;
    this.ui = ui;
    this.simNow = 0;
    this.simEnd = world.events.length ? world.events[world.events.length - 1].t : 0;
    this.idx = 0;
    this.speed = 1;
    this.playing = false;
    this.lastFrame = 0;
    this.stats = { tx: 0, rx: 0, drops: 0, pathLen: 0 };
    this.feedItems = []; // last 50 dispatched events for the feed
    this.activeFilter = "all";
    this.prevUavPos = renderer.uavGroup ? uavPositionAt(world, 0) : null;
  }

  setSpeed(s) { this.speed = s; this.ui.updateSpeed(s); }

  play() { if (!this.playing && this.simEnd > 0) { this.playing = true; this.lastFrame = performance.now(); this.ui.updateButtons(true); requestAnimationFrame(this.tick); } }
  pause() { this.playing = false; this.ui.updateButtons(false); }

  reset() {
    this.pause();
    this.simNow = 0;
    this.idx = 0;
    this.stats = { tx: 0, rx: 0, drops: 0, pathLen: 0 };
    this.feedItems = [];
    this.prevUavPos = uavPositionAt(this.world, 0);
    this.renderer.prevUavPos = null;
    this.refresh();
  }

  seek(T) {
    // Simpler: if seeking backwards, reset and replay forward; this keeps state consistent.
    if (T < this.simNow) {
      this.pause();
      this.simNow = 0; this.idx = 0;
      this.stats = { tx: 0, rx: 0, drops: 0, pathLen: 0 };
      this.feedItems = [];
      this.renderer.prevUavPos = null;
      this.prevUavPos = uavPositionAt(this.world, 0);
    }
    this.advanceTo(T, /*silent=*/true);
    this.refresh();
  }

  advanceTo(T, silent = false) {
    while (this.idx < this.world.events.length && this.world.events[this.idx].t <= T) {
      this.dispatch(this.world.events[this.idx], silent);
      this.idx++;
    }
    // UAV pos & path length
    const uavPos = uavPositionAt(this.world, T);
    if (this.prevUavPos) {
      const dx = uavPos.x - this.prevUavPos.x;
      const dy = uavPos.y - this.prevUavPos.y;
      const dz = uavPos.z - this.prevUavPos.z;
      this.stats.pathLen += Math.hypot(dx, dy, dz);
    }
    this.prevUavPos = uavPos;
    this.renderer.setUavPosition(uavPos, T);
    this.simNow = T;
  }

  step() {
    if (this.idx >= this.world.events.length) return;
    const next = this.world.events[this.idx];
    this.advanceTo(next.t);
    this.refresh();
  }

  tick = (now) => {
    if (!this.playing) return;
    const dt = (now - this.lastFrame) / 1000;
    this.lastFrame = now;
    let T = this.simNow + dt * this.speed;
    if (T >= this.simEnd) { T = this.simEnd; this.playing = false; this.ui.updateButtons(false); }
    this.advanceTo(T);
    this.refresh();
    if (this.playing) requestAnimationFrame(this.tick);
  };

  dispatch(ev, silent) {
    // Stats
    if (ev.kind === "tx") this.stats.tx++;
    else if (ev.kind === "rx") this.stats.rx++;
    else if (ev.kind === "drop") this.stats.drops++;

    // Maintain feed (last 50)
    this.feedItems.push(ev);
    if (this.feedItems.length > 200) this.feedItems.shift();

    if (silent) return;

    // Visuals
    const senderPos = this.modulePos(ev.module);
    if (ev.kind === "tx") {
      const sid = this.sensorIdOf(ev.module);
      if (sid != null) {
        this.renderer.flashSensor(sid);
        const s = this.world.sensors.get(sid);
        if (s) this.renderer.txRing(s.x, s.y);
      } else if (ev.module === "BS" && this.world.bsPos) {
        this.renderer.flashBS();
        this.renderer.txRing(this.world.bsPos.x, this.world.bsPos.y);
      }
    } else if (ev.kind === "rx") {
      const sid = this.sensorIdOf(ev.module);
      if (sid != null) this.renderer.flashSensor(sid);
      else if (ev.module === "BS") this.renderer.flashBS();
      else if (ev.module === "UAV") this.renderer.flashUav();
    } else if (ev.kind === "bs_to_uav") {
      const uavPos = uavPositionAt(this.world, ev.t);
      this.renderer.flashBS();
      this.renderer.arrowBsToUav(uavPos, `${ev.payload.size}B`);
    } else if (ev.kind === "uav_recv") {
      this.renderer.flashUav();
    }
  }

  sensorIdOf(mod) {
    const m = mod.match(/^ground-node\[(\d+)\]$/) || mod.match(/^Node\[(\d+)\]\./);
    return m ? +m[1] : null;
  }
  modulePos(mod) {
    const sid = this.sensorIdOf(mod);
    if (sid != null) return this.world.sensors.get(sid);
    if (mod === "BS") return this.world.bsPos;
    if (mod === "UAV") return uavPositionAt(this.world, this.simNow);
    return null;
  }

  refresh() { this.ui.refresh(this); }
}

// ------------------------- UI wiring -------------------------

const FILTERS = ["all", "TX", "RX", "UAV", "BS", "drop"];

class UI {
  constructor() {
    this.fileInput   = document.getElementById("file-input");
    this.btnLoad     = document.getElementById("btn-load");
    this.btnPlay     = document.getElementById("btn-play");
    this.btnPause    = document.getElementById("btn-pause");
    this.btnStep     = document.getElementById("btn-step");
    this.metaScenario= document.getElementById("meta-scenario");
    this.metaPath    = document.getElementById("meta-path");
    this.scrubber    = document.getElementById("scrubber");
    this.timeReadout = document.getElementById("time-readout");
    this.speedRow    = document.getElementById("speed-row");
    this.eventList   = document.getElementById("event-list");
    this.filtersBar  = document.getElementById("event-filters");
    this.statTx      = document.getElementById("stat-tx");
    this.statRx      = document.getElementById("stat-rx");
    this.statDrops   = document.getElementById("stat-drops");
    this.statPath    = document.getElementById("stat-path");
    this.statElapsed = document.getElementById("stat-elapsed");
    this.emptyState  = document.getElementById("empty-state");
    this.world       = document.getElementById("world");
    this.player      = null;
    this.filter      = "all";

    this.renderFilters();
    this.bindControls();
  }

  renderFilters() {
    this.filtersBar.innerHTML = "";
    for (const f of FILTERS) {
      const b = document.createElement("button");
      b.className = "filter-chip" + (f === this.filter ? " active" : "");
      b.textContent = f;
      b.onclick = () => {
        this.filter = f;
        [...this.filtersBar.children].forEach(c => c.classList.toggle("active", c.textContent === f));
        if (this.player) this.refresh(this.player);
      };
      this.filtersBar.appendChild(b);
    }
  }

  bindControls() {
    this.btnLoad.onclick = () => this.fileInput.click();
    this.fileInput.onchange = async () => {
      const f = this.fileInput.files[0];
      if (!f) return;
      const text = await f.text();
      this.loadText(text, f.name);
    };
    this.btnPlay.onclick  = () => this.player && this.player.play();
    this.btnPause.onclick = () => this.player && this.player.pause();
    this.btnStep.onclick  = () => this.player && this.player.step();

    this.scrubber.oninput = () => {
      if (!this.player) return;
      const T = (+this.scrubber.value / 100) * this.player.simEnd;
      this.player.seek(T);
    };

    this.speedRow.querySelectorAll(".speed-btn").forEach(b => {
      b.onclick = () => {
        const s = parseFloat(b.dataset.speed);
        if (this.player) this.player.setSpeed(s);
        else this.updateSpeed(s);
      };
    });

    // Drag & drop
    document.addEventListener("dragover", e => e.preventDefault());
    document.addEventListener("drop", async e => {
      e.preventDefault();
      const f = e.dataTransfer.files[0];
      if (f) this.loadText(await f.text(), f.name);
    });
  }

  loadText(text, fileName) {
    const rows = parseLog(text);
    const world = buildWorld(rows);
    // Scenario name from first H1 or fallback
    const h1 = text.split(/\r?\n/).find(l => l.startsWith("# "));
    const scenarioName = h1 ? h1.replace(/^#\s*/, "").trim() : fileName;
    world.scenario = scenarioName;

    this.metaScenario.textContent = scenarioName;
    this.metaPath.textContent = fileName;
    this.emptyState.classList.add("hidden");

    const renderer = new Renderer(this.world, world);
    this.player = new Player(world, renderer, this);
    this.btnPlay.disabled = false;
    this.btnPause.disabled = false;
    this.scrubber.value = 0;
    this.refresh(this.player);
  }

  updateButtons(playing) {
    this.btnPlay.textContent  = playing ? "Playing" : "Replay";
    this.btnPlay.disabled  = playing;
    this.btnPause.disabled = !playing;
  }
  updateSpeed(s) {
    this.speedRow.querySelectorAll(".speed-btn").forEach(b => {
      b.classList.toggle("active", parseFloat(b.dataset.speed) === s);
    });
  }

  refresh(player) {
    // Scrubber + readout
    const pct = player.simEnd > 0 ? (player.simNow / player.simEnd) * 100 : 0;
    this.scrubber.value = pct;
    this.timeReadout.textContent = `${player.simNow.toFixed(3)} / ${player.simEnd.toFixed(3)}s`;

    // Stats
    this.statTx.textContent      = player.stats.tx;
    this.statRx.textContent      = player.stats.rx;
    this.statDrops.textContent   = player.stats.drops;
    this.statPath.textContent    = `${player.stats.pathLen.toFixed(1)} m`;
    this.statElapsed.textContent = `${player.simNow.toFixed(3)} s`;

    // Event feed — last 50, filtered
    const filtered = [];
    for (let i = player.feedItems.length - 1; i >= 0 && filtered.length < 50; i--) {
      const ev = player.feedItems[i];
      if (!this.matchesFilter(ev)) continue;
      filtered.push(ev);
    }
    // Rebuild list (small N, cheap)
    this.eventList.innerHTML = "";
    for (const ev of filtered) {
      const row = document.createElement("div");
      row.className = "event-row";
      row.innerHTML = `<span class="t">${ev.t.toFixed(3)}</span><span class="m">${ev.module}</span><span class="c">${escapeHtml(ev.raw)}</span>`;
      row.onclick = () => { player.seek(ev.t); };
      this.eventList.appendChild(row);
    }
  }

  matchesFilter(ev) {
    if (this.filter === "all") return true;
    if (this.filter === "TX") return ev.kind === "tx" || ev.kind === "bs_to_uav";
    if (this.filter === "RX") return ev.kind === "rx" || ev.kind === "uav_recv";
    if (this.filter === "UAV") return ev.module === "UAV";
    if (this.filter === "BS")  return ev.module === "BS";
    if (this.filter === "drop") return ev.kind === "drop";
    return true;
  }
}

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]));
}

// Boot
const ui = new UI();
(async () => {
  try {
    const r = await fetch(DEFAULT_LOG);
    if (r.ok) {
      const text = await r.text();
      ui.loadText(text, DEFAULT_LOG);
    }
  } catch (e) {
    // file:// usage — silently skip, user can still pick a file
  }
})();
