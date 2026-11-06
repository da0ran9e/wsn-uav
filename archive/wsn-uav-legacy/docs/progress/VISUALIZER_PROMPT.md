# Prompt: Build HTML Visualizer for WSN-UAV Simulation Logs

## Mission

Build a single-page HTML visualizer that replays an NS-3 WSN-UAV simulation from its log file. The entry point is `src/wsn-uav/docs/index.html`. Supporting assets already scaffolded: `src/wsn-uav/docs/visualize/app.js`, `src/wsn-uav/docs/visualize/styles.css`. Follow the visual language documented in `src/wsn-uav/docs/visualize/DESIGN.md` (Notion-style: deep navy hero, purple primary CTA, 8px buttons, 12px cards, pastel feature tints, Inter/Notion-Sans typography).

The visualizer is for **research / debugging the simulation**, not a marketing page — apply the DESIGN.md tokens to a functional dashboard, don't build a marketing site.

## Input: Log File Format

Logs live under `src/wsn-uav/docs/visualize/result/<scenarioName>/<dd-MM-yy>/<hh-mm-ss>.md`. Each file is a markdown document with a 3-column table:

```markdown
# scenario1 event log

Log file: `src/wsn-uav/docs/visualize/result/scenario1/13-05-26/13-55-31.md`

| simtime | module | content |
|---------|--------|---------|
| - | Scenario1Network | Node Creation: |
| - | Scenario1Network |   BaseStation ID=0 |
| - | Scenario1Network |   UAV ID=1 |
| - | Scenario1Network |   Sensors: 3×3 (IDs=2-10) |
| - | Scenario1Network | Mobility Setup: |
| - | Scenario1Network |   BaseStation: (-200, -200, 0) |
| - | Scenario1Network |   UAV: (-200, -200, 20) |
| 0.000055 | ground-node[3] | TX beacon (size=15B) [OK] |
| 0.002144 | ground-node[2] | RX packet (size=4B) |
| 0.101103 | BS | send topology to UAV[1] (nodes=11 size=79B sent=OK) |
| 0.105775 | UAV | received topology (nodes=11) |
| 0.105775 | UAV |   node[0] pos=(-200,-200,0) |
| 0.105775 | UAV |   node[2] pos=(0,0,0) |
| 1.009532 | UAV | started |
| 1.009532 | UAV | CMD waypoint t=1.00953s -> (-200, -200, 20) |
| 1.009532 | UAV | CMD waypoint t=15.1517s -> (0, 0, 20) |
| 1.009532 | UAV | CMD waypoint t=17.1517s -> (40, 0, 20) |
| 3.009532 | UAV | pos sample, v=20 m/s |
```

### Column semantics

- **simtime**: float seconds, or `-` for setup-time logs (no simulation time yet). Setup rows must be processed before time-zero events.
- **module**: who emitted the log. Forms encountered today:
  - `Scenario1Config`, `Scenario1Network` — orchestrator setup logs (no node).
  - `BS` — base station application.
  - `UAV` — UAV application.
  - `ground-node[<id>]` — sensor application. `<id>` is the ns-3 node ID (uint32).
  - Generic future form: `Node[<id>].<Layer>` where Layer ∈ {Application, Phy, Mac, Mobility}.
- **content**: free-form text. `\n` was escaped to `<br>` and `|` to `\|` by the logger. Content begins with action verbs (`TX`, `RX`, `started`, `CMD waypoint`, `pos sample`, `send topology`, `received topology`, `drop packet`).

### Lines you must parse

| Pattern (regex-ish) | Meaning | Use |
|---|---|---|
| `BaseStation ID=<n>` | BS node id | identify BS sprite |
| `UAV ID=<n>` | UAV node id | identify UAV sprite |
| `Sensors: <R>×<C> (IDs=<lo>-<hi>)` | Sensor count + id range | allocate sensors |
| `BaseStation: (x, y, z)` | BS position | static placement |
| `Sensors: grid [0,<W>] × [0,<H>] spacing=<s>m` | Grid bounds | viewport bounds |
| `UAV: (x, y, z)` | UAV start position | initial sprite |
| `TX beacon (size=<n>B)` | sensor radio TX | flash sprite + optional radius ping |
| `RX packet (size=<n>B)` | RX event | flash sprite |
| `CMD waypoint t=<t>s -> (x, y, z)` | UAV actuator command | build flight path polyline |
| `pos sample, v=<v> m/s` | UAV velocity sample | velocity HUD (interpolate position from waypoints) |
| `send topology to UAV[<id>] (nodes=<n> size=<b>B sent=<OK\|FAIL>)` | BS→UAV unicast | flash both, draw arrow BS→UAV |
| `received topology (nodes=<n>)` | UAV decoded topology | flash UAV |
| `  node[<id>] pos=(x,y,z)` | UAV's view of node | optional confirmation, skip in viz |
| `drop packet (destId=<n> not me)` | drop event | optional dim flash |

