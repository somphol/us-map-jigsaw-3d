# AGENTS.md — UNITED STATES ATLAS

> Handoff for the next maintainer or agent. Rebuild detail is in
> [docs/REPRODUCTION.md](docs/REPRODUCTION.md); the technical map is
> [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## 1. What this is

A static, single-document **3D United States map and capitals jigsaw**. `index.html`
contains the markup, CSS, inlined state geometry and one ES module; **Three.js r160**
and `OrbitControls` are imported from jsDelivr. Fifty extruded state blocks start in a
left-hand tray, fifty brass capital pins in a bottom tray. The player drags each state
onto its silhouette, rotates misaligned blocks in 45° steps, then seats each capital pin
on the correct state. Correct pairings raise a fact card; clicking any placed state opens
a dossier with area, population, density and clickable neighbours. A timer, live counters,
synthesised audio and a victory orbit complete the loop.

It is **not** a survey-grade or official map — boundaries are simplified census-derived
polygons and populations are 2023 estimates — not a multiplayer or server-backed game,
and **not offline-capable**: the first load needs the Three.js CDN. **There is no
persistence**: progress, timer and settings live in memory and reloading or scrambling
resets the table.

Live copy: <https://somphol.github.io/us-map-jigsaw-3d/>. Local master:
`~/Projects/us-map-jigsaw-3d`. No version string is declared in the code and there is no
git tag; `CHANGELOG.md` is the release record. Latest source commit at the time of writing:
`567e354`.

## 2. Commands

```bash
cd ~/Projects/us-map-jigsaw-3d

# run — ES modules need HTTP
python3 -m http.server 8000
open http://localhost:8000/

# headless render (macOS WebGL via Metal)
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --use-angle=metal --mute-audio \
  --virtual-time-budget=12000 --timeout=30000 --window-size=1600,1000 \
  --screenshot=/tmp/us-atlas.png "http://localhost:8000/"

# smoke check: init finished, welcome gate open, 50 pieces and pins
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --use-angle=metal --mute-audio \
  --virtual-time-budget=12000 --timeout=30000 \
  --dump-dom "http://localhost:8000/?test=1" | grep -o 'id="loader" class="hide"'

# full solve in a real browser: open ?test=1, then in the console
#   __ATLAS__.solve()       // places and crowns all 50 in ~9 s

# regenerate geometry, then inline it
python3 tools/generate_map_data.py   # needs network: fetches census GeoJSON
python3 tools/build.py               # rewrites between MAP_DATA markers

# live probe
curl -s -o /dev/null -w '%{http_code}\n' https://somphol.github.io/us-map-jigsaw-3d/

# deploy — Pages serves the repository root of main; no workflow
git push origin main
```

`?test=1` is required for the `place` / `crown` / `solve` mutators; the read-only
`window.__ATLAS__` projection object exists on every load. Headless `--dump-dom` proves
the scene booted but cannot drag pieces; the full solve was driven through the Chrome
DevTools Protocol. Evidence is in [docs/TESTING.md](docs/TESTING.md).

## 3. Architecture

| File | Lines | Role |
| --- | ---: | --- |
| `index.html` | 3,583 | head/meta/CSS (1–681), OG/Twitter/canonical (682–699), HUD and overlays (700–898), inlined map data (900–905), import map (907–914), CDN timeout (916–924), game module (926–3581) |
| `assets/mapdata.js` | 2 | generated `window.US_MAP_DATA`: 50 states, 55 polygons, 739 points, three insets |
| `tools/generate_map_data.py` | 422 | fetches public-domain GeoJSON, Albers projection, simplification, capitals, neighbours, insets |
| `tools/build.py` | 24 | inlines `assets/mapdata.js` between `/* MAP_DATA_START */` and `/* MAP_DATA_END */` |
| `docs/social-card.png` | — | 1200 × 630 preview image |

The module is organised into banner sections:

| Section | Lines | Subject |
| --- | --- | --- |
| Data & constants | 930–977 | `DATA`, `STATES`, anchors, map/tray/snap constants, easing |
| Audio engine | 978–1120 | `SoundEngine` and the shared `sound` instance |
| Renderer/scene/camera | 1121–1153 | renderer, scene, camera, `OrbitControls`, pick state |
| Small visual helpers | 1154–1408 | rounded shapes, canvas textures, sprites, wood/felt/plate textures |
| Tween helpers | 1409–1446 | tag-based tween manager |
| Scene construction | 1447–2041 | `init`, lights, table, compass, map base, inset board, docks |
| State pieces | 2042–2169 | 50 extruded state blocks and slot visuals |
| Capital pins | 2170–2236 | 50 brass pins |
| Atmosphere | 2237–2262 | dust motes |
| Interaction | 2263–2935 | pointer, drag, rotation, snapping, rejection, hover, rotate dock |
| State dossier | 2936–2980 | click inspector and neighbour chips |
| HUD, timer, facts | 2981–3096 | counters, timer, fact queue, toasts, hints |
| Welcome / help | 3097–3140 | rules modal and `beginGame` |
| Reset / scramble | 3141–3230 | full board reset |
| Victory | 3231–3331 | 50/50 check, orbit, particles, results card |
| Camera flights | 3332–3354 | view buttons |
| Effects | 3355–3379 | snap burst rings |
| Ambient animation | 3380–3497 | loop, boat/dust/water motion, timer/HUD ticks |
| Debug / automation | 3498–3565 | `window.__ATLAS__`, `?test` mutators |
| Boot | 3566–3581 | `init()` inside try/catch with a visible failure card |

Key paths:

- **Boot** — `init()` (`index.html:1451`) creates the renderer (DPR capped at 2,
  ACES tone mapping, sRGB, PCF soft shadows), scene, camera, OrbitControls (12–230 m),
  then builds lights, table, map plate, inset board, docks, pieces, pins, dust and events.
  It sets `window.__USMAP_LOADED` and opens the welcome gate.
- **State** — one `game` object (`index.html:1141`): `started`, `finished`, `running`,
  `elapsed`, `startedAt`, `states`, `caps`, `completed` (a Set), `factCount`, `orbs`.
  `pieces[]` and `pins[]` hold the 3D objects; each piece has a state machine
  `dock → dragging → placing → placed` (or `returning`), and each pin adds `rejecting`.
- **Geometry** — `buildPieces()` (`index.html:2046`) extrudes every polygon with a
  bevel, edge lines and an invisible pick proxy; `buildPins()` (`index.html:2174`) builds
  base, ring, stem, collar, dome, label and proxy. The map plate and inset board are
  `buildMapBase()` (1717) and `buildInsetBoard()` (1882).
- **Coordinates** — map is 32 × 19.85 units; `MAP_Y = 0.24`, `PIECE_DEPTH = 0.62`,
  `SOCKET_Y = 0.91`, `DOCK_Y = 0.19`, `DRAG_Y = 1.72`, `PIN_DRAG_Y = 1.20`
  (`index.html:944–953`). State tray centre `(-26.8, 0)`, capital tray `(0, 20.3)`;
  grids are 5 × 10 and 10 × 5.
- **Snapping** — state drop requires distance `< 3.05` from the anchor and yaw within
  `0.18` rad (`endStateDrag`, `index.html:2557`; `snapState`, 2648). A pin is accepted
  when dropped inside the correct placed state or within `2.85` of its socket
  (`endPinDrag`, 2584; `snapPin`, 2691); a different state triggers `rejectPin` (2732).
- **Rotation** — `rotatePiece()` (`index.html:2783`) adds 45°; 34% of pieces start at
  −45° in `resetBoard()` (`index.html:3145`). `R`, double-click and the floating
  **Rotate 45°** button all use it.
- **Dossier** — `showStateInfo()` (`index.html:2940`) computes density from area and
  population, builds neighbour chips and reports whether the state is placed.
- **Victory** — `checkVictory()` (`index.html:3235`) fires only when both counters reach
  50; `triggerVictory()` (3240) stops the timer, creates 520 particles, starts a 9 s
  orbit and reveals the results card after 7.6 s (1.2 s with reduced motion).
- **Audio** — `SoundEngine` (`index.html:982`) creates one context on the first gesture
  and synthesises clicks, a wooden snap, a buzz, a chime and a victory fanfare.
- **Automation** — `window.__ATLAS__` (`index.html:3502`) exposes read-only state and
  screen projections; `?test=1` adds `place`, `crown` and `solve` (3539–3564).

## 4. Decisions and constraints

- **One HTML file is the deliverable.** The CSS anchors, canvas helpers, audio and game
  all live in `index.html`. Do not split it into a bundler project for convenience; the
  single-file property is the product.
- **Map data is duplicated on purpose.** `assets/mapdata.js` is the editable/generated
  source; `index.html` carries the same payload between build markers so the game runs
  without a fetch. `tools/build.py` is the only supported way to sync them.
- **Three.js is pinned to r160 via import map.** `index.html:907–914` points at jsDelivr.
  Changing the version or host requires re-running the solve and screenshots.
- **The network dependency is real.** There is no local Three.js copy and no offline
  mode. The 9-second timeout (`index.html:916–924`) only changes the loader text.
- **No persistence is a choice.** No `localStorage`, `sessionStorage`, cookie, export or
  resume exists. Do not add autosave without designing a reset/migration path and
  updating the docs.
- **Snap radii and the 45° grid are gameplay contracts.** `SNAP_RADIUS = 3.05`,
  `PIN_SNAP_RADIUS = 2.85` and the `0.18` rad alignment test decide what feels fair.
  Change them together, then re-solve all fifty.
- **Progress counters live inside the snap callbacks.** `game.states++` and `game.caps++`
  happen in `snapState` / `snapPin`. Do not increment them from drag handlers or the
  test helpers, or double counting and false victories follow.
- **State and pin objects are state machines.** Animations and `returnToDock` /
  `returnPin` assume the current state. Replacing a tween without preserving the state
  transition can leave pieces unclickable.
- **The map is educational, not authoritative.** Boundaries are projected and
  simplified; populations are estimates. Keep that framing in the README and dossier.
- **Audio is gesture-gated.** `sound.ensure()` must run inside the click handler before
  any playback; browsers block otherwise.
- **The automation mutators are test-only.** `place`/`crown`/`solve` exist only under
  `?test=1`, but they ship in the published file. Keep them side-effect-free outside
  their intended test path or remove them deliberately.
- **Docs-only changes should not touch `index.html`.** The published app is served
  directly from `main`; there is no staging build.

## 5. Known issues

- **No offline mode.** If jsDelivr is blocked the loader reports "Unable to load
  Three.js — check your connection and reload" after 9 seconds. The import map has no
  `integrity` metadata.
- **No save or resume.** Reloading loses progress, elapsed time, mute state and camera
  position; Scramble resets deliberately. `CONTRIBUTING.md` asks contributors to test
  "reload and persistence", which does not match this app — that is a documentation
  inconsistency, not a missing feature.
- **Keyboard-only users cannot play.** `R`, `M`, `H` and `Esc` work, but picking up,
  moving and dropping a piece requires a pointer drag. The help modal lists the pointer
  gestures; `CONTRIBUTING.md`'s "keyboard paths" checklist overstates the current state.
- **Mobile framing is loose.** At 390 × 844 the layout has no horizontal overflow, but
  the whole table is pulled back into a small band with large empty areas above and
  below. Pieces are hard to grab at that scale. Real touch hardware is unverified.
- **Rapid solving suppresses most fact cards.** `enqueueFact()` queues one card per
  capital and shows each for 5.2 s; `triggerVictory()` clears the queue. A scripted solve
  reaches `factCount = 50` while displaying only a few.
- **The `?test` mutators ship in production.** They bypass the drag and rotation checks
  and can mark progress; the read-only `__ATLAS__` object is always present.
- **No CI or automated test suite.** Verification is the manual matrix plus a
  DevTools-driven solve. There is no `package.json`, runner or workflow.
- **Only Chromium headless was verified.** Safari, Firefox, Edge, real iOS/Android,
  touch gestures, HiDPI rendering and screen-reader output are unverified.
- **Accessibility is partial.** The HUD status is `aria-live`, buttons have labels and
  the canvas has an `aria-label`, but drag/drop has no keyboard equivalent, dialogs have
  no focus trap, and the viewport sets `user-scalable=no`.
- **Boundaries and figures are simplified.** State shapes are Douglas–Peucker-simplified
  census polygons and populations are 2023 estimates; do not use them for navigation,
  legal or statistical work.
- **`STATE.md` is a historical receipt.** It records 3,566 lines / 162,264 bytes; the
  current file is 3,583 lines / 163,690 bytes. It also has no functional test record.

## 6. Continuity

- Live: <https://somphol.github.io/us-map-jigsaw-3d/> (HTTP 200 at the time of writing).
- Pages: `main` branch, repository root, `.nojekyll` present, no Actions workflow.
- Repository: <https://github.com/somphol/us-map-jigsaw-3d>.
- Local master copy: `~/Projects/us-map-jigsaw-3d`.
- Initial build: commit `fd9251b` "feat: United States Atlas — 3D map & capitals jigsaw".
- Alaska/Hawaii insets: commit `43a5326` "feat: complete all fifty states with Alaska
  and Hawaii insets".
- Last source/state commit before the documentation release: `567e354` "docs: add
  complete repository documentation and community files".
- Documentation release: the commit adding this file and `docs/`.
- Author: Somphol Boonjing, MIT. State boundaries are public-domain Census-derived data;
  see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
