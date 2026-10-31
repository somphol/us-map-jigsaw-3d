# Build State

| Field | Value |
| --- | --- |
| Project | United States Atlas (`us-map-jigsaw-3d`) |
| Started | 2026-10-31 18:24:10 UTC |
| Completed | 2026-10-31 19:38:36 UTC |
| Duration | **1h 14m 26s** (4465.9 seconds) |
| Harness | OpenCode 2.2.5 |
| Model | DeepSeek V4.1 Flash (`opencode-go/deepseek-v4.1-flash`) |
| Session | `ses_e6ccb8c03ffepuWoju93Bqua9y` |
| Repository | <https://github.com/somphol/us-map-jigsaw-3d> |
| Live demo | <https://somphol.github.io/us-map-jigsaw-3d/> |

## Token usage

| Metric | Tokens |
| --- | ---: |
| Input | 589,096 |
| Output | 122,782 |
| Reasoning | 172,829 |
| **Total (input + output + reasoning)** | **884,707** |
| Cache read | 53,404,800 |
| Cache write | 1,172 |
| Total including cache | 54,290,679 |

> Snapshot taken from the OpenCode session record when the project was packaged at 2026-10-31 19:38:36 UTC. The final commit/push commands and the closing response occur outside this snapshot, so the live session totals will be marginally higher.

## What was built

- One self-contained `index.html`: **146,664 bytes, 3,309 lines**.
- **All 50 states**: 48 contiguous extruded blocks on the main recessed baseplate, plus Alaska and Hawaii on a separate Pacific inset plaque.
- **All 50 capitals** as labeled 3D pins in a 10 × 5 brass tray.
- Raycast drag-and-drop, 45° rotation, dual-snap validation with rotation checks, wrong-capital rejection, Web Audio synthesis, fact cards, live timer, scramble/reset, and a 360° victory orbit with particles.
- A floating **Rotate 45°** control appears while dragging, alongside `R` and double-click rotation.
- Procedural mahogany/felt textures, semi-transparent recessed map plate, soft shadows, compass rose, Pacific inset, and a responsive glass HUD.
- Custom view buttons for Overview, Map, State tray, Capitals, and Pacific.
- Reproducible fifty-state geometry pipeline in `tools/`, and five rendered screenshots.

## Credits

Built with [OpenCode](https://opencode.ai) and **DeepSeek V4.1 Flash**. The game, 3D scene, HUD, audio, geometry pipeline, and documentation were generated in a single agent session.

State boundaries are derived from the public-domain PublicaMundi US states GeoJSON (US Census Bureau source data). Three.js is by mrdoob and contributors. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
