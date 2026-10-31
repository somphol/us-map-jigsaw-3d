# Build State

| Field | Value |
| --- | --- |
| Project | United States Atlas (`us-map-jigsaw-3d`) |
| Started | 2026-10-31 18:24:10 UTC |
| Completed | 2026-10-31 22:24:01 UTC |
| Duration | **3h 59m 50s** (14390.5 seconds) |
| Harness | OpenCode 2.2.5 |
| Model | DeepSeek V4.1 Flash (`opencode-go/deepseek-v4.1-flash`) |
| Session | `ses_e6ccb8c03ffepuWoju93Bqua9y` |
| Repository | <https://github.com/somphol/us-map-jigsaw-3d> |
| Live demo | <https://somphol.github.io/us-map-jigsaw-3d/> |

## Token usage

| Metric | Tokens |
| --- | ---: |
| Input | 1,075,531 |
| Output | 150,052 |
| Reasoning | 225,251 |
| **Total (input + output + reasoning)** | **1,450,834** |
| Cache read | 79,892,992 |
| Cache write | 1,172 |
| Total including cache | 81,344,998 |

> Snapshot taken from the OpenCode session record when the project was packaged at 2026-10-31 22:24:01 UTC. The final commit/push commands and the closing response occur outside this snapshot, so the live session totals will be marginally higher.

## What was built

- One self-contained `index.html`: **162,264 bytes, 3,566 lines**.
- **All 50 states**: 48 contiguous extruded blocks on the main recessed baseplate, plus Alaska and Hawaii on a **Pacific inset plaque** with pulsing gold drop rings and full-name labels.
- **All 50 capitals** as labeled 3D pins in a 10 × 5 brass tray.
- **Click-to-inspect state dossier**: total area, population, population density, and clickable neighboring states for every placed state.
- **Capital sockets no longer mask state names**: each state abbreviation is placed by an interior label planner away from its capital socket while keeping the socket accurate.
- Raycast drag-and-drop, 45° rotation, dual-snap validation, wrong-capital rejection, Web Audio synthesis, fact cards, live timer, scramble/reset, and a 360° victory orbit with particles.
- A floating **Rotate 45°** control appears while dragging, alongside `R` and double-click rotation.
- Custom view buttons for Overview, Map, State tray, Capitals, and Pacific — and a start-up hint pointing to the Pacific inset.
- Procedural mahogany/felt textures, semi-transparent recessed map plate, soft shadows, compass rose, responsive glass HUD, and seven rendered screenshots.

## Credits

Built with [OpenCode](https://opencode.ai) and **DeepSeek V4.1 Flash**. The game, 3D scene, HUD, audio, geometry pipeline, and documentation were generated in a single agent session.

State boundaries are derived from the public-domain PublicaMundi US states GeoJSON (US Census Bureau source data). Three.js is by mrdoob and contributors. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
