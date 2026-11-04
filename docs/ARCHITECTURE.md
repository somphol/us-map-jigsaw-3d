# Architecture

`us-map-jigsaw-3d` is a static, single-document Three.js puzzle. This map covers the
parts that control behaviour: the data pipeline, the scene, the drag/snap state machines,
and the UI. It is not a file dump.

## 1. File map

| File | Lines | Contents |
| --- | ---: | --- |
| `index.html` | 3,583 | head/meta (1–9), all CSS (10–681), canonical/OG/Twitter (682–699), body and HUD (700–898), inlined map data (900–905), import map (907–914), 9 s CDN timeout (916–924), game module (926–3581) |
| `assets/mapdata.js` | 2 | `window.US_MAP_DATA`; 50 states, 32 × 19.85 units, 55 polygons, 739 points, AK/HI insets |
| `tools/generate_map_data.py` | 422 | source fetch, Albers/inset projection, simplification, capitals, neighbours, area/population metadata |
| `tools/build.py` | 24 | inlines `assets/mapdata.js` into `index.html` between `/* MAP_DATA_START */` and `/* MAP_DATA_END */` |
| `docs/social-card.png` | — | 1200 × 630 link preview |
| `STATE.md`, `state.json` | 45 / — | historical build receipt (not regenerated) |

CSS blocks in `index.html`:

| Range | Block |
| --- | --- |
| 11–53 | tokens, reset, body, vignette |
| 54–172 | HUD (brand, stats, bars, actions) |
| 173–282 | hint bar and rotate dock |
| 283–309 | tooltip |
| 310–340 | toasts |
| 341–403 | fact card |
| 404–450 | state dossier |
| 451–560 | welcome/help modal |
| 561–609 | victory overlay |
| 610–637 | loader |
| 638–677 | breakpoints at 980 and 720 px |
| 678–681 | reduced motion |

HTML blocks:

| Range | Block |
| --- | --- |
| 700–702 | stage and vignette |
| 704–744 | header: brand, states/capitals/time, help, sound, scramble |
| 746–752 | Overview / Map / State tray / Capitals / Pacific |
| 754–763 | hint and floating **Rotate 45°** dock |
| 764–771 | side note, tooltip, toast host, flash layer |
| 773–799 | fact card |
| 800–821 | state dossier |
| 823–871 | welcome/help modal |
| 873–890 | victory results |
| 892–898 | loader |

Module sections in `index.html`:

| § | Lines | Subject |
| --- | --- | --- |
| Data & constants | 930–977 | `DATA`, `STATES`, anchors, constants, easing |
| Audio engine | 978–1120 | `SoundEngine`, shared `sound` |
| Renderer/scene/camera | 1121–1153 | renderer, scene, camera, `OrbitControls`, pick registries |
| Visual helpers | 1154–1408 | shapes, canvas textures, sprites, wood/felt/plate maps |
| Tweens | 1409–1446 | tag-based animation manager |
| Scene construction | 1447–2041 | `init`, lights, table, compass, map base, inset board, docks |
| State pieces | 2042–2169 | 50 extruded blocks, proxies, slot visuals |
| Capital pins | 2170–2236 | 50 brass pins |
| Atmosphere | 2237–2262 | dust motes |
| Interaction | 2263–2935 | pointer, drag, snapping, rotation, hover, rejection |
| State dossier | 2936–2980 | inspector and neighbours |
| HUD/timer/facts | 2981–3096 | counters, timer, fact queue, toasts, hints |
| Welcome/help | 3097–3140 | rules modal and `beginGame` |
| Reset/scramble | 3141–3230 | board reset |
| Victory | 3231–3331 | 50/50 check, orbit, particles, results |
| Camera flights | 3332–3354 | view buttons |
| Effects | 3355–3379 | snap bursts |
| Ambient animation | 3380–3497 | render loop and updates |
| Debug/automation | 3498–3565 | `__ATLAS__`, `?test` mutators |
| Boot | 3566–3581 | `init()` and the failure card |

## 2. Runtime state

```js
game = {
  started: false, finished: false, running: false,
  elapsed: 0, startedAt: 0, states: 0, caps: 0,
  completed: new Set(), factCount: 0, orbs: 0
}
```

`game` is defined at `index.html:1141`. The rest of the session state is held in module
variables:

| Value | Purpose | Persisted? |
| --- | --- | --- |
| `pieces[]` | 50 `{data, group, state, dock, baseYaw, dockScale, topMat, collar, label}` | no |
| `pins[]` | 50 `{data, group, state, dock, socketOwner, label}` | no |
| `slotVisuals` | per-state plate label, halo, fill, socket dot | no |
| `pickables[]` | invisible proxies used by the raycaster | no |
| `activeDrag`, `pendingInspect`, `hoveredRef` | pointer session | no |
| `game.completed` | set of crowned state ids | no |
| `game.elapsed` | timer in ms | no |
| `sound.muted` | audio mute | no |
| camera / controls | view and orbit target | no |

