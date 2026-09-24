# retry-watch steps (session lab05-human, same browser context as the original run)

| # | Before | Action (command) | What actually happened | Evidence |
|---|---|---|---|---|
| 0 | Dashboard said "No tabs open" | `list`, `tab-list` | Session lab05-human was open (in-memory, headless). Tab 0 = th.trip.com homepage, so the old context was kept | commands.log |
| 0a | Tab 0 | snapshot + screenshot | Thai homepage; form was pre-filled from site state | 00-existing-tab.png/.yml |
| 1 | - | `tab-new https://www.trip.com/` (homepage opened once) | Redirected to th.trip.com/?locale=th-th in tab 1; no CAPTCHA | 01-home.png/.yml |
| 2 | Homepage | click radio "ไป-กลับ" (e210) | Round trip selected | 02-roundtrip.* |
| 3 | | click origin "ลบ" (e239) | Pre-filled origin cleared | 03-origin-cleared.* |
| 4 | | click origin combobox (e240) | Dropdown opened | 04-origin-open.* |
| 5 | | fill e725 "Bangkok" | Suggestion "กรุงเทพ · ทุกสนามบิน ไทย" appeared | 05-origin-typed.* |
| 6 | | click e962 | Origin = กรุงเทพ, all airports | 06-origin-set.* |
| 7 | | click destination "ลบ" (e252) | Pre-filled destination cleared | 07-dest-cleared.* |
| 8 | | click dest combobox (e253) | Dropdown opened | 08-dest-open.* |
| 9 | | fill e1007 "Tokyo" | Suggestion "โตเกียว · ทุกสนามบิน ญี่ปุ่น" appeared | 09-dest-typed.* |
| 10 | | click e1247 | Destination = โตเกียว, all airports | 10-dest-set.* |
| 11 | | click departure date (e259) | Calendar opened | 11-calendar.* |
| 12 | | click "วันอาทิตย์ 27 กันยายน 2026" (e1502) | Departure picked | 12-depart-picked.* |
| 13 | | click "วันพฤหัสบดี 1 ตุลาคม 2026" (e1775) | Dates: อา. 27 ก.ย. - พฤ. 1 ต.ค. | 13-dates-set.* |
| 14 | | click "ผู้ใหญ่ 1 คน, ชั้นประหยัด" (e270) | Panel showed ผู้ใหญ่ 1, เด็ก 0, ทารก 0, ชั้นประหยัด | 14-pax-class.* |
| 15 | Form complete | click " ค้นหา" (e1936), waited 8 s, snapshot + screenshot | showfarefirst URL shows **"whaleguard block"** again (1-line a11y tree). STOPPED | 15-flight-results.png/.yml |

About 2 s pause before each action and before each capture. Per-command UTC/monotonic timings are in commands.log.
