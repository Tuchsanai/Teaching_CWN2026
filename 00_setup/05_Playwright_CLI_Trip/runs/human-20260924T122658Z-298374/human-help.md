# WAITING_FOR_HUMAN: whaleguard block on user-requested retry

- Status: **WAITING_FOR_HUMAN** (the AI will not retry automatically)
- Block seen at: 2026-09-24T12:46:54Z (snapshot). WAIT_START 2026-09-24T12:47:01Z, mono 354431.71
- Run path: /root/workspace/CWN/Teaching/00_setup/05_Playwright_CLI_Trip/runs/human-20260924T122658Z-298374
- Session: **lab05-human**. Same browser context as the original run (in-memory profile, headless, idle-timeout=0). It was not recreated, so no context was lost.
- Tabs: 0 = th.trip.com homepage (old tab, kept). **1 = current, blocked page**
- Current URL (tab 1): https://th.trip.com/flights/showfarefirst?dcity=bkk&acity=tyo&ddate=2026-09-27&rdate=2026-10-01&triptype=rt&class=y&lowpricesource=searchform&quantity=1&searchboxarg=t&nonstoponly=off&locale=th-TH&curr=THB
- Page type: plain text "whaleguard block" (Trip.com bot protection). No CAPTCHA widget. Same result as the first attempt (evidence/trip/14-flight-results.*)
- Stuck step: flight search, after clicking ค้นหา. The form was filled through the UI: round trip, Bangkok all airports to Tokyo all airports, 27 Sep - 1 Oct 2026, 1 adult, economy (see 13-dates-set.png, 14-pax-class.png)
- After the block the AI took one snapshot, one screenshot and one tab-list. No reload/goto/retry. No flight or hotel data was collected.
- Fingerprint, proxy and security settings were not changed.

## For the human
Dashboard: http://127.0.0.1:9230/ (pid 298777, still running). Select session lab05-human, tab 1.
There is nothing to solve on the page. Options: try from the dashboard yourself, use a headed/persistent-profile run in a new session, or record the Trip.com branch as BLOCKED (bot protection).