Piece states are `dock`, `dragging`, `placing`, `placed` and `returning`. Pin states add
`rejecting`. `snapState()` and `snapPin()` are the only places that increment
`game.states` / `game.caps`; `checkVictory()` reads both counters.

## 3. Data pipeline

```text
PublicaMundi us-states.json (Census-derived)
        │  tools/generate_map_data.py
        ├─ Albers conic for the 48 contiguous states
        ├─ inset projection for Alaska (lat0 64) and Hawaii (lat0 20.6)
        ├─ Douglas–Peucker simplification
        ├─ capitals, neighbours, area, population, order, colour
        └─ assets/mapdata.js  (window.US_MAP_DATA)
                    │  tools/build.py
                    └─ index.html between MAP_DATA_START / MAP_DATA_END
```

The generator fetches its source over the network; the game does not. The inlined copy
is what ships. `assets/mapdata.js` and the block in `index.html` must stay identical;
`build.py` is the supported sync tool and only touches the marked block.

Audited payload (2026-11-03): **50 states, 50 unique ids/names/capitals, admission order
1–50 complete, 55 polygons, 739 points, no dangling neighbour names, AK and HI flagged
as insets.** Michigan, Hawaii and Virginia keep multiple polygons.

Each state record carries `id`, `name`, `capital`, `population`, `area`, `neighbors[]`,
`order`, `color`, `center`, `capitalPt`, `polys[][]`, `inset`. At load, an `anchor` is
computed as the bounding-box centre of all polygon points (`index.html:937–943`) so the
block can be packed in the tray and snapped by its centre.

## 4. Scene construction and coordinates

`init()` (`index.html:1451`) builds in this order: renderer → scene → camera →
OrbitControls → lights → label points → table → map base → docks → inset board → pieces
→ pins → dust → events. It then opens the welcome gate on the next frame and starts the
loop.

Coordinates are game units, not degrees:

| Constant | Value | Meaning |
| --- | ---: | --- |
| `MAP_W`, `MAP_H` | 32, 19.85 | map plate extents |
| `MAP_Y` | 0.24 | top of the plate |
| `PIECE_DEPTH` | 0.62 | extruded block height |
| `SOCKET_Y` | 0.91 | capital socket height |
| `DOCK_Y` | 0.19 | tray rest height |
| `DRAG_Y` | 1.72 | state drag plane |
| `PIN_DRAG_Y` | 1.20 | pin drag plane |
| `SNAP_RADIUS` | 3.05 | state anchor tolerance |
| `PIN_SNAP_RADIUS` | 2.85 | capital socket tolerance |
| `TRAY.state` | cx −26.8, cz 0, 17 × 40 | left tray |
| `TRAY.capital` | cx 0, cz 20.3, 35.6 × 15.6 | bottom tray |

`STATE_COLS = 5`, `STATE_ROWS = 10`, `CAP_COLS = 10`, `CAP_ROWS = 5`; dock positions are
computed by `stateDockPosition()` (2025) and `capitalDockPosition()` (2033). The map
plate is `buildMapBase()` (1717); the Pacific plaque is `buildInsetBoard()` (1882), using
`DATA.insets` from the generated file.

The renderer caps DPR at 2, enables PCF soft shadows, sRGB output and ACES tone mapping
with exposure 1.01. The camera FOV is 54° in portrait, 44° in square-ish aspect and 38°
in landscape (`fovForAspect`, 1517); `getOverviewPose()` (1523) pulls back for portrait
so both trays stay in frame. OrbitControls has damping 0.065, distances 12–230 and polar
limits 0.18–1.36 rad.

## 5. Interaction and snapping

```text
pointerdown → pickAt() → beginStateDrag / beginPinDrag
pointermove → drag plane at DRAG_Y or PIN_DRAG_Y → highlight slot / socket
pointerup   → endStateDrag / endPinDrag
                ├─ state: distance + yaw test → snapState / returnToDock
                └─ pin:   placed-state hit or nearest socket → snapPin / rejectPin
```

Key functions:

- `setupEvents()` (`index.html:2267`) — pointer, resize, keyboard, all buttons.
- `pickAt()` (2373) — raycasts the invisible proxies, not the visible meshes.
- `beginStateDrag()` (2417) / `beginPinDrag()` (2455) — lift, scale and disable orbit.
- `endStateDrag()` (2557) — accepts distance `< 3.05` **and** `|yaw| < 0.18`; a near but
  twisted piece is returned with a rotate hint.
- `snapState()` (2648) — 0.62 s spring to the anchor, `game.states++`, HUD, chime,
  `checkVictory()`.
- `endPinDrag()` (2584) — prefers `findPlacedStateAt()` (point-in-polygon), falls back to
  the nearest socket under 2.85 units.
