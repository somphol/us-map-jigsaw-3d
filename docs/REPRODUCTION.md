# Reproduction book

How to rebuild **United States Atlas — 3D Map & Capitals Jigsaw** from scratch, or
re-verify that a rebuild matches the published release. Read
[ARCHITECTURE.md](ARCHITECTURE.md) first for the file and function map.

> **The source is the truth.** `main` at HEAD is the release. There is no bundle, package
> manager or tagged version. Rebuild only when the files are unavailable or you
> deliberately want a variant.

## 1. What is being reproduced

A static, single-document 3D jigsaw of the United States:

- **Fifty state blocks** — extruded, bevelled polygons with edge lines, inside a
  recessed map plate; the 48 contiguous states on the main plate, Alaska and Hawaii on a
  labelled Pacific inset plaque.
- **Fifty capital pins** — brass base, ring, stem, collar, dome and label, in a 10 × 5
  bottom tray.
- **Fifty state labels and sockets** — abbreviation labels placed away from the capital
  socket so names stay readable; pulsing drop rings on the inset.
- **Drag, rotate, snap** — raycast drag on a raised plane, 45° rotation by `R`,
  double-click or the floating button, centre-distance plus yaw validation, spring drop.
- **Dual validation** — a capital pin must land on its own placed state (point-in-polygon)
  or within its socket radius; wrong pairings buzz, flash and return.
- **Educational feedback** — fact card per completed state/capital pair, and a click
  dossier with area, population, density, admission order and clickable neighbours.
- **Table and atmosphere** — procedural mahogany, felt, map plate, compass, studio
  lighting, soft shadows, dust motes, snap bursts.
- **Audio** — synthesised click, wooden snap, buzz, chime and victory fanfare.
- **HUD and victory** — live state/capital counters, progress bars, assembly timer, five
  camera views, scramble, 9 s victory orbit, particles and a results card.
- **Delivery** — one `index.html`; generated `assets/mapdata.js` inlined between build
  markers; Three.js r160 from jsDelivr. No build server, backend, persistence or CI.

## 2. Requirements matrix

| # | Requirement | Implementation | Where |
| ---: | --- | --- | --- |
| 1 | All fifty states, including AK/HI | generated `US_MAP_DATA`, `buildPieces`, `buildInsetBoard` | `assets/mapdata.js`, `index.html` |
| 2 | All fifty capitals, correctly paired | generated `capital`/`capitalPt`, `buildPins`, `snapPin` | `assets/mapdata.js`, `index.html` |
| 3 | 3D tabletop scene with plate and trays | `buildTable`, `buildMapBase`, `buildDocks` | `index.html` |
| 4 | Extruded state blocks with labels | `buildPieces`, `chooseLabelPoint`, `slotVisuals` | `index.html` |
| 5 | Drag-and-drop with generous picking | `pickAt`, `beginStateDrag`, `onPointerMove` | `index.html` |
| 6 | 45° rotation by three input paths | `rotatePiece`, `onDoubleClick`, `onKeyDown`, `#rotateBtn` | `index.html` |
| 7 | Position + yaw validation | `endStateDrag`, `SNAP_RADIUS`, `0.18` rad test | `index.html` |
| 8 | Capital validation against the state beneath | `findPlacedStateAt`, `pointInState`, `endPinDrag` | `index.html` |
| 9 | Rejection feedback (buzz/flash/shake/return) | `rejectPin`, `SoundEngine.buzz`, flash CSS | `index.html` |
| 10 | Fact card per completed pair | `enqueueFact`, `showNextFact` | `index.html` |
| 11 | State dossier with neighbours | `showStateInfo`, `#infoNeighbors` | `index.html` |
| 12 | Live counters, bars, timer | `updateHUD`, `updateTimerUI`, `startTimer` | `index.html` |
| 13 | Camera presets | `getOverviewPose`, `flyCamera`, view buttons | `index.html` |
| 14 | Synthesised audio, no files | `SoundEngine` | `index.html` |
| 15 | Victory sequence and results | `checkVictory`, `triggerVictory`, `createVictoryParticles` | `index.html` |
| 16 | Responsive desktop/phone layout | CSS 638–677, `fovForAspect` | `index.html` |
| 17 | Reproducible data pipeline | `generate_map_data.py`, `build.py` | `tools/` |
| 18 | Static Pages delivery | root `index.html`, `.nojekyll`, import map | repository root |

## 3. Build order

