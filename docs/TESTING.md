# Testing

## Status of this release

| Evidence | When | Result |
| --- | --- | --- |
| Local init (headless Chrome, HTTP) | 2026-11-03 | **loader hidden, welcome gate open**, 50 pieces, 50 pins |
| Local DOM dump | 2026-11-03 | **163,970 bytes**, 0/50 and 0/50 counters |
| Data audit (Node) | 2026-11-03 | **50 states, 50 unique capitals, order 1–50, 55 polygons, 739 points** |
| Full scripted solve (CDP) | 2026-11-03 | **50 / 50 states, 50 / 50 capitals, 50 fact cards**, timer **00:09**, 0 exceptions |
| Victory overlay | 2026-11-03 | **visible**, shows 00:09, 50 states, 50 capitals, 50 facts |
| Live Pages init | 2026-11-03 | **163,970-byte DOM**, loader hidden, welcome open |
| Live Pages probe (`curl`) | 2026-11-03 | **200** |
| Local vs live `index.html` (SHA-1) | 2026-11-03 | **match** (`e0b080c3…`) |
| Desktop screenshot, 1600 × 913 | 2026-11-03 | **1,089,759-byte PNG** |
| Victory screenshot, 1600 × 913 | 2026-11-03 | **1,125,445-byte PNG** |
| Phone screenshot, 390 × 844 | 2026-11-03 | **199,554-byte PNG**, no horizontal overflow |
| jsDelivr probes (Three.js, OrbitControls) | 2026-11-03 | **200 / 200** |
| No-GPU negative control | 2026-11-03 | **"The table could not be prepared"** card |
| Safari / Firefox / Edge / real touch / screen reader | — | **Not verified** |
| CI | — | **None exists** in this repository |

The documentation commit changes Markdown only; `index.html`, `assets/mapdata.js` and the
tools are untouched.

## 1. Commands

```bash
cd ~/Projects/us-map-jigsaw-3d

# run
python3 -m http.server 8000          # http://localhost:8000/
open index.html                      # markup only; ES modules need HTTP

# init smoke check (macOS WebGL via Metal)
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --use-angle=metal --mute-audio \
  --virtual-time-budget=12000 --timeout=30000 \
  --dump-dom "http://localhost:8000/?test=1" > /tmp/usmap-dom.html

grep -o 'id="loader" class="hide"' /tmp/usmap-dom.html
grep -o '<div class="modal-backdrop on" id="welcome"' /tmp/usmap-dom.html

# live probe and source match
curl -s -o /dev/null -w '%{http_code}\n' https://somphol.github.io/us-map-jigsaw-3d/
shasum index.html
curl -sL https://raw.githubusercontent.com/somphol/us-map-jigsaw-3d/main/index.html | shasum

# data audit (no browser)
node - <<'JS'
const fs=require('fs'), s=fs.readFileSync('assets/mapdata.js','utf8');
const d=JSON.parse(s.slice(s.indexOf('{'),s.lastIndexOf('}')+1)), st=d.states;
const orders=st.map(x=>x.order).sort((a,b)=>a-b);
console.log(st.length, new Set(st.map(x=>x.capital)).size,
  orders[0], orders[orders.length-1],
  st.reduce((n,x)=>n+x.polys.length,0),
  st.reduce((n,x)=>n+x.polys.reduce((m,p)=>m+p.length,0),0));
JS
```

### Full solve

The app ships a test harness behind `?test=1`:

```js
__ATLAS__.place(id)   // snap a state to its slot
__ATLAS__.crown(id)   // seat that state's capital
__ATLAS__.solve()     // all 50 states, then all 50 capitals
```

