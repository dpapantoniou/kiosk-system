# Kiosk UI walkthrough

Screenshots captured via Chrome DevTools MCP at 1920×1080 (landscape) and 800×1290 (portrait), against the demo questionnaire (`?demo=1`). The **Acme & Co.** wordmark in the header is a placeholder; real deployments receive `data.logo_data` from `/by-code/{code}` and render the tenant logo there.

## Landscape (1920×1080)

### 1. Attract — full-bleed canvas, multilingual phrase crossfade, mono ticker
![](./screenshots/01-attract.png?v=3)

### 2. Language picker — three native-script cards with drop-cap watermark
![](./screenshots/02-language.png?v=3)

### 3. Survey · rating — pill buttons, terracotta selection
![](./screenshots/03-survey-rating.png?v=3)

### 4. Survey · single choice — square indicator, full-row tap target
![](./screenshots/04-survey-single.png?v=3)

### 5. Survey · multi-choice — square + animated checkmark
![](./screenshots/05-survey-multi.png?v=3)

### 6. Survey · text — bottom-border-only field, mono floating label
![](./screenshots/06-survey-text.png?v=3)

### 7. Inline validation — margin manicule replaces `alert()`, multilingual
![](./screenshots/07-validation.png?v=3)

### 8. Idle warning — quiet footnote at top-center, fires at 75% of timeout
![](./screenshots/08-idle-warning.png?v=3)

### 9. Offline badge — top-right pulsing indicator, multilingual
![](./screenshots/09-offline.png?v=3)

### 10. Cooldown overlay — surfaced on HTTP 429, 4s before returning to attract
![](./screenshots/10-cooldown.png?v=3)

### 11. Keyboard handling — `body.kbd-open` reserves bottom space for the OS keyboard so the text field + Continue stay visible
![](./screenshots/11-keyboard-open.png?v=3)

### 12. Thank-you (Greek) — typographic full-stop with terracotta period
![](./screenshots/12-thanks-el.png?v=3)

### 13. Thank-you (English)
![](./screenshots/13-thanks-en.png?v=3)

## Portrait (800×1290) — for 10–13" Elo tablets

### 14. Attract
![](./screenshots/14-portrait-attract.png?v=3)

### 15. Language picker — single-column stack
![](./screenshots/15-portrait-language.png?v=3)

### 16. Survey — single-column with horizontal meta row at the bottom
![](./screenshots/16-portrait-survey.png?v=3)