1. **Data** — fetch the PublicaMundi GeoJSON with `tools/generate_map_data.py`; project the
   48 contiguous states with Albers, Alaska and Hawaii with local inset projections;
   simplify rings; compute anchors, capitals, neighbours, area/population/order; write
   `assets/mapdata.js`.
2. **Inline** — run `tools/build.py` to replace the block between
   `/* MAP_DATA_START */` and `/* MAP_DATA_END */` in `index.html`.
3. **Shell** — head, fonts (system only), tokens, HUD, view buttons, hint, fact card,
   dossier, welcome/help, victory and loader. Keep the canvas as the only WebGL surface.
4. **Renderer and table** — renderer, scene, camera, OrbitControls, lights, mahogany
   table, compass, plate, inset plaque and trays.
5. **State pieces** — extrude every polygon, add edge lines, top/side materials, pick
   proxies, abbreviation labels and slot visuals.
6. **Capital pins** — brass geometry, labels, proxies and tray positions.
7. **Interaction** — pointer down/move/up, drag plane, orbit disable, rotation, hover,
   tooltips, slot/socket highlighting.
8. **Validation** — state distance/yaw test, pin point-in-polygon, socket fallback,
   rejection, return animations.
9. **Feedback** — counters, timer, fact queue, toast, hint, state dossier.
10. **Audio** — noise buffer, clicks, snap, buzz, chime, victory arpeggio.
11. **Victory** — 50/50 check, particle field, glow, orbit, results card, reset.
12. **Responsive and accessibility** — breakpoints, touch-friendly controls, focus styles,
   aria-live status, reduced motion.
13. **Automation and docs** — `__ATLAS__` projections, `?test` mutators, README, changelog,
   screenshots, this set.

## 4. Acceptance checks

A rebuild is done when all of these pass:

1. `python3 -m http.server 8000` serves the page; the loader hides and the welcome gate
   opens over a rendered table.
2. `window.__ATLAS__.pieces.length === 50` and `.pins.length === 50` after init.
3. The data audit reports 50 states, 50 unique ids/names/capitals, admission order 1–50
   complete, 55 polygons, 739 points and no dangling neighbour names.
4. Opening `?test=1` and running `__ATLAS__.solve()` reaches `states: 50`, `caps: 50`,
   `factCount: 50` and `finished: true` in about 9 seconds.
5. The HUD shows `50 / 50` for both counters and the victory card shows the elapsed time.
6. The victory overlay appears after the orbit reveal; **Play again** resets to 0/0 and
   **Keep exploring** closes the card.
7. Dragging a state to the wrong silhouette returns it; dropping within 3.05 units but
   without alignment gives the rotate hint instead of snapping.
8. Dropping a capital on the wrong placed state rejects it; dropping it on its own state
   increments the capital counter and shows a fact card.
9. Clicking a placed state opens the dossier with area, population, density and
   neighbour chips; clicking a neighbour switches the dossier.
10. The five view buttons move the camera and re-enable controls afterwards.
11. Scramble returns all pieces and pins to the trays and resets the timer.
12. At 390 × 844 the document has no horizontal overflow and the controls remain usable,
    even though the table is small.
13. A reload returns a fresh 0/0 table; there is no saved state by design.
14. The live `index.html` SHA-1 matches the local file.
15. No uncaught exceptions during init or a scripted solve.

Record what you actually ran in [TESTING.md](TESTING.md), including the things that
failed.

## 5. Provenance

| Item | Value |
| --- | --- |
| Initial build | `fd9251b` "feat: United States Atlas — 3D map & capitals jigsaw" |
| Alaska/Hawaii insets | `43a5326` "feat: complete all fifty states with Alaska and Hawaii insets" |
| State dossier / inset targets | `dea9a2e` "feat: add state dossier and clearer Pacific inset targets" |
| Repository docs and community files | `567e354` "docs: add complete repository documentation and community files" |
| Release docs | this commit (`AGENTS.md` + `docs/`) |
| Three.js | r160, MIT, imported from jsDelivr |
| Boundaries | PublicaMundi US states GeoJSON, public-domain Census-derived |
| Populations | approximate 2023 US Census Bureau estimates |
| Author | Somphol Boonjing, MIT |

There is no tagged release and no generated build artefact beyond the inlined map data.
`CHANGELOG.md` is the change record; `STATE.md` / `state.json` are the 2026-10-31 build
receipt and are not regenerated by later commits.