Open `http://localhost:8000/?test=1` in a browser and run `__ATLAS__.solve()` in the
console. For headless verification, launch Chrome with
`--remote-debugging-port=9229 --user-data-dir=/tmp/usmap-profile`, attach with the
DevTools Protocol (Node's built-in `WebSocket` is enough), evaluate `solve()`, wait about
9 seconds, and read:

```js
({
  game: __ATLAS__.game,
  victory: document.getElementById('victory').className,
  states: document.getElementById('statesCount').textContent,
  caps: document.getElementById('capsCount').textContent
})
```

The observed result was:

```text
states 50, caps 50, factCount 50, finished true, elapsed 9372 ms
victory class "victory-backdrop on"
HUD 50 / 50, timer 00:09, victoryFacts 50
Runtime.exceptionThrown events: 0
```

Screenshots were captured through `Page.captureScreenshot` in the same session.

### Negative control

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --mute-audio \
  --virtual-time-budget=12000 --timeout=30000 \
  --dump-dom "http://localhost:8140/" > /tmp/usmap-nogpu.html
grep -o 'The table could not be prepared' /tmp/usmap-nogpu.html
```

With no GPU the renderer throws, the top-level `try/catch` replaces the loader content
with **"The table could not be prepared"** and a browser/WebGL explanation. The dump was
163,860 bytes and did not reach the welcome gate.

## 2. Results (2026-11-03)

### Local initialisation

```text
DOM dump:            163,970 bytes
loader:              class="hide"
welcome:             class="modal-backdrop on"
pieces:              50
pins:                50
counters:            0 / 50 states, 0 / 50 capitals
timer:               00:00 before Begin
```

The 50/50 piece and pin counts came from `window.__ATLAS__` via CDP, not from the DOM
alone.

### Data audit

```text
states 50 · unique ids 50 · unique names 50 · unique capitals 50
admission order 1–50 complete
bad records 0 · dangling neighbour names 0
polygons 55 · points 739
inset states AK:alaska, HI:hawaii
multi-polygon states HI, MI, VA
```

This checks the generated payload only; it does not re-validate the source GeoJSON
against the Census Bureau.

### Scripted solve

`__ATLAS__.solve()` places a state every 90 ms and a capital every 110 ms starting at
1.4 s. The run reached:

```text
game.states = 50
game.caps = 50
game.factCount = 50
game.finished = true
game.elapsed = 9,372.7 ms
victory = "victory-backdrop on"
victoryTime = "00:09"
victoryFacts = 50
uncaught exceptions = 0
```

The victory card appeared after the 7.6 s orbit reveal. This proves the counters, both
snap paths, the fact queue, the 50/50 gate and the results card. It does **not** prove
that a human can drag, rotate and drop every piece comfortably.

### Live Pages build

The same initial DOM was 163,970 bytes with the loader hidden and the welcome gate open.
`https://somphol.github.io/us-map-jigsaw-3d/` returned 200 and the live `index.html`
matched the local SHA-1 (`e0b080c364c505baf867018a70b0969f8a9044f1`). The full solve was
run locally, not against the live URL.

### Screenshots

| View | Size | Observed |
| --- | --- | --- |
| Table after Begin, 1600 × 913 | 1,089,759 bytes | 50 state blocks, 50 pins, 0/50, timer 00:01 |
| Victory, 1600 × 913 | 1,125,445 bytes | 50/50, 00:09, 50 fact cards, results card |
| Phone table, 390 × 844 | 199,554 bytes | no horizontal overflow; table small with empty bands |

The repository's own screenshots are older, larger captures from the 2026-10-31 build;
the evidence above is from the current source.

## 3. Manual matrix

| Area | Check | Status |
| --- | --- | --- |
| Entry | Loader hides, welcome gate opens over a rendered table | Verified headless |
| Entry | Begin closes the gate and starts the timer | Verified by scripted click |
| Drag | Pick a state, lift it, move it on the drag plane | Logic verified; gesture not measured |
| Rotate | `R`, double-click and the floating button add 45° | Code paths shared through `rotatePiece`; not gesture-tested |
| Snap | Correct position + 0° yaw seats a state | Verified by 50-state solve |
| Snap | Near but twisted piece is returned with a rotate hint | Code inspection; not driven |
| Snap | Wrong position returns to tray | Code inspection; not driven |
| Pin | Correct capital seats and raises a fact card | Verified by 50-capital solve |
| Pin | Wrong capital buzzes, flashes and returns | Code inspection; not driven |
| Dossier | Click a placed state; area, population, density, neighbours | Markup/logic verified; click not headless |
| Dossier | Neighbour chip switches the dossier | Code inspection; not driven |
| Views | Overview, Map, State tray, Capitals, Pacific fly the camera | Bindings verified; flights not measured |
| HUD | Counters and bars update | Verified at 0 and 50 |
| Timer | Starts, pauses for help, stops on victory | Start/stop verified; pause by code |
| Scramble | Returns all pieces and resets timer | Code inspection; not driven |
| Victory | 50/50 triggers orbit, particles, results card | Verified via solve |
| Mobile | 390 × 844 has no horizontal overflow | Verified in emulation |
| Reload | Starts a fresh 0/0 table | Design; no storage code exists |
| Audio | Click, snap, buzz, chime, victory | Context and methods exist; quality not measured |

## 4. Failure triage

- **Loader never hides** — check the jsDelivr requests and the console. The module cannot
  start without Three.js; after 9 s the subtitle says the CDN failed.
- **"The table could not be prepared"** — WebGL is unavailable or the renderer threw.
  Use `--use-angle=metal` on macOS headless; check hardware acceleration in a normal
  browser.
- **Some pieces have no `anchor`** — the generated polygons are empty or malformed;
  re-run the data generator and the audit.
- **A state will not snap** — check its anchor, the 3.05 radius and whether yaw is within
  0.18 rad. The piece may need one 45° rotation.
- **A capital is rejected on the right state** — check `capitalPt`, the point-in-polygon
  test and whether that state is actually `placed`.
- **Counters jump or victory fires early** — inspect `game.states` / `game.caps` and the
  snap callbacks; the `?test` helpers bypass drag validation.
- **No audio** — the context is gesture-gated; click Begin first, then check the mute
  state and the browser's autoplay policy.
- **Fact cards stop appearing** — the queue shows one card per 5.2 s; victory clears it by
  design. `game.factCount` is still the total.

## 5. Not verified

- Human drag, rotate and drop feel; raycast tolerance and collision with other pieces.
- The rejection animations (buzz, red flash, socket shake) end to end.
- The dossier click path, neighbour chips and placing-state text.
- The five camera flights, their easing and control re-enable after victory.
- Scramble and **Play again** from the results card.
- Audio character, mix and the victory fanfare.
- Safari, Firefox, Edge, real iOS/Android, touch gestures and HiDPI rendering.
- Keyboard-only play; there is no keyboard pickup/drop path to test.
- Screen-reader announcements, focus order and modal focus trapping.
- Frame rate, GPU thermals and long-session memory use.
- Geographic accuracy of the simplified boundaries or the 2023 population estimates.
- The live full solve; only initialisation and the source hash were checked on Pages.
