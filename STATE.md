# Build State

| Field | Value |
| --- | --- |
| Project | United States Atlas (`us-map-jigsaw-3d`) |
| Started | 2026-10-31 18:24:10 UTC |
| Completed | 2026-10-31 18:54:34 UTC |
| Duration | **30m 24s** (1823.9 seconds) |
| Harness | OpenCode 2.2.5 |
| Model | DeepSeek V4.1 Flash (`opencode-go/deepseek-v4.1-flash`) |
| Session | `ses_e6ccb8c03ffepuWoju93Bqua9y` |
| Repository | <https://github.com/somphol/us-map-jigsaw-3d> |
| Live demo | <https://somphol.github.io/us-map-jigsaw-3d/> |

## Token usage

| Metric | Tokens |
| --- | ---: |
| Input | 415,042 |
| Output | 79,895 |
| Reasoning | 94,812 |
| **Total (input + output + reasoning)** | **589,749** |
| Cache read | 17,169,920 |
| Cache write | 1,172 |
| Total including cache | 17,760,841 |

> Snapshot taken from the OpenCode session record when the project was packaged at 2026-10-31 18:54:34 UTC. The final commit/push commands and the closing response occur outside this snapshot, so the live session totals will be marginally higher.

## What was built

- One self-contained `index.html`: **133,978 bytes, 3,143 lines**.
- 30 playable extruded state blocks with capital sockets, and 30 labeled 3D capital pins.
- All 48 contiguous state outlines on the baseplate, with 18 non-playable states rendered as muted inlays.
- Raycast drag-and-drop, 45° rotation, dual-snap validation with rotation checks, wrong-capital rejection, Web Audio synthesis, fact cards, live timer, scramble/reset, and a 360° victory orbit with particles.
- Procedural mahogany/felt textures, semi-transparent recessed map plate, soft shadows, compass rose, and a responsive glass HUD.
- Separately reproducible map build pipeline in `tools/` and three rendered screenshots.

## Credits

Built with [OpenCode](https://opencode.ai) and **DeepSeek V4.1 Flash**. The game, 3D scene, HUD, audio, geometry pipeline, and documentation were generated in a single agent session.

State boundaries are derived from the public-domain PublicaMundi US states GeoJSON (US Census Bureau source data). Three.js is by mrdoob and contributors. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