UAV position is **derived by linear interpolation between waypoints by simtime** — the log only emits commands and periodic velocity samples, not absolute position per tick. Build `[(t, x, y, z), ...]` from `CMD waypoint` rows, then at playback time `T` find the bracketing pair and lerp.

## Layout Requirements

Single page, three regions:

1. **Header strip** (top, ~64px): scenario name, log file path, "Load log" file picker (accept `.md`), "Replay" / "Pause" / "Step" buttons. Use `button-primary` (purple) for Play, `button-secondary` for others, per DESIGN.md.

2. **Main canvas** (left, flex 1): 2D top-down view of the simulation world. Use SVG (preferred over canvas for selectability) with a coordinate system that maps simulation meters → pixels. Auto-fit the bounding box of all node positions + UAV waypoints + 10% padding. Render:
   - Grid background (light hairline).
   - Sensors as small circles labelled with id.
   - BS as a square (distinguish color).
   - UAV as a triangle / drone glyph at its interpolated position; orientation along velocity vector.
   - Past UAV trajectory as a faded polyline; future waypoints as a dashed line.
   - TX events: 1-frame ring expanding from sender.
   - RX events: brief 200ms flash on receiver fill color.
   - BS→UAV directed messages: animated arrow with packet-size label.

3. **Side panel** (right, ~360px): three stacked cards, all `card-feature` style:
   - **Timeline**: scrubber (range input) over simtime min..max, current time readout, play speed (0.25× / 1× / 4× / 16×).
   - **Event feed**: virtualized list of the last 50 events (filterable by module). Click an event → scrubber jumps to that simtime.
   - **Stats**: total TX, total RX, drops, UAV path length (m), elapsed simtime.

## Architecture Notes for the Agent

- Pure static site — **no build step, no npm**. Load `app.js` as `type="module"`. Use vanilla JS + SVG.
- The `result/` folder is **not** auto-listed by the browser; provide a file picker (`<input type="file">`) so the user drops a `.md` file. Optionally hardcode a default sample log path that loads via `fetch()` for local dev (path relative to `index.html`: `visualize/result/scenario1/13-05-26/13-55-31.md`).
- Parsing: split into lines, skip until the table header, then iterate rows. Strip `|`, trim cells, unescape `\|` → `|` and `<br>` → `\n`.
- Two phases: **setup phase** (rows with simtime=`-`) build the world (nodes, grid bounds, initial positions); **runtime phase** (numeric simtime) becomes the event stream sorted by simtime.
- Playback loop uses `requestAnimationFrame`. Advance a virtual `simNow` by `dt * speed`. Pop events whose simtime ≤ `simNow` and dispatch.
- Interpolate UAV position by binary-searching waypoints.

## Important Constraints

- **Do NOT modify** code outside `src/wsn-uav/docs/`. The simulation source is frozen for this task.
- **Do NOT add a build pipeline / bundler**. Plain `index.html` + ES module `app.js` + `styles.css`.
- Follow DESIGN.md tokens (colors, radii, typography) — define them as CSS custom properties at the top of `styles.css`. The page should feel like Notion's dashboards: white canvas, dark text, purple primary accent, generous whitespace.
- Sensors will scale: log files can contain up to ~1225 nodes (35×35 grid). SVG should remain responsive at that size — group sensors in one `<g>` and use `transform` updates rather than re-rendering.
- Events can number in the tens of thousands. Keep the parsed event array as plain JS objects `{t, module, kind, payload}`; don't store the raw markdown rows past parsing.

## Background Context (read once)

- Scenario 1: 1 base station (ID=0) + N×N sensor grid (IDs 2..N²+1) + 1 UAV (ID=1). BS at `(-200,-200,0)`. UAV starts at `(-200,-200,20)` and flies a boustrophedon over the sensor grid at altitude 20m, speed 20 m/s.
- BS sends a compact 79-byte topology packet to UAV at t≈0.1s. Sensors emit a single beacon at startup (staggered by random delay ≤ 10ms).
- Channel: IEEE 802.15.4, LogDistance loss (n=3, refLoss=46.6 dB @ 1m), TX=0 dBm, RX sensitivity=-95 dBm. Effective sensor↔sensor range ≈ 40m at the current grid; BS/UAV cannot RX sensor beacons from 290m away (correct behavior).

## Deliverables Checklist

- [ ] `src/wsn-uav/docs/index.html` — entry point with header / canvas / side panel skeleton.
- [ ] `src/wsn-uav/docs/visualize/app.js` — parser + playback engine + SVG renderer (ES module).
- [ ] `src/wsn-uav/docs/visualize/styles.css` — DESIGN.md tokens + layout.
- [ ] Loads the sample log `visualize/result/scenario1/13-05-26/13-55-31.md` on first run (if reachable via `fetch`).
- [ ] Playback runs at 1× without dropping events on a 10×10 grid log.
- [ ] No console errors. No external CDN dependencies (offline-capable).
