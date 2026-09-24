# WAITING_FOR_HUMAN (2nd block)

- Status: **WAITING_FOR_HUMAN**
- WAIT_START UTC: 2026-09-24T12:39:03Z
- WAIT_START monotonic (/proc/uptime): 353954.43 (block first seen in snapshot at 12:38:46Z / mono 353937.51)
- Run path: /root/workspace/CWN/Teaching/00_setup/05_Playwright_CLI_Trip/runs/human-20260924T122658Z-298374
- Session: `lab05-human` (headless chromium, in-memory profile, --idle-timeout=0). Browser, context and tab were kept as-is.
- Previous wait (CAPTCHA at step 1) is closed: WAIT_END 2026-09-24T12:36:49Z, 554.33 s. The old help file is kept at evidence/trip/human-help-01-captcha.md.
- Stuck at: step 7, clicking "ค้นหา" on the flight form (filled through the UI: round trip, Bangkok all airports BKK+DMK → Tokyo all airports NRT+HND, 27 Sep 2026 – 1 Oct 2026, 1 adult, economy)
- Current URL: https://th.trip.com/flights/showfarefirst?dcity=bkk&acity=tyo&ddate=2026-09-27&rdate=2026-10-01&triptype=rt&class=y&lowpricesource=searchform&quantity=1&searchboxarg=t&nonstoponly=off&locale=th-TH&curr=THB
- Page type: **HTTP 432, plain text "whaleguard block"** (Trip.com bot-protection block page; no CAPTCHA widget shown)
- AI actions after the block: one passive snapshot and one screenshot. No reload, goto, retry or hotel search.
- Evidence: evidence/trip/14-flight-results.png (shows "whaleguard block"), 14-flight-results.yml (empty accessibility tree), commands.log, human-wait.log, phases.log, steps.md
- No flight or hotel prices were collected. results.md has not been written.

## For the human
1. Open the dashboard at http://127.0.0.1:9230/ (SSH tunnel if needed: `ssh -L 9230:127.0.0.1:9230 <host>`).
2. Select session **lab05-human** and look at the current tab (the "whaleguard block" page).
3. The page has no widget to solve. You could reload it or go back and search again from the dashboard, or pick one of these:
   - wait a few minutes and let the AI retry the same search once;
   - use headed or persistent-profile mode in a new run;
   - stop the Trip.com part and record the block as the lab result.
4. Reply with what you chose. The AI will then log WAIT_END, take a new snapshot and screenshot, and continue (flights, then hotel: 1 room, 1 adult, 4 nights, target THB 3000/night).

Dashboard: pid 298777, log dashboard.log. Stop it later with `kill $(cat /root/workspace/CWN/Teaching/00_setup/05_Playwright_CLI_Trip/runs/human-20260924T122658Z-298374/dashboard.pid)`.
