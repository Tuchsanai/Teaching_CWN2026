# BLOCKED — Trip.com bot verification (CAPTCHA)

- Observed (UTC): 2026-09-24T12:01:17Z (first), re-confirmed 12:02:00Z and 12:02:15Z
- Requested URL: `https://www.trip.com/?locale=en-xx&curr=THB` (retry: `https://www.trip.com/`)
- Actual URL: `https://verify.trip.com/static/tripVerify.html?returnUrl=...`
- Page title: `Trip.com-Verification`
- Visible text: "To continue, please complete the verification test below." + "Select icons in the correct order" / "Slide to complete the puzzle"
- Evidence: `02-verify-after-wait.png`, `02-verify-after-wait.yml`, `03-retry-blocked.png`, `03-retry-blocked.yml`
- Decision: **STOP**. We did not solve, automate, or get around the CAPTCHA: no clicks on the puzzle, no user-agent/stealth changes, no proxy, and no cookies or state from another browser.
- Flight branch: **BLOCKED** (no search form reached, no prices seen)
- Hotel branch: **BLOCKED** (no search form reached, no prices seen)
- Recommendation: **none**, because we have no visible evidence