- `snapPin()` (2691) — seats the pin, `game.caps++`, adds to `completed`, queues a fact.
- `rejectPin()` (2732) — buzz, red flash, socket shake, return to tray.
- `rotatePiece()` (2783) — +45°; also bound to `R`, double-click and the rotate dock.
- `returnToDock()` / `returnPin()` (2618 / 2635) — animated reset without touching
  counters.

`resetBoard(scramble)` (3145) resets counters, completed set, timer, victory effects and
every piece/pin; 34% of pieces are given a −45° starting yaw and a smaller dock scale.
`game.elapsed` is wall-clock time derived from `performance.now()`; time spent in a
background tab is included when the render loop resumes.

## 6. UI, dossier, audio

`updateHUD()` (2985) writes `#statesCount`, `#capsCount`, both bar widths and the fact
count. `updateTimerUI()` (3016) is called every 15 frames from the loop; `formatTime()`
(2993) renders `MM:SS`. The fact queue (`enqueueFact`, 3024) shows one card per correct
capital for 5.2 s; `showNextFact()` (3030) drains the queue.

`showStateInfo()` (2940) fills the dossier: capital, admission order, area, population,
density (`population / area`), neighbour chips and whether the state is currently placed.
Neighbour chips are real buttons and re-open the dossier for that state.

`SoundEngine` (982) lazily creates `AudioContext` on the first user gesture. `click()`
uses a short filtered noise burst; `snap()` adds a wooden body; `buzz()` a low oscillator;
`chime()` a two-tone bell; `victory()` a short arpeggio. `M` and `#soundBtn` toggle mute.

The welcome modal (`openWelcome`, 3101) pauses the timer when opened over a running game
and offers **Begin assembly** / **Return to the table**. `beginGame()` (3126) starts the
timer only once.

## 7. Victory and effects

`checkVictory()` (3235) requires `game.states === 50 && game.caps === 50`.
`triggerVictory()` (3240) sets `game.finished`, stops the timer, clears the fact queue,
sets every placed piece's emissive intensity to 0.36, creates 520 particles
(`createVictoryParticles`, 3275), starts a 9 s orbit around the map and reveals
`#victory` after 7.6 s (1.2 s under reduced motion). The results card shows the elapsed
time, 50 states, 50 capitals and the fact count. **Play again** calls `resetBoard(true)`
and restarts; **Keep exploring** just closes the card.

`flyCamera()` (3336) tweens position and target for the five view buttons. `burstAt()`
(3359) creates a short additive ring on every snap. The render loop (`animate`, 3387)
caps `dt` at 50 ms, updates tweens, dust, water/boat motion, HUD every 15 frames and the
timer, then renders.

## 8. Data flow

```text
US_MAP_DATA ──► STATES ──► buildPieces() ──► pieces[]
                    │                 └──► slotVisuals
                    ├──► buildPins() ──► pins[]
                    └──► buildDocks() / buildInsetBoard()

pointer drag ──► activeDrag ──► endStateDrag ──► snapState ──► game.states++
                                                    └──► checkVictory()
                                                   endPinDrag ──► snapPin ──► game.caps++
                                                                     └──► enqueueFact()

checkVictory(50,50) ──► triggerVictory() ──► particles + orbit + results card
```

## 9. Change guide

| To change… | Touch | Watch out for |
| --- | --- | --- |
| State colours or labels | generated `color`, `buildPieces`, `chooseLabelPoint` | label/socket overlap; rerun the data audit |
| Snap feel | `SNAP_RADIUS`, `PIN_SNAP_RADIUS`, `endStateDrag` yaw test | re-solve all 50 states and pins |
| Tray layout | `TRAY`, `STATE_COLS/ROWS`, `CAP_COLS/ROWS`, dock functions | camera overview and portrait fit |
| Map or inset geometry | `tools/generate_map_data.py`, then `tools/build.py` | never hand-edit only one copy |
| Rotation behaviour | `rotatePiece`, `onDoubleClick`, `onKeyDown`, `#rotateBtn` | 45° increments and the −45° start |
| Dossier fields | `showStateInfo`, `index.html` dossier markup | density is computed; neighbours must exist |
| Victory timing | `triggerVictory`, `createVictoryParticles` | reduced-motion branch and orbit length |
| Camera views | `getOverviewPose`, `flyCamera`, `#*Btn` bindings | `controls.enabled` is restored on completion |
| Audio | `SoundEngine` | keep context creation inside a gesture |
| Mobile layout | CSS 638–677, `fovForAspect` | test 390 × 844 and a real phone |
| Test hooks | `window.__ATLAS__`, `?test` block | mutators must not run without the query flag |

Keep the app static: one HTML file, CDN Three.js, no build server, no analytics, no
persistence. A change that needs any of those is a product decision, not a refactor.
