# frontend-kiosk

Vanilla HTML/CSS/JS kiosk frontend for CX-FP. Runs on locked 15" 1920×1080 touchscreen Linux devices in Chrome kiosk mode.

## Files

- `index.html` — single-page state machine. Hand-edit.
- `input.css` — **CSS source.** Tailwind 4 directives, `@theme` tokens, `@layer components`. Hand-edit.
- `kiosk.css` — **GENERATED** from `input.css`. Do not hand-edit; the next build wipes your changes.
- `fonts/` — self-hosted variable fonts (Fraunces, JetBrains Mono).
- `tailwindcss` — standalone binary, **not** in git. See setup below.

The kiosk itself only ever loads `index.html` + `kiosk.css` + `fonts/`. Tailwind is dev-only.

## Setup (per dev machine)

```sh
# Download the standalone Tailwind binary for your platform
# (~73MB; this lives outside git via .gitignore)
curl -fsSL -o tailwindcss \
  https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-macos-arm64
chmod +x tailwindcss
```

Releases for other platforms: <https://github.com/tailwindlabs/tailwindcss/releases/latest>

## Workflow

```sh
# Watch — regenerates kiosk.css on every save of input.css
npm run dev:css

# Production build — minified
npm run build:css
```

Commit `kiosk.css` along with `input.css` whenever you change tokens or component classes. The kiosk is deployed via `scp`; we don't run a build step on the deploy host.

## Demo mode

Append `?demo=1` to the URL to boot a four-question demo questionnaire (rating + single-choice + multi-choice + text, with one branching rule) without touching the backend. Submitting in demo mode short-circuits the POST and goes straight to the thank-you screen. Useful for showing the UI to stakeholders or running locally without the FastAPI service.

```
http://localhost:8765/index.html?demo=1
```

## Aesthetic

Editorial Quiet — single typeface (Fraunces variable) carrying multiple voices via opsz/SOFT/wght axes; JetBrains Mono for meta. Warm paper-and-ink palette, single terracotta accent. See `input.css` for the token system.
