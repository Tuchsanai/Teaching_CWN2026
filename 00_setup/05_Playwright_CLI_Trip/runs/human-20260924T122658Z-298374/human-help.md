# WAITING_FOR_HUMAN

- Status: **WAITING_FOR_HUMAN**
- WAIT_START UTC: 2026-09-24T12:27:34Z
- WAIT_START monotonic (/proc/uptime): 353265.53
- Run path: /root/workspace/CWN/Teaching/00_setup/05_Playwright_CLI_Trip/runs/human-20260924T122658Z-298374
- Session: `lab05-human` (headless chromium, in-memory profile, --idle-timeout=0). Browser, context and tab were kept as-is.
- Stuck at: step 1 (setup), right after `open https://www.trip.com/`, before any search
- Current URL: https://verify.trip.com/static/tripVerify.html?returnUrl=https%3A%2F%2Fwww.trip.com%2F (full URL in evidence/trip/02-verify-recheck.yml)
- Page type: Trip.com verification CAPTCHA ("Select icons in the correct order" / "Slide to complete the puzzle")
- AI actions: waited about 8 s and took one passive snapshot (no goto, reload or retry). Did not interact with the CAPTCHA.
- Evidence: evidence/trip/01-home.png, 01-home.yml, 02-verify-recheck.png, 02-verify-recheck.yml, commands.log, human-wait.log

## For the human
1. Open the dashboard at http://127.0.0.1:9230/ (use an SSH tunnel if needed: `ssh -L 9230:127.0.0.1:9230 <host>`).
2. Select session **lab05-human**, then the "Trip.com-Verification" tab, and complete the verification yourself.
3. Reply to confirm when you are done. The AI will then log WAIT_END, take a new snapshot, and continue from step 2 with the same dates (DEPART=2026-09-27, RETURN_SEARCH=2026-10-01).

Dashboard: pid 298777, log /root/workspace/CWN/Teaching/00_setup/05_Playwright_CLI_Trip/runs/human-20260924T122658Z-298374/dashboard.log. When the lab is finished, stop it with Ctrl+C or `kill $(cat /root/workspace/CWN/Teaching/00_setup/05_Playwright_CLI_Trip/runs/human-20260924T122658Z-298374/dashboard.pid)`.
