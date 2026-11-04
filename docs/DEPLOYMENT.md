# Deployment

Hosted on **GitHub Pages**, served straight from `main` as a static site. There is no
build artifact, package manager, backend or CI workflow: the committed `index.html` is
what is served.

- Live URL: <https://somphol.github.io/us-map-jigsaw-3d/>
- Repository: <https://github.com/somphol/us-map-jigsaw-3d>
- Source branch: `main`, folder `/` (repository root)
- Entry file: `index.html`
- Runtime network calls: **Three.js r160 and OrbitControls from jsDelivr** (see §3)

## 1. Deploy a change

```bash
cd ~/Projects/us-map-jigsaw-3d

# 1. verify locally (ES modules need HTTP)
python3 -m http.server 8000          # http://localhost:8000/
#    run the matrix in docs/TESTING.md

# 2. if map data changed, regenerate and inline it
python3 tools/generate_map_data.py
python3 tools/build.py

# 3. commit and push
git add -A
git commit -m "…"
git push origin main
```

Pages rebuilds on push, usually within a minute. Confirm:

```bash
curl -s -o /dev/null -w '%{http_code}\n' https://somphol.github.io/us-map-jigsaw-3d/
```

Re-check that the served document is the committed one:

```bash
shasum index.html
curl -sL https://raw.githubusercontent.com/somphol/us-map-jigsaw-3d/main/index.html | shasum
```

At the documentation release both hashes were
`e0b080c364c505baf867018a70b0969f8a9044f1`.

## 2. Repository settings that matter

| Setting | Value | Why |
| --- | --- | --- |
| Pages source | Deploy from a branch → `main` → `/ (root)` | the app lives at the root |
| Custom domain | none | default `*.github.io` host |
| Enforce HTTPS | on | default certificate |
| Actions | none required | no workflow exists in `.github/workflows/` |

`.nojekyll` is committed. Keep it: it stops Jekyll from processing the site and keeps the
publish path a plain static copy. Pages serves `.html`, `.css` and `.js` with normal MIME
types; the import map resolves `three` and `three/addons/` to jsDelivr.

## 3. Files that are published

Everything in the repository root is public, including documentation and screenshots:

- `index.html` — the complete game, CSS, inlined map data and module
- `assets/mapdata.js` — generated geometry/metadata source (not fetched at runtime)
- `tools/generate_map_data.py`, `tools/build.py` — data pipeline and inliner
- `screenshot.png`, `screenshot-menu.png`, `screenshot-rotate.png`,
  `screenshot-info.png`, `screenshot-inset.png`, `screenshot-complete.png`,
  `screenshot-victory.png` — README images, about 6.6 MB total
- `docs/social-card.png` — 1200 × 630 Open Graph / Twitter preview
- `README.md`, `CHANGELOG.md`, `AGENTS.md`, `docs/*.md`
- `STATE.md`, `state.json` — historical build receipt
- `THIRD_PARTY_NOTICES.md`, `LICENSE`
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`
- `robots.txt`, `sitemap.xml`
- `.github/` issue templates, pull-request template and CODEOWNERS

There is no secrets file, no environment variable and no runtime configuration.

**Runtime network dependencies.** These are real requests on every cold load:

| Request | Host | Purpose |
| --- | --- | --- |
| `three.module.js` r160 | `cdn.jsdelivr.net` | Three.js core |
| `OrbitControls.js` r160 | `cdn.jsdelivr.net` | camera orbit, pan, zoom |

The import map (`index.html:907–914`) has no `integrity` metadata. If jsDelivr is
unreachable the module never starts; the inline 9-second timeout
(`index.html:916–924`) changes the loader subtitle to "Unable to load Three.js — check
your connection and reload". Fonts are system stacks, not downloads. The generated map
data is inlined and is not fetched.

Do not describe the site as offline-capable.

## 4. Rollback

Pages serves the current `main`, so rolling back is a normal history operation:

```bash
git revert <bad-commit>          # preferred: keeps history
git push origin main
```

or, for an immediate local reset:

```bash
git reset --hard <good-commit>
git push --force-with-lease origin main
```

Force-pushing rewrites published history; prefer `git revert` unless the bad commit
contains something that must not remain public.

## 5. Caching

At the time of writing the live document returned:

```text
cache-control: max-age=600
etag: "6ae76b5d-27f6a"
last-modified: Sun, 01 Nov 2026 16:39:57 GMT
```

A browser may keep an old `index.html` for up to ten minutes. After a deploy, hard-refresh
(Shift-Reload) or check in a private window. There is no service worker and no offline
cache to invalidate. Pages serves ETags, so conditional requests are cheap.

## 6. Local preview versus production

ES modules are fetched with CORS rules, so `index.html` must be served over HTTP. Opening
it directly from `file://` does not run the module:

```bash
python3 -m http.server 8000
open http://localhost:8000/
```

Use HTTP for every check involving the 3D table. `file://` is only useful for inspecting
the markup. `?test=1` enables the `__ATLAS__.place/crown/solve` helpers; without it only
the read-only projections exist.

## 7. Platform requirements

- A browser with **WebGL**, ES modules and import-map support. Current Chrome, Edge and
  Safari are the intended targets; only Chromium was verified for this release.
- A network connection on first load for jsDelivr. There is no local Three.js copy.
- No GPU / disabled WebGL triggers the top-level catch: the loader is replaced with
  "The table could not be prepared" and a short explanation. Headless WebGL on macOS
  needs `--use-angle=metal`.
- Real touch hardware, HiDPI scaling and screen readers are unverified.
- No install, service worker or manifest; there is nothing to add to a home screen.
- Regenerating `assets/mapdata.js` needs network access to GitHub; that is a build-time
  tool, not a runtime dependency.
