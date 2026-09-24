# Trip.com experiment — steps (actual run by the instructor/AI, 2026-09-24)

Session: `playwright-cli -s=trip` · headless Chromium 154 · config `.playwright/cli.config.json`
Run date Asia/Bangkok: 2026-09-24 → departure date (+3 calendar days): **2026-09-27**

| # | State before | Action (command) | Observed result | Evidence | Elapsed (s) |
|---|---|---|---|---|---|
| 1 | No browser session | `open "https://www.trip.com/?locale=en-xx&curr=THB"` | Redirected to `verify.trip.com/static/tripVerify.html`, title "Trip.com-Verification" | — | 4.57 |
| 2 | Verification page, widget not yet rendered | `screenshot --filename=evidence/trip/01-home.png` | Blue background and text "To continue, please complete the verification test below." | 01-home.png | 0.25 |
| 3 | Same | `snapshot --filename=evidence/trip/01-home.yml` | 1 paragraph (ref e9), no search form | 01-home.yml | 0.20 |
| 4 | Same | wait (`sleep 8`) for the widget to load | — | phases.log | 8.01 |
| 5 | CAPTCHA widget visible | `screenshot` + `snapshot` (02-*) | "Select icons in the correct order" / "Slide to complete the puzzle" | 02-verify-after-wait.png/.yml | 0.51 |
| 6 | CAPTCHA | **Retry 1:** `goto https://www.trip.com/` | Redirected to verify again (new bgref) | — | 0.89 |
| 7 | Loading | wait (`sleep 6`) | — | phases.log | 6.00 |
| 8 | CAPTCHA widget visible (new image) | `screenshot` + `snapshot` (03-*) | Same puzzle again; refs changed from `e7` to `f2e7` (refs are transient) | 03-retry-blocked.png/.yml | 0.50 |
| 9 | CAPTCHA | `tracing-start` → `reload` → `screenshot` → `tracing-stop` | Still verify.trip.com; trace written to `.playwright-cli/traces/` | 04-reload-still-blocked.png (captured before the widget rendered), trace/ | 1.16 |
| 10 | BLOCKED | Stop the flight and hotel branches, `close` | "Browser 'trip' closed"; `list` → (no browsers) | blocker.md | 0.22 |

Result: **BLOCKED** — no flights or hotels were seen, so there is no comparison and no recommendation.
The full commands log with UTC timestamps and monotonic time is in `commands.log`.
